# Contributing to EZRA

Thank you for contributing. EZRA is governed as an artifact-grade runtime: changes should stay small, explicit, and verifiable. This guide is practical and repo-specific; the full governance ledger is **`docs/ezra.md`**.

## Local setup

- **Python:** 3.11+ (see `pyproject.toml`).
- **Virtual environment:** Create and activate a venv, then install in editable mode with dev dependencies:

  ```bash
  pip install -e ".[dev]"
  ```

- **Optional OCR backends:** EasyOCR and similar are optional extras (e.g. `pip install -e ".[easyocr]"`). CI does not require downloading model weights during PR gates.

## Standard verification

Run these before opening a PR:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

For parity with release supply-chain checks locally (optional but recommended):

```bash
pip-audit -r requirements.txt
python scripts/verify_distribution.py --mode ci-local
```

## Parity and integration tests

By default, parity and integration tests are **skipped**. Enable only when you need them:

```bash
set EZRA_RUN_INTEGRATION=1
pytest -m integration
```

```bash
set EZRA_RUN_PARITY=1
pytest -m parity
```

(On Unix, use `export` instead of `set`.)

Golden baselines and parity discipline are documented in **`docs/ezra.md`** (§5–6). Any change that intentionally alters plugin output, canonicalization, or model behavior requires an explicit milestone, baseline update, and audit justification—do not "fix" golden failures by loosening tests without governance sign-off.

## Contributing plugins

1. Implement a plugin class against `OCRPlugin` in `src/ezra/plugins/`.
2. Register the plugin in `src/ezra/plugins/registry.py` using the existing lazy string pattern (`"module.path:ClassName"`).
3. Add or extend unit tests (e.g. `tests/test_plugin_registry.py`).
4. If the plugin affects observable EPB output, plan for parity / integration verification per `docs/ezra.md`.

Do not add dynamic entry-point discovery or environment-based resolution unless a future milestone authorizes it.

## EPB and schema invariants

- **EPB version:** The `epb_version` field in emitted bundles is **immutable** at `1.0.0` unless a milestone explicitly bumps the contract.
- **Canonicalization and hashing:** Rules in **`docs/specs/epb_v1/`** and **`docs/ezra.md`** must be preserved; do not change hashing or canonical JSON behavior in a drive-by PR.
- **RediAI separation:** Integration with RediAI v3 is **artifact-only** (EPB bundles). No runtime or code-level coupling.

## Public-release boundary

These paths are **not** part of the public Git surface (see **`tests/test_public_release_boundary.py`** and **`.gitignore`**):

- `.cursorrules`
- `docs/enhancements/`
- `docs/prompts/`

Do not commit files under those roots. Confirm locally:

```bash
git ls-files .cursorrules docs/enhancements docs/prompts
```

Expected: no output.

## Where governance lives

| Document | Role |
| --- | --- |
| `docs/VISION.md` | Architecture and non-goals |
| `docs/ezra.md` | Canonical ledger: invariants, layout, milestones |
| `docs/ezra_operating_manual_v1.md` | Runtime behavior and extension (code-aligned) |
| `docs/release/PUBLIC_RELEASE_CHECKLIST.md` | Pre-release verification (reusable) |

## PR checklist

- [ ] Scope matches a single milestone or agreed issue; no unrelated refactors.
- [ ] `ruff check .`, `ruff format --check .`, `mypy src`, `pytest` pass locally.
- [ ] No changes under `docs/specs/epb_v1/` unless the milestone explicitly owns an EPB contract change.
- [ ] No new tracked paths under `.cursorrules`, `docs/enhancements/`, or `docs/prompts/`.
- [ ] Documentation updated if behavior or developer workflow changed (`docs/ezra.md` per `.cursorrules` for major work).

For release and CI caveats (SLSA, Dependency Review, distribution modes), see **`docs/release/PUBLIC_RELEASE_CHECKLIST.md`**.
