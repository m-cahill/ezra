# M40 Run 1 — Visibility-only public release execution

**Branch:** `ops/m40-public-release-execution`  
**Authorization:** Maintainer-authorized **visibility-only** execution (no tag, release, PyPI, Pages, workflow/settings/code edits).

**M39 decision (unchanged):** `GO WITH DOCUMENTED LIMITATIONS`

---

## Preflight (2026-05-07)

| Command | Result |
| --- | --- |
| `git status --short` | *(empty — clean working tree)* |
| `git rev-parse HEAD` | `38498ac5c81e010ab4ee73b34b4222e56ff1a76f` |
| `git ls-files .cursorrules docs/enhancements docs/prompts` | *(empty — no tracked boundary paths)* |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 90 files already formatted |
| `mypy src` | Success: no issues found in 40 source files |
| `pytest -q` | 273 passed, 28 skipped |
| `pip-audit -r requirements.txt` | No known vulnerabilities found |
| `python scripts/verify_distribution.py --mode ci-local` | `distribution_verified: true`, `sbom_valid: true` |
| `gh run list --branch main --limit 5` | Latest runs **success** (e.g. `25526993512`, `25526915472`, …) |
| `gh repo view m-cahill/ezra --json visibility,url,nameWithOwner` | `PRIVATE` before operation |

**Visibility before:** `PRIVATE`

---

## Visibility operation

```bash
gh repo edit m-cahill/ezra --visibility public --accept-visibility-change-consequences
```

**Note:** GitHub CLI requires `--accept-visibility-change-consequences` together with `--visibility public`.

**Exit code:** `0`

---

## Post-visibility verification

| Command | Result |
| --- | --- |
| `gh repo view m-cahill/ezra --json visibility,url,nameWithOwner` | `PUBLIC`, `https://github.com/m-cahill/ezra` |
| `git ls-files .cursorrules docs/enhancements docs/prompts` | *(empty)* |
| `gh run list --branch main --limit 5` | Same recent **success** snapshots as preflight (no new push triggered by visibility) |
| `gh release list --limit 5` | Existing releases only (e.g. `v1.0.0` **Latest**) — **no release created in this step** |
| `git ls-remote --tags origin` | Pre-existing tags only — **no new tag in this step** |

---

## Posture after public visibility (observe on next CI)

- **Dependency Review:** Still depends on GHAS / dependency graph; behavior should be rechecked on the **next pull request** (not re-run here).
- **SLSA / attestation:** Workflows gate on `repository_visibility == 'public'`; **actual attestation success** should be confirmed on a future **`main`** / **`v*`** workflow run that executes the attestation step—not claimed from visibility change alone.
- **Pages:** Still gated by `vars.EZRA_ENABLE_PAGES_DEPLOY` and repo Pages configuration — **not enabled** in this step.

---

## Deliverables

- `docs/milestones/M40/M40_visibility_record.md`
- Governance updates: `REFACTOR.md`, `docs/ezra.md`

---

ensure all documentation is updated as necessary
