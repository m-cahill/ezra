# M12 Plan

## Contract Hardening & Deterministic Zone Schema Lock

---

## 1. Intent / Target

### Primary Objective

Refactor EZRA to formally **lock the Universal Zone Schema as a versioned, validated contract**, eliminating ambiguity between:

* Visual zone definitions
* Tensor channel indexing
* Persistence semantics
* Runtime zone interpretation

This milestone does **not** add new features.

It converts the current informal/implicit zone mapping into:

* A typed schema
* Deterministic serialization
* Strict validation
* CI-gated compatibility guarantees

This aligns with RediAI's contract-first discipline.

---

## 2. Scope Boundaries

### ✅ In Scope

* **ZoneSchema dataclass** — Frozen dataclass with `id`, `kind`, `channel_index`, `bbox_norm`, `persistence`
* **BBoxNorm dataclass** — Frozen dataclass with `x_min`, `y_min`, `x_max`, `y_max` (normalized 0-1)
* **ZonePersistence dataclass** — Frozen dataclass with `sticky: bool` flag
* **Deterministic serialization** — Stable key ordering, 6 decimal place float rounding
* **Validation layer** — Unique channel indices, normalized bbox range, unique zone IDs, no overlapping channels
* **Schema registry** — Immutable registry with freeze-after-init (strangler pattern)
* **JSON schema export** — Deterministic JSON snapshot for contract locking
* **CI artifact upload** — `zone_schema.json` uploaded via `actions/upload-artifact@v4`
* **Contract tests** — Snapshot tests, round-trip tests, channel mapping tests
* **Architecture tests** — Verify runtime does not import registry internals

### ❌ Out of Scope

* No changes to runtime inference logic
* No performance optimizations
* No new zone kinds (kind is free-form string)
* No API surface changes
* No CLI changes
* No change to tensor layout semantics
* No enum-based persistence (sticky bool only)
* No contiguity enforcement for channel indices
* No sample zones in `src/` (registry ships empty, tests use fixtures)

---

## 3. Invariants (Must Not Change)

### Behavioral Invariants

1. Existing zone definitions produce identical tensor channel mappings (N/A in M12 — no zones exist yet).
2. Existing workflows using zones behave identically (N/A in M12 — no zones exist yet).
3. No change to:
   * Channel index resolution (when zones are added later)
   * Bounding box normalization semantics
   * Zone persistence behavior
4. Existing tests must pass unchanged.

### Serialization Invariants

* Zone schema JSON produced before M12 == after M12 (byte-stable when sorted).
* Float precision: 6 decimal places for bbox coordinates.
* Key ordering: deterministic (sorted by `(channel_index, id)`).

### CI Invariants

* Determinism check continues to pass (M11 introduced deterministic bundles).
* Coverage must not drop below current baseline (94.13%).
* No new architecture violations.

### Validation Invariants

* BBox normalization: `0 <= x_min < x_max <= 1` and `0 <= y_min < y_max <= 1` (strict `<` for max bounds).
* Channel indices: `int >= 0`, globally unique across registry.
* Zone IDs: non-empty strings, globally unique across registry.
* Zone kind: non-empty string (free-form, no taxonomy enforcement).

---

## 4. Verification Plan

| Invariant                 | Verification Method      |
| ------------------------- | ------------------------ |
| Channel mapping unchanged | Golden snapshot test     |
| JSON schema stable        | Snapshot comparison      |
| Deterministic output      | Run determinism check 3x |
| No runtime regression     | Full test suite          |
| No API drift              | Contract comparison test |
| No coverage regression    | CI coverage gate         |

Add:

* `tests/contracts/test_zone_schema_snapshot.py`
* `tests/contracts/test_zone_schema_roundtrip.py`
* `tests/contracts/test_zone_channel_mapping.py`

---

## 5. Implementation Steps (Small, Ordered, Reversible)

### Step 1 — Introduce Type Definitions

Create:

```
src/ezra/zones/__init__.py
src/ezra/zones/schema.py
```

**BBoxNorm:**
```python
@dataclass(frozen=True)
class BBoxNorm:
    x_min: float
    y_min: float
    x_max: float
    y_max: float
```

**ZonePersistence:**
```python
@dataclass(frozen=True)
class ZonePersistence:
    sticky: bool
```

**ZoneSchema:**
```python
@dataclass(frozen=True)
class ZoneSchema:
    id: str
    kind: str
    channel_index: int
    bbox_norm: BBoxNorm
    persistence: ZonePersistence
```

