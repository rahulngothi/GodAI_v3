"""Canonical THEMES taxonomy for the Reflective Question Engine.

This is the single source of truth for the theme vocabulary used by:
  - llm_classify() in safety.py  (input classification)
  - reflective_questions collection (question tagging)
  - selection logic in reflective.py (candidate filtering)

Never import from a module that imports this one — kept dependency-free.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Canonical theme slugs — 28 values, immutable.
# ---------------------------------------------------------------------------
THEMES: frozenset[str] = frozenset({
    "anger",
    "ego",
    "fear",
    "anxiety",
    "attachment",
    "desire",
    "jealousy",
    "grief",
    "failure",
    "success",
    "money",
    "purpose",
    "duty",
    "discipline",
    "laziness",
    "relationships",
    "family",
    "parenting",
    "marriage",
    "loneliness",
    "self_worth",
    "control",
    "forgiveness",
    "faith_doubt",
    "uncertainty",
    "comparison",
    "regret",
    "restlessness",
})

THEMES_LIST: list[str] = sorted(THEMES)

# ---------------------------------------------------------------------------
# Alias map: free-text the LLM might emit → canonical slug
# ---------------------------------------------------------------------------
_ALIAS: dict[str, str] = {
    # duty / karma / dharma
    "duty": "duty",
    "dharma": "duty",
    "svadharma": "duty",
    "karma": "duty",
    "action": "duty",
    "responsibility": "duty",
    "purpose": "purpose",
    "meaning": "purpose",
    "direction": "purpose",

    # laziness / inertia
    "inertia": "laziness",
    "laziness": "laziness",
    "procrastination": "laziness",
    "tamasic": "laziness",
    "motivation": "laziness",

    # attachment / desire
    "attachment": "attachment",
    "attachment to outcome": "attachment",
    "clinging": "attachment",
    "craving": "desire",
    "desire": "desire",
    "want": "desire",
    "greed": "desire",

    # restlessness / anxiety / fear
    "restlessness": "restlessness",
    "equanimity": "restlessness",   # equanimity as a concern maps here
    "peace": "restlessness",
    "anxiety": "anxiety",
    "worry": "anxiety",
    "stress": "anxiety",
    "overwhelm": "anxiety",
    "fear": "fear",
    "dread": "fear",
    "phobia": "fear",
    "insecurity": "fear",

    # self / ego / worth
    "ego": "ego",
    "pride": "ego",
    "arrogance": "ego",
    "self-doubt": "self_worth",
    "self doubt": "self_worth",
    "self_doubt": "self_worth",
    "self-worth": "self_worth",
    "self worth": "self_worth",
    "self_worth": "self_worth",
    "confidence": "self_worth",
    "worthiness": "self_worth",
    "identity": "self_worth",

    # emotions
    "anger": "anger",
    "rage": "anger",
    "frustration": "anger",
    "resentment": "anger",
    "jealousy": "jealousy",
    "envy": "jealousy",
    "grief": "grief",
    "sorrow": "grief",
    "sadness": "grief",
    "loss": "grief",
    "mourning": "grief",
    "suffering": "grief",
    "impermanence": "uncertainty",
    "regret": "regret",
    "guilt": "regret",
    "shame": "regret",
    "comparison": "comparison",
    "competition": "comparison",
    "loneliness": "loneliness",
    "isolation": "loneliness",
    "aloneness": "loneliness",
    "forgiveness": "forgiveness",
    "letting go": "forgiveness",
    "compassion": "forgiveness",

    # mind / control
    "control": "control",
    "surrender": "control",
    "acceptance": "control",
    "resistance": "control",
    "discipline": "discipline",
    "willpower": "discipline",
    "habit": "discipline",
    "practice": "discipline",

    # relationships
    "relationships": "relationships",
    "relationship": "relationships",
    "family": "family",
    "parents": "family",
    "parent": "family",
    "parenting": "parenting",
    "children": "parenting",
    "marriage": "marriage",
    "partner": "marriage",
    "spouse": "marriage",

    # life outcomes
    "failure": "failure",
    "success": "success",
    "achievement": "success",
    "money": "money",
    "wealth": "money",
    "finances": "money",
    "financial": "money",

    # faith / uncertainty
    "faith": "faith_doubt",
    "doubt": "faith_doubt",
    "faith-doubt": "faith_doubt",
    "faith_doubt": "faith_doubt",
    "belief": "faith_doubt",
    "God": "faith_doubt",
    "uncertainty": "uncertainty",
    "change": "uncertainty",
    "impermanence": "uncertainty",
    "transition": "uncertainty",

    # generic fallbacks
    "general spiritual inquiry": "restlessness",
    "spiritual": "faith_doubt",
    "general": "restlessness",
}


def normalize_theme(raw: str) -> str | None:
    """Map a raw theme string to a canonical slug. Returns None if unmapped."""
    cleaned = raw.strip().lower().replace("-", "_")
    if cleaned in THEMES:
        return cleaned
    # Try alias map (original casing too)
    if cleaned in _ALIAS:
        return _ALIAS[cleaned]
    raw_lower = raw.strip().lower()
    if raw_lower in _ALIAS:
        return _ALIAS[raw_lower]
    return None


def normalize_themes(themes_str: str) -> list[str]:
    """Convert a comma-separated themes string to a list of canonical slugs.

    Unknown terms are logged. Duplicates are removed. Order is preserved.
    """
    import logging
    log = logging.getLogger(__name__)

    seen: set[str] = set()
    result: list[str] = []
    for part in themes_str.split(","):
        part = part.strip()
        if not part:
            continue
        canonical = normalize_theme(part)
        if canonical and canonical not in seen:
            result.append(canonical)
            seen.add(canonical)
        elif not canonical:
            log.info("themes.normalize: unmapped theme %r — using nearest fallback", part)
            # Nearest-neighbor: find longest alias key that is a substring
            best = _nearest_fallback(part)
            if best and best not in seen:
                result.append(best)
                seen.add(best)
    return result or ["restlessness"]


def _nearest_fallback(raw: str) -> str | None:
    """Best-effort fuzzy match via longest common token overlap with alias keys."""
    raw_tokens = set(raw.lower().split())
    best_score, best_val = 0, None
    for key, val in _ALIAS.items():
        key_tokens = set(key.lower().split())
        score = len(raw_tokens & key_tokens)
        if score > best_score:
            best_score, best_val = score, val
    return best_val


__all__ = ["THEMES", "THEMES_LIST", "normalize_theme", "normalize_themes"]
