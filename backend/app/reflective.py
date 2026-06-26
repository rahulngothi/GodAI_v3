"""Reflective Question Engine — selection, gate, and seed-injection logic.

This module runs in the hot path but adds zero LLM calls.
All work is indexed MongoDB queries + in-process ranking.

Public API:
  select_reflective_seed(sr, history, user_id, turn_count, lang_key)
    → (seed_doc | None, on_the_fly: bool)

  build_seed_instruction(seed, lang_display)
    → str to append to the system prompt

  should_skip_question(sr, history, user_id, turn_count)
    → bool (True = no question this turn)
"""
from __future__ import annotations

import logging
import random
import re
from typing import TYPE_CHECKING

from .config import settings
from .db import get_db, REFLECTIVE_QUESTIONS, USER_PROFILES
from .themes import normalize_themes

if TYPE_CHECKING:
    from .safety import ScreenResult

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Distress level classification (from ScreenResult + heuristics)
# ---------------------------------------------------------------------------
_DISTRESS_WORDS = {
    "acute": {
        "devastated", "shattered", "can't go on", "cant go on",
        "hopeless", "helpless", "nothing left", "no way out",
        "want to disappear", "falling apart", "breaking down",
    },
    "moderate": {
        "overwhelmed", "exhausted", "crying", "can't sleep", "cant sleep",
        "anxious", "panicking", "depressed", "heartbroken", "grief",
        "terrified", "scared", "miserable", "desperate",
    },
    "mild": {
        "worried", "stressed", "frustrated", "confused", "uncertain",
        "lost", "stuck", "upset", "sad", "lonely", "anxious",
    },
}

# Patterns for casual/closing/factual messages — skip question for these
_CASUAL_PATTERNS = [
    re.compile(r"^\s*(ok|okay|hmm|hm|thanks?|thank\s+you|bye|goodbye|see\s+you|noted|got\s+it|sure|cool|nice|great|good|understood)\s*[.!]*\s*$", re.I),
    re.compile(r"^\s*(namaste|pranam|jai|🙏)\s*$", re.I),
]
_CLOSING_PATTERNS = [
    re.compile(r"\b(goodbye|bye|see\s+you|take\s+care|good\s+night|goodnight|have\s+to\s+go|need\s+to\s+go)\b", re.I),
]
_FACTUAL_PATTERNS = [
    re.compile(r"\bBG\s*\d+\.\d+\b"),
    re.compile(r"\bwhat\s+(is|does|did|are|was|were)\b.*\bteach\b", re.I),
    re.compile(r"\bexplain\b.*\bverse\b", re.I),
    re.compile(r"\bmeaning\s+of\b", re.I),
    re.compile(r"\btranslation\s+of\b", re.I),
]
_ANNOYANCE_PATTERNS = [
    re.compile(r"\bstop\s+(asking|posing)\b.*\bquestion", re.I),
    re.compile(r"\bno\s+more\s+question", re.I),
    re.compile(r"\bdon'?t\s+ask\s+me\b", re.I),
    re.compile(r"\bstop\s+the\s+question", re.I),
    re.compile(r"\bquit\s+asking\b", re.I),
    re.compile(r"\bI\s+just\s+want\s+(an?\s+)?answer\b", re.I),
    re.compile(r"\bkoi\s+sawaal\s+mat\b", re.I),
    re.compile(r"\bsawaal\s+band\b", re.I),
]


def _classify_distress(text: str, sr: "ScreenResult") -> str:
    """Returns 'none' | 'mild' | 'moderate' | 'acute'."""
    if sr.is_crisis:
        return "acute"
    lower = text.lower()
    for level in ("acute", "moderate", "mild"):
        if any(w in lower for w in _DISTRESS_WORDS[level]):
            return level
    return "none"


def _is_casual_or_closing(text: str) -> bool:
    for pat in _CASUAL_PATTERNS:
        if pat.match(text.strip()):
            return True
    for pat in _CLOSING_PATTERNS:
        if pat.search(text):
            return True
    return len(text.strip().split()) <= 3


def _is_purely_factual(text: str) -> bool:
    for pat in _FACTUAL_PATTERNS:
        if pat.search(text):
            return True
    return False


