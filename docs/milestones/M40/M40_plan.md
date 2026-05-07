# M40 — Public Release Operation / Visibility Decision

**Status:** Planning  
**Repository target:** `m-cahill/ezra`  
**M39 decision (must be preserved):** `GO WITH DOCUMENTED LIMITATIONS` (see `docs/milestones/M39/M39_public_release_audit.md`)

This milestone is **planning only** until the maintainer explicitly authorizes operational steps. **No** visibility change, tag, GitHub Release, PyPI publish, Pages enablement, workflow edit, or runtime change occurs as part of this plan’s deliverables.

---

## 1. Intent / Target

M40 plans the **operational** public-release step after M39’s readiness decision.

The plan must answer:

- Should the repository be made **public** now, **later after another review**, or **kept private** with a ready-when-triggered posture?
- If public: what **preflight**, **approval gate**, **operation**, and **post-public** verification steps apply?
- Should a **tag** or **GitHub Release** follow visibility, and only **after** explicit maintainer approval of naming and notes?
- What **limitations** (from M39) must appear in release notes / governance evidence?
- What **evidence** (URL, visibility, tag SHA, CI runs, boundary check) must be recorded when operations are later authorized?

**Preference (per maintainer guidance):** treat the primary path as **make public after explicit maintainer approval**, with a documented fallback to **keep private** until triggered.

**Non-conversion rule:** M40 does **not** restate the verdict as “GO without limitations.” The release posture remains **GO WITH DOCUMENTED LIMITATIONS** until a future audit says otherwise.

---

## 2. Scope Boundaries

### In scope

- Planning for repository **visibility** decision and sequencing.
- Planning for optional **tag** / **GitHub Release** **after** visibility, only if separately authorized; **no assumed tag name**.
- Planning for **Post-public** CI and behavior checks (Dependency Review, SLSA/Pages posture may change or stay limited).
- Planning for **evidence** fields to capture in governance docs after operations (public URL, tag, release URL, run IDs).
- Planning for **release notes outline** and **announcement checklist** (factual, governance-oriented; not marketing unless explicitly requested).
- **Limitation carry-forward:** Dependency Review / GHAS, SLSA on private repo class, Pages gated by settings / `EZRA_ENABLE_PAGES_DEPLOY`.

### Out of scope (for M40 planning deliverables and for any work done under “planning only”)

- Making the repo public, private → public toggling, or changing GitHub org/repo settings.
- Creating **tags** or **GitHub Releases**.
- Publishing to **PyPI** (release workflow exists but must not be triggered from planning).
- **Enabling GitHub Pages** or setting `EZRA_ENABLE_PAGES_DEPLOY` unless explicitly authorized as a separate operational decision.
- Edits under `src/ezra/**`, `docs/specs/epb_v1/**`, `.github/workflows/**`, `pyproject.toml`, `requirements.txt`.
- Altering **secret-boundary** tracked content or restoring `docs/prompts/` to the Git surface.
- Claiming that M39’s **documented limitations are fully resolved**.
- Branch protection or repository policy changes (unless a future milestone explicitly owns them).

---

## 3. Preconditions

Before any **authorized** operational execution (not during planning-only work), verify:

| Prerequisite | Location / check | M40 planning verification |
|--------------|------------------|---------------------------|
| M39 public-release audit | `docs/milestones/M39/M39_public_release_audit.md` | **Present** (local workspace) |
| M39 merge record | `docs/milestones/M39/M39_merge.md` | **Present** |
| M39 run evidence | `docs/milestones/M39/M39_run1.md` | **Present** |
| Public release checklist | `docs/release/PUBLIC_RELEASE_CHECKLIST.md` | **Present** (repo root docs) |
| Refactor ledger | `REFACTOR.md` | **Present** |
| Governance ledger | `docs/ezra.md` | **Present** |
| README | `README.md` | **Present** |
| Contributing | `CONTRIBUTING.md` | **Present** |

**Planning note:** `docs/milestones/` is listed in `.gitignore` for local-only proof packs; milestone files may require `git add -f` to include in PRs. Historical M39 artifacts remain referenced in `REFACTOR.md` and `docs/ezra.md` if not cloned.

**M39 decision summary (carry forward):**

1. Dependency Review depends on **GHAS / dependency graph**; PR behavior may differ from `push` to `main`.
2. **SLSA** artifact attestation was limited for **private / user-owned** repos; reassess after visibility change without claiming success until a workflow run proves it.
3. **Pages** deploy is **gated**; **Documentation Build** in CI remains the proof of Sphinx correctness.

---

## 4. Invariants

M40 planning and any planning-only documentation edits must preserve:

