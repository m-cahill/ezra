# Milestone Summary — M27

**Project:** EZRA  
**Phase:** Phase V (Release Lock / artifact-governed posture)  
**Milestone:** M27 — Detached Certification Metadata Layer  
**Timeframe:** 2026-02-27  
**Status:** Closed  
**Baseline:** e06d2c5 (M29 merge); tag v0.0.28-m29  
**Refactor Posture:** Behavior-Preserving

---

## 1. Milestone Objective

Aggregate scattered certification artifacts (hashes.json, bundle.sig, certification stdout) into a single **detached certification metadata envelope** (`bundle.cert.json`) for archival, compliance, and external indexing. Without this, attestation evidence remains fragmented and harder to consume in downstream workflows.

---

## 2. Scope Definition

### In Scope
- New tool: `epb_generate_cert_metadata.py` (output `bundle.cert.json` or `-o` path).
- Envelope: nested sections only (certification, signature, environment); canonical JSON.
- Contract tests: valid structure, no-signature case, with-signature valid, tamper (payload, hashes.json, signature), subprocess exit 0/1.
- CI: required step "EPB Certification Metadata" in Test job; Quality Envelope summary updated.
- Public surface snapshot and M27 milestone scaffold (plan, run1, toolcalls, audit, summary).

### Out of Scope
- No embedding into EPB directory; no schema/emission/canonicalization/hashing changes; no new dependencies; no PKI/revocation; no edits to `src/ezra/core/` or `docs/specs/epb_v1/`.

---

## 3. Refactor Classification

**Change Type:** Boundary refactor (additive tool; new output artifact).  
**Observability:** New CLI and new file `bundle.cert.json`; existing EPB contents and emission unchanged.

---

## 4. Work Executed

- Implemented `epb_generate_cert_metadata.py`: calls `certify()` and `verify_bundle()` when `bundle.sig` present; builds nested envelope; writes canonical JSON; exit 0/1 by certification validity only (no hard-fail on missing sig).
- `certifier_version` from `ezra.__version__` → package metadata → `"unknown"`.
- Added 8 contract tests; added CI step and Quality Envelope section.
- Updated public surface snapshot; Run 1 Ruff format failure corrected in follow-up commit.

---

## 5. Invariants & Compatibility

**Declared invariants (unchanged):** EPB v1.0.0 schema frozen; canonicalization, hashing, signing rules; hermetic reproducibility; no coverage drop > 0.1%.

**Compatibility:** Backward compatibility preserved. No breaking changes. No deprecations. New surface only (tool + file).

---

## 6. Validation & Evidence

| Evidence Type    | Tool/Workflow           | Result   | Notes                                      |
|------------------|-------------------------|----------|--------------------------------------------|
| Unit/contract    | pytest                  | 276 pass | +8 in test_epb_cert_metadata.py            |
| Coverage         | pytest-cov              | 95.70%   | Within 0.1% of M29 baseline                 |
| Lint/format      | Ruff                    | Pass     | After format fix (Run 2)                    |
| Type             | Mypy                    | Pass     |                                            |
| Public surface   | Snapshot diff           | Pass     | New module added to snapshot               |
| CI               | Run 22506873541         | Green    | 9/9 required checks                        |
| EPB Cert Metadata| Test job step 15        | Pass     | metadata_structure, metadata_tamper, metadata_no_sig |

---

## 7. CI / Automation Impact

- One new required step: "EPB Certification Metadata" (pytest tests/contracts/test_epb_cert_metadata.py).
- Quality Envelope summary extended with "EPB Certification Metadata" section.
- No checks removed or weakened. No signal drift. Dependency Review remains continue-on-error (SEC-001).

---

## 8. Issues, Exceptions, and Guardrails

- **Run 1 Lint (Ruff format):** One file reformatted; committed and pushed; Run 2 green. No guardrail change.
- **Dependency Review:** Failed (SEC-001); non-blocking; pre-existing.

No new issues introduced. No new deferred work.

---

## 9. Deferred Work

None. SEC-001 (Dependency Review) pre-existing; status unchanged.

---

## 10. Governance Outcomes

- Artifact evidence stack is now complete: canonical bundle, hash integrity, detached signature, cross-interpreter reproducibility, **detached certification metadata envelope**.
- Envelope format is canonical and documented; contract tests lock shape and certification/signature semantics.
- CI truthfulness preserved; new step is required and deterministic.

---

## 11. Exit Criteria Evaluation

| Criterion                              | Status | Evidence |
|----------------------------------------|--------|----------|
| Metadata file generated correctly      | Met    | Tool + tests |
| Signing + certification integration   | Met    | With/without sig tests |
| Tampered bundle → invalid metadata     | Met    | Payload/hashes/sig tamper tests |
| CI 9/9 required checks passing        | Met    | Run 22506873541 |
| No runtime/schema changes             | Met    | Additive tool only |
| Audit verdict 🟢                      | Met    | M27_audit.md |

---

## 12. Final Verdict

Milestone objectives met. Refactor verified safe. Additive tooling only; invariants held; CI green. Proceed.

---

## 13. Authorized Next Step

**Next milestone:** M28 — Artifact-Only Distribution Mode (lightweight EPB validation package; artifact validation without full runtime install). No post-merge commits to the M27 branch.

---

## 14. Canonical References

- **Commits:** e7c4f1b (merge), 391fa5d (run report), 54a53c4 (format fix), 80c1f59 (M27 implementation).
- **PR:** #29 — M27: Detached Certification Metadata Layer.
- **Tag:** v0.0.29-m27.
- **CI run:** https://github.com/m-cahill/ezra/actions/runs/22506873541.
- **Docs:** docs/milestones/M27/M27_plan.md, M27_run1.md, M27_audit.md, M27_summary.md, M27_toolcalls.md.
