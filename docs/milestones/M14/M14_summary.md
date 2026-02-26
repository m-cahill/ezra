📌 Milestone Summary — M14
========================

**Project:** EZRA (Extensible Zone-Based Runtime Architecture)  
**Phase:** Contract Hardening  
**Milestone:** M14 — Zone-Scoped State Projection (Behavior-Preserving Runtime Extension)  
**Timeframe:** 2026-02-26 → 2026-02-26  
**Status:** Closed  
**Baseline:** v0.0.14-m13 (tag)  
**Refactor Posture:** Behavior-Preserving (Runtime Extension Only)

* * *

## 1. Milestone Objective

M14 introduces deterministic, zone-scoped state projection inside the runtime without altering inference behavior. Prior to M14, zones existed as a locked schema contract (M12) and were wired into EPB as optional artifact metadata (M13), but were not yet usable inside runtime logic. This milestone converts zones from "artifact metadata" into a **runtime-scoped projection primitive**, enabling deterministic partitioning of perception outputs (OCR detections) into zone-scoped state partitions.

Without this milestone, zones would remain purely metadata attached to EPB bundles, preventing runtime logic from using zones for state partitioning, synthesis, or cross-zone reasoning. The zone projection utility provides a pure functional, opt-in mechanism for mapping detections to zones by spatial containment, establishing zones as a structural perception primitive usable both in artifact bundles and runtime state partitioning.

* * *

## 2. Scope Definition

### In Scope

* **ZoneProjector module** — `src/ezra/zones/projector.py` (pure function for mapping detections to zones by centroid containment)
* **Canonical projection serializer** — `to_projection_canonical_json()` with 6dp precision (zone contract)
* **Validation rules** — Frozen registry required, strict mode for overlapping zones, invalid dimension checks
* **Comprehensive tests** — 16 unit tests covering all projection scenarios
* **Contract snapshot tests** — 2 snapshot tests for deterministic projection output
* **Determinism gate extension** — Extended `check_determinism.py` to emit projection.json and verify byte-identical across 3 runs
* **Architecture boundary test** — Ensures projector does not import EPB internals

### Out of Scope

* No automatic zone detection
* No ML changes
* No EPB schema changes
* No inference logic modifications
* No performance optimizations
* No schema version bump
* No runtime default behavior changes
* No non-strict overlap mode (strict mode only for M14)

Projection must be opt-in.

* * *

## 3. Refactor Classification

### Change Type

**Boundary Refactor / Runtime Extension** — Behavior-preserving runtime extension. Introduces pure functional projection utility that maps perception outputs into zone-scoped partitions without modifying existing inference behavior, EPB schema, or plugin registry. Pure additive extension with opt-in design.

### Observability

* **Externally observable:** New public API functions (`project_state_to_zones()`, `to_projection_canonical_json()`) exported from `ezra.zones`
* **Internally observable:** Projector module exists in zones package, determinism script emits projection.json
* **CI observable:** Determinism gate now includes projection.json and verifies byte-identical across 3 runs
* **Runtime observable:** Projection is opt-in only — no default behavior changes unless explicitly called

* * *

## 4. Work Executed

### Key Actions

1. **ZoneProjector Pure Function** (`src/ezra/zones/projector.py`, 219 lines):
   * `project_state_to_zones()` — Maps detections to zones by centroid containment (normalizes pixel coordinates to 0-1 space)
   * Registry must be frozen (raises ValueError if not)
   * Strict mode for overlapping zones (raises ValueError if detection matches multiple zones)
   * Unassigned detections silently dropped (no special key)
   * Deterministic ordering (sorted by zone_id, stable detection order within zones)
   * No mutation of original detections

2. **Canonical Projection Serializer** (`src/ezra/zones/projector.py`):
   * `to_projection_canonical_json()` — Serializes projection dict with 6dp precision (zone contract)
   * Stable key ordering (sorted by zone_id)
   * No reliance on EPB canonicalization (independent serializer)
   * Rejects NaN/Infinity values

