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
- **EPB bundle schema stability:** Once an EPB bundle is emitted, its schema must remain stable. The `epb_version` field is immutable.
- **EPB canonicalization rules:** Canonical JSON rules (UTF-8, LF, sorted keys, 8 decimal place float precision, no NaN/Infinity) must be preserved.
- **EPB hashing rules:** SHA256 hashing algorithm and bundle hash computation rules must not change without milestone-level justification.
- **Artifact-boundary-only integration:** Integration between EZRA and RediAI v3 occurs only at the artifact boundary (EPB bundles). No code-level integration, no shared modules, no runtime-level integration.

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
| M02 | Golden Output Lock & Parity Verification | Complete | v0.0.3-m02 | PR#3 | Hard parity gate enforced |
| M03 | Structural Extraction of EasyOCR Integration | Complete | v0.0.4-m03 | PR#4 | Adapter layer isolation, clean integration boundaries |
| M04 | Multi-Plugin Abstraction Layer | Complete | v0.0.5-m04 | PR#5 | Plugin registry with lazy resolution, extensibility foundation |
| M05 | Plugin Configuration & Interface Hardening | Complete | v0.0.6-m05 | PR#6 | Runtime config-driven resolution, strict interface validation, registry hardening |
| M06 | Tesseract Plugin (Provider Boundary Extension) | Complete | v0.0.7-m06 | PR#7 | Second OCR backend plugin added, cross-plugin isolation verified, registry extensibility proven (coverage: 94.85% overall, 100% registry, 100% tesseract) |
| M07 | EPB v1 Specification & External Certification Guardrail | Complete | v0.0.8-m07 | PR#8 | EPB v1 spec locked, RediAI separation rule formalized |
| M08 | EPB v1 Emission (Runtime Wiring, Deterministic Bundle Output) | Complete | v0.0.9-m08 | PR#9 | EPB v1.0.0 bundle emission implemented, 100% EPB module coverage, coverage 96.33% (above 94.85% baseline) |
| M09 | Determinism Multi-Run Gate (EPB Hardening) | Complete | v0.0.10-m09 | PR#10 | Determinism CI gate implemented, byte-identical bundles verified across N≥3 runs, timestamp injection added, all CI checks passing |
| M10 | EPB Schema Validation Wiring (EPB Hardening Phase 2) | Complete | v0.0.11-m10 | PR#11 | JSON Schema validation wired into emission pipeline, invalid bundles fail fast, determinism gate confirmed validation does not mutate data, all CI checks passing |
| M11 | EPB Hash Integrity Verification (EPB Hardening Phase 3) | Complete | v0.0.12-m11 | PR#12 | Hash verification wired into emission pipeline, tampered bundles fail verification, determinism gate confirmed verification does not mutate data, all CI checks passing |
| M12 | Contract Hardening & Deterministic Zone Schema Lock | Complete | v0.0.13-m12 | PR#13 | Zone schema contract introduced with deterministic serialization, validation, and registry freeze semantics. Architecture boundaries enforced. All existing tests pass unchanged. CI Run: 22461501678 |
| M13 | Zone-Aware EPB Extension (Adapter-Gated) | Complete | v0.0.14-m13 | PR#14 | Optional zones.json emission via adapter-gated wiring, deterministic, backward compatible. Hash integrity preserved. Determinism verified with zones. CI Run: 22462632573 |
| M14 | Zone-Scoped State Projection (Behavior-Preserving Runtime Extension) | Complete | v0.0.15-m14 | PR#15 | Zone-scoped state projection utility introduced as pure functional runtime extension. Deterministic projection.json emission verified. Strict mode for overlapping zones. Architecture boundaries preserved. Opt-in design. CI Run: 22464039455 |
| M14 | Zone-Scoped State Projection (Runtime Extension) | Complete | v0.0.15-m14 | PR#15 | Zone-scoped state projection as pure functional runtime utility, deterministic, opt-in only. Architecture boundaries preserved. Determinism verified with projection.json. CI Run: 22464039455 |
| M15 | CI Evidence & Deterministic Quality Envelope Hardening | Complete | v0.0.16-m15 | PR#16 | Structured CI evidence, security/complexity/SBOM gates, audit-ready governance. All 7 jobs pass, all invariants preserved, zero runtime changes. CI Run: 22466225248 |
| M16 | Runtime Exception Contract & Failure Surface Hardening | Complete | v0.0.17-m16 | PR#17 | Typed exception hierarchy with dual inheritance, zero generic exception leakage, backward compatibility preserved. All 213 tests pass (205 original + 8 new), all invariants preserved, zero runtime behavior changes. CI Run: 22467380030 |
| M17 | Release Lock Program (Phase V Initiation) | Complete | v0.0.18-m17 | PR#18 | Public surface freeze test and snapshot baseline, exception taxonomy frozen, EPB v1.0.0 contract frozen, CI enforcement strengthened (gitleaks full-repo scan). All 214 tests pass (213 original + 1 new), all invariants preserved, zero runtime behavior changes. Release-candidate ready. CI Run: 22468659282 |
| M18 | Enterprise Hardening: Security & Supply Chain Gate (Non-Behavioral Refactor) | Complete | v0.0.19-m18 | PR#19 | Enterprise-grade security, supply chain, and audit posture: pydocstyle enforcement, pre-commit hooks, dependency lockfile, CODEOWNERS, OpenSSF Scorecard (warn-first), SLSA provenance, dependency review, Sphinx docs + Pages. All 214 tests pass (unchanged), all invariants preserved, zero runtime behavior changes. Procurement-grade governance. CI Run: 22469338896 |
| M19 | Post-Merge CI Integrity & Release Attestation Closure | Complete | v0.0.20-m19 | PR#20 | Resolved SLSA Provenance and Documentation Deploy workflow configuration errors from M18. Both jobs now execute correctly on main push. Failures are infrastructure limitations (private repo attestation restriction, Pages not enabled), not workflow bugs. All 214 tests pass (unchanged), all invariants preserved, zero runtime behavior changes. CI truthfulness maintained. CI Run: 22470215827 |
| M20 | Deterministic Runtime Hardening & Contract Surface Sealing | Complete | v0.0.21-m20 | PR#21 | Runtime immutability enforcement: frozen dataclasses for core types, EPB bundle sealing with MappingProxyType, comprehensive immutability test suite (14 new tests). All 228 tests pass (214 baseline + 14 new), coverage maintained at 95.78%, all invariants preserved, zero runtime behavior drift. Structural immutability at object level, not just output level. CI Run: 22470798544 |
| M21 | Deterministic Zone Schema Lock & Adapter Boundary Hardening | Complete | v0.0.22-m21 | PR#22 | Zone schema contract formalized: JSON Schema (schema_v1.json), canonical serialization with SCHEMA_VERSION constant, comprehensive contract tests (12 new tests), CI schema validation step. All 239 tests pass (228 baseline + 12 new - 1 public surface test initially failed, then passed), coverage improved to 95.86%, all invariants preserved, zero runtime behavior drift. Schema validation step successfully added and executing. CI Run: 22471646113 |
| M22 | Zone Schema Evolution Guardrails & Diff Governance | Complete | v0.0.23-m22 | PR#23 | Schema evolution governance guardrails: snapshot baseline (zone_schema_snapshot.json), schema diff enforcement test, version-schema coupling test, CI schema governance step, Schema Evolution Policy documentation. All 241 tests pass (239 baseline + 2 new), coverage maintained, all invariants preserved, zero runtime behavior drift. Schema governance step successfully added and executing. CI Run: 22473936860 |
| M23 | Zone Registry Deterministic State & Integrity Hardening | Complete | v0.0.24-m23 | PR#24 | Registry integrity hardening: snapshot baseline (zone_registry_snapshot.json), hash determinism, freeze enforcement, channel ordering invariants, CI registry integrity section. All 252 tests pass (241 baseline + 10 new + 1 existing), coverage maintained, all invariants preserved, zero runtime behavior drift. Registry Integrity section visible in CI. CI Run: 22475261410 |
| M24 | Consumer Contract Harness & Invariant Hardening | Complete | v0.0.25-m24 | PR#25 | Introduced EPB consumer contract harness with golden snapshot baseline and Python-level determinism invariant enforcement. All 256 tests pass (252 baseline + 4 new), coverage 95.90% (↑ from 95.78%), no public surface drift, no CI weakening. EPB Contract Harness step and summary in CI. CI Run: 22476148423 |

