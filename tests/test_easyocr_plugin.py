"""Tests for EasyOCR plugin implementation."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from ezra.plugins.easyocr_plugin import EasyOCRPlugin
from tests.utils.ml_available import has_easyocr

EASYOCR_REQUIRED = pytest.mark.skipif(
    not has_easyocr(),
    reason="EasyOCR not installed in CI environment",
)


def test_easyocr_plugin_import_without_easyocr() -> None:
    """Test that plugin module can be imported without EasyOCR installed."""
    # This should not raise ImportError
    # But instantiating should raise if easyocr is None
    # We need to mock the import to test this
    import importlib

    from ezra.plugins import easyocr_plugin  # noqa: F401

    with patch.dict(sys.modules, {"easyocr": None}):
        # Force reload to pick up the mocked module
        import ezra.plugins.easyocr_adapter as adapter_module
        import ezra.plugins.easyocr_plugin as plugin_module

        importlib.reload(adapter_module)
        importlib.reload(plugin_module)
        # Now try to instantiate - should raise ImportError
        with pytest.raises(ImportError, match="EasyOCR is not installed"):
            plugin_module.EasyOCRPlugin()


@EASYOCR_REQUIRED
@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_plugin_initialization(mock_easyocr: MagicMock) -> None:
    """Test plugin initialization with mocked EasyOCR."""
    plugin = EasyOCRPlugin(device="cpu", languages=["en"])
    assert plugin.device == "cpu"
    assert plugin.languages == ["en"]
    assert not plugin._adapter._loaded


@EASYOCR_REQUIRED
@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_plugin_load(mock_easyocr: MagicMock) -> None:
    """Test plugin load method."""
    mock_reader = MagicMock()
    mock_easyocr.Reader.return_value = mock_reader

    plugin = EasyOCRPlugin(device="cpu", languages=["en"])
    plugin.load("")

    mock_easyocr.Reader.assert_called_once_with(
        ["en"],
        gpu=False,
        verbose=False,
    )
    assert plugin._adapter._loaded
    assert plugin._adapter._reader is mock_reader


@EASYOCR_REQUIRED
@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_plugin_infer(mock_easyocr: MagicMock) -> None:
    """Test plugin infer method."""
    # Mock EasyOCR readtext output
    # Format: [(bbox_points, text, confidence), ...]
    # bbox_points is list of 4 points: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    mock_result = [
        ([[10, 10], [50, 10], [50, 30], [10, 30]], "Hello", 0.95),
        ([[60, 10], [100, 10], [100, 30], [60, 30]], "World", 0.92),
    ]

    mock_reader = MagicMock()
    mock_reader.readtext.return_value = mock_result
    mock_easyocr.Reader.return_value = mock_reader

    plugin = EasyOCRPlugin(device="cpu", languages=["en"])
    plugin.load("")

    # Create mock image
    mock_image = MagicMock()
    result = plugin.infer(mock_image)

    assert "detections" in result
    assert len(result["detections"]) == 2

    # Check first detection
    det0 = result["detections"][0]
    assert det0["text"] == "Hello"
    assert det0["confidence"] == 0.95
    assert det0["bbox"] == [10.0, 10.0, 50.0, 30.0]

    # Check second detection
    det1 = result["detections"][1]
    assert det1["text"] == "World"
    assert det1["confidence"] == 0.92
    assert det1["bbox"] == [60.0, 10.0, 100.0, 30.0]

    mock_reader.readtext.assert_called_once_with(mock_image)


@EASYOCR_REQUIRED
@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_plugin_infer_not_loaded(mock_easyocr: MagicMock) -> None:
    """Test that infer raises RuntimeError if model not loaded."""
    plugin = EasyOCRPlugin(device="cpu", languages=["en"])

    with pytest.raises(RuntimeError, match="Model not loaded"):
        plugin.infer(MagicMock())


@EASYOCR_REQUIRED
@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_plugin_describe_capabilities(mock_easyocr: MagicMock) -> None:
    """Test plugin describe_capabilities method."""
    plugin = EasyOCRPlugin(device="cpu", languages=["en", "fr"])

    caps = plugin.describe_capabilities()

    assert caps["version"] == "1.7.2"
    assert caps["plugin_name"] == "EasyOCRPlugin"
    assert "supported_formats" in caps
    assert caps["input_requirements"]["device"] == "cpu"
    assert caps["input_requirements"]["languages"] == ["en", "fr"]
    assert "output_schema" in caps


@EASYOCR_REQUIRED
@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_plugin_load_failure(mock_easyocr: MagicMock) -> None:
    """Test that load raises RuntimeError on failure."""
    mock_easyocr.Reader.side_effect = Exception("Model load failed")

    plugin = EasyOCRPlugin(device="cpu", languages=["en"])

    with pytest.raises(RuntimeError, match="Failed to load EasyOCR model"):
        plugin.load("")
