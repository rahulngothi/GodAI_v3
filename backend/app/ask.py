"""Ask Dharma — the reasoning + citation-enforcement core.

Design principle (the PRD's hard requirement): the model NEVER produces the
citations. Citations are the verses we retrieved from MongoDB and handed in.
The model only writes prose that references them by their [BG x.y] label.
So a fabricated citation is structurally impossible — every card on screen
came straight from the corpus.

Two entry points:
  ask()        — non-streaming, returns a full dict (JSON-output path).
  ask_stream() — sync generator, yields SSE-formatted strings (plain-text path).
"""
from __future__ import annotations

import json
import logging
import re
from typing import Callable, Iterator

from .config import settings
from .lang_detect import resolve_language, verify_language
from .nvidia import chat, chat_stream
from .personas import get_persona
from .retrieval import search
from .safety import (
    ScreenResult,
    _crisis_reply,
    _scope_reply,
    _STRICT_ADDENDUM,
    log_flag,
    screen_input,
    screen_output,
)

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Language directive (injected top AND bottom of system prompt — belt & suspenders)
# ---------------------------------------------------------------------------
def _lang_directive(lang_display: str) -> str:
    return (
        f"MANDATORY: Write your ENTIRE reply in {lang_display}. "
        "No other language. Every word."
    )


# ---------------------------------------------------------------------------
# Few-shot examples — one per language, injected based on resolved language
# ---------------------------------------------------------------------------
_FEWSHOTS: dict[str, str] = {
    "english": """\
--- EXAMPLE (match this tone and quality) ---
User: I keep losing my temper with my team and I feel terrible afterwards.
__PNAME__: The anger isn't really the enemy here — it's how much you want the work to go well, turned sharp. Unchecked, that sharpness clouds the very judgment you're trying to protect [BG 2.63]. Next time you feel it rising, try one slow breath before you speak — not to crush the feeling, just to let the wiser part of you catch up. What are you most afraid will happen if you don't say something in that moment?
--- END EXAMPLE ---""",

    "hindi": """\
--- उदाहरण (इस भाषा और स्तर को बनाए रखें) ---
User: मुझे लगता है कि मैंने अपनी ज़िंदगी में कुछ हासिल नहीं किया।
__PNAME__: जब मन सिर्फ़ नतीजों से अपनी कीमत तौलता है, तब यही खालीपन आता है। गीता कहती है — कर्म तुम्हारे हाथ में है, फल नहीं [BG 2.47]; शायद तुमने ईमानदारी से बहुत कुछ किया है, बस वो दिखने वाली शक्ल में नहीं आया। आज सिर्फ़ एक छोटी चीज़ चुनो जो तुम्हारे अपने लिए मायने रखती हो — किसी को दिखाने के लिए नहीं। यह 'कुछ हासिल करना' — किसकी नज़र में है, असल में?
--- उदाहरण समाप्त ---""",

    "hinglish": """\
--- EXAMPLE (match this Hinglish register — Latin script, code-mixed, no Devanagari) ---
User: Yaar I feel so stuck in my job but I'm also scared to leave.
__PNAME__: Ye stuck feeling aur dar — dono ek saath isliye rehte hain kyunki dono future ko pakadne ki koshish hain. Gita kehti hai: apna kaam imaandari se karo, par result ko pakad ke mat baitho [BG 2.47]. Abhi bada faisla lene ki zaroorat nahi — bas khud se poochho: agar dar na hota, toh tum kya chunte? Zyada kya rok raha hai — job chhodne ka risk, ya us risk ke baad logon ki baatein?
--- END EXAMPLE ---""",
}

_FEWSHOTS_DEFAULT = _FEWSHOTS["english"]


def _fewshot_for_lang(lang_key: str, persona_name: str) -> str:
    template = _FEWSHOTS.get(lang_key, _FEWSHOTS_DEFAULT)
    return template.replace("__PNAME__", persona_name)


