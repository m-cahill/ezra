# M37 — Public Release Boundary Cleanup (plan)

## Note

M37 removes only the user-approved company-secret boundary paths. It is not an audit-polish milestone and not a runtime refactor.

## 1. Intent / target

Remove approved company-secret paths from the committed public repo surface and add guardrails so they are not reintroduced via Git:

- `.cursorrules`
- `docs/enhancements/`
- `docs/prompts/`

## 2. Scope boundaries

**In scope:** Untrack the three known `docs/enhancements/*.md` files; ensure `.gitignore` covers all three path classes; add a deterministic test that fails if any of these paths become tracked.

**Out of scope:** Other docs, M36/M37A/M37B artifacts, `docs/M33fullaudit.md`, EPB specs, runtime `src/ezra/**`, dependencies, workflows (unless guardrail absolutely required — it is not), broadening the secret list, milestone folder policy (`docs/milestones/` stays as today).

## 3. Invariants

| Invariant | Check |
| --- | --- |
| No runtime behavior change | No edits under `src/ezra/**` (except disallowed — no runtime edits) |
| EPB unchanged | No `docs/specs/epb_v1/**` edits |
| Only approved paths | `git diff --name-status` |
| `git ls-files` on the three roots empty | Guardrail test + manual |
| CI posture | Same gates as M37B; no workflow edits |

## 4. Verification plan

- `git ls-files .cursorrules docs/enhancements docs/prompts` → empty
- `pytest -q`, `ruff`, `mypy src`, `pip-audit -r requirements.txt`, `verify_distribution.py --mode ci-local`
- PR CI: expect M37B-style green workflow; Dependency Review may fail on PR only (infra)

## 5. Implementation steps

1. Inventory tracked paths (record in `M37_run1.md`).
2. `git rm` the three `docs/enhancements/*.md` files.
3. Add `docs/enhancements/` to `.gitignore` if missing (`.cursorrules` and `docs/prompts` already ignored).
4. Add `tests/test_public_release_boundary.py`.
5. Update `REFACTOR.md`, `docs/ezra.md`, tool log; open PR.

## 6. Risk & rollback

**Risk:** Low — removals are explicit; rollback is `git revert` on the merge commit.

## 7. Deliverables

| Artifact | Purpose |
| --- | --- |
| `M37_plan.md` | This document |
| `M37_run1.md` | Command evidence, PR CI |
| `M37_toolcalls.md` | Tool/command log |
| Guardrail test | Prevents re-tracking |
| Governance updates | `REFACTOR.md`, `docs/ezra.md` |

## 8. Explicit non-goals

- No M38 / audit-polish work.
- No removal of files outside the approved three path prefixes.
- No changes to dependencies, workflows, or EPB.
