# R281 — PR #35 workflow preflight integration fix

**Outcome:** COMPLETE. Continued the existing PR #35 head and closed all three HIGH R277 false-PASS classes without Actions, merge, fixture/estimator execution, science, paid resources, or private/competition data.

## Queue and source evidence

R281 was already RUNNING under the assigned owner `workflow-preflight-integration-fix` when this session refreshed live control, so no duplicate claim/start was published. Existing run ID: `R281-pr35-preflight-failclosed-fix-20260923`.

Primary review input:
- R277 receipt commit: `2ffac1885bdd2424b5e3dbf8519cd8159e23962e`
- R277 receipt SHA256: `97b2446a66bb00a38837f5cf0a5083ce2b61dcca668ca03969f0321743b86058`
- R277 verdict: `FINDINGS_NOT_PASS`

PR #35 branch: `research/r275-workflow-preflight-integration-20260923`.

## Tests-first sequence

The PR already contained a test-only R281 regression commit before production changes:
- regression commit: `65634dfedfa3d46be785d2b07ba3997b292be16e`
- it added focused cases for env-vs-with checkout configuration, clear/pop/helper mutation, exact manifest binding, and unsupported `.get()`.

Production fix:
- `886cebdface628cc49165f145c8afcd0476ff4ff`

The first local regression execution exposed a defect in three newly added synthetic test fixtures: they inserted a literal escaped newline into generated Python and raised SyntaxError before analyzer validation. The fixtures were corrected separately without rewriting earlier commits:
- fixture correction commit: `579c2d3c38c1489b8d9287d4fed63486002624a6`

## R277 findings closed

### F1 — checkout input scoping

`fetch-depth: 0` is accepted only when nested under the actual `actions/checkout` step's own `with:` block. A same-step `env.fetch-depth: 0` no longer satisfies the ancestry guard.

### F2 — manifest mutation fail-closed

Schema tracking now permits only the modeled `.update(...)` on a tracked manifest dict. `.clear()`, `.pop()`, other direct methods, and helper calls receiving the tracked manifest fail closed as unsupported mutations instead of retaining stale schema.

### F3 — exact manifest binding and access tracing

`json.loads` is accepted only when its input is the exact runtime-manifest path read via `.read_text()`. Merely mentioning the manifest path in another expression no longer binds the loaded object. Unsupported method access such as `d.get("ghost")` is rejected rather than silently omitted from key-path validation.

## Offline verification

Production script was materialized locally and verified byte-for-byte by Git blob:
- `scripts/arc_workflow_preflight.py`
- git blob: `f9b01ba259cd57bd1692fbfc904585b05f561000`
- SHA256: `1f73f557d943dc6b4fb4d42b2a5935f1d627082b292d8465f5018794dc8a38ce`

A local standard-library contract harness exercised the same 10 prior compatibility contracts plus the 6 R281 regressions against that exact production blob:
- compatibility: **10/10 PASS**
- R281 regressions: **6/6 PASS**
- total: **16/16 PASS**
- output SHA256: `d8b5331ce601706d133f7133b97a376d736350df9517b2d166bd76ec296cb726`

The committed focused test file after fixture correction is:
- `tests/test_arc_workflow_preflight.py`
- git blob: `c94c6e7521a612d496f544eec19c863bc05bbb73`

No GitHub Actions run was triggered. No workflow file was edited.

## PR state

PR #35 remains open and unmerged. Its description was updated to enumerate the R277 fixes and the 16/16 offline contract result. Before R281 evidence files, the branch was ahead 5 / behind 0 from `main`, with changes confined to the existing preflight integration/evidence files.
