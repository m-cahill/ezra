# M32 Run 1 — CI Workflow Analysis

**Milestone:** M32 — Reproducible Distribution Baseline  
**Workflow:** CI  
**Run ID:** *Pending — PR #33*  
**Trigger:** pull_request (PR #33)  
**Branch:** m32-reproducible-distribution  
**Commit:** 6bcc84f (M32: Reproducible distribution baseline — lockfile, action SHA pinning, doc env-var)

---

## 1. Workflow Identity

| Field | Value |
|-------|--------|
| Workflow name | CI |
| Run ID | *To be filled after first workflow run* |
| Trigger | pull_request |
| Branch | m32-reproducible-distribution |
| PR | #33 |
| Run URL | *To be filled* |
| Head SHA | 6bcc84f |

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

## Step 1 — Workflow Inventory (Expected)

| Job / Check | Required? | Purpose | Pass/Fail | Notes |
|-------------|------------|---------|-----------|-------|
| Lint | Yes | Ruff + Pydocstyle; install from requirements.txt | *Pending* | Install step changed |
| Type Check | Yes | Mypy; install from requirements.txt | *Pending* | Install step changed |
| EPB Tools Minimal Environment | Yes | Install from requirements.txt + pip install -e . | *Pending* | Install step changed |
| Test | Yes | Pytest, coverage ≥85%, zone/EPB contract steps | *Pending* | Install step changed |
| Security Check | Yes | Bandit, pip-audit, gitleaks | *Pending* | Install step changed |
| SBOM Generation | Yes | CycloneDX; install from requirements.txt | *Pending* | Install step changed |
| Complexity Check | Yes | Radon; install from requirements.txt | *Pending* | Install step changed |
| Determinism Check | Yes | Triple-run byte-identical bundles | *Pending* | Install step changed |
| Hermetic Hash (Py 3.10/3.11/3.12) | Yes | Per-version canonical bundle hash | *Pending* | No install change in matrix; hash must match baseline |
| Hermetic Reproducibility | Yes | Cross-matrix hash comparison | *Pending* | Must pass |
| Documentation Build | Yes | Sphinx; install from requirements.txt | *Pending* | Install step changed |
| Dependency Review | continue-on-error | SEC-001; infra | *Pending* | Non-blocking |
| OpenSSF Scorecard | continue-on-error | Informational | *Pending* | Non-blocking |
| SLSA Provenance | Conditional | push main/tags | Skipped on PR | — |
| Documentation Deploy | Conditional | push main | Skipped on PR | — |

All actions in CI now use full SHA (checkout, setup-python, upload-artifact, download-artifact, attest-build-provenance, upload-pages-artifact, deploy-pages, dependency-review-action, gitleaks-action, scorecard-action).

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

**Expected vs observed (after run):**
- Expected: CI green; hermetic hash unchanged; determinism unchanged; coverage unchanged; no EPB/schema drift.
- Observed: *To be filled after Run 1 completes.*

---

## Step 4 — Failure Analysis

*To be filled if any job fails.*

---

## Step 5 — Invariants & Guardrails Check

| Guardrail | Status (pre-run) |
|-----------|------------------|
| Required checks enforced | No threshold or check removed |
| No scope expansion | Packaging + doc + workflow only |
| Public surfaces / EPB / schema | No code change |
| Determinism / hermetic | Logic unchanged; hash must match M31 baseline |
| No green-but-misleading | No new skips or continue-on-error on required checks |

*Final status after Run 1: to be confirmed.*

---

## Step 6 — Verdict

*To be set after CI Run 1.*  
**Interim:** Local ruff, mypy, pytest (253 passed, 28 skipped), coverage 85.54%; hermetic hash `c186777c33b7b7b9d11540bda7398efd0dfb085143506513a4ce87836c6ac7c2` (unchanged).

---

## Step 7 — Next Actions

| Owner | Action | Scope | Milestone |
|-------|--------|-------|-----------|
| Human/Cursor | Update this document with Run ID, URL, and per-job Pass/Fail after workflow completes | M32_run1.md | M32 |
| Human | Merge PR #33 after CI green (with permission) | main | M31 closeout rules |
| Cursor/Human | Finalize M32_audit.md, M32_summary.md; update M32_toolcalls.md | docs/milestones/M32/ | M32 closeout |

---

## CI Run Reference (To Be Filled)

- **Run ID:** —
- **URL:** —
- **Conclusion:** —
- **Status:** —

---

## Hermetic Reproducibility (M32)

- No code affecting `_to_canonical_json`, `_compute_file_hash`, or `_compute_bundle_hash_from_file_hashes` was changed. Hermetic matrix job does not use the lockfile (it uses PYTHONPATH=src and the same inline script). Expected hash: `c186777c33b7b7b9d11540bda7398efd0dfb085143506513a4ce87836c6ac7c2`. CI Hermetic Reproducibility job must pass (all three Python versions identical).