* Pure data.
* No runtime side effects.

---

### Step 2 — Add Deterministic Serialization

Add to `ZoneSchema`:

```python
def to_dict(self) -> Dict[str, Any]:
```

Requirements:

* Stable key ordering: `["id", "kind", "channel_index", "bbox_norm", "persistence"]`
* Float rounding to 6 decimal places for bbox coordinates
* No dynamic fields
* BBoxNorm serialized as nested dict: `{"x_min": ..., "y_min": ..., "x_max": ..., "y_max": ...}`
* ZonePersistence serialized as: `{"sticky": bool}`

Add snapshot test.

---

### Step 3 — Add Validation Layer

Create:

```
src/ezra/zones/validator.py
```

Validation rules:

* Channel indices must be unique across registry.
* BBox normalized range must be `0 <= x_min < x_max <= 1` and `0 <= y_min < y_max <= 1`.
* No overlapping channel assignments.
* Zone `id` uniqueness across registry.
* Zone `id` and `kind` must be non-empty strings.
* `channel_index` must be `int >= 0`.

Add negative tests for each rule.

---

### Step 4 — Introduce Schema Registry (Non-Invasive)

Create:

```
src/ezra/zones/registry.py
```

Registry responsibilities:

* Register zone schemas
* Freeze registry after initialization
* Provide immutable lookup
* Export deterministic JSON (sorted by `(channel_index, id)`)

Important:
Old entrypoints must remain stable.
Registry introduced behind adapter layer (strangler pattern).

**Registry API:**
```python
class ZoneRegistry:
    def __init__(self) -> None:
        self._zones: dict[str, ZoneSchema] = {}
        self._frozen: bool = False
    
    def register(self, schema: ZoneSchema) -> None:
        """Register a zone schema. Raises ValueError if frozen or validation fails."""
    
    def freeze(self) -> None:
        """Freeze registry (no further registrations allowed)."""
    
    def get(self, zone_id: str) -> ZoneSchema | None:
        """Get zone schema by ID."""
    
    def list_all(self) -> list[ZoneSchema]:
        """Return all zones sorted by (channel_index, id)."""
    
    def export_to_dict(self) -> dict[str, Any]:
        """Export registry to deterministic dict for JSON serialization."""
```

---

### Step 5 — Add JSON Schema Export

Create:

```
src/ezra/zones/export.py
```

Exports:

* Deterministic JSON file
* Used for contract locking
* Future cross-repo consumption

**Export function:**
```python
def export_zone_schema_json(registry: ZoneRegistry, output_path: Path) -> None:
    """Export registry to deterministic JSON file."""
```

Add CI artifact upload of:

```
zone_schema.json
```

**CI integration:**
* Add step to `.github/workflows/ci.yml`:
  * Create empty registry (or load from fixtures if needed)
  * Export to `zone_schema.json` (repo root)
  * Upload as artifact `zone-schema`

---

### Step 6 — Add Architecture Test

Add test ensuring:

* Runtime (`src/ezra/core/**`) does not import registry internals directly.
* Zone schema is only consumed via public API (`ezra.zones`).

Prevents boundary leakage.

**Test location:** `tests/test_zone_architecture.py`

**Test pattern:**
* Verify `src/ezra/core/**` imports only from `ezra.zones` (public `__init__.py`)
* Verify no direct imports of `ezra.zones.registry` or `ezra.zones.validator` from core

---

### Step 7 — Add Contract Tests

Create:

```
tests/contracts/__init__.py
tests/contracts/snapshots/zone_schema_snapshot.json
tests/contracts/test_zone_schema_snapshot.py
tests/contracts/test_zone_schema_roundtrip.py
tests/contracts/test_zone_channel_mapping.py
```

**Snapshot test:**
* Build deterministic registry with 2-3 sample zones (fixtures)
* Export to dict → JSON
* Compare loaded JSON to committed snapshot (order-insensitive on parse)
* Second test: export JSON string twice, assert equality (ensures key ordering + float formatting stability)

**Round-trip test:**
* Create zone schemas
* Serialize to dict
* Deserialize back
* Assert equality

**Channel mapping test:**
* Verify unique channel indices
* Verify no overlaps
* Verify channel index >= 0

---

## 6. Risk & Rollback Plan

### Risks

* Hidden coupling to legacy zone definitions (N/A — no zones exist yet)
* Float rounding drift in serialization (mitigated by 6dp precision + snapshot tests)
* Registry freeze interfering with test setup (mitigated by fixture pattern)

