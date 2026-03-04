# M20 Plan

**Milestone:** M20 — Deterministic Runtime Hardening & Contract Surface Sealing  
**Status:** In Progress  
**Baseline:** `v0.0.20-m19` (tag)  
**Working Branch:** `m20-runtime-contract-seal`  
**Posture:** Behavior-preserving unless explicitly locked  
**Mode:** Runtime Hardening (not feature expansion)

---

## Milestone Objective

After M19, CI and supply chain posture are hardened. What remains soft is **runtime contract sealing**:

* EPB v1.0.0 is frozen.
* Public surface freeze exists.
* Determinism gate exists.

But we do **not yet enforce structural immutability at the object level** inside the runtime boundary.

M20 introduces:

> Deterministic runtime structural sealing and immutability guarantees.

This strengthens EZRA as an artifact-boundary engine.

---

## Problem Statement

Currently:

* EPB bundles are deterministic.
* Public surface is frozen.
* Schema hash is frozen.

But:

* Internal data structures (e.g., `ImageInput`, `OCRResult`, `ModelArtifactMetadata`) are mutable.
* EPB bundle dictionaries are mutable after construction.
* No runtime enforcement prevents accidental post-construction mutation.
* No structural hash assertion exists at object instantiation time.
* No contract-level immutability test suite.

For enterprise-grade reproducibility, runtime structures must be sealed.

---

## Scope Definition

### In Scope

* Introduce frozen dataclass structures for:

  * `ImageInput` (in `types.py`)
  * `OCRResult` (in `types.py`) — convert `bbox: list[float]` → `tuple[float, float, float, float]`
  * `ModelArtifactMetadata` (in `types.py`)
* Seal EPB bundle dictionaries with `MappingProxyType` before returning from builder/export functions
* Add `__post_init__` methods for coercion (list→tuple, dict→MappingProxyType) using `object.__setattr__`
* Introduce runtime structural hash assertion helper (internal-only, in existing module)
* Add immutability tests (mutation guard tests)
* Add mutation attempt negative tests (expect TypeError)
* Add contract sealing test harness
* Add structural hash cross-validation tests

### Out of Scope

* No schema changes
* No EPB format changes
* No new fields
* No plugin changes
* No behavior changes (except immutability enforcement)
* No performance optimization
* No refactor unrelated to sealing
* No new public modules/types (keep helpers internal)

---

## Implementation Steps (Small, Ordered, Reversible)

### Step 1 — Convert Core Types to Frozen Dataclasses

* Convert `ImageInput` to `@dataclass(frozen=True)`
* Convert `OCRResult` to `@dataclass(frozen=True)` with `bbox: tuple[float, float, float, float]`
* Convert `ModelArtifactMetadata` to `@dataclass(frozen=True)`
* Add `__post_init__` methods to coerce:
  * `OCRResult.bbox`: list → tuple
  * `OCRResult.metadata`: dict → `MappingProxyType` (if not None)
  * `ImageInput.metadata`: dict → `MappingProxyType` (if not None)
  * `ModelArtifactMetadata` nested dicts: wrap top-level only

Use `object.__setattr__` for frozen dataclass attribute assignment.

**Files:** `src/ezra/types.py`

---

### Step 2 — Seal EPB Bundle Dictionaries

* Wrap EPB bundle dict in `MappingProxyType` before returning from `build_epb_bundle()`
* Ensure nested dicts in bundle are also wrapped (top-level only, not recursive)
* Verify no mutation is possible after construction

**Files:** `src/ezra/epb/builder.py`

---

### Step 3 — Structural Hash Assertion Utility

Add internal utility function (in existing module, e.g., `epb/canonical.py` or `epb/hasher.py`):

```python
def assert_structural_hash(obj: Any) -> str:
    """Compute structural hash of an object for immutability verification.
    
    Canonicalizes, serializes, and hashes the object structure.
    Used only in tests.
    
    Returns:
        SHA256 hash (lowercase hex, 64 characters).
    """
```

**Files:** `src/ezra/epb/hasher.py` (or appropriate existing module)

---

### Step 4 — Mutation Guard Tests

Add tests:

* Attempt attribute assignment on `ImageInput` → expect `FrozenInstanceError`
* Attempt attribute assignment on `OCRResult` → expect `FrozenInstanceError`
* Attempt attribute assignment on `ModelArtifactMetadata` → expect `FrozenInstanceError`
* Attempt mutation of EPB bundle dict → expect `TypeError` (MappingProxyType)
* Attempt mutation of `OCRResult.bbox` tuple → expect `TypeError`
* Attempt mutation of `OCRResult.metadata` dict → expect `TypeError` (MappingProxyType)
* Attempt mutation of zone structures (`BBoxNorm`, `ZonePersistence`, `ZoneSchema`) → expect `FrozenInstanceError` (regression guard)

**Files:** `tests/test_runtime_immutability.py` (new test file)

---

### Step 5 — Structural Hash Cross-Validation

Add test:

* Build EPB bundle
* Compute structural hash
* Rebuild EPB bundle (same inputs)
* Assert hash identical

Separate from determinism CI script (this is object-level, not file-level).

**Files:** `tests/test_runtime_immutability.py`

---

### Step 6 — Public Surface Freeze Re-Verification

Ensure:

* No public API drift
* Freeze snapshot unchanged (no new public modules/types)
* All existing tests pass

---

## Invariants (Must Not Change)

1. All 214 tests pass (may increase count with new tests).
2. Coverage ≥ 85%.
3. EPB v1.0.0 schema unchanged.
4. Hash algorithm unchanged.
5. Determinism check passes.
6. Public surface freeze unchanged (no new public modules/types).
7. No runtime behavior drift (except immutability enforcement).
8. CI jobs unchanged.
9. No weakening of guards.
10. No plugin interface change.

---

## Verification Plan

We prove preservation through:

* Full pytest run (all passing)
* Determinism check (multi-run identical bundles)
* Snapshot test stability
* New mutation attempt tests (must raise TypeError/FrozenInstanceError)
* Structural equality checks
* Hash stability confirmation
* Public surface freeze test (unchanged snapshot)

---

## Risk & Rollback Plan

**Risk:** Low

Potential break:

* Plugins relying on mutation (unlikely but must verify)
* Internal code mutating bundle before return
* Callers expecting mutable `bbox` lists (mitigated by `__post_init__` coercion)

If failure occurs:

* Roll back frozen enforcement
* Replace with defensive copying instead
* Re-run full CI

All changes reversible in single commit.

---

## Deliverables

* Updated runtime data models (sealed)
* New tests (~10–15)
* Updated coverage maintained
* `M20_plan.md` (this document)
* `M20_toolcalls.md`
* `M20_run1.md`
* `M20_audit.md`
* `M20_summary.md`

---

## Enterprise Impact

After M20:

EZRA becomes:

* Structurally immutable
* Artifact-boundary sealed
* Mutation-proof at runtime
* Deterministic at object level, not just output level

This is the final runtime hardening step before long-term freeze.

---

**End of M20 Plan**
