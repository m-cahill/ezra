# M37 — Tool call / command log

| Step | Command / action |
| --- | --- |
| Inventory | `git status`, `git rev-parse HEAD`, `git ls-files .cursorrules docs/enhancements docs/prompts` |
| Removals | `git rm docs/enhancements/*.md` (three files) |
| Verify | `pytest`, `ruff`, `mypy`, `pip-audit`, `verify_distribution.py --mode ci-local` |
| Verify | `pytest`, `ruff`, `mypy`, `pip-audit`, `verify_distribution.py --mode ci-local` |
| PR | https://github.com/m-cahill/ezra/pull/40 (`head` `0b2fed8`); CI `25471712032` success except Dependency Review (infra) |
