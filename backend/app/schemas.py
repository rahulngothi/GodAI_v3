"""Pydantic request/response models for the API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Citation(BaseModel):
    ref: str                        # e.g. "BG 2.47" or "Dhammapada 5"
    source: str = "Bhagavad Gita"
    chapter: int | None = None
    verse: int | None = None
    sanskrit: str | None = None
    transliteration: str | None = None
    translation: str
    translator: str
    used: bool = True


# ---- Ask (single guide) ----
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    persona: str = "guide"
    language: str = "english"


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    followups: list[str]
    persona: str
    persona_name: str


# ---- Multi-Perspective Wisdom ----
class PerspectivesRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    language: str = "english"


class Perspective(BaseModel):
    key: str
    tradition: str
    view: str
    used_refs: list[str] = []


class PerspectivesResponse(BaseModel):
    question: str
    language: str
    perspectives: list[Perspective]
    citations: list[Citation]


# ---- Daily Guidance ----
class DailyResponse(BaseModel):
    date: str
    period: str                     # "morning" | "evening"
    verse: Citation
    reflection: str
    practice: str                   # gratitude / action prompt
    journal_prompt: str
