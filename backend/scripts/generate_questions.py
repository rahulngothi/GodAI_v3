"""Reflective Question Library — generation pipeline.

Usage:
  python -m scripts.generate_questions          # generate full 1000-question library
  python -m scripts.generate_questions --dry-run  # print coverage matrix only
  python -m scripts.generate_questions --themes anger,failure  # specific themes

Design:
  - Generates across 28 themes × 3 types × 3 depths = 252 cells
  - Target: settings.rqe_target_per_cell questions per cell (default 4)
  - Validates each question against the quality bar before inserting
  - Deduplicates via embedding similarity before inserting
  - Idempotent: re-running fills gaps only; never overwrites approved/edited rows
  - Seeds gold-standard questions from GOLD_SEEDS below (marked human_written)
  - All generated questions start as status="draft"; human review promotes to "approved"
"""
from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import sys
import time
from pathlib import Path

# Allow running as `python -m scripts.generate_questions` from backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.db import get_db, ensure_reflective_indexes, REFLECTIVE_QUESTIONS
from app.nvidia import chat, embed_one
from app.themes import THEMES_LIST

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Generation matrix
# ---------------------------------------------------------------------------
TYPES = ["self_awareness", "action_oriented", "spiritual"]
DEPTHS = [1, 2, 3]
DEPTH_LABELS = {1: "gentle/opening", 2: "moderate", 3: "deep/probing"}
INTENSITY_FLOORS = {1: "any", 2: "mild", 3: "moderate"}

