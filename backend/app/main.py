"""Dharma AI FastAPI app — one backend that serves web + (future) mobile clients."""
from __future__ import annotations

import datetime as _dt
from pathlib import Path

import logging

from bson import ObjectId
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

log = logging.getLogger(__name__)


from . import ask as ask_module
from . import daily as daily_module
from . import memory as memory_module
from . import perspectives as perspectives_module
from . import push as push_module
from . import ratelimit
from .auth import authenticate, create_token, get_current_user, signup
from .config import settings
from .db import VERSES, REFLECTIVE_QUESTIONS, USER_PROFILES, ensure_indexes, get_db
from .engagement import ENGAGEMENT_SCORES
from .languages import LANGUAGES
from .personas import PERSONAS
from .schemas import (
    AskRequest,
    AskResponse,
    ChatFull,
    ChatSummary,
    DailyResponse,
    JournalEntry,
    JournalSaveRequest,
    LoginRequest,
    LoginResponse,
    PerspectivesRequest,
    PerspectivesResponse,
    SignupRequest,
    TTSRequest,
    UserProfile,
    UserProfileUpdate,
)

app = FastAPI(title="Dharma AI", version="1.0.0")


@app.on_event("startup")
def _startup():
    try:
        ensure_indexes()
    except Exception:
        pass
    push_module.start_scheduler()
    try:
        get_db()["safety_flags"].create_index([("ts", -1)])
        get_db()["safety_flags"].create_index([("user", 1), ("ts", -1)])
    except Exception:
        pass


# CORS — locked to configured origins (set ALLOWED_ORIGINS in .env).
_origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── health ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    try:
        count = get_db()[VERSES].count_documents({})
        embedded = get_db()[VERSES].count_documents({"embedding": {"$exists": True}})
    except Exception as e:
        return {"status": "db_error", "error": str(e)}
    return {
        "status": "ok",
        "verses": count,
        "embedded": embedded,
        "llm": settings.llm_model,
        "embed": settings.embed_model,
    }


# ─── TTS ──────────────────────────────────────────────────────────────────────

@app.get("/api/tts/health")
def tts_health():
    from .tts import get_backend, get_default_profile
    profile = get_default_profile()
    backend = get_backend(settings.tts_backend)
    return {
        "backend": settings.tts_backend,
        "available": backend is not None and backend.health_check(),
        "fallback_order": settings.tts_fallback_order,
        "voice_profile": profile.name,
        "hf_token_set": bool(settings.hf_api_token),
    }


@app.post("/api/tts")
async def synthesize_speech(body: TTSRequest, user: str = Depends(get_current_user)):
    from .tts import get_backend, get_cache, get_default_profile, prepare_text

    text = prepare_text(body.text, body.language, settings.tts_citation_mode)
    if not text:
        raise HTTPException(400, "Empty text after cleanup")

    profile = get_default_profile()
    chain = [b.strip() for b in settings.tts_fallback_order.split(",") if b.strip()]
    cache = get_cache(settings.tts_cache_max_items)

    for backend_name in chain:
        if backend_name == "browser":
            return JSONResponse({"fallback": "browser"}, status_code=503)

        backend = get_backend(backend_name)
        if backend is None or not backend.health_check():
            continue

        cached = cache.get(text, body.language, profile.name, backend_name)
        if cached:
            return Response(
                content=cached,
                media_type="audio/mpeg",
                headers={"X-TTS-Backend": "cache", "X-TTS-Source": backend_name},
            )

        try:
            audio = await run_in_threadpool(backend.synthesize, text, body.language, profile)
        except Exception as exc:
            log.warning("TTS backend %r failed: %s", backend_name, exc)
            continue

        if settings.tts_cache_enabled:
            cache.put(text, body.language, profile.name, backend_name, audio)

        return Response(
            content=audio,
            media_type="audio/mpeg",
            headers={"X-TTS-Backend": backend_name},
        )

    return JSONResponse({"fallback": "browser"}, status_code=503)


