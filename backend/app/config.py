"""Application configuration loaded from the project-root .env file.

Mirrors nebula's settings-singleton convention but lightweight: a single
pydantic-settings model, importable as `from app.config import settings`.
"""
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py -> project root is two parents up
ROOT = Path(__file__).resolve().parents[2]

# Only pass env_file if it's readable (SIP sandbox may block access in preview)
_ENV_FILE = ROOT / ".env"
_env_file_arg = _ENV_FILE if os.access(_ENV_FILE, os.R_OK) else None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_file_arg,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # NVIDIA (serves nv-embedqa embeddings — always used for RAG)
    nvidia_api_key: str
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    embed_model: str = "nvidia/nv-embedqa-e5-v5"

    # LLM provider — swap with env vars, no code change required.
    # LLM_PROVIDER: "nvidia" | "gemini" | "sarvam"
    # LLM_BASE_URL / LLM_API_KEY / LLM_MODEL override per-provider defaults.
    llm_provider: str = "nvidia"
    llm_model: str = ""          # empty → resolved from llm_provider default
    llm_api_key: str = ""        # empty → falls back to nvidia_api_key
    llm_base_url: str = ""       # empty → resolved from llm_provider default

    # RAG: minimum cosine similarity score for a verse to be injected into context.
    # Drop verses below this; prefer no citation over a weakly-related one.
    rag_similarity_threshold: float = 0.30

    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017/"
    mongo_db: str = "dharma_ai"

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Auth (token signing). Override via JWT_SECRET in .env for production.
    jwt_secret: str = "dharma-dev-secret-change-me"

    # Web Push (VAPID). Empty disables push features gracefully.
    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_sub: str = "mailto:admin@example.com"

    # ── Voice / TTS ───────────────────────────────────────────────────────
    # TTS_BACKEND controls which engine is tried first.
    # Fallback chain is tried left-to-right; "browser" signals the client.
    # Supported names: hf_indic, browser
    tts_backend: str = "hf_indic"
    tts_fallback_order: str = "hf_indic,browser"

    # HuggingFace Inference API — required for hf_indic backend.
    # Get a free token at huggingface.co/settings/tokens (read scope is enough).
    hf_api_token: str = ""
    hf_tts_model_url: str = ""  # empty → uses ai4bharat/indic-parler-tts default

    # Audio cache — keyed by hash(text + language + profile + backend).
    tts_cache_enabled: bool = True
    tts_cache_max_items: int = 256

    # "drop" removes [BG 2.47] from audio (visual tag stays on screen).
    # "speak" expands it to "chapter 2, verse 47".
    tts_citation_mode: str = "drop"

    # Voice character — edit these to tune the voice without touching code.
    # browser_rate/pitch: 0.82/0.78 = calm, deep, meditative (not dramatic).
    tts_browser_rate: float = 0.82
    tts_browser_pitch: float = 0.78
    tts_voice_description: str = (
        "A calm, warm, middle-aged Indian man speaking slowly and gently, "
        "with a serene, meditative, reverent tone. "
        "The voice is clear and close-sounding with no background noise."
    )

    # ── Reflective Question Engine ────────────────────────────────────────
    # Master switch — set RQE_ENABLED=false to disable the whole engine.
    rqe_enabled: bool = True

    # Minimum turns between consecutive reflective questions in one conversation.
    rqe_min_turns_between_questions: int = 2

    # When frequency="reduced", require this many turns between questions.
    rqe_reduced_cap: int = 5

    # Every N assistant turns, base depth increases by 1 (max 3).
    rqe_depth_turns_per_level: int = 5

    # Embedding similarity threshold for semantic dedup during generation.
    rqe_dedup_threshold: float = 0.92

    # Exploration factor in candidate ranking (0=pure exploit, 1=pure random).
    rqe_exploration_factor: float = 0.2

    # After this many shows with engagement_rate below the floor, auto-flag.
    rqe_demote_min_shows: int = 20
    rqe_demote_max_rate: float = 0.15

    # How many recently-shown question IDs to remember per user (cross-session).
    rqe_recently_shown_cap: int = 50

    # Generation targets — questions per (theme, type, depth) cell.
    rqe_target_per_cell: int = 4


settings = Settings()