3. **Determinism Script Extension** (`scripts/check_determinism.py`, +30 lines):
   * Extended to emit projection.json alongside EPB bundles
   * Verifies byte-identical projection.json across 3 runs
   * Projection.json included in bundle hash computation

4. **Test Coverage** (18 new tests):
   * `test_zone_projector.py` — 16 tests (basic assignment, empty registry, overlapping zones error, deterministic order, bbox edge precision, unfrozen registry error, unassigned detections dropped, invalid image dimensions, invalid bbox skipped, no mutation, canonical JSON serialization, determinism, empty projection, multiple detections per zone, metadata preserved, no metadata)
   * `test_zone_projection_snapshot.py` — 2 tests (snapshot matching, roundtrip)
   * `test_zone_architecture.py` — 1 new test (projector does not import EPB internals)

5. **Architecture Boundary Test** (`tests/test_zone_architecture.py`, +43 lines):
   * Ensures projector module does not import EPB internals
   * Verifies public API includes projector functions

### Counts

* **Files changed:** 17 files
* **Lines added:** 2,518 insertions
* **Lines removed:** 0 deletions
* **Net change:** +2,518 lines
* **New modules:** 1 (`projector.py`)
* **New tests:** 18 (projector tests, snapshot tests, architecture test)
* **CI runs:** 3 (first run failed on lint, second run failed on format, third run passed)

### Migration Steps

None required — backward compatible changes, no breaking changes, existing behavior preserved. Projection is opt-in only.

### Functional Logic Changes

**No functional logic changed in existing code.** Projection is additive only. All existing tests pass unchanged. Inference pipeline unchanged, EPB emission unchanged, plugin registry unchanged.

* * *

## 5. Invariants & Compatibility

### Declared Invariants (Must Not Change)

1. **CI remains truthful** — ✅ Preserved (no weakened gates, all checks pass)
2. **Determinism multi-run gate remains green** — ✅ Preserved (determinism check passed with projection.json)
3. **EPB canonicalization rules unchanged** — ✅ Preserved (8dp for EPB files, projection.json uses 6dp zone contract)
4. **EPB hashing algorithm unchanged** — ✅ Preserved (SHA256, projection.json included when present)
5. **Backward compatibility preserved** — ✅ Preserved (new functions added, no breaking changes)
6. **Coverage ≥ baseline** — ✅ Preserved (coverage maintained, all new code tested)
7. **Adapter boundary preserved** — ✅ Preserved (projector does not import EPB internals)
8. **Zone precision contract preserved (6dp)** — ✅ Preserved (projection.json uses 6dp precision)
9. **NEW: If projection is used, projected state must be deterministic across N ≥ 3 runs** — ✅ Added and verified (determinism check passed)

All invariants verified and preserved.

### Compatibility Notes

* **Backward compatibility preserved:** Yes (new functions added, opt-in only, no default behavior changes)
* **Breaking changes introduced:** No
* **Deprecations introduced:** No

* * *

## 6. Validation & Evidence

| Evidence Type | Tool/Workflow | Result | Notes |
| ------------- | ------------- | ------ | ----- |
| Lint | `ruff check --no-fix .` | ✅ Pass | All checks passed (after fixing line length and import sorting) |
| Format | `ruff format --check .` | ✅ Pass | All files formatted correctly (after ruff format) |
| Type Check | `mypy src/` | ✅ Pass | No issues found |
| Unit Tests | `pytest` (default) | ✅ Pass | All tests passed (204 passed, 4 skipped) |
| Coverage | `pytest --cov=src` | ✅ Maintained | Coverage maintained above baseline |
| Contract Tests | `pytest tests/contracts/` | ✅ Pass | 2/2 snapshot tests pass |
| Determinism Check | `scripts/check_determinism.py` | ✅ Pass | All 3 runs produced identical bundles with projection.json |
| CI Run 1 | GitHub Actions | ❌ Fail | Lint failure (line length, import sorting) |
| CI Run 2 | GitHub Actions | ❌ Fail | Format check failure |
| CI Run 3 | GitHub Actions | ✅ Pass | All jobs passed (Run 22464039455) |
| Snapshot Test | `test_zone_projection_snapshot.py` | ✅ Pass | Snapshot committed and matches |

