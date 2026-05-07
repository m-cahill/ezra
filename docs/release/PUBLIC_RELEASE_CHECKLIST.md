# Public release checklist

Reusable checklist before tagging or announcing a **public** EZRA release. Complete all applicable items; record evidence (CI run URLs, command output) in the milestone or release notes as appropriate.

## 1. Repository boundary (secrets / local-only paths)

- [ ] **Guardrail test** — `pytest` includes `tests/test_public_release_boundary.py` and it passes.
- [ ] **No tracked secret-boundary paths:**

  ```bash
  git ls-files .cursorrules docs/enhancements docs/prompts
  ```

  Expected: *empty output*.

## 2. Default-branch CI

- [ ] Latest **`main`** workflow run(s) are **green** for required jobs (no muted failures, no `continue-on-error` on required checks).
- [ ] **Dependency Review** — If this check is required on PRs, note it may be unavailable without GitHub Advanced Security / dependency graph; do not treat "skipped" on `push` as a regression if documented (see M37B posture).

## 3. Supply chain

- [ ] **`pip-audit`** passes against the locked requirements in use for release:

  ```bash
  pip-audit -r requirements.txt
  ```

## 4. Distribution verification

- [ ] **PR / local CI parity:** `python scripts/verify_distribution.py --mode ci-local` succeeds.
- [ ] **Release artifacts (tag or workflow_dispatch):** When validating a published tag, use **`--mode release`** per **`docs/release/DISTRIBUTION_VERIFICATION.md`** (may need appropriate `GITHUB_TOKEN` / repository permissions).

## 5. Documentation build (if enabled)

- [ ] If Sphinx / docs-deploy is enabled for the repo (`vars.EZRA_ENABLE_PAGES_DEPLOY` or equivalent), confirm the docs build job succeeds.
- [ ] If Pages deploy is intentionally disabled, confirm that is documented and not mistaken for a product defect.

## 6. EPB contract non-drift

- [ ] No unintended edits under **`docs/specs/epb_v1/`** (schemas, normative spec) for a docs-only release.
- [ ] **`epb_version`** in emitted manifests remains **`1.0.0`** unless a milestone explicitly bumps the EPB contract.
- [ ] Determinism / contract tests still pass (`pytest`, including EPB consumer contract tests as gated by CI).

## 7. Contributor-facing docs

- [ ] **`README.md`** reflects what EZRA is and is not (runtime-only, no training in-repo, RediAI boundary).
- [ ] **`CONTRIBUTING.md`** is present and linked from the README.

## 8. Honest claims (SLSA, Dependency Review, private repo)

- [ ] **SLSA provenance:** On **private** repositories, attestation may be gated or skipped by GitHub policy; workflows should reflect that honestly (see M37B).
- [ ] **Dependency Review:** May be PR-only and infrastructure-dependent; do not claim full supply-chain dashboard coverage unless the org has enabled it.
- [ ] **No overclaims** in README or release notes: no implied RediAI runtime integration, no training-in-EZRA claims, no performance guarantees unless measured and cited.

## 9. Final public-release audit

- [ ] Schedule or run a **fresh** public-readiness audit (external or internal) using the current tree; **do not** assert a numeric audit score recovery without a new audit artifact.
- [ ] **ensure all documentation is updated as necessary** (`docs/ezra.md`, `REFACTOR.md`, milestone proof pack as required).

## Initial public release (extra notes)

For the **first** public clone of a previously private tree:

- Confirm default-branch green post-boundary cleanup (M37-style) and that `.gitignore` covers `.cursorrules`, `docs/enhancements/`, `docs/prompts/`.
- Communicate known CI limitations (Dependency Review, SLSA on private repos) in README or release notes.
