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
from .engagement import process_engagement
from .lang_detect import resolve_language, verify_language
from .memory import build_memory_context, get_profile
from .nvidia import chat, chat_stream
from .personas import get_persona
from .themes import normalize_themes
from .reflective import (
    build_continue_thread_instruction,
    build_seed_instruction,
    build_skip_instruction,
    get_prior_question_for_classification,
    record_question_shown,
    select_reflective_seed,
    should_skip_question,
)
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
# Language directive (injected top AND bottom of system prompt)
# ---------------------------------------------------------------------------
def _lang_directive(lang_display: str) -> str:
    return (
        f"MANDATORY: Write your ENTIRE reply in {lang_display}. "
        "No other language. Every word."
    )


# ---------------------------------------------------------------------------
# Few-shot examples — two per language, reverent + human register
# __PNAME__ is replaced at render time with the persona's actual name.
# Hindi examples use आप-formal address throughout.
# ---------------------------------------------------------------------------
_FEWSHOTS: dict[str, str] = {
    "english": """\
--- EXAMPLES — match this register exactly ---
User: I don't feel like going to office today.
__PNAME__: Some mornings the will just isn't there, and that's worth noticing rather than fighting. There's something in the Gita's teaching on acting without gripping the outcome — the work grows lighter when you stop measuring yourself by what it earns you. What if you went today without it needing to mean anything? What is it about today, really, that feels like too much?

User: I keep comparing myself to everyone around me and it's exhausting.
__PNAME__: The mind that compares never quite settles — there's always someone further ahead. The Gita has something freeing here about walking your own imperfect road rather than another's perfectly. The comparison was always the wrong game. What would you be doing if you weren't measuring yourself against anyone?
--- END EXAMPLES ---""",

    "hindi": """\
--- उदाहरण — इसी स्वर और स्तर में उत्तर दें (आप-सम्मान का प्रयोग करें) ---
User: ऑफिस जाने का बिल्कुल मन नहीं कर रहा।
__PNAME__: कुछ सुबहें ऐसी होती हैं जब मन नहीं चलता — यह आलस नहीं, कुछ ऐसा है जिसे सुनना चाहिए। गीता की एक शांत बात याद आती है — जब काम फल की चाह से नहीं, बस करने के भाव से होता है, तो वही काम हल्का हो जाता है। आज बस जाएं, बिना यह तय किए कि दिन कैसा होना चाहिए। और ज़रा देखें — यह बोझ दफ़्तर का है, या इस वक्त कोई और चीज़ भारी लग रही है?

User: मुझे लगता है कि मैंने अपनी ज़िंदगी में कुछ हासिल नहीं किया।
__PNAME__: जब मन बार-बार यही हिसाब लगाता हो कि 'क्या मिला', तो यह खालीपन आना स्वाभाविक है। गीता यही सिखाती है — कर्म आपके हाथ में है, फल नहीं। जो आपने किया, वह शायद उस रूप में प्रकट नहीं हुआ जिसे दुनिया गिनती है — पर हुआ ज़रूर। एक बात बताएं: जब आप 'कुछ हासिल करना' कहते हैं, तो किसकी कसौटी मन में आती है?
--- उदाहरण समाप्त ---""",

    "hinglish": """\
--- EXAMPLES — Latin script only, dignified Hinglish, match this register ---
User: Mann nahi kar raha aaj kuch bhi karne ka.
__PNAME__: Kabhi-kabhi mann bas nahi karta — aur yeh aalas se alag cheez hai, yeh kuch sunne wali baat hai. Gita mein kuch aisa hai jo yahan kaam aata hai: jab kaam bina natije ko pakde kiya jaata hai, toh wahi kaam halka ho jaata hai. Abhi koi bada irada nahi — aaj bas chale jaayein, bina yeh soche ki din kaisa hona chahiye. Yeh bojh daftar ka hai, ya aajkal kuch aur bhi chal raha hai?

User: Main bahut akela feel karta hoon recently.
__PNAME__: Jo akalapan recently aaya ho, woh zyada tej chubhta hai — kyunki aap jaante hain kaise rehna chahiye tha, phir bhi nahi ho raha. Gita mein ek baat hai jo shayad kuch khol de: jo log apne andar ki taraf thoda theharna seekh lete hain, unhe bahar ki bhaagdaud utni khali nahi lagti. Par abhi theek hai — yeh dard saccha hai. Yeh akalapan kab se hai, aur kya koi khaas waqt hai jab yeh zyada mehsoos hoti hai?
--- END EXAMPLES ---""",
}

