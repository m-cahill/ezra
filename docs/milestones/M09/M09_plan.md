# 📌 M09_plan — Determinism Multi-Run Gate (EPB Hardening)

---

## 1. Intent / Target

**Primary Objective:**
Introduce a **determinism multi-run CI gate** for EPB bundle emission to formally prove:

> Identical inputs → byte-stable EPB bundle outputs across repeated executions in the same environment.

M08 delivered:

* EPB v1.0.0 bundle emission
* 100% EPB module coverage
* 33 tests
* No behavioral drift
* Green CI

However:

* Determinism is currently validated by unit tests and structural assertions.
* We do **not yet have a CI-level multi-run byte comparison guardrail**.
* Determinism is a core RediAI posture expectation (see Phase XV inheritance logic).

This milestone converts determinism from "implicitly covered" → **explicit CI invariant**.

---

## 2. Scope Boundaries

### ✅ In Scope

* EPB bundle emission pipeline
* Deterministic artifact serialization
* CI workflow modification
* Artifact comparison logic
* Job summary evidence
* Machine-readable determinism report (JSON)

### ❌ Out of Scope

* Feature additions to EPB format
* Schema changes
* Performance optimization
* Refactoring unrelated modules
* Coverage threshold changes
* Security enhancements (unless required for gate stability)
* JSON Schema validation wiring (deferred candidate for M10)

---

## 3. Refactor Posture

**Behavior-Preserving**

No externally observable behavior changes are authorized.

The milestone introduces:

* A CI gate
* Verification logic
* Artifact comparison

It must not:

* Change bundle format
* Change ordering
* Change hashing algorithm
* Modify serialization behavior

If determinism fails, CI must fail — not auto-fix.

---

## 4. Invariants (Mandatory)

At least three invariants must be declared and verified.

### Invariant 1 — Byte Stability

Given identical input fixture, the emitted EPB bundle bytes are identical across N repeated executions within the same CI job.

**Verification:**

* Execute emission ≥3 times.
* Compute SHA256 of each output.
* Compare hashes.
* Fail on mismatch.

---

### Invariant 2 — No Hidden Timestamp / Randomness

Bundle must not contain:

* timestamps
* nondeterministic ordering
* random seeds
* UUIDs
* environment-derived data

**Verification:**

* Determinism comparison
* Explicit scan for known volatile fields (if applicable)

---

### Invariant 3 — CI Signal Integrity

If determinism fails:

* CI job fails
* No continue-on-error
* No muted failure

**Verification:**

* Determinism job marked required
* Branch protection includes job

---

## 5. Verification Plan

### CI Additions

New job: `determinism-check`

Runs after tests.

Steps:

1. Install dependencies
2. Generate bundle 1 → save as `bundle_1.epb`
3. Generate bundle 2 → save as `bundle_2.epb`
4. Generate bundle 3 → save as `bundle_3.epb`
5. Compute SHA256 of each
6. Compare all hashes
7. Emit:

   * `determinism_report.json`
   * SHA values
   * Result summary

If mismatch → exit 1

---

### Artifacts to Upload

* `bundle_1.epb`
* `bundle_2.epb`
* `bundle_3.epb`
* `determinism_report.json`

Add to job summary:

```
## Determinism Gate
SHA1: <hash>
SHA2: <hash>
SHA3: <hash>
Result: PASS/FAIL
```

---

### Acceptance Criteria

* All 3 hashes identical
* No test coverage regression
* No CI weakening
* CI green with determinism gate required

---

## 6. Implementation Steps (Ordered & Reversible)

### Step 1 — Create Determinism Script

Add:

```
scripts/check_determinism.py
```

Responsibilities:

* Run emission N times
* Hash outputs
* Compare
* Write JSON report
* Exit non-zero on mismatch

No logic refactor. Only invocation wrapper.

---

### Step 2 — Wire CI Job

Modify `.github/workflows/ci.yml`:

Add job:

```
determinism:
  needs: build-test
  runs-on: ubuntu-latest
```

Ensure:

* No continue-on-error
* Explicit failure propagation

---

### Step 3 — Upload Artifacts

Use `actions/upload-artifact@v4`

---

### Step 4 — Add Required Check

If branch protections configurable:

* Add determinism job as required
  Else:
* Open issue with exact CLI command

---

### Step 5 — Add Minimal Determinism Unit Test

Optional but recommended:

* Snapshot-based assertion inside test suite
* But CI multi-run remains canonical proof

---

## 7. Risk & Rollback Plan

### Risks

* Hidden nondeterminism discovered
* Flaky ordering bug
* Environment differences in matrix

### Containment

If nondeterminism found:

1. Capture artifact diffs
2. Fail CI
3. Do not patch silently
4. Create hotfix branch

### Rollback

If CI wiring causes failure unrelated to determinism:

* Revert workflow change
* Preserve script
* Move to follow-up milestone

---

## 8. Deliverables

* `scripts/check_determinism.py`
* Updated `ci.yml`
* Determinism job summary output
* Uploaded determinism artifacts
* Required check enforcement
* M09_summary.md
* M09_audit.md
* M09_run1.md

---

## 9. Guardrail Additions

From Refactoring Audit Standard:

Add to audit checklist:

* Invariant declaration verified
* Determinism gate present
* No silent CI weakening
* Artifact hash comparison evidence attached

---

## 10. Definition of Done

* CI job passes across matrix
* Hashes identical
* No coverage regression
* No artifact drift
* Determinism job required for merge
* Audit passes
* Tag created after merge

---

# 📌 Milestone Classification

Change Type: **Boundary Hardening / Governance Hardening**

Not semantic refactor.
Not behavior change.
Pure invariant enforcement.

---

# 📌 Explicit Cursor Handoff Prompt

> Implement **M09 — Determinism Multi-Run Gate** exactly as specified in M09_plan.
>
> Follow the refactor template strictly.
>
> * Do not modify bundle format.
> * Do not refactor unrelated modules.
> * Add determinism-check CI job.
> * Add artifact hashing + JSON report.
> * Upload artifacts.
> * Fail CI on mismatch.
>
> After implementation:
>
> 1. Open PR `m09-determinism-gate`
> 2. Monitor CI
> 3. Generate `M09_run1.md`
> 4. If green → request merge approval
> 5. On merge → generate summary + audit
> 6. Tag `v0.0.10-m09`
> 7. Create next milestone folder stub (M10_plan.md + toolcalls.md)