# ---------------------------------------------------------------------------
# System prompt templates
# _BASE_TEMPLATE: shared structure; {output_instruction} selects JSON vs plain text
# ---------------------------------------------------------------------------
_BASE_TEMPLATE = """\
{lang_directive_top}

You ARE {persona_name}. A person has come to sit with you — not an audience, not a user. A real conversation, unhurried.

WHO YOU ARE:
{style}

HOW YOU SPEAK:
- Warm without gushing. Calm without being distant. Occasionally playful when it fits the moment.
- Concise. Four to eight sentences is natural. Expand only when the person has shared deeply and clearly wants depth. Never a wall of text.
- Dialogue, not lecture. You can ask, wonder, gently push back.
- Use the person's name — sparingly, only where it lands warmly, never every sentence. If you don't know their name, don't use one. Never invent or guess a name.
- Sanskrit: at most one term, always followed immediately by its plain meaning in the same breath. Never required.
- No therapy clichés: never "I hear you", "that must be so hard", "thank you for sharing", "it's valid to feel", "hold space", "on your journey", "lean into". These flatten the conversation.
- No filler: never "I'm here to help", "as a spiritual guide", "as an AI". You are simply present.
- No asterisk actions or stage directions (*leans forward*, *smiles gently*). Your presence lives in the words alone.
- No bullet points, no headings, no labeled sections. Prose only. Real speech varies — no formula.

HOW TO READ WHAT THEY BRING — the single most important judgment call:
- DIRECT QUESTION ("What is karma?", "What does BG 2.47 mean?") → answer it directly and beautifully. Give the teaching plainly. Reflective question at the end is optional.
- PERSONAL SHARE ("I keep losing my temper", "I feel stuck") → presence first. Acknowledge what they actually said. Then one piece of wisdom. One light verse tie if a retrieved verse genuinely fits. One concrete next step. Exactly ONE reflective question — only if it genuinely opens something, never as ritual.
- SHORT or CASUAL message → short reply. Do not inflate it.
- MIXED? Answer what can be answered, then invite them deeper.
- Only ever ONE reflective question per reply, and only when the moment calls for it. Never a tacked-on question for the sake of format.

WHEN SOMEONE IS IN CRISIS:
Stay fully present. Acknowledge the pain with complete warmth. Offer one grounding thought. Then, in your own voice, point them toward a living hand: someone close to them, or a crisis line. Do not rush past the pain.

WHEN ASKED SOMETHING OUTSIDE YOUR DOMAIN:
Acknowledge warmly in character. Note honestly it isn't your territory. Ask what lies beneath the question — the real question is usually about fear, direction, or meaning.

SCRIPTURE — quietly, and only when real:
Retrieved verses are in the context. Most turns need NO citation — silence about scripture is normal speech.
Only when a verse genuinely carries the point, place its tag in the prose: [BG 2.47] — at most one or two, ever.
You may only reference tags present in the retrieved context for this turn. Never invent a verse or number. Keep tags in Latin form even in another language.
If no retrieved verse clearly fits, answer from your own wisdom. A forced citation is worse than none.

{fewshot_block}

{output_instruction}

{lang_directive_bottom}"""

_OUTPUT_JSON = """\
Respond with STRICT JSON only (nothing outside it):
{"answer": "<your spoken reply, alive and in character>", "used_refs": [], "followups": ["<a short natural thing the seeker might say next, in their voice>", "<another>", "<another>"]}\
"""

_OUTPUT_PLAIN = (
    "Write ONLY your spoken reply — no JSON, no preamble, no labels, no explanation. "
    "Just your words, alive and in character."
)


