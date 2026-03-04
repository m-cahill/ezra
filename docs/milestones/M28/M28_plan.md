# M28_plan — Artifact-Only Distribution Mode

---

## 1. Intent / Target

After M27, EPB artifacts are: structurally locked, deterministically reproducible, externally certifiable (stdlib-only), cryptographically attestable, hermetically reproducible, and carry detached certification metadata.

Validation tooling currently lives inside the full EZRA runtime package. M28 introduces a minimal, runtime-independent EPB validation surface that can be distributed and used **without the EZRA runtime engine**.

**Goal:** Allow downstream consumers to validate EPB bundles without installing OCR plugins, ML dependencies, or runtime orchestration code, with minimal dependency footprint. This strengthens artifact-boundary isolation and enables ecosystem distribution.

---

## 2. Scope

### In Scope

1. Extract artifact-validation tools into a clean, isolated module surface:
   - `epb_certify`
   - `epb_verify`
   - `epb_generate_cert_metadata`
2. Ensure they: import no runtime code, import no plugin code, import no ML libraries.
3. Keep single package; create isolated subpackage `src/ezra/epb_tools/`. No `ezra[epb-tools]` extras in M28.
4. CI: new required job "EPB Tools Minimal Environment" — fresh venv, `pip install .`, run only `pytest tests/contracts/test_epb_tools_*.py`, verify no runtime imports.
5. Backward compatibility: thin wrappers under `ezra.tools` with DeprecationWarning; do not remove old paths in M28.
6. Isolation test `test_epb_tools_import_surface.py` asserting no ezra.core, ezra.plugins, torch, easyocr in sys.modules after importing ezra.epb_tools.
7. Public surface snapshot updated (new `ezra.epb_tools` namespace; legacy wrappers still present).
8. Milestone scaffold + audit + summary.

### Out of Scope

- No refactor of OCR plugins
- No runtime code changes
- No schema changes
- No canonicalization changes
- No dependency upgrades (except packaging config)
- No new cryptography changes
- No pip extras `ezra[epb-tools]` (Phase VI)

---

## 3. Architecture Decision (Locked)

Keep a single package; create clearly isolated subpackage:

```
src/ezra/epb_tools/
```

NOT a new PyPI distribution. Tools currently in `ezra.tools` (epb_certify, epb_verify, epb_generate_cert_metadata) are relocated into `ezra.epb_tools`. Runtime-only utilities (e.g. _epb_hash, epb_sign, capture_easyocr_baseline) remain under `ezra.tools`.

---

## 4. Invariants (Must Not Change)

| Invariant                   | Must Hold |
| --------------------------- | --------- |
| EPB v1.0.0 schema frozen    | Yes       |
| Canonicalization rules      | Yes       |
| Hashing rules               | Yes       |
| Signing rules               | Yes       |
| Hermetic reproducibility    | Yes       |
| CI required checks          | Yes       |
| No runtime emission changes | Yes       |

---

## 5. Technical Work

### A. Directory Refactor

Move:

- `src/ezra/tools/epb_certify.py` → `src/ezra/epb_tools/epb_certify.py`
- `src/ezra/tools/epb_verify.py` → `src/ezra/epb_tools/epb_verify.py`
- `src/ezra/tools/epb_generate_cert_metadata.py` → `src/ezra/epb_tools/epb_generate_cert_metadata.py`

Replace originals with thin wrappers that delegate to `ezra.epb_tools.*` and emit DeprecationWarning.

### B. Isolation Enforcement

Add test `test_epb_tools_import_surface.py` asserting that after importing `ezra.epb_tools`, sys.modules does NOT contain: ezra.core, ezra.plugins, torch, easyocr.

### C. CI: EPB Tools Minimal Environment

New required job:

- Create fresh venv
- `pip install .`
- Optionally uninstall optional runtime deps if present (defensive)
- Run: `pytest tests/contracts/test_epb_tools_*.py`
- Must fail on import leakage

### D. Public Surface Snapshot

Update snapshot to reflect new `ezra.epb_tools` modules and legacy wrappers under `ezra.tools`.

---

## 6. Verification Plan

CI must show: all existing tests passing; EPB certification/signing tests passing; hermetic matrix passing; coverage ≥ 95%; new isolation test passing; no import leakage.

---

## 7. Exit Criteria

- EPB tools import without pulling runtime
- Minimal install test passes
- CI 9/9 required checks passing
- No invariant drift
- Audit verdict 🟢

---

## 8. Deliverables

- `docs/milestones/M28/M28_plan.md`
- `M28_run1.md`
- `M28_audit.md`
- `M28_summary.md`
- Updated snapshot
- CI proof
- Ledger update (on closeout)
