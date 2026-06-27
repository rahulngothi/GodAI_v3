from .base import TTSBackend, VoiceProfile
from .cache import get_cache
from .registry import get_backend, register
from .text_prep import prepare_text

# Populate the registry by importing all backends (side-effect: @register calls)
from . import backends  # noqa: F401

__all__ = [
    "TTSBackend",
    "VoiceProfile",
    "get_backend",
    "get_cache",
    "prepare_text",
    "register",
]


def get_default_profile() -> VoiceProfile:
    from app.config import settings
    return VoiceProfile(
        name="krishna-default",
        browser_rate=settings.tts_browser_rate,
        browser_pitch=settings.tts_browser_pitch,
        indic_description=settings.tts_voice_description,
    )
