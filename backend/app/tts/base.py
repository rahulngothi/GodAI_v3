from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class VoiceProfile:
    name: str = "krishna-default"

    # ── Browser Web Speech API ──────────────────────────────────────────────
    # Slower rate + lower pitch = calm, not theatrical. Indian voices preferred.
    browser_rate: float = 0.82
    browser_pitch: float = 0.78
    browser_voice_prefs: list[str] = field(default_factory=lambda: [
        "hi-IN", "en-IN",
        "Ravi", "Hemant", "Prabhat", "Madhur",
        "Google हिन्दी", "Microsoft Hemant", "Microsoft Prabhat",
    ])

    # ── ai4bharat/indic-parler-tts ─────────────────────────────────────────
    # Voice is entirely controlled by this description — tune here, not in code.
    indic_description: str = (
        "A calm, warm, middle-aged Indian man speaking slowly and gently, "
        "with a serene, meditative, reverent tone. "
        "The voice is clear and close-sounding with no background noise."
    )

    # ── Cloud voices (future backends) ─────────────────────────────────────
    cloud_voice_id_hi: str = "hi-IN-Neural2-C"
    cloud_voice_id_en: str = "en-IN-Neural2-C"


class TTSBackend(ABC):
    name: str = "base"
    available_languages: list[str] = ["english", "hindi", "hinglish"]

    @abstractmethod
    def synthesize(self, text: str, language: str, profile: VoiceProfile) -> bytes:
        """Return raw audio bytes (WAV / FLAC / MP3 — whatever the backend produces)."""
        ...

    def health_check(self) -> bool:
        """Return False if this backend cannot serve right now (missing key, etc.)."""
        return True