@app.post("/api/stt")
async def transcribe_speech(
    audio: UploadFile = File(...),
    language: str = Form(default=""),
    user: str = Depends(get_current_user),
):
    from .stt import transcribe
    data = await audio.read()
    if not data:
        raise HTTPException(400, "Empty audio file")
    try:
        result = await run_in_threadpool(transcribe, data, language)
    except Exception as exc:
        log.warning("Whisper transcription failed: %s", exc)
        raise HTTPException(500, f"Transcription failed: {exc}") from exc
    return result


# ── personas / languages ──────────────────────────────────────────────────────

@app.get("/api/personas")
def list_personas():
    return [
        {"key": k, "name": v["name"], "blurb": v["blurb"]} for k, v in PERSONAS.items()
    ]


@app.get("/api/languages")
def list_languages():
    return [
        {"key": k, "name": v["name"], "native": v["native"], "bcp47": v["bcp47"]}
        for k, v in LANGUAGES.items()
    ]


# ── auth ──────────────────────────────────────────────────────────────────────

@app.post("/api/auth/signup", response_model=LoginResponse)
def signup_endpoint(req: SignupRequest):
    try:
        signup(req.username, req.password, req.display_name)
        # Persist display_name into user_profiles immediately.
        memory_module.update_profile(req.username, display_name=req.display_name or req.username)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"token": create_token(req.username), "username": req.username}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    if not authenticate(req.username, req.password):
        raise HTTPException(status_code=401, detail="Wrong username or password.")
    return {"token": create_token(req.username), "username": req.username}


@app.get("/api/auth/me")
def me(user: str = Depends(get_current_user)):
    profile = memory_module.get_profile(user)
    return {"username": user, "display_name": profile["display_name"]}


# ── user profile ──────────────────────────────────────────────────────────────

@app.get("/api/profile", response_model=UserProfile)
def profile_get(user: str = Depends(get_current_user)):
    return memory_module.get_profile(user)


