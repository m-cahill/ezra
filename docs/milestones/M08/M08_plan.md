# M08_plan

**Milestone:** M08
**Title:** EPB v1 Emission (Runtime Wiring, Deterministic Bundle Output)
**Mode:** Refactor-Safe Feature Addition
**Posture:** Behavior-Preserving (Existing Surfaces Must Not Drift)

---

# 1. Intent / Target

Implement **EPB v1.0.0 bundle emission** inside EZRA runtime.

M07 defined the EPB spec and schemas (documentation only).
M08 wires runtime emission of EPB bundles without:

* Changing existing plugin behavior
* Breaking golden parity
* Modifying registry semantics
* Altering baseline capture tools
* Weakening CI gates

At end of M08:

* EZRA can optionally emit deterministic EPB bundles
* Output is canonicalized per EPB v1 spec
* Hash computation is deterministic
* Feature is additive and isolated

No RediAI integration. Artifact boundary only (already formalized in M07).

---

# 2. Scope Boundaries

## In Scope

* EPB emission module (new)
* Canonical JSON serializer (shared utility)
* SHA256 bundle hashing implementation
* Optional runtime hook to emit EPB bundle
* Unit tests for:

  * Canonicalization
  * Hash determinism
  * Schema structural conformity (structure only, not full JSON Schema validation yet)

## Out of Scope

* RediAI repo changes
* Schema validation wiring (deferred to Phase XVI)
* Determinism multi-run gate
* Plugin refactors
* Baseline modifications
* CLI breaking changes
* Performance optimization

---

# 3. Invariants (Must Not Change)

These are binding unless explicitly overridden:

From M07 audit and `ezra.md`:

1. CI remains truthful (no weakened gates)
2. No `src/` behavior drift for existing plugin calls
3. Registry static and deterministic
4. No new required dependencies
5. Golden parity discipline unchanged
6. EPB canonicalization rules preserved:

   * UTF-8
   * LF
   * Sorted keys
   * 8 decimal float precision
   * No NaN/Infinity
7. SHA256 hashing rules must match EPB spec
8. Artifact-boundary-only RediAI separation preserved

---

# 4. Verification Plan

## A. Behavioral Parity Verification

* Existing test suite must pass unchanged.
* Golden parity tests must pass unchanged.

## B. Canonicalization Tests (New)

Add unit tests verifying:

* Sorted keys
* 8-decimal float formatting
* Deterministic string output across runs
* Stable encoding

## C. Hash Determinism Tests

* Same logical state → identical bundle hash
* Order of JSON writing does not affect hash
* Hash changes if content changes

## D. Structural Contract Tests

Without full JSON Schema wiring:

* Verify required top-level EPB files:

  * manifest
  * detections
  * state
  * hashes
* Verify `epb_version == "1.0.0"`

---

# 5. Implementation Steps (Small & Reversible)

## Step 1 — Add EPB Module

Create:

```
src/ezra/epb/
    __init__.py
    canonical.py
    builder.py
    hasher.py
    writer.py
```

No modifications to existing core modules yet.

---

## Step 2 — Implement Canonical JSON Serializer

`canonical.py`

* Deterministic serializer:

  * sort_keys=True
  * ensure_ascii=False
  * separators=(",", ":")
  * float formatting to 8 decimal places
  * reject NaN/Infinity

Add unit tests in `tests/test_epb_canonical.py`.

---

## Step 3 — Implement Bundle Builder

`builder.py`

Input:

* plugin detections
* structured state

Output:

* In-memory EPB bundle dictionary

No disk I/O here.

---

## Step 4 — Implement SHA256 Hasher

`hasher.py`

* Hash canonical JSON strings
* Compute per-file hashes
* Compute bundle hash from sorted file hashes

Add deterministic tests.

---

## Step 5 — Implement Writer

`writer.py`

* Write EPB directory
* Write files in deterministic order
* Enforce LF line endings
* No implicit mutation

---

## Step 6 — Add Optional Emission Hook

Inside core orchestration:

Add optional parameter:

```
emit_epb: bool = False
epb_output_dir: Optional[str] = None
```

Default must preserve old behavior.

No existing call sites changed.

---

## Step 7 — Add Tests

Add:

* `tests/test_epb_builder.py`
* `tests/test_epb_hashing.py`
* `tests/test_epb_emission.py`

No integration with plugins required beyond stub data.

---

## Step 8 — CI Verification

* Lint
* Type check
* Unit tests
* Coverage ≥ current (94.85% baseline)
* No threshold lowering

---

# 6. Risk & Rollback Plan

## Risk

* Accidental mutation of runtime behavior
* Float precision inconsistency
* Non-deterministic dictionary ordering
* Encoding inconsistencies

## Rollback

* Revert M08 branch
* No migrations required
* No schema changes required
* No registry changes

Blast radius isolated to new `epb/` module.

---

# 7. Deliverables

At milestone close:

* `src/ezra/epb/` module
* Unit tests for canonicalization and hashing
* CI green
* Coverage ≥ baseline
* `M08_run1.md`
* `M08_audit.md`
* `M08_summary.md`
* Tag: `v0.0.9-m08`

---

# 8. Explicit Cursor Instructions

Cursor must:

1. Follow refactor posture — preserve behavior.
2. Not modify existing plugin interfaces.
3. Not alter baseline capture logic.
4. Not add external dependencies.
5. Not weaken CI.
6. Keep EPB version locked to `"1.0.0"`.
7. Ensure no RediAI imports exist.

After implementation:

* Generate CI run analysis.
* Generate audit.
* Generate summary.
* Await merge authorization.

---

# Strategic Note

This milestone keeps RediAI separation intact:

* EZRA now emits certifiable bundles.
* RediAI still untouched.
* Artifact boundary preserved.
* Governance purity maintained.

This is the correct next mechanical step before Phase XVI.

