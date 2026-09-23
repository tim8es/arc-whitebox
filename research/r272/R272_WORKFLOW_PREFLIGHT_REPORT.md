# R272 — offline workflow preflight guard

**Outcome:** COMPLETE. Added one narrow reusable offline guard and focused regression tests for the three infrastructure contracts that failed in R257–R259. No historical workflow/receipt was edited; no Actions workflow, estimator, scientific measurement, competition dataset, submission, leaderboard, or canonical file was run or changed.

## Inputs inspected

- Current `AGENTS.md`, `research/RESEARCH_PROCESS.md`, `research/control/STATUS.md`, and live control state at R272 start.
- R267 postmortem `research/r267/R267_WORKFLOW_POSTMORTEM.md` from branch `research/r267-workflow-postmortem-20260923`.
- Actual frozen workflow sources for R257, R258, R259, and R260 at their recorded workflow commits.
- Immutable `research/r254/r254_fixture.py`.
- Existing R259 filename preflight and R260 schema preflight.
- Current shared helper/test style (`scripts/arc_control.py`, `tests/test_arc_control.py`).

## Verified contracts from the historical sources

1. **R257 shallow history:** the workflow contained `git merge-base --is-ancestor` but `actions/checkout@v4` had no `fetch-depth: 0`.
2. **R258 manifest path:** checkout was repaired to full history, but the workflow read `R254_RUNTIME_FIXTURE_MANIFEST.json`; the generator writes `R254_FIXTURE_RUNTIME_MANIFEST.json`.
3. **R259 schema:** the filename was repaired, but the workflow asserted `independent_replay["all_layer_hashes_equal"]`; the generator emits `replay_equal`, `layer_sha256`, `weights_concat_sha256`, `truth_sha256`, and `independent_replay`, with no `all_layer_hashes_equal`.
4. **R260 repaired pattern:** full-history checkout and the corrected runtime-manifest contract were present, and R260 reached target-free science.

## Guard added

`scripts/arc_workflow_preflight.py` is standard-library only and intentionally narrow. It does not parse or modify workflow YAML semantically, execute a fixture, import an estimator, access the network, or read competition data.

It fails closed when:
- an ancestry guard is present without an `actions/checkout` step using `fetch-depth: 0`;
- a workflow runtime-manifest filename differs from the filename statically emitted by the fixture generator;
- inline JSON assertions in a runtime-manifest step reference keys not statically emitted by the generator.

`tests/test_r272_workflow_preflight.py` contains four focused cases: R257-like shallow history, R258-like filename mismatch, R259-like stale schema key, and an R260-like repaired contract.

## Offline check

The environment could not clone GitHub directly (`Could not resolve host: github.com`), so no network fallback or Actions run was used. The committed guard file was fetched through the authorized GitHub connector; its locally executed bytes reproduced Git blob `c50e96d37610af0a6745eb8d4fcbf83a16a00bc6`.

One local offline check exercised the four focused cases:

- R257-like shallow checkout → rejected: `fetch-depth: 0` required.
- R258-like wrong runtime manifest → rejected.
- R259-like `all_layer_hashes_equal` → rejected as absent from generator schema.
- R260-like repaired contract → PASS.

This check executed only the guard logic on synthetic strings. It did not execute the R254 fixture generator or any estimator/science.

## Scope and hashes

Implementation commit: `986770e65787b440bbce80ca24f97baf3601a349`

Diff from R272 branch base `afc0e19c9d3892ac1fe331f5c5105e4392579872` contains exactly:
- `scripts/arc_workflow_preflight.py` — git blob `c50e96d37610af0a6745eb8d4fcbf83a16a00bc6`
- `tests/test_r272_workflow_preflight.py` — git blob `fff37038b1992a913d9c1de3ff6d64d0ac664e3e`

No `.github/workflows/*`, historical receipt/result, submission, leaderboard, or canonical file changed.
