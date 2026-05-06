# M36_plan — Audit Reconciliation & Public Release Boundary Inventory

## Milestone

**Milestone ID:** M36  
**Name:** Audit Reconciliation & Public Release Boundary Inventory  
**Refactor Posture:** Behavior-preserving (evidence and documentation only)  
**Primary Objective:** Reconcile the M33/Post-M32 audit score against the M35/current audit before any remediation work begins.

---

## 1. Intent / Target

EZRA has two materially different full-audit scores:

- M33/Post-M32 audit: **4.95 / 5.0** (`docs/M33fullaudit.md`).
- M35/current audit: **4.40 / 5.0** (external planning artifact; not committed in M36).

This milestone determines whether the score drop reflects:

1. actual project regression,
2. audit calibration drift,
3. stricter public-release-readiness criteria,
4. missing evidence,
5. or issues that should be addressed in M37/M38.

**M36 must not fix** audit findings. It reconciles evidence and inventories the public-release secret boundary.

---

## 2. Detected Surfaces & Constraints

### Project Shape

- Python package under `src/ezra/`.
- Tests under `tests/`.
- CI under `.github/workflows/`.
- Governance under `docs/`.

### Public / Consumer Surfaces (unchanged in M36)

- Python import surfaces.
- EPB v1.0.0 schemas and serialized artifact formats.
- CLI behavior, if any exists.
- CI enforcement contracts.
- Public docs outside the new reconciliation artifact.

### Company Secret Boundary (inventory only in M36)

Approved paths for **later** M37 cleanup:

- `.cursorrules`
- `docs/enhancements/`
- `docs/prompts/`

M36 **does not** remove, rename, redact, or `.gitignore` these paths.

---

## 3. Scope Boundaries

### In Scope

- Create audit reconciliation document: `docs/release/AUDIT_RECONCILIATION_M33_M35.md`.
- Compare scoring category by category.
- Classify score delta (regression vs calibration vs polish).
- Inventory tracked paths via `git ls-files .cursorrules docs/enhancements docs/prompts`.
- Record diff context `23789314ba5f6a502c650f6a098f12eb4ed0e8b4..HEAD`.
- Create / update `REFACTOR.md` (refactor ledger).
- Create M37 folder stubs.
- Run local verification; record results in `M36_run1.md`.
- Closeout: `M36_summary.md`, `M36_audit.md`.

### Out of Scope

- No code, CI, dependency, schema, `.gitignore`, or secret-cleanup changes.
- No copying external M35 audit file into repo.
- No new `docs/refactor/prompts/` tree in M36.

---

## 4. Invariants

See `REFACTOR.md` and `docs/release/AUDIT_RECONCILIATION_M33_M35.md` for verification. M36 must not touch `src/ezra/**`, EPB specs, workflows, or dependencies.

---

## 5. Verification Plan

Recorded in `M36_run1.md`:

- `git status --short`
- `git rev-parse HEAD`
- `git ls-files .cursorrules docs/enhancements docs/prompts`
- `git diff --stat 23789314ba5f6a502c650f6a098f12eb4ed0e8b4..HEAD`
- `git diff --name-only 23789314ba5f6a502c650f6a098f12eb4ed0e8b4..HEAD`
- `ruff check .`, `ruff format --check .`, `mypy src`, `pytest`

---

## 6. Deliverables

- `docs/milestones/M36/M36_plan.md` (this file)
- `docs/milestones/M36/M36_run1.md`
- `docs/release/AUDIT_RECONCILIATION_M33_M35.md`
- `REFACTOR.md`
- `docs/milestones/M37/M37_plan.md`
- `docs/milestones/M37/M37_toolcalls.md`
- `docs/milestones/M36/M36_summary.md`
- `docs/milestones/M36/M36_audit.md`

---

## 7. Acceptance Criteria

See `M36_audit.md` checklist mirror. Closure verdict targets **Closed — Proceed to M37** when only allowed documentation paths are modified.

---

## 8. Risk & Rollback

Rollback: `git restore` on `REFACTOR.md`, `docs/release/AUDIT_RECONCILIATION_M33_M35.md`, `docs/milestones/M36/**`, `docs/milestones/M37/**`, and `docs/ezra.md` if updated.
