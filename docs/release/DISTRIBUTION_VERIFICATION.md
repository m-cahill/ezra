# Distribution Verification

This document describes how EZRA verifies distribution artifacts in **CI** and how maintainers can run **full release verification** against GitHub Actions artifacts.

---

## Purpose

The release workflow (pushing a `v*` tag) builds sdist and wheel, records hashes in `dist/SHA256SUMS.txt`, generates a CycloneDX SBOM, and uploads `ezra-distribution`, `ezra-sbom`, and `ezra-provenance`. Verification proves:

1. **PR / main (default CI):** The project still **builds**, **hash bookkeeping** for the built artifacts is internally consistent, and a **structurally valid SBOM** can be generated — without depending on downloading private workflow artifacts (avoids HTTP 401 from the artifact ZIP API under default `GITHUB_TOKEN` scopes).
2. **Release path (manual / tag context):** Artifacts from a real release run match their recorded hashes, a local rebuild matches those artifacts, and SBOM + provenance metadata are structurally valid.

---

## Modes (`scripts/verify_distribution.py`)

| Mode | When to use | GitHub API | Proves |
|------|-------------|------------|--------|
| **`ci-local`** | PRs, pushes to `main`, local smoke | No | Local build succeeds; `SHA256SUMS.txt` matches files under `dist/`; SBOM JSON is valid (components or dependencies present). Does **not** compare to a prior release or validate `provenance.json` from the workflow. |
| **`release`** | After a tag release; CI via `workflow_dispatch` | Yes (needs token with **`actions: read`**) | Downloads `ezra-distribution`, `ezra-sbom`, `ezra-provenance` for the resolved tag’s workflow run; verifies hashes; rebuilds and compares hashes; validates SBOM and provenance JSON. |

Exit codes: **`0`** verified (or `ci-local` checks passed); **`1`** verification failed; **`2`** error (missing token/repo, run not found, build failure).

---

## CI behavior (`.github/workflows/ci.yml`)

### Distribution Verification (PR and push to `main`)

- Runs for **`pull_request`**, **`push` to `main`**, and any event **except** `workflow_dispatch`.
- Executes: `python scripts/verify_distribution.py --mode ci-local`
- **Permissions:** `contents: read` only (no artifact download).
- **Does not prove:** that publish-time artifacts match an earlier release run; that GitHub attestation exists; reproducibility against another machine beyond “this runner’s build + hash file self-check.”

### Distribution Verification (release artifacts)

- Runs only on **`workflow_dispatch`**, with required input **`verify_tag`** (e.g. `v0.0.22-m21`).
- Executes: `python scripts/verify_distribution.py --mode release --tag "<verify_tag>"`
- **Environment:** `GITHUB_TOKEN`, `GITHUB_REPOSITORY` (automatic in Actions).
- **Permissions:** `contents: read`, **`actions: read`** (required to list and download workflow artifacts).

If artifact download still fails for your org/repo (e.g. token class or enterprise policy), treat that as an **infrastructure** limitation: document whether a PAT or settings change is needed; do not claim full release verification passed until downloads succeed.

---

## Manual release verification

Full check for a specific tag (local or maintainer machine):

```bash
export GITHUB_TOKEN=...   # needs actions:read for the repo
export GITHUB_REPOSITORY=owner/repo
python scripts/verify_distribution.py --mode release --tag vX.Y.Z
```

Latest release by workflow run order:

```bash
python scripts/verify_distribution.py --mode release --tag latest
```

PR-safe local check (no token):

```bash
python scripts/verify_distribution.py --mode ci-local
```

Example **`ci-local`** success report fields include `distribution_verified`, `artifact_hashes_match`, `sbom_valid`, `mode`, and notes that provenance was not checked in this mode.

---

## Security model (summary)

- **Artifact hashing** — Release workflow records SHA256 of wheel and sdist; **release** mode confirms files match `SHA256SUMS.txt` and that a clean rebuild matches.
- **SBOM** — CycloneDX output is validated for parseability and non-empty dependency/component structure.
- **Provenance JSON** — Validated only in **release** mode (`commit`, `builder`, `workflow`, `artifact_hashes`).
- **SLSA / GitHub attestation** — Separate from this script; see `REFACTOR.md` and CI job summaries. Private user-owned repos may skip attestation; do not claim SLSA until the attestation step actually succeeds.

---

## Documentation deploy (GitHub Pages)

Documentation **build** in CI always proves Sphinx compiles. **Deploy to GitHub Pages** runs only when:

- the event is a **push** to `main`, and  
- repository variable **`EZRA_ENABLE_PAGES_DEPLOY`** is set to **`true`**, and  
- GitHub Pages is configured for the repo (e.g. “GitHub Actions” source).

If Pages is not enabled, leave the variable unset so default-branch CI is not failed by a missing Pages environment.
