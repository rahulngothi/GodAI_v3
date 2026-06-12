"""Multi-Perspective Wisdom (PRD Feature 2).

One question, answered by several traditions side-by-side — each in its own
authentic voice, all grounded in the same retrieved verses. A single Kimi call
produces all views, so they share one set of cited sources.
"""
from __future__ import annotations

import json
import re

from .languages import lang_name
from .nvidia import chat
from .retrieval import search

TRADITIONS = [
    {"key": "krishna", "name": "Krishna",
     "lens": "the Gita's path of selfless action and loving surrender — act without attachment to results; the eternal Self is never touched by loss."},
    {"key": "buddha", "name": "Buddha",
     "lens": "the Middle Way — suffering is born of craving and clinging; freedom comes from seeing impermanence and letting go, with compassion."},
    {"key": "shankara", "name": "Adi Shankaracharya",
     "lens": "Advaita Vedanta — the changing world is appearance; you are the one non-dual Self (Brahman); sorrow dissolves in that knowledge."},
    {"key": "vivekananda", "name": "Swami Vivekananda",
     "lens": "practical Vedanta — you are already divine and free; rise in strength, and turn work and service into worship."},
    {"key": "modern", "name": "Modern Interpretation",
     "lens": "contemporary psychology and practical daily life — a concrete, compassionate, secular reading of the same wisdom."},
]

_SYSTEM = """You are a council of {n} wisdom traditions, each answering the SAME question in its OWN authentic voice, all grounded ONLY in the Bhagavad Gita verses given in CONTEXT.

The traditions, in order, and the lens each speaks from:
{lenses}

RULES:
- Each view: 45-85 words, alive and in that tradition's distinct voice (first person where natural for Krishna/Buddha/Vivekananda).
- Ground every view in the provided verses. After a specific teaching, place its source tag exactly as labelled in CONTEXT, e.g. [BG 2.47]. Keep tags in Latin form.
- NEVER invent verses, numbers, or teachings the verses don't support. If a tradition has little from these verses, let it speak briefly to the spirit without fabricating.
- Write every view in {language}. Keep the [BG x.y] tags in Latin form.

Respond with STRICT JSON only:
{{"perspectives": [{{"key": "krishna", "view": "...", "used_refs": ["BG x.y"]}}, ... all {n} in order]}}"""


def _context(verses: list[dict]) -> str:
    return "\n".join(f'[{v["ref"]}] "{v["translation"]}"' for v in verses)


def _extract_json(raw: str) -> dict | None:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw).strip()
    s, e = raw.find("{"), raw.rfind("}")
    if s != -1 and e != -1 and e > s:
        try:
            return json.loads(raw[s : e + 1])
        except Exception:
            return None
    return None


def perspectives(question: str, language: str = "english", k: int = 6) -> dict:
    verses = search(question, k=k)
    lenses = "\n".join(f'- {t["name"]}: {t["lens"]}' for t in TRADITIONS)
    system = _SYSTEM.format(n=len(TRADITIONS), lenses=lenses, language=lang_name(language))
    user = (
        f"CONTEXT (Bhagavad Gita verses, translation by Shri Purohit Swami):\n"
        f"{_context(verses)}\n\nQUESTION: {question}"
    )
    raw = chat([{"role": "system", "content": system}, {"role": "user", "content": user}],
               temperature=0.4, max_tokens=1800)
    parsed = _extract_json(raw) or {}
    by_key = {p.get("key"): p for p in parsed.get("perspectives", []) if isinstance(p, dict)}

    out_perspectives = []
    all_used: set[str] = set()
    for t in TRADITIONS:
        p = by_key.get(t["key"], {})
        view = (p.get("view") or "").strip()
        used = [r for r in (p.get("used_refs") or [])]
        for r in used:
            all_used.add(r.replace(" ", ""))
        if view:
            out_perspectives.append({"key": t["key"], "tradition": t["name"], "view": view, "used_refs": used})

    citations = []
    for v in verses:
        citations.append({**v, "used": v["ref"].replace(" ", "") in all_used if all_used else True})

    return {
        "question": question,
        "language": language,
        "perspectives": out_perspectives,
        "citations": citations,
    }
