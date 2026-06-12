"""Multi-Perspective Wisdom (PRD Feature 2).

One question, answered by several traditions side-by-side — each in its OWN
voice and grounded in its OWN scripture (Krishna from the Gita, Buddha from the
Dhammapada, etc.), never borrowing another tradition's verses.
"""
from __future__ import annotations

import json
import re

from .languages import lang_name
from .nvidia import chat
from .retrieval import search

# Each tradition retrieves only from its own source(s). When a text isn't in the
# corpus yet (Upanishads for Shankara, Vivekananda's works), we fall back to the
# Gita, which both genuinely commented on / taught.
TRADITIONS = [
    {"key": "krishna", "name": "Krishna", "sources": ["Bhagavad Gita"],
     "lens": "selfless action and loving surrender — act without attachment to results; the eternal Self is untouched by loss."},
    {"key": "buddha", "name": "Buddha", "sources": ["Dhammapada"],
     "lens": "the Middle Way — suffering is born of craving and clinging; freedom comes from seeing impermanence and letting go, with compassion."},
    {"key": "shankara", "name": "Adi Shankaracharya", "sources": ["Upanishads"],
     "lens": "Advaita (non-dual) Vedanta — the changing world is appearance; you are the one Self (Brahman); sorrow dissolves in that knowledge."},
    {"key": "vivekananda", "name": "Swami Vivekananda", "sources": ["Vivekananda (Complete Works)"],
     "lens": "practical Vedanta — you are already divine and free; rise in strength, and turn work and service into worship."},
    {"key": "modern", "name": "Modern Interpretation", "sources": None,
     "lens": "contemporary psychology and practical daily life — a concrete, compassionate, secular reading."},
]

_SYSTEM = """You are a council of {n} wisdom traditions, each answering the SAME question in its OWN authentic voice. CRUCIAL: each tradition may use ONLY its own passages, listed under its name below. Buddha speaks ONLY from the Dhammapada; Krishna ONLY from the Gita; and so on. NEVER let one tradition quote another's scripture.

{blocks}

RULES:
- You MUST return ALL {n} traditions, in order, each with a non-empty view. Do not skip any.
- Each view: 40-70 words, alive and in that tradition's distinct voice (first person where natural). Keep them concise so all {n} fit.
- Ground each view ONLY in that tradition's own passages above. After a specific teaching, tag its source exactly as labelled, e.g. [BG 2.47] or [Dhammapada 5]. Keep tags in Latin form.
- NEVER invent verses or use another tradition's passages. If a tradition's passages don't speak to the question, let it answer briefly to the spirit of its teaching without fabricating.
- Write every view in {language}.

Respond with STRICT JSON only (all {n} entries):
{{"perspectives": [{{"key": "krishna", "view": "...", "used_refs": ["BG x.y"]}}, {{"key": "buddha", ...}}, {{"key": "shankara", ...}}, {{"key": "vivekananda", ...}}, {{"key": "modern", ...}}]}}"""


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


def perspectives(question: str, language: str = "english", per_tradition_k: int = 3) -> dict:
    # Retrieve each tradition's OWN passages.
    verses_by_key: dict[str, list[dict]] = {}
    for t in TRADITIONS:
        verses_by_key[t["key"]] = search(question, k=per_tradition_k, sources=t["sources"])

    blocks = []
    for t in TRADITIONS:
        vs = verses_by_key[t["key"]]
        src_label = " / ".join(t["sources"]) if t["sources"] else "any source"
        ctx = "\n".join(f'  [{v["ref"]}] "{v["translation"]}"' for v in vs) or "  (no specific passage — speak to the spirit of your teaching)"
        blocks.append(f'{t["name"].upper()} — speaks from {src_label}; lens: {t["lens"]}\nPASSAGES (use ONLY these):\n{ctx}')

    system = _SYSTEM.format(n=len(TRADITIONS), blocks="\n\n".join(blocks), language=lang_name(language))

    # The model occasionally mislabels keys ("Krishna", "adi_shankaracharya"…) or
    # returns malformed JSON. Normalize keys, fall back to answer ORDER, retry once.
    def _ask_model() -> list[dict]:
        raw = chat(
            [{"role": "system", "content": system}, {"role": "user", "content": f"QUESTION: {question}"}],
            temperature=0.45, max_tokens=2600,
        )
        parsed = _extract_json(raw) or {}
        items = [p for p in parsed.get("perspectives", []) if isinstance(p, dict)]
        return items

    items = _ask_model()
    if not items:
        items = _ask_model()  # one retry

    def _norm(s: str) -> str:
        return "".join(ch for ch in (s or "").lower() if ch.isalnum())

    by_key: dict[str, dict] = {}
    for p in items:
        k = _norm(p.get("key", ""))
        for t in TRADITIONS:
            if k and (k == t["key"] or t["key"] in k or k in _norm(t["name"])):
                by_key.setdefault(t["key"], p)
                break
    # Order-based fallback: if matching failed but we have the right count, zip in order.
    if len(by_key) < len(items) == len(TRADITIONS):
        by_key = {t["key"]: p for t, p in zip(TRADITIONS, items)}

    out_perspectives = []
    citations = []
    seen_refs: set[str] = set()
    for t in TRADITIONS:
        p = by_key.get(t["key"], {})
        view = (p.get("view") or "").strip()
        used = [r for r in (p.get("used_refs") or [])]
        if view:
            out_perspectives.append({"key": t["key"], "tradition": t["name"], "view": view, "used_refs": used})
        # citations: this tradition's own retrieved verses (dedup across traditions)
        used_norm = {r.replace(" ", "") for r in used}
        for v in verses_by_key[t["key"]]:
            if v["ref"] in seen_refs:
                continue
            seen_refs.add(v["ref"])
            citations.append({**v, "used": (v["ref"].replace(" ", "") in used_norm) if used_norm else True})

    return {
        "question": question,
        "language": language,
        "perspectives": out_perspectives,
        "citations": citations,
    }
