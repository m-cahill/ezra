# EZRA v1.0.0 — Enterprise-Certified Release

**Release tag:** v1.0.0  
**Milestone:** M31 — v1.0.0 Release Gate  
**Date:** 2026-02-28  

---

## Summary

EZRA (Extensible Zone-Based Runtime Architecture) v1.0.0 is the first semantically versioned enterprise-certified release. This release freezes the EPB (EZRA Perception Bundle) contract at a tagged boundary and establishes the governance baseline for future v1.x and v2.0 work.

**No behavioral changes since v0.0.31-m30.** This release consists solely of:

- Version constant set to `1.0.0` (no dev suffix)
- Phase V completion declaration updated to reference the certified release tag v1.0.0

---

## CI Evidence

- **CI Run:** [22509645140](https://github.com/m-cahill/ezra/actions/runs/22509645140)
- **Conclusion:** All required jobs passed (Lint, Type Check, Test, EPB Tools Minimal, Security, SBOM, Complexity, Determinism, Hermetic Reproducibility, Documentation Build)
- **Hermetic reproducibility:** Canonical bundle hash identical across Python 3.10, 3.11, and 3.12

---

## Hermetic Baseline Hash (M29)

Canonical bundle hash (fixed hermetic fixture; unchanged from M29):

```
c186777c33b7b7b9d11540bda7398efd0dfb085143506513a4ce87836c6ac7c2
```

All three interpreters (3.10 / 3.11 / 3.12) produce this exact value. No drift in canonicalization or hashing logic.

---

## Determinism

- Determinism gate passed: byte-identical EPB bundles across N≥3 runs.
- No schema, canonicalization, or hashing changes in M31.

---

## SBOM

- CycloneDX SBOM is generated in CI and available as a workflow artifact for run [22509645140](https://github.com/m-cahill/ezra/actions/runs/22509645140) (SBOM Generation job).

---

## Governance

- **Phase V completion declaration:** [docs/phase_v_completion_declaration.md](https://github.com/m-cahill/ezra/blob/v1.0.0/docs/phase_v_completion_declaration.md)
- EPB contract frozen at v1.0.0. Future EPB/schema/hashing changes require a new milestone and explicit versioning.

---

## What's Next

- **v1.x:** Public surface or non-contract changes → minor version milestones
- **v2.0.0:** EPB contract change, schema change, or hashing rule change → major version milestone

EZRA is now in **product governance mode**, not hardening mode.
