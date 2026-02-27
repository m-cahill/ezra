# M29 Tool Calls Log

| Timestamp | Tool | Purpose | Target / Files | Status |
| 2026-02-27 | ReadFile | Review prior milestone toolcall format and plan | docs/milestones/M26/M26_toolcalls.md, docs/milestones/M26/M26_plan.md | Complete |
| 2026-02-27 | Shell | Create milestone branch | git checkout -b m29-hermetic-reproducibility | Complete |
| 2026-02-27 | ApplyPatch | Create M29 plan file | docs/milestones/M29/M29_plan.md | Complete |
| 2026-02-27 | ApplyPatch | Create M29 toolcalls log | docs/milestones/M29/M29_toolcalls.md | Complete |
| 2026-02-27 | Shell | Commit M29 scaffold files | docs/milestones/M29/M29_plan.md, docs/milestones/M29/M29_toolcalls.md | Complete |
| 2026-02-27 | ReadFile | Inspect CI workflow and EPB hash/signing contracts | .github/workflows/ci.yml, src/ezra/tools/_epb_hash.py, tests/contracts/test_epb_artifact_signing.py | Complete |
| 2026-02-27 | ReadFile | Review EPB consumer certification fixture helper | tests/contracts/test_epb_consumer_certification.py | Complete |
| 2026-02-27 | ApplyPatch | Add Python matrix and hermetic reproducibility gate | .github/workflows/ci.yml | Complete |
| 2026-02-27 | Shell | Run focused EPB contract tests | tests/contracts/test_epb_consumer_certification.py, tests/contracts/test_epb_artifact_signing.py | Complete |
| 2026-02-27 | Shell | Inspect branch status and current diff | .github/workflows/ci.yml, docs/milestones/M29/M29_toolcalls.md | Complete |
| 2026-02-27 | Shell | Commit CI matrix and hermetic gate changes | .github/workflows/ci.yml, docs/milestones/M29/M29_toolcalls.md | Complete |