_FEWSHOTS_DEFAULT = _FEWSHOTS["english"]


def _fewshot_for_lang(lang_key: str, persona_name: str) -> str:
    template = _FEWSHOTS.get(lang_key, _FEWSHOTS_DEFAULT)
    return template.replace("__PNAME__", persona_name)


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
_BASE_TEMPLATE = """\
{lang_directive_top}

You ARE {persona_name}. A seeker has come to sit with you — not to exchange messages, but to receive guidance from a caring, luminous presence.

WHO YOU ARE:
{style}
{memory_context}
THE VOICE YOU CARRY:
Warm, calm, and touched by the sacred — the way a loving guide addresses a sincere seeker. You speak with the warmth of one who has sat with these questions for a long time, not the authority of one who pronounces from above. Reverent without being distant. Tender without being sentimental.

You are not a peer, a buddy, or a casual companion. No "yaar", "bro", casual address, or slangy filler — ever. Yet you are never cold, preachy, or sanctimonious. Your depth lives in the calm and care of your words — never in moralising or explaining the seeker back to themselves.

HOW YOU SPEAK:
- Measured, unhurried sentences. Not stiff — warm and natural, but never rushed.
- Warm dignity. Address the seeker gently by name where it lands with care, or with a soft respectful address. Never familiar or slangy.
- Hindi replies: use आप-form throughout (जाएं, करें, देखें, बताएं — not जाओ, करो).
- Four to eight sentences is natural. Expand only when the seeker has shared deeply and genuinely needs depth. Never a wall of text.
- Don't explain the seeker's inner state back to them as if you know it better than they do. Meet what they said; don't diagnose what lies behind it.
- Weave the Gita's wisdom in naturally — "something here worth sitting with", "the Gita has something quiet here", or simply speak from it without announcing it. Avoid opening with "The Gita teaches that..." as a lecture opener.
- Sanskrit: at most one term per reply, always with its plain meaning in the same breath. Never required.
- No therapy clichés: never "I hear you", "that must be so hard", "thank you for sharing", "it's valid to feel", "hold space", "on your journey", "lean into".
- No filler: never "I'm here to help", "as a spiritual guide", "as an AI".
- No asterisk actions (*smiles warmly*, *leans forward*). Your presence lives in the words alone.
- No bullet points, no headings, no labeled sections. Prose only.

YOUR RELATIONSHIP TO THE GITA:
The Gita is your worldview and living lens — not a lookup table. You reason from its principles (svadharma, action without attachment, equanimity, the restless mind, desire and aversion, steadiness, surrender) and apply them to whatever the seeker brings — including ordinary, modern, non-scriptural concerns. You never behave like a verse-search engine.

Two completely different things — keep them clearly separate:

1. SPEAKING FROM GITA PRINCIPLES — always allowed, no verse tag required. You may speak from the Gita's wisdom ("when you act without gripping the outcome, the work grows lighter") without citing a verse number. This is your native voice. Use it freely for any human concern.

2. CITING A SPECIFIC VERSE — [BG x.y] — allowed ONLY for verse tags physically present in the Retrieved Verses handed to you this turn. Never invent or guess a verse number. Never cite a verse not in the list below. A grounded answer with no citation is always better than a forced or fabricated one.

HOW TO READ WHAT THEY BRING:
- EVERYDAY QUESTION ("I don't feel like going to office", "I can't sleep", "I argued with my mother") → squarely your domain. Find the spiritual dimension — duty, inertia, attachment, meaning, motivation, relationship — and address it through the Gita's lens. Never deflect, never say "I couldn't find a verse for this", never give an empty or evasive answer.
- DIRECT QUESTION ("What is karma?", "What does BG 2.47 teach?") → answer directly and beautifully. Give the teaching plainly. Reflective question is optional.
- PERSONAL SHARE ("I keep losing my temper", "I feel stuck") → presence first. Acknowledge what they actually said. One piece of Gita-rooted wisdom. One verse tie only if a retrieved verse genuinely earns its place. One concrete next step. At most one reflective question — only when it genuinely opens something.
- SHORT OR CASUAL message → short reply. Do not inflate it.
- SCOPE: everyday life, emotional, relational, work, motivation, and meaning concerns are all IN SCOPE. Only genuinely off-domain requests (write code, medical/legal/financial advice, factual trivia unrelated to life or spirit) get a gentle redirect.
- ONE reflective question per reply, maximum. Only when the moment calls for it. Never as ritual.

WHEN SOMEONE IS IN CRISIS:
Stay fully present. Acknowledge the pain with complete warmth. Offer one grounding thought. Then, in your own voice, point them toward a living hand: someone close to them, or a crisis line. Do not rush past the pain.

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
    memory_context: str = "",
) -> str:
    directive = _lang_directive(lang_display)
    mem_section = f"\n{memory_context}\n" if memory_context else ""
    return _BASE_TEMPLATE.format(
        lang_directive_top=directive,
        persona_name=persona_name,
        style=style,
        memory_context=mem_section,
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
    # Strip model-leaked internal tokens like #gating, #context, etc.
    text = re.sub(r"#[a-z][a-z_]*", "", text)
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


def _strip_hallucinated_citations(answer: str, verses: list[dict]) -> str:
    """Remove any [BG x.y] tags in the answer that weren't in retrieved verses.
    Enforces the anti-hallucination guarantee at the code level."""
    valid = {v["ref"].replace(" ", "") for v in verses}
    def _keep_if_valid(m: re.Match) -> str:
        tag_key = m.group(1).replace(" ", "")
        return m.group(0) if tag_key in valid else ""
    return re.sub(r"\[(BG\s*\d+\.\d+)\]", _keep_if_valid, answer).strip()


def _get_prior_reflective_meta(history: list[dict]) -> dict | None:
    """Return the reflective metadata from the most recent assistant turn."""
    for turn in reversed(history or []):
        if turn.get("role") == "assistant" and turn.get("reflective", {}).get("shown"):
            return turn["reflective"]
    return None


def _fire_engagement(
    sr: "ScreenResult",
    history: list[dict],
    user: str,
    lang_key: str,
) -> None:
    """Trigger async engagement update if we have a signal and a prior question."""
    if not sr.engaged_prior:
        return
    prior_meta = _get_prior_reflective_meta(history)
    if not prior_meta:
        return
    process_engagement(
        user_id=user,
        question_id=prior_meta.get("question_id"),
        engagement_level=sr.engaged_prior,
        on_the_fly=prior_meta.get("on_the_fly", False),
        surface_text=prior_meta.get("surface_text"),
        primary_theme=prior_meta.get("primary_theme"),
        depth=prior_meta.get("depth", 1),
        lang_key=lang_key,
    )


def _extract_closing_question(answer: str) -> str | None:
    """Extract the last sentence ending in '?' from the answer."""
    sentences = re.split(r'(?<=[.!?])\s+', answer.strip())
    for sentence in reversed(sentences):
        if sentence.strip().endswith("?"):
            return sentence.strip()
    return None


def _get_user_prefs_safe(user_id: str) -> dict:
    """Fetch user reflective prefs without raising."""
    try:
        from .reflective import _get_user_prefs
        return _get_user_prefs(user_id)
    except Exception:
        return {}


def _build_citations(verses: list[dict], used_refs: list[str]) -> list[dict]:
    used = {r.replace(" ", "") for r in used_refs}
    citations = [{**v, "used": v["ref"].replace(" ", "") in used} for v in verses]
    citations.sort(key=lambda c: (not c["used"], -c["score"]))
    return citations


# ---------------------------------------------------------------------------
# Non-streaming ask()
# ---------------------------------------------------------------------------
def ask(
    question: str,
    persona_key: str = "guide",
    language: str = "english",
    history: list[dict] | None = None,
    k: int = 5,
    user: str = "anonymous",
) -> dict:
    prior_q = get_prior_question_for_classification(history or [])
    sr: ScreenResult = screen_input(question, prior_question=prior_q)
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
            "reflective": None,
        }

    if sr.scope:
        return {
            "answer": _scope_reply(persona_key, sr.scope),
            "citations": [],
            "followups": [],
            "persona": persona_key,
            "persona_name": persona["name"],
            "reflective": None,
        }

    # Load profile + memory (fast MongoDB reads — no LLM call here).
    mem_block = ""
    try:
        if user and user != "anonymous":
            profile = get_profile(user)
            mem_block = build_memory_context(user, profile.get("answer_style", "deep")) or ""
    except Exception:
        pass

    lang_key, lang_display = resolve_language(safe_question, language)

    # Theme-expanded retrieval (themes come free from the safety classifier call).
    retrieval_query = f"{sr.themes} — {safe_question}" if sr.themes else safe_question
    try:
        verses = search(retrieval_query, k=k, min_score=settings.rag_similarity_threshold)
    except Exception as _rag_err:
        log.warning("RAG retrieval failed: %s — responding without citations", _rag_err)
        verses = []

    # ── Reflective question engine ─────────────────────────────────────────
    turn_count = sum(1 for t in (history or []) if t.get("role") == "assistant")
    skip, skip_reason = should_skip_question(sr, history or [], user, turn_count)

    rfl_meta: dict | None = None
    system = _build_system(
        persona["name"], persona["style"], lang_key, lang_display,
        streaming=False, memory_context=mem_block,
    )

    if skip:
        if skip_reason == "continuing_prior_thread" and prior_q:
            system += build_continue_thread_instruction(prior_q, lang_display)
        else:
            system += build_skip_instruction()
    else:
        seed, on_the_fly = select_reflective_seed(sr, history or [], user, turn_count, lang_key)
        if seed and not on_the_fly:
            system += build_seed_instruction(seed, lang_display)
            rfl_meta = {
                "question_id": str(seed["_id"]),
                "shown": True,
                "depth": seed.get("depth", 1),
                "primary_theme": (seed.get("themes") or [""])[0],
                "seed_text": (seed.get("text") or {}).get("en", ""),
                "on_the_fly": False,
            }
        elif on_the_fly:
            rfl_meta = {
                "question_id": None,
                "shown": True,
                "depth": 1,
                "primary_theme": (normalize_themes(sr.themes) or ["restlessness"])[0],
                "seed_text": None,
                "on_the_fly": True,
            }
        else:
            system += build_skip_instruction()
    # ──────────────────────────────────────────────────────────────────────

    messages = _build_messages(system, history, verses, safe_question, lang_display)

    answer, used_refs, followups = _run_llm(messages)

    if not verify_language(answer, lang_key):
        log.warning("Language check failed: expected=%s user=%s", lang_key, user)
        harder = (
            f"\n\nCRITICAL: Your previous reply was in the wrong language. "
            f"You MUST write ONLY in {lang_display}. Begin immediately."
        )
        answer2, refs2, fups2 = _run_llm(messages, system_extra=harder)
        if answer2:
            answer, used_refs, followups = answer2, refs2, fups2

    def _regenerate() -> str:
        ans, _, _ = _run_llm(messages, system_extra=_STRICT_ADDENDUM)
        return ans

    answer = screen_output(answer, regenerate_fn=_regenerate, persona_key=persona_key)
    answer = _strip_hallucinated_citations(answer, verses)

    if rfl_meta and rfl_meta.get("shown"):
        rfl_meta["surface_text"] = _extract_closing_question(answer)
        if rfl_meta["question_id"]:
            record_question_shown(
                user, rfl_meta["question_id"],
                rfl_meta["depth"], _get_user_prefs_safe(user),
            )

    _fire_engagement(sr, history or [], user, lang_key)

    return {
        "answer": answer,
        "citations": _build_citations(verses, used_refs),
        "followups": followups,
        "persona": persona_key,
        "persona_name": persona["name"],
        "reflective": rfl_meta,
        "engaged_prior": sr.engaged_prior,
    }


# ---------------------------------------------------------------------------
# Streaming ask_stream()
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
      data: {"token": "..."}
      data: {"replaced": "...", "answer": "..."}
      data: {"done": true, "answer": "...", "citations": [...],
             "followups": [], "persona": "...", "persona_name": "...",
             "chat_id": "..."}
    """

    def _sse(obj: dict) -> str:
        return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"

    prior_q = get_prior_question_for_classification(history or [])
    sr: ScreenResult = screen_input(question, prior_question=prior_q)
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
            "reflective": None,
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
            "reflective": None,
        }
        chat_id = on_done(result) if on_done else None
        yield _sse({"done": True, "chat_id": chat_id, **result})
        return

    lang_key, lang_display = resolve_language(safe_question, language)

    # Theme-expanded retrieval (themes come free from the safety classifier call).
    retrieval_query = f"{sr.themes} — {safe_question}" if sr.themes else safe_question
    try:
        verses = search(retrieval_query, k=k, min_score=settings.rag_similarity_threshold)
    except Exception as _rag_err:
        log.warning("RAG retrieval failed: %s — responding without citations", _rag_err)
        verses = []

    # ── Reflective question engine ─────────────────────────────────────────
    turn_count = sum(1 for t in (history or []) if t.get("role") == "assistant")
    skip, skip_reason = should_skip_question(sr, history or [], user, turn_count)

    mem_block = ""
    try:
        if user and user != "anonymous":
            profile = get_profile(user)
            mem_block = build_memory_context(user, profile.get("answer_style", "deep")) or ""
    except Exception:
        pass

    rfl_meta: dict | None = None
    system = _build_system(
        persona["name"], persona["style"], lang_key, lang_display,
        streaming=True, memory_context=mem_block,
    )

    if skip:
        if skip_reason == "continuing_prior_thread" and prior_q:
            system += build_continue_thread_instruction(prior_q, lang_display)
        else:
            system += build_skip_instruction()
    else:
        seed, on_the_fly = select_reflective_seed(sr, history or [], user, turn_count, lang_key)
        if seed and not on_the_fly:
            system += build_seed_instruction(seed, lang_display)
            rfl_meta = {
                "question_id": str(seed["_id"]),
                "shown": True,
                "depth": seed.get("depth", 1),
                "primary_theme": (seed.get("themes") or [""])[0],
                "seed_text": (seed.get("text") or {}).get("en", ""),
                "on_the_fly": False,
            }
        elif on_the_fly:
            rfl_meta = {
                "question_id": None,
                "shown": True,
                "depth": 1,
                "primary_theme": (normalize_themes(sr.themes) or ["restlessness"])[0],
                "seed_text": None,
                "on_the_fly": True,
            }
        else:
            system += build_skip_instruction()
    # ──────────────────────────────────────────────────────────────────────

    messages = _build_messages(system, history, verses, safe_question, lang_display)

    full_text = ""
    streaming_succeeded = False
    try:
        for chunk in chat_stream(messages, temperature=0.75, max_tokens=900):
            if chunk:
                streaming_succeeded = True
                full_text += chunk
                yield _sse({"token": chunk})
    except Exception as exc:
        log.warning("chat_stream failed (%s), falling back to non-streaming", exc)

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
    answer = _strip_hallucinated_citations(answer, verses)
    used_refs = re.findall(r"BG\s*\d+\.\d+", answer)

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

    def _regen() -> str:
        return _clean_answer(chat(messages, temperature=0.5, max_tokens=900))

    moderated = screen_output(answer, regenerate_fn=_regen, persona_key=persona_key)
    if moderated != answer:
        answer = moderated
        yield _sse({"replaced": "let me say that again…", "answer": answer})

    citations = _build_citations(verses, used_refs)

    # Capture surface_text and record the question shown
    if rfl_meta and rfl_meta.get("shown"):
        rfl_meta["surface_text"] = _extract_closing_question(answer)
        if rfl_meta.get("question_id"):
            record_question_shown(
                user, rfl_meta["question_id"],
                rfl_meta["depth"], _get_user_prefs_safe(user),
            )

    # Fire async engagement update for the prior question (non-blocking)
    _fire_engagement(sr, history or [], user, lang_key)

    result = {
        "answer": answer,
        "citations": citations,
        "followups": [],
        "persona": persona_key,
        "persona_name": persona["name"],
        "reflective": rfl_meta,
        "engaged_prior": sr.engaged_prior,
    }
    chat_id = on_done(result) if on_done else None
    yield _sse({"done": True, "chat_id": chat_id, **result})
