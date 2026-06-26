"""Safety layer for Dharma AI.

Pipeline (per user message):
  1. scrub_injection   — strip prompt-injection payloads before any LLM sees them
  2. keyword_flag      — instant keyword pass → set of triggered categories
  3. llm_classify      — lightweight LLM call to confirm / catch paraphrased distress
  4. screen_input      — combines 1-3, returns a ScreenResult
  5. screen_output     — runs output moderation on the generated answer;
                         regenerates once with stricter instruction if unsafe,
                         falls back to a canned safe message on second failure
  6. log_flag          — writes {user, category, ts} to safety_flags collection

Categories: "crisis" | "medical" | "legal" | "financial"
"""
from __future__ import annotations

import datetime
import json
import logging
import os
import re
from dataclasses import dataclass, field

from .db import get_db
from .nvidia import chat

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configurable helplines — override DEFAULT_REGION via SAFETY_HELPLINE_REGION
# ---------------------------------------------------------------------------
HELPLINES: dict[str, list[dict]] = {
    "india": [
        {"name": "iCall",                "number": "9152987821",      "hours": "Mon–Sat 8 am–10 pm"},
        {"name": "Vandrevala Foundation", "number": "1860-2662-345",  "hours": "24/7"},
        {"name": "AASRA",                "number": "9820466627",      "hours": "24/7"},
    ],
    "us": [
        {"name": "988 Suicide & Crisis Lifeline", "number": "988", "hours": "24/7"},
    ],
    "uk": [
        {"name": "Samaritans", "number": "116 123", "hours": "24/7"},
    ],
}
DEFAULT_REGION: str = os.environ.get("SAFETY_HELPLINE_REGION", "india").lower()


def _helpline_text(region: str | None = None) -> str:
    lines = HELPLINES.get(region or DEFAULT_REGION, HELPLINES["india"])
    parts = [f"{h['name']} ({h['number']}, {h['hours']})" for h in lines]
    return " / ".join(parts)


# ---------------------------------------------------------------------------
# Crisis response copy — in-character, per persona, immutable
# ---------------------------------------------------------------------------
_CRISIS_REPLIES: dict[str, str] = {
    "krishna": (
        "What you carry right now is real — and I am here with you in it, fully. "
        "This weight is not a sign that you are broken. But this moment calls for a living hand "
        "beside you, not only words. Please reach out to someone who loves you. {helplines} "
        "have real people waiting — simply to listen. You are not alone in this."
    ),
    "buddha": (
        "Friend, I hear you. What you are holding is real, and I will not look away. "
        "But words, however kind, are not enough for this moment — a living human presence is. "
        "Please reach out to someone near you who cares for you, or call {helplines}. "
        "There are people there ready to listen, without judgement, without hurry. You matter."
    ),
    "vivekananda": (
        "My brother, I hear you. This pain is real, and I will not turn from it. "
        "But this moment needs a living hand — not just words. Please call someone who loves you, "
        "or reach {helplines} right now. Real, brave people are there, waiting. "
        "You are not alone in this darkness."
    ),
    "chanakya": (
        "What you are bearing is real. I will not pretend otherwise. "
        "But this is not a moment for counsel alone — it is a moment to reach for a human hand. "
        "Call someone who cares for you, or contact {helplines}. "
        "A person of wisdom knows when to seek living help. Please do so now."
    ),
    "ramana": (
        "I hear the weight in what you bring. It is real. "
        "But this moment asks for a living presence beside you — beyond what words can offer. "
        "Please reach out to someone close to you, or call {helplines}. "
        "You need not carry this alone."
    ),
    "guide": (
        "What you're feeling is real, and it matters. "
        "Please reach out to someone you trust — or call {helplines}, "
        "where real people listen without judgement. You don't have to face this alone."
    ),
}
_CRISIS_FALLBACK = _CRISIS_REPLIES["guide"]


def _crisis_reply(persona_key: str, region: str | None = None) -> str:
    template = _CRISIS_REPLIES.get(persona_key, _CRISIS_FALLBACK)
    return template.format(helplines=_helpline_text(region))