def _user_signals_annoyance(text: str) -> bool:
    for pat in _ANNOYANCE_PATTERNS:
        if pat.search(text):
            return True
    return False


# ---------------------------------------------------------------------------
# User profile helpers
# ---------------------------------------------------------------------------
def _get_user_prefs(user_id: str) -> dict:
    try:
        doc = get_db()[USER_PROFILES].find_one({"_id": user_id})
        if doc and "reflective_prefs" in doc:
            return doc["reflective_prefs"]
    except Exception as exc:
        log.warning("get_user_prefs failed: %s", exc)
    return {
        "frequency": "normal",
        "avg_engagement": 0.0,
        "recently_shown_question_ids": [],
        "last_depth_reached": 0,
    }


def _upsert_user_prefs(user_id: str, update: dict) -> None:
    try:
        get_db()[USER_PROFILES].update_one(
            {"_id": user_id},
            {"$set": {f"reflective_prefs.{k}": v for k, v in update.items()}},
            upsert=True,
        )
    except Exception as exc:
        log.warning("upsert_user_prefs failed: %s", exc)


# ---------------------------------------------------------------------------
# Conversation history helpers
# ---------------------------------------------------------------------------
def _turns_since_last_question(history: list[dict]) -> int:
    """Count user turns since the last turn that had a reflective question shown."""
    count = 0
    for turn in reversed(history):
        if turn.get("role") == "assistant":
            if turn.get("reflective", {}).get("shown"):
                return count
        elif turn.get("role") == "user":
            count += 1
    return count


def _get_shown_in_conversation(history: list[dict]) -> set[str]:
    shown = set()
    for turn in history:
        q_id = (turn.get("reflective") or {}).get("question_id")
        if q_id:
            shown.add(str(q_id))
    return shown


def _get_prior_question(history: list[dict]) -> str | None:
    """Return the surface_text of the most recent reflective question, if any."""
    for turn in reversed(history):
        if turn.get("role") == "assistant":
            rfl = turn.get("reflective") or {}
            if rfl.get("shown"):
                return rfl.get("surface_text") or rfl.get("seed_text")
    return None


def _user_just_answered_prior(history: list[dict]) -> bool:
    """True if the last user turn follows a turn that had a reflective question."""
    turns = [t for t in history if t.get("role") in ("user", "assistant")]
    if len(turns) < 2:
        return False
    last_two = turns[-2:]
    # If second-to-last was assistant with question, and last was user → just answered
    if (last_two[0].get("role") == "assistant"
            and last_two[0].get("reflective", {}).get("shown")
            and last_two[1].get("role") == "user"):
        return True
    return False


