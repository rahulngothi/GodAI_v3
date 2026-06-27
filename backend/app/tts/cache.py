from __future__ import annotations

import hashlib
from collections import OrderedDict
from threading import Lock


class AudioCache:
    """Thread-safe LRU in-memory cache for synthesised audio blobs."""

    def __init__(self, max_items: int = 256) -> None:
        self._data: OrderedDict[str, bytes] = OrderedDict()
        self._max = max_items
        self._lock = Lock()

    def _key(self, text: str, language: str, profile_name: str, backend: str) -> str:
        raw = f"{text}|{language}|{profile_name}|{backend}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, text: str, language: str, profile_name: str, backend: str) -> bytes | None:
        k = self._key(text, language, profile_name, backend)
        with self._lock:
            if k in self._data:
                self._data.move_to_end(k)
                return self._data[k]
        return None

    def put(self, text: str, language: str, profile_name: str, backend: str, audio: bytes) -> None:
        k = self._key(text, language, profile_name, backend)
        with self._lock:
            self._data[k] = audio
            self._data.move_to_end(k)
            while len(self._data) > self._max:
                self._data.popitem(last=False)


_instance: AudioCache | None = None


def get_cache(max_items: int = 256) -> AudioCache:
    global _instance
    if _instance is None:
        _instance = AudioCache(max_items)
    return _instance
