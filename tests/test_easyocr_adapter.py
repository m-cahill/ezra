"""Tests for EasyOCR adapter implementation."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from ezra.plugins.easyocr_adapter import EasyOCRAdapter


def test_easyocr_adapter_import_without_easyocr() -> None:
    """Test that adapter module can be imported without EasyOCR installed."""
    import importlib

    from ezra.plugins import easyocr_adapter  # noqa: F401

    with patch.dict(sys.modules, {"easyocr": None}):
        # Force reload to pick up the mocked module
        import ezra.plugins.easyocr_adapter as adapter_module

        importlib.reload(adapter_module)
        # Now try to instantiate - should raise ImportError
        with pytest.raises(ImportError, match="EasyOCR is not installed"):
            adapter_module.EasyOCRAdapter()


@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_adapter_initialization(mock_easyocr: MagicMock) -> None:
    """Test adapter initialization with mocked EasyOCR."""
    adapter = EasyOCRAdapter(device="cpu", languages=["en"])
    assert adapter.device == "cpu"
    assert adapter.languages == ["en"]
    assert not adapter._loaded


@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_adapter_initialization_defaults(mock_easyocr: MagicMock) -> None:
    """Test adapter initialization with default parameters."""
    adapter = EasyOCRAdapter()
    assert adapter.device == "cpu"
    assert adapter.languages == ["en"]
    assert not adapter._loaded


@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_adapter_initialization_cuda(mock_easyocr: MagicMock) -> None:
    """Test adapter initialization with CUDA device."""
    adapter = EasyOCRAdapter(device="cuda", languages=["en", "fr"])
    assert adapter.device == "cuda"
    assert adapter.languages == ["en", "fr"]
    assert not adapter._loaded


@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_adapter_load(mock_easyocr: MagicMock) -> None:
    """Test adapter load method."""
    mock_reader = MagicMock()
    mock_easyocr.Reader.return_value = mock_reader

    adapter = EasyOCRAdapter(device="cpu", languages=["en"])
    adapter.load()

    mock_easyocr.Reader.assert_called_once_with(
        ["en"],
        gpu=False,
        verbose=False,
    )
    assert adapter._loaded
    assert adapter._reader is mock_reader


@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_adapter_load_cuda(mock_easyocr: MagicMock) -> None:
    """Test adapter load method with CUDA device."""
    mock_reader = MagicMock()
    mock_easyocr.Reader.return_value = mock_reader

    adapter = EasyOCRAdapter(device="cuda", languages=["en"])
    adapter.load()

    mock_easyocr.Reader.assert_called_once_with(
        ["en"],
        gpu=True,
        verbose=False,
    )
    assert adapter._loaded


@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_adapter_load_idempotent(mock_easyocr: MagicMock) -> None:
    """Test that adapter load is idempotent."""
    mock_reader = MagicMock()
    mock_easyocr.Reader.return_value = mock_reader

    adapter = EasyOCRAdapter(device="cpu", languages=["en"])
    adapter.load()
    adapter.load()  # Second call should not create new reader

    mock_easyocr.Reader.assert_called_once()
    assert adapter._loaded


@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_adapter_load_failure(mock_easyocr: MagicMock) -> None:
    """Test that load raises RuntimeError on failure."""
    mock_easyocr.Reader.side_effect = Exception("Model load failed")

    adapter = EasyOCRAdapter(device="cpu", languages=["en"])

    with pytest.raises(RuntimeError, match="Failed to load EasyOCR model"):
        adapter.load()


@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_adapter_infer(mock_easyocr: MagicMock) -> None:
    """Test adapter infer method returns raw EasyOCR output."""
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

    adapter = EasyOCRAdapter(device="cpu", languages=["en"])
    adapter.load()

    # Create mock image
    mock_image = MagicMock()
    result = adapter.infer(mock_image)

    # Adapter should return raw EasyOCR output unchanged
    assert result == mock_result
    assert len(result) == 2
    assert result[0] == ([[10, 10], [50, 10], [50, 30], [10, 30]], "Hello", 0.95)
    assert result[1] == ([[60, 10], [100, 10], [100, 30], [60, 30]], "World", 0.92)

    mock_reader.readtext.assert_called_once_with(mock_image)


@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_adapter_infer_not_loaded(mock_easyocr: MagicMock) -> None:
    """Test that infer raises RuntimeError if model not loaded."""
    adapter = EasyOCRAdapter(device="cpu", languages=["en"])

    with pytest.raises(RuntimeError, match="Model not loaded"):
        adapter.infer(MagicMock())


@patch("ezra.plugins.easyocr_adapter.easyocr")
def test_easyocr_adapter_infer_failure(mock_easyocr: MagicMock) -> None:
    """Test that infer raises RuntimeError on inference failure."""
    mock_reader = MagicMock()
    mock_reader.readtext.side_effect = Exception("Inference failed")
    mock_easyocr.Reader.return_value = mock_reader

    adapter = EasyOCRAdapter(device="cpu", languages=["en"])
    adapter.load()

    with pytest.raises(RuntimeError, match="EasyOCR inference failed"):
        adapter.infer(MagicMock())

