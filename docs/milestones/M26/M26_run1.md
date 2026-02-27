# M26 Run 1 — Implementation + Local Verification

**Milestone:** M26 — EPB Artifact Signing & Verification (Detached Ed25519)  
**Posture:** Behavior-preserving (additive tooling only; no schema/emission changes)  
**Run type:** Initial implementation + local verification (CI run ID to be filled after PR)

---

## 1. Workflow identity

| Field        | Value |
|-------------|--------|
| Workflow    | CI (`.github/workflows/ci.yml`) |
| Run ID      | (Pending — PR not yet pushed) |
| Trigger     | pull_request (expected) |
| Branch      | `m26-epb-artifact-signing` |
| PR          | (To be opened) |
| Conclusion  | (Pending CI) |

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

## 4. Implementation summary

- **New files:** `src/ezra/tools/_epb_hash.py`, `src/ezra/tools/epb_sign.py`, `src/ezra/tools/epb_verify.py`, `tests/contracts/test_epb_artifact_signing.py`, `docs/milestones/M26/M26_plan.md`, `M26_toolcalls.md`.
- **Modified:** `pyproject.toml` (cryptography==46.0.5), `.github/workflows/ci.yml` (EPB Artifact Signing step + summary), `docs/baselines/public_surface_snapshot.json`.
- **Tests:** Sign+verify roundtrip, subprocess sign/verify, tamper fails, wrong public key fails, sign with provided key, sign fails on invalid path.

---

## 5. Next actions

- Push branch, open PR to main.
- After CI run: record Run ID and conclusion in this document; generate M26_audit.md and M26_summary.md after green; update docs/ezra.md at closeout.

---

**CI run ID:** (To be filled)  
**PR:** (To be opened)
