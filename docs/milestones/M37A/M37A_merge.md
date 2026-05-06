# M37A Merge Record

| Field | Value |
| --- | --- |
| **PR** | https://github.com/m-cahill/ezra/pull/38 |
| **Branch** | `docs/m37a-required-gate-recovery-plan` |
| **Final head SHA (pre-squash tip)** | `cbde3dac495420760246c0df9d83f7b0548717de` |
| **Merge SHA (`main`)** | `266f398fb4a40cd5a4a4f700e3e02d6e77402a37` |
| **Merge date** | 2026-05-06 (UTC, per GitHub `mergedAt`) |
| **Merge method** | Squash merge |
| **Post-merge CI (`main`)** | https://github.com/m-cahill/ezra/actions/runs/25467827609 — `conclusion: failure` |
| **Remaining red checks** | **Security Check** (`pip-audit`); **Distribution Verification** (HTTP 401 artifact download); **SLSA Provenance** (attestation not available for user-owned private repo); **Documentation Deploy** (GitHub Pages not enabled / 404). **Dependency Review** — *skipped* on `push` (PR-only per workflow). |

## Rationale

M37A delivered planning-only artifacts: gate evidence, recovery matrix, M37B implementation plan stub, and governance updates. No supply-chain or workflow fixes were in scope. Post-merge CI failures match the **known pre-existing gate-recovery classes** documented in `M37A_run1.md` / `M37A_plan.md`, not regressions from documentation edits.

## Scope Confirmation

M37A was planning-only. No runtime, schema, workflow, dependency, `.gitignore`, or secret-boundary cleanup changes were made.

## Remaining Release Risk

- Security / `pip-audit` (lockfile vulnerabilities)
- Distribution Verification HTTP 401
- Dependency Review availability (PR + GHAS / dependency graph)
- SLSA / private user-owned repo attestation limitation
- Documentation Deploy / Pages setting

## Authorized Next Milestone

**M37B — Required Gate Recovery Implementation** — see `docs/milestones/M37B/M37B_plan.md`.
