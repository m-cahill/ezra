"""Plugin registry for dynamic plugin resolution.

This module provides a static registry mapping plugin names to their module paths
and class names. Plugins are resolved lazily to avoid importing heavy ML modules
at registry import time.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any, cast

from ezra.plugins.interface import OCRPlugin

# Static registry mapping plugin names to "module.path:ClassName" strings
_PLUGIN_REGISTRY: dict[str, str] = {
    "easyocr": "ezra.plugins.easyocr_plugin:EasyOCRPlugin",
}


def get_plugin(name: str, **kwargs: Any) -> OCRPlugin:
    """Get a plugin instance by name.

    Args:
        name: Plugin name (e.g., "easyocr").
        **kwargs: Plugin-specific initialization arguments.

    Returns:
        Plugin instance implementing OCRPlugin interface.

    Raises:
        ValueError: If plugin name is unknown.

    Example:
        >>> plugin = get_plugin("easyocr", device="cpu", languages=["en"])
        >>> plugin.load("")
        >>> result = plugin.infer(image)
    """
    try:
        path = _PLUGIN_REGISTRY[name]
    except KeyError:
        raise ValueError(f"Unknown plugin: {name}")

    # Lazy import: resolve module path and class name
    module_path, class_name = path.split(":")
    module = import_module(module_path)
    plugin_cls = getattr(module, class_name)

    # Instantiate plugin with provided kwargs
    # Cast to OCRPlugin since registry only contains OCRPlugin subclasses
    return cast(OCRPlugin, plugin_cls(**kwargs))


def list_plugins() -> list[str]:
    """List all registered plugin names.

    Returns:
        Sorted list of plugin names.

    Example:
        >>> plugins = list_plugins()
        >>> print(plugins)
        ['easyocr']
    """
    return sorted(_PLUGIN_REGISTRY.keys())
