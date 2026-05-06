# M37_plan — Public Release Boundary Cleanup

**Status:** Stub seeded by M36. **Do not implement until M36 is merged/accepted and M37 is explicitly started.**

---

## Intent

Remove **only** the user-approved company-secret paths from Git tracking (where applicable), add `.gitignore` and automation/guardrail patterns that prevent reintroduction, and document the public clone boundary.

## Approved paths (from M36 reconciliation)

- `.cursorrules`
- `docs/enhancements/`
- `docs/prompts/`

## Preconditions

- M36 closed with verdict **Closed — Proceed to M37**.
- Re-read `docs/release/AUDIT_RECONCILIATION_M33_M35.md` and `REFACTOR.md`.

## Out of scope for this stub

- Any implementation, commits, or workflow changes.
