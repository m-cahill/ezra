# M39 — Final public-release audit (current state)

**Audited HEAD:** `2f782010cecb72856bbf39b5f90b6c526d183d34`  
**Branch:** `audit/m39-final-public-release-audit` (matches **`main`** tip at audit time)  
**Evidence commands:** `docs/milestones/M39/M39_run1.md`  
**Methodology note:** This audit **does not** reuse or validate historical **M33/M35 weighted scores**. Findings are from commands and doc review **on this tree**.

---

## Release Readiness Decision

**GO WITH DOCUMENTED LIMITATIONS**

---

## 1. Public-release boundary

| Check | Result |
| --- | --- |
| `git ls-files .cursorrules docs/enhancements docs/prompts` | **Empty** (no tracked paths) |
| Guardrail test | **`tests/test_public_release_boundary.py`** exists and **passed** in full suite (`M39_run1`) |
| Reintroduction risk | No tracked private prompt/enhancement roots observed |
| `.gitignore` | Contains `.cursorrules`, `docs/enhancements/`, `docs/prompts/` (approved local-only boundary; prevents accidental commit) |

**Assessment:** **Clean** for public Git surface.

---

## 2. Default-branch CI trust

| Check | Result |
| --- | --- |
| Latest **`main`** runs (`gh run list`, limit 5) | All listed **`CI`** workflow rows **`success`** |
| Representative runs | https://github.com/m-cahill/ezra/actions/runs/25481762088 — **`success`** (HEAD `2f78201`); https://github.com/m-cahill/ezra/actions/runs/25481653532 — **`success`** |
| Required gate muting | Core jobs (`Lint`, `Test`, `Type Check`, `Security Check`, `Distribution Verification`, hermetic/determinism jobs, etc.) use **`continue-on-error: false`** where enumerated in `ci.yml`; **Dependency Review** intentionally uses **`continue-on-error: true`** with an explanatory step summary (**GHAS / dependency graph**) |
| Dependency Review framing | Documented as infrastructure-dependent; **`push`** pipelines typically **skip** or soft-handle Dependency Review compared with **PR** runs |

**Assessment:** **Truthful** default-branch posture for this repo; PR-side Dependency Review remains a **documented limitation**, not silent success theater on **`main`**.

---

## 3. Supply chain

| Check | Result |
| --- | --- |
| `pip-audit -r requirements.txt` (local) | **No known vulnerabilities** (`M39_run1`) |
| SBOM | **`SBOM Generation`** job present in CI; **`ci-local`** distribution verification reports **`sbom_valid: true`** |
| Honest dependency-review limits | Workflow notes GHAS requirement; README/checklist align |

**Assessment:** **Passes** supply-chain checks exercised here; remaining GitHub Dependency Review limits are **documentation/infrastructure**, not a failing lockfile audit.

---

## 4. Distribution verification

| Check | Result |
| --- | --- |
| `python scripts/verify_distribution.py --mode ci-local` | **`distribution_verified: true`** (`M39_run1`) |
| Release vs CI-local | **`docs/release/DISTRIBUTION_VERIFICATION.md`** describes modes; **`ci-local`** explicitly avoids GitHub artifact download and notes provenance scope |
| Stale HTTP 401 on PR/main default CI | **Not reproduced** in current verification — **`ci-local`** path matches **M37B** honest split (release artifact verification separate) |

**Assessment:** **Truthful** for **`ci-local`** / default CI expectations.

---

## 5. EPB contract non-drift

| Check | Result |
| --- | --- |
| Unintended churn under `docs/specs/epb_v1/**` | Last touched commit for tree **`174875b`** — **not** part of M38/M39 doc waves on this branch |
| `epb_version` | **`EPB_VERSION = "1.0.0"`** in `src/ezra/epb/builder.py`; spec examples **`"1.0.0"`** |
| `ezra_version` | **Producer metadata** only — resolved via **`importlib.metadata`** / fallback (**M38**); **not** EPB contract version |
| Canonicalization / hashing | No changes asserted in this audit beyond existing locked governance |

**Assessment:** **No drift** detected vs EPB v1.0.0 contract posture.

---

## 6. Docs / DX public readiness

| Artifact | Assessment |
| --- | --- |
| **`README.md`** | Clear public narrative; links governance and checklist; states boundaries |
| **`CONTRIBUTING.md`** | Present; actionable verification + boundary guidance |
| **`docs/release/PUBLIC_RELEASE_CHECKLIST.md`** | Present; reusable |
| **`docs/ezra.md`** | Ledger current through M39 planning merge; updated again with audit completion PR |
| **`REFACTOR.md`** | M36–M39 narrative coherent |

**Assessment:** **Ready** for external readers at documentation layer.

---

## 7. Honest claims

| Risk | Finding |
| --- | --- |
| Training-in-EZRA | **None** — README states training **out of scope** |
| RediAI **runtime** integration | **None** — README specifies **artifact-boundary-only** EPB consumption |
| SLSA **success** overclaim | **Controlled** — README and workflows state attestation may be **unavailable** on private repos until step succeeds |
| Performance guarantees | **None** found as blanket guarantees |
| Numeric audit-score “recovery” | **Not claimed** — this audit does not publish a recovered M33/M35 score |

**Assessment:** **No release-blocking overclaims** identified in primary public surfaces reviewed.

---

## Documented limitations (for “GO WITH DOCUMENTED LIMITATIONS”)

1. **GitHub Dependency Review** — Depends on repository Advanced Security / dependency graph posture; workflow uses **`continue-on-error`** and summaries to avoid false **`main`** failure while staying transparent on PRs.
2. **GitHub SLSA artifact attestation** — May be **skipped** or non-persistent for **private** repository classes; workflows/README instruct **not** to claim success until attestations persist.
3. **GitHub Pages deploy** — Optional/**gated**; docs **build** remains validated in CI.

---

## NO-GO issues

**None found** under M39 criteria for this audited HEAD (no tracked secrets in boundary paths, **`pip-audit`** clean, **`main`** green on sampled runs, EPB stable, distribution **`ci-local`** honest).

---

**ensure all documentation is updated as necessary.**
