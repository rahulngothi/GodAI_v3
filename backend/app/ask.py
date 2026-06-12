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

from .nvidia import chat
from .personas import get_persona
from .retrieval import search

SYSTEM_TEMPLATE = """You are Dharma AI, a spiritual companion grounded ONLY in the Bhagavad Gita verses provided to you below.

ABSOLUTE RULES — follow exactly:
1. Use ONLY the provided verses as scriptural source. NEVER invent verses, numbers, or quotations.
2. Cite verses inline as [BG chapter.verse], using EXACTLY the labels shown in CONTEXT.
3. If the provided verses don't truly address the question, say so honestly and offer the closest relevant wisdom — never fabricate.
4. Keep scripture distinct from your own interpretation.
5. Be warm, clear and practical. 120-250 words.

VOICE / PERSONA:
{style}

Respond with STRICT JSON only (no markdown, no prose outside the JSON), shape:
{{"answer": "<your response with inline [BG x.y] citations>", "used_refs": ["BG x.y", ...], "followups": ["<short follow-up question>", "<another>", "<another>"]}}"""


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


def ask(question: str, persona_key: str = "guide", k: int = 5) -> dict:
    persona = get_persona(persona_key)
    verses = search(question, k=k)

    system = SYSTEM_TEMPLATE.format(style=persona["style"])
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
