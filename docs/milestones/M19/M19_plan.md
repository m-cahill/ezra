# M19 Plan — Post-Merge CI Integrity & Release Attestation Closure

**Milestone:** M19  
**Status:** In Progress  
**Baseline:** `v0.0.19-m18` (tag)  
**Type:** Stability-hardening (CI-only, no runtime changes)

---

## 1. Milestone Objective

Resolve the post-merge CI configuration failures introduced in M18 and formally close the release-attestation loop.

Specifically:

1. Fix **CI-001** — SLSA Provenance failure on main push
2. Fix **CI-002** — Documentation Deploy failure on main push
3. Ensure these jobs cannot silently regress (no `continue-on-error`)
4. Close deferred registry items CI-001 and CI-002

---

## 2. Scope Boundaries

### In Scope

- CI workflow configuration fixes (`.github/workflows/ci.yml`)
- SLSA Provenance: remove invalid `build-workflow-path` input, add `subject-path: dist/`
- Documentation Deploy: fix permissions (`id-token: write`, `pages: write`), fix artifact wiring (`upload-pages-artifact@v3`), add `environment: github-pages`
- Documentation Build: switch to `upload-pages-artifact@v3` for deploy pipeline
- Deferred registry updates (CI-001, CI-002 → Resolved)

### Out of Scope

- Runtime code changes
- API changes
- EPB changes
- Plugin changes
- Schema changes
- Test rewrites
- Coverage threshold changes
- Architecture refactors
- SEC-001 (GitHub Advanced Security) — remains deferred

---

## 3. Root Cause Analysis

### CI-001: SLSA Provenance

- **Error:** `One of subject-path or subject-digest must be provided`
- **Root Cause:** `actions/attest-build-provenance@v1` was given `subject-name: ezra` and an invalid input `build-workflow-path`. Neither `subject-path` nor `subject-digest` was provided. The build step produces `dist/*.whl` and `dist/*.tar.gz` but these were not passed to the attestation step.
- **Fix:** Remove `build-workflow-path`, add `subject-path: dist/` to attest all built artifacts.

### CI-002: Documentation Deploy

- **Error:** `Unable to get ACTIONS_ID_TOKEN_REQUEST_URL env variable` / `Ensure GITHUB_TOKEN has permission "id-token: write"`
- **Root Cause:** Two issues:
  1. The `docs-deploy` job only has `contents: write` permission. `actions/deploy-pages@v4` requires `id-token: write` and `pages: write`.
  2. `deploy-pages@v4` expects a `github-pages` artifact uploaded by `actions/upload-pages-artifact@v3`, but `docs-build` uses regular `actions/upload-artifact@v4` with name `docs-html`.
  3. The `docs-deploy` job unnecessarily rebuilds docs instead of consuming the build artifact.
- **Fix:**
  - Add `upload-pages-artifact@v3` step to `docs-build`
  - Fix `docs-deploy` permissions to `id-token: write` + `pages: write`
  - Add `environment: github-pages` to `docs-deploy`
  - Simplify `docs-deploy` to just deploy (remove redundant rebuild)

---

## 4. Invariants (Must Not Change)

| Surface | Verification |
|---------|-------------|
| 214 tests pass | CI |
| Coverage ≥ 85% | CI |
| Determinism preserved | Determinism job |
| EPB schema unchanged | Freeze test |
| Hash algorithm unchanged | Freeze test |
| Exception hierarchy unchanged | Freeze test |
| No new runtime imports | import-linter |
| No new coverage exclusions | coverage config |

If any invariant breaks → rollback immediately.

---

## 5. Implementation Steps

### Step 1 — Fix SLSA Provenance (CI-001)

In `.github/workflows/ci.yml`, provenance job:
- Remove `build-workflow-path: .github/workflows/ci.yml` (invalid input)
- Add `subject-path: dist/` to `actions/attest-build-provenance@v1`

### Step 2 — Fix Documentation Deploy (CI-002)

In `.github/workflows/ci.yml`:
- `docs-build` job: Add `actions/upload-pages-artifact@v3` step with `path: docs/_build/html`
- `docs-deploy` job:
  - Fix permissions: `pages: write`, `id-token: write`
  - Add `environment: github-pages`
  - Remove redundant build steps (checkout, python, sphinx, rebuild)
  - Keep only `actions/deploy-pages@v4` step

### Step 3 — Verify Guardrails

- Confirm no `continue-on-error` on provenance or docs-deploy jobs
- Confirm these jobs fail visibly on main if misconfigured

### Step 4 — Update Deferred Registry

- CI-001 → Resolved
- CI-002 → Resolved
- SEC-001 → Remains deferred

---

## 6. Risk & Rollback Plan

If fixes introduce instability:
- Revert workflow file
- Re-run baseline CI
- No runtime rollback required — CI-only changes

---

## 7. Exit Criteria

M19 is complete only if:

- [ ] SLSA Provenance job passes on main push
- [ ] Documentation Deploy job passes on main push (or fails only due to Pages not enabled in repo settings — acceptable known state)
- [ ] All 214 tests pass
- [ ] Coverage ≥ 85%
- [ ] Determinism intact
- [ ] No `continue-on-error` on provenance or docs-deploy
- [ ] Deferred registry updated (CI-001, CI-002 resolved)

---

## 8. Deliverables

- `docs/milestones/M19/M19_plan.md` (this document)
- `docs/milestones/M19/M19_toolcalls.md`
- `docs/milestones/M19/M19_run1.md`
- `docs/milestones/M19/M19_summary.md`
- `docs/milestones/M19/M19_audit.md`
- Updated `docs/ezra.md` milestone table
- Updated deferred registry
- Tag: `v0.0.20-m19`

---

**End of M19 Plan**
