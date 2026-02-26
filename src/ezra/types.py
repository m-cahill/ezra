"""Type definitions for EZRA core data structures."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ImageInput:
    """Input image data for perception processing."""

    data: bytes
    width: int
    height: int
    channels: int = 3
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class OCRResult:
    """OCR detection result."""

    text: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ModelArtifactMetadata:
    """Metadata for a model artifact."""

    artifact_path: str
    version: str
    input_size: tuple[int, int]
    normalization: Optional[Dict[str, float]] = None
    preprocessing_config: Optional[Dict[str, Any]] = None
    postprocessing_config: Optional[Dict[str, Any]] = None
