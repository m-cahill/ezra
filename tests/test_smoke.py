"""Smoke tests to verify basic import and instantiation."""

from unittest.mock import Mock

import pytest

from ezra.core.engine import EzraEngine
from ezra.plugins.interface import OCRPlugin


class MockPlugin(OCRPlugin):
    """Mock plugin for testing."""

    def load(self, artifact_path: str) -> None:
        """Mock load implementation."""
        pass

    def infer(self, image) -> dict:
        """Mock infer implementation."""
        return {"text": "", "confidence": 0.0, "bbox": []}

    def describe_capabilities(self) -> dict:
        """Mock capabilities description."""
        return {"version": "0.0.0", "supported_formats": []}


def test_import_ezra() -> None:
    """Test that ezra package can be imported."""
    from ezra import __version__  # noqa: F401
    from ezra.core.engine import EzraEngine  # noqa: F401
    from ezra.plugins.interface import OCRPlugin  # noqa: F401
    from ezra.types import ImageInput, OCRResult  # noqa: F401


def test_engine_instantiation() -> None:
    """Test that engine can be instantiated with a mock plugin."""
    plugin = MockPlugin()
    engine = EzraEngine(plugin)
    assert engine.plugin is plugin


def test_plugin_interface() -> None:
    """Test that mock plugin implements required interface."""
    plugin = MockPlugin()
    assert hasattr(plugin, "load")
    assert hasattr(plugin, "infer")
    assert hasattr(plugin, "describe_capabilities")
