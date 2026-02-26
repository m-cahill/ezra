# EZRA Perception Bundle (EPB) v1.0.0 Specification

**Version:** 1.0.0  
**Status:** Specification (not yet implemented)  
**Last Updated:** 2026-02-26  
**Milestone:** M07

---

## 1. Overview

The **EZRA Perception Bundle (EPB)** is a deterministic, certifiable artifact format that encapsulates the complete output of an EZRA perception run. EPB bundles are designed to be:

* **Deterministic** — Identical inputs produce identical bundles (modulo ML nondeterminism containment)
* **Certifiable** — RediAI v3 can validate bundle integrity and schema compliance
* **Versioned** — Immutable version string prevents silent schema drift
* **Domain-agnostic** — Core format supports multiple perception domains (chess, cards, UI automation, etc.)

EPB v1.0.0 defines the **canonical output surface** for EZRA runtime perception engines.

---

## 2. EPB Directory Structure

An EPB bundle is a directory containing the following files:

```
epb/
  manifest.json      # Bundle metadata, version, provenance
  detections.json    # Raw OCR/detection results
  state.json         # Domain-agnostic structured state
  delta.json         # Optional: incremental state changes
  hashes.json        # Deterministic hashes for all components
```

### File Descriptions

* **`manifest.json`** — Bundle metadata, EZRA version, plugin versions, input metadata, timestamp
* **`detections.json`** — Raw detection results from OCR/perception plugins (domain-agnostic)
* **`state.json`** — Domain-agnostic structured state representation (e.g., board positions, UI elements)
* **`delta.json`** — Optional: Incremental state changes from previous bundle (for temporal sequences)
* **`hashes.json`** — SHA256 hashes of all other files, plus bundle-level hash

**Domain-specific artifacts** (e.g., `domain/chess/fen.txt`) are **not** part of the core EPB contract. They are layered on top as domain profiles.

---

## 3. Canonical JSON Rules

All JSON files in an EPB bundle **must** conform to these canonicalization rules:

### 3.1 Encoding

* **Encoding:** UTF-8
* **Line endings:** LF (`\n`) only (no CRLF)
* **BOM:** Not permitted

### 3.2 Serialization

* **Key ordering:** Sorted alphabetically (case-sensitive)
* **Indentation:** 2 spaces
* **Trailing commas:** Not permitted
* **Unicode:** Escaped only when necessary (use `ensure_ascii=False` in Python)

### 3.3 Floating Point Numbers

* **Precision:** Maximum 8 decimal places
* **Normalization:** Round to 8 decimal places before serialization
* **Forbidden values:** `NaN`, `Infinity`, `-Infinity` are not permitted
* **Serialization:** Use `json.dumps(..., allow_nan=False)` to enforce

**Rationale:** Hash stability requires deterministic float representation. 8 decimal places provides sufficient precision for bounding boxes and confidence scores while ensuring cross-platform consistency.

### 3.4 Arrays

* **Ordering:** Preserved (arrays are ordered structures)
* **Empty arrays:** `[]` (not `null`)

### 3.5 Objects

* **Key sorting:** Alphabetical (case-sensitive)
* **Empty objects:** `{}` (not `null`)
* **Additional properties:** Not permitted (strict schema validation)

### 3.6 Strings

* **Encoding:** UTF-8
* **Control characters:** Escaped per JSON spec
* **Newlines:** Escaped as `\n` (not literal newlines)

---

## 4. Deterministic Hashing

### 4.1 Hash Algorithm

**Algorithm:** SHA256  
**Input:** Canonical JSON string (per Section 3)  
**Output:** Hexadecimal string (lowercase, 64 characters)

### 4.2 Hash Computation

1. Serialize JSON object to canonical string (per Section 3)
2. Compute SHA256 hash of UTF-8 encoded string
3. Output as lowercase hexadecimal string

### 4.3 Hash File Structure

`hashes.json` contains:

```json
{
  "bundle_hash": "sha256 of concatenated file hashes",
  "epb_version": "1.0.0",
  "files": {
    "detections.json": "sha256...",
    "delta.json": "sha256...",
    "hashes.json": "sha256...",
    "manifest.json": "sha256...",
    "state.json": "sha256..."
  }
}
```

**Bundle hash computation:**

1. Sort file names alphabetically
2. Concatenate file hashes in sorted order: `hash1 + hash2 + ...`
3. Compute SHA256 of concatenated string
4. Store as `bundle_hash`

**Note:** `hashes.json` is excluded from bundle hash computation (circular dependency).

---

## 5. Determinism Requirements

