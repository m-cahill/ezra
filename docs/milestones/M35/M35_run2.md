# M35 Run 2 & 3 — CI Workflow Analysis (Follow-up)

**Milestone:** M35 — EZRA Operating Manual (AI-Agent Ready, Verified)  
**Workflow:** CI  
**PR:** #36 (squash-merged as `457afb8`)

---

## Run 2 — CI Run ID 23362812040

**Trigger:** pull_request  
**Head SHA:** `cb56cc0` (after E501 fix in `scripts/verify_distribution.py`)  
**URL:** https://github.com/m-cahill/ezra/actions/runs/23362812040  
**Overall conclusion:** failure (workflow red)

### Required gates

| Job | Result | Notes |
|-----|--------|-------|
| Lint — Ruff (lint) | **Pass** | E501 remediation succeeded |
| Lint — Ruff (format check) | **Fail** | `tests/test_distribution_verification.py` would be reformatted |
| Type Check | Pass | |
| EPB Tools Minimal / Smoke / Test | Pass | |
| Security / SBOM / Complexity | Pass | |
| Determinism + Hermetic + Docs Build | Pass | |

### Infra / non-blocking (same as Run 1)

| Job | Result | Notes |
|-----|--------|-------|
| Dependency Review | Fail | GHAS not enabled — `continue-on-error` |
| Distribution Verification | Fail | HTTP **401** on artifact download — unchanged infra class |

### Verdict (Run 2)

**Mechanical follow-up:** `ruff format tests/test_distribution_verification.py` applied locally; committed as `2d483ab` and pushed.

---

## Run 3 — CI Run ID 23362922215

**Trigger:** pull_request  
**Head SHA:** `2d483ab` (after ruff format on test file)  
**URL:** https://github.com/m-cahill/ezra/actions/runs/23362922215  
**Overall conclusion:** failure (workflow red — Distribution Verification only among blocking-style jobs)

### Required gates

| Job | Result | Notes |
|-----|--------|-------|
| Lint (ruff check + format) | **Pass** | |
| Type Check | Pass | |
| EPB Tools Minimal / Smoke / Test | Pass | |
| Security / SBOM / Complexity | Pass | |
| Determinism + Hermetic + Docs Build | Pass | |

### Infra

| Job | Result | Notes |
|-----|--------|-------|
| Dependency Review | Fail | Non-blocking (SEC-001) |
| Distribution Verification | Fail | **401** — same as Runs 1–2; not a M35 regression |

### CI verdict for M35 closeout

- **All merge-relevant quality gates** (lint, typecheck, tests, determinism, hermetic, docs) **green** on Run 3.
- **Distribution Verification** failure is **infra-class** (token/artifact API permissions), explicitly **out of scope** for M35 per governance.
- **PR #36** squash-merged to `main` at **`457afb8`** with this understanding.

---

## Canonical references

- **Merge commit:** `457afb8` — `M35: EZRA Operating Manual (AI-Agent Ready, Verified) (#36)`
- **Run 1:** 23362721199 — see `M35_run1.md`
- **Run 2:** 23362812040
- **Run 3:** 23362922215
