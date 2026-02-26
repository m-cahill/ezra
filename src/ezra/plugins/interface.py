"""Abstract plugin interface for OCR and perception backends."""

from abc import ABC, abstractmethod
from typing import Any


class OCRPlugin(ABC):
    """Abstract base class for OCR plugin implementations."""

    @abstractmethod
    def load(self, artifact_path: str) -> None:
        """Load a model artifact from the given path.

        Args:
            artifact_path: Path to the model artifact file.

        Raises:
            FileNotFoundError: If artifact_path does not exist.
            ValueError: If artifact is malformed or incompatible.
        """
        ...

    @abstractmethod
    def infer(self, image: Any) -> dict[str, Any]:
        """Run inference on an input image.

        Args:
            image: Input image (format depends on plugin implementation).

        Returns:
            Dictionary containing detection results with deterministic schema.

        Raises:
            RuntimeError: If model is not loaded or inference fails.
        """
        ...

    @abstractmethod
    def describe_capabilities(self) -> dict[str, Any]:
        """Describe plugin capabilities and metadata.

        Returns:
            Dictionary containing:
            - version: Plugin version string
            - supported_formats: List of supported image formats
            - input_requirements: Required input dimensions/normalization
            - output_schema: Description of output structure
        """
        ...
