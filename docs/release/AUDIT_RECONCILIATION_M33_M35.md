# Audit Reconciliation — M33/Post-M32 vs M35

## 1. Purpose

Reconcile two materially different full-audit scores for EZRA before any audit-driven remediation:

- **M33/Post-M32 audit:** weighted **4.95 / 5.0** (`docs/M33fullaudit.md`).
- **M35/current audit:** weighted **4.40 / 5.0** (external planning artifact; **not** committed in M36).

This document determines whether the score drop reflects true regression, audit calibration drift, stricter public-release criteria, missing evidence, or items to schedule in M37/M38—**without** changing code, CI, schemas, or dependencies.

---

## 2. Inputs

| Input | Location | Notes |
| --- | --- | --- |
| M33/Post-M32 audit | `docs/M33fullaudit.md` | Baseline; commit `23789314ba5f6a502c650f6a098f12eb4ed0e8b4` per that file |
| M35/current audit | External planning artifact (May 2026 handoff) | Used for score reconciliation; **not** copied into repo during M36 per release-prep policy |
| Current repo HEAD (M36 execution) | `f12fd083b1b0e9f9c518535e0938b65d204b5075` | Recorded in `docs/milestones/M36/M36_run1.md` |
| M33 baseline commit (diff anchor) | `23789314ba5f6a502c650f6a098f12eb4ed0e8b4` | Used for `git diff` scope in M36 |
| Refactor ledger | `REFACTOR.md` | Created in M36; records verdict and M37 authorization |

---

## 3. Score Comparison

| Category | M33/Post-M32 Score | M35 Score | Delta | Reconciliation |
| --- | ---: | ---: | ---: | --- |
| Architecture | 5 | 5 | 0 | No regression indicated. |
| Modularity / Coupling | 5 | 4 | −1 | **Audit calibration drift:** same `EzraEngine` → EPB late-import pattern; M33 framed as “appropriate inversion / no change recommended,” M35 as “top coupling / optional EPBEmitter.” Not evidence of new coupling introduced between audits. |
| Code Health | 5 | 4 | −1 | **Public-readiness polish + calibration:** M35 called out `ezra_version` TODO, legacy wrappers, optional structural refactors; M33 treated pre-commit vs CI mypy as acceptable only. Underlying toolchain discipline unchanged at EPB/plugin contract level. |
| Tests & CI | 5 | 5 | 0 | No regression indicated; M35 audit explicitly notes strong multi-job CI. |
| Security & Supply Chain | 5 | 5 | 0 | No regression indicated. |
| Performance | 4 | 3 | −1 | **Audit calibration:** performance remains a documented non-goal in `docs/VISION.md`; M35 weighted profiling/SLO emphasis more heavily without claiming throughput regression. |
| DX | 5 | 4 | −1 | **Public-readiness polish:** M35 cited `CONTRIBUTING.md`, Makefile/just ergonomics; M33 rated DX 5 with “optional” CI tweaks only. |
| Docs | 5 | 4 | −1 | **Public-readiness polish:** M35 cited Sphinx API depth vs M33’s pre-M35 doc set; M35 milestone **added** `docs/ezra_operating_manual_v1.md`—the lower score reflects **stricter external-audience** bar, not loss of governance docs. |
| **Overall (weighted)** | **4.95** | **4.40** | **−0.55** | See §6. |

---

## 4. Category-by-Category Reconciliation

### Architecture (5 → 5)

Both audits agree: ML-free core, plugin boundary, EPB as artifact surface, determinism posture. **No delta to explain.**

### Modularity / Coupling (5 → 4)

**M33 evidence:** `core/engine.py` → `build_epb_bundle` / `write_epb_bundle` described as appropriate late import; “no surgical decoupling needed.”

**M35 evidence:** Same pattern relabeled “tight coupling” with recommendation for `EPBEmitter`.

**Conclusion:** Interpretive shift on the **same** code path, not a measured increase in fan-in/out or new illegal imports.

### Code Health (5 → 4)

**M33:** Emphasis on lockfile, Ruff, mypy, action pinning; pre-commit vs CI mypy noted as non-blocking.

**M35:** Added narrative on TODO (`ezra_version`), deprecation wrappers, optional extractions.

**Conclusion:** Mostly **checklist depth** and **release-facing nit picks**; no claim that CI truthfulness or `ruff check --no-fix` posture regressed.

### Tests & CI / Security (5 → 5)

Stable high scores; M35 audit text matches M33’s “enterprise” characterization.

### Performance (4 → 3)

Both agree EPB path is correct; neither claims latency regression. Delta is **rubric weighting** of “profiling plan / SLO” vs product philosophy.

### DX & Docs (5 → 4)

M35 demands more **contributor-facing** artifacts (`CONTRIBUTING.md`, fuller API docs) despite M35 shipping the operating manual—consistent with **stricter public repo** expectations.

---

## 5. Findings Classification

Every M35 opportunity from the external audit is classified below (exactly one label each).

