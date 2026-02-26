"""Tests for zone schema validation."""

import pytest

from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema
from ezra.zones.validator import (
    validate_bbox,
    validate_registry,
    validate_zone_schema,
)


def test_validate_bbox_valid():
    """Test validation of valid bbox."""
    bbox = BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.9, y_max=0.8)
    validate_bbox(bbox)  # Should not raise


def test_validate_bbox_invalid_x_min():
    """Test validation fails for x_min < 0."""
    bbox = BBoxNorm(x_min=-0.1, y_min=0.2, x_max=0.9, y_max=0.8)
    with pytest.raises(ValueError, match="Invalid bbox x coordinates"):
        validate_bbox(bbox)


def test_validate_bbox_invalid_x_max():
    """Test validation fails for x_max > 1."""
    bbox = BBoxNorm(x_min=0.1, y_min=0.2, x_max=1.1, y_max=0.8)
    with pytest.raises(ValueError, match="Invalid bbox x coordinates"):
        validate_bbox(bbox)


def test_validate_bbox_invalid_x_min_equals_x_max():
    """Test validation fails for x_min == x_max."""
    bbox = BBoxNorm(x_min=0.5, y_min=0.2, x_max=0.5, y_max=0.8)
    with pytest.raises(ValueError, match="Invalid bbox x coordinates"):
        validate_bbox(bbox)


def test_validate_bbox_invalid_x_min_greater_than_x_max():
    """Test validation fails for x_min > x_max."""
    bbox = BBoxNorm(x_min=0.9, y_min=0.2, x_max=0.1, y_max=0.8)
    with pytest.raises(ValueError, match="Invalid bbox x coordinates"):
        validate_bbox(bbox)


def test_validate_bbox_invalid_y_min():
    """Test validation fails for y_min < 0."""
    bbox = BBoxNorm(x_min=0.1, y_min=-0.1, x_max=0.9, y_max=0.8)
    with pytest.raises(ValueError, match="Invalid bbox y coordinates"):
        validate_bbox(bbox)


def test_validate_bbox_invalid_y_max():
    """Test validation fails for y_max > 1."""
    bbox = BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.9, y_max=1.1)
    with pytest.raises(ValueError, match="Invalid bbox y coordinates"):
        validate_bbox(bbox)


def test_validate_zone_schema_valid():
    """Test validation of valid zone schema."""
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)
    schema = ZoneSchema(
        id="test_zone",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    validate_zone_schema(schema)  # Should not raise


def test_validate_zone_schema_empty_id():
    """Test validation fails for empty id."""
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)
    schema = ZoneSchema(
        id="",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    with pytest.raises(ValueError, match="Zone id must be a non-empty string"):
        validate_zone_schema(schema)


def test_validate_zone_schema_empty_kind():
    """Test validation fails for empty kind."""
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)
    schema = ZoneSchema(
        id="test_zone",
        kind="",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    with pytest.raises(ValueError, match="Zone kind must be a non-empty string"):
        validate_zone_schema(schema)


def test_validate_zone_schema_negative_channel():
    """Test validation fails for negative channel_index."""
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)
    schema = ZoneSchema(
        id="test_zone",
        kind="ocr",
        channel_index=-1,
        bbox_norm=bbox,
        persistence=persistence,
    )
    with pytest.raises(ValueError, match="Channel index must be a non-negative integer"):
        validate_zone_schema(schema)


def test_validate_registry_valid():
    """Test validation of valid registry."""
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
    validate_registry([schema1, schema2])  # Should not raise


def test_validate_registry_duplicate_ids():
    """Test validation fails for duplicate zone IDs."""
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)
    schema1 = ZoneSchema(
        id="duplicate",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    schema2 = ZoneSchema(
        id="duplicate",
        kind="detection",
        channel_index=1,
        bbox_norm=bbox,
        persistence=persistence,
    )
    with pytest.raises(ValueError, match="Duplicate zone id"):
        validate_registry([schema1, schema2])


def test_validate_registry_duplicate_channels():
    """Test validation fails for duplicate channel indices."""
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
        channel_index=0,  # Duplicate!
        bbox_norm=bbox2,
        persistence=persistence,
    )
    with pytest.raises(ValueError, match="Duplicate channel index"):
        validate_registry([schema1, schema2])


def test_validate_registry_skip_unique_checks():
    """Test that unique checks can be skipped."""
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)
    schema1 = ZoneSchema(
        id="duplicate",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    schema2 = ZoneSchema(
        id="duplicate",
        kind="detection",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    # Should not raise when checks are disabled
    validate_registry([schema1, schema2], check_unique_ids=False, check_unique_channels=False)

