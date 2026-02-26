

## Cursor Handoff Prompt — Baseline Codebase Audit for Refactoring Program

You are Cursor AI operating as a **Refactoring Audit Lead**. This is **not** greenfield. Your job is to analyze the existing repository, identify refactor targets and risks, and produce a **complete audit pack** that will become the governance baseline for all future milestones.

This audit begins by identifying client priorities (stability, velocity, compliance, maintainability, or cost reduction).
Findings and recommendations are prioritized accordingly.


### default posture posture

* Default assumption is **behavior preservation** unless explicitly authorized later.
* Audit outputs must by default be **evidence-based** (paths, line numbers, command output, CI links).
* Prefer **small, verifiable milestones**; avoid big-bang rewrites.
* Treat CI as a **truth signal**; “green” is not automatically “safe.”

---

# A) Recon & Evidence Collection (run locally)

## A1. Repo facts (record outputs verbatim)

Run and capture:

* `git status`
* `git log -1`
* `git remote -v`
* `git branch --show-current`
* `git ls-files | wc -l`
* LOC snapshot (choose one):

  * `python -m pip install tokei && tokei`
  * or `cloc .`
* Dependency manifests present:

  * list any of: `pyproject.toml`, `requirements*.txt`, `poetry.lock`, `Pipfile.lock`, `package.json`, `pnpm-lock.yaml`, `yarn.lock`, `Dockerfile`, `docker-compose.yml`

## A2. Run tests / checks (best effort)

Detect the current toolchain and run what exists:

* Python:

  * `python -V`
  * `python -m pip install -r requirements.txt` (or project equivalent)
  * `pytest -q` (if present)
  * if coverage configured: `pytest --cov` (record result)
* Node (if present):

  * `node -v`
  * `npm test` / `pnpm test` / `yarn test` (record result)
* If nothing runs, record that as a **finding** and propose the minimal “sanity harness” needed to establish baseline truth.

## A3. CI state (if GitHub Actions exists)

* List workflows: `.github/workflows/*`
* If you have access to run CI, run it once on a branch: record URL(s), failing jobs, logs.
* If you cannot run CI, do a static audit of workflows and identify risks: action pinning, permissions, missing gates, caching, etc.

---

# B) Baseline Audit (produce an “Audit Pack”)

Create the following documents under:

`docs/refactor/audit/`

Each file must by default be **complete** and written as if it will be read by a third-party reviewer.

---

## B1) `BASELINE_AUDIT.md`

A full codebase audit in **BASELINE RESET** mode using the structure and rigor of our unified milestone audit prompt.

Mandatory sections:

1. Header (Mode = BASELINE RESET, CI Status, Verdict)
2. Executive Summary (wins/risks/one next action)
3. Delta Map & Blast Radius (for baseline: major surfaces)
4. Architecture & Modularity Review
5. CI/CD & Workflow Audit
6. Tests, Coverage, and Invariants (baseline status)
7. Security & Supply Chain (baseline status)
8. Guardrail Compliance Check (baseline)
9. Top Issues (max 7, ranked, with Observation/Interpretation/Recommendation/Guardrail/Rollback)
10. PR-sized action plan (3–10 items)
11. Deferred Issues Registry (initialize)
12. Score Trend (initialize baseline row)
13. Flake & Regression Log (initialize)
14. Machine-readable JSON appendix

**Evidence rule:** every issue must by default cite either file+line or workflow+job+step, with excerpts ≤10 lines.

---

## B2) `SYSTEM_SURFACES.md`

Define what is “externally observable” for this repo:

* Public APIs (HTTP, CLI commands, library exports)
* File formats / serialized artifacts
* Config formats
* Model artifacts (if ML)
* Integration points (DB, queues, external services)
* Any downstream consumers known or implied

This is the map we’ll protect during refactors.

---

## B3) `INVARIANTS_CATALOG.md`

Create a refactor-first invariants catalog:

* **Invariant** (must by default not change)
* **Surface** (where)
* **Verification method** (test/snapshot/schema)
* **Current coverage** (present/missing)
* **Priority** (P0/P1/P2)
* **Notes** (what could drift)

