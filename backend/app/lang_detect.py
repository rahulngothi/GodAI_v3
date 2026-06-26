"""Language detection and verification for Dharma AI.

Priority for resolving which language to reply in:
  1. User's saved preference (passed as user_pref)
  2. Detected language of the current message text  ← trust what they typed
  3. UI selector (ui_language param)
  4. Default: English

Key buckets handled:
  - English (Latin script, non-Hindi words)
  - Hindi / Devanagari (Devanagari Unicode range ऀ-ॿ)
  - Hinglish (romanized Hindi in Latin script, code-mixed with English)
  - Other Indian scripts: Bengali, Tamil, Telugu, Kannada (script detection)
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Script detection helpers
# ---------------------------------------------------------------------------

_DEVA_RE = re.compile(r"[ऀ-ॿ]")


def _devanagari_ratio(text: str) -> float:
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return 0.0
    return sum(1 for c in chars if "ऀ" <= c <= "ॿ") / len(chars)


def _script_count(text: str, lo: str, hi: str) -> int:
    return sum(1 for c in text if lo <= c <= hi)


# ---------------------------------------------------------------------------
# Hinglish seed words (romanized Hindi commonly used in code-mixed messages)
# Strong indicators: one match alone is enough to classify as Hinglish.
# Broader set: need 2+ matches without a strong indicator.
# ---------------------------------------------------------------------------
_STRONG_HINDI_INDICATORS: frozenset[str] = frozenset({
    "yaar", "bhai", "kya", "nahi", "nahin", "mujhe", "bahut", "zaroor",
    "isliye", "kyunki", "accha", "theek", "matlab", "lagta", "lagti",
    "sochta", "milta", "rehta", "zindagi", "duniya", "waqt", "pyaar",
    "dekho", "batao", "zyada", "thoda", "kaafi", "bilkul", "maloom",
    "mujhko", "humko", "tumhe", "tumko", "humne", "mujhse",
})

_HINGLISH_WORDS: frozenset[str] = _STRONG_HINDI_INDICATORS | frozenset({
    "hai", "hain", "tum", "main", "acha", "kyun", "lekin",
    "aur", "bhi", "abhi", "phir", "waise", "samajh",
    "dil", "kal", "aaj", "koi", "sab", "hoga",
    "tha", "thi", "raha", "rahi", "mera", "tera", "apna", "unka", "usse",
    "isse", "toh", "woh", "wo", "ye", "yeh", "jo", "jab", "tab",
    "kaisa", "kaisi", "kitna", "kitni", "jaan", "dost", "baat", "kaam",
    "samay", "pata", "unhe", "inhe", "inse", "unse", "agar",
    "kuch", "sirf", "bas", "hi", "haan",
})


def _is_hinglish(text: str) -> bool:
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    if len(words) < 2:
        return False
    # One strong indicator is enough — e.g. "Yaar I feel so stuck"
    if any(w in _STRONG_HINDI_INDICATORS for w in words):
        return True
    # Otherwise require 2+ broader matches
    return sum(1 for w in words if w in _HINGLISH_WORDS) >= 2


# ---------------------------------------------------------------------------
# Language display names used in prompts
# ---------------------------------------------------------------------------
_LANG_DISPLAY: dict[str, str] = {
    "english":  "English",
    "hindi":    "Hindi (Devanagari script)",
    "hinglish": "Hinglish (romanized Hindi mixed with English, Latin script only — no Devanagari)",
    "marathi":  "Marathi (Devanagari script)",
    "tamil":    "Tamil",
    "telugu":   "Telugu",
    "kannada":  "Kannada",
    "bengali":  "Bengali",
}


def _key_and_display(lang_key: str) -> tuple[str, str]:
    display = _LANG_DISPLAY.get(lang_key, lang_key.capitalize())
    return (lang_key, display)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_language(text: str) -> str:
    """Return a language key detected from the message text."""
    if not text or len(text.strip()) < 3:
        return "english"

    # 1. Devanagari → Hindi (Marathi also uses Devanagari; treat as Hindi for prompt purposes)
    if _devanagari_ratio(text) > 0.15:
        return "hindi"

    # 2. Other Indian scripts — script count > 2 to avoid stray Unicode chars
    if _script_count(text, "ঀ", "৿") > 2:
        return "bengali"
    if _script_count(text, "஀", "௿") > 2:
        return "tamil"
    if _script_count(text, "ఀ", "౿") > 2:
        return "telugu"
    if _script_count(text, "ಀ", "೿") > 2:
        return "kannada"

    # 3. Hinglish (romanized Hindi in Latin script)
    if _is_hinglish(text):
        return "hinglish"

    return "english"


def resolve_language(
    message: str,
    ui_language: str,
    user_pref: str | None = None,
) -> tuple[str, str]:
    """
    Return (lang_key, lang_display_name) per priority order:
      1. user_pref (explicitly saved by user)
      2. detected language of the message text
      3. ui_language (the selector value sent by the frontend)
      4. "english"
    """
    # 1. Saved user preference
    if user_pref:
        return _key_and_display(user_pref)

    # 2. Detect from message text
    detected = detect_language(message)
    if detected != "english":
        return _key_and_display(detected)

    # 3. UI selector (non-english values are explicit choices)
    if ui_language and ui_language != "english":
        return _key_and_display(ui_language)

    # 4. Default
    return ("english", "English")


def verify_language(text: str, target_key: str) -> bool:
    """
    Return True if `text` appears to be in the target language.
    Used post-generation to catch wrong-language replies.
    Intentionally lenient to avoid false positives on short or mixed replies.
    """
    if not text or len(text.strip()) < 20:
        return True  # too short to verify reliably

    if target_key == "hindi":
        # Require at least 20% Devanagari characters
        return _devanagari_ratio(text) > 0.20

    if target_key == "hinglish":
        # Must stay in Latin script; fail if more than 10% Devanagari
        return _devanagari_ratio(text) < 0.10

    if target_key == "english":
        # Fail only if clearly in a non-Latin script
        return _devanagari_ratio(text) < 0.10

    if target_key in ("marathi",):
        return _devanagari_ratio(text) > 0.15

    if target_key == "bengali":
        ratio = _script_count(text, "ঀ", "৿") / max(len(text.replace(" ", "")), 1)
        return ratio > 0.10

    if target_key == "tamil":
        ratio = _script_count(text, "஀", "௿") / max(len(text.replace(" ", "")), 1)
        return ratio > 0.10

    return True  # unknown language key — pass
