"""guardrails.hub - Dynamic import resolution from hub_registry.json.

Validators registered in .guardrails/hub_registry.json are resolved lazily
on first attribute access and cached for subsequent imports.
"""

import importlib

from guardrails.hub.registry import get_registry


_export_map_cache = None


def _build_export_map() -> dict:
    """Build mapping from export name to import path.

    Returns a dict mapping export names (e.g. "DetectPII") to their
    module import paths (e.g. "guardrails_grhub_detect_pii").
    """
    pass


def _get_export_map() -> dict:
    """Return cached export map, building it on first access."""
    pass


def __getattr__(name: str):
    export_map = _get_export_map()
    if name in export_map:
        import_path = export_map[name]
        try:
            module = importlib.import_module(import_path)
            attr = getattr(module, name)
            globals()[name] = attr
            return attr
        except (ModuleNotFoundError, AttributeError) as e:
            raise ImportError(
                f"Cannot import '{name}' from hub registry. "
                f"Module '{import_path}' not found. "
                f"Try reinstalling: guardrails hub install "
                f"hub://<org>/<validator>"
            ) from e
    raise AttributeError(f"module 'guardrails.hub' has no attribute '{name}'")


def __dir__():
    base = list(globals().keys())
    base.extend(_get_export_map().keys())
    return base
