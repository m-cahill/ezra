"""Tests for zone schema JSON export."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ezra.zones.export import export_zone_schema_json
from ezra.zones.registry import ZoneRegistry
from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema


def test_export_empty_registry():
    """Test exporting empty registry."""
    registry = ZoneRegistry()
    registry.freeze()

    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "zone_schema.json"
        export_zone_schema_json(registry, output_path)

        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert data == {"zones": []}


def test_export_registry_with_zones():
    """Test exporting registry with zones."""
    registry = ZoneRegistry()
    bbox1 = BBoxNorm(x_min=0.0, y_min=0.0, x_max=0.5, y_max=0.5)
    bbox2 = BBoxNorm(x_min=0.5, y_min=0.5, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)

    schema1 = ZoneSchema(
        id="zone1",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox1,
        persistence=persistence,
    )
    schema2 = ZoneSchema(
        id="zone2",
        kind="detection",
        channel_index=1,
        bbox_norm=bbox2,
        persistence=persistence,
    )

    registry.register(schema1)
    registry.register(schema2)
    registry.freeze()

    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "zone_schema.json"
        export_zone_schema_json(registry, output_path)

        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert "zones" in data
        assert len(data["zones"]) == 2
        assert data["zones"][0]["id"] == "zone1"
        assert data["zones"][1]["id"] == "zone2"


def test_export_deterministic():
    """Test that export produces deterministic output."""
    registry = ZoneRegistry()
    bbox = BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.9, y_max=0.8)
    persistence = ZonePersistence(sticky=True)
    schema = ZoneSchema(
        id="zone1",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    registry.register(schema)
    registry.freeze()

    with TemporaryDirectory() as tmpdir:
        output_path1 = Path(tmpdir) / "zone_schema1.json"
        output_path2 = Path(tmpdir) / "zone_schema2.json"

        export_zone_schema_json(registry, output_path1)
        export_zone_schema_json(registry, output_path2)

        # Files should be byte-identical
        assert output_path1.read_bytes() == output_path2.read_bytes()