| Invariant | Verification |
|-----------|---------------|
| No runtime behavior change | No edits under `src/ezra/**` |
| EPB v1.0.0 contract unchanged | No edits under `docs/specs/epb_v1/**` |
| No dependency changes | No edits to `requirements.txt` or `pyproject.toml` |
| No workflow changes in this milestone’s planning scope | No edits under `.github/workflows/**` |
| Public boundary remains clean | `git ls-files .cursorrules docs/enhancements docs/prompts` → **empty** |
| M39 decision preserved | Text remains **GO WITH DOCUMENTED LIMITATIONS** where cited |
| No unapproved release operation during planning | No `gh repo edit`, `git tag`, `gh release create`, PyPI, Pages enable |

---

## 5. Operational Decision Points

### Decision A — Repository visibility

**Preferred path:** Make **public** only after explicit maintainer approval and successful preflight.

| Option | Benefits | Risks | Required checks before / after | Rollback / mitigation |
|--------|----------|-------|-------------------------------|------------------------|
| **A1 — Keep private for now** | No public clone surface; time for extra review | “Ready” state not visible to outsiders; Dependency Review / SLSA may stay in private-repo class | Preflight §6; document “ready-when-triggered” in governance | N/A (no visibility change) |
| **A2 — Make public after approval** | Open source posture; may unlock SLSA/attestation classes; community/clarity | Irreversible **social** footprint (forks/clones may persist); scans surface repo history | Full preflight §6; post-public §6; boundary check; record URL | GitHub can set repo private again; **forks and clones are not recalled** — obtain explicit approval |
| **A3 — Public only after manual review** | Defers risk until a second checkpoint | Delay | Same as A2 plus explicit second approval gate | Same honesty as A2 |

### Decision B — Tag / release (after visibility, if authorized)

**Visibility-first:** Do **not** assume a tag with the visibility flip.

| Option | Expected commands (illustrative — **do not run until authorized**) | Evidence to record | Risks | Rollback / mitigation |
|--------|---------------------------------------------------------------------|-------------------|--------|----------------------|
| **B1 — Visibility only** | None | Public URL, visibility JSON, `main` CI green | Users may not have a single “release” pointer | Document that `main` is canonical until a tag |
| **B2 — Annotated tag** (name TBD; e.g. semver or `v*-public` **only if approved**) | `git tag -a <tag> -m "..."`; `git push origin <tag>` | Tag name, annotated message, `git rev-parse <tag>^{}`, push log | Wrong SHA or message | Delete remote tag only if no consumers rely on it; prefer new corrected tag after governance review |
| **B3 — GitHub Release** | `gh release create <tag> --title "..." --notes-file ...` | Release URL, notes hash, attached artifacts if any | Notes overclaim limitations | Edit release notes; do not claim resolved limitations without evidence |
| **B4 — Tag + release after post-public CI** | B2 then B3 after `main` CI success on public repo | Combined evidence above | Race if CI fails post-public | Wait for green required jobs before tag |

**Do not** reuse historical milestone tags (e.g. `v1.0.2-m34`) as the **public announcement** tag unless the maintainer explicitly decides; those are **distribution/milestone** history, not necessarily the public visibility marker.

### Decision C — Pages / SLSA / Dependency Review

| Topic | Post-public planning check | Default M40 posture |
|-------|---------------------------|---------------------|
| **Dependency Review** | Open a test PR or rely on next PR; note if GHAS enables full gate | Document actual behavior; do not claim full dashboard without proof |
| **SLSA** | Re-read CI/Release workflow summaries; attestation runs when `repository_visibility == 'public'` | Record whether attestation step **succeeded** or is still skipped; README honesty |
| **Pages** | Docs build already proves Sphinx | **Do not** enable Pages during default visibility op; `EZRA_ENABLE_PAGES_DEPLOY` stays unset/false until authorized; then configure Pages source + variable |

---

## 6. Verification Plan

### 6.1 Preflight (before any authorized operation)

Run locally or in CI-aligned environment; expect clean working tree on release branch, empty boundary listing, and passing checks:

```bash
git status --short
git rev-parse HEAD
git ls-files .cursorrules docs/enhancements docs/prompts
ruff check .
ruff format --check .
mypy src
pytest -q
pip-audit -r requirements.txt
python scripts/verify_distribution.py --mode ci-local
gh run list --branch main --limit 5
```

**Expected:**

- Working tree clean (or only approved doc changes for the operation PR).
- `git ls-files` for boundary paths: **no output**.
- Lint, typecheck, tests, audit, distribution `ci-local` succeed.
- Latest `main` CI workflows: **success** (or document any known infra exceptions per M39).

### 6.2 Post-operation (only after maintainer authorizes visibility/tag/release)

```bash
gh repo view m-cahill/ezra --json visibility,url
gh release list --limit 5
gh run list --branch main --limit 5
git ls-remote --tags origin
git ls-files .cursorrules docs/enhancements docs/prompts
```

**Do not** run post-operation block during **planning-only** M40; record commands for the implementation phase.

---

## 7. Implementation Steps (future — after planning approval)

### Step 1 — Preflight

- Confirm current `main` SHA and that it matches the commit intended for public visibility.
- Confirm latest CI on `main` is green.
- Confirm `git ls-files` boundary check is empty.
- Re-read M39 limitations and `docs/release/PUBLIC_RELEASE_CHECKLIST.md`.

