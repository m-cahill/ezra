"""Zone schema definitions for EZRA.

This module provides the Universal Zone Schema contract for mapping
visual zones to tensor channels with deterministic serialization.

Public API:
- BBoxNorm, ZonePersistence, ZoneSchema: Core schema types
- ZoneRegistry: Immutable registry with freeze semantics
- export_zone_schema_json: JSON export for contract locking
"""

from ezra.zones.export import export_zone_schema_json
from ezra.zones.registry import ZoneRegistry
from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema

__all__ = [
    "BBoxNorm",
    "ZonePersistence",
    "ZoneSchema",
    "ZoneRegistry",
    "export_zone_schema_json",
]
