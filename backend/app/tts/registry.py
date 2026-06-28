from __future__ import annotations

from typing import Type

from .base import TTSBackend

_REGISTRY: dict[str, Type[TTSBackend]] = {}
_instances: dict[str, TTSBackend] = {}


def register(name: str):
    """Class decorator — registers a TTSBackend under `name`.

    Adding a new backend = add one class with @register("myname"), zero
    other code changes required.
    """
    def decorator(cls: Type[TTSBackend]) -> Type[TTSBackend]:
        _REGISTRY[name] = cls
        return cls
    return decorator


def get_backend(name: str) -> TTSBackend | None:
    """Return a cached singleton instance for `name`, or None if unknown."""
    if name not in _REGISTRY:
        return None
    if name not in _instances:
        _instances[name] = _REGISTRY[name]()
    return _instances[name]
