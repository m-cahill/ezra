# 📌 M10_plan — EPB Schema Validation Wiring (EPB Hardening Phase 2)

---

## 1. Intent / Target

### Primary Objective

Promote EPB JSON Schema validation from documentation-level specification to **runtime-enforced invariant** inside EZRA emission.

After M09:

* EPB bundles are deterministic.
* Hashing rules are enforced.
* Canonicalization rules are locked.
* Schema spec exists in `docs/specs/epb_v1/schemas/`.

However:

> EZRA currently emits EPB bundles without validating them against their own JSON Schemas before hashing + writing.

M10 introduces:

* Internal JSON Schema validation step.
* Validation failure = hard error.
* CI verification of schema enforcement.
* No schema modification.
* No EPB version bump.

This converts schema stability from documentation promise → runtime invariant.

---

## 2. Scope Boundaries

### ✅ In Scope

* JSON Schema validation using local schema files.
* Validation of:

  * `manifest.json`
  * `detections.json`
  * `state.json`
  * `delta.json` (if present)
  * `hashes.json`
* Emission pipeline update to validate before write.
* CI test coverage for validation logic.
* Negative test cases (invalid bundle structure).
* No new external network calls.

### ❌ Out of Scope

* Changing EPB schemas.
* Bumping `epb_version`.
* Changing canonicalization rules.
* Changing hashing rules.
* Cross-platform determinism.
* RediAI integration.
* Performance optimization.

---

## 3. Refactor Posture

**Behavior-Preserving (Strict Hardening)**

The only allowed behavior change:

> Invalid EPB structures now fail fast instead of silently emitting.

Valid bundles must remain byte-identical to M09 behavior.

---

## 4. Invariants (Must Remain True)

From Operating Manual:

1. CI remains truthful.
2. EPB canonicalization rules unchanged.
3. EPB hashing rules unchanged.
4. EPB schema stability maintained.
5. Artifact-boundary-only RediAI separation preserved.
6. Determinism gate remains green.

### New Invariant (M10)

7. All emitted EPB JSON files must validate against EPB v1.0.0 schemas before hash computation and write.

---

## 5. Verification Plan

### A. Runtime Validation

Introduce:

```
src/ezra/epb/schema_validator.py
```

Responsibilities:

* Load local schema from:

  ```
  docs/specs/epb_v1/schemas/
  ```
* Validate JSON dict using `jsonschema`.
* Raise `ValueError` on failure with human-readable message.

### B. Emission Flow Change

Modify builder/writer pipeline:

Current flow:

```
build → canonicalize → hash → write
```

New flow:

```
build → canonicalize → validate → hash → write
```

Validation must occur on in-memory dicts before hashing.

### C. Unit Tests

Add:

1. `test_valid_bundle_passes_schema_validation()`
2. `test_invalid_manifest_fails_validation()`
3. `test_invalid_detections_fails_validation()`
4. `test_schema_validator_raises_on_missing_required_field()`

All PR-gated.

### D. CI Enforcement

No new job required.

Validation runs during:

* Standard test job.
* Determinism job indirectly (if invalid, determinism job fails before hashing).

---

## 6. Implementation Steps (Ordered & Reversible)

### Step 1 — Add `jsonschema` dependency

Add to `pyproject.toml`:

```
jsonschema>=4.0
```

Dev + runtime (lightweight dependency, no network at runtime).

### Step 2 — Implement Schema Loader

* Use `pathlib` to load schema files.
* Cache loaded schemas in-memory.
* No dynamic schema fetching.

### Step 3 — Implement Validator

```
def validate_bundle(bundle_dict: dict) -> None:
    ...
```

Raise on failure.

No return value.

### Step 4 — Integrate Into Emission

Inside EPB builder or writer:

```
validate_bundle(bundle)
```

Before hashing.

### Step 5 — Add Unit Tests

Include negative tests.

### Step 6 — Verify Determinism Still Passes

Run full CI:

* Determinism-check must remain green.
* Hashes must remain identical.

If hashes change → immediate failure and rollback.

---

## 7. Risk & Rollback Plan

### Risks

* Schema files mismatch implementation.
* Minor formatting differences trigger validation errors.
* Unexpected schema looseness/tightness.

### Mitigation

* If schema mismatch discovered:

  * Do NOT modify schema.
  * Do NOT silently relax validation.
  * Open issue.
  * Decide in separate milestone.

### Rollback

If integration breaks valid emission:

```
git revert emission integration commit
```

Schemas remain untouched.

---

## 8. Deliverables

* `schema_validator.py`
* Updated emission pipeline
* Added unit tests
* Updated CI passing
* `M10_run1.md`
* `M10_summary.md`
* `M10_audit.md`
* Tag: `v0.0.11-m10`

---

## 9. Acceptance Criteria

* All valid bundles pass validation.
* Invalid structures fail.
* Determinism gate still passes.
* No schema modifications.
* No coverage regression.
* CI remains truthful.
* No branch protection weakening.

---

## 10. Definition of Done

* CI green (all jobs).
* Validation invoked in runtime.
* Determinism unchanged.
* Audit passes.
* Tag created.
* Milestone table updated.

---

# 📌 Cursor Handoff Block

You may now hand this directly to Cursor:

---

> Implement **M10 — EPB Schema Validation Wiring** exactly as specified in M10_plan.
>
> Constraints:
>
> * Do NOT modify EPB schemas.
> * Do NOT change canonicalization.
> * Do NOT change hashing rules.
> * Validation must occur before hash computation.
> * CI must remain fully truthful.
> * Determinism-check must remain green.
>
> Steps:
>
> 1. Create branch `m10-epb-schema-validation`
> 2. Add jsonschema dependency
> 3. Implement `schema_validator.py`
> 4. Integrate validation into emission pipeline
> 5. Add unit tests (positive + negative)
> 6. Open PR
> 7. Monitor CI
> 8. Generate M10_run1.md
> 9. After merge:
>
>    * Generate M10_summary.md
>    * Generate M10_audit.md
>    * Update `docs/ezra.md`
>    * Tag `v0.0.11-m10`
>    * Seed M11 folder stub

---

# 📌 Strategic Positioning

With M10 complete:

* EPB determinism (M09) ✅
* EPB schema enforcement (M10) ✅
* Canonicalization + hashing stability (M08) ✅

At that point:

> EPB becomes a formally deterministic, schema-validated, hash-stable, CI-enforced artifact surface.

Which aligns perfectly with your RediAI artifact-boundary discipline.
