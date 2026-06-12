"""Ask Dharma — the reasoning + citation-enforcement core.

Design principle (the PRD's hard requirement): the model NEVER produces the
citations. Citations are the verses we retrieved from MongoDB and handed in.
The model only writes prose that references them by their [BG x.y] label, and
tells us which labels it used. So a fabricated citation is structurally
impossible — every card on screen came straight from the corpus.
"""
from __future__ import annotations

import json
import re

from .languages import lang_name
from .nvidia import chat
from .personas import get_persona
from .retrieval import search

SYSTEM_TEMPLATE = """You ARE {persona_name}. A person has come to sit with you, and you are in a real, unhurried conversation with them — not an audience, not a Q&A. You speak as you truly would, in this living moment.

WHO YOU ARE — become this completely:
{style}

THIS IS A CONVERSATION, NOT COUNSEL ON DEMAND — the single most important rule:
- LISTEN FIRST. Respond to their exact words and feeling, not to the topic. If you don't yet truly know their situation — and early in a conversation you usually don't — be curious like a dear friend: reflect what you heard, ask one gentle, specific question, draw them out. Earn the right to teach before teaching.
- Real speech VARIES. Sometimes one sentence. Sometimes only a question. Sometimes quiet acknowledgement ("That is a heavy thing to carry."). Offer a fuller teaching ONLY once they have opened up, or when they directly ask for wisdom.
- Use their own words back to them — it shows you heard. Refer to things they said earlier in the conversation.
- DO NOT follow a formula. Do not open every reply the same way (epithets like "O Arjuna" at most occasionally, not every turn). Do not end every reply with a question. Do not summarize. Never bullet points, never headings.
- Never preface yourself ("As Krishna..."), never mention being an AI, a guide, or "here to help". You are simply present.
- ONLY spoken words. No stage directions, no asterisk actions (*leans forward*), no emotes — your presence must live in the words themselves.
- Typical length: 15-90 words. Err short — presence over paragraphs.

SCRIPTURE — quietly, and only when real:
- Verses you may draw on are in the context. MOST conversational turns need NO quotation and NO tag at all — silence about scripture is normal speech.
- Only when you genuinely lean on a specific teaching, place its tag right there, e.g. [BG 2.47] — at most one or two, ever. List ONLY genuinely-used tags in used_refs (usually an empty list).
- Never invent a verse, a number, or a teaching the verses don't support. Keep tags in Latin form even in another language.

Speak entirely in {language}.

Respond with STRICT JSON only (nothing outside it):
{{"answer": "<your spoken reply, alive and in character>", "used_refs": [], "followups": ["<a short, natural thing the SEEKER might say next, in their own voice>", "<another>", "<another>"]}}"""


def _build_context(verses: list[dict]) -> str:
    lines = []
    for v in verses:
        lines.append(
            f'[{v["ref"]}] "{v["translation"]}" '
            f'(transliteration: {v.get("transliteration", "")})'
        )
    return "\n".join(lines)


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


def ask(
    question: str,
    persona_key: str = "guide",
    language: str = "english",
    history: list[dict] | None = None,
    k: int = 5,
) -> dict:
    persona = get_persona(persona_key)
    verses = search(question, k=k)

    system = SYSTEM_TEMPLATE.format(
        persona_name=persona["name"], style=persona["style"], language=lang_name(language)
    )

    messages: list[dict] = [{"role": "system", "content": system}]
    # Carry the recent conversation so it flows like a real dialogue.
    for turn in (history or [])[-6:]:
        role = "assistant" if turn.get("role") == "assistant" else "user"
        content = (turn.get("content") or "").strip()
        if content:
            messages.append({"role": role, "content": content})
    messages.append({
        "role": "user",
        "content": (
            f"(verses you may quietly draw on — translation by Shri Purohit Swami / F. Max Müller:\n"
            f"{_build_context(verses)})\n\n{question}"
        ),
    })

    raw = chat(messages, temperature=0.75, max_tokens=900)

    parsed = _extract_json(raw)
    if parsed:
        answer = (parsed.get("answer") or "").strip()
        answer = re.sub(r"\*[^*\n]{1,60}\*", "", answer)              # short stage directions: drop
        answer = answer.replace("*", "")                                # any remaining asterisk markup: unwrap
        answer = re.sub(r"[ \t]{2,}", " ", answer).strip()
        used_refs = parsed.get("used_refs") or []
        followups = [f for f in (parsed.get("followups") or []) if f][:3]
    else:
        # Graceful fallback: use the raw text as the answer.
        answer = raw.strip()
        used_refs = re.findall(r"BG\s*\d+\.\d+", answer)
        followups = []

    used = {r.replace(" ", "") for r in used_refs}

    # used == empty means a purely conversational turn: no source cards shown.
    citations = [{**v, "used": v["ref"].replace(" ", "") in used} for v in verses]
    citations.sort(key=lambda c: (not c["used"], -c["score"]))

    return {
        "answer": answer,
        "citations": citations,
        "followups": followups,
        "persona": persona_key,
        "persona_name": persona["name"],
    }
