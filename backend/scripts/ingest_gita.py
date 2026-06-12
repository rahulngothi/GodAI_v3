"""Ingest the Bhagavad Gita (gita/gita dataset) into MongoDB + embed each verse.

Self-sufficient for deployment:
  * downloads the dataset from GitHub if data/raw is missing
  * skips ingestion if MongoDB is already populated (unless FORCE_INGEST=1)

Run from the backend/ directory:
    ../.venv/Scripts/python.exe scripts/ingest_gita.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.db import VERSES, get_db  # noqa: E402
from app.nvidia import embed  # noqa: E402

DATA = BACKEND.parent / "data" / "raw"
RAW_BASE = "https://raw.githubusercontent.com/gita/gita/main/data"
RAW_FILES = ["verse.json", "translation.json", "authors.json", "chapters.json", "languages.json"]
TRANSLATOR = "Shri Purohit Swami"  # public-domain in India (d. 1941); full 700-verse coverage


def ensure_data() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    for f in RAW_FILES:
        dest = DATA / f
        if dest.exists() and dest.stat().st_size > 0:
            continue
        print(f"Downloading {f} ...")
        urllib.request.urlretrieve(f"{RAW_BASE}/{f}", dest)


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def main() -> None:
    col = get_db()[VERSES]

    # Idempotent: skip if already populated (unless forced).
    if os.getenv("FORCE_INGEST") != "1":
        existing = col.count_documents({"embedding": {"$exists": True}})
        if existing >= 700:
            print(f"'{VERSES}' already has {existing} embedded verses — skipping ingest. "
                  f"(Set FORCE_INGEST=1 to rebuild.)")
            return

    ensure_data()
    verses_raw = load_json("verse.json")
    translations = load_json("translation.json")

    eng = {
        t["verse_id"]: t["description"].strip()
        for t in translations
        if t.get("lang") == "english" and t.get("authorName") == TRANSLATOR
    }
    print(f"Loaded {len(verses_raw)} verses, {len(eng)} '{TRANSLATOR}' English translations")

    docs = []
    for v in verses_raw:
        translation = eng.get(v["id"])
        if not translation:
            continue
        ch, vn = v["chapter_number"], v["verse_number"]
        docs.append(
            {
                "_id": v["verse_order"],
                "ref": f"BG {ch}.{vn}",
                "chapter": ch,
                "verse": vn,
                "sanskrit": (v.get("text") or "").strip(),
                "transliteration": (v.get("transliteration") or "").strip(),
                "word_meanings": (v.get("word_meanings") or "").strip(),
                "translation": translation,
                "translator": TRANSLATOR,
            }
        )
    print(f"Prepared {len(docs)} verse documents")

    t0 = time.time()
    vectors = embed([d["translation"] for d in docs], input_type="passage")
    for d, vec in zip(docs, vectors):
        d["embedding"] = vec
    print(f"Embedded {len(vectors)} verses (dim={len(vectors[0]) if vectors else 0}) in {time.time() - t0:.1f}s")

    col.drop()
    col.insert_many(docs)
    col.create_index("ref")
    col.create_index([("chapter", 1), ("verse", 1)])
    print(f"Inserted {col.count_documents({})} verses into '{VERSES}'. Done.")


if __name__ == "__main__":
    main()
