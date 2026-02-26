# EZRA

## 0. What EZRA Is

EZRA (Extensible Zone-Based Runtime Architecture) is a modular **runtime perception engine** that converts raw pixels (screenshots / frames) into structured, interpretable state for interactive systems (games, UI automation, research rigs).

**North Star:** `docs/VISION.md` (architecture + non-goals).

## 1. Source of Truth Hierarchy

1. **VISION:** `docs/VISION.md` — architectural boundaries, non-goals, guiding principles.
2. **Operating Manual (this doc):** `docs/ezra.md` — canonical project ledger: phases, invariants, policies, project layout, milestone index.
3. **Proof Artifacts:** `docs/milestones/MNN/*` — plan/run/summary/audit for each milestone.

If this doc and a milestone artifact disagree, the milestone artifact wins for the specific milestone; VISION wins for architecture and boundaries.

## 2. Boundary Contracts (Non-Negotiable)

- **EZRA is runtime-only.** It loads models and runs inference.
- **Training is out-of-scope for EZRA.** Training pipelines belong to **RediAI-v3**.
- **Annotation is out-of-scope for EZRA.** Tools like **CVAT** are external upstream systems; EZRA consumes exported datasets/artifacts.

## 3. Standing Invariants

These must remain true unless a milestone explicitly declares and justifies a change:

- CI is **truthful** (no muted failures, no `continue-on-error` for required checks).
- CI checks are **non-mutating** (linters must not rewrite files during CI — see M00 lesson: `ruff check --no-fix`).
- PR-gating checks must not require network access beyond dependency install (avoid "download model weights during PR gate").
- Deterministic text normalization enforced (LF line endings via `.gitattributes`).
- Plugin-first posture: core engine remains ML-free; ML is loaded via plugin interfaces.

## 4. Repository Layout

- `src/ezra/`
  - `core/` — orchestration, state machine, pipeline coordination (ML-free)
  - `plugins/` — plugin interfaces + reference plugin implementations
  - `baseline/` — canonicalization utilities for golden output capture
  - `tools/` — command-line tools (e.g., baseline capture)
  - `types.py` — canonical types / schemas for runtime inputs/outputs
- `tests/`
  - Unit tests (always PR-gated)
  - Integration tests marked `@pytest.mark.integration` (skip by default unless `EZRA_RUN_INTEGRATION=1`)
- `docs/baselines/`
  - Golden outputs + capture manifests for behavior preservation
- `docs/milestones/`
  - Milestone proof packs (plan/run/summary/audit/toolcalls)

## 5. Baseline & Golden Output Strategy

EZRA's refactor safety comes from "baseline first":
- Capture known-good outputs from upstream behavior (EasyOCR) on a small, controlled fixture set.
- Store:
  - input fixture definition (generated at runtime via PIL, not committed images)
  - output JSON in a canonical schema (stable ordering + stable rounding)
  - capture manifest:
    - `easyocr` version
    - python version
    - torch/torchvision versions
    - model file checksums (sha256) for downloaded weights

Golden outputs are only comparable if the manifest matches (or the milestone explicitly updates the baseline).

## 6. Golden Parity Discipline

After M02:

* Golden baseline artifacts are binding.
* Any change affecting:

  * Plugin output
  * Canonicalization logic
  * Model invocation behavior
* Must:

  1. Run parity suite (`EZRA_RUN_PARITY=1 pytest -m parity`)
  2. Pass manifest check
  3. Update baseline explicitly in a dedicated milestone if behavior change is intentional

Baseline updates require:

* New milestone ID
* Updated manifest
* Explicit audit justification

Parity tests are marked with `@pytest.mark.integration` and `@pytest.mark.parity`, and skip by default unless `EZRA_RUN_PARITY=1` is set. They are **not** run in CI by default (local refactor guard only).

---

## 7. Milestones

| Milestone | Objective | Status | Tag | PR | Notes |
|-----------|-----------|--------|-----|----|------|
| M00 | Genesis baseline (CI + skeleton + governance) | Complete | v0.0.1-m00 | PR#1 | Non-mutating CI + LF normalization |
| M01 | EasyOCR baseline harness (behavior capture) | Complete | v0.0.2-m01 | PR#2 | Golden baseline locked, deterministic canonicalization |
| M02 | Golden Output Lock & Parity Verification | In Progress | v0.0.3-m02 | TBD | Hard parity gate enforced |

## 8. Local Dev Quickstart

- Create venv (Python 3.11+)
- Install dev deps: `pip install -e ".[dev]"`
- Run checks: `ruff check . && ruff format --check . && mypy src && pytest`

Optional (M01+):
- Install EasyOCR extras: `pip install -e ".[easyocr]"`
- Run baseline capture tool: `python -m ezra.tools.capture_easyocr_baseline`

