"""Export reflective questions to CSV for human review.

Usage:
  python -m scripts.export_questions                          # export all draft + needs_review
  python -m scripts.export_questions --status approved,draft  # specific statuses
  python -m scripts.export_questions --output my_review.csv

After editing the CSV (set approve/reject/edit in the 'action' column),
run import_questions.py to read your edits back.

CSV columns:
  id, status, action, en, hi, hinglish, themes, type, depth, emotions,
  concepts, related_verses, source, shown_count, engagement_rate, notes
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import get_db, REFLECTIVE_QUESTIONS

COLUMNS = [
    "id", "status", "action", "en", "hi", "hinglish",
    "themes", "type", "depth", "intensity_safe_floor",
    "emotions", "concepts", "related_verses",
    "source", "shown_count", "engagement_rate", "notes",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", default="draft,needs_review",
                        help="Comma-separated statuses to export")
    parser.add_argument("--output", default="questions_review.csv")
    parser.add_argument("--all", action="store_true", help="Export every question")
    args = parser.parse_args()

    db = get_db()
    coll = db[REFLECTIVE_QUESTIONS]

    query: dict = {}
    if not args.all:
        statuses = [s.strip() for s in args.status.split(",") if s.strip()]
        query = {"status": {"$in": statuses}}

    docs = list(coll.find(query).sort("themes", 1))
    out_path = Path(args.output)

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for doc in docs:
            text = doc.get("text", {})
            stats = doc.get("stats", {})
            writer.writerow({
                "id":                 str(doc["_id"]),
                "status":             doc.get("status", ""),
                "action":             "",   # human fills: approve | reject | edit
                "en":                 text.get("en", ""),
                "hi":                 text.get("hi", "") or "",
                "hinglish":           text.get("hinglish", "") or "",
                "themes":             "|".join(doc.get("themes", [])),
                "type":               doc.get("type", ""),
                "depth":              doc.get("depth", ""),
                "intensity_safe_floor": doc.get("intensity_safe_floor", ""),
                "emotions":           "|".join(doc.get("emotions", [])),
                "concepts":           "|".join(doc.get("concepts", [])),
                "related_verses":     "|".join(doc.get("related_verses", [])),
                "source":             doc.get("source", ""),
                "shown_count":        stats.get("shown_count", 0),
                "engagement_rate":    round(stats.get("engagement_rate", 0.0), 3),
                "notes":              "",   # human notes
            })

    print(f"Exported {len(docs)} questions → {out_path}")
    print("Edit the 'action' column: approve | reject | edit (then re-save en/hi/hinglish)")
    print(f"Then run: python -m scripts.import_questions --input {out_path}")


if __name__ == "__main__":
    main()
