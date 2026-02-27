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

---

## Schema Evolution Policy

**Enforcement:** M22+ (CI-enforced schema governance)

The zone schema evolution is governed by strict rules to prevent silent drift and ensure explicit versioning.

### Version-Schema Coupling

**Rule:** Schema changes and version bumps are **bidirectionally coupled**:

- If `schema_v1.json` changes → `SCHEMA_VERSION` must change
- If `SCHEMA_VERSION` changes → `schema_v1.json` must change

**Enforcement:**
- `tests/test_zone_schema_version_enforcement.py` validates coupling
- CI fails if coupling is violated

### Snapshot Baseline

**Rule:** `schema_v1.json` must match the committed snapshot baseline.

**Baseline file:** `docs/baselines/zone_schema_snapshot.json`

**Enforcement:**
- `tests/test_zone_schema_diff.py` compares current schema against snapshot
- CI fails if schema drifts from snapshot without explicit update

**Snapshot update workflow:**
1. Schema change is made in `schema_v1.json`
2. Schema is canonically re-serialized (sorted keys, stable formatting)
3. Snapshot is updated to match new schema
4. Both changes committed in same milestone

### Version Bump Rules

**Semantic versioning:** Follow `MAJOR.MINOR.PATCH` semantics:

- **MAJOR** (`1.0.0` → `2.0.0`): Breaking changes
  - Field removal
  - Constraint tightening (e.g., `minLength: 1` → `minLength: 5`)
  - Type changes (e.g., `string` → `integer`)
  - Required field additions

- **MINOR** (`1.0.0` → `1.1.0`): Backward-compatible additions
  - New optional fields
  - New enum values
  - Constraint relaxation (e.g., `minLength: 5` → `minLength: 1`)

- **PATCH** (`1.0.0` → `1.0.1`): Documentation/description-only changes
  - Description text updates
  - Example updates
  - No structural changes

### Prohibited Changes

The following changes are **prohibited** without explicit milestone justification:

- **Silent field removal** (must bump MAJOR version)
- **Constraint tightening without version bump** (must bump MAJOR version)
- **Schema drift without snapshot update** (must update snapshot)
- **Version bump without schema change** (must change schema)
- **Schema change without version bump** (must bump version)

### Required Milestone Posture

Any schema change milestone must:

1. **Declare intent** in milestone plan
2. **Document rationale** for change
3. **Update snapshot** if schema structure changes
4. **Bump version** if schema structure changes
5. **Update tests** if contract changes
6. **Pass audit** with explicit justification

### Backward Compatibility

**Policy:** Prefer backward-compatible changes (MINOR bumps) over breaking changes (MAJOR bumps).

**Guidelines:**
- Add optional fields rather than required fields
- Relax constraints rather than tighten them
- Extend enums rather than restrict them
- Deprecate fields before removing them (future: deprecation support)

### Deprecation Rules

**Current status:** Deprecation support is not yet implemented (future milestone).

**Future deprecation workflow:**
1. Mark field as deprecated in schema (metadata)
2. Bump MINOR version
3. Document deprecation timeline
4. Remove in next MAJOR version

---

## Zone Registry Integrity Model

**Enforcement:** M23+ (CI-enforced registry integrity)

The zone registry runtime state is governed by deterministic snapshot and hash verification to ensure registry integrity across runs.

### Deterministic Registry Contract

**Rule:** Given identical zone definitions, registry snapshot must be byte-identical across runs.

**Enforcement:**
- `tests/test_zone_registry_snapshot.py` validates snapshot matching
- `docs/baselines/zone_registry_snapshot.json` provides committed baseline
- CI fails if registry state drifts from snapshot

**Snapshot baseline:**
- Generated from test fixture with 5 zones registered out-of-order
- Validates ordering determinism (zones sorted by `channel_index`, then `id`)
- Committed as golden file for drift detection

### Freeze Lifecycle

**Rule:** After `freeze()`, registry becomes immutable:

- No new zones may be registered
- No channel reassignment allowed
- Freeze is idempotent (multiple freezes are no-ops)

**Enforcement:**
- `tests/test_zone_registry_integrity.py` validates freeze enforcement
- Post-freeze registration attempts raise `ZoneSchemaError`
- Hash remains stable after freeze

### Snapshot Workflow

**Baseline generation:**
1. Test fixture creates registry with zones registered out-of-order
2. Registry is frozen
3. Canonical JSON is generated via `canonical_registry_json()`
4. Snapshot is written to `docs/baselines/zone_registry_snapshot.json`

**Snapshot validation:**
1. Test fixture recreates registry (same zones, same order)
2. Canonical JSON is generated
3. JSON is compared byte-identical to committed snapshot
4. Test fails if mismatch (requires explicit baseline update)

### Hash Semantics

**Rule:** Registry hash is deterministic and stable:

- Identical registries produce identical hashes
- Hash is independent of insertion order
- Hash remains stable after freeze
- Hash is computed over canonical JSON (SHA256)

**Functions:**
- `canonical_registry_json(registry) -> str`: Canonical JSON string
- `registry_hash(registry) -> str`: SHA256 hash (64-char hex)

**Enforcement:**
- `tests/test_zone_registry_snapshot.py` validates hash determinism
- Hash stability verified across multiple calls
- Hash independence from insertion order verified

### Channel Stability

**Rule:** Channel indices must be:

- Unique (no duplicate channel indices)
- Deterministic (same zones → same channel assignments)
- Ordered (zones sorted by `channel_index`, then `id`)

**Enforcement:**
- `tests/test_zone_registry_integrity.py` validates channel uniqueness
- Registration ordering determinism verified
- Channel index ordering preserved regardless of insertion order

### Registry Integrity CI Gate

**CI step:** "Validate registry integrity"

**Tests run:**
- `tests/test_zone_registry_snapshot.py` (snapshot match, hash determinism)
- `tests/test_zone_registry_integrity.py` (freeze enforcement, channel uniqueness, ordering)

**CI summary section:**
```
## Registry Integrity
- Snapshot match: PASS
- Hash determinism: PASS
- Freeze enforcement: PASS
```

**Failure modes:**
- Snapshot mismatch → requires explicit baseline update
- Hash non-determinism → indicates serialization bug
- Freeze violation → indicates registry mutation bug

---

## Related Documentation

