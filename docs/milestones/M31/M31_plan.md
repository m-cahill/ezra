# M31_plan — v1.0.0 Release Gate (Enterprise Lock)

**Project:** EZRA  
**Phase:** Transition from Phase V → v1.0.0  
**Milestone:** M31 — v1.0.0 Release Gate  
**Refactor Posture:** Behavior-Preserving  
**Objective Type:** Governance & Release Certification  

---

## 1. Intent / Target

M31 formally transitions EZRA from **Phase V (Release Lock)** to a **v1.0.0 certified release artifact**.

This milestone does **not** introduce feature work or structural refactors.

Its purpose is to:

* Freeze the EPB contract at a tagged release boundary
* Certify CI invariants at release level
* Validate artifact reproducibility at tagged commit
* Produce external-audit-ready evidence
* Establish semantic versioning baseline

> If M31 does not occur, EZRA remains "phase-complete" but not formally released.

---

## 2. Scope Boundaries

### In Scope

* Version bump to `v1.0.0`
* Release tag creation (annotated)
* Re-run full CI matrix on release commit
* Validate:
  * Hermetic reproducibility (3.10/3.11/3.12)
  * Determinism gates
  * SBOM generation
  * Security gates
  * Required checks enforcement
* Confirm no drift between:
  * M29 reproducibility guarantees
  * M30 governance declaration
* Generate:
  * `M31_plan.md`
  * `M31_run1.md`
  * `M31_audit.md`
  * `M31_summary.md`
  * `M31_toolcalls.md`
* Update `docs/phase_v_completion_declaration.md` to reference v1.0.0 tag
* Create GitHub Release (machine-verifiable)

### Out of Scope

* No EPB schema changes
* No emission logic changes
* No CI structural changes
* No dependency upgrades
* No coverage adjustments
* No refactors
* No feature additions
* No README expansion beyond version reference

---

## 3. Invariants (Must Not Change)

These are binding:

1. **EPB contract frozen**
2. **Bundle hash determinism preserved**
3. **Hermetic reproducibility preserved across 3.10–3.12**
4. **Coverage ≥ 95% (current baseline)** — *Note: M28 gate is ≥85%; ledger shows 95.90% at M30.*
5. **Required checks unchanged**
6. **No `continue-on-error` added**
7. **Security gates unchanged**
8. **SBOM generation unchanged**
9. **No artifact structure drift**

If any invariant fails → milestone blocks and reverts to corrective action.

---

## 4. Verification Plan

### A. CI Run (Release Commit)

* Trigger full matrix CI on:
  * `main`
  * tagged commit candidate
* Capture run ID
* Confirm all required checks green

### B. Reproducibility Check

Confirm:

* Identical canonical bundle hash across Python 3.10/3.11/3.12
* Hash matches M29 baseline: `c186777c33b7b7b9d11540bda7398efd0dfb085143506513a4ce87836c6ac7c2`
* No delta in canonicalization logic

### C. Determinism Check

* Re-run determinism gate (triple-run compare)
* Confirm byte-identical bundles

### D. SBOM + Security

* SBOM artifact generated
* No new high-severity findings
* SEC-001 remains infra-only and documented (no scope expansion)

### E. Governance Confirmation

* Required checks still enforced
* No reclassification
* No silent weakening

### F. Evidence Artifacts

Store:

* CI run link
* Hermetic hash outputs
* Coverage report
* SBOM artifact
* Security reports

---

## 5. Implementation Steps (Ordered, Reversible)

### Step 0 — Housekeeping on `main`

* Commit `.gitignore` update (`.venv_minimal/`, `ci_test_run_*.log`)

### Step 1 — Branch

* `m31-release-gate`

### Step 2 — Version Bump + Declaration Update

Single commit: `chore(release): prepare v1.0.0`

Only:

* `src/ezra/__init__.py`
* `pyproject.toml`
* `docs/phase_v_completion_declaration.md`

### Step 3 — Open PR

* Wait for full CI matrix

### Step 4 — Generate `M31_run1.md`

* Using workflow analysis posture

### Step 5 — Merge (merge commit only)

### Step 6 — Tag

* Annotated tag: `v1.0.0`

### Step 7 — GitHub Release

* Attach evidence via `gh release create v1.0.0 --notes-file RELEASE_NOTES.md`

### Step 8 — Milestone Artifacts

Generate:

* `M31_summary.md` (strict format per summaryprompt)
* `M31_audit.md`
* `M31_toolcalls.md` (full log)

### Step 9 — Closeout

* Confirm tag exists
* Confirm release published
* Confirm branch protection unchanged

---

## 6. Risk & Rollback Plan

### Potential Risks

* Hash drift across interpreters
* Coverage regression
* Dependency transient break
* Toolchain version change affecting determinism
* Release tag created on wrong commit

### Rollback

If failure occurs:

1. Delete tag (if pushed)
2. Revert release commit
3. Restore `main` to prior green SHA
4. Open corrective milestone (M31-R1)

No weakening of gates permitted.

---

## 7. Deliverables

* `docs/milestones/M31/M31_plan.md`
* `docs/milestones/M31/M31_run1.md`
* `docs/milestones/M31/M31_audit.md`
* `docs/milestones/M31/M31_summary.md`
* `docs/milestones/M31/M31_toolcalls.md`
* Annotated tag `v1.0.0`
* GitHub Release artifact
* CI run evidence

---

## 8. Exit Criteria

M31 closes only when:

* CI fully green on release commit
* Hermetic hashes match across 3.10/3.11/3.12 (and match M29 baseline)
* Determinism verified
* Coverage unchanged
* Security unchanged
* Required checks unchanged
* Tag exists and verified
* GitHub Release published
* Audit + summary generated

---

## 9. Final Outcome

After M31:

* EZRA is no longer "phase-complete"
* EZRA becomes **v1.0.0 — Enterprise-Certified Release**
* EPB contract becomes semantically versioned
* Future work requires v1.x or v2.0 milestone framing
* Governance resets from "refactor hardening" to "stable product evolution"
