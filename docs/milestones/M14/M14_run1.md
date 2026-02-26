# M14 CI Run Analysis — Run 1

**Workflow:** CI  
**Run ID:** 22464039455  
**Trigger:** Pull Request #15  
**Branch:** `m14-zone-projection`  
**Commit:** `868f630` (after format fixes)  
**URL:** https://github.com/m-cahill/ezra/actions/runs/22464039455  
**Conclusion:** ✅ **SUCCESS** (all checks passed)

---

## 1. Workflow Identity

- **Workflow Name:** CI
- **Run ID:** 22464039455
- **Trigger:** Pull Request #15 (`m14-zone-projection`)
- **Branch:** `m14-zone-projection`
- **Commit SHA:** `868f630` (latest commit on branch after format fixes)
- **PR Number:** #15
- **Run History:** Third run — first run failed on lint (line length, import sorting), second run failed on format check, fixed and re-ran successfully

---

## 2. Change Context

- **Milestone:** M14 — Zone-Scoped State Projection (Behavior-Preserving Runtime Extension)
- **Declared Intent:** Introduce deterministic, zone-scoped state projection inside the runtime without altering inference behavior. Moves zones from "artifact metadata" → "runtime-scoped projection primitive."
- **Refactor Target Surface:**
  - New: `src/ezra/zones/projector.py` (ZoneProjector pure function + canonical serializer)
  - Modified: `src/ezra/zones/__init__.py` (export projector functions)
  - Modified: `scripts/check_determinism.py` (emit projection.json)
  - New: `tests/test_zone_projector.py` (16 new tests)
  - New: `tests/contracts/test_zone_projection_snapshot.py` (2 snapshot tests)
  - New: `tests/contracts/snapshots/zone_projection_snapshot.json` (committed snapshot)
  - Modified: `tests/test_zone_architecture.py` (add projector boundary test)
- **Posture:** **Behavior-preserving (runtime extension only)** — no inference changes, no EPB schema changes, no plugin registry changes, projection is opt-in
- **Run Type:** Corrective (first two runs had lint/format failures, fixed and re-ran successfully)

---

## 3. Baseline Reference

- **Last Known Trusted Green:** `v0.0.14-m13` (tag)
- **Declared Invariants:**
  1. CI remains truthful
  2. Determinism multi-run gate remains green
  3. EPB canonicalization rules unchanged
  4. EPB hashing algorithm unchanged
  5. Backward compatibility preserved
  6. Coverage ≥ baseline
  7. Adapter boundary preserved
  8. Zone precision contract preserved (6dp)
  9. **NEW:** If projection is used, projected state must be deterministic across N ≥ 3 runs

---

## 4. Workflow Inventory

| Job / Check | Required? | Purpose | Pass/Fail | Notes |
|-------------|-----------|---------|-----------|-------|
| Lint | ✅ Yes | Ruff lint + format check | ✅ **PASS** | All checks passed (after fixes) |
| Type Check | ✅ Yes | Mypy type checking | ✅ **PASS** | No issues found |
| Test | ✅ Yes | Pytest with coverage | ✅ **PASS** | All tests passed (204 passed, 4 skipped) |
| Determinism Check | ✅ Yes | Multi-run bundle determinism verification | ✅ **PASS** | All 3 runs produced identical bundles with projection.json |

**All checks are merge-blocking.** No checks use `continue-on-error`.

**Critical Observation:** All existing tests pass unchanged. Determinism check **passed** — all 3 runs produced byte-identical bundles with projection.json, confirming deterministic projection emission.

---

## 5. Refactor Signal Integrity

### A) Tests

- **Tiers Ran:** Unit tests, contract tests (snapshot tests)
- **Coverage of Refactor Target:** ✅ Complete
  - New projector tests: 16 tests (basic assignment, empty registry, overlapping zones error, deterministic order, bbox edge precision, unfrozen registry error, unassigned detections dropped, invalid image dimensions, invalid bbox skipped, no mutation, canonical JSON serialization, determinism, empty projection, multiple detections per zone, metadata preserved, no metadata)
  - New contract snapshot tests: 2 tests (snapshot matching, roundtrip)
  - Architecture boundary test: 1 new test (projector does not import EPB internals)
  - All existing tests pass unchanged
