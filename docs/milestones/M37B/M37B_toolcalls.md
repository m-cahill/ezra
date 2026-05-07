# M37B — Tool call / command log

Fragmentary log of commands executed during M37B implementation (agent session).

| Step | Command / action |
|------|-------------------|
| Git state | `git status --short; git rev-parse HEAD; git branch --show-current` |
| Supply chain | `pip-audit -r requirements.txt` |
| Lockfile tooling | `pip-compile --version` |
| Tests | `pytest -q` (full); `pytest -q tests/test_distribution_verification.py` |
| Lint | `ruff format scripts/verify_distribution.py`; `ruff format --check .`; `ruff check .` |
| Types | `mypy src` |
| Docs | Edited `docs/release/DISTRIBUTION_VERIFICATION.md`, `REFACTOR.md`, `docs/ezra.md` |
| Workflows | Edited `.github/workflows/ci.yml`, `.github/workflows/release.yml` |

Post-PR (maintainer):

- `gh pr checks <M37B_PR_NUMBER>`
- `gh run view <M37B_CI_RUN_ID> --json conclusion,headSha,event,workflowName,url`
- `gh run view <M37B_CI_RUN_ID> --log-failed`
