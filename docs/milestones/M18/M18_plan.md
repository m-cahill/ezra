# M18 Plan — Enterprise Hardening: Security & Supply Chain Gate (Non-Behavioral Refactor)

**Milestone:** M18  
**Objective:** Strengthen EZRA's security, supply chain, and audit posture without changing runtime behavior  
**Baseline:** `v0.0.18-m17` (tag)  
**Status:** In Progress

---

## 1️⃣ Intent / Target

Strengthen EZRA's **security, supply chain, and audit posture** by introducing:

* Static security scanning (enhanced)
* Dependency vulnerability gating (dependency-review-action)
* SBOM generation (already present, verify)
* OpenSSF Scorecard (warn-first, SARIF upload)
* SLSA provenance attestations (job-level id-token)
* CI artifact evidence publication (enhanced)
* SSDF + ASVS alignment documentation (SECURITY.md)
* pydocstyle enforcement (Google convention, src/ only)
* pre-commit hooks
* Dependency lockfile (requirements-dev.txt from pyproject.toml)
* CODEOWNERS file
* Sphinx documentation build + GitHub Pages deployment

This milestone:

* **Does not change runtime behavior**
* **Does not change public APIs**
* **Does not change CLI output**
* **Does not change file formats**
* **Does not expand feature surface**

It is purely **governance & operational hardening**.

---

## 2️⃣ Scope Boundaries (Explicitly Out of Scope)

🚫 No feature work  
🚫 No workflow engine modification  
🚫 No domain logic refactors  
🚫 No test rewrites (only additive)  
🚫 No coverage threshold changes  
🚫 No architectural layer restructuring  
🚫 No async migration

This milestone must remain **operational hardening only**.

---

## 3️⃣ Invariants (Must Not Change)

| Invariant Surface               | Must Remain True      | Verification                |
| ------------------------------- | --------------------- | --------------------------- |
| All existing tests pass         | 100% unchanged        | CI green                    |
| Deterministic workflow behavior | Bit-identical outputs | Existing determinism checks |
| Coverage %                      | Must not drop         | Coverage gate               |
| Public API schemas              | No changes            | Contract diff (if present)  |
| Architecture layer rules        | No new violations     | import-linter               |
| Multi-tenant enforcement        | No regression         | existing isolation tests    |
| CI truthfulness                 | No muted failures     | No continue-on-error on required checks |

If any invariant breaks → rollback.

---

## 4️⃣ Verification Plan (Proof Over Narration)

CI must show:

* ✅ Ruff
* ✅ mypy
* ✅ pydocstyle (Google convention, src/ only)
* ✅ Radon (CC ≤ C)
* ✅ pytest + coverage ≥ current baseline (85%)
* ✅ Bandit (no HIGH)
* ✅ pip-audit strict pass
* ✅ Gitleaks pass
* ✅ Dependency Review (PR-only, merge-blocking)
* ✅ SBOM artifact uploaded
* ✅ SLSA provenance (job-level id-token, main + tags)
* ✅ Scorecard job executed (warn-first, SARIF upload, security-events: write)
* ✅ Job summary includes coverage + security summary
* ✅ Sphinx docs build & deploy (QA page)
* ✅ pre-commit hooks configured

All artifacts must be uploaded per run.

---

## 5️⃣ Implementation Steps (Ordered, Reversible)

### Step 1 — Phase 0 Pre-Flight (Idempotent)

* Detect:
  * Is this a Python package? ✅ Yes (setuptools, pyproject.toml)
  * Does a Dockerfile exist? ❌ No (check)
  * Is there already a CI workflow? ✅ Yes (.github/workflows/ci.yml)
* Add missing `.gitignore` entries for:
  * coverage (already present)
  * radon output (already present)
  * SBOM (already present)
  * build artifacts (already present)
  * Sphinx build output (`docs/_build/`, `docs/_static/`)
  * pre-commit cache (`.pre-commit-cache/`)

Commit: `chore(ci): preflight detection + hygiene`

---

### Step 2 — Phase 1: Tooling & Pre-Commit Hardening

Add:

* pydocstyle config (Google convention, src/ only, exclude tests/)
* mypy strict (already present, verify)
* pre-commit config (hooks for ruff, mypy, pydocstyle, bandit basic checks)
* requirements-dev.in (extract from pyproject.toml [project.optional-dependencies] dev)
* pip-compile lockfile (requirements-dev.txt)
* CODEOWNERS (if absent)

