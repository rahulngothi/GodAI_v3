"""LLM + embedding client.

LLM: any OpenAI-compatible provider, selected via LLM_PROVIDER / LLM_BASE_URL /
LLM_API_KEY / LLM_MODEL env vars.  Switching provider requires no code change.

Embeddings: always NVIDIA nv-embedqa (the corpus was ingested against it; changing
the embed provider would invalidate all stored vectors).

Provider defaults (used when LLM_MODEL / LLM_BASE_URL are not explicitly set):
  nvidia  → integrate.api.nvidia.com/v1  +  moonshotai/kimi-k2.6
  gemini  → generativelanguage.googleapis.com/v1beta/openai  +  gemini-2.5-flash
  sarvam  → api.sarvam.ai/v1  +  sarvam-m
  claude  → Anthropic SDK  +  claude-sonnet-4-6  (set ANTHROPIC_API_KEY in .env)
"""
from __future__ import annotations

import json
import logging
import os

import httpx

from .config import settings

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Provider resolution
# ---------------------------------------------------------------------------
_PROVIDER_DEFAULTS: dict[str, dict[str, str]] = {
    "nvidia": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "model": "moonshotai/kimi-k2.6",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.5-flash",
    },
    "sarvam": {
        "base_url": "https://api.sarvam.ai/v1",
        "model": "sarvam-m",
    },
    "claude": {
        "base_url": "",  # uses Anthropic SDK, not httpx
        "model": "claude-sonnet-4-6",
    },
}


def _llm_base_url() -> str:
    if settings.llm_base_url:
        return settings.llm_base_url
    return _PROVIDER_DEFAULTS.get(settings.llm_provider, _PROVIDER_DEFAULTS["nvidia"])["base_url"]


def _llm_api_key() -> str:
    return settings.llm_api_key or settings.nvidia_api_key


def _llm_model() -> str:
    if settings.llm_model:
        return settings.llm_model
    return _PROVIDER_DEFAULTS.get(settings.llm_provider, _PROVIDER_DEFAULTS["nvidia"])["model"]


# ---------------------------------------------------------------------------
# Lazy singleton clients (created on first use so config is fully loaded)
# ---------------------------------------------------------------------------
_llm_client: httpx.Client | None = None
_embed_client: httpx.Client | None = None


