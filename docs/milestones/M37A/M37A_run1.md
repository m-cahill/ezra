# M37A Run 1 — Evidence (planning)

Planning-only milestone. Captures commands and post-merge CI evidence for required-gate recovery.

---

## `git status --short`

After authoring M37A docs (before `git add`):

```
 M REFACTOR.md
 M docs/ezra.md
```

`docs/milestones/M37A/*.md` exist on disk but match `.gitignore` entry `docs/milestones/`; they are included in the commit via **`git add -f`** (same mechanism as other milestone paths that remain tracked in Git).

## `git rev-parse HEAD`

```
bc0347f70df65ad92407f5d000f10ffcdd4e185f
```

(Local checkout matches documented post-M36 docs commit on `main`.)

## `gh run view 25466391573 --json conclusion,headSha,event,workflowName,url`

```json
{
  "conclusion": "failure",
  "event": "push",
  "headSha": "969471060c0ad9b528836209531a023c098e5a4e",
  "url": "https://github.com/m-cahill/ezra/actions/runs/25466391573",
  "workflowName": "CI"
}
```

_Post-merge `main` CI run for the M36 squash merge commit._

## `gh pr view 37 --json state,mergedAt,mergeCommit,url`

```json
{
  "mergeCommit": { "oid": "969471060c0ad9b528836209531a023c098e5a4e" },
  "mergedAt": "2026-05-06T23:14:19Z",
  "state": "MERGED",
  "url": "https://github.com/m-cahill/ezra/pull/37"
}
```

## `gh api repos/m-cahill/ezra/branches/main/protection || true`

Exit non-zero; HTTP **404** with body:

```json
{
  "message": "Branch not protected",
  "documentation_url": "https://docs.github.com/rest/branches/branch-protection#get-branch-protection",
  "status": "404"
}
```

**Interpretation:** Classic REST branch protection is **not** enabled for `main` (same class as M36 merge record). Merge mechanics are **not** blocked by required status checks via this API; release risk is **policy/process**, not GitHub mechanical enforcement.

## `gh api repos/m-cahill/ezra` (summary only)

**Not pasted:** full JSON includes operator-only fields; do not commit raw responses unredacted.

**Recorded facts relevant to M37A:**

- `private`: **true**
- `owner.type`: **User** (user-owned repository)
- `has_pages`: **false**
- `default_branch`: **main**

These support classifying **SLSA attestation** and **Pages deploy** limitations (see failed log below).

---

## Failed jobs — `gh run view 25466391573 --log-failed` (extract)

Captured from `gh run view 25466391573 --log-failed` (2026-05-06). Failed job / step mapping:

| Job | Failed step | Primary signal |
| --- | --- | --- |
| Security Check | **Run pip-audit** | `Found 11 known vulnerabilities in 6 packages`; step exit **1** |
| Distribution Verification | **Verify distribution** | `urllib.error.HTTPError: HTTP Error 401: Server failed to authenticate the request` in `_download_artifact_zip` (GitHub artifact ZIP API) |
| SLSA Provenance | **Generate provenance attestation** | `Failed to persist attestation: Feature not available for user-owned private repositories` |
| Documentation Deploy | **Deploy to GitHub Pages** | `HttpError: Not Found` — enable Pages in repo settings |

**`gh run view 25466391573 --json jobs` — Dependency Review:**

- Job **Dependency Review**: `conclusion`: **skipped** for this **push** event (workflow `if` limits job to `pull_request`).

**pip-audit excerpt (Linux CI log):**

- Same advisory set as local run: `cryptography` 46.0.5; `lxml` 6.0.2; `pillow` 12.1.1 (multiple); `pygments` 2.19.2; `pytest` 9.0.2; `requests` 2.32.5.
- Skip note: `ezra Dependency not found on PyPI and could not be audited: ezra (1.0.0)` (editable / local project install).

---

## Local `pip-audit` (Windows)

**Commands:**

```bat
pip-audit -r requirements.txt
pip-audit -r requirements.txt -f json -o pip_audit_current.json
```

**Tooling note:** System `pip-audit` reported version **2.7.3**; lockfile pins **pip-audit==2.10.0** for CI. Advisory set matched Linux CI (11 vulns / 6 packages).

**Human-readable summary (exit code 1):**

```
Found 11 known vulnerabilities in 6 packages
Name         Version ID                  Fix Versions
------------ ------- ------------------- ------------
cryptography 46.0.5  GHSA-m959-cc7f-wv43 46.0.6
cryptography 46.0.5  GHSA-p423-j2cm-9vmq 46.0.7
lxml         6.0.2   GHSA-vfmq-68hx-4jfw 6.1.0
pillow       12.1.1  (5 advisories)    12.2.0
pygments     2.19.2  GHSA-5239-wwwm-4pmq 2.20.0
pytest       9.0.2   GHSA-6w46-j5rx-g56g 9.0.3
requests     2.32.5  GHSA-gc5v-m9x4-r6x2 2.33.0
```

**JSON output:** Written to `pip_audit_current.json` locally for inspection. **Not committed** (per milestone rules — summarize only; file removed after review).

**Windows environment noise:**

- `WARNING:cachecontrol.controller:Cache entry deserialization failed`
- `WARNING:pip_audit._cache:Failed to write to cache directory ... [WinError 5] Access is denied`

These do **not** change the vulnerability list; they indicate local cache/permissions drift vs Linux CI.

---

## Direct vs transitive notes (for planning)

| Package | Lockfile version | In `pyproject.toml`? | Role |
| --- | --- | --- | --- |
| cryptography | 46.0.5 | Yes (`dependencies`) | **Direct** (runtime) |
| pillow | 12.1.1 | Yes (`dev`) | **Direct** (dev / optional) |
| pytest | 9.0.2 | Yes (`dev`) | **Direct** (dev) |
| lxml | 6.0.2 | No | **Transitive** (SBOM / cyclonedx stack) |
| pygments | 2.19.2 | No | **Transitive** (Sphinx / rich tooling) |
| requests | 2.32.5 | No | **Transitive** (multiple consumers) |

**Likely fix path (implementation milestone, not M37A):** regenerate lockfile via `pip-compile` after bumping constraints in `pyproject.toml` / upstream pins; prefer minimum bumps that satisfy **max(fix_versions)** per package (e.g. cryptography **≥46.0.7** to cover both GHSA entries).

**Runtime risk:** `cryptography` and `pillow` affect runtime or plugin paths; version bumps deserve quick regression smoke. Dev-only packages (pytest, pygments) lower runtime risk but still affect CI hermeticity.

---

## Planning-commit verification (local)

| Command | Result |
| --- | --- |
| `ruff format --check .` | Pass (`88 files already formatted`) |
| `pytest -q` | Pass (`267 passed, 28 skipped`) |
| `ruff check .` | **Fail** — `UP038` in `tests/test_baseline_schema.py` (lines 47, 50) |

**Note:** M37A touches **no** Python sources; these Ruff findings are **pre-existing local drift** vs a clean Linux CI expectations narrative — record only; do not fix under M37A.

---

## Supplemental: Documentation Deploy

Not in the four named M37A tracks but **failed on the same `main` push run**:

- **Job:** Documentation Deploy  
- **Step:** Deploy to GitHub Pages  
- **Cause:** Pages not enabled (`has_pages: false`); HTTP 404 on deployment creation.

Treat as **settings / infra**, analogous to M19 notes.
