# M36 Merge Record

| Field | Value |
| --- | --- |
| **PR** | https://github.com/m-cahill/ezra/pull/37 |
| **Branch** | `docs/m36-audit-reconciliation` |
| **Final head SHA (pre-squash tip)** | `3f5647adcf8dc77f4e8c3f060cd6c4eec75fe100` |
| **Merge SHA (`main`)** | `969471060c0ad9b528836209531a023c098e5a4e` |
| **Merge date** | 2026-05-06 (UTC, per GitHub `mergedAt`) |
| **Merge method** | Squash merge |
| **Post-merge CI (`main`)** | https://github.com/m-cahill/ezra/actions/runs/25466391573 — workflow **`conclusion: failure`** (same non-M36 failure class as PR runs). |

## Required checks at merge (GitHub)

- **`mergeable`:** MERGEABLE; **`mergeStateStatus`:** UNSTABLE on the PR while open.
- **REST branch protection** (`GET .../branches/main/protection`): **404 — "Branch not protected"** for this repo at merge time—i.e. no classic required-status API surfaced; merge was **not mechanically blocked** by GitHub despite failing jobs.
- Maintainers must still treat failing jobs as **release and supply-chain risk** even when merge is allowed.

## Remaining red checks (PR last run / representative)

At merge/decision time, these jobs **failed** and were **not** caused by M36 docs:

| Check | Cause (triage) |
| --- | --- |
| Dependency Review | GHAS / dependency graph not available on repo. |
| Distribution Verification | HTTP 401 on artifact download (`GITHUB_TOKEN` / permissions). |
| Security Check | Pre-existing `pip-audit` findings in committed lockfile. |

**Passing** substantive gates included: Lint, Type Check, Smoke Tests, Test, EPB Tools Minimal Environment, SBOM, Complexity, Determinism, Hermetic matrix + reproducibility, Documentation Build.

## Rationale

M36 changed **only** documentation and governance artifacts (`REFACTOR.md`, `docs/ezra.md`, `docs/milestones/M36/*`, `docs/milestones/M37/*` stubs, `docs/release/AUDIT_RECONCILIATION_M33_M35.md`). No `src/ezra/**`, EPB specs, workflows, dependencies, `.gitignore`, or secret cleanup. Failures above are **pre-existing / infrastructure / supply-chain**, per `docs/milestones/M36/M36_pr1_ci_triage.md`.

## Authorized next milestone

- **M37 — Public Release Boundary Cleanup** is authorized to proceed from a **governance** perspective (M36 merged to `main`).
- **Recommendation:** Run a **narrow required-gate recovery** milestone (see `REFACTOR.md` / maintainer plan—e.g. **M37A**) **before** declaring **public-release CI green**, so future PRs (including M37) are not repeatedly **UNSTABLE** for the same reasons. M37 secret-path work does not fix `pip-audit` or Distribution Verification.

## Artifacts

- Triage: `docs/milestones/M36/M36_pr1_ci_triage.md`
- This record: `docs/milestones/M36/M36_merge.md`
