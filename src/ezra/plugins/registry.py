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
    "tesseract": "ezra.plugins.tesseract_plugin:TesseractPlugin",
}


def _validate_registry_entry_format(path: str, plugin_name: str) -> None:
    """Validate that a registry entry has the correct format.

    Args:
        path: Registry entry path string.
        plugin_name: Plugin name for error messages.

    Raises:
        TypeError: If path format is invalid (not a string or missing ':').
    """
    if not isinstance(path, str):
        raise TypeError(
            f"Registry entry for '{plugin_name}' must be a string, got {type(path).__name__}"
        )
    if path.count(":") != 1:
        raise TypeError(
            f"Registry entry for '{plugin_name}' must contain exactly one ':', got '{path}'"
        )


def _validate_plugin_instance(obj: object) -> None:
    """Validate that an object implements the OCRPlugin interface.

    Args:
        obj: Object to validate.

    Raises:
        TypeError: If object is not an OCRPlugin instance or missing required methods.
    """
    if not isinstance(obj, OCRPlugin):
        raise TypeError(
            f"Plugin instance must be a subclass of OCRPlugin, got {type(obj).__name__}"
        )

    # Verify required methods exist
    required_methods = ["load", "infer", "describe_capabilities"]
    for method_name in required_methods:
        if not hasattr(obj, method_name):
            raise TypeError(f"Plugin instance missing required method: {method_name}")


def get_plugin(name: str, **kwargs: Any) -> OCRPlugin:
    """Get a plugin instance by name.

    Args:
        name: Plugin name (e.g., "easyocr").
        **kwargs: Plugin-specific initialization arguments.

    Returns:
        Plugin instance implementing OCRPlugin interface.

    Raises:
        ValueError: If plugin name is unknown.
        TypeError: If registry entry is malformed or plugin instance violates contract.

    Example:
        >>> plugin = get_plugin("easyocr", device="cpu", languages=["en"])
        >>> plugin.load("")
        >>> result = plugin.infer(image)
    """
    try:
        path = _PLUGIN_REGISTRY[name]
    except KeyError:
        raise ValueError(f"Unknown plugin: {name}")

    # Validate registry entry format
    _validate_registry_entry_format(path, name)

    # Lazy import: resolve module path and class name
    module_path, class_name = path.split(":")
    module = import_module(module_path)
    plugin_cls = getattr(module, class_name)

    # Instantiate plugin with provided kwargs
    instance = plugin_cls(**kwargs)

    # Validate instance implements OCRPlugin contract
    _validate_plugin_instance(instance)

    return cast(OCRPlugin, instance)


def get_plugin_from_config(config: dict[str, Any]) -> OCRPlugin:
    """Get a plugin instance from a configuration dictionary.

    Args:
        config: Configuration dictionary with:
            - "name": str (required) - Plugin name
            - "kwargs": dict (optional) - Plugin-specific initialization arguments

    Returns:
        Plugin instance implementing OCRPlugin interface.

    Raises:
        ValueError: If "name" key is missing or plugin name is unknown.
        TypeError: If registry entry is malformed or plugin instance violates contract.

    Example:
        >>> config = {"name": "easyocr", "kwargs": {"device": "cpu", "languages": ["en"]}}
        >>> plugin = get_plugin_from_config(config)
        >>> plugin.load("")
        >>> result = plugin.infer(image)
    """
    if "name" not in config:
        raise ValueError("Configuration must contain 'name' key")

    name = config["name"]
    kwargs = config.get("kwargs", {})

    return get_plugin(name, **kwargs)


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


def validate_registry() -> None:
    """Validate that all registry entries are correctly formatted and resolvable.

    This function:
    - Validates registry entry format (must be "module.path:ClassName")
    - Confirms module path resolves
    - Confirms class exists in module
    - Confirms class is a subclass of OCRPlugin

    Does NOT instantiate plugins (avoids loading heavy ML models).

    Raises:
        TypeError: If registry entry format is invalid.
        RuntimeError: If module import fails or class is not a subclass of OCRPlugin.

    Example:
        >>> validate_registry()  # Raises if registry is malformed
    """
    for plugin_name, path in _PLUGIN_REGISTRY.items():
        # Validate format
        _validate_registry_entry_format(path, plugin_name)

        # Resolve module and class
        try:
            module_path, class_name = path.split(":")
            module = import_module(module_path)
        except ImportError as e:
            raise RuntimeError(
                f"Failed to import module '{module_path}' for plugin '{plugin_name}': {e}"
            ) from e

        if not hasattr(module, class_name):
            raise RuntimeError(
                f"Class '{class_name}' not found in module '{module_path}' "
                f"for plugin '{plugin_name}'"
            )

        plugin_cls = getattr(module, class_name)

        # Verify it's a subclass of OCRPlugin (without instantiating)
        if not issubclass(plugin_cls, OCRPlugin):
            raise RuntimeError(
                f"Class '{class_name}' in module '{module_path}' is not a subclass of OCRPlugin "
                f"for plugin '{plugin_name}'"
            )
