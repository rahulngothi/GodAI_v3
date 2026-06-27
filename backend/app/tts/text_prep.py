"""Text preparation pipeline — runs before any TTS backend.

Order: strip citations → strip markdown → apply lexicon → collapse whitespace.
Each step is pure (no I/O) and easily unit-testable.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

_LEXICON_PATH = Path(__file__).parent / "lexicon.json"

# Regex for citation tags like [BG 2.47], [UP 1.3], [GY 4.1]
_CITE_RE = re.compile(r"\[[A-Za-z][^\]]*?\d[^\]]*\]")
_CITE_EXPAND_RE = re.compile(r"\[([A-Za-z]+)\s+(\d+)\.(\d+)\]")

# Basic emoji / symbol ranges
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0000FE00-\U0000FE0F"
    "\U0001F1E0-\U0001F1FF"
    "]",
    re.UNICODE,
)


@lru_cache(maxsize=1)
def _load_lexicon() -> dict[str, str]:
    if _LEXICON_PATH.exists():
        try:
            return json.loads(_LEXICON_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def strip_citations(text: str, mode: str = "drop") -> str:
    """Remove or expand [BG 2.47] style citations.

    mode="drop"  — silently removed from audio (visual tag kept on screen).
    mode="speak" — expanded to "chapter 2, verse 47".
    """
    if mode == "speak":
        def _expand(m: re.Match) -> str:
            return f"chapter {m.group(2)}, verse {m.group(3)}"
        return _CITE_EXPAND_RE.sub(_expand, text)
    return _CITE_RE.sub("", text)


def strip_markdown(text: str) -> str:
    """Remove markdown formatting, emojis, URLs, stray symbols."""
    # Headings
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Bold / italic / strikethrough
    text = re.sub(r"\*{1,3}([^*\n]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_\n]+)_{1,3}", r"\1", text)
    text = re.sub(r"~~([^~\n]+)~~", r"\1", text)
    # Inline code
    text = re.sub(r"`[^`\n]+`", "", text)
    # URLs
    text = re.sub(r"https?://\S+", "", text)
    # Emojis
    text = _EMOJI_RE.sub("", text)
    # Collapse whitespace
    return re.sub(r"\s{2,}", " ", text).strip()


def apply_lexicon(text: str, language: str) -> str:
    """Substitute Sanskrit/Hindi romanisations with pronunciation hints.

    Devanagari text is handled natively by indic-parler-tts; skip it.
    """
    if language == "hindi":
        return text
    lexicon = _load_lexicon()
    for word, hint in lexicon.items():
        text = re.sub(rf"\b{re.escape(word)}\b", hint, text, flags=re.IGNORECASE)
    return text


def prepare_text(text: str, language: str, citation_mode: str = "drop") -> str:
    """Full pipeline: citations → markdown → lexicon → whitespace."""
    text = strip_citations(text, mode=citation_mode)
    text = strip_markdown(text)
    text = apply_lexicon(text, language)
    return re.sub(r"\s{2,}", " ", text).strip()
