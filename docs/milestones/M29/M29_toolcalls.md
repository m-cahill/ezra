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
| 2026-02-27 | Shell | Commit toolcalls update entry | docs/milestones/M29/M29_toolcalls.md | Complete |
| 2026-02-27 | Shell | Push branch to origin | m29-hermetic-reproducibility | Complete |
| 2026-02-27 | Shell | Create M29 pull request | PR #28 | Complete |
| 2026-02-27 | Shell | Monitor PR checks and workflow status | GitHub Actions run 22504290359 | Complete |
| 2026-02-27 | Shell | Inspect failed workflow logs | GitHub Actions run 22504290359 | Complete |
| 2026-02-27 | ApplyPatch | Fix matrix artifact naming and py3.10 install gate | .github/workflows/ci.yml | Complete |
| 2026-02-27 | Shell | Commit and push first CI fix set | .github/workflows/ci.yml, docs/milestones/M29/M29_toolcalls.md | Complete |
| 2026-02-27 | Shell | Track latest CI run IDs and statuses | GitHub Actions runs 22504361016, 22504428388 | Complete |
| 2026-02-27 | ReadFile | Inspect CI status command background output | terminal run status output | Complete |
| 2026-02-27 | Shell | Inspect failed logs from follow-up runs | GitHub Actions runs 22504361016, 22504428388 | Complete |
| 2026-02-27 | ReadFile | Verify workflow sections after patching | .github/workflows/ci.yml | Complete |
| 2026-02-27 | rg | Find unintended matrix references in workflow | .github/workflows/ci.yml | Complete |
| 2026-02-27 | ApplyPatch | Re-scope M29 to dedicated hermetic matrix job | .github/workflows/ci.yml | Complete |
| 2026-02-27 | Shell | Validate hermetic hash module import path | src/ezra/tools/_epb_hash.py | Complete |
| 2026-02-27 | Shell | Commit and push dedicated hermetic matrix workflow | .github/workflows/ci.yml, docs/milestones/M29/M29_toolcalls.md | Complete |
| 2026-02-27 | Shell | Monitor green CI run and check matrix statuses | GitHub Actions run 22504550465 | Complete |
| 2026-02-27 | Shell | Capture hermetic comparison logs and hash evidence | Hermetic Reproducibility job logs | Complete |
| 2026-02-27 | Shell | Capture test/coverage evidence from CI logs | Test job logs (run 22504550465) | Complete |
| 2026-02-27 | ReadFile | Review prior milestone run-analysis formats | docs/milestones/M25/M25_run1.md, docs/milestones/M26/M26_run1.md | Complete |
| 2026-02-27 | ApplyPatch | Create M29 run analysis, audit, and summary docs | docs/milestones/M29/M29_run1.md, M29_audit.md, M29_summary.md | Complete |
| 2026-02-27 | ApplyPatch | Update ledger with M29 completion | docs/ezra.md | Complete |
| 2026-02-27 | ReadLints | Verify no new lint issues in edited files | .github/workflows/ci.yml, docs/ezra.md, docs/milestones/M29/* | Complete |
