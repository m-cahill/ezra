"""Zone schema type definitions.

This module defines the core data structures for the Universal Zone Schema:
- BBoxNorm: Normalized bounding box (0-1 range)
- ZonePersistence: Persistence semantics (sticky flag)
- ZoneSchema: Complete zone definition with channel mapping
"""

from __future__ import annotations

from dataclasses import dataclass


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
