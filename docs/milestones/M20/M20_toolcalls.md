# M20 Tool Calls Log

**Milestone:** M20  
**Status:** In Progress

---

## Tool Calls

| Timestamp | Tool | Purpose | Files/Target | Status |
|-----------|------|---------|--------------|--------|
| 2026-02-27 | write | Populate M20 plan document | docs/milestones/M20/M20_plan.md | ✅ Complete |
| 2026-02-27 | run_terminal_cmd | Create working branch | git checkout -b m20-runtime-contract-seal | ✅ Complete |
| 2026-02-27 | search_replace | Convert ImageInput, OCRResult, ModelArtifactMetadata to frozen dataclasses | src/ezra/types.py | ✅ Complete |
| 2026-02-27 | search_replace | Seal EPB bundle dict with MappingProxyType | src/ezra/epb/builder.py | ✅ Complete |
| 2026-02-27 | search_replace | Add structural hash assertion utility | src/ezra/epb/hasher.py | ✅ Complete |
| 2026-02-27 | search_replace | Update canonicalization to handle MappingProxyType | src/ezra/epb/canonical.py, src/ezra/epb/zone_adapter.py, src/ezra/zones/projector.py | ✅ Complete |
| 2026-02-27 | search_replace | Update schema validator to handle MappingProxyType | src/ezra/epb/schema_validator.py | ✅ Complete |
| 2026-02-27 | search_replace | Fix test that uses .bbox.copy() | tests/test_zone_projector.py | ✅ Complete |
| 2026-02-27 | write | Create immutability test suite | tests/test_runtime_immutability.py | ✅ Complete |
| 2026-02-27 | search_replace | Update schema validation tests to handle sealed bundles | tests/test_epb_schema_validation.py | ✅ Complete |
| 2026-02-27 | run_terminal_cmd | Run full test suite | pytest tests/ | ✅ Complete (228 passed, 4 skipped) |

---

**End of M20 Tool Calls Log**

