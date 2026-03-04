# M32 — Reproducible Distribution Baseline

**Phase:** XVIII — Distribution & Supply Chain Hardening  
**Version Target:** v1.0.x (no feature bump)  
**Type:** Governance + Packaging Hardening  
**Scope:** EZRA repo only  
**No runtime or EPB changes allowed**

---

# 1. Intent

Make EZRA v1.0.0 a fully reproducible, supply-chain-hardened distribution artifact.

This milestone addresses the small remaining audit gaps identified in the full codebase audit (post–M31) and aims to bring the overall audit score from 4.75 → 5.0.

Specifically:

- Introduce deterministic dependency locking
- Pin GitHub Actions to immutable SHAs
- Close minor documentation gaps
- Preserve all EPB and canonicalization invariants

---

# 2. Hard Invariants (Non-Negotiable)

The following must NOT change:

- EPB schema
- Canonicalization logic
- Hashing logic
- Signing logic
- Plugin interfaces
- Zone registry format
- CI enforcement thresholds
- Coverage threshold (85%)
- Determinism checks
- Hermetic reproducibility logic

This is a packaging + governance milestone only.

---

# 3. Scope

## 3.1 Dependency Reproducibility (Primary)

Introduce a committed lockfile for deterministic installs.

Choose ONE:

- `pip-compile` → `requirements.txt`
- `uv lock` → `uv.lock`

Requirements:

- Lockfile committed
- CI install step updated to use lockfile
- Local dev flow remains simple
- CI remains green

Acceptance Criteria:

- Fresh clone + install from lockfile produces identical dependency graph
- CI passes unchanged
- No dependency drift between environments

---

## 3.2 Pin GitHub Actions to Full SHA

Replace tag-based usage:

- `actions/checkout@v4`
- `actions/setup-python@v5`
- `actions/upload-artifact@v4`
- Any other core actions

With full SHA references.

Acceptance Criteria:

- All critical actions pinned
- CI green
- No workflow behavior change

---

## 3.3 Documentation Quick Win

Add one sentence to `docs/ezra.md` §8:

> Parity and integration tests are skipped unless `EZRA_RUN_PARITY=1` or `EZRA_RUN_INTEGRATION=1` is set.

No structural doc changes.

---

## 3.4 Optional (Only If ≤15 LOC)

Add `docs/ci/CI_ARCHITECTURE.md` describing:

- Current required checks
- Determinism gate
- Hermetic matrix
- Optional future smoke tier

Pure documentation.

---

# 4. Out of Scope

- No CI threshold changes
- No new CI jobs
- No packaging split
- No PyPI publishing (that is M33)
- No RediAI integration
- No performance work
- No refactors
- No code movement

---

# 5. Verification Plan

After implementation:

1. Fresh clone
2. Install via lockfile
3. Run:
   - ruff
   - mypy
   - pytest
4. Confirm CI green
5. Confirm hermetic hash unchanged
6. Confirm EPB determinism unchanged

Compare against M31 baseline commit.

---

# 6. Acceptance Criteria

M32 is complete when:

- Lockfile committed and used in CI
- Actions pinned to SHA
- Docs updated
- CI passes with no threshold weakening
- Deterministic bundle hash unchanged
- No change to EPB artifacts

---

# 7. Risk Assessment

Risk: Low  
Blast Radius: CI + packaging only  
Rollback: Revert PR

---

# 8. Deliverables

- `requirements.txt` or `uv.lock`
- Updated `.github/workflows/ci.yml`
- Minor doc update
- `M32_run1.md`
- `M32_audit.md`
- `M32_summary.md`
- `M32_toolcalls.md`

---

# 9. Definition of Done

Audit score moves to 5.0.

Specifically closing:

- DEPS-001 (lockfile)
- CI-001 (action SHA pinning)
- DOC-001 (env var documentation)

No new technical debt introduced.