# ---------------------------------------------------------------------------
# Gold-standard seed questions (human-written, auto-approved)
# ---------------------------------------------------------------------------
GOLD_SEEDS: list[dict] = [
    {
        "text": {
            "en": "What is it you are truly seeking here — the world's recognition, or your own peace?",
            "hi": "तुम सच में क्या खोज रहे हो — दूसरों की पहचान, या अपनी शांति?",
            "hinglish": "Aap sach mein kya dhoondh rahe ho — duniya ki pahchaan, ya apni shanti?",
        },
        "themes": ["ego", "self_worth", "restlessness"],
        "type": "self_awareness",
        "depth": 2,
        "emotions": ["longing", "pride", "confusion"],
        "concepts": ["ego", "equanimity"],
    },
    {
        "text": {
            "en": "If the outcome of this were not in your hands at all, would you still choose to act?",
            "hi": "यदि इसका परिणाम तुम्हारे हाथ में न होता, तो क्या तुम फिर भी यही कर्म चुनते?",
            "hinglish": "Agar is ka natija bilkul aapke haath mein na hota — toh bhi yahi karte?",
        },
        "themes": ["duty", "attachment", "control"],
        "type": "action_oriented",
        "depth": 2,
        "emotions": ["anxiety", "doubt"],
        "concepts": ["karma", "detachment", "dharma"],
        "related_verses": ["BG 2.47"],
    },
    {
        "text": {
            "en": "Whose voice are you listening to when you call yourself a failure — your own, or one you borrowed long ago?",
            "hi": "जब तुम खुद को असफल कहते हो — यह तुम्हारी अपनी आवाज़ है, या कोई और आवाज़ जो तुमने बहुत पहले अपना ली?",
            "hinglish": "Jab tum khud ko asafal kehte ho — yeh tumhari apni aawaaz hai, ya koi aur aawaaz jo tumne bahut pehle apna li?",
        },
        "themes": ["failure", "self_worth", "ego"],
        "type": "self_awareness",
        "depth": 3,
        "emotions": ["shame", "self-criticism"],
        "concepts": ["ego", "witness-self"],
    },
    {
        "text": {
            "en": "What would remain of this fear if you released your grip on how it must turn out?",
            "hi": "यदि तुम यह पकड़ छोड़ दो कि यह कैसे होना चाहिए — तो इस डर में से क्या शेष बचेगा?",
            "hinglish": "Agar aap yeh pakad chod do ki yeh kaisa hona chahiye — toh is dar mein se kya bachi rahegi?",
        },
        "themes": ["fear", "attachment", "control"],
        "type": "spiritual",
        "depth": 2,
        "emotions": ["dread", "clinging"],
        "concepts": ["detachment", "surrender"],
    },
    {
        "text": {
            "en": "When this flares up, whose peace is it that most suffers?",
            "hi": "जब यह क्रोध उठता है, सबसे पहले किसकी शांति भंग होती है?",
            "hinglish": "Jab yeh gussa uthta hai — sabse pehle kiska sukoon toot-ta hai?",
        },
        "themes": ["anger", "restlessness"],
        "type": "self_awareness",
        "depth": 1,
        "emotions": ["frustration"],
        "concepts": ["equanimity"],
    },
    {
        "text": {
            "en": "If the thing you are holding most tightly were to pass — what would remain of you?",
            "hi": "जो चीज़ आप सबसे कसकर थामे हुए हैं, वह चली जाए तो आप में क्या शेष बचेगा?",
            "hinglish": "Jo cheez aap sabse zyada pakde hue hain — woh chali jaaye toh aap mein kya bacha rahega?",
        },
        "themes": ["attachment", "grief", "control"],
        "type": "spiritual",
        "depth": 2,
        "emotions": ["clinging", "fear of loss"],
        "concepts": ["detachment", "impermanence"],
    },
    {
        "text": {
            "en": "Whose measure of success are you failing by — your own, or one you absorbed without choosing?",
            "hi": "आप किसकी कसौटी पर असफल हो रहे हैं — अपनी, या वह जो कभी बिना चुने अपना ली?",
            "hinglish": "Aap kiske scale par fail ho rahe hain — apne, ya woh jo kabhi bina choose kiye apna li?",
        },
        "themes": ["failure", "comparison", "self_worth"],
        "type": "self_awareness",
        "depth": 2,
        "emotions": ["shame", "resentment"],
        "concepts": ["ego", "svadharma"],
    },
    {
        "text": {
            "en": "In the quiet of this aloneness, what is the voice that speaks most clearly?",
            "hi": "इस एकांत की शांति में, कौन-सी आवाज़ सबसे स्पष्ट सुनाई देती है?",
            "hinglish": "Is akele pal ki khamoshi mein — kaun si aawaaz sabse saaf sunai deti hai?",
        },
        "themes": ["loneliness", "restlessness"],
        "type": "spiritual",
        "depth": 1,
        "emotions": ["emptiness", "longing"],
        "concepts": ["witness-self"],
    },
    {
        "text": {
            "en": "If you stripped away what you have achieved and what others think of you — who is left, and is that person enough?",
            "hi": "यदि आप अपनी सभी उपलब्धियाँ और दूसरों की राय हटा दें — तो जो बचता है, क्या वह पर्याप्त है?",
            "hinglish": "Agar sab achievements aur duniya ki raay hataa do — jo bacha, kya woh kaafi hai?",
        },
        "themes": ["self_worth", "ego", "comparison"],
        "type": "self_awareness",
        "depth": 3,
        "emotions": ["emptiness", "fear"],
        "concepts": ["ego", "witness-self"],
    },
    {
        "text": {
            "en": "What would you do with yourself if, just for today, you stopped trying to arrive somewhere?",
            "hi": "यदि आज बस एक दिन के लिए आप कहीं पहुँचने की कोशिश छोड़ दें — तो क्या करेंगे?",
            "hinglish": "Agar sirf aaj ke liye aap kahi pahunchne ki koshish band kar do — toh kya karoge?",
        },
        "themes": ["restlessness", "purpose", "anxiety"],
        "type": "action_oriented",
        "depth": 1,
        "emotions": ["drivenness", "exhaustion"],
        "concepts": ["equanimity"],
    },
]

