"""Tesseract plugin stub implementation for EZRA.

This is a minimal stub plugin that implements the OCRPlugin interface
without invoking an actual Tesseract binary. It is used to prove that
the plugin registry supports multi-backend extension without coupling.
"""

from __future__ import annotations

from typing import Any

from ezra.plugins.interface import OCRPlugin


class TesseractPlugin(OCRPlugin):
    """Tesseract-backed OCR plugin stub implementation.

    This plugin is a stub that implements the OCRPlugin interface without
    actually invoking a Tesseract binary. It returns empty detections to
    maintain interface compatibility while proving registry extensibility.

    This is a structural hardening step (M06) to demonstrate multi-backend
    plugin support without introducing runtime dependencies or behavior drift.
    """

    def __init__(self, languages: list[str] | None = None) -> None:
        """Initialize Tesseract plugin stub.

        Args:
            languages: List of language codes to support. Defaults to ['eng'].
        """
        self.languages = languages or ["eng"]

    def load(self, artifact_path: str) -> None:
        """Load Tesseract model (stub - no-op).

        Args:
            artifact_path: Path is ignored for stub implementation.
                This parameter exists for interface compatibility.

        This is a no-op to keep the plugin instantiable and maintain
        interface contract without special-case branching.
        """
        return None

    def infer(self, image: Any) -> dict[str, Any]:
        """Run OCR inference on an input image (stub - returns empty detections).

        Args:
            image: Input image (format ignored for stub).

        Returns:
            Dictionary containing empty detection results with deterministic schema:
            {
                "detections": []
            }

        This stub returns empty detections to maintain interface compatibility
        without making semantic claims or introducing false confidence.
        """
        return {"detections": []}

    def describe_capabilities(self) -> dict[str, Any]:
        """Describe plugin capabilities and metadata.

        Returns:
            Dictionary containing:
            - version: Plugin version string ("stub-0.0.1" to indicate non-production)
            - plugin_name: "TesseractPlugin"
            - supported_formats: List of supported image formats
            - input_requirements: Required input dimensions/normalization
            - output_schema: Description of output structure
        """
        return {
            "version": "stub-0.0.1",
            "plugin_name": "TesseractPlugin",
            "supported_formats": ["numpy array", "PIL Image", "file path"],
            "input_requirements": {
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
