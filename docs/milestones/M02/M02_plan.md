# M02 — Golden Output Lock & Parity Verification Framework

**Mode:** Behavior Preservation Lock
**Refactor Posture:** Preserve
**Baseline:** `v0.0.2-m01` (tag)
**Branch:** `m02-golden-parity-lock`

---

# 1. Objective

Establish a **hard parity gate** between:

* `EasyOCRPlugin` runtime output
* Committed golden baseline artifacts
* Captured manifest environment

After M02:

> No structural refactor may proceed unless it proves behavioral equivalence against the golden baseline.

This milestone transforms M01 from *baseline capture* into *enforced regression discipline*.

---

# 2. Why M02 Exists (Grounded in M01 Audit)

From the M01 audit :

> ⚠️ No automated parity test yet
> ⚠️ No manifest equality check
> ⚠️ Canonicalization stability not locked across repeated runs

From the M01 summary :

> Golden baseline committed
> Deterministic canonicalization utilities implemented

M01 created the artifacts.
M02 enforces them.

---

# 3. Scope Definition

## In Scope

1. **Parity Test Framework**

   * Load committed `baseline.json`
   * Re-run EasyOCRPlugin on synthetic fixture
   * Canonicalize output
   * Compare to baseline
   * Fail on mismatch

2. **Manifest Equality Check**

   * Load `manifest.json`
   * Validate:

     * easyocr version
     * python version
     * torch version
     * model file checksums
   * Hard fail if mismatch unless explicitly overridden

3. **Determinism Stability Check**

   * Run canonicalization N times (e.g., 5x)
   * Ensure identical JSON output every time
   * Assert bitwise equality

4. **Parity Gate Design**

   * Parity test is:

     * Marked `@pytest.mark.integration` and `@pytest.mark.parity`
     * Disabled by default in CI
     * Enabled via `EZRA_RUN_PARITY=1`
   * Must be runnable locally before any structural refactor

5. **Golden Baseline Integrity Lock**

   * Add hash of `baseline.json` into test
   * Fail if baseline file modified without manifest update

6. **docs/ezra.md Update**

   * Add new section: "Golden Parity Discipline"
   * Clarify policy for updating baseline

---

## Out of Scope

* EasyOCR refactor
* CVAT integration
* RediAI-v3 interaction
* Performance benchmarking
* Multi-fixture expansion

---

# 4. Deliverables

## Code

```
src/ezra/baseline/parity.py
```

Functions:

* `load_baseline()`
* `load_manifest()`
* `validate_manifest_environment()`
* `compare_outputs(current, baseline)`
* `compute_file_sha256(path)`

---

## Tests

```
tests/test_parity.py
```

### Required Tests

1. `test_parity_matches_baseline()`

   * Re-run plugin
   * Canonicalize
   * Compare JSON
   * Assert exact equality

2. `test_manifest_matches_environment()`

   * Validate environment fields
   * Assert equality

3. `test_canonicalization_stable_multiple_runs()`

   * Run 5 times
   * Assert identical output

4. `test_baseline_file_hash_stable()`

   * Compute SHA256 of baseline.json
   * Compare to hardcoded expected hash

All parity tests marked:

```python
@pytest.mark.integration
@pytest.mark.parity
```

---

# 5. CI & Gating Rules

M02 must NOT:

* Require model downloads in PR gating
* Break existing CI
* Lower coverage threshold
* Introduce network dependency

Parity tests must:

* Skip automatically in CI unless `EZRA_RUN_PARITY=1`
* Be documented clearly in README

CI must remain:

```
ruff check --no-fix .
ruff format --check .
mypy src
pytest
coverage ≥85%
```

No gate weakening allowed.

---

# 6. Invariants (Declared for M02)

Must remain true:

* M01 baseline unchanged
* No plugin behavioral drift
* Canonicalization remains deterministic
* CI remains non-mutating
* Plugin-first architecture maintained

Add new invariant:

> Any structural refactor touching EasyOCRPlugin must prove parity via M02 test suite before merge.

---

# 7. docs/ezra.md Updates Required

Add new section:

---

## 8. Golden Parity Discipline (NEW)

After M02:

* Golden baseline artifacts are binding.
* Any change affecting:

  * Plugin output
  * Canonicalization logic
  * Model invocation behavior
* Must:

  1. Run parity suite
  2. Pass manifest check
  3. Update baseline explicitly in a dedicated milestone if behavior change is intentional

Baseline updates require:

* New milestone ID
* Updated manifest
* Explicit audit justification

---

Update milestone table:

| M02 | Golden Output Lock & Parity Verification | Complete | v0.0.3-m02 | PR#X | Hard parity gate enforced |

---

# 8. Acceptance Criteria

M02 is complete when:

* Parity tests implemented
* Manifest validation implemented
* Determinism test implemented
* Baseline hash lock implemented
* CI unaffected
* Coverage ≥85%
* docs/ezra.md updated
* Milestone fold created
* CI green on merge

---

# 9. Risks

| Risk                   | Mitigation                                     |
| ---------------------- | ---------------------------------------------- |
| EasyOCR nondeterminism | Canonicalization + multiple-run stability test |
| Model weight drift     | SHA256 checksum verification                   |
| Torch version mismatch | Manifest equality test                         |
| Silent baseline edit   | Baseline hash assertion                        |

---

# 10. Estimated Size

* ~250–350 lines new code/tests
* 1–2 CI cycles
* 1 milestone fold
* No structural risk

---

# 11. After M02

Only after M02 passes may we begin:

**M03 — Structural Extraction of EasyOCR Integration**

Without M02, refactor is unsafe.

---

# 12. Cursor Execution Instructions

1. Create branch: `m02-golden-parity-lock`
2. Implement parity module
3. Implement tests
4. Update docs/ezra.md
5. Create milestone fold
6. Run full CI locally
7. Open PR
8. Generate M02_run1.md
9. Await merge permission

---

# Strategic Note

You are building EZRA like RediAI v3:

* Phase-gated
* Baseline-first
* Deterministic
* Governance-anchored

M02 is where EZRA transitions from "well-written project" to:

> **Behaviorally governed system.**

