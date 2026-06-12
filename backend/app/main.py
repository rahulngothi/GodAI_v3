"""Dharma AI FastAPI app — one backend that serves web + (future) mobile clients."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import datetime as _dt

from bson import ObjectId
from fastapi import Depends

from . import ask as ask_module
from . import daily as daily_module
from . import perspectives as perspectives_module
from . import ratelimit
from .auth import authenticate, create_token, get_current_user
from .config import settings
from .db import VERSES, get_db
from .languages import LANGUAGES
from .personas import PERSONAS
from .schemas import (
    AskRequest,
    AskResponse,
    DailyResponse,
    JournalEntry,
    JournalSaveRequest,
    LoginRequest,
    LoginResponse,
    PerspectivesRequest,
    PerspectivesResponse,
)

app = FastAPI(title="Dharma AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    try:
        count = get_db()[VERSES].count_documents({})
        embedded = get_db()[VERSES].count_documents({"embedding": {"$exists": True}})
    except Exception as e:  # pragma: no cover
        return {"status": "db_error", "error": str(e)}
    return {
        "status": "ok",
        "verses": count,
        "embedded": embedded,
        "llm": settings.llm_model,
        "embed": settings.embed_model,
    }


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


@app.post("/api/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    if not authenticate(req.username, req.password):
        raise HTTPException(status_code=401, detail="Wrong username or password.")
    return {"token": create_token(req.username), "username": req.username}


@app.get("/api/auth/me")
def me(user: str = Depends(get_current_user)):
    return {"username": user}


@app.post("/api/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest, user: str = Depends(get_current_user)):
    ratelimit.check(user)
    try:
        return ask_module.ask(
            req.question,
            persona_key=req.persona,
            language=req.language,
            history=[t.model_dump() for t in req.history],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


@app.post("/api/perspectives", response_model=PerspectivesResponse)
def perspectives_endpoint(req: PerspectivesRequest, user: str = Depends(get_current_user)):
    ratelimit.check(user)
    try:
        return perspectives_module.perspectives(req.question, language=req.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


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


# ---- Journal (per user) ----
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


# Serve the web UI (mounted last so /api/* routes win).
_FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
if _FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND), html=True), name="frontend")
