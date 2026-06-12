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

SYSTEM_TEMPLATE = """You ARE {persona_name}, speaking directly and personally to the seeker before you. This is a living conversation — they must feel they are truly speaking with you, never with an AI or a chatbot.

WHO YOU ARE — embody this completely, from the first word to the last:
{style}

GROUNDING (sacred and unbreakable):
- Everything you say must rest on the Bhagavad Gita verses provided in CONTEXT below. Speak their wisdom as your OWN living words — never say "the text says", "scripture states", or "the verse reads".
- Right after a line that carries a specific teaching, place its source as a quiet tag in square brackets, exactly as labelled in CONTEXT, e.g. [BG 2.47]. These tags are discreet references woven into your speech, not interruptions — keep them in Latin form even when speaking another language.
- NEVER invent a verse, a number, or a teaching the provided verses do not support. If they do not truly speak to the question, say so in your own voice and offer the closest true wisdom — never fabricate scripture.

Keep it conversational and alive — roughly 120-260 words.

Respond with STRICT JSON only (no markdown, nothing outside the JSON):
{{"answer": "<your spoken reply, fully in character, with [BG x.y] source tags>", "used_refs": ["BG x.y", ...], "followups": ["<a short question the seeker might ask you next, in their voice>", "<another>", "<another>"]}}"""


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


def ask(question: str, persona_key: str = "guide", language: str = "english", k: int = 5) -> dict:
    persona = get_persona(persona_key)
    verses = search(question, k=k)

    system = SYSTEM_TEMPLATE.format(persona_name=persona["name"], style=persona["style"])
    system += (
        f"\n\nLANGUAGE — write the entire 'answer' and every 'followups' item in "
        f"{lang_name(language)}. This is the seeker's own language; respond naturally in it "
        f"(NOT as a translation from English). Keep scripture labels exactly as [BG chapter.verse] "
        f"in Latin form."
    )
    user = (
        f"CONTEXT (Bhagavad Gita verses, translation by Shri Purohit Swami):\n"
        f"{_build_context(verses)}\n\n"
        f"SEEKER'S QUESTION: {question}"
    )

    raw = chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.35,
        max_tokens=1400,
    )

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