# ---------------------------------------------------------------------------
# Quality bar — generation prompt
# ---------------------------------------------------------------------------
_GENERATION_PROMPT = """\
You are generating reflective questions for a spiritual AI companion whose voice is warm, reverent,
and grounded in the Bhagavad Gita. Your output will be used in production.

QUALITY BAR — a good question:
- Is open-ended: never answerable with yes/no or a single word.
- Invites introspection, not information. Turns the person inward.
- Is non-leading: does not smuggle in advice or a "correct" answer.
- Is grounded in the Gita's worldview (attachment, duty/svadharma, restless mind,
  desire/aversion, fruit of action, equanimity, witness-self) — no verse citation required.
- Matches the reverent register: serene, dignified, contemplative, warm.
  Never casual, never clinical, never preachy.
- Is ONE question only. No stacked questions with multiple "?"s.
- Is {depth_label} — {depth_guidance}

REJECT — do NOT generate:
- Yes/no or factual questions ("Are you angry?", "Did that happen yesterday?")
- Therapy clichés ("How does that make you feel?", "Can you sit with that?", "What comes up for you?")
- Leading/advice-in-disguise ("Don't you think you should just let it go?")
- Casual/slangy phrasing ("What's really bugging you?")
- Preachy, judgmental, or shaming questions
- Multi-part questions (two or more "?" clusters)

TARGET REGISTER EXAMPLES (match this voice exactly):
- "What is it you are truly seeking here — the world's recognition, or your own peace?"
- "If the outcome of this were not in your hands at all, would you still choose to act?"
- "Whose voice are you listening to when you call yourself a failure — your own, or one you borrowed long ago?"
- "What would remain of this fear if you released your grip on how it must turn out?"

TASK: Generate {n} DISTINCT reflective questions for:
  Theme: {theme}
  Type: {qtype} — {type_guidance}
  Depth: {depth} ({depth_label}) — {depth_guidance}
  Intensity floor: {floor} (show only when emotional distress is {floor_guidance})

For each question produce natural phrasing in all three registers:
  - en: English (canonical)
  - hi: Hindi in Devanagari script (natural and reverent — आप-form, not a literal translation)
  - hinglish: Romanized dignified Hinglish (Latin script only, no Devanagari)

Also list 2-3 emotions and 1-2 Gita concepts it touches.

Self-flag with "uncertain": true if you are not confident the question meets the bar.

Reply with a JSON array only — no commentary, no preamble:
[
  {{
    "en": "...",
    "hi": "...",
    "hinglish": "...",
    "emotions": ["...", "..."],
    "concepts": ["...", "..."],
    "uncertain": false
  }},
  ...
]
"""

_TYPE_GUIDANCE = {
    "self_awareness": "turns the seeker toward examining their own inner patterns, assumptions, and identity",
    "action_oriented": "invites reflection on choices, actions, duty, and what the seeker would or could do",
    "spiritual": "opens toward the Gita's deeper teachings — surrender, witness-self, impermanence, the infinite",
}
_DEPTH_GUIDANCE = {
    1: "gentle and opening — safe for a first exchange or a fragile emotional state. Soft, welcoming, low-stakes.",
    2: "moderate — assumes some trust is established. Goes one layer deeper than surface. Warm but probing.",
    3: "deep and probing — only for a stable, reflective seeker with established trust. Can touch the most fundamental questions of self and meaning.",
}
_FLOOR_GUIDANCE = {
    "any": "any level (including acute distress)",
    "mild": "mild distress or below",
    "moderate": "moderate distress or below (stable enough for reflection)",
}


def _generation_prompt(theme: str, qtype: str, depth: int, n: int) -> str:
    floor = INTENSITY_FLOORS[depth]
    return _GENERATION_PROMPT.format(
        theme=theme,
        qtype=qtype,
        type_guidance=_TYPE_GUIDANCE[qtype],
        depth=depth,
        depth_label=DEPTH_LABELS[depth],
        depth_guidance=_DEPTH_GUIDANCE[depth],
        floor=floor,
        floor_guidance=_FLOOR_GUIDANCE[floor],
        n=n,
    )


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------
_YES_NO_PATTERNS = [
    r"^(are|is|do|does|did|have|has|had|will|would|could|can|should|were|was)\b",
    r"^(have you|did you|are you|do you|will you|can you|could you|would you)\b",
]
_CLICHE_PHRASES = [
    "how does that make you feel",
    "can you sit with",
    "what comes up for you",
    "how are you feeling",
    "what are you feeling",
    "don't you think you should",
    "wouldn't it be better",
    "what's really bugging",
    "what's going on",
    "tell me more",
]
_CASUAL_WORDS = ["yaar", "bro", "dude", "man ", "hey ", "gonna", "wanna", "kinda", "sorta"]

