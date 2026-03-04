# M32 Run 1 — CI Workflow Analysis

**Milestone:** M32 — Reproducible Distribution Baseline  
**Workflow:** CI  
**Run ID:** 22654032205  
**Trigger:** pull_request (PR #33)  
**Branch:** m32-reproducible-distribution  
**Commit:** 8b7dee3 (docs(M32): add M32_run1, M32_audit, M32_summary, toolcalls)

---

## 1. Workflow Identity

| Field | Value |
|-------|--------|
| Workflow name | CI |
| Run ID | 22654032205 |
| Trigger | pull_request |
| Branch | m32-reproducible-distribution |
| PR | #33 |
| Run URL | https://github.com/m-cahill/ezra/actions/runs/22654032205 |
| Head SHA | 8b7dee3f8a7264bb55a8048e469837f9c3d7f571 |

---

## 2. Change Context

| Field | Value |
|-------|--------|
| Milestone | M32 — Reproducible Distribution Baseline |
| Declared intent | Lockfile (pip-compile → requirements.txt), all critical actions pinned to full SHA, one-sentence doc update §8; no runtime or EPB changes |
| Refactor target surface | `.github/workflows/ci.yml` (install steps + action refs), `requirements.txt` (new), `docs/ezra.md` (§8) |
| Posture | Behavior-preserving (packaging + governance only) |
| Run type | Hardening |

---

## 3. Baseline Reference

- **Last trusted green:** main @ 027ef9c (M32 plan + ezra.md 7A + M31 full audit); M31 release tag v1.0.0; CI Run 22509645140.
- **M29/M31 hermetic baseline hash:** `c186777c33b7b7b9d11540bda7398efd0dfb085143506513a4ce87836c6ac7c2`. M32 does not change hashing/canonicalization; hermetic matrix uses same fixture → hash must remain unchanged.
- **Declared invariants:** EPB schema, canonicalization, hashing, signing, plugin interfaces, zone registry format, CI thresholds, coverage 85%, determinism checks, hermetic reproducibility logic — all unchanged.

---

## Step 1 — Workflow Inventory

| Job / Check | Required? | Purpose | Pass/Fail | Notes |
|-------------|------------|---------|-----------|-------|
| Lint | Yes | Ruff + Pydocstyle; install from requirements.txt | Pass | 27s |
| Type Check | Yes | Mypy; install from requirements.txt | Pass | 30s |
| EPB Tools Minimal Environment | Yes | Install from requirements.txt + pip install -e . | Pass | 23s |
| Test | Yes | Pytest, coverage ≥85%, zone/EPB contract steps | Pass | 49s |
| Security Check | Yes | Bandit, pip-audit, gitleaks | Pass | 32s |
| SBOM Generation | Yes | CycloneDX; install from requirements.txt | Pass | 37s |
| Complexity Check | Yes | Radon; install from requirements.txt | Pass | 28s |
| Determinism Check | Yes | Triple-run byte-identical bundles | Pass | 31s |
| Hermetic Hash (Py 3.10) | Yes | Per-version canonical bundle hash | Pass | 8s |
| Hermetic Hash (Py 3.11) | Yes | Per-version canonical bundle hash | Pass | 6s |
| Hermetic Hash (Py 3.12) | Yes | Per-version canonical bundle hash | Pass | 8s |
| Hermetic Reproducibility | Yes | Cross-matrix hash comparison | Pass | 5s |
| Documentation Build | Yes | Sphinx; install from requirements.txt | Pass | 33s |
| Dependency Review | continue-on-error | SEC-001; infra (GHAS) | Fail | Non-blocking; "Dependency graph / Advanced Security" not enabled |
| OpenSSF Scorecard | continue-on-error | Informational | Pass | 9s |
| SLSA Provenance | Conditional | push main/tags | Skipped | PR trigger |
| Documentation Deploy | Conditional | push main | Skipped | PR trigger |

All required (merge-blocking) checks passed. No new checks added or removed. No silent weakening. All actions use full SHA.

---

## Step 2 — Refactor Signal Integrity

### A) Tests

- No test code or emission logic changed. Install path only. All unit/contract/schema/registry/EPB steps run unchanged; dependency set is locked → identical graph.

### B) Coverage

- Coverage gate (≥85%) must remain satisfied. Local run: 85.54%. No code changes; no exclusion changes.

### C) Static / Policy Gates

- Lint, typecheck, complexity, docs build: same commands; only install uses lockfile.

### D) Security / Supply Chain

- Same security steps; install from lockfile. Actions pinned to SHA (supply-chain hardening).

### E) Performance / Benchmarks

- N/A.

---

## Step 3 — Delta Analysis

**Change inventory:**
- `requirements.txt` — new (pip-compile from pyproject.toml --extra dev)
- `.github/workflows/ci.yml` — all jobs that install: use `pip install -r requirements.txt` + `pip install -e .`; all action refs changed from tags to full SHA
- `docs/ezra.md` — §8: one sentence added (parity/integration skip unless env vars set)

**Expected vs observed:**
- Expected: CI green; hermetic hash unchanged; determinism unchanged; coverage unchanged; no EPB/schema drift.
- Observed: All required jobs passed. Hermetic Reproducibility passed (all three Python versions produced identical canonical bundle hash). Determinism Check passed. Lockfile install path used successfully in every job that installs the project. No signal drift.

---

## Step 4 — Failure Analysis

**Dependency Review:** Failed with "Dependency review is not supported on this repository. Please ensure that Dependency graph is enabled along with GitHub Advanced Security." This is infrastructure/settings (SEC-001); the job has `continue-on-error: true` and is documented as non-blocking. Not in scope for M32; no code or workflow fix required for merge.

---

## Step 5 — Invariants & Guardrails Check

| Guardrail | Status |
|-----------|--------|
| Required checks enforced | Yes; all required jobs passed |
| No scope expansion | Yes; packaging + doc + workflow only |
| Public surfaces / EPB / schema | Yes; no code change |
| Determinism / hermetic | Yes; Determinism Check passed; Hermetic Reproducibility passed (hash unchanged) |
| No green-but-misleading | Yes; no new skips or continue-on-error on required checks |

All invariants held. No violation.

---

## Step 6 — Verdict

**Verdict:** Safe to merge. Run 22654032205 confirms M32 is behavior-preserving: lockfile and action SHA pinning in place; all required checks passed; determinism and hermetic reproducibility passed; no coverage or contract drift. Dependency Review failure is known infra (GHAS); non-blocking.

**Recommended outcome:** ✅ Merge approved (subject to express permission per .cursorrules).

---

## Step 7 — Next Actions

| Owner | Action | Scope | Milestone |
|-------|--------|-------|-----------|
| Human | Merge PR #33 after express permission (merge commit per preference) | main | M32 closeout |
| Human/Cursor | Update docs/ezra.md §7 milestone table when M32 is closed | docs/ezra.md | M32 closeout |

---

## CI Run Reference

- **Run ID:** 22654032205  
- **URL:** https://github.com/m-cahill/ezra/actions/runs/22654032205  
- **Conclusion:** success  
- **Status:** completed  

---

## Hermetic Reproducibility (M32)

- Hermetic Hash (Py 3.10, 3.11, 3.12): all three jobs passed; Hermetic Reproducibility job passed (all matrix hashes identical).
- No code affecting `_to_canonical_json`, `_compute_file_hash`, or `_compute_bundle_hash_from_file_hashes` was changed in M32; canonical bundle hash for the fixed fixture remains `c186777c33b7b7b9d11540bda7398efd0dfb085143506513a4ce87836c6ac7c2`. Drift would have caused the comparison job to fail.