### Failures Encountered and Resolved

**First CI Run Failure:**
- **Type:** Policy violation (lint)
- **Issue:** Line too long errors (E501) and import block un-sorted (I001) in test files
- **Resolution:** Fixed line length by moving comments, fixed import sorting, re-ran CI
- **Status:** ✅ Fixed and verified in second run

**Second CI Run Failure:**
- **Type:** Policy violation (format check)
- **Issue:** 4 files would be reformatted (projector.py, test files)
- **Resolution:** Ran `ruff format` on affected files, committed and pushed
- **Status:** ✅ Fixed and verified in third run

### Validation Meaningfulness

* Git diff confirms all changes in expected files — validates runtime extension implementation
* CI passes all checks — confirms no behavioral drift or boundary violations
* Determinism gate passes — confirms zone projection emission is deterministic
* All invariants verified — confirms governance posture maintained
* Contract tests comprehensive — confirms backward compatibility and projection correctness

* * *

## 7. CI / Automation Impact

### Workflows Affected

* **CI workflow** (`.github/workflows/ci.yml`): No changes (determinism gate extended via script modification)

### Checks Added/Removed/Reclassified

* **Added:** None
* **Removed:** None
* **Reclassified:** None

### Enforcement Changes

* **Stricter:** No
* **Looser:** No
* **Unchanged:** All existing CI gates remain unchanged

### Signal Drift

* **False green:** None — all checks pass, no silent bypasses
* **Missing coverage:** None — coverage maintained above baseline
* **Flaky tests:** None observed

### CI Effectiveness

* **Blocked incorrect changes:** Yes — lint and format failures caught code quality issues
* **Validated correct changes:** Yes — Final run confirmed all checks pass
* **Failed to observe relevant risk:** No — All issues would be caught

* * *

## 8. Issues, Exceptions, and Guardrails

### Issues Encountered

**Lint Failure (First Run):**
- **Description:** Line too long errors and import block un-sorted in test files
- **Root Cause:** Long inline comments and unsorted imports
- **Resolution:** Moved comments to separate lines, fixed import sorting
- **Status:** ✅ Resolved

**Format Failure (Second Run):**
- **Description:** 4 files would be reformatted
- **Root Cause:** Code formatting not applied after manual edits
- **Resolution:** Ran `ruff format` on affected files
- **Status:** ✅ Resolved

### Guardrails Added

1. **Frozen registry enforcement** — Registry must be frozen before projection (prevents post-initialization modifications)
2. **Strict overlap mode** — Detections matching multiple zones raise ValueError (prevents ambiguous assignments)
3. **Architecture boundary enforcement** — Projector module remains independent (no projector→epb import) — preserves zone schema portability
4. **Determinism verification** — Projection.json verified byte-identical across N≥3 runs — ensures projection determinism

### No New Issues Introduced

No functional issues, no architectural problems, no test failures. All checks pass cleanly after lint/format fixes.

* * *

## 9. Deferred Work

### Deferred Items

None — All objectives met, no deferred work.

* * *

## 10. Governance Outcomes

### What is Now Provably True

1. **Zone-scoped state projection is operational** — Pure functional projection utility maps detections to zones by centroid containment
2. **Projection is deterministic** — Projection.json is byte-identical across N≥3 runs, verified by determinism gate
3. **Strict mode enforced** — Overlapping zones raise ValueError, preventing ambiguous assignments
4. **Architecture boundaries preserved** — Projector does not import EPB internals, maintaining zone schema portability
5. **Precision contracts preserved** — Projection.json uses 6dp precision (zone contract), consistent with zones.json
6. **Opt-in design maintained** — Projection must be explicitly called, no default behavior changes
7. **CI truthfulness maintained** — All checks pass, no weakening

### Governance Posture Changes

