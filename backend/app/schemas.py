"""Pydantic request/response models for the API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Citation(BaseModel):
    ref: str                        # e.g. "BG 2.47" or "Katha Upanishad 1.2.20"
    source: str = "Bhagavad Gita"
    chapter: int | None = None
    verse: int | None = None
    sanskrit: str | None = None
    transliteration: str | None = None
    translation: str
    translator: str
    layer: str = "scripture"        # "scripture" | "teacher" (AI interpretation = the reply itself)
    used: bool = True


# ---- Ask (single guide) ----
class Turn(BaseModel):
    role: str   # "user" | "assistant"
    content: str


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    persona: str = "guide"
    language: str = "english"
    history: list[Turn] = []
    chat_id: str | None = None      # continue a saved conversation


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    followups: list[str]
    persona: str
    persona_name: str
    chat_id: str | None = None


# ---- saved chats ----
class ChatSummary(BaseModel):
    id: str
    title: str
    persona: str
    language: str
    updated: str


class ChatFull(BaseModel):
    id: str
    title: str
    persona: str
    language: str
    turns: list[dict]               # [{role:"user",content} | {role:"assistant", ...AskResponse}]


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


# ---- Auth ----
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class LoginResponse(BaseModel):
    token: str
    username: str


# ---- Journal ----
class JournalSaveRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    prompt: str | None = None       # the journal prompt being answered, if any


class JournalEntry(BaseModel):
    id: str
    date: str
    prompt: str | None = None
    text: str
