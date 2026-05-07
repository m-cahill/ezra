# M37B — Run 1 (implementation evidence)

Branch: `fix/m37b-required-gate-recovery`  
Recorded: 2026-05-06

## Note on Git tracking

`docs/milestones/` is listed in `.gitignore`; milestone evidence files must be added with `git add -f <path>` when they should be committed (M37B does not change `.gitignore`).

## Missing prompt paths (closeout)

The following paths from the milestone closeout instructions were **not** present in this working tree at recording time:

- `docs/prompts/summaryprompt.md`
- `docs/prompts/unifiedmilestoneauditpromptV2.md`

Use the established M36/M37A summary/audit structure for `M37B_summary.md` and `M37B_audit.md` when closing the milestone after CI review.

## `git status --short` (before commit)

```
 M .github/workflows/ci.yml
 M .github/workflows/release.yml
 M REFACTOR.md
 M docs/ezra.md
 M docs/release/DISTRIBUTION_VERIFICATION.md
 M pyproject.toml
 M requirements.txt
 M scripts/verify_distribution.py
 M tests/test_distribution_verification.py
... (plus type-ignore removals in src after mypy verification)
```

## `git rev-parse HEAD` (recording start)

```
822f87ff7fe94daf2209f27f2ed8ae7d9c0ef01c
```

*(Update this section after committing M37B work to the final squashed/merge commit SHA.)*

## `pip-audit -r requirements.txt`

```
No known vulnerabilities found
```

## `pip-compile --version`

```
pip-compile, version 7.5.3
```

## `pytest -q`

```
269 passed, 28 skipped (full suite)
16 passed (tests/test_distribution_verification.py only, spot-check after edits)
```

## `ruff format --check .` / `ruff check .`

```
88 files already formatted
All checks passed!
```

## `mypy src`

Local run with `types-jsonschema` from the dev lockfile:

```
Success: no issues found in 40 source files
```

## GitHub CLI (post-PR)

```text
PR #39: https://github.com/m-cahill/ezra/pull/39
Initial CI run 25468412095: Type Check failed until `types-jsonschema` added to dev deps; Dependency Review failed (GHAS/settings).
After follow-up push: update this block with `gh pr checks 39` output.
```

## Summary of implementation (Tracks 1–4)

1. **pip-audit:** Direct/transitive floors in `pyproject.toml`; dev **`types-jsonschema`** added so Linux CI and local `mypy` agree on `jsonschema` typing; `requirements.txt` regenerated via `pip-compile --extra=dev --output-file=requirements.txt pyproject.toml`.
2. **Distribution verification:** `ci-local` on PR/main; `workflow_dispatch` + `verify_tag` for `--mode release`; docs updated in `docs/release/DISTRIBUTION_VERIFICATION.md`.
3. **SLSA:** `actions/attest-build-provenance` only if `github.repository_visibility == 'public'`; otherwise job summary + notice (CI + Release workflows).
4. **Pages:** `docs-deploy` requires `vars.EZRA_ENABLE_PAGES_DEPLOY == 'true'`.
5. **Dependency Review:** Documented as settings/GHAS-dependent in `REFACTOR.md` (warn-first; not a primary M37B code target).

Ensure all documentation is updated as necessary.