## 8. Local Dev Quickstart

- Create venv (Python 3.11+)
- Install dev deps: `pip install -e ".[dev]"`
- Run checks: `ruff check . && ruff format --check . && mypy src && pytest`

Optional (M01+):
- Install EasyOCR extras: `pip install -e ".[easyocr]"`
- Run baseline capture tool: `python -m ezra.tools.capture_easyocr_baseline`

## 9. Plugin Registration Policy

After M05:

EZRA uses a **static plugin registry** for plugin resolution. The registry is located in `src/ezra/plugins/registry.py` and provides:

* `get_plugin(name: str, **kwargs) -> OCRPlugin` — Factory function to resolve and instantiate plugins by name
* `get_plugin_from_config(config: dict) -> OCRPlugin` — Factory function to resolve plugins from configuration dictionary
* `list_plugins() -> list[str]` — Returns sorted list of registered plugin names
* `validate_registry() -> None` — Test-time validation function to verify registry integrity

### Registration Pattern

Plugins are registered using a **lazy import pattern** to avoid importing heavy ML modules at registry import time:

```python
_PLUGIN_REGISTRY: dict[str, str] = {
    "easyocr": "ezra.plugins.easyocr_plugin:EasyOCRPlugin",
}
```

The registry maps plugin names to `"module.path:ClassName"` strings, which are resolved dynamically when `get_plugin()` is called.