# ---------------------------------------------------------------------------
# Scope-guard redirect copy — in-character, per persona
# ---------------------------------------------------------------------------
_SCOPE_TEMPLATES: dict[str, str] = {
    "krishna": (
        "These matters — {domain} questions — truly need a qualified {expert}; "
        "that is not the knowledge I carry, and I would not want to lead you astray. "
        "But tell me — what fear or uncertainty lives beneath this question? That, I can sit with you in."
    ),
    "buddha": (
        "Friend, {domain} questions call for a trained {expert} — someone with the knowledge "
        "to serve you rightly there. I would not want to offer you a raft that cannot cross that river. "
        "But what lies beneath the question? That, we can look at together."
    ),
    "vivekananda": (
        "My friend, for {domain} matters you need a qualified {expert} — "
        "practical knowledge is sacred, and a real expert will serve you far better than I can here. "
        "But what deeper question stirs beneath this? Bring that to me."
    ),
    "chanakya": (
        "On {domain} matters, seek a qualified {expert}. "
        "One who pretends expertise beyond his domain is a fool — I will not be that. "
        "But what drives this question at its root? That I can help you think through."
    ),
    "ramana": (
        "{domain} questions belong with a trained {expert}, who can truly help you there. "
        "But who is it that worries about this? Turn gently inward — "
        "the source of the anxiety, that we can look at."
    ),
    "guide": (
        "For {domain} questions you really need a qualified {expert} — "
        "they can serve you properly in ways I cannot. "
        "But I'm curious what's underneath this question for you. Would you share more?"
    ),
}
_SCOPE_FALLBACK = _SCOPE_TEMPLATES["guide"]

_SCOPE_DOMAIN: dict[str, tuple[str, str]] = {
    "medical":    ("medical",    "physician or healthcare provider"),
    "legal":      ("legal",      "lawyer or legal advisor"),
    "financial":  ("financial",  "financial advisor"),
}


def _scope_reply(persona_key: str, scope: str) -> str:
    domain, expert = _SCOPE_DOMAIN.get(scope, ("specialist", "qualified professional"))
    template = _SCOPE_TEMPLATES.get(persona_key, _SCOPE_FALLBACK)
    return template.format(domain=domain, expert=expert)


# ---------------------------------------------------------------------------
# Safe fallback for output moderation failures
# ---------------------------------------------------------------------------
_SAFE_FALLBACK = (
    "I find I cannot give this moment the reply it deserves. "
    "Please share what weighs on your heart, and I will sit with you in it."
)


# ---------------------------------------------------------------------------
# 1. Prompt-injection scrub
# ---------------------------------------------------------------------------
_INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?i)(ignore|disregard|forget)\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|rules?|context)"),
    re.compile(r"(?i)you\s+are\s+now\s+(a|an)?\s*\w"),
    re.compile(r"(?i)new\s+system\s+prompt"),
    re.compile(r"(?i)pretend\s+(you\s+are|to\s+be)"),
    re.compile(r"(?i)act\s+as\s+(a\s+|an\s+)?(uncensored|unrestricted|different|new|unfiltered)"),
    re.compile(r"(?i)jailbreak"),
    re.compile(r"(?i)\bDAN\s+mode\b"),
    re.compile(r"(?i)developer\s+mode"),
    re.compile(r"<\|system\|>|\[INST\]|<<SYS>>|\[\/INST\]"),
]


