"""Daily Guidance (PRD Feature 5): verse of the day + reflection + practice + journal."""
from __future__ import annotations

import datetime as _dt
import json
import re

from .db import VERSES, get_db
from .languages import lang_name
from .nvidia import chat


def _verse_of_day() -> dict:
    col = get_db()[VERSES]
    n = col.count_documents({})
    if not n:
        raise RuntimeError("No verses available.")
    idx = _dt.date.today().toordinal() % n
    doc = next(iter(col.find().sort("_id", 1).skip(idx).limit(1)))
    return doc


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw).strip()
    s, e = raw.find("{"), raw.rfind("}")
    if s != -1 and e != -1:
        try:
            return json.loads(raw[s : e + 1])
        except Exception:
            return {}
    return {}


def daily(period: str | None = None, language: str = "english") -> dict:
    if period not in ("morning", "evening"):
        period = "morning" if _dt.datetime.now().hour < 16 else "evening"
    v = _verse_of_day()

    if period == "morning":
        ask_for = ("a 'practice' that is a short morning intention or gratitude focus for the day, "
                   "and a 'journal_prompt' to set an intention")
    else:
        ask_for = ("a 'practice' that is a short evening reflection or letting-go exercise, "
                   "and a 'journal_prompt' to look back on the day")

    system = (
        "You are a warm spiritual companion offering today's guidance from a single Bhagavad Gita verse. "
        f"Write everything in {lang_name(language)}. Ground it in the given verse; do not invent scripture. "
        "Return STRICT JSON only: {\"reflection\": \"<90-140 word warm reflection a person can read in ~2 minutes, "
        "weaving in the verse's meaning>\", \"practice\": \"<1-2 sentences>\", \"journal_prompt\": \"<one short question>\"}. "
        f"For the {period}, give {ask_for}."
    )
    user = f'Verse {v["ref"]}: "{v["translation"]}"  (translator: {v["translator"]})'
    raw = chat([{"role": "system", "content": system}, {"role": "user", "content": user}],
               temperature=0.5, max_tokens=700)
    p = _extract_json(raw)

    return {
        "date": _dt.date.today().isoformat(),
        "period": period,
        "verse": {
            "ref": v["ref"],
            "source": v.get("source", "Bhagavad Gita"),
            "chapter": v.get("chapter"),
            "verse": v.get("verse"),
            "sanskrit": v.get("sanskrit"),
            "transliteration": v.get("transliteration"),
            "translation": v["translation"],
            "translator": v["translator"],
            "used": True,
        },
        "reflection": (p.get("reflection") or "").strip(),
        "practice": (p.get("practice") or "").strip(),
        "journal_prompt": (p.get("journal_prompt") or "").strip(),
    }
