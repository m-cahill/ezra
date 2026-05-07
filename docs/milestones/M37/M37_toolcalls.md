# M37 — Tool call / command log

| Step | Command / action |
| --- | --- |
| Inventory | `git status`, `git rev-parse HEAD`, `git ls-files .cursorrules docs/enhancements docs/prompts` |
| Removals | `git rm docs/enhancements/*.md` (three files) |
| Verify | `pytest`, `ruff`, `mypy`, `pip-audit`, `verify_distribution.py --mode ci-local` |
| PR | `gh pr create` (after commit) |