### Naming Conventions

* Plugin names should be lowercase, alphanumeric with underscores (e.g., `"easyocr"`, `"tesseract"`)
* Plugin class names should follow `{Name}Plugin` pattern (e.g., `EasyOCRPlugin`)
* Module paths should be relative to `ezra.plugins` package

### Extension Pattern

To add a new plugin:

1. Implement `OCRPlugin` ABC in `src/ezra/plugins/{name}_plugin.py`
2. Add entry to `_PLUGIN_REGISTRY` in `registry.py`:
   ```python
   "plugin_name": "ezra.plugins.plugin_name_plugin:PluginNamePlugin",
   ```
3. Add unit tests in `tests/test_plugin_registry.py`
4. Ensure parity suite passes (if applicable)

### Current Plugins

* `easyocr` — EasyOCR-backed OCR plugin (requires `pip install -e ".[easyocr]"`)
* `tesseract` — Tesseract-backed OCR plugin stub (M06, no external dependencies required)

### Plugin Configuration Format

After M05, plugins can be resolved from configuration dictionaries:

```python
config = {
    "name": "easyocr",
    "kwargs": {
        "device": "cpu",
        "languages": ["en"]
    }
}
plugin = get_plugin_from_config(config)
```

The configuration format requires:
- `"name"`: str (required) - Plugin name matching a registered plugin
- `"kwargs"`: dict (optional) - Plugin-specific initialization arguments passed directly to the plugin constructor

**Important constraints:**
- Registry remains static (no dynamic discovery)
- No environment variable resolution
- No entry-point discovery
- Deterministic resolution only
- Configuration validation is strict (raises `ValueError` for missing name or unknown plugin)

### Future Extensions

Dynamic plugin discovery via entry points or packaging metadata is deferred to future milestones. The current static registry is deterministic, testable, and sufficient for initial extensibility needs.

---

## 10. RediAI Separation & Certification Posture

After M07:

EZRA and RediAI v3 maintain **strict architectural separation** with integration occurring **only at the artifact boundary**.

### Artifact Boundary Rule

**Integration between EZRA and RediAI occurs only at the artifact boundary. No runtime code is shared. No plugin loaders are shared.**

### Core Principles

1. **EZRA produces EPB bundles** — EZRA runtime emits EZRA Perception Bundle (EPB) v1.0.0 artifacts containing:
   * `manifest.json` — Bundle metadata, version, provenance
   * `detections.json` — Raw OCR/detection results
   * `state.json` — Domain-agnostic structured state
   * `delta.json` — Optional: incremental state changes
   * `hashes.json` — Deterministic SHA256 hashes

2. **RediAI certifies EPB bundles** — RediAI v3 validates bundle integrity, schema compliance, and hash verification. RediAI does not execute EZRA code.

3. **No code-level integration:**
   * EZRA never imports RediAI modules
   * RediAI never imports EZRA modules
   * No shared plugin loaders
   * No shared schemas (EPB schemas are defined in EZRA, consumed by RediAI)
   * No runtime-level integration

4. **No bidirectional communication** — EZRA does not call RediAI APIs. RediAI does not import EZRA code. Certification is a one-way validation process.

### EPB Specification

The EPB v1.0.0 specification is defined in:

* **Specification document:** `docs/specs/epb_v1/EPB_V1_SPEC.md`
* **JSON Schemas:** `docs/specs/epb_v1/schemas/` (manifest, detections, state, delta, hashes)

EPB bundles are:
* **Deterministic** — Identical inputs produce identical bundles (modulo ML nondeterminism containment)
* **Certifiable** — RediAI v3 can validate bundle integrity and schema compliance
* **Versioned** — Immutable version string (`epb_version: "1.0.0"`) prevents silent schema drift
* **Domain-agnostic** — Core format supports multiple perception domains (chess, cards, UI automation, etc.)

### Governance Rule

**Any change to EPB directory structure, canonicalization rules, hashing algorithm, or schema definitions requires:**

* A new milestone
* A version bump in `epb_version` (e.g., `1.0.0` → `2.0.0`)
* Explicit audit justification

This prevents silent drift and ensures EPB remains a stable, certifiable output surface.

### Certification Flow

1. EZRA emits EPB bundle (deterministic, canonicalized per EPB v1.0.0 spec)
2. RediAI v3 validates bundle against JSON schemas
3. RediAI v3 verifies hash integrity (`hashes.json`)
4. RediAI v3 certifies bundle (or rejects with validation errors)

**No runtime integration. Artifact-boundary-only interaction.**

---