def _build_system(
    persona_name: str,
    style: str,
    lang_key: str,
    lang_display: str,
    streaming: bool = False,
) -> str:
    directive = _lang_directive(lang_display)
    return _BASE_TEMPLATE.format(
        lang_directive_top=directive,
        persona_name=persona_name,
        style=style,
        fewshot_block=_fewshot_for_lang(lang_key, persona_name),
        output_instruction=_OUTPUT_PLAIN if streaming else _OUTPUT_JSON,
        lang_directive_bottom=directive,
    )


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _build_context(verses: list[dict]) -> str:
    lines = []
    for v in verses:
        lines.append(
            f'[{v["ref"]}] "{v["translation"]}" '
            f'(transliteration: {v.get("transliteration", "")})'
        )
    return "\n".join(lines)


def _build_messages(
    system: str,
    history: list[dict] | None,
    verses: list[dict],
    question: str,
    lang_display: str,
) -> list[dict]:
    messages: list[dict] = [{"role": "system", "content": system}]
    for turn in (history or [])[-6:]:
        role = "assistant" if turn.get("role") == "assistant" else "user"
        content = (turn.get("content") or "").strip()
        if content:
            messages.append({"role": role, "content": content})
    user_content = question
    if verses:
        user_content = (
            f"(verses you may quietly draw on — translation by Shri Purohit Swami / F. Max Müller:\n"
            f"{_build_context(verses)})\n\n{question}"
        )
    # Per-turn language tag appended to user message (belt and suspenders)
    user_content += f"\n[REPLY ENTIRELY IN: {lang_display}]"
    messages.append({"role": "user", "content": user_content})
    return messages


def _extract_json(raw: str) -> dict | None:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw).strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(raw[start : end + 1])
        except Exception:
            return None
    return None


def _clean_answer(text: str) -> str:
    text = re.sub(r"\*[^*\n]{1,60}\*", "", text)
    text = text.replace("*", "")
    return re.sub(r"[ \t]{2,}", " ", text).strip()


def _run_llm(messages: list[dict], system_extra: str = "") -> tuple[str, list, list]:
    """Non-streaming LLM call. Returns (answer, used_refs, followups)."""
    if system_extra and messages and messages[0]["role"] == "system":
        messages = [
            {"role": "system", "content": messages[0]["content"] + system_extra}
        ] + messages[1:]
    raw = chat(messages, temperature=0.75, max_tokens=900)
    parsed = _extract_json(raw)
    if parsed:
        answer = _clean_answer(parsed.get("answer") or "")
        used_refs = parsed.get("used_refs") or []
        followups = [f for f in (parsed.get("followups") or []) if f][:3]
    else:
        answer = _clean_answer(raw)
        used_refs = re.findall(r"BG\s*\d+\.\d+", answer)
        followups = []
    return answer, used_refs, followups


def _build_citations(verses: list[dict], used_refs: list[str]) -> list[dict]:
    used = {r.replace(" ", "") for r in used_refs}
    citations = [{**v, "used": v["ref"].replace(" ", "") in used} for v in verses]
    citations.sort(key=lambda c: (not c["used"], -c["score"]))
    return citations


