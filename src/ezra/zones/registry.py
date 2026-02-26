"""Zone schema registry with freeze semantics.

This module provides an immutable registry for zone schemas with:
- Freeze-after-init pattern
- Deterministic export (sorted by channel_index, id)
- Validation on registration
"""

from __future__ import annotations

from ezra.zones.schema import ZoneSchema
from ezra.zones.validator import validate_registry


class ZoneRegistry:
    """Immutable registry for zone schemas.

    Registry starts empty and can be populated via register().
    After freeze(), no further registrations are allowed.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._zones: dict[str, ZoneSchema] = {}
        self._frozen: bool = False

    def register(self, schema: ZoneSchema) -> None:
        """Register a zone schema.

        Args:
            schema: Zone schema to register.

        Raises:
            ValueError: If registry is frozen, schema is invalid, or ID/channel conflicts exist.
        """
        if self._frozen:
            raise ValueError("Cannot register zone: registry is frozen")

        # Validate schema individually
        from ezra.zones.validator import validate_zone_schema

        validate_zone_schema(schema)

        # Check for duplicate ID
        if schema.id in self._zones:
            raise ValueError(f"Duplicate zone id: {schema.id}")

        # Check for duplicate channel index
        existing_with_channel = [
            z for z in self._zones.values() if z.channel_index == schema.channel_index
        ]
        if existing_with_channel:
            existing_ids = [z.id for z in existing_with_channel]
            raise ValueError(
                f"Duplicate channel index {schema.channel_index} "
                f"(already used by zones: {existing_ids})"
            )

        self._zones[schema.id] = schema

    def freeze(self) -> None:
        """Freeze registry (no further registrations allowed)."""
        # Validate entire registry before freezing
        validate_registry(list(self._zones.values()))
        self._frozen = True

    def get(self, zone_id: str) -> ZoneSchema | None:
        """Get zone schema by ID.

        Args:
            zone_id: Zone identifier.

        Returns:
            Zone schema if found, None otherwise.
        """
        return self._zones.get(zone_id)

    def list_all(self) -> list[ZoneSchema]:
        """Return all zones sorted by (channel_index, id).

        Returns:
            List of zone schemas in deterministic order.
        """
        return sorted(self._zones.values(), key=lambda z: (z.channel_index, z.id))

    def export_to_dict(self) -> dict[str, Any]:
        """Export registry to deterministic dict for JSON serialization.

        Returns:
            Dictionary with structure:
            {
                "zones": [
                    {zone_schema_dict},
                    ...
                ]
            }
            Zones are sorted by (channel_index, id).
        """
        from typing import Any

        zones = self.list_all()
        return {
            "zones": [zone.to_dict() for zone in zones],
        }

    @property
    def is_frozen(self) -> bool:
        """Check if registry is frozen."""
        return self._frozen

    @property
    def count(self) -> int:
        """Get number of registered zones."""
        return len(self._zones)

