"""HuggingFace Inference API backend — ai4bharat/indic-parler-tts.

Voice character is set entirely by VoiceProfile.indic_description.
Model URL and token are read from settings so no code change is needed
to swap models or switch to a dedicated HF Inference Endpoint.

Cold-start behaviour: HF returns 503 + estimated_time when the model is
loading. We retry up to 3 times, sleeping the suggested wait (capped at 30s).
"""
from __future__ import annotations

import logging
import time

import httpx

from ..base import TTSBackend, VoiceProfile
from ..registry import register

log = logging.getLogger(__name__)

_DEFAULT_URL = "https://router.huggingface.co/hf-inference/models/ai4bharat/indic-parler-tts"


@register("hf_indic")
class HFIndicParlerBackend(TTSBackend):
    name = "hf_indic"

    def __init__(self) -> None:
        from app.config import settings
        self._token: str = settings.hf_api_token
        self._url: str = settings.hf_tts_model_url or _DEFAULT_URL

    def health_check(self) -> bool:
        return bool(self._token)

    def synthesize(self, text: str, language: str, profile: VoiceProfile) -> bytes:
        if not self._token:
            raise RuntimeError("HF_API_TOKEN not configured — set it in .env")

        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        # indic-parler-tts is a Parler-TTS fine-tune: voice is driven by `description`.
        payload: dict = {
            "inputs": text,
            "parameters": {"description": profile.indic_description},
        }

        with httpx.Client(timeout=90.0) as client:
            for attempt in range(3):
                resp = client.post(self._url, headers=headers, json=payload)

                if resp.status_code == 200:
                    return resp.content

                if resp.status_code == 503:
                    try:
                        wait = float(resp.json().get("estimated_time", 25))
                    except Exception:
                        wait = 25.0
                    wait = min(wait, 30.0)
                    log.info(
                        "indic-parler-tts warming up — sleeping %.0fs (attempt %d/3)",
                        wait, attempt + 1,
                    )
                    time.sleep(wait)
                    continue

                raise RuntimeError(
                    f"HF API returned {resp.status_code}: {resp.text[:300]}"
                )

        raise RuntimeError("HF API: model still loading after 3 retries")
