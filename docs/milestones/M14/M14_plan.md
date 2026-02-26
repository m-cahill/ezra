# M14_plan

## Milestone: Zone-Scoped State Projection (Behavior-Preserving Runtime Extension)

**Project:** EZRA
**Baseline Tag:** `v0.0.14-m13`
**Mode:** Behavior-Preserving Extension
**Posture:** Artifact-Surface → Runtime-Scoped Projection
**Target Tag:** `v0.0.15-m14`

---

# 1. Intent / Target

M12 locked the ZoneSchema contract.
M13 wired zones into EPB as an optional artifact extension.

M14's purpose is to:

> Introduce deterministic, zone-scoped state projection inside the runtime without altering inference behavior.

Currently:

* Runtime produces OCR/detection state.
* EPB optionally includes structural zones metadata.
* Zones are not yet usable inside runtime logic.

M14 introduces:

* A **ZoneProjector** utility that maps perception outputs into zone-scoped state partitions.
* A deterministic projection mechanism.
* Zero change to inference outputs.
* Zero change to EPB schema.
* Zero change to plugin registry.

This milestone moves zones from "artifact metadata" → "runtime-scoped projection primitive."

---

# 2. Scope Boundaries

## In Scope

* `src/ezra/zones/projector.py`
* Deterministic projection of detections into zones
* Pure functional projection (no mutation)
* Tests covering:

  * Determinism
  * Boundary conditions
  * Overlapping bbox rules
  * Empty registry behavior
* Architecture boundary test updates (if needed)

## Out of Scope

* No automatic zone detection
* No ML changes
* No EPB schema changes
* No inference logic modifications
* No performance optimizations
* No schema version bump
* No runtime default behavior changes

Projection must be opt-in.

---

# 3. Invariants (Must Not Change)

From M13 audit :

1. CI truthfulness preserved
2. Determinism gate remains green
3. EPB canonicalization unchanged
4. Hash algorithm unchanged
5. Backward compatibility preserved
6. Coverage ≥ baseline
7. Adapter boundary preserved
8. Zone precision contract preserved (6dp)

### New Invariant (M14)

9. If projection is used, projected state must be deterministic across N ≥ 3 runs.

---

# 4. Verification Plan

## Unit Tests

* `test_zone_projector_basic_assignment`
* `test_zone_projector_empty_registry`
* `test_zone_projector_overlapping_zone_error`
* `test_zone_projector_deterministic_order`
* `test_zone_projector_bbox_edge_precision`
* `test_zone_projector_unfrozen_registry_error`

## Contract Test

* Snapshot test:

  * Given fixed detections + fixed zones → deterministic projected state JSON

## Determinism Gate

Extend `check_determinism.py`:

* Emit:

  * EPB baseline
  * EPB + zones
  * EPB + zones + projection
* Verify byte-identical across 3 runs

---

# 5. Implementation Steps (Ordered & Reversible)

### Step 1 — Introduce ZoneProjector (Pure Function)

File: `src/ezra/zones/projector.py`

```python
def project_state_to_zones(
    detections: list[OCRResult],
    registry: ZoneRegistry,
    image_width: int,
    image_height: int,
) -> dict[str, list[OCRResult]]:
```

Rules:

* Registry must be frozen
* Each detection assigned to zones whose bbox contains its centroid
* Deterministic ordering (sorted by zone_id, then detection order)
* No mutation of original detections

Commit.

---

### Step 2 — Deterministic Canonical Projection Serializer

Add:

```python
def to_projection_canonical_json(...)
```

* 6dp precision (zone contract)
* Stable key ordering
* No reliance on EPB canonicalization

Commit.

---

### Step 3 — Validation Rules

Add checks:

* If registry not frozen → ValueError
* If detection matches multiple zones → ValueError (strict mode)
* Channel uniqueness not modified
* Bounding box normalization respected

Commit.

---

### Step 4 — Tests

Add comprehensive projector tests.

Ensure:

* 100% coverage of new module
* All existing tests pass unchanged

Commit.

---

### Step 5 — Determinism Script Extension

Extend `check_determinism.py`:

* Include projection-enabled emission
* Verify identical across 3 runs

Commit.

---

### Step 6 — Architecture Boundary Test

Ensure:

* `zones.projector` does not import epb internals
* `core/` still does not import zones internals directly

Commit.

---

# 6. Risk & Rollback Plan

### Primary Risk

Projection assignment ambiguity (detections falling into multiple zones).

Mitigation:

* Strict error mode
* Explicit test coverage

### Rollback Strategy

* Entire milestone is additive
* Revert commits between:
  `v0.0.14-m13` → `v0.0.15-m14`
* No schema migrations required

---

# 7. Deliverables

* `projector.py`
* Deterministic projection serializer
* 10–15 new tests
* Snapshot file
* Determinism gate updated
* `M14_run1.md`
* `M14_summary.md`
* `M14_audit.md`
* Tag `v0.0.15-m14`

---

# 8. Success Criteria

M14 is complete when:

* All existing tests pass unchanged
* All new tests pass
* Coverage ≥ baseline
* Determinism gate green
* No EPB schema changes
* No runtime behavior changes unless projection explicitly used
* Adapter boundary intact

---

# 9. Strategic Position After M14

After M14, EZRA will have:

* Deterministic artifact surface (M08–M13)
* Locked zone schema (M12)
* Zone-aware EPB extension (M13)
* Deterministic runtime zone projection (M14)

At that point, zones become:

> A structural perception primitive usable both in artifact bundles and runtime state partitioning.

This sets up future milestones for:

* Zone-aware state synthesis
* Zone-aware delta generation
* Cross-zone reasoning adapters for RediAI v3

---

If you approve, the next instruction to Cursor should be:

> Create branch `m14-zone-projection` and implement M14_plan in strict ordered steps. Stop if CI fails.
