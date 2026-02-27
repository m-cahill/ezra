# Zone Architecture

**Schema Version:** 1.0.0  
**Last Updated:** M21

---

## Overview

The **Universal Zone Mapping Schema (UZMS)** is EZRA's contract for mapping visual zones (pixel regions) to tensor channels with persistence semantics. Zones enable zone-scoped state projection, channel-based tensor organization, and deterministic zone-aware EPB emission.

---

## Core Concepts

### Zone Schema

A `ZoneSchema` defines:

- **`id`**: Unique zone identifier (non-empty string)
- **`kind`**: Zone category (free-form string, e.g., "ocr", "detection", "segmentation")
- **`channel_index`**: Tensor channel assignment (int >= 0, globally unique across registry)
- **`bbox_norm`**: Normalized bounding box (0-1 coordinate space)
- **`persistence`**: Persistence semantics (`sticky: bool`)

All zone schema types are **frozen dataclasses** (immutable after construction).

### Zone Registry

The `ZoneRegistry` provides:

- **Freeze-after-init pattern**: Registry starts empty, can be populated via `register()`, then frozen via `freeze()` to prevent further mutations
- **Deterministic export**: Zones are sorted by `(channel_index, id)` for stable ordering
- **Validation**: Unique channel indices, unique zone IDs, valid bbox ranges

### Schema Version

The schema version is declared as a constant:

```python
from ezra.zones.serialize import SCHEMA_VERSION
# SCHEMA_VERSION = "1.0.0"
```

The version is immutable unless explicitly bumped in a milestone.

---

## Invariants

The zone schema contract enforces four mandatory invariants:

### I1 — Deterministic Zone Serialization

Identical zone definitions must produce byte-identical JSON.

**Verification:**
- Snapshot test (`tests/contracts/test_zone_schema_snapshot.py`)
- Hash comparison test (`tests/test_zone_contract.py::test_i1_byte_identical_serialization`)

### I2 — Stable Zone Ordering

Zone list ordering must be stable and explicit (sorted by `channel_index`, then `id`).

**Verification:**
- Order test (`tests/test_zone_contract.py::test_i2_stable_ordering_by_channel_then_id`)
- Multiple export test (`tests/test_zone_contract.py::test_i2_ordering_stable_across_exports`)

### I3 — Plugin Isolation

ML plugins must not modify:
- Zone `id`
- `bbox` coordinates
- `channel_index`
- `persistence` flags

**Verification:**
- Frozen dataclass enforcement (`tests/test_zone_contract.py::test_i3_zone_schema_immutable`)
- Registry freeze enforcement (`tests/test_zone_contract.py::test_i3_registry_frozen_prevents_mutation`)

### I4 — Schema Version Stability

Schema version must be declared and immutable unless explicitly bumped.

**Verification:**
- Version constant test (`tests/test_zone_contract.py::test_i4_schema_version_constant`)
- Schema file metadata test (`tests/test_zone_contract.py::test_i4_schema_version_in_schema_file`)

---

## Schema Validation

Zone data is validated against a formal JSON Schema:

- **Schema file**: `src/ezra/zones/schema_v1.json`
- **Validation function**: `ezra.zones.serialize.validate_zone_data_against_schema()`
- **CI enforcement**: Zone schema validation step in CI workflow

The JSON Schema defines:
- Required fields and types
- Bbox coordinate constraints (0-1 range)
- Channel index constraints (>= 0)
- String constraints (non-empty, no whitespace)

---

## Serialization

### Canonical Serialization

The `serialize.py` module provides:

- **`serialize_zone_registry()`**: Compact, byte-identical JSON (for hashing/determinism)
- **`serialize_zone_registry_pretty()`**: Pretty-printed JSON (for human-readable output)

Both functions:
- Sort keys at all levels
- Use deterministic zone ordering (via `registry.export_to_dict()`)
- Preserve 6 decimal place float precision (via `ZoneSchema.to_dict()`)

### Export

The `export.py` module handles file I/O and delegates to `serialize.py` for canonical formatting.

---

## Snapshot Testing

Golden snapshot tests ensure deterministic serialization:

- **Snapshot file**: `tests/contracts/snapshots/zone_schema_snapshot.json`
- **Test**: `tests/contracts/test_zone_schema_snapshot.py::test_zone_schema_snapshot_matches`

The snapshot is committed and must match exactly. Any change requires explicit regeneration and audit justification.

---

## Usage Example

```python
from ezra.zones.registry import ZoneRegistry
from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema
from ezra.zones.export import export_zone_schema_json
from pathlib import Path

# Create registry
registry = ZoneRegistry()

# Define zone
bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=0.5, y_max=0.5)
persistence = ZonePersistence(sticky=True)
zone = ZoneSchema(
    id="ocr_zone",
    kind="ocr",
    channel_index=0,
    bbox_norm=bbox,
    persistence=persistence,
)

# Register and freeze
registry.register(zone)
registry.freeze()

# Export to JSON
export_zone_schema_json(registry, Path("zones.json"))
```

---

## Related Documentation

- **EPB Zones Extension**: `docs/specs/epb_v1/EPB_V1_SPEC.md` (zones.json emission)
- **Zone Projection**: `src/ezra/zones/projector.py` (zone-scoped state projection)
- **Zone Validator**: `src/ezra/zones/validator.py` (validation rules)

---

## Contract Stability

The zone schema contract is **frozen** as of M21:

- Schema version: `1.0.0` (immutable)
- JSON Schema: `schema_v1.json` (immutable)
- Deterministic serialization rules (immutable)
- Invariant tests (regression guards)

Any change to the schema structure, version, or serialization rules requires:
- A new milestone
- A version bump (e.g., `1.0.0` → `2.0.0`)
- Explicit audit justification
- Updated snapshot (if applicable)

