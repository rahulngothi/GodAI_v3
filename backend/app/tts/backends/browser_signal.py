"""Browser-signal backend — sentinel that tells the client to use Web Speech API.

This is the last entry in the fallback chain. It never synthesises audio
server-side; the route handler intercepts it and returns a 503 with
{"fallback": "browser"} so the JS can switch to speakRaw().
"""
from ..base import TTSBackend, VoiceProfile
from ..registry import register


@register("browser")
class BrowserSignalBackend(TTSBackend):
    name = "browser"

    def synthesize(self, text: str, language: str, profile: VoiceProfile) -> bytes:
        raise NotImplementedError("browser TTS is client-side only")
