# M40 Visibility Merge Record

| Field | Value |
|---|---|
| PR | https://github.com/m-cahill/ezra/pull/45 |
| Branch | `ops/m40-public-release-execution` |
| Final head SHA | `44d34881a7f762a49669e1f1d3546d51710987f0` |
| Merge SHA | `ac18a7ebbe806c098223d055a3b07fb342be791d` |
| Merge date | 2026-05-08T00:16:34Z (`mergedAt`, squash to `main`) |
| Merge method | squash |
| Post-merge CI | https://github.com/m-cahill/ezra/actions/runs/25529262946 — **success** |
| Remaining red checks | None observed on this `main` run |

## Scope Confirmation

M40 visibility execution was visibility-only.

No tag, GitHub Release, PyPI publish, Pages enablement, branch protection change, workflow edit, dependency edit, runtime edit, EPB spec edit, secret-boundary change, or `docs/prompts/` change occurred.

## Public Visibility Result

| Field | Value |
|---|---|
| Repository | `m-cahill/ezra` |
| Visibility before | `PRIVATE` |
| Visibility after | `PUBLIC` |
| Public URL | https://github.com/m-cahill/ezra |

## Documented Limitations Carried Forward

- Dependency Review requires GHAS / dependency graph.
- SLSA artifact attestation behavior must be verified on a future public workflow/release run before claiming success.
- Pages deploy remains gated until explicitly enabled.

## Authorized Next Step

No tag, GitHub Release, PyPI publish, Pages enablement, or announcement is authorized by this merge. Those remain separate maintainer decisions.
