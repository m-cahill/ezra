# M15_plan — CI Evidence & Deterministic Quality Envelope Hardening

## 1. Intent / Target

**Objective:**
Harden EZRA's CI surface to produce structured, auditable, machine-readable quality evidence without expanding runtime behavior.

This milestone:

* Adds structured CI job summaries
* Uploads machine-readable artifacts (coverage, radon, security JSON, etc.)
* Introduces deterministic quality dashboards
* Formalizes quality envelope contracts
* Does NOT change runtime logic

This is a **governance and signal-strengthening milestone**, not a feature milestone.

---

## 2. Scope Boundaries

### In Scope

* CI workflow updates only
* Artifact uploads
* Coverage + complexity reporting improvements
* JSON report generation
* Job summary enhancement
* Documentation: `docs/qa.md`
* Minor config additions (radon config, etc.)
* Deterministic report generation

### Explicitly Out of Scope

* No runtime code changes
* No new domain features
* No plugin additions
* No architectural layer movement
* No dependency upgrades beyond dev tooling
* No behavior changes

---

## 3. Invariants (Must Not Change)

| Invariant Surface              | Verification               |
| ------------------------------ | -------------------------- |
| All 205 tests pass             | CI pytest run              |
| 4 skipped tests remain skipped | CI output comparison       |
| Determinism script passes      | Existing determinism check |
| No new architecture violations | import-linter              |
| No behavior drift              | Full test suite            |
| Tag v0.0.15-m14 remains valid  | Git history check          |
| No public API changes          | Schema diff check          |

---

## 4. Verification Plan

Each change must be proven through CI artifacts:

### Required Evidence

* coverage.xml uploaded
* coverage summary in job summary
* radon JSON artifact
* bandit JSON artifact
* pip-audit JSON artifact
* SBOM (CycloneDX) artifact
* CI job summary page with:

  * Coverage %
  * Complexity grade summary
  * Security summary
  * Links to artifacts

### CI Must:

* Stay green
* Not weaken any existing gates
* Not reduce coverage %
* Not introduce flaky behavior

---

## 5. Implementation Steps (Ordered, Reversible)

### Step 1 — Pre-Flight Detection (Idempotent)

* Detect:

  * Existing Dockerfile?
  * Existing coverage config?
  * Existing docs folder?
* Add missing `.gitignore` entries for:

  * coverage.xml (already present)
  * sbom.cdx.json
  * bandit.json
  * pip_audit.json
  * radon.json

No behavior change.

---

### Step 2 — Coverage Formalization

Enhance existing `pyproject.toml` coverage config (do NOT create `.coveragerc`).

Keep `source = ["src"]` and `--cov=src`.

Modify CI to:

* Add artifact uploads (already present)
* Enhance summary block in `$GITHUB_STEP_SUMMARY`

---

### Step 3 — Complexity Gate

Add radon step:

```
radon cc -s -n C . > radon.txt
radon cc -j . > radon.json
```

Fail build if any grade worse than C.

Upload radon.json artifact.

Add summary table:

* Average complexity
* Worst file
* Count of C grades

---

### Step 4 — Security Surface (Fail-Fast)

Add CI security job:

* bandit → fail on HIGH
* pip-audit → strict
* gitleaks → detect mode (using gitleaks/gitleaks-action)

Upload:

* bandit.json
* pip_audit.json
* gitleaks.json

Add summary block to job summary.

This is enforcement, not reporting.

---

### Step 5 — SBOM + Supply Chain Evidence

Add:

```
cyclonedx-py -o sbom.cdx.json -e
```

Upload artifact.

Do not block build for Scorecard (warn-first).

---

### Step 6 — Structured CI Summary

Add consolidated summary section:

```
## EZRA Quality Envelope

### Coverage
Lines: X%
Branches: Y%

### Complexity
Worst Grade: C
Files > C: 0

### Security
Bandit HIGH: 0
pip-audit: clean
Gitleaks: clean

### Determinism
Byte-identical bundle confirmed

Artifacts:
- coverage.xml
- radon.json
- bandit.json
- pip_audit.json
- sbom.cdx.json
```

This creates an **audit-ready single-page surface**.

---

### Step 7 — Docs

Create:

`docs/qa.md`

Include:

* What each gate enforces
* How to reproduce locally
* Mapping table to:

  * NIST SSDF
  * OWASP ASVS L2
  * OpenSSF Scorecard
  * SLSA provenance

This connects EZRA to RediAI-grade governance posture.

---

## 6. Risk & Rollback Plan

### Risks

* Radon false positives
* pip-audit strict failures
* CI duration increase
* Tool version instability

### Mitigation

* Pin versions in pyproject.toml dev extras
* Fail early with clear logs
* Rollback by:

  * Removing new workflow file
  * Reverting to previous CI config

Revert is clean and isolated to CI files.

---

## 7. Deliverables

* CI workflow updates
* `docs/qa.md`
* Uploaded artifacts per run
* CI summary enhancement
* Updated milestone table in `docs/ezra.md`
* M15 folder seeded and populated

---

# M15 Closeout Instructions (Explicit Cursor Handoff)

After CI is green:

1. Generate:

   * `docs/milestones/M15/M15_summary.md`
   * `docs/milestones/M15/M15_audit.md`
2. Update `docs/ezra.md`
3. Tag: `v0.0.16-m15`
4. Verify determinism
5. Merge
6. Create M16 stub folder

No additional commits after closeout.

---

# Strategic Rationale

M15:

* Strengthens audit signal
* Makes EZRA enterprise-evidence ready
* Preserves runtime invariants
* Raises governance surface without risk
* Keeps milestones small and non-overlapping (your Phase discipline)

This aligns with your broader AI-native governance approach.
