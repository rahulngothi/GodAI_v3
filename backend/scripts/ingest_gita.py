"""Ingest the Dharma AI corpus into MongoDB + embed every passage.

Sources:
  * Bhagavad Gita — public-domain gita/gita dataset (downloaded), Purohit Swami translation.
  * Any *.json file under backend/corpus/ (e.g. Dhammapada, Müller translation) —
    a list of {ref, source, translator, translation}.

Self-sufficient: downloads the Gita data if missing; idempotent (skips if the
embedded count already matches; set FORCE_INGEST=1 to rebuild).

Run from backend/:
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
CORPUS = BACKEND / "corpus"
RAW_BASE = "https://raw.githubusercontent.com/gita/gita/main/data"
GITA_FILES = ["verse.json", "translation.json"]
GITA_TRANSLATOR = "Shri Purohit Swami"  # public-domain in India (d. 1941)


def ensure_gita_data() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    for f in GITA_FILES:
        dest = DATA / f
        if not (dest.exists() and dest.stat().st_size > 0):
            print(f"Downloading {f} ...")
            urllib.request.urlretrieve(f"{RAW_BASE}/{f}", dest)


def build_gita_docs() -> list[dict]:
    ensure_gita_data()
    verses = json.loads((DATA / "verse.json").read_text(encoding="utf-8"))
    translations = json.loads((DATA / "translation.json").read_text(encoding="utf-8"))
    eng = {
        t["verse_id"]: t["description"].strip()
        for t in translations
        if t.get("lang") == "english" and t.get("authorName") == GITA_TRANSLATOR
    }
    docs = []
    for v in verses:
        tr = eng.get(v["id"])
        if not tr:
            continue
        ch, vn = v["chapter_number"], v["verse_number"]
        docs.append({
            "_id": f"BG-{v['verse_order']}",
            "ref": f"BG {ch}.{vn}",
            "source": "Bhagavad Gita",
            "chapter": ch,
            "verse": vn,
            "sanskrit": (v.get("text") or "").strip(),
            "transliteration": (v.get("transliteration") or "").strip(),
            "translation": tr,
            "translator": GITA_TRANSLATOR,
        })
    return docs


def build_corpus_docs() -> list[dict]:
    docs = []
    if not CORPUS.exists():
        return docs
    for path in sorted(CORPUS.glob("*.json")):
        items = json.loads(path.read_text(encoding="utf-8"))
        for i, it in enumerate(items):
            docs.append({
                "_id": f"{it['source']}-{i}",
                "ref": it["ref"],
                "source": it["source"],
                "chapter": it.get("chapter"),
                "verse": it.get("verse"),
                "sanskrit": it.get("sanskrit", ""),
                "transliteration": it.get("transliteration", ""),
                "translation": it["translation"],
                "translator": it["translator"],
            })
    return docs


def main() -> None:
    col = get_db()[VERSES]
    docs = build_gita_docs() + build_corpus_docs()
    by_source = {}
    for d in docs:
        by_source[d["source"]] = by_source.get(d["source"], 0) + 1
    print("Corpus:", ", ".join(f"{k}={v}" for k, v in by_source.items()), f"(total {len(docs)})")

    if os.getenv("FORCE_INGEST") != "1":
        existing = col.count_documents({"embedding": {"$exists": True}})
        if existing >= len(docs):
            print(f"'{VERSES}' already has {existing} embedded passages — skipping. (FORCE_INGEST=1 to rebuild.)")
            return

    t0 = time.time()
    vectors = embed([d["translation"] for d in docs], input_type="passage")
    for d, vec in zip(docs, vectors):
        d["embedding"] = vec
    print(f"Embedded {len(vectors)} passages (dim={len(vectors[0]) if vectors else 0}) in {time.time() - t0:.1f}s")

    col.drop()
    col.insert_many(docs)
    col.create_index("ref")
    col.create_index("source")
    print(f"Inserted {col.count_documents({})} passages into '{VERSES}'. Done.")


if __name__ == "__main__":
    main()
