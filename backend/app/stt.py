"""Whisper-based Speech-to-Text using faster-whisper.

Model is loaded lazily on first request (downloads ~142 MB for 'base').
Subsequent requests hit the in-memory model — no reload cost.

Accepts any audio format ffmpeg can decode (WebM Opus from Chrome,
MP4 from Safari, WAV, etc.).
"""
from __future__ import annotations

import logging
import os
import tempfile
from functools import lru_cache

log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_model():
    from faster_whisper import WhisperModel
    model_name = os.environ.get("WHISPER_MODEL", "base")
    log.info("Loading Whisper model '%s' (first request — may download)…", model_name)
    # cpu + int8 = good speed on Mac without GPU
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    log.info("Whisper '%s' ready.", model_name)
    return model


def transcribe(audio_bytes: bytes, hint_language: str = "") -> dict:
    """Transcribe raw audio bytes. Returns {"text": str, "language": str}."""
    model = _get_model()

    # Write to a temp file so faster-whisper can detect format via ffmpeg
    suffix = ".webm"  # ffmpeg handles format detection regardless of extension
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name

    try:
        # language=None → auto-detect (best for Hindi/Hinglish/English)
        # beam_size=5, best_of=5 → accuracy over speed
        lang_arg = hint_language if hint_language in ("hi", "en") else None
        segments, info = model.transcribe(
            tmp_path,
            language=lang_arg,
            beam_size=5,
            vad_filter=True,       # skip silent regions
            vad_parameters={"min_silence_duration_ms": 500},
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return {"text": text, "language": info.language}
    finally:
        os.unlink(tmp_path)