### Mitigation

* Implement registry behind adapter.
* Add full round-trip tests before refactoring callers.
* If regression detected:
  * Revert registry layer only
  * Keep schema + validation (safe subset)

---

## 7. Deliverables

* `src/ezra/zones/__init__.py` (public API exports)
* `src/ezra/zones/schema.py` (ZoneSchema, BBoxNorm, ZonePersistence)
* `src/ezra/zones/validator.py` (validation rules)
* `src/ezra/zones/registry.py` (immutable registry)
* `src/ezra/zones/export.py` (JSON export)
* `tests/contracts/test_zone_schema_snapshot.py`
* `tests/contracts/test_zone_schema_roundtrip.py`
* `tests/contracts/test_zone_channel_mapping.py`
* `tests/test_zone_architecture.py`
* `tests/contracts/snapshots/zone_schema_snapshot.json` (committed snapshot)
* CI artifact: `zone_schema.json` (uploaded, not committed)
* Updated milestone ledger in `docs/ezra.md`
* M12 summary + audit at close

---

## 8. Exit Criteria

M12 closes only if:

* All tests pass
* Determinism passes (if applicable)
* Coverage ≥ baseline (94.13%)
* Snapshot matches
* No behavior drift (existing tests unchanged)
* CI green on first or second run
* Architecture test passes
* Audit ≥ 4.8/5

---

## 9. Why This Is the Correct Next Move

RediAI v3 emphasizes:

* Contract-first design
* Trace-first, deterministic artifacts
* Architecture enforcement via CI

EZRA's Universal Zone Mapping is a structural primitive.

If it is not locked as a contract:

* Downstream training reproducibility weakens.
* Multi-project reuse becomes fragile.
* Cross-repo consumption (e.g., VULCAN, UNGAR, future CV adapters) becomes unsafe.

This milestone strengthens the foundation without expanding scope.

---

## 10. Implementation Details (Locked Answers)

### Type Definitions

**BBoxNorm:**
```python
@dataclass(frozen=True)
class BBoxNorm:
    x_min: float
    y_min: float
    x_max: float
    y_max: float
```

**ZonePersistence:**
```python
@dataclass(frozen=True)
class ZonePersistence:
    sticky: bool
```

**ZoneSchema:**
```python
@dataclass(frozen=True)
class ZoneSchema:
    id: str
    kind: str
    channel_index: int
    bbox_norm: BBoxNorm
    persistence: ZonePersistence
```

### Validation Rules

* BBox: `0 <= x_min < x_max <= 1` and `0 <= y_min < y_max <= 1` (strict `<` for max bounds)
* Channel index: `int >= 0`, globally unique
* Zone ID: non-empty string, globally unique
* Zone kind: non-empty string (free-form)

### Serialization

* Float precision: 6 decimal places
* Key ordering: deterministic (sorted by `(channel_index, id)` for registry export)
* BBoxNorm: nested dict with keys `["x_min", "y_min", "x_max", "y_max"]`
* ZonePersistence: dict with key `["sticky"]`

### Registry

* Ships empty in runtime/library code
* Tests populate via fixtures only
* Freeze-after-init pattern
* Export sorted by `(channel_index, id)`

### CI Artifact

* File: `zone_schema.json` (repo root)
* Artifact name: `zone-schema`
* Upload via `actions/upload-artifact@v4`
* Content: deterministic JSON snapshot of registry contents (not JSON Schema spec)

### Snapshot Test

* Location: `tests/contracts/snapshots/zone_schema_snapshot.json`
* Strategy: simple JSON comparison (no snapshot framework)
* Test: build deterministic registry, export to dict → JSON, compare to snapshot
* Byte-stability test: export JSON string twice, assert equality

### Architecture Test

* Rule: `src/ezra/core/**` must not import `ezra.zones.registry` or any private module directly
* Core may import only from public surface: `ezra.zones` (i.e., `src/ezra/zones/__init__.py`)
* Test location: `tests/test_zone_architecture.py`

---

## 11. Handoff Instructions

1. Create branch: `m12-zone-schema-contract-lock`
2. Implement in small commits per step
3. Push PR
4. Monitor CI
5. Generate:
   * `M12_run1.md`
   * `M12_summary.md`
   * `M12_audit.md`
6. Update ledger in `docs/ezra.md`
7. Seed `docs/milestones/M13/` with stub

---

**End of Plan**
