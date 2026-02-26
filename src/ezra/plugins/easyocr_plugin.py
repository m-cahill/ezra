"""EasyOCR plugin implementation for EZRA."""

from __future__ import annotations

from typing import Any

try:
    import easyocr
except ImportError:
    easyocr = None

from ezra.plugins.interface import OCRPlugin


class EasyOCRPlugin(OCRPlugin):
    """EasyOCR-backed OCR plugin implementation.

    This plugin wraps EasyOCR's Reader class and implements the OCRPlugin interface.
    It defaults to CPU mode and requires EasyOCR to be installed as an optional dependency.
    """

    def __init__(self, device: str = "cpu", languages: list[str] | None = None) -> None:
        """Initialize EasyOCR plugin.

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
        self.languages = languages or ["en"]
        self._reader: Any = None
        self._loaded = False

    def load(self, artifact_path: str) -> None:
        """Load EasyOCR model.

        Args:
            artifact_path: Path is ignored for EasyOCR (it loads models automatically).
                This parameter exists for interface compatibility.

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

    def infer(self, image: Any) -> dict[str, Any]:
        """Run OCR inference on an input image.

        Args:
            image: Input image (numpy array, PIL Image, or file path).

        Returns:
            Dictionary containing detection results with deterministic schema:
            {
                "detections": [
                    {
                        "text": str,
                        "confidence": float,
                        "bbox": [x1, y1, x2, y2] (float coordinates)
                    },
                    ...
                ]
            }

        Raises:
            RuntimeError: If model is not loaded or inference fails.
        """
        if not self._loaded or self._reader is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        try:
            # EasyOCR returns list of (bbox, text, confidence) tuples
            # bbox is list of 4 points: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            results = self._reader.readtext(image)

            detections = []
            for bbox_points, text, confidence in results:
                # Convert 4-point bbox to axis-aligned [x1, y1, x2, y2]
                x_coords = [point[0] for point in bbox_points]
                y_coords = [point[1] for point in bbox_points]
                x1 = min(x_coords)
                y1 = min(y_coords)
                x2 = max(x_coords)
                y2 = max(y_coords)

                detections.append(
                    {
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    }
                )

            return {"detections": detections}
        except Exception as e:
            raise RuntimeError(f"EasyOCR inference failed: {e}") from e

    def describe_capabilities(self) -> dict[str, Any]:
        """Describe plugin capabilities and metadata.

        Returns:
            Dictionary containing:
            - version: Plugin version string
            - supported_formats: List of supported image formats
            - input_requirements: Required input dimensions/normalization
            - output_schema: Description of output structure
        """
        return {
            "version": "1.7.2",
            "plugin_name": "EasyOCRPlugin",
            "supported_formats": ["numpy array", "PIL Image", "file path"],
            "input_requirements": {
                "device": self.device,
                "languages": self.languages,
            },
            "output_schema": {
                "detections": [
                    {
                        "text": "str",
                        "confidence": "float (0.0-1.0)",
                        "bbox": "list[float] [x1, y1, x2, y2]",
                    }
                ],
            },
        }