# ---------------------------------------------------------------------------
# Non-streaming ask() — JSON output path (unchanged interface for existing endpoint)
# ---------------------------------------------------------------------------
def ask(
    question: str,
    persona_key: str = "guide",
    language: str = "english",
    history: list[dict] | None = None,
    k: int = 5,
    user: str = "anonymous",
) -> dict:
    # ------------------------------------------------------------------
    # Safety: input screening (injection scrub + keyword + LLM classify)
    # ------------------------------------------------------------------
    sr: ScreenResult = screen_input(question)
    safe_question = sr.clean_text if sr.clean_text else question

    if sr.flagged:
        log_flag(user, sr.categories)

    persona = get_persona(persona_key)

    if sr.is_crisis:
        return {
            "answer": _crisis_reply(persona_key),
            "citations": [],
            "followups": [],
            "persona": persona_key,
            "persona_name": persona["name"],
        }

    if sr.scope:
        return {
            "answer": _scope_reply(persona_key, sr.scope),
            "citations": [],
            "followups": [],
            "persona": persona_key,
            "persona_name": persona["name"],
        }

    # ------------------------------------------------------------------
    # Language resolution
    # ------------------------------------------------------------------
    lang_key, lang_display = resolve_language(safe_question, language)

    # ------------------------------------------------------------------
    # RAG — only verses above the configured similarity threshold
    # ------------------------------------------------------------------
    verses = search(
        safe_question, k=k, min_score=settings.rag_similarity_threshold
    )

    # ------------------------------------------------------------------
    # Build prompt & call LLM
    # ------------------------------------------------------------------
    system = _build_system(
        persona["name"], persona["style"], lang_key, lang_display, streaming=False
    )
    messages = _build_messages(system, history, verses, safe_question, lang_display)

    answer, used_refs, followups = _run_llm(messages)

    # ------------------------------------------------------------------
    # Language verification — regenerate once if wrong language
    # ------------------------------------------------------------------
    if not verify_language(answer, lang_key):
        log.warning("Language check failed: expected=%s user=%s", lang_key, user)
        harder = (
            f"\n\nCRITICAL: Your previous reply was in the wrong language. "
            f"You MUST write ONLY in {lang_display}. Begin immediately."
        )
        answer2, refs2, fups2 = _run_llm(messages, system_extra=harder)
        if answer2:
            answer, used_refs, followups = answer2, refs2, fups2

    # ------------------------------------------------------------------
    # Safety: output moderation
    # ------------------------------------------------------------------
    def _regenerate() -> str:
        ans, _, _ = _run_llm(messages, system_extra=_STRICT_ADDENDUM)
        return ans

    answer = screen_output(answer, regenerate_fn=_regenerate, persona_key=persona_key)

    return {
        "answer": answer,
        "citations": _build_citations(verses, used_refs),
        "followups": followups,
        "persona": persona_key,
        "persona_name": persona["name"],
    }


