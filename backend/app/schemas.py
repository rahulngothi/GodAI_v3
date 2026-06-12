"""Pydantic request/response models for the API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Citation(BaseModel):
    ref: str                      # e.g. "BG 2.47"
    chapter: int
    verse: int
    sanskrit: str | None = None
    transliteration: str | None = None
    translation: str
    translator: str
    used: bool = True             # did the model actually cite this verse?


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    persona: str = "guide"


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    followups: list[str]
    persona: str
    persona_name: str
