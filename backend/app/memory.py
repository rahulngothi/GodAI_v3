"""Per-user profile and rolling memory summary.

Two MongoDB collections:
  user_profiles — display_name, preferred_language, answer_style
  user_memory   — a ≤100-word prose portrait updated after each conversation turn

Memory update is fire-and-forget (daemon thread) so it never blocks the API response.
"""
from __future__ import annotations

import datetime as _dt
import threading

from .db import get_db
from .nvidia import chat as llm_chat

_PROFILES = "user_profiles"
_MEMORY = "user_memory"

VALID_STYLES = {"short", "deep", "reflective"}

_STYLE_HINT = {
    "short": "Be concise — 1-3 sentences unless the seeker clearly needs more.",
    "deep": "Give a full, thoughtful response when the question calls for it.",
    "reflective": "Favour questions back to the seeker, helping them discover their own answer.",
}


# ── profile ──────────────────────────────────────────────────────────────────

def get_profile(user: str) -> dict:
    doc = get_db()[_PROFILES].find_one({"user": user}) or {}
    return {
        "display_name": doc.get("display_name", user),
        "preferred_language": doc.get("preferred_language", "english"),
        "answer_style": doc.get("answer_style", "deep"),
    }


def update_profile(user: str, **kwargs) -> None:
    safe = {k: v for k, v in kwargs.items()
            if k in {"display_name", "preferred_language", "answer_style"} and v is not None}
    if not safe:
        return
    if "answer_style" in safe and safe["answer_style"] not in VALID_STYLES:
        raise ValueError(f"answer_style must be one of {VALID_STYLES}")
    get_db()[_PROFILES].update_one(
        {"user": user},
        {"$set": {**safe, "updated_at": _dt.datetime.now(_dt.timezone.utc)}},
        upsert=True,
    )


# ── memory ────────────────────────────────────────────────────────────────────

def get_summary(user: str) -> str:
    doc = get_db()[_MEMORY].find_one({"user": user}) or {}
    return doc.get("summary", "")


def _do_update(user: str, question: str, answer: str) -> None:
    try:
        old = get_summary(user)
        prompt = (
            "You maintain a compact, evolving portrait of a spiritual seeker. "
            "Update the portrait given this new exchange, keeping it under 100 words. "
            "Focus on recurring themes, emotional patterns, and what this person seeks. "
            "Write in third person (e.g. 'This seeker often returns to...').\n\n"
            f"Current portrait:\n{old or '(none yet)'}\n\n"
            f"New exchange —\nSeeker: {question}\nGuide: {answer}\n\n"
            "Updated portrait (≤100 words, no preamble):"
        )
        new_summary = llm_chat(
            [{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=160,
        ).strip()
        get_db()[_MEMORY].update_one(
            {"user": user},
            {"$set": {"summary": new_summary, "updated_at": _dt.datetime.now(_dt.timezone.utc)}},
            upsert=True,
        )
    except Exception:
        pass  # never let a memory update break the main flow


def update_memory_bg(user: str, question: str, answer: str) -> None:
    """Fire-and-forget: update memory summary in a background thread."""
    t = threading.Thread(target=_do_update, args=(user, question, answer), daemon=True)
    t.start()


def build_memory_context(user: str, answer_style: str = "deep") -> str:
    """Return the block injected into the system prompt. Empty string if no memory yet."""
    summary = get_summary(user)
    hint = _STYLE_HINT.get(answer_style, "")
    parts: list[str] = []
    if summary:
        parts.append(
            "WHAT YOU KNOW OF THIS SOUL (from prior conversations — "
            "treat as living knowledge, not recitation):\n" + summary
        )
    if hint:
        parts.append("Their preferred depth: " + hint)
    return "\n\n".join(parts)
