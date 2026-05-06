# M36 PR #37 — CI workflow triage

**Purpose:** Documentation-only follow-up for [PR #37](https://github.com/m-cahill/ezra/pull/37). No dependency, workflow, or source fixes—triage and merge-routing only.

---

## 1. PR identity

| Field | Value |
| --- | --- |
| **Branch** | `docs/m36-audit-reconciliation` |
| **Commit SHA (M36 docs closeout)** | `bd6cffa47e36cab0afae9fb7bfd366e674a82656` |
| **PR URL** | https://github.com/m-cahill/ezra/pull/37 |
| **CI run URL** | https://github.com/m-cahill/ezra/actions/runs/25465492721 |
| **CI run ID** | `25465492721` |
| **Workflow conclusion** | `failure` (overall; see §3) |
| **Documentation-only M36 PR?** | **Yes** — governance/reconciliation artifacts and M37 stubs only; no runtime, schema, workflow, dependency, `.gitignore`, or secret-cleanup changes in M36 scope. |

---

## 2. Changed files confirmation

### Files in M36 documentation commit (`bd6cffa`)

- `REFACTOR.md`
- `docs/ezra.md`
- `docs/milestones/M36/M36_audit.md`
- `docs/milestones/M36/M36_plan.md`
- `docs/milestones/M36/M36_run1.md`
- `docs/milestones/M36/M36_summary.md`
- `docs/milestones/M36/M36_toolcalls.md`
- `docs/milestones/M37/M37_plan.md`
- `docs/milestones/M37/M37_toolcalls.md`
- `docs/release/AUDIT_RECONCILIATION_M33_M35.md`

### Explicit confirmations

| Assertion | Confirmed |
| --- | ---: |
| No `src/ezra/**` changes | Yes |
| No `docs/specs/epb_v1/**` changes | Yes |
| No `.github/workflows/**` changes | Yes |
| No `pyproject.toml` changes | Yes |
| No `requirements.txt` changes | Yes |
| No `.gitignore` changes | Yes |
| No secret-boundary cleanup (untrack/remove enhancements/prompts) | Yes |

---

## 3. Check-by-check triage

Classifications: **M36-blocking regression** | **Pre-existing supply-chain issue** | **Known infrastructure/config issue** | **Local-only/tooling drift** | **Passed**

| Check | Result | Classification | Introduced by M36? | Merge impact | Follow-up |
| --- | --- | --- | --- | --- | --- |
| Lint | Pass | Passed | No | None | — |
| Type Check | Pass | Passed | No | None | Local Windows `mypy` drift (if any) is **Local-only/tooling drift** unless CI reproduces; Linux CI passed on PR #37. |
| Smoke Tests | Pass | Passed | No | None | — |
| Test | Pass | Passed | No | None | — |
| EPB Tools Minimal Environment | Pass | Passed | No | None | — |
| SBOM Generation | Pass | Passed | No | None | — |
| Complexity Check | Pass | Passed | No | None | — |
| Determinism Check | Pass | Passed | No | None | — |
| Hermetic Hash matrix | Pass | Passed | No | None | — |
| Hermetic Reproducibility | Pass | Passed | No | None | — |
| Documentation Build | Pass | Passed | No | None | — |
| OpenSSF Scorecard | Pass (informational posture in workflow) | Passed / informational | No | None | — |
| Dependency Review | Fail | Known infrastructure/config issue | No | May affect **branch protection** / red PR UI | Enable GHAS / dependency graph, or maintain `continue-on-error` policy; document. |
| Distribution Verification | Fail (HTTP 401) | Known infrastructure/config issue | No | May affect **branch protection** | Artifact token/permissions workflow or infra fix; same class as M35 notes. |
| Security Check (`pip-audit`) | Fail | Pre-existing supply-chain issue | No | May **block merge** if required | Dedicated supply-chain recovery milestone (bump lockfile / advisories); **not** M36. |
| SLSA Provenance | Skipped | — | No | N/A for PR | Expected skip on PR triggers per workflow. |
| Documentation Deploy | Skipping | — | No | N/A for PR | Expected when deploy is push-only. |

---

## 4. M36 merge recommendation

**Recommendation:** **Approve M36 merge despite unrelated failing gates, *if* repository policy allows maintainer override for pre-existing, non-M36 failures.**

**Mechanical caveat:** `gh pr view` reports `mergeable: MERGEABLE` but `mergeStateStatus: UNSTABLE` for PR #37—i.e. the PR is not green as a whole and **branch protection may still block** the merge button until failing required checks pass or are exempted. If protection requires Security Check / Distribution Verification / Dependency Review, then **M36 is ready in substance but mechanically blocked** until those gates pass or policy is updated.

**Do not** treat M36 doc changes as the cause of `pip-audit` or HTTP 401 failures.

---

## 5. Follow-up milestone routing

| Issue | Route |
| --- | --- |
| `pip-audit` vulnerabilities | New **supply-chain recovery** milestone before public release (e.g. **M37b** or **M38**, depending on whether M37 boundary cleanup can merge first). |
| Dependency Review unavailable | Document as infra; optional org/repo settings change; **not** M36. |
| Distribution Verification HTTP 401 | Workflow recovery or token/permissions infra; **not** M36. |
| Local Windows `mypy` drift | Optional local dev follow-up only unless CI reproduces. |

---

## 6. Separate CI/security recovery before M37?

**Yes, if** `pip-audit` (Security Check) is a **required** status check for `main`: merging M36 may be blocked until the lockfile is updated or the check is waived—address in a **narrow CI/supply-chain recovery** milestone **before** or **in parallel with** M37 planning, per maintainer preference.

**If** Security / Distribution Verification / Dependency Review are **not** required checks, M36 can merge after policy acknowledgement of red but non-M36 failures.

---

## 7. Do not fix in M36 (this triage)

This artifact must not be used to justify, in the same M36 scope:

- dependency updates or `pip-compile` regeneration,
- workflow edits,
- `.gitignore` or secret-path cleanup,
- `src/ezra/**` or EPB spec changes,
- silencing or weakening CI checks.
