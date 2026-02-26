# M01 Plan — EasyOCR Baseline Harness (Behavior Capture)

## 1. Intent / Target

Establish a **behavior-capture harness** for upstream EasyOCR so future refactors can prove parity against a golden baseline.

M01 introduces EasyOCR **as a pinned, optional dependency** and adds:

* a baseline capture tool (local-run)
* golden output artifacts (checked-in JSON + manifest)
* non-gating integration path (so PR CI stays stable)

## 2. Scope Boundaries

### In Scope

* Pin EasyOCR version (`easyocr==1.7.2`) and document it.
* Add an **EasyOCR-backed plugin implementation** behind the existing `OCRPlugin` interface.
* Add baseline harness that runs EasyOCR on controlled fixtures and emits:
  * `baseline.json` (canonical output)
  * `manifest.json` (environment + model checksum capture)
* Add schema validation tests for baseline artifacts (PR-gated).
* Update `docs/ezra.md` to the "source-of-truth" form.
* Create `docs/milestones/M01/` fold with the standard artifacts.

### Out of Scope

* Refactoring EasyOCR internals (that starts after baseline is locked).
* CVAT integration.
* Training pipelines / RediAI orchestration code.
* Making EasyOCR inference a required PR gate (avoid network/model downloads in required CI).

## 3. Invariants

* **M00 gates remain enforced**: lint, format, typecheck, tests, coverage (≥85%) remain required.
* CI remains **non-mutating** (keep `ruff check --no-fix`). (M00 taught us why.)
* PR gating must not require network beyond dependency install.
* No CVAT code added; no training code added.

## 4. Verification Plan

### PR-gated (CI required)

* Ruff lint + format check
* Mypy
* Pytest unit tests
* New tests:
  * baseline manifest schema validation
  * canonicalization determinism (ordering/rounding function is stable)

### Local-only (evidence artifacts committed)

* Run `baseline capture` tool once with pinned versions and commit:
  * `docs/baselines/easyocr/1.7.2/<fixture_set>/baseline.json`
  * `docs/baselines/easyocr/1.7.2/<fixture_set>/manifest.json`

## 5. Implementation Steps (ordered, reversible)

1. **Add dependency pin as optional extra**
   * In `pyproject.toml`:
     * `[project.optional-dependencies]`
     * `easyocr = ["easyocr==1.7.2"]`
   * Add Pillow as dev dependency (for fixture generation)

2. **Create reference plugin implementation**
   * `src/ezra/plugins/easyocr_plugin.py`
   * Implements `OCRPlugin`
   * Wraps `easyocr.Reader`
   * Ensures CPU mode by default (device config explicit)
   * Must be importable without EasyOCR installed (ImportError handling)

3. **Define canonical baseline output format**
   * Add `src/ezra/baseline/canonicalize.py`
   * Sort detections deterministically (e.g., by top-left y then x)
   * Round floats to fixed precision
   * Emit stable JSON

4. **Create fixture set**
   * Generate fixtures at runtime using PIL (no committed PNGs)
   * Prefer generated fixtures (PIL-drawn text) to avoid copyright issues

5. **Add baseline capture tool (local-run)**
   * `src/ezra/tools/capture_easyocr_baseline.py` (or `python -m ezra.tools.capture_easyocr_baseline`)
   * Outputs:
     * `baseline.json`
     * `manifest.json` including:
       * python version, platform
       * easyocr version
       * torch/torchvision versions
       * model file names + sha256 checksums (where accessible)

6. **Add PR-gated tests**
   * Validate:
     * baseline files exist and match schema
     * canonicalizer is deterministic
   * Mark actual EasyOCR inference tests as `@pytest.mark.integration` and **skip by default** unless `EZRA_RUN_INTEGRATION=1`.

7. **Update `docs/ezra.md`**
   * Apply the expanded "source of truth" structure (sectioned doc).
   * Add M01 row as Planned (and fill in once closed).

8. **Milestone fold**
   * `docs/milestones/M01/`
     * `M01_plan.md` (this)
     * `M01_toolcalls.md`
     * `M01_run1.md` (CI report)
     * `M01_summary.md`
     * `M01_audit.md`

## 6. Risk & Rollback Plan

### Risks

* EasyOCR pulls heavy deps; installing/running in CI may be slow/flaky.
* Model weight downloads introduce nondeterminism if used in PR gates.

### Mitigation

* Keep EasyOCR under optional extras.
* Keep inference integration tests non-gating by default.
* Commit golden outputs + manifest to lock baseline.

### Rollback

* Revert M01 PR (additive changes only).

## 7. Deliverables

* Optional dependency pin for EasyOCR (`easyocr==1.7.2`)
* `EasyOCRPlugin` implementing `OCRPlugin`
* Baseline capture tool + canonicalization utility
* `docs/baselines/easyocr/1.7.2/.../baseline.json` + `manifest.json`
* Updated `docs/ezra.md` (source-of-truth upgrade)
* M01 milestone documentation fold

## 8. Locked Decisions

| Topic           | Locked Decision                                 |
| --------------- | ----------------------------------------------- |
| Fixtures        | Generate at runtime via PIL                     |
| EasyOCR Version | Pin `1.7.2` exactly                             |
| Baseline Path   | `docs/baselines/easyocr/1.7.2/...`              |
| Capture Tool    | `python -m ezra.tools.capture_easyocr_baseline` |
| Coverage        | Plugin mock-covered; no gate weakening          |
| ezra.md         | Expand + integrate; not verbatim paste          |
| Branch          | `m01-easyocr-baseline`                          |
| CI              | No model download in required gates             |

