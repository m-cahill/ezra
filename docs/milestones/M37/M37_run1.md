# M37 — Run 1 (implementation evidence)

Branch: `chore/m37-public-boundary-cleanup`  
Recorded: 2026-05-07

## Note on Git tracking

`docs/milestones/` is listed in `.gitignore`; use `git add -f` when committing milestone files.

## Missing prompt paths (future M37 closeout)

Closeout may reference:

- `docs/prompts/summaryprompt.md`
- `docs/prompts/unifiedmilestoneauditpromptV2.md`

Those paths are **not** in-repo (and `docs/prompts/` is intentionally ignored). Use M36/M37B-style summary/audit structure for `M37_summary.md` / `M37_audit.md` when closing.

---

## Task 1 — Inventory (before changes)

### `git status --short`

```
(clean on branch chore/m37-public-boundary-cleanup at start)
```

### `git rev-parse HEAD`

```
5b0da49bb31185c39ced9ea16c73c1256c183c35
```

### `git ls-files .cursorrules docs/enhancements docs/prompts`

```
docs/enhancements/AuditEnhancementsV2.md
docs/enhancements/EnhancementsV2.md
docs/enhancements/TestingEnhancementsV2.md
```

Matches expected three files only.

### `.gitignore` lines (before / after M37)

Pre-M37: `.cursorrules`, `/docs/prompts/`, but **no** `docs/enhancements/`.  
M37: `.cursorrules`, `docs/enhancements/`, `docs/prompts/` (normalized from `/docs/prompts/` prefix form).

---

## Task 6 — Verification before closeout commit (2026-05-07)

| Command | Result |
| --- | --- |
| `git ls-files .cursorrules docs/enhancements docs/prompts` | *(no output — empty)* |
| `pytest -q` | 270 passed, 28 skipped |
| `ruff format --check .` | 89 files already formatted |
| `ruff check .` | All checks passed |
| `mypy src` | Success: no issues found in 40 source files |
| `pip-audit -r requirements.txt` | No known vulnerabilities found |
| `python scripts/verify_distribution.py --mode ci-local` | Exit 0; `distribution_verified: true` |

---

## Task 7 — Verification (after initial cleanup)

| Command | Result |
| --- | --- |
| `git ls-files .cursorrules docs/enhancements docs/prompts` | *(no output — empty)* |
| `pytest -q` | 270 passed, 28 skipped |
| `ruff format --check .` | All files formatted |
| `ruff check .` | All checks passed |
| `mypy src` | Success: no issues found in 40 source files |
| `pip-audit -r requirements.txt` | No known vulnerabilities found |
| `python scripts/verify_distribution.py --mode ci-local` | Exit 0; `distribution_verified: true` |

---

## Task 9 — PR evidence (tip refresh)

| Field | Value |
| --- | --- |
| PR | **#40** |
| URL | https://github.com/m-cahill/ezra/pull/40 |
| `headRefOid` (closeout) | `375cb73caa266b9913498c6229674174526fb689` |
| CI run (tip) | `25471797382` — https://github.com/m-cahill/ezra/actions/runs/25471797382 — **`conclusion: success`**, `headSha` matches tip |
| Implementation commit | `0b2fed8c3303ee84c4c5e9a68b28daf702325a69` |
| Earlier CI (implementation) | `25471712032` — success |
| `mergeStateStatus` | `UNSTABLE` (Dependency Review fails — GHAS/deps graph; expected infra) |
| M37 / M37B-relevant gates | Pass; **Test** includes `test_public_release_boundary` |

**Remaining red:** **Dependency Review** only.

### Prompt template paths (absent)

Per closeout instructions, **`docs/prompts/summaryprompt.md`** and **`docs/prompts/unifiedmilestoneauditpromptV2.md`** are not in-repo. Recorded in **`M37_summary.md`** and **`M37_audit.md`**; do not add `docs/prompts/` to Git.

ensure all documentation is updated as necessary
