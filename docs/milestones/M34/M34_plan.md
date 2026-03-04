# M34 — Distribution Verification

**Phase:** XVIII — Distribution & Supply Chain Hardening  
**Version Target:** v1.0.x (no runtime changes)  
**Type:** Verification + Governance  
**Scope:** EZRA repo only  

**No runtime or EPB changes allowed**

---

## 1. Intent (Placeholder)

Validate release reproducibility, artifact hash stability, SBOM/provenance correctness, and PyPI Trusted Publishing configuration.

*Full plan TBD.*

---

## 2. Hard Invariants (Non-Negotiable)

Same as M33: EPB schema, canonicalization, hashing, signing, plugin interfaces, zone registry format, CI thresholds, coverage 85%, determinism, hermetic logic. No runtime logic changes.

---

## 3. Scope (TBD)

- Validate release workflow reproducibility.
- Verify artifact hashes stable across runs.
- Confirm SBOM and provenance correctness.
- Confirm PyPI Trusted Publishing configuration.

---

## 4. Deliverables (TBD)

- docs/milestones/M34/M34_plan.md (full plan)
- docs/milestones/M34/M34_run1.md
- docs/milestones/M34/M34_audit.md
- docs/milestones/M34/M34_summary.md
- docs/milestones/M34/M34_toolcalls.md