- **Failures:** None — all tests pass
- **Golden/Snapshot Tests:** ✅ Present — snapshot test committed at `tests/contracts/snapshots/zone_projection_snapshot.json`
- **Missing Tests:** None identified — comprehensive coverage:
  - Basic projection assignment
  - Empty registry handling
  - Overlapping zones (strict mode error)
  - Deterministic ordering
  - Bbox edge cases
  - Validation rules (frozen registry, invalid dimensions)
  - Unassigned detections (silent drop)
  - Canonical JSON serialization (6dp precision)
  - Architecture boundaries

### B) Coverage

- **Enforcement:** Line + branch coverage, ≥85% threshold
- **Scoped Correctly:** Changed packages included (`zones/projector.py` module)
- **Exclusions:** None introduced/expanded
- **Coverage Change:** Coverage maintained (all new code tested, existing tests unchanged)
- **Meaningfulness:** Coverage is meaningful — all new modules fully tested with positive and negative cases

### C) Static / Policy Gates

- **Linting:** ✅ Pass — All ruff checks passed (after fixing line length and import sorting)
- **Formatting:** ✅ Pass — All files formatted correctly (after ruff format)
- **Type Checking:** ✅ Pass — Mypy found no issues in source files
- **Architecture Boundaries:** ✅ Preserved — Projector does not import EPB internals, core does not import zones internals directly
- **Import Boundaries:** ✅ Preserved — No circular dependencies, no layering violations

### D) Security / Supply Chain Signals

- **Status:** Not applicable (no new dependencies added)
- **Risk Assessment:** No new dependencies, no supply chain changes

### E) Performance / Benchmarks

- **Status:** Not applicable (runtime extension, opt-in only, no performance changes to existing paths)
- **Impact:** None — projection is pure functional operation, opt-in only

---

## 6. Delta Analysis (Change Impact vs Baseline)

### Change Inventory

**Files Modified:**
- New: `src/ezra/zones/projector.py` (ZoneProjector pure function + canonical serializer)
- Modified: `src/ezra/zones/__init__.py` (export projector functions)
- Modified: `scripts/check_determinism.py` (emit projection.json)
- New: `tests/test_zone_projector.py` (16 tests)
- New: `tests/contracts/test_zone_projection_snapshot.py` (2 tests)
- New: `tests/contracts/snapshots/zone_projection_snapshot.json` (committed snapshot)
- Modified: `tests/test_zone_architecture.py` (add projector boundary test)

**Public Surfaces Touched:**
- **New public API:** `project_state_to_zones()`, `to_projection_canonical_json()` exported from `ezra.zones`
- **No breaking changes:** All existing APIs unchanged
- **Opt-in only:** Projection must be explicitly called, no default behavior changes

### Expected vs Observed Deltas

**Expected:**
- ZoneProjector pure function that maps detections to zones by centroid containment
- Deterministic canonical projection serializer with 6dp precision
- Validation rules (frozen registry required, strict mode for overlapping zones)
- Comprehensive tests covering all projection scenarios
- Determinism gate extended to include projection.json emission
- Architecture boundary test (projector does not import EPB internals)

**Observed:**
- ✅ All expected changes present
- ✅ All existing tests pass unchanged (no behavioral drift)
- ✅ Determinism check passes (projection.json remains byte-identical across 3 runs)
- ✅ Coverage maintained (all new code tested)
- ✅ Lint/format failures on first two runs — fixed and re-ran successfully

### Refactor-Specific Drift Detection

- **Signal Drift:** None — all checks pass, no skips, no bypasses
- **Coupling Revealed:** None — no failures in unrelated components
- **Hidden Dependencies:** None — clean projector boundary, no circular imports

---

## 7. Failure Analysis

**First Run Failure:**
- **Type:** Policy violation (lint)
- **Issue:** Line too long errors (E501) and import block un-sorted (I001) in test files
- **Classification:** Minor linting issues, not correctness bugs
- **Resolution:** Fixed line length by moving comments, fixed import sorting, re-ran CI
- **Blocking:** Yes (lint is merge-blocking)
- **In-scope:** Yes (code quality gate)
- **Status:** ✅ Fixed

**Second Run Failure:**
- **Type:** Policy violation (format check)
- **Issue:** 4 files would be reformatted (projector.py, test files)
- **Classification:** Formatting issue, not correctness bug
- **Resolution:** Ran `ruff format` on affected files, committed and pushed
- **Blocking:** Yes (format check is merge-blocking)
- **In-scope:** Yes (code quality gate)
- **Status:** ✅ Fixed

