# M35 — EZRA Operating Manual (AI-Agent Ready, Verified)

**Project:** EZRA
**Phase:** Post-Phase XVIII (Documentation Hardening)
**Milestone:** M35 — Operating Manual v1
**Refactor Posture:** Behavior-Preserving (documentation only)
**Objective Type:** Documentation & Governance Hardening

---

## 1. Intent / Target

Create a single authoritative EZRA operating manual (`docs/ezra_operating_manual_v1.md`) that:

- Is sufficient for a GPT/Cursor agent to operate EZRA with zero additional context
- Accurately documents the current implemented runtime surface
- Does not overstate unimplemented capabilities
- Aligns with VISION.md (architectural intent) and EPB spec (artifact contract)
- Matches the tone and discipline of the DARIA operating manual (style reference only)

This milestone introduces **no runtime changes**. It is a documentation + governance hardening milestone.

---

## 2. Scope Boundaries

### In Scope

- Create `docs/ezra_operating_manual_v1.md`
- Add link from `docs/ezra.md` to the new manual
- Add link from `README.md` to the new manual
- Add M35 to the milestone table in `docs/ezra.md`
- Generate M35 milestone artifacts (plan, toolcalls, summary, audit)

### Out of Scope

- No runtime code changes
- No EPB spec changes
- No new CLI or API surface
- No CI changes
- No `.cursorrules` changes (remains local-only per Q6 locked answer)
- No doc site redesign or broader documentation reorganization

---

## 3. Invariants (Must Not Change)

1. Runtime behavior unchanged
2. EPB contract unchanged
3. Existing public repo structure unchanged except for docs/linking
4. No new CLI/API/runtime claims beyond what code/specs prove

---

## 4. Authority Ordering

For behavioral claims in the manual, prefer:

1. Actual runtime code
2. EPB spec
3. docs/ezra.md
4. VISION.md
5. DARIA manual (style reference only, not EZRA source of truth)

---

## 5. Honesty Markers

The manual must use explicit markers:

- **Implemented** — feature exists in code
- **Not Yet Implemented** — declared in VISION.md but not present in code
- **UNKNOWN** — insufficient evidence to determine status

---

## 6. Document Structure

Required sections (adapted from DARIA style to EZRA reality):

0. Purpose & AI-Agent Instructions
1. System Overview
2. Core Mental Model
3. Core Concepts
4. Execution Flow
5. Plugin System
6. EPB Bundle Construction
7. Relationship to External Systems
8. Determinism Rules
9. How to Use EZRA
10. Debugging Guide
11. Extension Guide
12. v1 Guarantees (Frozen Surface)
Appendix A: Repository Structure
Appendix B: Quick Reference Commands

---

## 7. Verification Requirements

### Document Verification

- Every behavioral claim traceable to code/spec/docs
- Every example avoids nonexistent APIs
- All terminology internally consistent

### Repo Verification

- No runtime files changed
- Existing tests still pass
- No broken relative links introduced

### Drift Verification

- Manual does not contradict docs/ezra.md
- Manual does not contradict EPB spec
- Manual does not overstate VISION.md as implemented runtime truth

---

## 8. Deliverables

- `docs/ezra_operating_manual_v1.md`
- Updated `docs/ezra.md` (M35 in milestone table + link to manual)
- Updated `README.md` (link to manual)
- `docs/milestones/M35/M35_plan.md`
- `docs/milestones/M35/M35_toolcalls.md`
- `docs/milestones/M35/M35_summary.md`
- `docs/milestones/M35/M35_audit.md`

---

## 9. Exit Criteria

M35 closes only when:

- Operating manual created and internally consistent
- All behavioral claims traceable to code or spec
- No runtime behavior changed
- No EPB contract changed
- Links added to ezra.md and README.md
- Milestone artifacts generated
- Blind verification passed

---

## 10. Risk Assessment

Risk: **Minimal**
Blast Radius: Documentation only
Rollback: Revert PR
