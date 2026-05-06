# M37B — Required Gate Recovery Implementation

**Status:** Planned (not executed — authorized after M37A planning closeout).  
**Objective:** Implement truthful recovery for default-branch (and PR) CI gates identified in M37A, **without** weakening checks or falsely claiming capabilities GitHub denies.

**Prerequisite evidence:** `docs/milestones/M37A/M37A_plan.md`, `docs/milestones/M37A/M37A_run1.md`.

---

## Intent / target

- Clear **`pip-audit`** on the committed lockfile with **minimal** dependency movement.
- Make **Distribution Verification** meaningful for the events where it runs (fix 401 and/or scope triggers).
- Make **SLSA / attestation** posture **honest** on private user-owned repositories (no fake green, no silent red without explanation).
- Make **Documentation Deploy** truthful relative to **GitHub Pages** availability.
- **Dependency Review:** document as PR-only and settings-dependent; **not** a primary implementation target unless fixable without repo settings.

**Ensure all documentation is updated as necessary** when behavior or required settings change (e.g. `docs/release/DISTRIBUTION_VERIFICATION.md`, `docs/ezra.md`, `REFACTOR.md`).

---

## Scope boundaries

**In scope:** `pyproject.toml`, `requirements.txt` (via `pip-compile`), `.github/workflows/**`, release/docs as needed, scripts/tests only if required for verification truthfulness.

**Out of scope:** `src/ezra/**` behavior changes except where a dependency upgrade **forces** no code change goal — prefer pin bumps only; **M37** secret-boundary path cleanup; broad unrelated upgrades.

---

## Implementation tracks (priority order)

### Track 1 — Supply chain / `pip-audit` recovery (P1)

**Goal:** `pip-audit` (as invoked in CI: install from lockfile then audit) exits **0** truthfully.

**Allowed:**

- Minimal direct constraint bumps in `pyproject.toml` (pin floors consistent with below).
- Regenerate `requirements.txt` with `pip-compile` (same invocation as file header).
- Confirm transitive packages resolve to **at least** the minimum safe targets:

| Package | Minimum safe target |
| --- | --- |
| `cryptography` | `>=46.0.7` |
| `pillow` | `>=12.2.0` |
| `lxml` | `>=6.1.0` |
| `pytest` | `>=9.0.3` |
| `pygments` | `>=2.20.0` |
| `requests` | `>=2.33.0` |

**Rules:**

- Do not add advisory ignore lists or silence `pip-audit`.
- Do not modernize unrelated packages for “hygiene.”
- If resolution forces wider movement, document in `M37B_run1.md` / audit with rationale.

**Verification:** `pytest`, Security job, SBOM job, smoke/import surfaces as today.

---

### Track 2 — Distribution Verification recovery (P2)

**Goal:** The job must **verify something meaningful** and not fail spuriously with **HTTP 401** when it is supposed to run.

**M37A finding:** failure in `scripts/verify_distribution.py` → `_download_artifact_zip` → GitHub artifact ZIP API returns **401**.

**Choose one coherent approach (document in PR + release docs):**

1. **Fix token / permissions** so `GITHUB_TOKEN` (or designated secret) can read Release workflow artifacts from the same repo on PR/`main` / `workflow_dispatch` as designed.
2. **Split** jobs: PR/`main` runs **local** build/hash sanity checks without cross-workflow artifact download; **tag/release** workflow runs full artifact download verification.
3. **Restrict** artifact-download verification to **tag push** or **workflow_run** completion when `ezra-distribution` artifacts exist.
4. **Document** a required maintainer setting or PAT if GitHub’s default token cannot read artifacts on private repos.

**Rules:**

- Do not delete Distribution Verification.
- Do not mark green without a real check.
- Align `docs/release/DISTRIBUTION_VERIFICATION.md` with actual gating and merge semantics.

---

### Track 3 — SLSA Provenance / attestation honesty (P3)

**Goal:** Avoid **misleading** red CI and **false** claims when GitHub cannot persist attestations.

**M37A finding:** `actions/attest-build-provenance` errors: feature unavailable for **user-owned private** repositories.

**Plan options (pick one or combine):**

- **Condition** attestation steps on repository visibility / supported event (e.g. only when attestations API is available).
- Keep provenance **release-only** (`release.yml` / tag paths) and document limitation for private phase.
- **Explicit skip** job with clear step summary explaining limitation (truthful yellow/skip, not fake success).
- Do **not** claim full SLSA attestation is green when GitHub rejects persistence.

---

### Track 4 — Documentation Deploy / Pages (P4)

**Goal:** Documentation deploy reflects reality.

**Options:**

- Enable **GitHub Pages** in repo settings (maintainer action) if product requires public docs.
- **Gate** `docs-deploy` on Pages being enabled or on `workflow_dispatch` opt-in.
- Keep **Documentation Build** required; deploy may be conditional with documented reason (matches M19 class).

---

## Dependency Review note

- Remains **PR-only** and **GHAS/settings-dependent**.
- M37B **does not** treat Dependency Review as primary unless a code-only fix exists; prefer **documentation** in `REFACTOR.md` / release readiness.

---

## Invariants (carry forward)

- CI remains **truthful** (no muting required failures).
- No M37 secret-path cleanup in M37B unless explicitly merged into scope later.
- EPB schema and runtime contracts: **no change** unless a dependency forces a documented exception (unexpected).

---

## Deliverables (when M37B executes)

- Green or **honestly explained** CI for the chosen matrix.
- `M37B_run1.md` (or subsequent runs), `M37B_summary.md`, `M37B_audit.md` after implementation review.
- Updated `REFACTOR.md` and `docs/ezra.md`.

---

## Exit criteria

- `pip-audit` passes in CI with updated lockfile.
- Distribution Verification matches documented, truthful behavior (no unexplained 401).
- SLSA/Pages jobs do not **lie** about availability.
- Governance docs describe any remaining **acceptable** reds (e.g. Dependency Review without GHAS).

---

## Explicit non-goals

- M37 secret-boundary untracking / `.gitignore` campaign.
- Arbitrary major dependency upgrades beyond security minima.
- Merging to `main` without maintainer approval.
