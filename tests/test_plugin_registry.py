"""Tests for plugin registry."""

import sys
from typing import Any
from unittest.mock import patch

import pytest

from ezra.plugins.interface import OCRPlugin
from ezra.plugins.registry import (
    get_plugin,
    get_plugin_from_config,
    list_plugins,
    validate_registry,
)


def test_list_plugins() -> None:
    """Test that list_plugins returns sorted plugin names."""
    plugins = list_plugins()
    assert isinstance(plugins, list)
    assert "easyocr" in plugins
    assert "tesseract" in plugins
    assert plugins == sorted(plugins)
    # Verify deterministic ordering: easyocr first, tesseract second
    assert plugins == ["easyocr", "tesseract"]


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


def test_get_plugin_from_config_success() -> None:
    """Test successful plugin resolution from configuration dictionary."""
    with patch("ezra.plugins.easyocr_adapter.easyocr"):
        config = {"name": "easyocr", "kwargs": {"device": "cpu", "languages": ["en"]}}
        plugin = get_plugin_from_config(config)
        assert isinstance(plugin, OCRPlugin)
        assert plugin.device == "cpu"
        assert plugin.languages == ["en"]


def test_get_plugin_from_config_missing_name() -> None:
    """Test that missing 'name' key raises ValueError."""
    config = {"kwargs": {"device": "cpu"}}
    with pytest.raises(ValueError, match=r"Configuration must contain 'name' key"):
        get_plugin_from_config(config)


def test_get_plugin_from_config_unknown() -> None:
    """Test that unknown plugin name in config raises ValueError."""
    config = {"name": "nonexistent", "kwargs": {}}
    with pytest.raises(ValueError, match=r"Unknown plugin: nonexistent"):
        get_plugin_from_config(config)


def test_registry_validation_success() -> None:
    """Test that validate_registry passes for valid registry."""
    with patch("ezra.plugins.easyocr_adapter.easyocr"):
        # Should not raise
        validate_registry()


def test_registry_validation_malformed_entry() -> None:
    """Test that validate_registry raises TypeError for malformed registry entry."""
    from ezra.plugins import registry

    # Temporarily corrupt registry entry
    original = registry._PLUGIN_REGISTRY["easyocr"]
    try:
        # Test missing colon
        registry._PLUGIN_REGISTRY["easyocr"] = "ezra.plugins.easyocr_plugin"
        with pytest.raises(TypeError, match=r"must contain exactly one ':'"):
            validate_registry()

        # Test multiple colons
        registry._PLUGIN_REGISTRY["easyocr"] = "ezra.plugins.easyocr_plugin:EasyOCRPlugin:Extra"
        with pytest.raises(TypeError, match=r"must contain exactly one ':'"):
            validate_registry()

        # Test non-string entry
        registry._PLUGIN_REGISTRY["easyocr"] = 123
        with pytest.raises(TypeError, match=r"must be a string"):
            validate_registry()
    finally:
        # Restore original
        registry._PLUGIN_REGISTRY["easyocr"] = original


def test_registry_validation_import_error() -> None:
    """Test that validate_registry raises RuntimeError for import failures."""
    from unittest.mock import patch

    from ezra.plugins import registry

    original = registry._PLUGIN_REGISTRY["easyocr"]
    try:
        # Test ImportError handling
        with patch(
            "ezra.plugins.registry.import_module", side_effect=ImportError("No module named 'fake'")
        ):
            registry._PLUGIN_REGISTRY["easyocr"] = "fake.module:SomeClass"
            with pytest.raises(RuntimeError, match=r"Failed to import module"):
                validate_registry()
    finally:
        registry._PLUGIN_REGISTRY["easyocr"] = original


def test_registry_validation_missing_class() -> None:
    """Test that validate_registry raises RuntimeError for missing class."""
    from unittest.mock import MagicMock, patch

    from ezra.plugins import registry

    original = registry._PLUGIN_REGISTRY["easyocr"]
    try:
        # Create a mock module without the class
        fake_module = MagicMock()
        delattr(fake_module, "NonExistentClass")  # Ensure it doesn't exist

        with patch("ezra.plugins.registry.import_module", return_value=fake_module):
            registry._PLUGIN_REGISTRY["easyocr"] = "fake.module:NonExistentClass"
            with pytest.raises(RuntimeError, match=r"Class 'NonExistentClass' not found"):
                validate_registry()
    finally:
        registry._PLUGIN_REGISTRY["easyocr"] = original


def test_registry_validation_non_subclass() -> None:
    """Test that validate_registry raises RuntimeError for non-OCRPlugin subclass."""
    from unittest.mock import MagicMock, patch

    from ezra.plugins import registry

    original = registry._PLUGIN_REGISTRY["easyocr"]
    try:
        # Create a mock module with a class that's not a subclass of OCRPlugin
        fake_module = MagicMock()
        fake_module.NonPluginClass = type("NonPluginClass", (), {})

        with patch("ezra.plugins.registry.import_module", return_value=fake_module):
            registry._PLUGIN_REGISTRY["easyocr"] = "fake.module:NonPluginClass"
            with pytest.raises(RuntimeError, match=r"is not a subclass of OCRPlugin"):
                validate_registry()
    finally:
        registry._PLUGIN_REGISTRY["easyocr"] = original