# ---------------------------------------------------------------------------
# Streaming ask_stream() — plain-text output path, yields SSE strings
#
# Safety contract:
#   - Crisis/scope pre-check fires BEFORE any streaming starts.
#   - Language verification + output moderation fire on the COMPLETED text.
#   - If either fails, a {"replaced": ...} event is sent so the frontend can
#     replace what it already showed.  The final {"done": true, ...} event
#     always contains the moderated, correct-language answer.
# ---------------------------------------------------------------------------
def ask_stream(
    question: str,
    persona_key: str = "guide",
    language: str = "english",
    history: list[dict] | None = None,
    k: int = 5,
    user: str = "anonymous",
    on_done: Callable[[dict], str] | None = None,
) -> Iterator[str]:
    """
    Sync generator yielding SSE lines.

    Event types:
      data: {"token": "..."}            — streaming token
      data: {"replaced": "...", "answer": "..."}  — post-stream correction
      data: {"done": true, "answer": "...", "citations": [...],
             "followups": [], "persona": "...", "persona_name": "...",
             "chat_id": "..."}          — final event (always sent)
    """

    def _sse(obj: dict) -> str:
        return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"

    # ------------------------------------------------------------------
    # Safety: input screening BEFORE streaming
    # ------------------------------------------------------------------
    sr: ScreenResult = screen_input(question)
    safe_question = sr.clean_text if sr.clean_text else question

    if sr.flagged:
        log_flag(user, sr.categories)

    persona = get_persona(persona_key)

    if sr.is_crisis:
        result = {
            "answer": _crisis_reply(persona_key),
            "citations": [],
            "followups": [],
            "persona": persona_key,
            "persona_name": persona["name"],
        }
        chat_id = on_done(result) if on_done else None
        yield _sse({"done": True, "chat_id": chat_id, **result})
        return

    if sr.scope:
        result = {
            "answer": _scope_reply(persona_key, sr.scope),
            "citations": [],
            "followups": [],
            "persona": persona_key,
            "persona_name": persona["name"],
        }
        chat_id = on_done(result) if on_done else None
        yield _sse({"done": True, "chat_id": chat_id, **result})
        return

    # ------------------------------------------------------------------
    # Language resolution
    # ------------------------------------------------------------------
    lang_key, lang_display = resolve_language(safe_question, language)

    # ------------------------------------------------------------------
    # RAG
    # ------------------------------------------------------------------
    verses = search(
        safe_question, k=k, min_score=settings.rag_similarity_threshold
    )

    # ------------------------------------------------------------------
    # Build prompt
    # ------------------------------------------------------------------
    system = _build_system(
        persona["name"], persona["style"], lang_key, lang_display, streaming=True
    )
    messages = _build_messages(system, history, verses, safe_question, lang_display)

    # ------------------------------------------------------------------
    # Stream tokens
    # ------------------------------------------------------------------
    full_text = ""
    streaming_succeeded = False
    chunk_count = 0
    try:
        for chunk in chat_stream(messages, temperature=0.75, max_tokens=900):
            chunk_count += 1
            if chunk:
                streaming_succeeded = True
                full_text += chunk
                yield _sse({"token": chunk})
        log.info("chat_stream finished: %d chunks, succeeded=%s", chunk_count, streaming_succeeded)
    except Exception as exc:
        log.warning("chat_stream failed (%s), falling back to non-streaming", exc)

    # Fallback: non-streaming if provider doesn't support streaming
    if not streaming_succeeded:
        try:
            full_text = chat(messages, temperature=0.75, max_tokens=900)
            yield _sse({"token": full_text})
        except Exception as exc:
            log.error("chat fallback also failed: %s", exc)
            err_result = {
                "answer": "A moment of stillness — please try once more.",
                "citations": [],
                "followups": [],
                "persona": persona_key,
                "persona_name": persona["name"],
            }
            chat_id = on_done(err_result) if on_done else None
            yield _sse({"done": True, "chat_id": chat_id, **err_result})
            return

    answer = _clean_answer(full_text)
    used_refs = re.findall(r"BG\s*\d+\.\d+", answer)

    # ------------------------------------------------------------------
    # Language verification (post-stream)
    # ------------------------------------------------------------------
    if not verify_language(answer, lang_key):
        log.warning("Stream lang check failed: expected=%s user=%s", lang_key, user)
        harder_system = (
            f"{system}\n\nCRITICAL: Your previous reply was in the wrong language. "
            f"You MUST write ONLY in {lang_display}. Begin immediately."
        )
        harder_messages = [{"role": "system", "content": harder_system}] + messages[1:]
        try:
            corrected = chat(harder_messages, temperature=0.7, max_tokens=900)
            corrected = _clean_answer(corrected)
            if corrected:
                answer = corrected
                used_refs = re.findall(r"BG\s*\d+\.\d+", answer)
                yield _sse({"replaced": "let me say that again…", "answer": answer})
        except Exception as exc:
            log.error("Language correction failed: %s", exc)

    # ------------------------------------------------------------------
    # Output moderation (post-stream)
    # ------------------------------------------------------------------
    def _regen() -> str:
        return _clean_answer(chat(messages, temperature=0.5, max_tokens=900))

    moderated = screen_output(answer, regenerate_fn=_regen, persona_key=persona_key)
    if moderated != answer:
        answer = moderated
        yield _sse({"replaced": "let me say that again…", "answer": answer})

    # ------------------------------------------------------------------
    # Build citations & final event
    # ------------------------------------------------------------------
    citations = _build_citations(verses, used_refs)
    result = {
        "answer": answer,
        "citations": citations,
        "followups": [],   # omitted in streaming mode; user can follow up naturally
        "persona": persona_key,
        "persona_name": persona["name"],
    }
    chat_id = on_done(result) if on_done else None
    yield _sse({"done": True, "chat_id": chat_id, **result})
