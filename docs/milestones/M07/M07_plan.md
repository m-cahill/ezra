# M07_plan — EPB v1 Specification & RediAI Separation Guardrail

---

## 1. Intent / Target

**Primary Objective:**
Define and lock the **EZRA Perception Bundle (EPB) v1 specification** and formally document the architectural separation between EZRA and RediAI v3.

This milestone does **not** implement engine orchestration or RediAI integration.

It:

* Defines EPB v1 artifact contract
* Defines canonicalization + hashing rules
* Documents artifact-boundary-only integration posture
* Updates `docs/ezra.md` to permanently record separation principles
* Saves draft EPB schemas into `docs/` for future Phase XVI certification

This milestone establishes EZRA's **certifiable output surface**.

---

## 2. Scope Boundaries

### In Scope

* Create `docs/specs/epb_v1/` directory
* Add:

  * `EPB_V1_SPEC.md`
  * JSON Schemas (manifest, detections, state, delta, hashes)
* Define canonical JSON rules
* Define deterministic hashing rules
* Add determinism requirements section
* Update `docs/ezra.md` with:

  * Explicit RediAI separation rule
  * Artifact-boundary-only integration posture
  * EPB v1 declared as future-certified surface

### Out of Scope

* No runtime changes
* No plugin modifications
* No engine orchestration
* No RediAI repo modifications
* No CI changes
* No schema validation wiring
* No determinism gate implementation
* No EPB emission code

This is specification + governance only.

---

## 3. Invariants (Must Not Change)

These are binding:

1. EasyOCR behavior unchanged (parity suite still passes)
2. Registry static + deterministic
3. No runtime behavior drift
4. CI remains unchanged and truthful
5. No new dependencies added
6. No changes to plugin interfaces
7. No runtime-level integration with RediAI
8. EZRA remains runtime-only (training remains out-of-scope)

Verification:

* Run full CI
* Run parity suite locally
* Confirm zero changes in `src/`
* Confirm no CI workflow diffs

---

## 4. Verification Plan

Cursor must:

1. Confirm `git diff` shows:

   * Only documentation changes
   * Only new files under `docs/specs/`
2. Run:

   ```
   ruff check --no-fix .
   ruff format --check .
   mypy src
   pytest
   ```
3. Confirm coverage unchanged (≈94–95%)
4. Confirm no registry modification
5. Confirm no changes to plugin files
6. Confirm parity suite still passes locally (if run)

Evidence must be recorded in:

* `docs/milestones/M07/M07_run1.md`

---

## 5. Implementation Steps (Ordered, Reversible)

### Step 1 — Create EPB Spec Directory

Create:

```
docs/specs/epb_v1/
```

---

### Step 2 — Add EPB_V1_SPEC.md

Must include:

* EPB directory contract
* Canonical JSON rules
* Hashing algorithm
* Determinism requirements
* ML nondeterminism containment rule
* Versioning rules
* Forward compatibility guidance

Include:

```
epb/
  manifest.json
  detections.json
  state.json
  delta.json (optional)
  hashes.json
```

Include canonicalization rules:

* UTF-8
* LF
* Sorted keys
* Stable float formatting (8 decimal places max, no NaN/Infinity)
* SHA256

---

### Step 3 — Add Draft JSON Schemas

Under:

```
docs/specs/epb_v1/schemas/
```

Add:

* manifest.schema.json
* detections.schema.json
* state.schema.json
* delta.schema.json
* hashes.schema.json

These are production-grade schemas (not sketches).

No validation wiring.

---

### Step 4 — Update docs/ezra.md

You must update `docs/ezra.md`  with:

#### A. New Section: External Governance Boundary

Add a new section:

## 10. RediAI Separation & Certification Posture

Include:

* EZRA produces EPB bundles
* RediAI certifies EPB bundles
* No code-level integration
* No shared modules
* Artifact-boundary-only interaction
* EZRA never imports RediAI
* RediAI never imports EZRA

State clearly:

> Integration between EZRA and RediAI occurs only at the artifact boundary.
> No runtime code is shared. No plugin loaders are shared.

This must become a standing invariant.

Add governance rule:

> Any change to EPB directory structure, canonicalization rules, hashing algorithm, or schema definitions requires:
>
> * A new milestone
> * A version bump in `epb_version`
> * Explicit audit justification

---

#### B. Add EPB v1 to Governance Model

Under "Standing Invariants" (Section 3), add:

* EPB bundle must remain schema-stable once emitted
* Canonical JSON rules must be preserved
* Hashing rules must not change without milestone
* Artifact-boundary-only integration with RediAI
* EPB version immutability (once emitted, version cannot change)

---

### Step 5 — Update Milestone Table

Add M07 entry:

| M07 | EPB v1 Specification & External Certification Guardrail | Complete | v0.0.8-m07 | PR#X | EPB v1 spec locked, RediAI separation rule formalized |

---

### Step 6 — Create M07 Audit + Summary

After CI passes:

Generate:

* `M07_summary.md`
* `M07_audit.md`

Audit must explicitly confirm:

* No runtime modifications
* No boundary violations
* No CI weakening
* Governance rule added
* Schemas saved in docs only

---

### Step 7 — Merge + Tag

Tag:

```
v0.0.8-m07
```

Verify:

* Tag points to merge commit
* CI green on main
* Milestone table updated

---

## 6. Risk & Rollback Plan

Risk level: Very low (documentation-only)

Rollback:

* Revert M07 commit
* No runtime impact
* No schema wiring impact

No migrations required.

---

## 7. Deliverables

* `docs/specs/epb_v1/EPB_V1_SPEC.md`
* 5 draft schema files
* Updated `docs/ezra.md`
* `M07_summary.md`
* `M07_audit.md`
* `M07_run1.md`
* Updated milestone table
* Tag `v0.0.8-m07`

---

## 8. Governance Notes

This milestone:

* Does not integrate RediAI
* Does not alter runtime
* Does not expand plugin system
* Does not add engine orchestration

It formalizes:

> EZRA emits certifiable artifacts
> RediAI certifies those artifacts
> Both remain architecturally pure

---

## 9. Exit Criteria

M07 is complete when:

* EPB v1 spec committed
* Schemas saved in `docs/specs/epb_v1/`
* `docs/ezra.md` updated with separation rule
* CI green
* No runtime drift
* Tag created
* Audit PASS

---

# End of Plan
