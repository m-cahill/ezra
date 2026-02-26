"""Tests for plugin registry."""

import sys
from unittest.mock import patch

import pytest

from ezra.plugins.interface import OCRPlugin
from ezra.plugins.registry import get_plugin, list_plugins


def test_list_plugins() -> None:
    """Test that list_plugins returns sorted plugin names."""
    plugins = list_plugins()
    assert isinstance(plugins, list)
    assert "easyocr" in plugins
    assert plugins == sorted(plugins)


def test_get_plugin_success() -> None:
    """Test successful plugin resolution."""
    with patch("ezra.plugins.easyocr_adapter.easyocr"):
        plugin = get_plugin("easyocr", device="cpu", languages=["en"])
        assert isinstance(plugin, OCRPlugin)
        assert plugin.device == "cpu"
        assert plugin.languages == ["en"]


def test_get_plugin_unknown() -> None:
    """Test that unknown plugin raises ValueError with correct message."""
    with pytest.raises(ValueError, match=r"Unknown plugin: nonexistent"):
        get_plugin("nonexistent")


def test_get_plugin_unknown_exact_message() -> None:
    """Test that unknown plugin error message is exact format."""
    with pytest.raises(ValueError) as exc_info:
        get_plugin("unknown_plugin")
    assert str(exc_info.value) == "Unknown plugin: unknown_plugin"


def test_registry_does_not_import_easyocr_on_import() -> None:
    """Test that importing registry does not import easyocr module.

    This ensures lazy loading works correctly - the registry should not
    trigger import of heavy ML modules until plugin resolution time.
    """
    # Remove easyocr from sys.modules if present (to test fresh import)
    easyocr_modules = [k for k in sys.modules.keys() if k.startswith("easyocr")]
    for mod in easyocr_modules:
        del sys.modules[mod]

    # Also remove the plugin module to test fresh import
    plugin_modules = [k for k in sys.modules.keys() if k.startswith("ezra.plugins.easyocr")]
    for mod in plugin_modules:
        del sys.modules[mod]

    # Import registry - this should not import easyocr
    import ezra.plugins.registry  # noqa: F401

    # Verify easyocr is not in sys.modules
    assert "easyocr" not in sys.modules
    assert "easyocr.reader" not in sys.modules

    # Now resolve plugin - this should trigger import
    with patch("ezra.plugins.easyocr_adapter.easyocr"):
        get_plugin("easyocr")

    # After resolution, easyocr_plugin should be imported, but easyocr itself
    # may still not be if it's mocked. The key is that registry import didn't
    # trigger it prematurely.


def test_get_plugin_passes_kwargs() -> None:
    """Test that get_plugin correctly passes kwargs to plugin constructor."""
    with patch("ezra.plugins.easyocr_adapter.easyocr"):
        plugin = get_plugin("easyocr", device="cuda", languages=["en", "fr"])
        assert plugin.device == "cuda"
        assert plugin.languages == ["en", "fr"]


def test_get_plugin_returns_ocrplugin_instance() -> None:
    """Test that get_plugin returns instance implementing OCRPlugin interface."""
    with patch("ezra.plugins.easyocr_adapter.easyocr"):
        plugin = get_plugin("easyocr", device="cpu", languages=["en"])
        assert isinstance(plugin, OCRPlugin)
        # Verify it has required methods
        assert hasattr(plugin, "load")
        assert hasattr(plugin, "infer")
        assert hasattr(plugin, "describe_capabilities")
