"""Type definitions for EZRA core data structures."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ImageInput:
    """Input image data for perception processing."""

    data: bytes
    width: int
    height: int
    channels: int = 3
    metadata: dict[str, Any] | None = None


@dataclass
class OCRResult:
    """OCR detection result."""

    text: str
    confidence: float
    bbox: list[float]  # [x1, y1, x2, y2]
    metadata: dict[str, Any] | None = None


@dataclass
class ModelArtifactMetadata:
    """Metadata for a model artifact."""

    artifact_path: str
    version: str
    input_size: tuple[int, int]
    normalization: dict[str, float] | None = None
    preprocessing_config: dict[str, Any] | None = None
    postprocessing_config: dict[str, Any] | None = None
