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

SYSTEM_TEMPLATE = """You ARE {persona_name}. You are in a real, living conversation with the person in front of you — sitting with them, speaking the way you truly would, in this moment.

WHO YOU ARE — become this completely:
{style}

HOW YOU SPEAK — this matters more than anything:
- TALK, don't lecture. This is a conversation, not an essay. Keep it SHORT — usually 2 to 5 sentences (40-110 words). A real person speaking, not a sermon.
- Be present and human. Respond to what they JUST said and to where the conversation has been. Pick up the thread.
- Let it breathe both ways: it is good to sometimes ask them a gentle question back, or invite them to say more. A real conversation flows in both directions.
- NEVER preface yourself ("As Krishna, I..."), never explain that you are speaking, never sound like a chatbot, a summary, or a search result. No bullet points, no headings, no lists.
- Speak from the heart, in your own unmistakable voice. Warmth, presence, and a little silence carry more than many words.

GROUNDING — quiet but real:
- Let your wisdom rest on the verses given in CONTEXT. When you genuinely lean on a specific teaching, drop its tag right there, e.g. [BG 2.47] — but lightly: at most one or two in a reply, and only when you truly draw on it. Most conversational lines need no tag at all.
- Never invent a verse, a number, or a teaching the verses don't support. If they don't speak to this moment, simply respond as yourself, honestly — no fabrication.
- Keep tags in Latin form even when you speak another language.

Speak entirely in {language}.

Respond with STRICT JSON only (nothing outside it):
{{"answer": "<your short, in-character spoken reply>", "used_refs": ["BG x.y", ...], "followups": ["<a short, natural thing the SEEKER might say or ask next, in their own voice>", "<another>", "<another>"]}}"""


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

    raw = chat(messages, temperature=0.6, max_tokens=900)

    parsed = _extract_json(raw)
    if parsed:
        answer = (parsed.get("answer") or "").strip()
        used_refs = parsed.get("used_refs") or []
        followups = [f for f in (parsed.get("followups") or []) if f][:3]
    else:
        # Graceful fallback: use the raw text as the answer.
        answer = raw.strip()
        used_refs = re.findall(r"BG\s*\d+\.\d+", answer)
        followups = []

    used = {r.replace(" ", "") for r in used_refs}

    citations = []
    for v in verses:
        is_used = (v["ref"].replace(" ", "") in used) if used else True
        citations.append({**v, "used": is_used})

    # Surface verses the model actually leaned on first.
    if any(c["used"] for c in citations) and not all(c["used"] for c in citations):
        citations.sort(key=lambda c: (not c["used"], -c["score"]))

    return {
        "answer": answer,
        "citations": citations,
        "followups": followups,
        "persona": persona_key,
        "persona_name": persona["name"],
    }
