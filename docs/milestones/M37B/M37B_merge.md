# M37B Merge Record

| Field | Value |
| --- | --- |
| **PR** | https://github.com/m-cahill/ezra/pull/39 |
| **Branch** | `fix/m37b-required-gate-recovery` |
| **Final head SHA (pre-squash tip)** | `456596c22d78854bc8897a741b9c99f569c4ee45` |
| **Merge SHA (`main`)** | `a51b6c0c731a1d3bc3f34ddc1e71ea240c1062f6` |
| **Merge date** | 2026-05-07 (UTC, per GitHub `mergedAt`) |
| **Merge method** | Squash merge |
| **Post-merge CI (`main`)** | https://github.com/m-cahill/ezra/actions/runs/25470570460 — `conclusion: success` |
| **Remaining red checks** | **None on `push`** for this run. **Dependency Review** — *skipped* on `main` `push` (PR-only per workflow); on pull requests it remains **unsupported** until dependency graph / GHAS (or equivalent) is enabled for the repository. |

## Scope Confirmation

M37B implemented required gate recovery only. No M37 secret-boundary cleanup was performed. No EPB schema, canonicalization, hashing, or intended runtime behavior changes were made.

## Gate Recovery Result

- **Security / pip-audit:** Lockfile / constraints updated; `pip-audit -r requirements.txt` passes without advisory ignores (see PR #39 and `M37B_run1.md`).
- **Distribution Verification:** PR/main uses `--mode ci-local`; full release-artifact path uses `workflow_dispatch` + `verify_tag` + `--mode release` with documented permissions (`docs/release/DISTRIBUTION_VERIFICATION.md`).
- **SLSA / private repo:** Attestation conditional on `github.repository_visibility == 'public'`; private context gets honest non-failing summary (CI + `release.yml`).
- **Documentation Deploy / Pages:** Deploy gated on `vars.EZRA_ENABLE_PAGES_DEPLOY == 'true'`; docs build remains the compile proof.
- **Dependency Review:** Documented as repository / GHAS / dependency-graph infrastructure limitation; PR-only; fails on PR when product tier does not support it.

## Validated evidence (pre-merge)

| Field | Value |
| --- | --- |
| Validated implementation baseline (`headSha`) | `aabfd92987093d0e1d3f81ffbab5adc3f7507a99` |
| Validated CI run | `25469067577` — https://github.com/m-cahill/ezra/actions/runs/25469067577 |
| Tip CI at merge (squash parent chain) | `25469154622` @ `456596c22d78854bc8897a741b9c99f569c4ee45` |

## Authorized Next Milestone

**M37 — Public Release Boundary Cleanup.**