def _get_llm_client() -> httpx.Client:
    global _llm_client
    if _llm_client is None:
        _llm_client = httpx.Client(
            base_url=_llm_base_url(),
            headers={
                "Authorization": f"Bearer {_llm_api_key()}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(90.0, connect=10.0),
        )
    return _llm_client


def _get_embed_client() -> httpx.Client:
    global _embed_client
    if _embed_client is None:
        _embed_client = httpx.Client(
            base_url=settings.nvidia_base_url,
            headers={
                "Authorization": f"Bearer {settings.nvidia_api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(90.0, connect=10.0),
        )
    return _embed_client


# ---------------------------------------------------------------------------
# Embeddings (always NVIDIA)
# ---------------------------------------------------------------------------
EMBED_BATCH = 32


def embed(texts: list[str], input_type: str = "query") -> list[list[float]]:
    """Embed a list of strings. input_type is 'query' (questions) or 'passage' (verses)."""
    vectors: list[list[float]] = []
    for i in range(0, len(texts), EMBED_BATCH):
        chunk = texts[i : i + EMBED_BATCH]
        resp = _get_embed_client().post(
            "/embeddings",
            json={
                "model": settings.embed_model,
                "input": chunk,
                "input_type": input_type,
                "encoding_format": "float",
                "truncate": "END",
            },
        )
        resp.raise_for_status()
        data = sorted(resp.json()["data"], key=lambda d: d["index"])
        vectors.extend(d["embedding"] for d in data)
    return vectors


def embed_one(text: str, input_type: str = "query") -> list[float]:
    return embed([text], input_type=input_type)[0]


# ---------------------------------------------------------------------------
# Claude (Anthropic SDK) — used when LLM_PROVIDER=claude
# ---------------------------------------------------------------------------
def _chat_claude(messages: list[dict], temperature: float, max_tokens: int) -> str:
    import anthropic  # lazy import — only needed when provider=claude
    api_key = settings.llm_api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    model = settings.llm_model or _PROVIDER_DEFAULTS["claude"]["model"]
    client = anthropic.Anthropic(api_key=api_key)

    # Split system message out (Anthropic API separates it)
    system = ""
    user_messages = []
    for m in messages:
        if m["role"] == "system":
            system = m["content"]
        else:
            user_messages.append({"role": m["role"], "content": m["content"]})

    kwargs: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": user_messages,
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    return response.content[0].text


def _chat_claude_stream(messages: list[dict], temperature: float, max_tokens: int):
    import anthropic
    api_key = settings.llm_api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    model = settings.llm_model or _PROVIDER_DEFAULTS["claude"]["model"]
    client = anthropic.Anthropic(api_key=api_key)

    system = ""
    user_messages = []
    for m in messages:
        if m["role"] == "system":
            system = m["content"]
        else:
            user_messages.append({"role": m["role"], "content": m["content"]})

    kwargs: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": user_messages,
    }
    if system:
        kwargs["system"] = system

    with client.messages.stream(**kwargs) as stream:
        for text in stream.text_stream:
            if text:
                yield text


# ---------------------------------------------------------------------------
# Chat — non-streaming (returns full content string)
# ---------------------------------------------------------------------------
def chat(
    messages: list[dict],
    temperature: float = 0.3,
    max_tokens: int = 1400,
    response_format: dict | None = None,
) -> str:
    if settings.llm_provider == "claude":
        return _chat_claude(messages, temperature, max_tokens)

    payload: dict = {
        "model": _llm_model(),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format is not None:
        payload["response_format"] = response_format
    resp = _get_llm_client().post("/chat/completions", json=payload)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Chat — streaming (yields text chunks as they arrive)
# ---------------------------------------------------------------------------
def chat_stream(
    messages: list[dict],
    temperature: float = 0.75,
    max_tokens: int = 900,
):
    """
    Generator that yields text chunks from the LLM as they stream.
    Raises on HTTP errors.  Callers should wrap in try/except and fall back to
    chat() if the provider doesn't support streaming.
    """
    payload: dict = {
        "model": _llm_model(),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }
    if settings.llm_provider == "claude":
        yield from _chat_claude_stream(messages, temperature, max_tokens)
        return

    with _get_llm_client().stream("POST", "/chat/completions", json=payload) as resp:
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        log.debug("chat_stream content-type: %s", content_type)

        # If the provider returns a regular JSON response instead of SSE
        # (some providers ignore stream:True), parse it as a normal completion.
        if "text/event-stream" not in content_type:
            body = resp.read()
            log.warning(
                "chat_stream: provider returned non-SSE content-type=%s, "
                "falling back to single-chunk parse",
                content_type,
            )
            try:
                data = json.loads(body)
                content = data["choices"][0]["message"]["content"]
                if content:
                    yield content
            except (json.JSONDecodeError, KeyError, IndexError):
                pass
            return

        lines_seen = 0
        for line in resp.iter_lines():
            if not line:
                continue
            lines_seen += 1
            # Handle both "data: " (standard) and "data:" (no space)
            if line.startswith("data:"):
                data = line[5:].lstrip(" ")
            else:
                log.debug("chat_stream unexpected line: %r", line[:80])
                continue
            if data.strip() == "[DONE]":
                break
            try:
                chunk = json.loads(data)
                choices = chunk.get("choices") or []
                if not choices:
                    # Usage/ping frame with no content — skip silently
                    continue
                delta = choices[0].get("delta", {}).get("content")
                if delta is None:
                    delta = choices[0].get("text")
                if delta:
                    yield delta
            except (json.JSONDecodeError, KeyError, IndexError) as exc:
                log.debug("chat_stream parse error on line %r: %s", line[:80], exc)

        log.debug("chat_stream finished: lines_seen=%d", lines_seen)