import re as _re


def validate_question(en: str) -> tuple[bool, str]:
    """Returns (is_valid, reason). Checks against the quality bar."""
    q = en.strip()

    # Must end with ?
    if "?" not in q:
        return False, "no question mark"

    # Multi-part: two or more standalone question marks (allow em-dash questions like "X — Y?")
    if q.count("?") > 1:
        return False, "multi-part question"

    # Yes/no pattern
    q_lower = q.lower()
    for pat in _YES_NO_PATTERNS:
        if _re.match(pat, q_lower):
            return False, "yes/no question"

    # Clichés
    for cliche in _CLICHE_PHRASES:
        if cliche in q_lower:
            return False, f"therapy cliché: {cliche!r}"

    # Casual
    for word in _CASUAL_WORDS:
        if word in q_lower:
            return False, f"casual phrasing: {word!r}"

    # Too short
    words = q.split()
    if len(words) < 8:
        return False, "too short (< 8 words)"

    # Too long — a single question shouldn't be an essay
    if len(words) > 50:
        return False, "too long (> 50 words)"

    return True, "ok"


# ---------------------------------------------------------------------------
# Embedding-based dedup
# ---------------------------------------------------------------------------
_cached_embeddings: list[tuple[str, list[float]]] = []  # (doc_id, embedding)


def _load_existing_embeddings(db) -> None:
    """Load en texts of existing questions into in-process cache for dedup."""
    global _cached_embeddings
    _cached_embeddings = []
    for doc in db[REFLECTIVE_QUESTIONS].find({}, {"_id": 1, "text.en": 1}):
        en = (doc.get("text") or {}).get("en", "")
        if en:
            try:
                emb = embed_one(en, input_type="query")
                _cached_embeddings.append((str(doc["_id"]), emb))
            except Exception:
                pass


def _is_near_duplicate(en: str, threshold: float) -> bool:
    """Return True if `en` is semantically too close to any cached question."""
    if not _cached_embeddings:
        return False
    import numpy as np
    try:
        new_emb = embed_one(en, input_type="query")
        new_v = np.array(new_emb, dtype="float32")
        new_v /= np.linalg.norm(new_v) + 1e-9
        for _, emb in _cached_embeddings:
            v = np.array(emb, dtype="float32")
            v /= np.linalg.norm(v) + 1e-9
            if float(new_v @ v) >= threshold:
                return True
        return False
    except Exception:
        return False


def _add_to_dedup_cache(doc_id: str, en: str) -> None:
    try:
        emb = embed_one(en, input_type="query")
        _cached_embeddings.append((doc_id, emb))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Coverage query
# ---------------------------------------------------------------------------
def coverage_report(db) -> dict:
    """Return {cell: count} for all (theme, type, depth) combinations."""
    report: dict[str, int] = {}
    for theme in THEMES_LIST:
        for qtype in TYPES:
            for depth in DEPTHS:
                key = f"{theme}/{qtype}/depth{depth}"
                count = db[REFLECTIVE_QUESTIONS].count_documents({
                    "themes": theme,
                    "type": qtype,
                    "depth": depth,
                    "status": {"$in": ["approved", "draft"]},
                    "active": True,
                })
                report[key] = count
    return report


def print_coverage(report: dict) -> None:
    total_cells = len(THEMES_LIST) * len(TYPES) * len(DEPTHS)
    filled = sum(1 for v in report.values() if v > 0)
    total_q = sum(report.values())
    print(f"\n{'─'*70}")
    print(f"  COVERAGE REPORT: {filled}/{total_cells} cells filled | {total_q} total questions")
    print(f"{'─'*70}")
    for theme in THEMES_LIST:
        row_parts = []
        for qtype in TYPES:
            for depth in DEPTHS:
                key = f"{theme}/{qtype}/depth{depth}"
                cnt = report[key]
                marker = "✓" if cnt >= settings.rqe_target_per_cell else ("·" if cnt > 0 else "○")
                row_parts.append(f"{marker}{cnt}")
        print(f"  {theme:<20} {' '.join(row_parts)}")
    print(f"{'─'*70}")
    print(f"  Legend: ✓=target met  ·=partial  ○=empty")
    print(f"  Columns: [self_awareness/1,2,3] [action_oriented/1,2,3] [spiritual/1,2,3]")
    print()


