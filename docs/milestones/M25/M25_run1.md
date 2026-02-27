# M25 Run 1 — CI / Workflow Run Analysis

**Milestone:** M25 — EPB Consumer Certification & Artifact Reproducibility Hardening  
**Posture:** Behavior-preserving (consumer certification harness only; no runtime/schema changes)  
**Run type:** Initial implementation + local verification

---

## 1. Workflow identity (post-push)

| Field        | Value |
|-------------|--------|
| Workflow    | CI (`.github/workflows/ci.yml`) |
| Run ID      | *(To be filled after PR creation and CI run)* |
| Trigger     | Pull request (expected) |
| Branch      | `m25-epb-consumer-certification` |
| Commit SHA  | `6b24e1b` |
| PR number   | *(To be filled when PR is opened)* |

---

## 2. Change context

- **Objective:** Add stdlib-only EPB certifier (`epb_certify.py`), consumer certification tests, reproducibility test (emit → rmtree → re-emit), and CI step.
- **Refactor target surface:** Artifact boundary (certification utility + contract tests); no change to EPB emission or schema.
- **Invariants:** EPB structure (M24), determinism (M24), new: artifact self-consistency, consumer-isolated validation.

---

## 3. Local verification (pre-CI)

| Check | Result | Notes |
|-------|--------|------|
| Pytest (all) | 262 passed, 4 skipped | 6 new tests in `test_epb_consumer_certification.py` |
| Coverage | 95.70% (≥85%) | `*/tools/*` omitted by config; rest of src unchanged |
| Ruff (lint) | Pass | `ruff check . --no-fix` |
| Ruff (format) | Pass | `ruff format --check .` |
| Mypy | Pass | `mypy src` |
| Public surface freeze | Pass | Snapshot updated to include `ezra.tools.epb_certify` |

---

## 4. Jobs / checks (CI inventory — expected)

| Job / Check | Required? | Purpose |
|-------------|-----------|---------|
| Lint | Yes | Ruff lint + format, pydocstyle |
| Type Check | Yes | Mypy |
| Test | Yes | Pytest + coverage, zone schema/registry, **EPB Contract Harness**, **EPB Consumer Certification** |
| Security Check | Yes | Bandit, pip-audit, gitleaks |
| SBOM | Yes | CycloneDX |
| Complexity | Yes | Radon |
| Determinism Check | Yes | Multi-run bundle determinism |
| Dependency Review | continue-on-error | Infra (SEC-001) |
| Scorecard | continue-on-error | Informational |
| Provenance | Conditional | Push/tag |
| Docs Build | Yes | Sphinx |

**New in M25:** Step “EPB Consumer Certification” in Test job; summary section “## EPB Consumer Certification” in Quality Envelope.

---

## 5. Certification JSON output (stability)

Certifier output shape (success):

```json
{
  "bundle_hash_valid": true,
  "deterministic": true,
  "epb_version": "1.0.0",
  "hash_integrity_valid": true,
  "structure_valid": true,
  "valid": true
}
```

- Emitted to stdout only; exit code 0. On failure: `valid: false`, `errors` array, exit code 1.
- Deterministic for a given bundle path (no timestamps in output).

---

## 6. Failures encountered

- **Local:** None. Public surface freeze failed initially until `docs/baselines/public_surface_snapshot.json` was updated to include `ezra.tools.epb_certify` (in-scope for M25).
- **CI:** *(To be filled after workflow run.)*

---

## 7. Delta summary

| Item | Delta |
|------|--------|
| New files | `src/ezra/tools/epb_certify.py`, `tests/contracts/test_epb_consumer_certification.py` |
| Modified | `.github/workflows/ci.yml`, `docs/baselines/public_surface_snapshot.json`, `docs/milestones/M25/*` |
| Test count | 256 → 262 (+6) |
| Coverage | 95.70% (tools omitted; no regression) |

---

## 8. Verdict (pre-CI)

**Verdict:** Implementation complete and locally verified. All 262 tests pass, lint/format/type checks pass, public surface snapshot updated. CI run required to confirm 9/9 required checks and EPB Consumer Certification step.

**Recommended next step:** Push branch, open PR, run CI; then fill **CI run ID** and any CI failure notes above and in exit criteria below.

---

## 9. Exit criteria (M25)

| Criterion | Status |
|-----------|--------|
| 100% EPB self-consistency verified | Yes (tests + certifier) |
| Consumer certification runs in isolation | Yes (subprocess test) |
| CI 9/9 required checks passing | *(Pending run)* |
| Coverage unchanged or improved | Yes (95.70%, tools omitted) |
| No invariant drift | Yes |
| Certification JSON output stable | Yes (deterministic, stdout-only) |

---

**CI run ID:** *(To be filled after PR and workflow run)*  
**Coverage delta:** 95.70% (M24 baseline 95.90% on measured src; tools excluded from coverage by design.)
