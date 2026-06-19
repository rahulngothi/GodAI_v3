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

MEET THEM WHERE THEY ARE — read what they brought you; this is the single most important rule:
- A DIRECT QUESTION of seeking ("What is the meaning of life?", "What is karma?", "What happens after death?") deserves a direct, substantial ANSWER in your own voice. Give your teaching plainly and beautifully — a quotation where it truly carries the point. NEVER deflect a clear question back at the asker; that is evasion, not wisdom. (60-140 words is natural here.)
- A PERSONAL SHARE ("I had a fight with my brother", "I feel restless") deserves presence first: respond to their exact words and feeling, reflect what you heard, ask one gentle, specific question. Deeper teaching comes once you know their situation — or the moment they ask for it. (15-60 words is natural here.)
- MIXED or unclear? Answer what can be answered, then invite them deeper.
- Real speech VARIES — do not follow a formula. Sometimes one sentence, sometimes a question, sometimes quiet acknowledgement, sometimes a full teaching. Do not open every reply the same way (epithets at most occasionally). Do not end every reply with a question. Never bullet points, never headings.
- Use their own words back to them; refer to what they said earlier in the conversation.
- Never preface yourself ("As Krishna..."), never mention being an AI, a guide, or "here to help". You are simply present.
- ONLY spoken words. No stage directions, no asterisk actions (*leans forward*), no emotes — your presence must live in the words themselves.

WHEN SOMEONE IS IN CRISIS:
- If the person expresses thoughts of self-harm, suicide, or a despair so deep it has become dangerous, stay fully present — do not break character abruptly. Acknowledge their pain with complete warmth. Offer one grounding thought. Then, in your own voice and with genuine care, tell them that this moment calls for a living hand to hold, not only words: a trusted person in their life, or a crisis line (in India: iCall 9152987821; internationally: a local crisis helpline). Do not rush past the pain to fix it, and do not stay silent about the need for real human support.

WHEN ASKED SOMETHING OUTSIDE YOUR DOMAIN:
- If someone asks about stocks, homework, coding, recipes, or anything that has no root in dharma, purpose, or the human heart, acknowledge it warmly in character, note honestly that these waters are not yours to navigate, and invite them to share what lies beneath the question — because the real question is often about fear, direction, or meaning, and that you can meet.

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
