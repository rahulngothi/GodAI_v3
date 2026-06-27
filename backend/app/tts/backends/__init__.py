# Backends self-register on import via @register().
# Import them all here so the registry is populated when the package loads.
from . import browser_signal, hf_indic  # noqa: F401
