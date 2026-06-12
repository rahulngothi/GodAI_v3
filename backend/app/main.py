"""Dharma AI FastAPI app — one backend that serves web + (future) mobile clients."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import ask as ask_module
from . import daily as daily_module
from . import perspectives as perspectives_module
from .config import settings
from .db import VERSES, get_db
from .languages import LANGUAGES
from .personas import PERSONAS
from .schemas import (
    AskRequest,
    AskResponse,
    DailyResponse,
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


@app.post("/api/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest):
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
def perspectives_endpoint(req: PerspectivesRequest):
    try:
        return perspectives_module.perspectives(req.question, language=req.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


@app.get("/api/daily", response_model=DailyResponse)
def daily_endpoint(period: str | None = None, language: str = "english"):
    try:
        return daily_module.daily(period=period, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


# Serve the web UI (mounted last so /api/* routes win).
_FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
if _FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND), html=True), name="frontend")