# ---------------------------------------------------------------------------
# Insert a question document
# ---------------------------------------------------------------------------
def _make_doc(
    en: str, hi: str, hinglish: str,
    theme: str, qtype: str, depth: int,
    emotions: list[str], concepts: list[str],
    source: str = "llm_generated",
    status: str = "draft",
    related_verses: list[str] | None = None,
    extra_themes: list[str] | None = None,
) -> dict:
    now = datetime.datetime.now(datetime.timezone.utc)
    themes = [theme]
    if extra_themes:
        for t in extra_themes:
            if t not in themes:
                themes.append(t)
    return {
        "text": {"en": en, "hi": hi or None, "hinglish": hinglish or None},
        "themes": themes,
        "type": qtype,
        "depth": depth,
        "intensity_safe_floor": INTENSITY_FLOORS[depth],
        "emotions": emotions,
        "concepts": concepts,
        "persona_fit": [],
        "related_verses": related_verses or [],
        "status": status,
        "source": source,
        "stats": {
            "shown_count": 0,
            "answered_count": 0,
            "engagement_rate": 0.0,
            "last_shown_at": None,
        },
        "active": True,
        "created_at": now,
        "updated_at": now,
        "version": 1,
    }


# ---------------------------------------------------------------------------
# Seed gold questions
# ---------------------------------------------------------------------------
def seed_gold_questions(db) -> int:
    """Insert gold-standard human-written seeds (idempotent by en text)."""
    inserted = 0
    coll = db[REFLECTIVE_QUESTIONS]
    for seed in GOLD_SEEDS:
        en = seed["text"]["en"]
        if coll.find_one({"text.en": en}):
            continue
        doc = _make_doc(
            en=en,
            hi=seed["text"].get("hi", ""),
            hinglish=seed["text"].get("hinglish", ""),
            theme=seed["themes"][0],
            qtype=seed["type"],
            depth=seed["depth"],
            emotions=seed.get("emotions", []),
            concepts=seed.get("concepts", []),
            source="human_written",
            status="approved",
            related_verses=seed.get("related_verses", []),
            extra_themes=seed["themes"][1:],
        )
        result = coll.insert_one(doc)
        _add_to_dedup_cache(str(result.inserted_id), en)
        inserted += 1
    log.info("Gold seeds: inserted %d", inserted)
    return inserted


