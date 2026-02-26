"""Zone schema definitions for EZRA.

This module provides the Universal Zone Schema contract for mapping
visual zones to tensor channels with deterministic serialization.
"""

from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema

__all__ = ["BBoxNorm", "ZonePersistence", "ZoneSchema"]
