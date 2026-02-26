# M11 Plan

## EPB Hash Integrity Verification (Self-Validation Hardening Phase 3)

---

## 1. Intent / Target

### Primary Objective

Introduce **runtime self-verification of `hashes.json`** after bundle emission.

After M10:

* EPB bundles are deterministic (M09).
* EPB bundles are schema-validated before hashing (M10).
* `hashes.json` is written but not verified against on-disk content.

Currently:

```
build → canonicalize → validate → hash → write
```

But we do not:

* Recompute hashes from written files.
* Verify that `hashes.json` matches actual file contents.
* Provide a runtime verification utility.

M11 adds:

> Post-write integrity verification of EPB bundles.

This ensures:

* On-disk integrity.
* No write-time corruption.
* No future accidental drift in hashing logic.
* Stronger artifact-boundary guarantees for RediAI certification.

---

## 2. Scope Boundaries

### ✅ In Scope

* Add `verify_epb_bundle(bundle_path: Path)` utility.
* Recompute SHA256 hashes for all JSON files.
* Compare to `hashes.json`.
* Raise `ValueError` on mismatch.
* Unit tests (positive + tamper cases).
* CI test coverage.
* No schema changes.
* No hashing rule changes.
* No canonicalization changes.

### ❌ Out of Scope

* Changing hashing algorithm.
* Modifying EPB spec.
* Changing bundle directory structure.
* Integrating with RediAI runtime.
* Signing / cryptographic key infrastructure.
* Cross-platform reproducibility.
* Performance optimization.

---

## 3. Refactor Posture

Strict Hardening — Behavior Preserving.

Valid bundles remain unchanged.

New behavior:

* Verification utility available.
* Optional verification step after writing.
* No changes to emission format.

---

## 4. Invariants (Must Remain True)

From `docs/ezra.md`:

* CI remains truthful.
* EPB canonicalization rules unchanged.
* EPB hashing rules unchanged.
* EPB schema stability maintained.
* Artifact-boundary-only RediAI separation preserved.
* Determinism gate remains green.
* Schema validation remains active.

### New Invariant (M11)

* EPB bundles must be internally hash-consistent when verified.

---

## 5. Verification Plan

### A. New Module

Create:

```
src/ezra/epb/hash_verifier.py
```

Responsibilities:

```python
def verify_epb_bundle(bundle_dir: Path) -> None:
    """
    Recompute SHA256 hashes of all bundle JSON files and
    verify against hashes.json.
    Raise ValueError if mismatch.
    """
```

Rules:

* Load hashes.json.
* Recompute hash for:

  * manifest.json
  * detections.json
  * state.json (if present)
  * delta.json (if present)
* Compare exactly.
* Raise descriptive error on mismatch.

---

### B. Optional Emission Integration

Modify `write_epb_bundle()`:

After writing all files:

```
verify_epb_bundle(bundle_path)
```

This ensures:

* If disk write corruption occurs, it is caught immediately.

Must not:

* Re-hash before writing.
* Mutate any files.

---

### C. Unit Tests

Add:

1. `test_verify_valid_bundle_passes()`
2. `test_verify_detects_tampered_manifest()`
3. `test_verify_detects_tampered_detections()`
4. `test_verify_missing_hash_entry_fails()`
5. `test_verify_extra_file_ignored_or_fails()` (explicit decision below)

---

## 6. Critical Design Decision — Extra Files

We must define expected behavior if bundle contains extra files.

### Locked Decision:

* Only JSON files defined by EPB spec are hashed.
* Extra files are ignored.
* Missing required files → fail.

This keeps compatibility with future optional artifacts.

---

## 7. Implementation Steps (Ordered)

1. Create branch `m11-epb-hash-verification`
2. Implement `hash_verifier.py`
3. Add unit tests
4. Integrate verification into emission pipeline (after write)
5. Run full CI
6. Confirm determinism gate still green
7. Open PR
8. Monitor CI
9. Generate `M11_run1.md`
10. After merge:

* Generate `M11_summary.md`
* Generate `M11_audit.md`
* Update milestone table
* Tag `v0.0.12-m11`

---

## 8. Risk & Rollback Plan

### Risks

* Hash recomputation order mismatch.
* Float precision differences.
* Determinism regression.

### Mitigation

* Reuse existing `compute_sha256()` logic from `hasher.py`.
* Do not duplicate hashing code.
* Determinism gate will detect drift.

### Rollback

If hashes change unexpectedly:

```
git revert integration commit
```

No schema change required.

---

## 9. Deliverables

* `hash_verifier.py`
* Emission integration patch
* 4–6 unit tests
* CI green
* Determinism still green
* M11 documentation
* Tag `v0.0.12-m11`

---

## 10. Acceptance Criteria

* All valid bundles verify successfully.
* Tampered bundles fail verification.
* Determinism unchanged.
* No coverage regression.
* CI remains truthful.
* No schema modification.
* No hashing algorithm change.

---

## 11. Locked Design Decisions

### Q1 — Extra Files Policy
**Hybrid (spec-strict for declared files, lenient for undeclared files)**
- Verify every file listed in `hashes.json.files` exists on disk and matches hash
- Ignore extra on-disk files not listed in `hashes.json.files`

### Q2 — `hashes.json` Self-Hash Verification
**YES, verify it**
- Reconstruct canonical bytes of `hashes.json` as written on disk
- Verify self-hash entry according to spec logic (hash computed before self-entry is added)

### Q3 — `bundle_hash` Verification
**YES, verify it**
- Recompute `bundle_hash` from verified per-file hashes using same deterministic rule
- Confirm equality

### Q4 — Required Files
**Required set:**
- `manifest.json` — required
- `detections.json` — required
- `hashes.json` — required
- `state.json` — optional (only if declared in `hashes.json.files`)
- `delta.json` — optional (only if declared in `hashes.json.files`)

### Q5 — Integration Call Location
**Unconditional verification after write**
- `write_epb_bundle()` MUST call `verify_epb_bundle(bundle_path)` unconditionally after all writes complete
- No parameter, no environment flag, no bypass