| Finding | Classification |
| --- | --- |
| EPB emission coupling in `EzraEngine` | **Audit calibration drift** (same design praised in M33); optionally **Valid refactor opportunity** for ergonomics—not a release blocker |
| Hardcoded `ezra_version` TODO in `epb/builder.py` | **Public-readiness polish** |
| Legacy `tools/` EPB wrappers vs `epb_tools/` | **Public-readiness polish** / **Deferred compatibility decision** |
| Missing `CONTRIBUTING.md` | **Public-readiness polish** |
| Sphinx API reference incomplete | **Public-readiness polish** |
| Lack of performance budgets / SLOs | **Out of scope for public release** unless marketing commits to perf claims |
| Integration/parity tests gated by env vars | **Audit calibration drift** — behavior documented in `docs/ezra.md` §6–8 since before M33 |
| Company-secret paths potentially tracked | **Release boundary issue for M37** — inventoried only in M36 |

---

## 6. Regression Assessment

Based on available evidence, the M33/Post-M32 to M35 score delta is classified as:

- [ ] True project regression
- [ ] Mixed regression and audit calibration drift
- [x] Primarily audit calibration drift
- [ ] Primarily public-release-readiness polish
- [ ] Insufficient evidence

**Rationale:** No concrete evidence in either audit of **broken** EPB contracts, weaker security gates, or architecture violation relative to `docs/ezra.md`. The **−0.55** weighted drop aligns with:

1. **Stricter interpretation** of the same engine→EPB wiring (Modularity 5→4).
2. **Stricter consumer-repo expectations** for docs/DX (5→4 each)—a **public-readiness polish** lens applied within the same calibration phenomenon (auditor rubric / framing), not a loss of shipped governance artifacts.
3. **Harsher Performance rubric** without alleging measured slowdown (4→3).

**M33→HEAD** code history added distribution verification, workflow, and doc surface (see `git diff --stat` in `M36_run1.md`)—**forward progress**, not audit-score regression. No audit claims those features lowered quality scores.
**Note:** If treating “public-readiness polish” as the headline label is preferred for executive comms, it is **not** inconsistent with this verdict—both are **non-regression** explanations; the single checkbox above selects the **dominant** technical explanation (scoring lens / calibration).

---

## 7. Public Release Implications

- **Audit scores are not interchangeable** across sessions without a fixed rubric sheet; reconciling narrative **before** “chasing 4.95” avoids wasted work.
- **Non-negotiable surfaces** (Python import API, EPB v1.0.0 serialization, CI policy) were **not** flagged as regressing between audits.
- **Contributor and external-reader** gaps (CONTRIBUTING, API reference depth) are **polish**, schedulable post-reconciliation (e.g. M38 or dedicated doc milestone)—not EPB emergencies.

---

## 8. Recommended Baseline Going Forward

1. Treat **`docs/M33fullaudit.md` + this reconciliation** as the **dual baseline**: factual project state (M33 era) plus **explicit** scoring drift analysis (M35 era).
2. For the **next full audit**, publish a **rubric appendix** (weights, definitions of 3 vs 4 vs 5 per category) **before** scoring to reduce calibration drift.
3. Keep **M35 external audit** as a **planning input** until a **public-safe** audit artifact is deliberately committed (out of scope for M36).

---

## 9. Recommended Next Milestones

| Milestone | Intent |
| --- | --- |
| **M37** | **Public release boundary cleanup:** untrack/ignore user-approved company-secret paths where still needed; guardrails against reintroduction. |
| **M38** (optional) | **Audit remediation slice:** addressing polish items (e.g. `ezra_version`, CONTRIBUTORS, Sphinx) in small behavior-preserving PRs—only after M37 if secrets/boundary is blocking public clone. |

---

## 10. Evidence Appendix

### A. M35 audit provenance

- Summary scores and category table taken from the **external** full audit prepared at planning time (commit context `f12fd083b1b0e9f9c518535e0938b65d204b5075`). Full text not committed in M36.

### B. M33 audit provenance

- `docs/M33fullaudit.md` (in repo).

### C. Historical diff M33 baseline → HEAD (excerpt)

Recorded in full in `docs/milestones/M36/M36_run1.md`: `git diff --stat` and `git diff --name-only` for `23789314ba5f6a502c650f6a098f12eb4ed0e8b4..HEAD`.

Notable: `.cursorrules` and `docs/prompts/**` appear as **removed** files in that range—i.e. they are **not** tracked at HEAD; `docs/enhancements/**` remains tracked.

---

## Public Release Secret Boundary Inventory

The user-approved company-secret paths are:

- `.cursorrules`
- `docs/enhancements/`
- `docs/prompts/`

**M36 inventory command:**

```bash
git ls-files .cursorrules docs/enhancements docs/prompts
```

**M36 inventory result (exact output at closeout):**

```text
docs/enhancements/AuditEnhancementsV2.md
docs/enhancements/EnhancementsV2.md
docs/enhancements/TestingEnhancementsV2.md
```

**Classification:**

- **`docs/enhancements/`:** tracked files present; **M37** should remove from Git tracking and add guardrails per plan.
- **`.cursorrules`:** **no** tracked path at inventory time; may exist **untracked** locally. **M37** should still enforce `.gitignore` / boundary guardrail so it is not re-committed.
- **`docs/prompts/`:** user-approved company-secret path; **no** tracked files at inventory time (historical commits removed prior prompt files per `git diff`). **M37** should still add path to `.gitignore` and public-boundary guardrail to prevent future tracking.

**Non-blocking note:** Missing tracked `docs/prompts/` at M36 inventory time is **not** an evidence gap for M36 closure—M37 handles ignore/guardrail regardless.

No cleanup was performed in M36. Cleanup is deferred to M37.
