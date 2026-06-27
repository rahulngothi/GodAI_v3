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
        # Force Hindi + seed with Devanagari prompt so the tokenizer outputs
        # Devanagari instead of Urdu (Arabic) script — same spoken language,
        # different script, and Whisper base confuses the two without this hint.
        segments, _ = model.transcribe(
            tmp_path,
            language="hi",
            initial_prompt="यह हिंदी में बातचीत है।",
            beam_size=5,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return {"text": text, "language": "hi"}
    finally:
        os.unlink(tmp_path)
