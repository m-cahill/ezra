"""Type definitions for EZRA core data structures."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True)
class ImageInput:
    """Input image data for perception processing.

    This dataclass is frozen to enforce immutability at runtime.
    The metadata field, if provided, is wrapped in MappingProxyType
    to prevent mutation of the top-level dictionary.
    """

    data: bytes
    width: int
    height: int
    channels: int = 3
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Coerce metadata dict to MappingProxyType for immutability."""
        if self.metadata is not None:
            # Use object.__setattr__ to set attributes on frozen dataclass
            object.__setattr__(self, "metadata", MappingProxyType(self.metadata))


@dataclass(frozen=True)
class OCRResult:
    """OCR detection result.

    This dataclass is frozen to enforce immutability at runtime.
    The bbox field is stored as a tuple (immutable), and the metadata
    field, if provided, is wrapped in MappingProxyType to prevent
    mutation of the top-level dictionary.
    """

    text: str
    confidence: float
    bbox: tuple[float, float, float, float]  # [x1, y1, x2, y2]
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Coerce bbox to tuple and metadata dict to MappingProxyType."""
        # Coerce bbox list to tuple if needed
        if isinstance(self.bbox, list):
            object.__setattr__(self, "bbox", tuple(self.bbox))
        # Wrap metadata dict in MappingProxyType if provided
        if self.metadata is not None:
            object.__setattr__(self, "metadata", MappingProxyType(self.metadata))


@dataclass(frozen=True)
class ModelArtifactMetadata:
    """Metadata for a model artifact.

    This dataclass is frozen to enforce immutability at runtime.
    Dictionary fields (normalization, preprocessing_config, postprocessing_config)
    are wrapped in MappingProxyType to prevent mutation of the top-level containers.
    """

    artifact_path: str
    version: str
    input_size: tuple[int, int]
    normalization: dict[str, float] | None = None
    preprocessing_config: dict[str, Any] | None = None
    postprocessing_config: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Coerce dict fields to MappingProxyType for immutability."""
        if self.normalization is not None:
            object.__setattr__(self, "normalization", MappingProxyType(self.normalization))
        if self.preprocessing_config is not None:
            object.__setattr__(
                self, "preprocessing_config", MappingProxyType(self.preprocessing_config)
            )
        if self.postprocessing_config is not None:
            object.__setattr__(
                self, "postprocessing_config", MappingProxyType(self.postprocessing_config)
            )
