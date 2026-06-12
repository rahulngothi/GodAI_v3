"""Thin client for NVIDIA's OpenAI-compatible API (Kimi K2.6 + nv-embedqa).

One shared httpx.Client. Both functions are synchronous; the FastAPI layer
calls them from threadpool-executed endpoints.
"""
from __future__ import annotations

import httpx

from .config import settings

_client = httpx.Client(
    base_url=settings.nvidia_base_url,
    headers={
        "Authorization": f"Bearer {settings.nvidia_api_key}",
        "Content-Type": "application/json",
    },
    timeout=httpx.Timeout(90.0, connect=10.0),
)

# nv-embedqa models require an input_type and have a modest batch ceiling.
EMBED_BATCH = 32


def embed(texts: list[str], input_type: str = "query") -> list[list[float]]:
    """Embed a list of strings. input_type is 'query' (questions) or 'passage' (verses)."""
    vectors: list[list[float]] = []
    for i in range(0, len(texts), EMBED_BATCH):
        chunk = texts[i : i + EMBED_BATCH]
        resp = _client.post(
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


def chat(
    messages: list[dict],
    temperature: float = 0.3,
    max_tokens: int = 1400,
    response_format: dict | None = None,
) -> str:
    payload: dict = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format is not None:
        payload["response_format"] = response_format
    resp = _client.post("/chat/completions", json=payload)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
