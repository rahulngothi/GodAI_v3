"""Supported languages (PRD Feature 4). BCP-47 codes drive browser STT/TTS."""

LANGUAGES: dict[str, dict] = {
    "english":  {"name": "English",  "native": "English", "bcp47": "en-IN"},
    "hindi":    {"name": "Hindi",    "native": "हिन्दी",   "bcp47": "hi-IN"},
    "marathi":  {"name": "Marathi",  "native": "मराठी",    "bcp47": "mr-IN"},
    "tamil":    {"name": "Tamil",    "native": "தமிழ்",    "bcp47": "ta-IN"},
    "telugu":   {"name": "Telugu",   "native": "తెలుగు",   "bcp47": "te-IN"},
    "kannada":  {"name": "Kannada",  "native": "ಕನ್ನಡ",    "bcp47": "kn-IN"},
    "bengali":  {"name": "Bengali",  "native": "বাংলা",    "bcp47": "bn-IN"},
}

DEFAULT_LANGUAGE = "english"


def lang_name(key: str) -> str:
    return LANGUAGES.get(key, LANGUAGES[DEFAULT_LANGUAGE])["name"]
