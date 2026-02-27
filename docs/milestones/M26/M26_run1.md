# M26 Run 1 — CI / Workflow Run Analysis

**Milestone:** M26 — EPB Artifact Signing & Verification (Detached Ed25519)  
**Posture:** Behavior-preserving (additive tooling only; no schema/emission changes)  
**Run type:** Initial implementation + CI verification

---

## 1. Workflow identity

| Field        | Value |
|-------------|--------|
| Workflow    | CI (`.github/workflows/ci.yml`) |
| Run ID      | **22479170028** |
| URL         | https://github.com/m-cahill/ezra/actions/runs/22479170028 |
| Trigger     | pull_request |
| Branch      | `m26-epb-artifact-signing` |
| PR          | **#27** (m-cahill/ezra#27) |
| Conclusion  | failure (Security Check failed; fix applied) |
| Duration    | ~1m 22s |

---

## 2. Change context

- **Objective:** Add detached Ed25519 signing (`epb_sign.py`) and verification (`epb_verify.py`) over canonical bundle hash; stdlib + cryptography only; default `bundle.sig`; ephemeral key by default, optional `--private-key`.
- **Refactor target surface:** `src/ezra/tools/` (new modules), `tests/contracts/`, CI Test job.
- **Invariants:** EPB structure (M24), determinism (M24/M25), artifact self-consistency (M25), consumer-isolated validation (both tools stdlib+cryptography only), CI truthfulness.

---

## 3. Local verification (pre-CI)

| Check | Result | Notes |
|-------|--------|------|
| Pytest (all) | 268 passed, 4 skipped | +6 tests in `test_epb_artifact_signing.py` |
| Coverage | 95.70% (≥85%) | Tools omitted by config; unchanged vs M25 |
| Ruff (lint) | Pass | `ruff check . --no-fix` |
| Ruff (format) | Pass | `ruff format --check .` |
| Mypy | Pass | `mypy src` |
| Public surface freeze | Pass | Snapshot includes `ezra.tools.epb_sign`, `ezra.tools.epb_verify`, `ezra.tools._epb_hash` |

---

## 4. Jobs / checks (CI Run 22479170028)

| Job / Check | Required? | Result | Notes |
|-------------|-----------|--------|-------|
| Lint | Yes | ✓ Pass | |
| Type Check | Yes | ✓ Pass | |
| Test | Yes | ✓ Pass | 268 passed, 4 skipped; EPB Artifact Signing step ran |
| Security Check | Yes | ✗ Fail | Gitleaks: 2 findings (false positive — see below) |
| SBOM Generation | Yes | ✓ Pass | |
| Complexity Check | Yes | ✓ Pass | |
| Determinism Check | Yes | ✓ Pass | |
| Documentation Build | Yes | ✓ Pass | |
| Dependency Review | continue-on-error | ✗ Fail | SEC-001 (repo/org config; not blocking) |
| OpenSSF Scorecard | continue-on-error | ✓ Pass | |
| SLSA Provenance | Conditional (push/tag) | Skipped | PR trigger |
| Documentation Deploy | Conditional (push/main) | Skipped | PR trigger |

**EPB Artifact Signing step (inside Test job):** Ran successfully (sign_pass, verify_pass, tamper_detection).

---

## 5. Security Check failure (Run 1)

**Cause:** Gitleaks rule `generic-api-key` flagged the variable name `private_key` in `src/ezra/tools/epb_sign.py` (lines 40 and 107) as a potential secret. This is a **false positive**: the identifier is a Python variable holding an Ed25519 key object, not a literal API key or secret.

**Findings:**
- File: `src/ezra/tools/epb_sign.py`, Line 40: `private_key: Ed25519PrivateKey | None = None` (function parameter)
- File: `src/ezra/tools/epb_sign.py`, Line 107: `private_key: Ed25519PrivateKey | None = None` (local variable in main)

**Fix applied:** Renamed the parameter and local variable to `signing_key` in `epb_sign.py` and updated all call sites (including tests) to use `signing_key=`. CLI flag remains `--private-key` (user-facing). No behavior change.

---

## 6. Delta summary

| Item | Delta |
|------|--------|
| New files | `src/ezra/tools/_epb_hash.py`, `epb_sign.py`, `epb_verify.py`, `tests/contracts/test_epb_artifact_signing.py`, `docs/milestones/M26/*` |
| Modified | `pyproject.toml`, `.github/workflows/ci.yml`, `docs/baselines/public_surface_snapshot.json` |
| Test count | 262 → 268 (+6) |
| Coverage (CI) | **95.70%** (tools omitted; matches M25) |
| Post-fix | `epb_sign.py`, `test_epb_artifact_signing.py` (gitleaks false-positive rename) |

---

## 7. Verdict

**Run 1:** CI run 22479170028 completed with **one required-job failure** (Security Check — gitleaks false positive on variable name `private_key`). All other 8/9 required checks passed. Dependency Review failure is known infra (SEC-001), non-blocking.

**Fix:** Variable renamed to `signing_key` in `epb_sign.py` and tests; committed and pushed to branch. CI re-run expected to pass Security Check.

**Outcome:** ✅ **Fix applied; re-run pending.** After green CI, proceed to M26_audit.md, M26_summary.md, and closeout.

---

## 8. Exit criteria (M26)

| Criterion | Status |
|-----------|--------|
| Sign + verify works | Yes (tests + local) |
| Tamper detection fails verification | Yes |
| Wrong-key fails verification | Yes |
| CI 9/9 required checks passing | Pending re-run after gitleaks fix |
| Coverage unchanged or improved | ✅ 95.70% (unchanged) |
| No invariant drift | Yes |

---

**CI run ID:** 22479170028  
**PR:** #27  
**Coverage (CI):** 95.70%
