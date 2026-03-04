# M27 Audit — Detached Certification Metadata Layer

**Milestone:** M27  
**Mode:** DELTA AUDIT  
**Range:** e06d2c5...e7c4f1b  
**CI Status:** Green (Run 22506873541)  
**Refactor Posture:** Behavior-Preserving  
**Audit Verdict:** 🟢 Additive tooling only; invariants held; 9/9 required checks passed; no schema/canonicalization/hashing drift.

---

## 2. Executive Summary (Delta-First)

**Wins**
- Detached certification metadata envelope (`bundle.cert.json`) added; artifact evidence stack complete (bundle, hash, signature, reproducibility, cert metadata).
- Single new tool (`epb_generate_cert_metadata.py`) with nested envelope shape; certifier_version from canonical source; no hard-fail on missing signature.
- Eight new contract tests cover valid structure, no-sig, with-sig, tamper (payload, hashes.json, signature), subprocess exit 0/1; CI step "EPB Certification Metadata" required and passing.
- Public surface snapshot updated; no silent CI weakening; coverage 95.70% within guardrail.

**Risks**
- None identified. Run 1 Lint (Ruff format) failure was single-file corrective; no behavior or invariant impact.

**Most important next action**
- Proceed to M28 (Artifact-Only Distribution Mode) per authorized roadmap.

---

## 3. Delta Map & Blast Radius

**Changed:** `src/ezra/tools/epb_generate_cert_metadata.py` (new), `tests/contracts/test_epb_cert_metadata.py` (new), `.github/workflows/ci.yml` (new step + Quality Envelope), `docs/baselines/public_surface_snapshot.json` (one new module), `docs/milestones/M27/*`.

**Consumer surfaces touched:** New CLI entrypoint `python -m ezra.tools.epb_generate_cert_metadata`; new output file `bundle.cert.json` (additive; no change to existing EPB contents or emission).

**Risky zones:** None. No persistence, migrations, or boundary seams modified.

**Blast radius:** Breakage would show only if consumers depend on the new tool or `bundle.cert.json`; both are additive. Existing certification/signing flows unchanged.

---

## 4. Architecture & Modularity Review

- **Boundary violations:** None. Tool lives in `ezra.tools`; uses existing `epb_certify` and `epb_verify`; no core or specs touched.
- **Coupling:** Tool depends on certify/verify and `ezra.__version__`; appropriate for metadata aggregation.
- **Dead abstractions:** None.
- **Layering:** No leaks.

**Keep.** No fix or defer.

---

## 5. CI/CD & Workflow Audit

- Required checks: 9/9 passed (Lint, Type Check, Test, Security, SBOM, Complexity, Determinism, Hermetic matrix + Reproducibility, Docs Build).
- EPB Certification Metadata step: required, deterministic fixture, no conditional skip.
- Dependency Review: failed (SEC-001); continue-on-error; non-blocking.

**CI Root Cause Summary:** Run 1 failed on Ruff format; fixed in 54a53c4. Run 2 green.  
**Minimal Fix Set:** N/A (already applied).  
**Guardrails:** Existing; no new workflow bypass.

---

## 6. Tests, Coverage, and Invariants (Delta-Only)

- **Coverage delta:** 95.70% (CI); within 0.1% of M29 baseline 95.90%. No drop on touched code.
- **New tests:** 8 contract tests; cover envelope shape, no-sig, with-sig, tamper paths, CLI exit codes.
- **Invariant verification:** EPB schema frozen, canonicalization/hashing/signing rules unchanged, no core/specs edits — PASS.
- **Snapshot/golden:** Public surface snapshot updated; contract tests validate metadata shape and certification/signature flags.

**Missing Invariants:** None.  
**Missing Tests:** None.  
**Fast Fixes:** None.

---

## 7. Security & Supply Chain (Delta-Only)

- No dependency changes. No new secrets or trust expansion. SBOM/provenance continuity unchanged. Security Check passed.

---

## 8. Refactor Guardrail Compliance Check

| Guardrail | Status |
|-----------|--------|
| Invariant declaration | PASS (M27 plan + run1) |
| Baseline discipline | PASS (M29 baseline; delta reported) |
| Consumer contract protection | PASS (contract tests + snapshot) |
| Extraction/split safety | N/A |
| No silent CI weakening | PASS (new step required; no continue-on-error on correctness) |

---

## 9. Top Issues (Max 7, Ranked)

None. Milestone is clean; no HIGH/MED/LOW issues to list.

---

## 10. PR-Sized Action Plan

| ID | Task | Category | Acceptance Criteria | Risk | Est |
|----|------|----------|---------------------|------|-----|
| — | No further M27 actions | Closeout | M27 closed; tag pushed; audit/summary/ledger updated | None | — |

---

## 11. Deferred Issues Registry (Cumulative)

No new deferred issues. SEC-001 (Dependency Review) remains known infra; not M27-specific.

---

## 12. Score Trend (Cumulative)

| Milestone | Invariants | Compat | Arch | CI | Sec | Tests | DX | Docs | Overall |
|-----------|------------|--------|------|-----|-----|-------|-----|------|---------|
| M26 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5.0 |
| M27 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5.0 |

M27: Additive tooling only; no compat or arch impact; CI extended with one required step; tests and coverage within guardrail; no doc regression.

---

## 13. Flake & Regression Log (Cumulative)

No new flaky tests or behavior-drift events. Run 1 format failure was deterministic and fixed.

---

## Machine-Readable Appendix (JSON)

```json
{
  "milestone": "M27",
  "mode": "delta",
  "posture": "preserve",
  "commit": "e7c4f1b",
  "range": "e06d2c5...e7c4f1b",
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
    "invariants": 5,
    "compat": 5,
    "arch": 5,
    "ci": 5,
    "sec": 5,
    "tests": 5,
    "dx": 5,
    "docs": 5,
    "overall": 5.0
  }
}
```
