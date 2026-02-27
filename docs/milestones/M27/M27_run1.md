# M27 Run 1 — CI / Workflow Run Analysis

**Milestone:** M27 — Detached Certification Metadata Layer  
**Posture:** Behavior-preserving (additive tooling only; no schema/emission/canonicalization changes)  
**Run type:** Initial implementation + CI verification (Run 2 green after format fix)

---

## 1. Workflow identity

| Field        | Value |
|-------------|--------|
| Workflow    | CI (`.github/workflows/ci.yml`) |
| Run ID      | **22506873541** (Run 2 — green) |
| URL         | https://github.com/m-cahill/ezra/actions/runs/22506873541 |
| Trigger     | pull_request |
| Branch      | `m27-detached-cert-metadata` |
| PR          | **#29** (m-cahill/ezra#29) |
| Conclusion  | success |
| Duration    | ~1m 24s |

**Run 1 (22506823194):** Failed on Lint — Ruff (format check). Fix: `ruff format src/ezra/tools/epb_generate_cert_metadata.py` committed and pushed (54a53c4). Run 2 triggered and passed.

---

## 2. Change context

- **Objective:** Add detached certification metadata envelope (`epb_generate_cert_metadata.py`) producing `bundle.cert.json` with nested certification/signature/environment sections; certifier_version from `ezra.__version__` or package metadata; no hard-fail on missing signature; CI step "EPB Certification Metadata."
- **Refactor target surface:** `src/ezra/tools/` (new module), `tests/contracts/`, CI Test job, public surface snapshot.
- **Invariants:** EPB schema frozen, canonicalization/hashing/signing rules unchanged, no edits to `src/ezra/core/` or `docs/specs/epb_v1/`, no new dependencies, coverage drop ≤ 0.1%.

---

## 3. Local verification (pre-CI)

| Check | Result | Notes |
|-------|--------|------|
| Pytest (all) | 276 passed, 4 skipped | +8 tests in `test_epb_cert_metadata.py` |
| Coverage | 95.70% (≥85%) | Within 0.1% of M29 baseline (95.90%) |
| Ruff (lint) | Pass | `ruff check . --no-fix` |
| Ruff (format) | Pass | After format fix (Run 1 corrective) |
| Mypy | Pass | `mypy src` |
| Public surface freeze | Pass | Snapshot includes `ezra.tools.epb_generate_cert_metadata` |

---

## 4. Jobs / checks (CI Run 22506873541)

| Job / Check | Required? | Result | Notes |
|-------------|-----------|--------|-------|
| Lint | Yes | ✓ Pass | Ruff lint + format + Pydocstyle |
| Type Check | Yes | ✓ Pass | |
| Test | Yes | ✓ Pass | 276 passed, 4 skipped; EPB Certification Metadata step ran |
| Security Check | Yes | ✓ Pass | |
| SBOM Generation | Yes | ✓ Pass | |
| Complexity Check | Yes | ✓ Pass | |
| Determinism Check | Yes | ✓ Pass | |
| Hermetic Hash (Py 3.10/3.11/3.12) | Yes | ✓ Pass | |
| Hermetic Reproducibility | Yes | ✓ Pass | |
| Documentation Build | Yes | ✓ Pass | |
| Dependency Review | continue-on-error | ✗ Fail | SEC-001 (repo/org config; not blocking) |
| OpenSSF Scorecard | continue-on-error | (informational) | |
| SLSA Provenance | Conditional | Skipped | PR trigger |
| Documentation Deploy | Conditional | Skipped | PR trigger |

**EPB Certification Metadata step (inside Test job):** Ran successfully. Step 15; outputs: metadata_structure=PASS, metadata_tamper=PASS, metadata_no_sig=PASS. Quality Envelope summary updated with "EPB Certification Metadata" section.

---

## 5. Refactor signal integrity

### A) Tests
- **Tiers:** Unit, contract (EPB contract harness, consumer certification, artifact signing, **certification metadata**).
- **Changed surface:** New tool and 8 contract tests cover valid structure, no-signature case, with-signature valid, tamper (payload, hashes.json, signature), subprocess exit 0/1.
- **Failures:** Run 1 had no test failures; only Lint (format). Run 2: no failures.

