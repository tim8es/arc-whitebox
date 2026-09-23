# R275 — clean main integration of workflow preflight

**Outcome:** COMPLETE. The hardened R272/R274 preflight was integrated onto a clean branch from current `main` and opened as a review PR without merge.

## Clean integration base

- `main` base: `b5b988f8ec49a5ec473d59fcbfdfaf8c4350c850`
- source R274 branch was confirmed unsafe for direct PR: `main...research/r274-workflow-preflight-hardening-20260923` was diverged by 426 commits ahead / 1 behind.
- clean integration branch: `research/r275-workflow-preflight-integration-20260923`
- implementation commit: `128e412673f2d495b999625a4fcc8b171c50691d`

Before evidence files were added, `main...R275` was exactly 1 commit ahead / 0 behind and changed only:

1. `scripts/arc_workflow_preflight.py`
2. `tests/test_arc_workflow_preflight.py`
3. `docs/workflow-preflight.md`

No historical workflow, research branch history, old receipt/result, or control state was copied into the integration commit.

## Integrated files

The production guard is byte-identical to the hardened R274 guard:

- `scripts/arc_workflow_preflight.py`
  - git blob: `a654fa1e15bfa8f9c2bfaa39073ecdf044a74a12`
  - SHA256: `8d002d9f98ce717d2f84757bb2efea9f5b2c4660fb097b230bcc199d6c310cdf`

The two R272/R274 focused suites were consolidated into one reviewable 10-case file:

- `tests/test_arc_workflow_preflight.py`
  - git blob: `a5c4cc5801d30af3ffcdcb9b53c0d5cc932593fb`
  - SHA256: `041102f9622deb96eb2fd886aca771de0dd0553ad6efbf626ea6d39a3449a5e8`

Invocation and fail-closed semantics are documented in:

- `docs/workflow-preflight.md`
  - git blob: `81d37a3759c0fc67b6bc8705e05a74e01877d4bd`
  - SHA256: `1b1118309f616c7e0d977d2c0da3e6073b99de2fc16459f7d338cef1d9c2a3ba`

## Focused offline verification

Exact command recorded at R275 start and executed against exact committed bytes:

`python -m unittest tests/test_arc_workflow_preflight.py -v`

Result: **10/10 PASS**, return code 0.

The committed local copies reproduced the Git blobs above before execution. Unittest output SHA256 (stderr, where unittest writes verbose output):

`49d62a48aa3753688382c26f6b51a6b55f7e70d5e0e5853f5d8c49a778f92f98`

No Actions, fixture generator, estimator, scientific/research run, competition dataset, or paid resource was executed.

## Review PR

PR: https://github.com/tim8es/arc-whitebox/pull/35

- base: `main`
- head: `research/r275-workflow-preflight-integration-20260923`
- state: OPEN
- draft: false
- mergeable after GitHub computed status: true
- merged: false

The PR was opened for review only. R275 did not merge it.
