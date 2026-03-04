# M33 Run 2 — CI Workflow Analysis

**Milestone:** M33 — Reproducible Distribution Artifacts & Trusted Publishing  
**Workflow:** CI  
**Run ID:** 22655694366  
**Trigger:** pull_request (PR #34)  
**Branch:** m33-reproducible-artifacts  
**Commit:** 3f81105 (M33 polish: dev tooling alignment, CI guardrails doc, README improvements)

---

## 1. Workflow Identity

| Field | Value |
|-------|--------|
| Workflow name | CI |
| Run ID | 22655694366 |
| Trigger | pull_request |
| Branch | m33-reproducible-artifacts |
| PR | #34 |
| Run URL | https://github.com/m-cahill/ezra/actions/runs/22655694366 |
| Head SHA | 3f811052e4a2f707aac0045d6a4c7cc0c34341f4 |

---

## 2. Change Context

| Field | Value |
|-------|--------|
| Milestone | M33 — Reproducible Distribution Artifacts & Trusted Publishing |
| Declared intent | M33 polish: pre-commit mypy aligned with CI; coverage guardrail doc; smoke-tests job; README Quickstart/Architecture/Development Workflow |
| Refactor target surface | `.pre-commit-config.yaml`, `docs/CI_ARCHITECTURE.md`, `.github/workflows/ci.yml` (smoke-tests job), `README.md`, `tests/test_public_surface_freeze.py` (import order) |
| Posture | Behavior-preserving (documentation, dev tooling, CI polish only) |
| Run type | Hardening |

---

## 3. Baseline Reference

- **Previous run:** M33 Run 1 (22654936020) — release workflow + quick wins; all required checks passed.
- **This run:** First CI run after M33 polish commit (smoke-tests job added; no threshold or runtime changes).
- **Declared invariants:** EPB schema, canonicalization, hashing, signing, plugin interfaces, zone registry format, coverage 85%, determinism checks, hermetic reproducibility logic — all unchanged.

---

## Step 1 — Workflow Inventory

| Job / Check | Required? | Purpose | Pass/Fail | Notes |
|-------------|------------|---------|-----------|-------|
| Lint | Yes | Ruff + Pydocstyle | Pass | — |
| Type Check | Yes | Mypy | Pass | — |
| EPB Tools Minimal Environment | Yes | EPB tools isolation tests | Pass | — |
| **Smoke Tests** | **Yes** | **test_smoke.py + test_epb_contract.py (fast)** | **Pass** | **New job; no coverage** |
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

All required (merge-blocking) checks passed. **Smoke Tests** is a new required job; full Test job unchanged (coverage, schema, registry, EPB steps). No threshold weakening.

---

## Step 2 — Refactor Signal Integrity

### A) Tests

- Smoke Tests job runs a subset (test_smoke + test_epb_contract) for faster feedback; full Test job unchanged. No runtime or EPB logic changed; test_public_surface_freeze import order only (ruff E402).

### B) Coverage

- Coverage gate (≥85%) enforced in Test job only; Smoke Tests does not run coverage. No change to threshold or exclusions.

### C) Static / Policy Gates

- Lint, typecheck, complexity, docs build: unchanged. Pre-commit mypy config change is local-only (aligns with CI).

### D) Security / Supply Chain

- Unchanged. Smoke job uses same checkout/setup-python SHAs and install path.

### E) Performance / Benchmarks

- Smoke Tests intended &lt;60s; does not replace or weaken full test gate.

---

## Step 3 — Delta Analysis

**Change inventory (Run 2 vs Run 1):**

- `.pre-commit-config.yaml` — mypy hook: rev v1.10.0, args `--config-file=pyproject.toml`; removed override flags.
- `docs/CI_ARCHITECTURE.md` — Coverage Guardrail subsection (fail_under=85, margin policy).
- `.github/workflows/ci.yml` — new smoke-tests job (before test).
- `README.md` — Quickstart, Architecture, Development Workflow sections.
- `tests/test_public_surface_freeze.py` — imports moved to top (E402).

**Expected vs observed:**

- Expected: All required jobs pass including new Smoke Tests; full Test job and determinism/hermetic unchanged.
- Observed: All required jobs passed. Smoke Tests passed. No signal drift.

---

## Step 4 — Failure Analysis

**Dependency Review:** Failed (Dependency review not supported / Dependency graph not enabled). Same as Run 1; infrastructure (SEC-001); job has `continue-on-error: true`. Not blocking.

No other failures.

---

## Step 5 — Invariants & Guardrails Check

| Guardrail | Status |
|-----------|--------|
| Required checks enforced | Yes; all required jobs passed including Smoke Tests |
| No scope expansion | Yes; docs, tooling, one new fast job only |
| Public surfaces / EPB / schema | Yes; no runtime/EPB/code logic change |
| Determinism / hermetic | Yes; Determinism Check and Hermetic Reproducibility passed |
| No green-but-misleading | Yes; no new skips or continue-on-error on required checks |
| Coverage threshold | Yes; still 85%; Smoke Tests does not enforce coverage |

All invariants held.

---

## Step 6 — Verdict

**Verdict:** Run 22655694366 confirms M33 polish is behavior-preserving: pre-commit mypy aligned with CI, coverage guardrail documented, smoke-tests job added and passing, README improved. All required checks passed; determinism and hermetic reproducibility passed. Safe to merge.

**Recommended outcome:** ✅ Merge approved (subject to express permission per .cursorrules).

---

## Step 7 — Next Actions

| Owner | Action | Scope | Milestone |
|-------|--------|-------|-----------|
| Human | Merge PR #34 after express permission | main | M33 closeout |
| Human/Cursor | Update docs/ezra.md §7 milestone table when M33 is closed | docs/ezra.md | M33 closeout |

---

## CI Run Reference

- **Run ID:** 22655694366  
- **URL:** https://github.com/m-cahill/ezra/actions/runs/22655694366  
- **Conclusion:** success  
- **Status:** completed  

---

## Run 2 vs Run 1

| Aspect | Run 1 (22654936020) | Run 2 (22655694366) |
|--------|---------------------|----------------------|
| Commit | f1198db (release + quick wins) | 3f81105 (polish) |
| Smoke Tests job | Not present | Added, passed |
| Required job count | 14 | 15 |
| All required passed | Yes | Yes |
