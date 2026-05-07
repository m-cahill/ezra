# M37B — Run 1 (implementation evidence)

Branch: `fix/m37b-required-gate-recovery`  
PR: https://github.com/m-cahill/ezra/pull/39  
Recorded: 2026-05-06 (initial); **tip refresh 2026-05-07**

## Note on Git tracking

`docs/milestones/` is listed in `.gitignore`; milestone evidence files must be added with `git add -f <path>` when they should be committed (M37B does not change `.gitignore`).

## Missing prompt paths (closeout)

The following paths from the milestone closeout instructions were **not** present in this working tree at recording time:

- `docs/prompts/summaryprompt.md`
- `docs/prompts/unifiedmilestoneauditpromptV2.md`

Use the established M36/M37A summary/audit structure for `M37B_summary.md` and `M37B_audit.md` when closing the milestone after CI review.

---

## PR #39 Tip CI Refresh

**Merge hygiene:** Before merge, run `gh pr view 39 --json headRefOid` and confirm the PR head either matches the **validated commit** below **or** has a newer successful CI run with the same expected pattern (M37B gates green; **Dependency Review** red/skipped per settings).

| Field | Value |
| --- | --- |
| Validated commit (`headSha` / `git rev-parse`) | `ce111d158ea0bb5f32b82a35e6b534b6b2eb8371` |
| CI run ID | `25469000753` |
| CI run URL | https://github.com/m-cahill/ezra/actions/runs/25469000753 |
| Conclusion | `success` (`event`: `pull_request`, `workflowName`: `CI`) |
| Remaining red checks | **Dependency Review** only (`actions/dependency-review-action`: dependency graph / GHAS not enabled for repo) |
| M37B-introduced failures? | **No** |

### Failed / skipped jobs (expected)

- **Failed:** Dependency Review — `##[error]Dependency review is not supported on this repository...` (settings).
- **Skipped (by design):** Distribution Verification (release artifacts), Documentation Deploy, SLSA Provenance — event/visibility/variable gating per M37B design.

### `gh pr view 39` (at validated commit; re-query before merge)

- `headRefOid` was `ce111d158ea0bb5f32b82a35e6b534b6b2eb8371` when run `25469000753` completed.
- `mergeable`: `MERGEABLE`
- `mergeStateStatus`: `UNSTABLE` (rollup includes failing Dependency Review)

### Historical runs

- `25468502386` @ `24c7cb4` — implementation validation before docs-only commits on the branch.
- `25468576713` @ `e9079b6` — tip **before** closeout evidence commit.
- `25468778850` @ `c64e2a3` — CI after `docs(m37b): close implementation evidence`.
- `25468841430` @ `accd5c7` — docs alignment commit only.
- `25468913909` @ `237451b` — validated CI after implementation + first closeout batch.
- **`25469000753` @ `ce111d1` — validated CI for merge review** (merge-hygiene wording + pinned-evidence docs; see merge hygiene above).

---

### `ci-local` verification at tip

Command: `python scripts/verify_distribution.py --mode ci-local`

```text
exit code: 0
distribution_verified: true
artifact_hashes_match: true
sbom_valid: true
(no reproducible_build_match in ci-local output — expected)
```

---

## Task 7 — Local verification before closeout commit (2026-05-07)

| Command | Result |
| --- | --- |
| `pip-audit -r requirements.txt` | No known vulnerabilities found |
| `python scripts/verify_distribution.py --mode ci-local` | Exit 0; JSON as above |
| `pytest -q` | 269 passed, 28 skipped |
| `ruff format --check .` | 88 files already formatted |
| `ruff check .` | All checks passed |
| `mypy src` | Success: no issues found in 40 source files |

---

## Decision

- [x] Ready for closeout / merge review *(M37B code gates green at tip; Dependency Review documented as infra)*  
- [ ] Not ready — fix required

---

## Earlier implementation record (archive)

### `git rev-parse HEAD` (session start from `main` merge record)

```
822f87ff7fe94daf2209f27f2ed8ae7d9c0ef01c
```

### `pip-compile --version`

```
pip-compile, version 7.5.3
```

### `pytest -q` (during implementation)

```
269 passed, 28 skipped (full suite)
```

### `mypy src`

```
Success: no issues found in 40 source files
```
(with `types-jsonschema` from dev lockfile)

---

## Summary of implementation (Tracks 1–4)

1. **pip-audit:** Direct/transitive floors in `pyproject.toml`; dev **`types-jsonschema`** for Linux `mypy`; `requirements.txt` via `pip-compile --extra=dev --output-file=requirements.txt pyproject.toml`.
2. **Distribution verification:** `ci-local` on PR/main; `workflow_dispatch` + `verify_tag` for `--mode release`; `docs/release/DISTRIBUTION_VERIFICATION.md` updated.
3. **SLSA:** Attest only when `github.repository_visibility == 'public'`; else summary (CI + Release workflows).
4. **Pages:** `docs-deploy` requires `vars.EZRA_ENABLE_PAGES_DEPLOY == 'true'`.
5. **Dependency Review:** Documented as settings/GHAS-dependent.

Ensure all documentation is updated as necessary.
