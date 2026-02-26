"""EasyOCR adapter for isolating direct EasyOCR framework interactions."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

try:
    import easyocr
except ImportError:
    easyocr = None


class EasyOCRAdapter:
    """Adapter for EasyOCR Reader lifecycle and inference.

    This adapter encapsulates all direct EasyOCR interactions, isolating
    third-party ML framework calls from the plugin orchestration layer.

    Responsibilities:
    - Reader initialization and lifecycle management
    - Raw inference calls to EasyOCR Reader
    - Returning raw EasyOCR output unchanged

    The adapter does NOT perform any output transformation or normalization.
    """

    def __init__(self, device: str = "cpu", languages: Sequence[str] | None = None) -> None:
        """Initialize EasyOCR adapter.

        Args:
            device: Device to use for inference ('cpu' or 'cuda'). Defaults to 'cpu'.
            languages: List of language codes to support. Defaults to ['en'].

        Raises:
            ImportError: If easyocr is not installed.
        """
        if easyocr is None:
            msg = "EasyOCR is not installed. Install it with: pip install -e '.[easyocr]'"
            raise ImportError(msg)

        self.device = device
        self.languages = list(languages) if languages else ["en"]
        self._reader: Any = None
        self._loaded = False

    def load(self) -> None:
        """Load EasyOCR model.

        Initializes the EasyOCR Reader, which automatically downloads and loads
        models on first use.

        Raises:
            RuntimeError: If model loading fails.
        """
        if self._loaded:
            return

        try:
            # EasyOCR automatically downloads and loads models on first use
            # We initialize the reader here to trigger model loading
            self._reader = easyocr.Reader(
                self.languages,
                gpu=(self.device == "cuda"),
                verbose=False,
            )
            self._loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load EasyOCR model: {e}") from e

    def infer(self, image: Any) -> list[Any]:
        """Run raw EasyOCR inference on an input image.

        Returns the raw EasyOCR output format unchanged:
        list of (bbox_points, text, confidence) tuples where:
        - bbox_points: list of 4 points [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        - text: str
        - confidence: float

        Args:
            image: Input image (numpy array, PIL Image, or file path).

        Returns:
            Raw EasyOCR output as list of tuples.

        Raises:
            RuntimeError: If model is not loaded or inference fails.
        """
        if not self._loaded or self._reader is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        try:
            # EasyOCR returns list of (bbox, text, confidence) tuples
            # bbox is list of 4 points: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            results = self._reader.readtext(image)
            return results  # type: ignore[no-any-return]
        except Exception as e:
            raise RuntimeError(f"EasyOCR inference failed: {e}") from e
