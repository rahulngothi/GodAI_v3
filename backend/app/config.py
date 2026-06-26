"""Application configuration loaded from the project-root .env file.

Mirrors nebula's settings-singleton convention but lightweight: a single
pydantic-settings model, importable as `from app.config import settings`.
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py -> project root is two parents up
ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # NVIDIA (serves Kimi K2.6 chat + nv-embedqa embeddings)
    nvidia_api_key: str
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    llm_model: str = "moonshotai/kimi-k2.6"
    embed_model: str = "nvidia/nv-embedqa-e5-v5"

    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017/"
    mongo_db: str = "dharma_ai"

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Auth (token signing). Set JWT_SECRET in .env — never use the default in production.
    jwt_secret: str = "dharma-dev-secret-change-me"

    # CORS — comma-separated allowed origins, e.g. "http://localhost:8000,https://yourdomain.com"
    allowed_origins: str = "*"

    # Web Push (VAPID). Empty disables push features gracefully.
    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_sub: str = "mailto:admin@example.com"


settings = Settings()