### 5.1 ML Nondeterminism Containment

ML models may exhibit nondeterministic behavior due to:

* Floating point precision differences
* GPU nondeterminism
* Random number generation (if used)

**EPB requirement:** Nondeterminism must be **contained** at the detection level. Once detections are canonicalized (rounded, sorted), the resulting EPB bundle must be deterministic.

**Implementation guidance:**

* Round all floats to 8 decimal places before serialization
* Sort detections deterministically (e.g., by top-left corner: y, then x)
* Do not include timestamps or random seeds in canonical output
* Use deterministic plugin versions (no "latest" tags)

### 5.2 Version Immutability

Once an EPB bundle is emitted, its `epb_version` field **must not change**. If schema changes are required:

* Create new EPB version (e.g., `2.0.0`)
* Update specification document
* Require milestone-level justification

**Governance rule:** Any change to EPB directory structure, canonicalization rules, hashing algorithm, or schema definitions requires a new milestone and version bump.

---

## 6. Schema Definitions

EPB v1.0.0 defines JSON Schema files for all components:

* `schemas/manifest.schema.json`
* `schemas/detections.schema.json`
* `schemas/state.schema.json`
* `schemas/delta.schema.json`
* `schemas/hashes.schema.json`

These schemas are **production-grade** and suitable for certification validation by RediAI v3.

**Note:** Schema validation is **not** wired into EZRA runtime in M07. Schemas are provided for future Phase XVI certification.

---

## 7. Versioning

### 7.1 EPB Version Format

**Format:** Semantic versioning (`MAJOR.MINOR.PATCH`)

* **MAJOR:** Breaking schema changes (directory structure, required fields)
* **MINOR:** Backward-compatible additions (optional fields, new file types)
* **PATCH:** Documentation/clarification only (no schema changes)

**Current version:** `1.0.0`

### 7.2 Forward Compatibility

EPB v1.0.0 consumers **must**:

* Ignore unknown fields in JSON objects
* Treat missing optional files as absent (not errors)
* Validate against schema before processing

**Backward compatibility:** Not guaranteed. EPB v2.0.0 may break v1.0.0 consumers.

---

## 8. Domain Profiles

EPB v1.0.0 is **domain-agnostic**. Domain-specific representations are layered on top:

```
epb/
  manifest.json
  detections.json
  state.json
  delta.json (optional)
  hashes.json
  domain/
    chess/
      fen.txt          # Chess-specific: FEN notation
      moves.json       # Chess-specific: move history
    cards/
      hand.json        # Card-specific: hand representation
      table.json       # Card-specific: table state
```

**Core EPB contract:** Only `manifest.json`, `detections.json`, `state.json`, `delta.json`, and `hashes.json` are required. Domain-specific artifacts are **optional extensions**.

---

## 9. Integration Posture

### 9.1 RediAI Separation

EPB bundles are the **only** integration boundary between EZRA and RediAI v3:

* **EZRA produces** EPB bundles
* **RediAI certifies** EPB bundles
* **No code-level integration** — no shared modules, no imports
* **No runtime integration** — no plugin loaders, no shared schemas

**Artifact-boundary-only interaction.**

### 9.2 Certification Flow

1. EZRA emits EPB bundle (deterministic, canonicalized)
2. RediAI v3 validates bundle against JSON schemas
3. RediAI v3 verifies hash integrity
4. RediAI v3 certifies bundle (or rejects with validation errors)

**No bidirectional communication.** EZRA does not call RediAI APIs. RediAI does not import EZRA code.

---

## 10. Examples

### 10.1 Minimal EPB Bundle

```
epb/
  manifest.json      # {"epb_version": "1.0.0", ...}
  detections.json    # {"detections": []}
  state.json         # {}
  hashes.json        # {"bundle_hash": "...", "files": {...}}
```

### 10.2 EPB Bundle with Detections

```
epb/
  manifest.json      # Plugin versions, input metadata
  detections.json    # {"detections": [{"text": "Hello", "confidence": 0.99, "bbox": [10, 20, 50, 40]}]}
  state.json         # Domain-agnostic state
  hashes.json        # All hashes
```

---

## 11. References

* **EZRA Governance:** `docs/ezra.md` Section 10 (RediAI Separation & Certification Posture)
* **JSON Schema Draft 2020-12:** https://json-schema.org/specification.html
* **SHA256:** RFC 6234

---

## 12. Change Log

| Version | Date | Changes | Milestone |
|---------|------|---------|-----------|
| 1.0.0 | 2026-02-26 | Initial specification | M07 |

---

**End of Specification**