Verify:

```
pre-commit run --all-files
```

CI must pass lint/type/docstring checks.

Commit:

```
chore(ci): enforce lint/type/docstring gates (pydocstyle + pre-commit)
```

---

### Step 3 — Phase 2: Coverage & Complexity Enforcement

Verify:

* .coveragerc or pyproject.toml [tool.coverage.run] has branch=True ✅ (already present)
* Fail-under enforcement ✅ (already present, 85%)
* Complexity gate via radon ✅ (already present, grade C)

If repo has zero tests:

* Add minimal sanity test (non-invasive) — N/A (214 tests exist)

Verify:

* Coverage ≥ 85% lines
* Coverage ≥ 80% branches (if branch coverage enabled)

Upload coverage.xml artifact. ✅ (already present)

Commit:

```
chore(ci): verify coverage + complexity gates (no changes needed)
```

---

### Step 4 — Phase 3: Security & Supply Chain

Add CI jobs:

#### 🔐 Security Job (enhance existing)

* Bandit (fail on HIGH) ✅ (already present)
* pip-audit strict ✅ (already present)
* Gitleaks ✅ (already present)
* Upload JSON artifacts ✅ (already present)

#### 📦 SBOM Job (verify existing)

* cyclonedx-bom → sbom.cdx.json ✅ (already present)
* Upload artifact ✅ (already present)

#### 🏷 Provenance Job (NEW)

If packageable:

* `python -m build`
* `actions/attest-build-provenance@v1`
* Job-level permissions: `id-token: write`
* Trigger: `push` to `main` and tags

#### 📊 Scorecard Job (NEW, warn-first)

* ossf/scorecard-action@v2
* continue-on-error: true
* security-events: write (job-level)
* Upload SARIF to Security tab + artifact

#### 🔍 Dependency Review Job (NEW, PR-only)

* actions/dependency-review-action@v4
* Only on `pull_request` events
* Merge-blocking on PRs

If Dockerfile exists:

* Trivy image scan (fail HIGH/CRITICAL)
* Cosign keyless sign

Commit:

```
chore(ci): add security + supply chain gates (SSDF/SLSA/Scorecard)
```

---

### Step 5 — Phase 4: Documentation & Evidence Publish

Add:

* Sphinx minimal bootstrap (conf.py, index.rst, qa.rst)
* docs/qa.md (artifact index) — already exists, update with links
* SECURITY.md
  * Include SSDF SP 800-218 mapping
  * Note ASVS L2 reference
  * If AI/ML present → reference SSDF 800-218A note

CI:

* sphinx-build job (runs on PR and push)
* publish to GitHub Pages (separate job, main only)
* Upload pages artifact
* Job summary includes links

Commit:

```
docs(governance): add QA & Evidence page + SSDF mapping
```

---

## 6️⃣ Risk & Rollback Plan

If:

* Coverage drops
* Determinism breaks
* CI runtime explodes
* False positives block workflow

Rollback procedure:

1. Revert CI workflow file
2. Re-run baseline CI
3. Re-introduce security jobs one-by-one

This milestone is fully reversible because:

* No runtime logic touched
* No schema changes
* No DB migrations
* No API changes

---

## 7️⃣ Deliverables

At closeout, Cursor must produce:

* `M18_summary.md`
* `M18_audit.md`
* `M18_run1.md` (and subsequent runs if needed)
* Updated ledger row in `docs/ezra.md`
* CI proof screenshots / links
* Updated DeferredIssuesRegistry (if needed)

And then:

* Merge branch
* Tag appropriately
* Seed `M19_plan` stub

---

## 8️⃣ Locked Decisions

1. **pydocstyle:** Google convention, src/ only, blocking CI gate, small explicit ignore list allowed
2. **Sphinx:** Separate CI job (PR + push), Pages deploy only on main push
3. **SLSA provenance:** Job-level `id-token: write`, run on main push + tags
4. **Scorecard:** Warn-first, SARIF upload to Security tab, job-level `security-events: write`
5. **Dependency Review:** PR-only, merge-blocking
6. **pip-compile:** Lockfile artifact, pyproject.toml remains source of truth
7. **continue-on-error:** Scorecard explicitly non-blocking, documented in qa.md
8. **Public surface freeze:** Must not be affected by docstring/CI changes

---

**End of Plan**
