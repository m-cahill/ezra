# M33 Run 1 — CI Workflow Analysis

**Milestone:** M33 — Reproducible Distribution Artifacts & Trusted Publishing  
**Workflow:** CI  
**Run ID:** 22654936020  
**Trigger:** pull_request (PR #34)  
**Branch:** m33-reproducible-artifacts  
**Commit:** f1198db (M33: Reproducible distribution artifacts and trusted publishing)

---

## 1. Workflow Identity

| Field | Value |
|-------|--------|
| Workflow name | CI |
| Run ID | 22654936020 |
| Trigger | pull_request |
| Branch | m33-reproducible-artifacts |
| PR | #34 |
| Run URL | https://github.com/m-cahill/ezra/actions/runs/22654936020 |
| Head SHA | f1198db16bd33474b0280ab28b0add551dcc474b |

---

## 2. Change Context

| Field | Value |
|-------|--------|
| Milestone | M33 — Reproducible Distribution Artifacts & Trusted Publishing |
| Declared intent | Add release workflow (tag v* → build sdist/wheel, hashes, SBOM, provenance, PyPI via OIDC); add PyPI Trusted Publishing doc; no runtime or EPB changes |
| Refactor target surface | `.github/workflows/release.yml` (new), `docs/release/PYPI_TRUSTED_PUBLISHING.md` (new) |
| Posture | Behavior-preserving (packaging + release automation only) |
| Run type | Hardening |

---

## 3. Baseline Reference

- **Last trusted green:** main after M32 (lockfile, action SHA pinning); M31 v1.0.0; CI Run 22654378419 (M32).
- **M33 scope:** New release workflow runs only on `push: tags: v*`; CI workflow unchanged. No code, pyproject.toml, or lockfile changes.
- **Declared invariants:** EPB schema, canonicalization, hashing, signing, plugin interfaces, zone registry format, CI thresholds, coverage 85%, determinism checks, hermetic reproducibility logic — all unchanged (no code touched).

---

## Step 1 — Workflow Inventory

| Job / Check | Required? | Purpose | Pass/Fail | Notes |
|-------------|------------|---------|-----------|-------|
| Lint | Yes | Ruff + Pydocstyle | Pass | — |
| Type Check | Yes | Mypy | Pass | — |
| EPB Tools Minimal Environment | Yes | EPB tools isolation tests | Pass | — |
| Test | Yes | Pytest, coverage ≥85% | Pass | — |
| Security Check | Yes | Bandit, pip-audit, gitleaks | Pass | — |
| SBOM Generation | Yes | CycloneDX | Pass | — |
| Complexity Check | Yes | Radon | Pass | — |
| Determinism Check | Yes | Triple-run byte-identical bundles | Pass | — |
| Hermetic Hash (Py 3.10) | Yes | Per-version canonical bundle hash | Pass | — |
| Hermetic Hash (Py 3.11) | Yes | Per-version canonical bundle hash | Pass | — |
| Hermetic Hash (Py 3.12) | Yes | Per-version canonical bundle hash | Pass | — |
| Hermetic Reproducibility | Yes | Cross-matrix hash comparison | Pass | — |
| Documentation Build | Yes | Sphinx | Pass | — |
| Dependency Review | continue-on-error | SEC-001; infra (GHAS) | Fail | Non-blocking; Dependency graph / Advanced Security not enabled |
| OpenSSF Scorecard | continue-on-error | Informational | Pass | — |
| SLSA Provenance | Conditional | push main/tags | Skipped | PR trigger |
| Documentation Deploy | Conditional | push main | Skipped | PR trigger |

**Release workflow:** Not run (expected). Release runs only on `push: tags: v*`; this was a PR run.

All required (merge-blocking) checks passed. No CI workflow changes; no new or removed checks; no weakening.

---

## Step 2 — Refactor Signal Integrity

### A) Tests

- No test or runtime code changed. New files are release workflow and docs only. All unit/contract/schema/registry/EPB steps ran unchanged.

### B) Coverage

- Coverage gate (≥85%) unchanged. No code changes; no exclusion changes.

### C) Static / Policy Gates

- Lint, typecheck, complexity, docs build: unchanged; no refactor target in application code.

### D) Security / Supply Chain

- Same security steps. New release workflow uses same action SHA-pinning policy; no secrets; OIDC only for PyPI.

### E) Performance / Benchmarks

- N/A.

---

## Step 3 — Delta Analysis

**Change inventory:**

- `.github/workflows/release.yml` — new (tag v* → build, hashes, SBOM, provenance, publish to PyPI via OIDC).
- `docs/release/PYPI_TRUSTED_PUBLISHING.md` — new (PyPI project creation, Trusted Publishing, GitHub environment).
- `docs/milestones/M33/M33_toolcalls.md` — updated (tool call log).

**Expected vs observed:**

- Expected: CI green (no CI workflow or code change); Release workflow not triggered on PR.
- Observed: All required CI jobs passed. Hermetic Reproducibility passed. No signal drift. Release workflow correctly does not run on PR.

---

## Step 4 — Failure Analysis

**Dependency Review:** Failed (Dependency review not supported / Dependency graph not enabled). Same as M32; infrastructure (SEC-001); job has `continue-on-error: true`. Not in scope for M33; no fix required for merge.

No other failures.

---

## Step 5 — Invariants & Guardrails Check

| Guardrail | Status |
|-----------|--------|
| Required checks enforced | Yes; all required jobs passed |
| No scope expansion | Yes; release workflow + doc only; no runtime/EPB/code change |
| Public surfaces / EPB / schema | Yes; untouched |
| Determinism / hermetic | Yes; Determinism Check and Hermetic Reproducibility passed |
| No green-but-misleading | Yes; no new skips or continue-on-error on required checks |

All invariants held.

---

## Step 6 — Verdict

**Verdict:** Run 22654936020 confirms M33 is behavior-preserving: new release workflow and PyPI doc only; CI unchanged; all required checks passed; determinism and hermetic reproducibility passed. Release workflow will run only on tag push (not validated in this run; to be validated when a tag is pushed). Safe to merge.

**Recommended outcome:** ✅ Merge approved (subject to express permission per .cursorrules).

---

## Step 7 — Next Actions

| Owner | Action | Scope | Milestone |
|-------|--------|-------|-----------|
| Human | Merge PR #34 after express permission | main | M33 closeout |
| Human/Cursor | Update docs/ezra.md §7 milestone table when M33 is closed | docs/ezra.md | M33 closeout |
| Human | Configure PyPI per docs/release/PYPI_TRUSTED_PUBLISHING.md when ready to publish | PyPI / GitHub | Post-merge |
| Human | Optional: push a tag (e.g. v1.0.1) to validate Release workflow end-to-end | repo | Post-merge |

---

## CI Run Reference

- **Run ID:** 22654936020  
- **URL:** https://github.com/m-cahill/ezra/actions/runs/22654936020  
- **Conclusion:** success  
- **Status:** completed  

---

## M33 Scope Reminder

- **Release workflow** runs only on `push: tags: v*`. This run exercised CI only; Release (build, SBOM, provenance, PyPI publish) will run when a version tag is pushed.
- **No code, pyproject.toml, or lockfile changes.** Packaging and release automation only.
