"""Dharma AI FastAPI app — one backend that serves web + (future) mobile clients."""
from __future__ import annotations

import datetime as _dt
from pathlib import Path

from bson import ObjectId
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import ask as ask_module
from . import daily as daily_module
from . import memory as memory_module
from . import perspectives as perspectives_module
from . import push as push_module
from . import ratelimit
from .auth import authenticate, create_token, get_current_user, signup
from .config import settings
from .db import VERSES, ensure_indexes, get_db
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
    UserProfile,
    UserProfileUpdate,
)

app = FastAPI(title="Dharma AI", version="1.0.0")


@app.on_event("startup")
def _startup():
    ensure_indexes()
    push_module.start_scheduler()


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
    }
    user_turn = {"role": "user", "content": req.question}
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


# ── saved chats ───────────────────────────────────────────────────────────────

@app.get("/api/chats", response_model=list[ChatSummary])
def chats_list(user: str = Depends(get_current_user)):
    docs = get_db()["chats"].find({"user": user}).sort("updated_at", -1).limit(50)
    return [
        {
            "id": str(d["_id"]),
            "title": d.get("title", ""),
            "persona": d.get("persona", "guide"),
            "language": d.get("language", "english"),
            "updated": d["updated_at"].strftime("%Y-%m-%d %H:%M"),
        }
        for d in docs
    ]


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


# Serve the web UI (mounted last so /api/* routes win).
_FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
if _FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND), html=True), name="frontend")
