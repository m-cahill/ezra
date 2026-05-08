# M41 Plan Merge Record

| Field | Value |
|---|---|
| PR | https://github.com/m-cahill/ezra/pull/46 |
| Branch | `docs/m41-post-visibility-smoke-plan` |
| Final head SHA | `648d80b0cbe8a8efba39f3281890aee051f1f703` |
| Merge SHA | `934304433043f5e161066a47c50d65ca9f248dfd` |
| Merge date | 2026-05-08T03:58:02Z (`mergedAt`, squash to `main`) |
| Merge method | squash |
| Post-merge CI | https://github.com/m-cahill/ezra/actions/runs/25535849971 — **success** |
| Remaining red checks | **PR #46 (pre-merge):** **Dependency Review** — `FAILURE` on workflow run [25532255676](https://github.com/m-cahill/ezra/actions/runs/25532255676), job [74940824955](https://github.com/m-cahill/ezra/actions/runs/25532255676/job/74940824955); `mergeStateStatus`: **UNSTABLE**; PR **MERGEABLE** per GitHub (known GHAS / dependency-graph class; not introduced by M41 docs). **Push to `main` (post-merge):** **Dependency Review** — **skipped**; required jobs **success** — no failing checks on run 25535849971. |

## PR #46 — Dependency Review (observed)

| Field | Value |
|---|---|
| Check name | Dependency Review |
| Conclusion on PR | **FAILURE** |
| Workflow run | https://github.com/m-cahill/ezra/actions/runs/25532255676 |
| Job URL | https://github.com/m-cahill/ezra/actions/runs/25532255676/job/74940824955 |

Other notable PR rollup items (observed): **SLSA Provenance** — **SKIPPED**; **Distribution Verification (release artifacts)** — **SKIPPED**; **Documentation Deploy** — **SKIPPED**.

## Scope Confirmation

M41 planning only. No smoke execution, tag, GitHub Release, PyPI publish, Pages enablement, repo settings, branch protection, workflow, dependency, runtime, EPB spec, secret-boundary, or `docs/prompts/` changes occurred.

## Planning Result

M41 defines a docs-only public PR smoke to observe:

1. public PR CI,
2. Dependency Review behavior after public visibility,
3. post-merge `main` CI,
4. public boundary guardrail,
5. continued deferral of tag / GitHub Release / PyPI / Pages actions.

## Authorized Next Step

M41 smoke execution on branch:

```text
docs/m41-post-visibility-smoke
```

No tag, GitHub Release, PyPI publish, Pages enablement, or repo settings change is authorized by this planning merge.
