"""EasyOCR plugin implementation for EZRA."""

from __future__ import annotations

from typing import Any

from ezra.plugins.easyocr_adapter import EasyOCRAdapter
from ezra.plugins.interface import OCRPlugin


def transform_easyocr_output(raw_output: list[Any]) -> list[dict[str, Any]]:
    """Transform raw EasyOCR output to EZRA canonical detection format.

    This is a pure function that converts EasyOCR's raw output format
    (list of (bbox_points, text, confidence) tuples) into EZRA's canonical
    detection format (list of dicts with text, confidence, bbox).

    Args:
        raw_output: Raw EasyOCR output as list of (bbox_points, text, confidence) tuples.
            bbox_points is a list of 4 points: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]

    Returns:
        List of detection dictionaries, each containing:
        - "text": str
        - "confidence": float
        - "bbox": list[float] [x1, y1, x2, y2] (axis-aligned bounding box)
    """
    detections = []
    for bbox_points, text, confidence in raw_output:
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

    return detections


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
        self.device = device
        self.languages = languages or ["en"]
        self._adapter = EasyOCRAdapter(device=device, languages=self.languages)

    def load(self, artifact_path: str) -> None:
        """Load EasyOCR model.

        Args:
            artifact_path: Path is ignored for EasyOCR (it loads models automatically).
                This parameter exists for interface compatibility.

        Raises:
            RuntimeError: If model loading fails.
        """
        self._adapter.load()

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
        raw_output = self._adapter.infer(image)
        detections = transform_easyocr_output(raw_output)
        return {"detections": detections}

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