# ---------------------------------------------------------------------------
# Depth progression
# ---------------------------------------------------------------------------
def _compute_allowed_depth(
    turn_count: int,
    distress: str,
    user_prefs: dict,
) -> int:
    if turn_count == 0 or user_prefs.get("last_depth_reached", 0) == 0:
        return 1  # first-ever turn: always gentle

    base = min(3, 1 + turn_count // settings.rqe_depth_turns_per_level)
    distress_cap = {"none": 3, "mild": 2, "moderate": 1, "acute": 0}[distress]
    return min(base, distress_cap)


# ---------------------------------------------------------------------------
# Intensity floor filtering
# ---------------------------------------------------------------------------
def _allowed_floors(distress: str) -> list[str]:
    """Return the intensity_safe_floor values compatible with the current distress."""
    if distress in ("none", "mild"):
        return ["any", "mild", "moderate"]
    if distress == "moderate":
        return ["any", "mild"]
    return ["any"]  # acute — only the softest questions allowed (but gate usually blocks)


# ---------------------------------------------------------------------------
# Anchor theme selection
# ---------------------------------------------------------------------------
def _pick_anchor_theme(canonical_themes: list[str], user_prefs: dict) -> str | None:
    if not canonical_themes:
        return None
    # Prefer emotional/inner themes over abstract ones
    emotion_first = [
        "anger", "grief", "fear", "anxiety", "loneliness", "shame",
        "jealousy", "regret", "attachment", "desire", "ego", "self_worth",
    ]
    for theme in canonical_themes:
        if theme in emotion_first:
            return theme
    return canonical_themes[0]


# ---------------------------------------------------------------------------
# Candidate ranking (multi-armed bandit)
# ---------------------------------------------------------------------------
def _score_candidate(doc: dict) -> float:
    stats = doc.get("stats", {})
    rate = stats.get("engagement_rate", 0.0)
    shown = stats.get("shown_count", 0)
    max_shown = 200  # normalizer
    freshness = 1.0 - min(shown / max_shown, 1.0)
    exploration = random.random()
    return (
        0.6 * rate
        + 0.2 * freshness
        + settings.rqe_exploration_factor * exploration
    )


def _rank_candidates(candidates: list[dict]) -> list[dict]:
    return sorted(candidates, key=_score_candidate, reverse=True)


# ---------------------------------------------------------------------------
# Gate — should we ask a question at all this turn?
# ---------------------------------------------------------------------------
def should_skip_question(
    sr: "ScreenResult",
    history: list[dict],
    user_id: str,
    turn_count: int,
) -> tuple[bool, str]:
    """Returns (skip, reason). Call this before select_reflective_seed."""
    if not settings.rqe_enabled:
        return True, "engine_disabled"

    if sr.is_crisis:
        return True, "crisis"

    text = sr.clean_text

    # Distress too acute
    distress = _classify_distress(text, sr)
    if distress == "acute":
        return True, "acute_distress"

    if _is_casual_or_closing(text):
        return True, "casual_or_closing"

    if _is_purely_factual(text):
        return True, "factual"

    # Annoyance detection — update prefs and skip
    if _user_signals_annoyance(text):
        _upsert_user_prefs(user_id, {"frequency": "off"})
        return True, "user_requested_stop"

    user_prefs = _get_user_prefs(user_id)

    if user_prefs.get("frequency") == "off":
        return True, "frequency_off"

    # User just answered the prior question — acknowledge on same thread (handled in ask.py)
    if _user_just_answered_prior(history):
        return True, "continuing_prior_thread"

    # Frequency cap
    turns_since = _turns_since_last_question(history)
    if turns_since < settings.rqe_min_turns_between_questions:
        return True, "frequency_cap"

    if user_prefs.get("frequency") == "reduced":
        if turns_since < settings.rqe_reduced_cap:
            return True, "reduced_frequency_cap"

    return False, "ok"


# ---------------------------------------------------------------------------
# Main selection function
# ---------------------------------------------------------------------------
def select_reflective_seed(
    sr: "ScreenResult",
    history: list[dict],
    user_id: str,
    turn_count: int,
    lang_key: str,
) -> tuple[dict | None, bool]:
    """Select a seed question from the library.

    Returns:
      (seed_doc, on_the_fly)
      seed_doc: the reflective_questions document to use as seed
      on_the_fly: True if no seed found — model should generate freely
    """
    try:
        return _select(sr, history, user_id, turn_count, lang_key)
    except Exception as exc:
        log.error("select_reflective_seed error (failing safe): %s", exc)
        return None, False  # fail safe: skip the question


def _select(
    sr: "ScreenResult",
    history: list[dict],
    user_id: str,
    turn_count: int,
    lang_key: str,
) -> tuple[dict | None, bool]:
    distress = _classify_distress(sr.clean_text, sr)
    user_prefs = _get_user_prefs(user_id)
    allowed_depth = _compute_allowed_depth(turn_count, distress, user_prefs)

    if allowed_depth == 0:
        return None, False

    canonical_themes = normalize_themes(sr.themes)
    anchor = _pick_anchor_theme(canonical_themes, user_prefs)
    floors = _allowed_floors(distress)
    shown_in_conv = _get_shown_in_conversation(history)
    recently_shown = set(str(i) for i in user_prefs.get("recently_shown_question_ids", []))
    excluded = shown_in_conv | recently_shown

    db = get_db()

    def _query(theme_filter: dict, depth_lte: int) -> list[dict]:
        q: dict = {
            "active": True,
            "status": "approved",
            "depth": {"$lte": depth_lte},
            "intensity_safe_floor": {"$in": floors},
        }
        q.update(theme_filter)
        docs = list(db[REFLECTIVE_QUESTIONS].find(q))
        return [d for d in docs if str(d["_id"]) not in excluded]

    # Pass 1: anchor theme exact match
    candidates = _query({"themes": anchor}, allowed_depth) if anchor else []

    # Pass 2: broaden — any of the canonical themes
    if not candidates and canonical_themes:
        candidates = _query({"themes": {"$in": canonical_themes}}, allowed_depth)

    # Pass 3: relax depth by 1
    if not candidates and allowed_depth > 1:
        candidates = _query(
            {"themes": {"$in": canonical_themes}} if canonical_themes else {},
            max(1, allowed_depth - 1),
        )

    # Pass 4: generic fallback — any question at allowed depth
    if not candidates:
        candidates = _query({}, allowed_depth)

    if not candidates:
        # Nothing approved yet — signal on-the-fly
        return None, True

    ranked = _rank_candidates(candidates)
    top_n = min(5, len(ranked))
    seed = random.choice(ranked[:top_n])
    return seed, False


# ---------------------------------------------------------------------------
# Instruction builder — injects the seed into the system prompt
# ---------------------------------------------------------------------------
def build_seed_instruction(seed: dict, lang_display: str) -> str:
    """Return the text to append to the system prompt for seed-and-rephrase."""
    en_text = (seed.get("text") or {}).get("en", "")
    depth = seed.get("depth", 1)
    depth_notes = {
        1: "Keep it gentle and opening — this is a soft invitation, not a probe.",
        2: "This is a moderate question — warm but goes one layer deeper than surface.",
        3: "This is a deep question — only appropriate because the seeker appears stable and reflective.",
    }
    return (
        f"\n\nCLOSING QUESTION GUIDANCE — end your reply with a single reflective question "
        f"expressed in your own reverent voice and in {lang_display}. "
        f"Capture the spirit of this seed: '{en_text}' — but adapt it naturally to exactly what "
        f"the seeker just said. Do not quote it mechanically; let it sound like your own words. "
        f"{depth_notes.get(depth, '')} "
        f"The question must be open-ended, non-leading, and NOT a yes/no question."
    )


def build_skip_instruction() -> str:
    """Return the text to append when we've decided no question this turn."""
    return (
        "\n\nCLOSING GUIDANCE — do NOT end this reply with a reflective question. "
        "Close warmly but without asking anything."
    )


def build_continue_thread_instruction(prior_text: str, lang_display: str) -> str:
    """Instruction when the user just answered the prior reflective question."""
    return (
        f"\n\nCONTINUITY GUIDANCE — the seeker has just responded to your previous "
        f"reflective question: '{prior_text}'. Acknowledge what they shared before moving on. "
        f"If appropriate, deepen the exploration of the SAME thread rather than introducing "
        f"a new topic. Any closing question should continue this thread, not pivot away. "
        f"Reply in {lang_display}."
    )


# ---------------------------------------------------------------------------
# Public helpers for ask.py
# ---------------------------------------------------------------------------
def get_prior_question_for_classification(history: list[dict]) -> str | None:
    """Return the prior reflective question text for passing to screen_input."""
    return _get_prior_question(history)


def record_question_shown(
    user_id: str,
    question_id: str | None,
    depth: int,
    user_prefs: dict,
) -> None:
    """Update user profile after showing a question. Fire-and-forget."""
    try:
        recent = list(user_prefs.get("recently_shown_question_ids", []))
        if question_id and question_id not in recent:
            recent.append(question_id)
            if len(recent) > settings.rqe_recently_shown_cap:
                recent = recent[-settings.rqe_recently_shown_cap:]
        _upsert_user_prefs(user_id, {
            "recently_shown_question_ids": recent,
            "last_depth_reached": max(depth, user_prefs.get("last_depth_reached", 0)),
        })
    except Exception as exc:
        log.warning("record_question_shown failed: %s", exc)


__all__ = [
    "should_skip_question",
    "select_reflective_seed",
    "build_seed_instruction",
    "build_skip_instruction",
    "build_continue_thread_instruction",
    "get_prior_question_for_classification",
    "record_question_shown",
]
