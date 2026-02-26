"""Zone schema type definitions.

This module defines the core data structures for the Universal Zone Schema:
- BBoxNorm: Normalized bounding box (0-1 range)
- ZonePersistence: Persistence semantics (sticky flag)
- ZoneSchema: Complete zone definition with channel mapping
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BBoxNorm:
    """Normalized bounding box in 0-1 coordinate space.

    Coordinates are normalized to image dimensions:
    - x_min, y_min: top-left corner (inclusive)
    - x_max, y_max: bottom-right corner (exclusive)

    Validation: 0 <= x_min < x_max <= 1 and 0 <= y_min < y_max <= 1
    """

    x_min: float
    y_min: float
    x_max: float
    y_max: float


@dataclass(frozen=True)
class ZonePersistence:
    """Zone persistence semantics.

    Controls whether zone state persists across frames or is ephemeral.
    """

    sticky: bool


@dataclass(frozen=True)
class ZoneSchema:
    """Complete zone schema definition.

    Maps a visual zone to a tensor channel with persistence semantics.
    This is the core contract for zone-based perception.

    Attributes:
        id: Unique zone identifier (non-empty string)
        kind: Zone kind/category (free-form, non-empty string)
        channel_index: Tensor channel assignment (int >= 0, globally unique)
        bbox_norm: Normalized bounding box (0-1 range)
        persistence: Persistence semantics
    """

    id: str
    kind: str
    channel_index: int
    bbox_norm: BBoxNorm
    persistence: ZonePersistence

    def to_dict(self) -> dict[str, Any]:
        """Serialize zone schema to deterministic dictionary.

        Returns:
            Dictionary with stable key ordering and 6 decimal place float precision.
            Keys: ["id", "kind", "channel_index", "bbox_norm", "persistence"]
        """
        return {
            "id": self.id,
            "kind": self.kind,
            "channel_index": self.channel_index,
            "bbox_norm": {
                "x_min": round(self.bbox_norm.x_min, 6),
                "y_min": round(self.bbox_norm.y_min, 6),
                "x_max": round(self.bbox_norm.x_max, 6),
                "y_max": round(self.bbox_norm.y_max, 6),
            },
            "persistence": {
                "sticky": self.persistence.sticky,
            },
        }
