"""Smoke tests to verify basic import and instantiation."""

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
        return {"detections": []}

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


def test_engine_process_image() -> None:
    """Test that engine can process an image."""
    plugin = MockPlugin()
    engine = EzraEngine(plugin)

    # Mock image object
    class MockImage:
        width = 100
        height = 200
        channels = 3

    image = MockImage()
    result = engine.process_image(image)

    assert result == {"detections": []}


def test_engine_process_image_with_epb_emission(tmp_path) -> None:
    """Test that engine can emit EPB bundle when requested."""
    plugin = MockPlugin()
    engine = EzraEngine(plugin)

    class MockImage:
        width = 100
        height = 200
        channels = 3

    image = MockImage()
    epb_dir = tmp_path / "epb"

    engine.process_image(image, emit_epb=True, epb_output_dir=epb_dir)

    # Verify EPB bundle was written
    assert (epb_dir / "manifest.json").exists()
    assert (epb_dir / "detections.json").exists()
    assert (epb_dir / "state.json").exists()
    assert (epb_dir / "hashes.json").exists()


def test_engine_process_image_epb_requires_dir() -> None:
    """Test that emit_epb=True requires epb_output_dir."""
    plugin = MockPlugin()
    engine = EzraEngine(plugin)

    class MockImage:
        width = 100
        height = 200

    image = MockImage()

    with pytest.raises(ValueError, match="epb_output_dir must be provided"):
        engine.process_image(image, emit_epb=True, epb_output_dir=None)
