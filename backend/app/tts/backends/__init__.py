# Backends self-register on import via @register().
# Import them all here so the registry is populated when the package loads.
from . import browser_signal, edge_tts_backend, hf_indic  # noqa: F401