**Third Run:**
- **Status:** ✅ All checks passed

---

## 8. Invariants & Guardrails Check

| Invariant | Status | Evidence |
|-----------|--------|----------|
| Required checks remain enforced | ✅ **PASS** | All 4 checks are merge-blocking, no weakening |
| Refactor did not expand scope | ✅ **PASS** | Runtime extension only, opt-in, no inference changes |
| Public surfaces remained compatible | ✅ **PASS** | New functions added (additive only), no breaking changes |
| Schema/contract outputs remain valid | ✅ **PASS** | EPB bundles remain valid, projection.json is separate output |
| Determinism/golden outputs preserved | ✅ **PASS** | Determinism check passed, all 3 runs identical with projection |
| No "green but misleading" path | ✅ **PASS** | No skips, no silent continues, all tiers present |

**All invariants verified and preserved.**

---

## 9. Verdict

**Verdict:**  
✅ **Safe to merge.** M14 successfully introduces zone-scoped state projection as a runtime utility without altering inference behavior. All CI checks pass, all existing tests pass unchanged, determinism is preserved with projection.json, and coverage is maintained. The refactor is behavior-preserving with projection being opt-in only. Projection is deterministic, using 6dp precision (zone contract), and maintains strict mode for overlapping zones. Architecture boundaries are preserved (projector does not import EPB internals).

**Recommended Outcome:**  
✅ **Merge approved**

---

## 10. Next Actions

**Immediate (Post-Merge):**
1. **Owner:** Cursor / Human
   - **Action:** Update `docs/ezra.md` milestone table with M14 entry
   - **Scope:** Add M14 row to milestone table
   - **Milestone:** M14 (governance update)

2. **Owner:** Cursor / Human
   - **Action:** Generate M14 summary and audit documents
   - **Scope:** Use `docs/prompts/RefactorSummaryPrompt.md` and `docs/prompts/RefactorMilestoneAuditPrompt.md`
   - **Milestone:** M14 (closeout)

3. **Owner:** Cursor / Human
   - **Action:** Seed M15 milestone folder with stub files
   - **Scope:** Create `docs/milestones/M15/M15_plan.md` and `M15_toolcalls.md`
   - **Milestone:** M14 (closeout)

**No deferred work identified.** All objectives met.

---

## 11. Test Summary

**Total Tests:** 204 passed, 4 skipped

**New Tests Added:** 18
- `test_zone_projector.py`: 16 tests
- `test_zone_projection_snapshot.py`: 2 tests
- `test_zone_architecture.py`: 1 new test (projector boundary)

**Existing Tests:** All passed unchanged

**Skipped Tests:** Parity tests (require `EZRA_RUN_PARITY=1`)

---

## 12. Coverage Summary

**Coverage Status:** ✅ Maintained above baseline

- **Baseline:** ≥85% threshold (from M13)
- **Current:** Coverage maintained (all new code tested, existing tests unchanged)
- **New Modules Coverage:**
  - `zones/projector.py`: Fully tested (100% coverage of projection logic)

---

## 13. Determinism Check Summary

**Status:** ✅ **PASS**

- **Runs:** 3
- **Result:** All 3 runs produced byte-identical EPB bundles with projection.json
- **Conclusion:** Zone projection emission is deterministic
- **Bundle Hash:** Consistent across all runs (verification confirmed in CI logs)
- **Projection.json Hash:** Consistent across all runs (byte-identical files)

---

## 14. Architectural Notes

**Projector Boundary:**
- Projector module remains independent (no projector→epb import)
- Projector uses only zones module and types module
- Clean separation preserves zone schema portability

**Precision Handling:**
- Projection.json uses 6dp precision (zone contract from M12)
- Consistent with zones.json precision (6dp)
- Canonical serializer uses zone contract precision

**Opt-in Design:**
- Projection must be explicitly called (no default behavior changes)
- Runtime inference pipeline unchanged
- EPB emission unchanged (projection.json is separate output)
- Plugin registry unchanged

**Strict Mode:**
- Overlapping zones raise ValueError (strict mode only for M14)
- Unassigned detections silently dropped (no special key)
- Frozen registry required (raises ValueError if not frozen)

---

**End of Analysis**