@app.patch("/api/profile", response_model=UserProfile)
def profile_update(req: UserProfileUpdate, user: str = Depends(get_current_user)):
    try:
        memory_module.update_profile(
            user,
            display_name=req.display_name,
            preferred_language=req.preferred_language,
            answer_style=req.answer_style,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return memory_module.get_profile(user)


# ── ask ───────────────────────────────────────────────────────────────────────

def _save_turns(user: str, chat_id: str | None, req: AskRequest, result: dict) -> str:
    chats = get_db()["chats"]
    now = _dt.datetime.now(_dt.timezone.utc)
    assistant_turn = {
        "role": "assistant",
        "answer": result["answer"],
        "citations": result["citations"],
        "followups": result["followups"],
        "persona": result["persona"],
        "persona_name": result["persona_name"],
        "reflective": result.get("reflective"),  # reflective question metadata
    }
    # Store engagement signal on the user turn (for the prior question)
    user_turn = {
        "role": "user",
        "content": req.question,
        "engaged_prior_question": result.get("engaged_prior"),
    }
    if chat_id:
        try:
            oid = ObjectId(chat_id)
            r = chats.update_one(
                {"_id": oid, "user": user},
                {"$push": {"turns": {"$each": [user_turn, assistant_turn]}},
                 "$set": {"updated_at": now}},
            )
            if r.matched_count:
                return chat_id
        except Exception:
            pass
    doc = {
        "user": user,
        "title": req.question[:80],
        "persona": req.persona,
        "language": req.language,
        "turns": [user_turn, assistant_turn],
        "created_at": now,
        "updated_at": now,
    }
    return str(chats.insert_one(doc).inserted_id)


@app.post("/api/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest, user: str = Depends(get_current_user)):
    ratelimit.check(user)
    try:
        result = ask_module.ask(
            req.question,
            persona_key=req.persona,
            language=req.language,
            history=[t.model_dump() for t in req.history],
            user=user,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    result["chat_id"] = _save_turns(user, req.chat_id, req, result)
    # Fire-and-forget: update the rolling memory summary in the background.
    memory_module.update_memory_bg(user, req.question, result["answer"])
    return result


@app.post("/api/ask/stream")
def ask_stream_endpoint(req: AskRequest, user: str = Depends(get_current_user)):
    ratelimit.check(user)

    def on_done(result: dict) -> str:
        return _save_turns(user, req.chat_id, req, result)

    return StreamingResponse(
        ask_module.ask_stream(
            req.question,
            persona_key=req.persona,
            language=req.language,
            history=[t.model_dump() for t in req.history],
            user=user,
            on_done=on_done,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ── saved chats ───────────────────────────────────────────────────────────────

@app.get("/api/chats", response_model=list[ChatSummary])
def chats_list(user: str = Depends(get_current_user)):
    docs = get_db()["chats"].find({"user": user}).sort("updated_at", -1).limit(50)
    result = []
    for d in docs:
        preview = ""
        for t in reversed(d.get("turns", [])):
            if t.get("role") == "assistant":
                preview = (t.get("answer") or "").replace("\n", " ").strip()[:80]
                break
        result.append({
            "id": str(d["_id"]),
            "title": d.get("title", ""),
            "persona": d.get("persona", "guide"),
            "language": d.get("language", "english"),
            "updated": d["updated_at"].strftime("%Y-%m-%d %H:%M"),
            "preview": preview,
        })
    return result


@app.get("/api/chats/{chat_id}", response_model=ChatFull)
def chats_get(chat_id: str, user: str = Depends(get_current_user)):
    try:
        oid = ObjectId(chat_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Bad chat id")
    d = get_db()["chats"].find_one({"_id": oid, "user": user})
    if not d:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "id": str(d["_id"]),
        "title": d.get("title", ""),
        "persona": d.get("persona", "guide"),
        "language": d.get("language", "english"),
        "turns": d.get("turns", []),
    }


@app.delete("/api/chats/{chat_id}")
def chats_delete(chat_id: str, user: str = Depends(get_current_user)):
    try:
        oid = ObjectId(chat_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Bad chat id")
    res = get_db()["chats"].delete_one({"_id": oid, "user": user})
    return {"deleted": res.deleted_count == 1}


# ── perspectives ──────────────────────────────────────────────────────────────

@app.post("/api/perspectives", response_model=PerspectivesResponse)
def perspectives_endpoint(req: PerspectivesRequest, user: str = Depends(get_current_user)):
    ratelimit.check(user)
    try:
        return perspectives_module.perspectives(req.question, language=req.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


# ── daily ─────────────────────────────────────────────────────────────────────

@app.get("/api/daily", response_model=DailyResponse)
def daily_endpoint(
    period: str | None = None,
    language: str = "english",
    user: str = Depends(get_current_user),
):
    ratelimit.check(user)
    try:
        return daily_module.daily(period=period, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


# ── journal ───────────────────────────────────────────────────────────────────

@app.post("/api/journal", response_model=JournalEntry)
def journal_save(req: JournalSaveRequest, user: str = Depends(get_current_user)):
    doc = {
        "user": user,
        "date": _dt.date.today().isoformat(),
        "prompt": req.prompt,
        "text": req.text.strip(),
        "created_at": _dt.datetime.now(_dt.timezone.utc),
    }
    res = get_db()["journal"].insert_one(doc)
    return {"id": str(res.inserted_id), "date": doc["date"], "prompt": doc["prompt"], "text": doc["text"]}


@app.get("/api/journal", response_model=list[JournalEntry])
def journal_list(user: str = Depends(get_current_user)):
    docs = get_db()["journal"].find({"user": user}).sort("created_at", -1).limit(50)
    return [
        {"id": str(d["_id"]), "date": d["date"], "prompt": d.get("prompt"), "text": d["text"]}
        for d in docs
    ]


@app.delete("/api/journal/{entry_id}")
def journal_delete(entry_id: str, user: str = Depends(get_current_user)):
    try:
        oid = ObjectId(entry_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Bad entry id")
    res = get_db()["journal"].delete_one({"_id": oid, "user": user})
    return {"deleted": res.deleted_count == 1}


# ── web push ──────────────────────────────────────────────────────────────────

@app.get("/api/push/vapid")
def push_vapid():
    return {"publicKey": settings.vapid_public_key, "enabled": push_module.enabled()}


@app.post("/api/push/subscribe")
def push_subscribe(sub: dict, user: str = Depends(get_current_user)):
    if not sub.get("endpoint"):
        raise HTTPException(status_code=400, detail="Bad subscription")
    push_module.save_subscription(user, sub)
    return {"subscribed": True}


@app.post("/api/push/unsubscribe")
def push_unsubscribe(body: dict, user: str = Depends(get_current_user)):
    removed = push_module.remove_subscription(user, body.get("endpoint", ""))
    return {"unsubscribed": bool(removed)}


@app.post("/api/push/test")
def push_test(user: str = Depends(get_current_user)):
    return push_module.send_to_all("morning")


# ---- Safety flags (admin review, auth-gated) ----
@app.get("/api/admin/safety-flags")
def safety_flags_list(limit: int = 100, user: str = Depends(get_current_user)):
    docs = (
        get_db()["safety_flags"]
        .find({}, {"_id": 0})
        .sort("ts", -1)
        .limit(min(limit, 500))
    )
    return [
        {"user": d["user"], "categories": d["categories"], "ts": d["ts"].isoformat()}
        for d in docs
    ]


# ── Reflective Question Engine — admin endpoints ───────────────────────────

@app.get("/api/admin/rqe/coverage")
def rqe_coverage(user: str = Depends(get_current_user)):
    """Coverage matrix: questions per (theme, type, depth) cell."""
    from .themes import THEMES_LIST
    TYPES = ["self_awareness", "action_oriented", "spiritual"]
    DEPTHS = [1, 2, 3]
    coll = get_db()[REFLECTIVE_QUESTIONS]
    report = {}
    total_q = 0
    for theme in THEMES_LIST:
        for qtype in TYPES:
            for depth in DEPTHS:
                count = coll.count_documents({
                    "themes": theme, "type": qtype, "depth": depth,
                    "status": {"$in": ["approved", "draft"]}, "active": True,
                })
                key = f"{theme}/{qtype}/depth{depth}"
                report[key] = count
                total_q += count
    target = settings.rqe_target_per_cell
    filled = sum(1 for v in report.values() if v >= target)
    partial = sum(1 for v in report.values() if 0 < v < target)
    empty = sum(1 for v in report.values() if v == 0)
    return {
        "total_questions": total_q,
        "cells": {"total": len(report), "filled": filled, "partial": partial, "empty": empty},
        "matrix": report,
        "target_per_cell": target,
    }


@app.get("/api/admin/rqe/analytics")
def rqe_analytics(user: str = Depends(get_current_user)):
    """Engagement rates by theme, type, depth — and top/bottom questions."""
    coll = get_db()[REFLECTIVE_QUESTIONS]
    pipeline_by_theme = [
        {"$match": {"active": True, "stats.shown_count": {"$gt": 0}}},
        {"$unwind": "$themes"},
        {"$group": {
            "_id": "$themes",
            "shown": {"$sum": "$stats.shown_count"},
            "answered": {"$sum": "$stats.answered_count"},
            "questions": {"$sum": 1},
        }},
        {"$addFields": {"engagement_rate": {
            "$cond": [{"$gt": ["$shown", 0]},
                      {"$divide": ["$answered", "$shown"]}, 0]
        }}},
        {"$sort": {"engagement_rate": -1}},
    ]
    pipeline_by_type = [
        {"$match": {"active": True, "stats.shown_count": {"$gt": 0}}},
        {"$group": {
            "_id": {"type": "$type", "depth": "$depth"},
            "shown": {"$sum": "$stats.shown_count"},
            "answered": {"$sum": "$stats.answered_count"},
            "questions": {"$sum": 1},
        }},
        {"$addFields": {"engagement_rate": {
            "$cond": [{"$gt": ["$shown", 0]},
                      {"$divide": ["$answered", "$shown"]}, 0]
        }}},
        {"$sort": {"_id.type": 1, "_id.depth": 1}},
    ]

    def _fmt_q(doc):
        return {
            "id": str(doc["_id"]),
            "en": (doc.get("text") or {}).get("en", "")[:120],
            "themes": doc.get("themes", []),
            "type": doc.get("type"),
            "depth": doc.get("depth"),
            "shown": doc["stats"]["shown_count"],
            "rate": round(doc["stats"]["engagement_rate"], 3),
        }

    top_q = list(coll.find(
        {"active": True, "stats.shown_count": {"$gte": 5}},
        sort=[("stats.engagement_rate", -1)], limit=10
    ))
    bottom_q = list(coll.find(
        {"active": True, "stats.shown_count": {"$gte": 5}},
        sort=[("stats.engagement_rate", 1)], limit=10
    ))
    needs_review = coll.count_documents({"status": "needs_review"})
    runtime_captured = coll.count_documents({"source": "runtime_captured"})

    return {
        "by_theme": list(coll.aggregate(pipeline_by_theme)),
        "by_type_depth": list(coll.aggregate(pipeline_by_type)),
        "top_questions": [_fmt_q(d) for d in top_q],
        "bottom_questions": [_fmt_q(d) for d in bottom_q],
        "needs_review_count": needs_review,
        "runtime_captured_count": runtime_captured,
    }


@app.get("/api/admin/rqe/questions")
def rqe_questions_list(
    status: str = "needs_review",
    limit: int = 50,
    user: str = Depends(get_current_user),
):
    """List questions by status for review."""
    statuses = [s.strip() for s in status.split(",") if s.strip()]
    docs = (
        get_db()[REFLECTIVE_QUESTIONS]
        .find({"status": {"$in": statuses}})
        .sort("created_at", -1)
        .limit(min(limit, 200))
    )
    return [
        {
            "id": str(d["_id"]),
            "en": (d.get("text") or {}).get("en", ""),
            "hi": (d.get("text") or {}).get("hi"),
            "hinglish": (d.get("text") or {}).get("hinglish"),
            "themes": d.get("themes", []),
            "type": d.get("type"),
            "depth": d.get("depth"),
            "status": d.get("status"),
            "source": d.get("source"),
            "active": d.get("active", True),
            "stats": d.get("stats", {}),
        }
        for d in docs
    ]


@app.patch("/api/admin/rqe/questions/{question_id}")
def rqe_question_update(
    question_id: str,
    body: dict,
    user: str = Depends(get_current_user),
):
    """Approve, reject, or deactivate a single question."""
    import datetime as _dt2
    try:
        oid = ObjectId(question_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Bad question id")

    allowed_fields = {"status", "active", "text", "themes", "depth", "type", "emotions", "concepts"}
    update = {k: v for k, v in body.items() if k in allowed_fields}
    if not update:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    update["updated_at"] = _dt2.datetime.now(_dt2.timezone.utc)
    res = get_db()[REFLECTIVE_QUESTIONS].update_one({"_id": oid}, {"$set": update, "$inc": {"version": 1}})
    return {"matched": res.matched_count, "modified": res.modified_count}


@app.get("/api/admin/rqe/user-prefs/{username}")
def rqe_user_prefs(username: str, user: str = Depends(get_current_user)):
    """Inspect a user's reflective preferences."""
    doc = get_db()[USER_PROFILES].find_one({"_id": username})
    if not doc:
        return {"user": username, "reflective_prefs": None}
    return {"user": username, "reflective_prefs": doc.get("reflective_prefs", {})}


# Serve the web UI (mounted last so /api/* routes win).
_FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
if _FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND), html=True), name="frontend")
