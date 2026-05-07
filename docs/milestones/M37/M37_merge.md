# M37 Merge Record

| Field | Value |
| --- | --- |
| **PR** | https://github.com/m-cahill/ezra/pull/40 |
| **Branch** | `chore/m37-public-boundary-cleanup` |
| **Final head SHA** | `f3e50b6c5684f0ef3ed95ec5c73613f9ac757fb8` |
| **Merge SHA (`main`)** | `9adfe7a0f789037fe3880a57f1e65cfbd5061f7b` |
| **Merge date** | 2026-05-07 (UTC, per GitHub `mergedAt`) |
| **Merge method** | Squash merge |
| **Post-merge CI (`main`)** | https://github.com/m-cahill/ezra/actions/runs/25473078293 — `conclusion: success` |
| **Remaining red checks** | **None** on this `push` workflow. **Dependency Review** — *skipped* on `main` `push` (PR-only); on PRs it may fail until dependency graph / GHAS is enabled. |

## Scope Confirmation

M37 removed only approved company-secret tracked files under `docs/enhancements/`.

No runtime, EPB schema, dependency, workflow, or broader documentation cleanup occurred.

## Boundary Result

Command:

```bash
git ls-files .cursorrules docs/enhancements docs/prompts
```

Result:

```text
(no output)
```

## Guardrail

`tests/test_public_release_boundary.py` prevents re-tracking:

* `.cursorrules`
* `docs/enhancements/`
* `docs/prompts/`

## Authorized Next Milestone

**M38 — Audit-Polish / Public-Readiness Improvements.**