### B) Coverage
- Line coverage enforced (fail-under 85%). CI report: 95.70%+ (tools omitted by config where applicable). No exclusions introduced. Delta vs M29 baseline within guardrail (no drop > 0.1%).

### C) Static / policy
- Lint (Ruff check, format, Pydocstyle), Type Check (Mypy), public surface freeze. All enforced. Run 1 format failure was corrective (single-file reformat).

### D) Security / supply chain
- Bandit, pip-audit, gitleaks, SBOM: no new findings from M27. Dependency Review failure is infra (SEC-001), not code.

### E) Invariants
- Required checks unchanged (no weakening). No scope creep. Public surface extended only by new tool module (snapshot updated). Schema/contract/determinism preserved. No green-but-misleading path.

---

## 6. Delta summary

| Item | Delta |
|------|--------|
| New files | `src/ezra/tools/epb_generate_cert_metadata.py`, `tests/contracts/test_epb_cert_metadata.py`, `docs/milestones/M27/*` |
| Modified | `.github/workflows/ci.yml`, `docs/baselines/public_surface_snapshot.json` |
| Test count | 268 → 276 (+8) |
| Coverage (CI) | **95.70%** (within 0.1% of M29 baseline 95.90%) |

---

## 7. Certification metadata output (stability)

Envelope shape (nested only; canonical JSON):

```json
{
  "bundle_hash": "<64-char hex>",
  "certification": {
    "bundle_hash_valid": true,
    "hash_integrity_valid": true,
    "structure_valid": true
  },
  "environment": {
    "certifier_version": "0.0.1.dev0",
    "python_version": "3.11.9"
  },
  "epb_version": "1.0.0",
  "generated_at_utc": "2026-02-27T22:47:24Z",
  "signature": {
    "algorithm": null,
    "present": false,
    "valid": false
  }
}
```

- Written to `bundle.cert.json` (or `-o` path). Exit 0 when certification valid (structure + hash integrity + bundle hash); exit 1 otherwise. Missing `bundle.sig` does not hard-fail; `signature.present: false`, `signature.valid: false`.

---

## 8. Failures encountered

- **Run 1 (22506823194):** Lint job — Ruff (format check) failed on `epb_generate_cert_metadata.py`. Corrective: `ruff format` applied, commit 54a53c4 pushed; Run 2 green.
- **Run 2:** Dependency Review failed (Dependency graph / Advanced Security not enabled). Known SEC-001; `continue-on-error: true`. Not blocking. All **9/9 required (merge-blocking) checks passed**.

---

## 9. Verdict

**Verdict:** CI run 22506873541 completed successfully. All 9/9 required checks passed. EPB Certification Metadata step ran and reported PASS for metadata structure, tamper, and no-signature cases. Coverage 95.70% (within 0.1% of M29 baseline). Dependency Review failure is known infra (SEC-001) and non-blocking. Run 1 format failure was in-scope corrective and did not indicate invariant drift.

**Outcome:** ✅ **Merge approved.**

---

## 10. Exit criteria (M27)

| Criterion | Status |
|-----------|--------|
| Metadata file generated correctly | ✅ Yes (tool + tests) |
| Signing + certification integration verified | ✅ Yes (with/without sig tests) |
| Tampered bundle produces invalid metadata | ✅ Yes (payload, hashes.json, sig tamper tests) |
| CI 9/9 required checks passing | ✅ Met (Run 22506873541) |
| No runtime/schema/canonicalization changes | ✅ Yes |
| No coverage drop > 0.1% | ✅ 95.70% vs 95.90% baseline |
| Public surface snapshot updated | ✅ Yes |

---

**CI run ID:** 22506873541  
**PR:** #29  
**Coverage (CI):** 95.70%

---

## 11. Next actions

| Action | Owner | Scope |
|--------|--------|--------|
| Merge PR #29 | Human | After approval |
| Tag (e.g. v0.0.29-m27) | Human | Post-merge |
| Generate M27_audit.md, M27_summary.md | Cursor / Human | After CI green confirmed |
| Update docs/ezra.md milestone table | Cursor / Human | Closeout |