def test_plugin_instance_type_violation() -> None:
    """Test that non-OCRPlugin instances raise TypeError."""
    from ezra.plugins.registry import _validate_plugin_instance

    # Create a class that is not a subclass of OCRPlugin
    class FakePlugin:
        def load(self, artifact_path: str) -> None:
            pass

        def infer(self, image: Any) -> dict[str, Any]:
            return {}

        def describe_capabilities(self) -> dict[str, Any]:
            return {}

    fake_instance = FakePlugin()

    # Test that validation raises TypeError for non-OCRPlugin instance
    with pytest.raises(TypeError, match=r"must be a subclass of OCRPlugin"):
        _validate_plugin_instance(fake_instance)

    # Test that validation raises TypeError for missing method
    # Create an object that passes isinstance check but is missing methods
    # This tests the secondary validation path
    from unittest.mock import MagicMock

    # Create a mock that claims to be an OCRPlugin but is missing methods
    incomplete_mock = MagicMock(spec=OCRPlugin)
    # Remove one required method to test method validation
    delattr(incomplete_mock, "describe_capabilities")

    with pytest.raises(TypeError, match=r"missing required method: describe_capabilities"):
        _validate_plugin_instance(incomplete_mock)


def test_kwargs_forwarding_behavior() -> None:
    """Test that kwargs are forwarded correctly through get_plugin_from_config."""
    with patch("ezra.plugins.easyocr_adapter.easyocr"):
        # Test with kwargs
        config = {"name": "easyocr", "kwargs": {"device": "cuda", "languages": ["fr", "de"]}}
        plugin = get_plugin_from_config(config)
        assert plugin.device == "cuda"
        assert plugin.languages == ["fr", "de"]

        # Test without kwargs (should use defaults)
        config_no_kwargs = {"name": "easyocr"}
        plugin2 = get_plugin_from_config(config_no_kwargs)
        assert plugin2.device == "cpu"  # EasyOCRPlugin default
        assert plugin2.languages == ["en"]  # EasyOCRPlugin default


def test_tesseract_plugin_loads() -> None:
    """Test that Tesseract plugin can be instantiated and implements OCRPlugin interface."""
    plugin = get_plugin("tesseract", languages=["eng", "fra"])
    assert isinstance(plugin, OCRPlugin)
    assert plugin.languages == ["eng", "fra"]
    # Verify it has required methods
    assert hasattr(plugin, "load")
    assert hasattr(plugin, "infer")
    assert hasattr(plugin, "describe_capabilities")
    # Verify stub behavior
    plugin.load("")
    result = plugin.infer(None)
    assert result == {"detections": []}
    capabilities = plugin.describe_capabilities()
    assert capabilities["version"] == "stub-0.0.1"
    assert capabilities["plugin_name"] == "TesseractPlugin"


def test_tesseract_plugin_default_languages() -> None:
    """Test that Tesseract plugin uses default languages when none provided."""
    plugin = get_plugin("tesseract")
    assert plugin.languages == ["eng"]


def test_registry_snapshot_updated() -> None:
    """Test that registry snapshot includes tesseract with deterministic ordering."""
    plugins = list_plugins()
    # Verify both plugins present
    assert "easyocr" in plugins
    assert "tesseract" in plugins
    # Verify deterministic ordering: easyocr first, tesseract second
    assert plugins == ["easyocr", "tesseract"]
    # Verify sorted order maintained
    assert plugins == sorted(plugins)


def test_tesseract_does_not_import_easyocr() -> None:
    """Test that importing/instantiating Tesseract plugin does not import EasyOCR module.

    This ensures lazy loading works correctly and there is no cross-plugin coupling.
    """
    # Remove easyocr from sys.modules if present (to test fresh import)
    easyocr_modules = [k for k in sys.modules.keys() if k.startswith("easyocr")]
    for mod in easyocr_modules:
        del sys.modules[mod]

    # Also remove the plugin modules to test fresh import
    plugin_modules = [k for k in sys.modules.keys() if k.startswith("ezra.plugins.easyocr")]
    for mod in plugin_modules:
        del sys.modules[mod]

    # Import registry - this should not import easyocr
    import ezra.plugins.registry  # noqa: F401

    # Verify easyocr is not in sys.modules
    assert "easyocr" not in sys.modules
    assert "easyocr.reader" not in sys.modules

    # Now instantiate tesseract plugin - this should NOT trigger easyocr import
    plugin = get_plugin("tesseract")
    assert isinstance(plugin, OCRPlugin)

    # Verify easyocr is still not in sys.modules after tesseract instantiation
    assert "easyocr" not in sys.modules
    assert "easyocr.reader" not in sys.modules
    assert "ezra.plugins.easyocr_plugin" not in sys.modules
    assert "ezra.plugins.easyocr_adapter" not in sys.modules


def test_registry_validation_includes_tesseract() -> None:
    """Test that validate_registry passes with tesseract plugin registered."""
    with patch("ezra.plugins.easyocr_adapter.easyocr"):
        # Should not raise - validates both easyocr and tesseract
        validate_registry()