### Step 2 — Human approval gate

Stop. Obtain **explicit** approval for each:

- [ ] Change repo visibility to **public**
- [ ] Create annotated **tag** (name approved separately)
- [ ] Create **GitHub Release** and notes
- [ ] Enable **Pages** / set `EZRA_ENABLE_PAGES_DEPLOY`
- [ ] Any **branch protection** or org policy change

### Step 3 — Visibility operation (if authorized)

Illustrative only:

```bash
gh repo edit m-cahill/ezra --visibility public
```

**Not executed in M40 planning.** Confirm org allows visibility change; some orgs restrict this.

### Step 4 — Tag / GitHub Release (if authorized)

Illustrative only:

```bash
git tag -a <tag> -m "<message>"
git push origin <tag>
gh release create <tag> --title "<title>" --notes-file <file>
```

**Not executed in M40 planning.** Align tag with `pyproject.toml` / release policy if a version bump milestone is required (out of scope for this plan unless authorized).

### Step 5 — Post-operation evidence

Record in `M40_run1.md` / `M40_summary.md` / `M40_merge.md` (when those exist):

- `visibility`, `url` from `gh repo view`
- Tag names → SHA mapping
- Release URLs
- Representative CI run URLs post-public
- Boundary command output
- Whether each M39 limitation **persists** or **changed** (with evidence)

### Step 6 — Closeout

- Update `REFACTOR.md` and `docs/ezra.md` with M40 completion and links.
- Closeout prompts: if `docs/prompts/summaryprompt.md` or `docs/prompts/unifiedmilestoneauditpromptV2.md` are absent (M37 boundary), use **M36–M39** structure and record missing paths in closeout artifacts.
- Include: **ensure all documentation is updated as necessary**

---

## 8. Risk & Rollback Plan

| Risk | Mitigation |
|------|------------|
| Public repo exposes unintended files | Re-run `git ls-files` boundary check; run guardrail `pytest tests/test_public_release_boundary.py`; codebase review |
| Dependency Review behavior changes after public | Re-check on first PR; document in merge record |
| SLSA / attestation still fails or differs | Capture workflow logs; do not claim success in README until proven |
| Pages remain disabled | Expected default; docs build proves Sphinx; enable Pages only if authorized |
| Wrong tag SHA | Use annotated tags; verify `git rev-parse` before push; document in evidence |
| Revert visibility to private | GitHub UI/API may allow; **forks/clones are not recalled** — maintain explicit approval and comms |

---

## 9. Deliverables

### Planning (this milestone)

- `docs/milestones/M40/M40_plan.md` (this file)
- `docs/milestones/M40/M40_toolcalls.md`
- Updated `REFACTOR.md` (M40 section)
- Updated `docs/ezra.md` (M40 row)

### Future implementation (only if authorized)

- `docs/milestones/M40/M40_run1.md` (and increments if needed)
- `docs/milestones/M40/M40_summary.md`
- `docs/milestones/M40/M40_audit.md`
- `docs/milestones/M40/M40_merge.md`
- Optional: `docs/release/<release-notes>.md` if maintainer approves concrete notes file

---

## 10. Explicit Non-Goals

- No runtime, EPB spec, dependency, workflow, or secret-boundary mutations in planning-only phase.
- No `docs/prompts/` restoration.
- No claim that documented limitations are fully resolved.
- No marketing announcement draft unless explicitly requested.

---

## 11. Closeout Instructions

When M40 **implementation** completes (post authorization), generate:

- Summary per `docs/prompts/summaryprompt.md` if present
- Audit per `docs/prompts/unifiedmilestoneauditpromptV2.md` if present  
If absent, record missing paths in `M40_run*.md`, `M40_summary.md`, `M40_audit.md`, then follow **M36–M39** artifact structure.

Closeout must include:

```text
ensure all documentation is updated as necessary
```

---

## Release notes outline (optional content — for use when authorized)

Use factual bullets only.

1. **Project:** EZRA — runtime perception engine; EPB v1.0.0 artifact surface.
2. **Visibility:** Repository URL; date; `main` SHA referenced.
3. **Limitations (carry forward):**
   - Dependency Review / GHAS dependency graph
   - SLSA attestation — state **observed** result after visibility
   - Pages — gated unless separately enabled
4. **Verification:** Pointer to CI runs; local commands from §6.1.
5. **Non-goals:** No training-in-repo; RediAI integration is artifact-only (per README / `docs/ezra.md`).

---

## Final announcement checklist (governance)

- [ ] Public URL recorded in `docs/ezra.md` or `REFACTOR.md` (after operation)
- [ ] M39 limitations copied or updated with **observed** post-public status
- [ ] Tag/release URLs recorded if created
- [ ] CI green post-public for required jobs
- [ ] Boundary `git ls-files` re-run and empty
- [ ] No overclaims in notes (performance, SLSA, Dependency Review coverage)

---

ensure all documentation is updated as necessary