* **Invariants:** Extended (new projection determinism invariant added and verified)
* **Interfaces:** Extended (new projector functions exported from `ezra.zones`)
* **Boundaries:** Maintained (projector boundary enforced, no reverse dependencies)
* **CI truthfulness:** Maintained (all checks pass, no weakening)
* **Documentation:** Improved (comprehensive test coverage, snapshot tests committed)

* * *

## 11. Exit Criteria Evaluation

| Criterion | Status | Evidence |
| --------- | ------ | -------- |
| ZoneProjector pure function | ✅ Met | `project_state_to_zones()` implemented with centroid-based assignment |
| Canonical projection serializer | ✅ Met | `to_projection_canonical_json()` implemented with 6dp precision |
| Validation rules | ✅ Met | Frozen registry check, strict mode for overlapping zones, invalid dimension checks |
| Comprehensive tests | ✅ Met | 16 unit tests + 2 snapshot tests + 1 architecture test |
| Determinism gate extended | ✅ Met | Projection.json emission and verification in determinism script |
| Architecture boundary test | ✅ Met | Projector does not import EPB internals verified |
| All existing tests pass unchanged | ✅ Met | 204 passed, 4 skipped (unchanged from baseline) |
| Coverage ≥ baseline | ✅ Met | Coverage maintained above baseline |
| No EPB schema changes | ✅ Met | No EPB schema modifications |
| No runtime behavior changes unless projection used | ✅ Met | Projection is opt-in only |
| Adapter boundary intact | ✅ Met | Projector boundary preserved |
| Determinism verified | ✅ Met | All 3 runs produced identical projection.json |

**All exit criteria met.**

* * *

## 12. Final Verdict

**Milestone objectives met. Zone-scoped state projection functional. Governance preserved. Proceed.**

M14 successfully introduces zone-scoped state projection as a runtime utility without altering inference behavior. All CI checks pass, coverage maintained, and all existing tests pass unchanged. The projection utility is operational with deterministic serialization (6dp precision), strict mode for overlapping zones, and full opt-in design. Projection.json is verified byte-identical across N≥3 runs. Architecture boundaries are preserved (projector does not import EPB internals). EZRA now supports zones as a structural perception primitive usable both in artifact bundles and runtime state partitioning.

* * *

## 13. Authorized Next Step

**Next milestone** (M15 or other contract hardening)

M14 provides the zone-scoped state projection foundation. Next steps may include:

* **M15 — Additional contract hardening** — Further governance strengthening or schema freeze reinforcement
* **M15 — Zone-aware state synthesis** — Runtime zone integration for state synthesis (if authorized)

**Constraints:**
* Zone schema specification must remain stable (governance rule in place)
* EPB v1.0.0 schema must remain stable (zones.json is optional extension)
* Projector boundary must be preserved
* Future zone schema or EPB changes require milestone-level justification

* * *

## 14. Canonical References

* **Commits:**
  * `a3699eb` — M14 implementation (squash merge of PR #15)
  * `868f630` — Format fixes (third CI run)
  * `26dd86d` — Lint fixes (second CI run)

* **Pull Request:** [#15](https://github.com/m-cahill/ezra/pull/15)

* **CI Runs:**
  * Run 1: [22463937511](https://github.com/m-cahill/ezra/actions/runs/22463937511) (failed on lint)
  * Run 2: [22463987348](https://github.com/m-cahill/ezra/actions/runs/22463987348) (failed on format)
  * Run 3: [22464039455](https://github.com/m-cahill/ezra/actions/runs/22464039455) (passed)

* **Tags:**
  * Baseline: `v0.0.14-m13`
  * Release: `v0.0.15-m14`

* **Documents:**
  * Plan: `docs/milestones/M14/M14_plan.md`
  * CI Analysis: `docs/milestones/M14/M14_run1.md`
  * Tool Calls: `docs/milestones/M14/M14_toolcalls.md`
  * This Summary: `docs/milestones/M14/M14_summary.md`
  * Audit: `docs/milestones/M14/M14_audit.md`

* * *

**End of Summary**
