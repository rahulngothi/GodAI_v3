"""Engagement tracking and the learning loop.

Responsibilities:
  1. Process the engaged_prior signal from ScreenResult and update the question's
     stats (shown_count, answered_count, engagement_rate) in the library.
  2. Update per-user reflective_prefs (rolling avg, frequency adaptation).
  3. Auto-demote persistently poor questions to status=needs_review.
  4. Auto-capture runtime_captured questions from on-the-fly generations.

All writes are fire-and-forget (called via threading.Thread from ask.py).
No latency is added to the hot path.

Engagement levels (from llm_classify):
  ignored         → 0.0 score
  deflected       → 0.2
  acknowledged    → 0.5
  engaged         → 0.8
  deeply_engaged  → 1.0
"""
from __future__ import annotations

import datetime
import logging
import threading
from typing import TYPE_CHECKING

from bson import ObjectId

from .config import settings
from .db import get_db, REFLECTIVE_QUESTIONS, USER_PROFILES

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Engagement level → numeric score
# ---------------------------------------------------------------------------
ENGAGEMENT_SCORES: dict[str, float] = {
    "ignored":        0.0,
    "deflected":      0.2,
    "acknowledged":   0.5,
    "engaged":        0.8,
    "deeply_engaged": 1.0,
}

# Levels that count as "answered" (seeker responded substantively)
_ANSWERED_LEVELS = {"acknowledged", "engaged", "deeply_engaged"}


# ---------------------------------------------------------------------------
# Core update — runs in a background thread, never blocks the response
# ---------------------------------------------------------------------------
def _update_question_stats(question_id: str, engagement_level: str) -> None:
    """Increment shown/answered counts and recalculate engagement_rate."""
    try:
        db = get_db()
        coll = db[REFLECTIVE_QUESTIONS]
        oid = ObjectId(question_id)
        doc = coll.find_one({"_id": oid}, {"stats": 1, "status": 1})
        if not doc:
            return

        stats = doc.get("stats", {})
        shown = stats.get("shown_count", 0) + 1
        answered = stats.get("answered_count", 0)
        if engagement_level in _ANSWERED_LEVELS:
            answered += 1

        rate = answered / shown if shown > 0 else 0.0
        now = datetime.datetime.now(datetime.timezone.utc)

        update: dict = {
            "stats.shown_count": shown,
            "stats.answered_count": answered,
            "stats.engagement_rate": round(rate, 4),
            "stats.last_shown_at": now,
            "updated_at": now,
        }

        # Auto-demote: persistently poor engagement after enough shows
        current_status = doc.get("status", "approved")
        if (current_status == "approved"
                and shown >= settings.rqe_demote_min_shows
                and rate < settings.rqe_demote_max_rate):
            update["status"] = "needs_review"
            log.info(
                "Auto-demoted question %s: shown=%d rate=%.2f (threshold=%.2f)",
                question_id, shown, rate, settings.rqe_demote_max_rate,
            )

        coll.update_one({"_id": oid}, {"$set": update})
    except Exception as exc:
        log.warning("_update_question_stats failed for %s: %s", question_id, exc)


def _update_user_prefs(user_id: str, engagement_level: str) -> None:
    """Update rolling engagement average and adapt frequency."""
    try:
        db = get_db()
        doc = db[USER_PROFILES].find_one({"_id": user_id}, {"reflective_prefs": 1})
        prefs = (doc or {}).get("reflective_prefs", {}) if doc else {}

        score = ENGAGEMENT_SCORES.get(engagement_level, 0.5)
        prev_avg = prefs.get("avg_engagement", 0.5)
        # Exponential moving average (α=0.2 — slow drift, responsive to trends)
        new_avg = round(0.8 * prev_avg + 0.2 * score, 4)

        # Frequency adaptation:
        #   avg < 0.2 for a while → reduce (too many ignored questions)
        #   avg > 0.6 consistently → normal (user engages well)
        current_freq = prefs.get("frequency", "normal")
        new_freq = current_freq
        if new_avg < 0.2 and current_freq == "normal":
            new_freq = "reduced"
            log.info("User %s frequency → reduced (avg_engagement=%.2f)", user_id, new_avg)
        elif new_avg >= 0.5 and current_freq == "reduced":
            new_freq = "normal"
            log.info("User %s frequency → normal (avg_engagement=%.2f)", user_id, new_avg)

        db[USER_PROFILES].update_one(
            {"_id": user_id},
            {"$set": {
                "reflective_prefs.avg_engagement": new_avg,
                "reflective_prefs.frequency": new_freq,
            }},
            upsert=True,
        )
    except Exception as exc:
        log.warning("_update_user_prefs failed for %s: %s", user_id, exc)


def _capture_on_the_fly(
    surface_text: str,
    primary_theme: str,
    depth: int,
    lang_key: str,
) -> None:
    """Save a runtime-generated question into the library as needs_review."""
    if not surface_text or "?" not in surface_text:
        return
    try:
        db = get_db()
        coll = db[REFLECTIVE_QUESTIONS]

        # Exact-text dedup
        if coll.find_one({"text.en": surface_text}):
            return

        now = datetime.datetime.now(datetime.timezone.utc)
        text_field: dict = {"en": surface_text}
        if lang_key == "hindi":
            text_field = {"en": None, "hi": surface_text, "hinglish": None}
        elif lang_key == "hinglish":
            text_field = {"en": None, "hi": None, "hinglish": surface_text}

        _INTENSITY_FLOORS = {1: "any", 2: "mild", 3: "moderate"}
        doc = {
            "text": text_field,
            "themes": [primary_theme] if primary_theme else ["restlessness"],
            "type": "self_awareness",
            "depth": depth,
            "intensity_safe_floor": _INTENSITY_FLOORS.get(depth, "any"),
            "emotions": [],
            "concepts": [],
            "persona_fit": [],
            "related_verses": [],
            "status": "needs_review",
            "source": "runtime_captured",
            "stats": {
                "shown_count": 0,
                "answered_count": 0,
                "engagement_rate": 0.0,
                "last_shown_at": None,
            },
            "active": False,  # inactive until reviewed
            "created_at": now,
            "updated_at": now,
            "version": 1,
        }
        coll.insert_one(doc)
        log.info("Captured runtime question for review: %s…", surface_text[:60])
    except Exception as exc:
        log.warning("_capture_on_the_fly failed: %s", exc)


# ---------------------------------------------------------------------------
# Public entry point — called from ask.py, non-blocking
# ---------------------------------------------------------------------------
def process_engagement(
    *,
    user_id: str,
    question_id: str | None,
    engagement_level: str | None,
    on_the_fly: bool = False,
    surface_text: str | None = None,
    primary_theme: str | None = None,
    depth: int = 1,
    lang_key: str = "english",
) -> None:
    """Fire-and-forget engagement processing. Never raises; never blocks."""
    if not engagement_level:
        return

    # Normalize to valid level; default to 'acknowledged' if ambiguous
    valid_levels = set(ENGAGEMENT_SCORES.keys())
    if engagement_level not in valid_levels:
        engagement_level = "acknowledged"

    def _run() -> None:
        if question_id and not on_the_fly:
            _update_question_stats(question_id, engagement_level)

        _update_user_prefs(user_id, engagement_level)

        # Capture on-the-fly questions for the review queue if they got engagement
        if on_the_fly and surface_text and engagement_level in _ANSWERED_LEVELS:
            _capture_on_the_fly(surface_text, primary_theme or "restlessness", depth, lang_key)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()


__all__ = ["process_engagement", "ENGAGEMENT_SCORES"]
