"""Microsoft Edge TTS backend — no API key, no account required.

Uses the `edge-tts` package which talks to Microsoft's neural TTS service
(the same engine powering Edge browser's Read Aloud).

Voice mapping:
  hindi     → hi-IN-MadhurNeural   (warm, natural Indian male, Hindi)
  english   → en-IN-PrabhatNeural  (Indian-accented English male)
  hinglish  → hi-IN-MadhurNeural   (handles code-switched text well)

Rate and pitch are tuned for a calm, meditative register — not the default
energetic podcast pace.
"""
from __future__ import annotations

import asyncio
import io
import logging

from ..base import TTSBackend, VoiceProfile
from ..registry import register

log = logging.getLogger(__name__)

_VOICE_MAP = {
    "hindi": "hi-IN-MadhurNeural",
    "hinglish": "hi-IN-MadhurNeural",
    "english": "en-IN-PrabhatNeural",
}


@register("edge_tts")
class EdgeTTSBackend(TTSBackend):
    """Microsoft Edge neural TTS — free, no key, authentic Indian voices."""

    name = "edge_tts"

    def health_check(self) -> bool:
        try:
            import edge_tts  # noqa: F401
            return True
        except ImportError:
            return False

    def synthesize(self, text: str, language: str, profile: VoiceProfile) -> bytes:
        import edge_tts

        voice = _VOICE_MAP.get(language, "en-IN-PrabhatNeural")

        async def _run() -> bytes:
            buf = io.BytesIO()
            tts = edge_tts.Communicate(
                text,
                voice=voice,
                rate="-12%",   # slower → calm, not rushed
                pitch="-4Hz",  # slightly deeper → dignified
            )
            async for chunk in tts.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])
            return buf.getvalue()

        # Run the async Edge TTS call in its own event loop
        # (FastAPI's run_in_threadpool gives us a plain thread, no loop)
        return asyncio.run(_run())