# ---------------------------------------------------------------------------
# Generate one cell
# ---------------------------------------------------------------------------
def generate_cell(
    db,
    theme: str,
    qtype: str,
    depth: int,
    target: int,
    dry_run: bool = False,
) -> int:
    """Generate questions for one (theme, type, depth) cell. Returns count inserted."""
    coll = db[REFLECTIVE_QUESTIONS]

    # Count already-existing non-rejected questions for this cell
    existing = coll.count_documents({
        "themes": theme,
        "type": qtype,
        "depth": depth,
        "status": {"$in": ["approved", "draft", "needs_review"]},
        "active": True,
    })
    needed = max(0, target - existing)
    if needed == 0:
        return 0

    if dry_run:
        log.info("DRY-RUN %s/%s/depth%d — need %d", theme, qtype, depth, needed)
        return 0

    log.info("Generating %d questions for %s/%s/depth%d …", needed, theme, qtype, depth)
    prompt = _generation_prompt(theme, qtype, depth, needed + 2)  # ask extra, validate filters

    raw = None
    for attempt in range(4):
        try:
            raw = chat(
                [{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=2000,
            )
            break
        except Exception as exc:
            exc_str = str(exc)
            is_rate_limit = "429" in exc_str
            wait = (60 * (attempt + 1)) if is_rate_limit else (8 * (attempt + 1))
            log.warning("LLM attempt %d failed for %s/%s/depth%d (%s) — waiting %ds",
                        attempt + 1, theme, qtype, depth,
                        "rate-limited" if is_rate_limit else "error", wait)
            if attempt < 3:
                time.sleep(wait)
    if raw is None:
        log.error("All LLM attempts failed for %s/%s/depth%d", theme, qtype, depth)
        return 0

    # Parse JSON array
    raw = raw.strip()
    s, e = raw.find("["), raw.rfind("]")
    if s == -1 or e == -1:
        log.warning("No JSON array in response for %s/%s/depth%d", theme, qtype, depth)
        return 0

    try:
        items: list[dict] = json.loads(raw[s:e+1])
    except Exception as exc:
        log.warning("JSON parse error for %s/%s/depth%d: %s", theme, qtype, depth, exc)
        return 0

    inserted = 0
    for item in items:
        if inserted >= needed:
            break

        en = (item.get("en") or "").strip()
        hi = (item.get("hi") or "").strip()
        hinglish = (item.get("hinglish") or "").strip()

        if not en:
            continue

        # Validator
        valid, reason = validate_question(en)
        if not valid:
            log.debug("Rejected [%s]: %s", reason, en[:80])
            continue

        # Skip flagged by model itself
        if item.get("uncertain"):
            log.debug("Model-flagged uncertain: %s", en[:80])
            continue

        # Exact-text dedup
        if coll.find_one({"text.en": en}):
            log.debug("Exact duplicate skipped")
            continue

        # Semantic dedup
        if _is_near_duplicate(en, settings.rqe_dedup_threshold):
            log.debug("Near-duplicate skipped: %s", en[:80])
            continue

        doc = _make_doc(
            en=en, hi=hi, hinglish=hinglish,
            theme=theme, qtype=qtype, depth=depth,
            emotions=item.get("emotions", []),
            concepts=item.get("concepts", []),
            source="llm_generated",
            status="draft",
        )
        result = coll.insert_one(doc)
        _add_to_dedup_cache(str(result.inserted_id), en)
        inserted += 1

    log.info("  → inserted %d/%d for %s/%s/depth%d", inserted, needed, theme, qtype, depth)
    return inserted


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Generate reflective question library")
    parser.add_argument("--dry-run", action="store_true", help="Print coverage only")
    parser.add_argument("--themes", default="", help="Comma-separated theme filter")
    parser.add_argument("--types", default="", help="Comma-separated type filter")
    parser.add_argument("--depths", default="", help="Comma-separated depth filter (1,2,3)")
    parser.add_argument("--target", type=int, default=settings.rqe_target_per_cell,
                        help="Questions per cell")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Seconds between LLM calls (rate-limit buffer)")
    args = parser.parse_args()

    db = get_db()
    ensure_reflective_indexes()

    theme_filter = [t.strip() for t in args.themes.split(",") if t.strip()] or THEMES_LIST
    type_filter  = [t.strip() for t in args.types.split(",")  if t.strip()] or TYPES
    depth_filter = [int(d)    for d in args.depths.split(",") if d.strip()] or DEPTHS

    # Validate filters
    for t in theme_filter:
        if t not in THEMES_LIST:
            print(f"ERROR: unknown theme {t!r}. Valid: {', '.join(THEMES_LIST)}")
            sys.exit(1)

    if args.dry_run:
        report = coverage_report(db)
        print_coverage(report)
        return

    log.info("Loading existing embeddings for dedup …")
    _load_existing_embeddings(db)

    log.info("Seeding gold-standard questions …")
    seed_gold_questions(db)

    total_inserted = 0
    total_cells = len(theme_filter) * len(type_filter) * len(depth_filter)
    cell_num = 0

    for theme in theme_filter:
        for qtype in type_filter:
            for depth in depth_filter:
                cell_num += 1
                log.info("[%d/%d] %s / %s / depth%d", cell_num, total_cells, theme, qtype, depth)
                n = generate_cell(db, theme, qtype, depth, args.target)
                total_inserted += n
                if n > 0 and args.delay > 0:
                    time.sleep(args.delay)

    report = coverage_report(db)
    print_coverage(report)
    log.info("Done. Total questions inserted this run: %d", total_inserted)


if __name__ == "__main__":
    main()