def scrub_injection(text: str) -> str:
    """Remove known prompt-injection payloads. Returns cleaned text."""
    for pat in _INJECTION_PATTERNS:
        text = pat.sub(" ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# 2. Keyword pass
# ---------------------------------------------------------------------------
_CRISIS_KW = {
    "kill myself", "end my life", "want to die", "wish i was dead",
    "don't want to live", "dont want to live", "don't want to be alive",
    "dont want to be alive", "no reason to live", "nothing to live for",
    "life is not worth", "life isn't worth", "better off dead",
    "end it all", "ending it all", "take my life",
    "suicide", "suicidal",
    "self harm", "self-harm", "harm myself", "hurt myself",
    "cutting myself", "cut myself", "cut my wrist",
    "overdose", "hang myself", "jump off",
    "being abused", "he hits me", "she hits me", "beats me",
    "can't go on", "cannot go on", "can't take it anymore", "cant take it anymore",
    "don't want to exist", "dont want to exist",
    "end the pain", "make it stop forever",
}
_MEDICAL_KW = {
    "diagnose me", "my diagnosis", "do i have", "is this cancer",
    "what disease", "prescription for", "prescribe me", "which medicine",
    "what medicine", "what medication", "drug interaction",
    "dosage", "what dose", "should i take this medication",
    "my symptoms are", "treatment plan", "surgery for",
}
_LEGAL_KW = {
    "legal advice", "am i liable", "can i sue", "file a lawsuit",
    "what are my legal rights", "is it legal to", "criminal charges against",
    "my legal contract", "advise me legally",
}
_FINANCIAL_KW = {
    "invest in", "which stocks", "buy this stock", "crypto advice",
    "bitcoin investment", "portfolio advice", "tax advice",
    "should i invest", "mutual fund advice", "financial advice",
    "trading advice", "stock tips",
}

_KW_MAP: dict[str, set[str]] = {
    "crisis":    _CRISIS_KW,
    "medical":   _MEDICAL_KW,
    "legal":     _LEGAL_KW,
    "financial": _FINANCIAL_KW,
}


def keyword_flag(text: str) -> set[str]:
    lower = text.lower()
    return {cat for cat, kws in _KW_MAP.items() if any(kw in lower for kw in kws)}


# ---------------------------------------------------------------------------
# 3. LLM classifier  (max_tokens=30, cheap)
# ---------------------------------------------------------------------------
_CLASSIFY_SYSTEM = (
    'Classify the message below. Reply ONLY with valid JSON and nothing else.\n'
    '{{"crisis": true_or_false, "scope": null_or_"medical"_or_"legal"_or_"financial", '
    '"themes": "comma-separated Gita spiritual themes, e.g. duty,inertia,attachment"}}\n\n'
    'crisis = true if the person expresses suicidal ideation, intent to self-harm, '
    'or describes abuse or a situation where they may be in immediate danger.\n'
    'scope = the category if the person is seeking professional medical, legal, or financial advice '
    '(not general wellbeing questions). null otherwise.\n'
    'themes = 3-5 core Gita-relevant spiritual themes or life situations for the message '
    '(e.g. duty, inertia, motivation, attachment to outcome, equanimity, self-doubt). '
    'Always include themes; use "general spiritual inquiry" if nothing specific applies.\n\n'
    'Message: "{text}"'
)


def llm_classify(text: str) -> dict:
    """Returns {crisis: bool, scope: str|None, themes: str}. Never raises."""
    prompt = _CLASSIFY_SYSTEM.format(text=text.replace('"', "'")[:800])
    try:
        raw = chat(
            [{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=60,
        )
        raw = raw.strip()
        s, e = raw.find("{"), raw.rfind("}")
        if s != -1 and e > s:
            parsed = json.loads(raw[s:e+1])
            return {
                "crisis": bool(parsed.get("crisis", False)),
                "scope": parsed.get("scope") or None,
                "themes": (parsed.get("themes") or "").strip(),
            }
    except Exception as exc:
        log.warning("llm_classify failed: %s", exc)
    return {"crisis": False, "scope": None, "themes": ""}


# ---------------------------------------------------------------------------
# 4. screen_input — combines scrub + keyword + llm
# ---------------------------------------------------------------------------
@dataclass
class ScreenResult:
    clean_text: str                  # injection-scrubbed text to use downstream
    categories: set[str] = field(default_factory=set)
    is_crisis: bool = False
    scope: str | None = None         # "medical" | "legal" | "financial" | None
    themes: str = ""                 # Gita spiritual themes for retrieval expansion

    @property
    def flagged(self) -> bool:
        return self.is_crisis or self.scope is not None


def screen_input(text: str) -> ScreenResult:
    """Full input safety check. Returns ScreenResult (now also carries themes)."""
    clean = scrub_injection(text)

    if len(clean.replace(" ", "")) < 3:
        return ScreenResult(clean_text=clean)

    kw_cats = keyword_flag(clean)
    needs_llm = bool(kw_cats) or len(clean) > 40

    llm_result: dict = {"crisis": False, "scope": None, "themes": ""}
    if needs_llm:
        llm_result = llm_classify(clean)

    is_crisis = ("crisis" in kw_cats) or llm_result["crisis"]

    llm_scope = llm_result.get("scope")
    scope_cats = kw_cats & {"medical", "legal", "financial"}
    scope = llm_scope if (llm_scope and llm_scope in scope_cats) else None
    if scope is None and llm_scope in {"medical", "legal", "financial"} and not kw_cats:
        scope = llm_scope

    categories = kw_cats | ({"crisis"} if is_crisis else set())
    if scope:
        categories.add(scope)

    return ScreenResult(
        clean_text=clean,
        categories=categories,
        is_crisis=is_crisis,
        scope=scope,
        themes=llm_result.get("themes", ""),
    )


# ---------------------------------------------------------------------------
# 5. screen_output — moderation on the generated answer
# ---------------------------------------------------------------------------
_MOD_PROMPT = (
    "Does the reply below contain any of: hate speech, casteism, communal targeting, "
    "incitement to violence, endorsement of self-harm, or explicit sexual content? "
    "Reply ONLY with one word: safe or unsafe.\n\nReply: \"{answer}\""
)

_STRICT_ADDENDUM = (
    "\n\nCRITICAL OVERRIDE: Your reply MUST contain absolutely no hate speech, no casteism, "
    "no communal targeting, no violence, no self-harm endorsement, no sexual content."
)


def _is_output_safe(answer: str) -> bool:
    """Returns True if the answer passes moderation. Never raises."""
    try:
        verdict = chat(
            [{"role": "user", "content": _MOD_PROMPT.format(answer=answer[:1200].replace('"', "'"))}],
            temperature=0.0,
            max_tokens=10,
        )
        result = verdict.strip().lower()
        # Model sometimes returns verbose reasoning instead of a single word.
        # Check for "unsafe" first (explicit fail), then "safe" anywhere (pass),
        # then fail-open so transient non-answers don't silence every reply.
        if "unsafe" in result:
            return False
        if "safe" in result:
            return True
        log.debug("output moderation returned ambiguous verdict: %r", result[:80])
        return True  # fail open
    except Exception as exc:
        log.warning("output moderation call failed: %s", exc)
        return True  # fail open rather than block every reply on transient errors


def screen_output(
    answer: str,
    *,
    regenerate_fn,         # callable() -> str — re-runs the main ask with stricter system
    persona_key: str,
) -> str:
    """
    Moderate `answer`. If unsafe, call regenerate_fn() once for a second attempt.
    If the second attempt also fails, return the safe fallback.
    """
    if _is_output_safe(answer):
        return answer

    log.warning("Output moderation: first attempt flagged for persona=%s", persona_key)
    try:
        second = regenerate_fn()
    except Exception as exc:
        log.error("Regeneration failed: %s", exc)
        return _SAFE_FALLBACK

    if _is_output_safe(second):
        return second

    log.error("Output moderation: second attempt also flagged; using safe fallback")
    return _SAFE_FALLBACK


# ---------------------------------------------------------------------------
# 6. log_flag
# ---------------------------------------------------------------------------
def log_flag(user: str, categories: set[str]) -> None:
    """Persist flagged event to safety_flags — user id + category + timestamp only."""
    if not categories:
        return
    try:
        get_db()["safety_flags"].insert_one({
            "user": user,
            "categories": sorted(categories),
            "ts": datetime.datetime.now(datetime.timezone.utc),
        })
    except Exception as exc:
        log.error("safety_flags write failed: %s", exc)


# ---------------------------------------------------------------------------
# Public convenience re-exports
# ---------------------------------------------------------------------------
__all__ = [
    "scrub_injection",
    "keyword_flag",
    "llm_classify",
    "screen_input",
    "screen_output",
    "log_flag",
    "ScreenResult",
    "HELPLINES",
    "DEFAULT_REGION",
]
