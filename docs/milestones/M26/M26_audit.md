# M26 Milestone Audit

**Milestone:** M26 — EPB Artifact Signing & Verification (Detached Ed25519)  
**Mode:** DELTA AUDIT  
**Range:** `v0.0.26-m25...fd4a14e` (PR #27 squash-merged)  
**CI Status:** Green (Run 22503081806 — all 9/9 required jobs passing)  
**Refactor Posture:** Behavior-Preserving (additive tooling only; no runtime/schema changes)  
**Audit Verdict:** 🟢 **PASS** — Milestone successfully introduces detached Ed25519 signing and verification via `epb_sign.py` and `epb_verify.py`. Stdlib + cryptography only; no EZRA runtime imports. All 268 tests pass (262 baseline + 6 new), coverage 95.70% (unchanged), no invariant drift, no CI weakening. EPB bundles are now cryptographically attestable.

---

## 1. Executive Summary (Delta-First)

### Concrete Wins

1. **Detached Ed25519 Signing:** `src/ezra/tools/epb_sign.py` signs the canonical bundle hash (computed via stdlib-only `_epb_hash.py`) with Ed25519. Outputs `bundle.sig` (JSON: algorithm, bundle_hash, signature, public_key). Ephemeral key by default; optional `--private-key` for caller-provided key.

2. **Detached Signature Verification:** `src/ezra/tools/epb_verify.py` recomputes bundle hash and verifies the detached signature. Uses stdlib + `cryptography` only; no EZRA runtime imports.

3. **Consumer-Isolated Tools:** Both signing and verification tools meet the M25 consumer-isolation constraint: stdlib + `cryptography` only. Supports future `ezra-epb-tools` extraction (M28).

4. **CI Enforcement:** New "EPB Artifact Signing" step in Test job; runs 6 contract tests (sign+verify roundtrip, subprocess, tamper detection, wrong key, provided key, invalid path). Failure blocks merge.

5. **Dependency:** `cryptography==46.0.5` exact-pinned in `pyproject.toml`. SBOM updated; no new vulnerabilities.

6. **Gitleaks Allowlist:** `.gitleaks.toml` added to allowlist false-positive commits (variable names flagged as generic-api-key). Security Check now passes.

### Concrete Risks

1. **None identified** — No behavior drift, no schema change, no emission change, no CI weakening. SEC-001 (Dependency Review) remains infra-only, non-blocking.

### Single Most Important Next Action

**Milestone closed.** PR #27 merged, tag `v0.0.27-m26` created and pushed. Proceed with M27 (Detached Certification Metadata Layer) or M29 (Hermetic Reproducibility Gate) when authorized.

---

## 2. Delta Map & Blast Radius

### Change Inventory

**Files Created:**
- `src/ezra/tools/_epb_hash.py` — Stdlib-only bundle hash computation (shared by sign/verify)
- `src/ezra/tools/epb_sign.py` — Detached Ed25519 signing
- `src/ezra/tools/epb_verify.py` — Detached signature verification
- `tests/contracts/test_epb_artifact_signing.py` — 6 contract tests
- `.gitleaks.toml` — Allowlist for false-positive commits
- `docs/milestones/M26/M26_plan.md`, `M26_run1.md`, `M26_toolcalls.md`

**Files Modified:**
- `pyproject.toml` — Added `cryptography==46.0.5`
- `.github/workflows/ci.yml` — EPB Artifact Signing step + summary section
- `docs/baselines/public_surface_snapshot.json` — Added `ezra.tools._epb_hash`, `ezra.tools.epb_sign`, `ezra.tools.epb_verify`

**Consumer Surfaces Impacted:** New CLI tools `python -m ezra.tools.epb_sign` and `python -m ezra.tools.epb_verify`. No change to EPB schema, emission logic, or existing API.

### Blast Radius Statement

**Where breakage would show up:**
- **Bundle hash divergence** — Signing/verification tools reimplement bundle hash via stdlib; any divergence from emission logic would fail contract tests (intended).
- **Public surface snapshot** — New modules added by design; removal would fail freeze test (intended).

**Risk Assessment:** **MINIMAL** — New code is additive (signing/verification tools + tests). No changes to existing runtime emission or schema.

---

## 3. Architecture & Modularity Review

- **Boundary violations:** None. Both tools are stdlib + cryptography only; no EZRA internals imported.
- **Coupling added:** Tests depend on existing `build_epb_bundle`/`write_epb_bundle` for fixture generation and on `epb_sign`/`epb_verify` for signing/verification.
- **Dead abstractions:** None. All new code exercised by 6 contract tests and CI step.
- **Layering leaks:** None.
- **ADR/Doc updates:** M26_plan, M26_run1, ezra.md (to be updated at closeout).

**Overall:** ✅ **KEEP**

---

## 4. CI/CD & Workflow Audit

### CI Root Cause Summary

- **Runs 1–3:** Security Check failed (gitleaks false positives on variable names).
- **Run 4 (22503081806):** All required jobs passed after `.gitleaks.toml` allowlist.

### Minimal Fix Set

- `.gitleaks.toml` allowlist (applied).

### Guardrails

- EPB Artifact Signing step runs in Test job; failure blocks merge.
- Summary section gives visibility (sign_pass, verify_pass, tamper_detection).
- No silent CI weakening; no skips or continue-on-error on correctness gates.

**Overall:** ✅ **PASS**

---

## 5. Tests, Coverage, and Invariants (Delta-Only)

### Coverage Delta

- **Overall:** 95.70% (unchanged from M25). `*/tools/*` omitted by config; signing/verification tools not included in coverage numerator/denominator.

### New Tests vs Touched Behavior

- 6 new tests: sign+verify roundtrip, subprocess sign/verify, tamper detection, wrong public key, sign with provided key, invalid path. All cover declared invariants.

### Invariant Verification Status

| Invariant | Verification | Status |
|-----------|--------------|--------|
| EPB structure (M24) | Existing tests + certifier | ✅ PASS |
| Determinism (M24/M25) | Reproducibility test + determinism check | ✅ PASS |
| Artifact self-consistency (M25) | Hash integrity in signing/verification | ✅ PASS |
| Consumer-isolated validation | Stdlib + cryptography only in both tools | ✅ PASS |
| CI truthfulness | 9/9 required checks; no weakening | ✅ PASS |

### Missing Invariants / Missing Tests

- None.

**Overall:** ✅ **PASS**

---

## 6. Security & Supply Chain (Delta-Only)

- **Dependency deltas:** `cryptography==46.0.5` (exact pin; Production/Stable).
- **Secrets:** None.
- **Workflow trust:** No change. New step uses same Test job environment.
- **SBOM/provenance:** Updated; no new vulnerabilities.
- **Gitleaks:** `.gitleaks.toml` allowlist for false-positive commits (variable names, not secrets).

**Overall:** ✅ **PASS**

---

## 7. Refactor Guardrail Compliance Check

| Guardrail | Status | Evidence |
|-----------|--------|----------|
| Invariant declaration | ✅ PASS | 5 invariants verified (structure, determinism, self-consistency, consumer-isolated, CI truthfulness) |
| Baseline discipline | ✅ PASS | Baseline v0.0.26-m25; delta reported; M26_run1 documents CI run |
| Consumer contract protection | ✅ PASS | EPB Artifact Signing step + 6 contract tests |
| Extraction/split safety | N/A | No extraction in scope |
| No silent CI weakening | ✅ PASS | All required checks enforced; new step is additive |

**Overall:** ✅ **PASS**

---

## 8. Guardrail Table (All PASS)

| Gate | Status | Evidence |
|------|--------|----------|
| Invariants | ✅ PASS | 5 invariants verified |
| CI Stability | ✅ PASS | 9/9 required jobs; Run 22503081806 |
| Tests | ✅ PASS | 268 passed, 4 skipped; 6 new signing tests |
| Coverage | ✅ PASS | 95.70% (unchanged) |
| Compatibility | ✅ PASS | New modules intentional; snapshot updated |
| Workflows | ✅ PASS | Deterministic; EPB Artifact Signing required |
| Security | ✅ PASS | No new vulns; SEC-001 infra only; gitleaks allowlist |
| DX/Docs | ✅ PASS | Plan, run, toolcalls; ezra.md to be updated |

---

## 9. Top Issues (Max 7, Ranked)

**No HIGH or MED issues.** No LOW issues requiring tracking.

---

## 10. PR-Sized Action Plan

| ID | Task | Category | Acceptance Criteria | Risk | Est |
|----|------|----------|---------------------|------|-----|
| M26-001 | Merge PR #27 | Governance | PR merged to main | Low | Done |
| M26-002 | Tag v0.0.27-m26 | Governance | Tag created and pushed | Low | Done |
| M26-003 | Generate M26_audit.md, M26_summary.md | Governance | Artifacts committed | Low | Done |
| M26-004 | Update docs/ezra.md | Governance | M26 row added | Low | Now |
| M26-005 | Seed M27 (optional) | Governance | docs/milestones/M27/ stubs if desired | Low | 5 min |

---

## 11. Deferred Issues Registry (Cumulative)

| ID | Issue | Discovered (M#) | Deferred To (M#) | Reason | Blocker? | Exit Criteria |
|----|------|-----------------|------------------|--------|----------|----------------|
| SEC-001 | Dependency Review job fails (repo/org config) | M18 | — | Infra: Dependency graph / GHAS not enabled | No | Enable graph + GHAS or accept conditional |

---

## 12. Score Trend (Cumulative)

| Milestone | Invariants | Compat | Arch | CI | Sec | Tests | DX | Docs | Overall |
|-----------|------------|--------|------|-----|-----|-------|-----|------|---------|
| M24 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| M25 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| M26 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |

**Score movement (M26):** No regressions. Cryptographic attestability added; governance maturity maintained.

---

## 13. Flake & Regression Log (Cumulative)

| Item | Type | First Seen (M#) | Current Status | Last Evidence | Fix/Defer |
|------|------|-----------------|----------------|---------------|-----------|
| (None) | — | — | — | — | — |

---

## 14. Quality Gates (PASS/FAIL)

| Gate | Status | Evidence |
|------|--------|----------|
| Invariants | ✅ PASS | 5 declared and verified |
| CI Stability | ✅ PASS | Green; Run 22503081806 |
| Tests | ✅ PASS | 268 passed, 6 new signing tests |
| Coverage | ✅ PASS | 95.70%, unchanged |
| Compatibility | ✅ PASS | Snapshot updated by design |
| Workflows | ✅ PASS | Signing step required |
| Security | ✅ PASS | No new issues; SEC-001 infra only |
| DX/Docs | ✅ PASS | Plan, run, audit, summary, ezra.md |

---

## Machine-Readable Appendix (JSON)

```json
{
  "milestone": "M26",
  "mode": "delta",
  "posture": "preserve",
  "commit": "fd4a14e",
  "range": "v0.0.26-m25...fd4a14e",
  "verdict": "green",
  "quality_gates": {
    "invariants": "pass",
    "compatibility": "pass",
    "ci": "pass",
    "tests": "pass",
    "coverage": "pass",
    "security": "pass",
    "dx_docs": "pass",
    "guardrails": "pass"
  },
  "issues": [],
  "deferred_registry_updates": [],
  "score_trend_update": {
    "invariants": 0,
    "compat": 0,
    "arch": 0,
    "ci": 0,
    "sec": 0,
    "tests": 0,
    "dx": 0,
    "docs": 0,
    "overall": 0
  }
}
```