If invariants cannot be proven today, mark them as **unverified** and propose the minimal harness needed.

---

## B4) `REFACTOR_PHASE_MAP.md`

Propose a phased plan with **small milestones** (non-overlapping), each milestone containing:

* Intent / scope boundaries
* Invariants protected
* Verification plan
* Expected risk / rollback
* Deliverables (docs, tests, CI changes)

Constraints:

* Milestones must by default be **PR-sized** where feasible.
* Prioritize “truth & safety first”: tests/CI/invariants before major restructuring.

---

## B5) `MODULE_BOUNDARY_MAP.md`

Produce a practical boundary map:

* Current modules/packages
* Dependency directions (who imports whom)
* Coupling hotspots (god modules, cycles, shared globals)
* Suggested “future boundaries” (what should be separated)

If relevant, include a simple dependency diagram (Mermaid OK).

---

## B6) `TESTING_GAPS_AND_PLAN.md`

* Current test inventory (unit/integration/e2e)
* Coverage snapshot (overall + touched surfaces)
* Flake risks / nondeterminism
* Minimal additions required to support safe refactoring:

  * regression tests
  * golden files / snapshots
  * contract tests
  * smoke tests

Include a short table: *Gap → Risk → Minimal fix → Gate location (CI/local)*.

---

## B7) `CI_GAPS_AND_GUARDRAILS.md`

* Required checks (current vs recommended)
* Any silent skipping / continue-on-error / conditional holes
* Action pinning and permissions posture
* Recommendations for guardrails that prevent repeat failures:

  * preflight scripts
  * workflow contract checks
  * deterministic installs
  * caching rules
  * artifact retention

Keep changes minimal; propose staged adoption if needed.

---

## B8) `SECURITY_AND_SUPPLY_CHAIN_BASELINE.md`

* Dependency posture and risk (including lockfile status)
* Secret scanning posture
* SBOM/provenance posture (present/missing)
* CI trust boundaries (permissions, unpinned actions)
* Top 3 supply-chain risks + minimal mitigations

---

## B9) `DEFINITION_OF_DONE.md`

This is a key output.

Define what “done” means for the overall refactoring program, as a **checklist of measurable outcomes**, including:

### 1) Behavioral safety

* invariants declared and verified
* compatibility preserved (or intentional breaks have migration plan)

### 2) Quality gates

* tests passing
* coverage thresholds (appropriate to repo)
* lint/type checks stable

### 3) CI truthfulness

* no silent bypasses
* required checks aligned with branch protection
* deterministic workflows

### 4) Security posture

* no secrets
* dependency audits
* SBOM/provenance targets (if applicable)

### 5) Architectural outcome

* boundaries achieved (what “separated” means)
* extraction goals (if repo split is planned)

Include a short “Done = evidence” section: which artifacts/CI proofs must by default exist to claim completion.

---

# C) Output Packaging Requirements

At the end, produce:

## C1) `docs/refactor/audit/README.md`

A table of contents linking all documents in the audit pack with 1–2 lines each explaining what it’s for.

## C2) “Top 10 Next Actions” summary

In the root of the PR description (or a `docs/refactor/audit/NEXT_ACTIONS.md`), list the top 10 PR-sized tasks with IDs.

---

# D) Guardrails for Scope Control

* Do **not** implement refactors yet unless explicitly authorized.
* Do **not** change behavior unless explicitly authorized.
* Do **not** do broad formatting sweeps unless explicitly authorized.
* Only create documents and (if absolutely necessary) minimal scripts to capture evidence (e.g., “loc script” or “dependency tree capture”).
* If you must by default add a minimal test harness to run anything at all, keep it to a single “sanity test” and document it as a baseline-enabling change.

---

# E) Deliverable Summary (must by default be present)

At the end of your work, output a short summary containing:

* repo facts (LOC, language mix, last commit, test status)
* CI status (if available)
* top 7 issues (IDs + severity)
* recommended next milestone (M01) with a one-paragraph rationale


