"""Dharma AI FastAPI app — one backend that serves web + (future) mobile clients."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import ask as ask_module
from .config import settings
from .db import VERSES, get_db
from .personas import PERSONAS
from .schemas import AskRequest, AskResponse

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


@app.post("/api/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest):
    try:
        return ask_module.ask(req.question, persona_key=req.persona)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


# Serve the web UI (mounted last so /api/* routes win).
_FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
if _FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND), html=True), name="frontend")
