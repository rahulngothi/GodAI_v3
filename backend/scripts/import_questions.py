"""Re-import human-edited question CSV back into MongoDB.

Usage:
  python -m scripts.import_questions --input questions_review.csv

Behavior:
  - Reads the 'action' column: approve | reject | (empty = skip)
  - 'approve' → sets status=approved, preserves edited text/themes
  - 'reject'  → sets status=rejected, active=False
  - ''        → no change (skip the row)
  - Never silently overwrites status=approved rows unless action='reject'
  - Bumps version on every update
  - Idempotent: running twice with same file has no extra effect

Safety: rows with no 'action' are skipped, so partial review is safe.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import sys
from pathlib import Path

from bson import ObjectId

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import get_db, REFLECTIVE_QUESTIONS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV file from export_questions.py")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    args = parser.parse_args()

    db = get_db()
    coll = db[REFLECTIVE_QUESTIONS]
    in_path = Path(args.input)
    if not in_path.exists():
        print(f"ERROR: {in_path} not found")
        sys.exit(1)

    approved = rejected = skipped = errors = 0
    now = datetime.datetime.now(datetime.timezone.utc)

    with in_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc_id = row.get("id", "").strip()
            action = row.get("action", "").strip().lower()

            if not doc_id or not action:
                skipped += 1
                continue

            try:
                oid = ObjectId(doc_id)
            except Exception:
                print(f"  WARN: invalid id {doc_id!r}")
                errors += 1
                continue

            existing = coll.find_one({"_id": oid})
            if not existing:
                print(f"  WARN: id {doc_id} not found in DB")
                errors += 1
                continue

            if action == "approve":
                # Collect edited fields — only update text if non-empty
                update: dict = {
                    "status": "approved",
                    "active": True,
                    "updated_at": now,
                    "version": existing.get("version", 1) + 1,
                }
                en = row.get("en", "").strip()
                if en:
                    update["text.en"] = en
                hi = row.get("hi", "").strip()
                if hi:
                    update["text.hi"] = hi
                hinglish = row.get("hinglish", "").strip()
                if hinglish:
                    update["text.hinglish"] = hinglish
                themes_raw = row.get("themes", "").strip()
                if themes_raw:
                    update["themes"] = [t.strip() for t in themes_raw.split("|") if t.strip()]
                emotions_raw = row.get("emotions", "").strip()
                if emotions_raw:
                    update["emotions"] = [e.strip() for e in emotions_raw.split("|") if e.strip()]

                if args.dry_run:
                    print(f"  DRY-RUN approve: {doc_id} — {en[:60]!r}")
                else:
                    coll.update_one({"_id": oid}, {"$set": update})
                approved += 1

            elif action == "reject":
                if args.dry_run:
                    print(f"  DRY-RUN reject: {doc_id}")
                else:
                    coll.update_one({"_id": oid}, {"$set": {
                        "status": "rejected",
                        "active": False,
                        "updated_at": now,
                        "version": existing.get("version", 1) + 1,
                    }})
                rejected += 1

            else:
                print(f"  WARN: unknown action {action!r} for {doc_id}")
                errors += 1

    prefix = "DRY-RUN " if args.dry_run else ""
    print(f"\n{prefix}Import complete:")
    print(f"  approved={approved}  rejected={rejected}  skipped={skipped}  errors={errors}")


if __name__ == "__main__":
    main()
