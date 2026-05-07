# Milestone Summary — M37B

**Project:** EZRA  
**Milestone:** M37B — Required Gate Recovery Implementation  
**Refactor posture:** Implementation (supply-chain CI, workflows, docs; no secret cleanup)  
**Status:** Implementation complete — **pending merge review** (PR #39)  

---

## What changed

1. **Advisory-driven dependency / lockfile updates** — `pyproject.toml` floors (`cryptography`, `pytest`, `pillow`, `lxml`, `pygments`, `requests`, etc.) and regenerated `requirements.txt` via `pip-compile --extra=dev`; **`pip-audit -r requirements.txt` passes without ignores**.
2. **`types-jsonschema`** — dev dependency so Linux CI `mypy` and local checks agree on `jsonschema` typing (no `import-untyped` suppression needed for CI).
3. **Distribution Verification** — **`--mode ci-local`** on PR/main (local build, SHA256SUMS self-check, SBOM); **`--mode release`** for `workflow_dispatch` with `verify_tag` and artifact download; `docs/release/DISTRIBUTION_VERIFICATION.md` aligned.
4. **SLSA honesty** — `actions/attest-build-provenance` only when `github.repository_visibility == 'public'`; private repo gets non-failing explanatory summary (CI + `release.yml`).
5. **Pages deploy** — `docs-deploy` gated on `vars.EZRA_ENABLE_PAGES_DEPLOY == 'true'`; docs **build** remains the compile proof.
6. **Dependency Review** — documented as **repo / GHAS / dependency-graph** dependent; not removed; expected red until settings support it.

---

## What did not change

- **No M37 secret-boundary cleanup** (no `docs/enhancements/` removal, no `.gitignore` edits for that program).
- **No EPB schema** changes under `docs/specs/epb_v1/**`.
- **No EPB canonicalization or hashing** rule changes.
- **No intended runtime behavior change** in perception/EPB pipelines; only typing imports for `jsonschema` and workflow/script/test/docs/lockfile updates.

---

## Verification

| Check | Result (see `M37B_run1.md`) |
| --- | --- |
| `pip-audit -r requirements.txt` | Passes |
| `pytest` | Passes |
| `ruff format --check .` / `ruff check .` | Pass |
| `mypy src` | Pass |
| PR #39 CI (validated `aabfd92`) | Run `25469067577`: workflow success; M37B-relevant jobs pass; **Dependency Review** fails (infra) |

---

## Remaining limitation

- **Dependency Review** still requires **dependency graph** and **GitHub Advanced Security** (or equivalent product tier) on the repository. **ensure all documentation is updated as necessary**

---

## Prompt templates note

Closeout referenced `docs/prompts/summaryprompt.md` and `docs/prompts/unifiedmilestoneauditpromptV2.md`; those paths **are not present** in the repository. This summary follows the **M37A / M36** milestone structure and the maintainer handoff checklist.

---

## Authorized next step

After **PR #39** merges to `main`, **M37 — Public Release Boundary Cleanup** may proceed per `REFACTOR.md` sequencing (subject to maintainer approval). **ensure all documentation is updated as necessary**
