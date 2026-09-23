# R256 static repair — R254 BudgetContext telemetry boundary

Status: **REPAIR COMPLETE / OFFLINE REGRESSION PASS / NOT AUTHORIZED TO RUN R257**

R256 is an isolated static/offline repair only. It does not rewrite R254, trigger
Actions, run the estimator/benchmark/science, inspect R209/public data, access
private/holdout data, submit, or mutate canonical/leaderboard state.

## Queue and base

- central assignment revision: 256
- owner: `r254-harness-repair-responsive`
- claim revision/commit: 257 / `bd37001bcb9cda9da75232542db4d2897270f8fc`
- start revision/commit: 258 / `d7c8b534fab4157536101cc15e214bbee87e069f`
- isolated branch: `research/r256-r254-harness-telemetry-repair-20260923`
- exact R254 execution base/head: `ff40219e132ce208428b7acfb1a03a79cd535be7`
- patch commit: `625992a673a9b1ceee136a2b8b4b27da378a824d`

The patch commit is one commit ahead of the exact R254 execution head and adds only:

- `research/r256/r254_one_shot_repaired.py`
- `research/r256/r256_timing.py`
- `research/r256/test_r256_timing_boundary.py`

No `research/r254/*`, workflow, result, canonical, or leaderboard file changed.

## Confirmed primary-source contract

R255 already proved the actual R254 runtime mismatch from immutable evidence:
R254 called `BudgetContext.summary()`, stored the returned string, and later chained
`.get("residual_wall_time_s")`, causing:

`AttributeError: 'str' object has no attribute 'get'`.

Primary FlopScope 0.12.1 source at release commit
`b599f015b0bc005b1edb6d7a1b10e0814675e693`, client budget blob
`93349b139b3a08bdd67a7bc37b1b446c681c835c`, defines:

- `BudgetContext.summary_dict(...) -> dict`
- `BudgetContext.summary(...) -> str`
- `BudgetContext.residual_wall_time_s -> float | None`

The residual property documentation states that it is the measured participant-Python
residual bucket, live in an open context and the closed total after exit, and matches
`summary_dict()["residual_wall_time_s"]`.

WhestBench primary source commit
`4794ce8673c1221bdb245b19e933ae0afd7ffa3c`, subprocess worker blob
`33f9d48793e67dd95180aadbcdd024720019348e`, likewise reads
`budget_ctx.residual_wall_time_s` for its residual timing payload.

R256 therefore uses the supported typed property
`ctx.residual_wall_time_s`. Unlike WhestBench's reporting fallback, the R256 gate does
**not** convert unknown timing to zero.

## Minimal repair

Original harness:

- path: `research/r254/r254_one_shot.py`
- Git blob: `52f1885fcb4fc3cfb99a0ad2fc6b8517187605d9`
- SHA256: `3cd153cbe3a5687acbb83f730c1cefa45c5d6b256ca375c1dbc576ace831ba11`

Repaired isolated harness:

- path: `research/r256/r254_one_shot_repaired.py`
- Git blob: `ca0eb5b53d86c4fa708c2b1cb4ed34a8146494ca`
- SHA256: `6b6b77d3bd539acfcab535e8b4727e67a45e512aacfdc2d7369b5fbd9acb5cfd`

Timing helper:

- Git blob: `ea26de92d74ea6b4432e1f89301a7d55c9e52ae2`
- SHA256: `dd7ea8de33d7810ad22087592ab0f744dcfec94903de13472d0a0c1dbb619cc6`

Regression test:

- Git blob: `4c273590b61f6f1624c68bdbb815891403c534fa`
- SHA256: `fa5a1b8d6cc6f93487cda87ba0ed2e7d87ca3c0ef913197a30e9ed483c2b8b17`

The repaired harness still calls `summary()` only as display text, but captures the
typed measured value separately from `ctx.residual_wall_time_s`.

`require_residual_wall_time` accepts only finite, nonnegative numeric values. A
missing value produces a named gate failure such as
`candidate_residual_wall_time_unavailable`; invalid values produce
`*_residual_wall_time_invalid`. Neither path substitutes `0.0`.

## Frozen invariants

Static comparison confirms:

- BPK2K parent `OLD` formula block: byte-identical
- BPK2K candidate `NEW` formula block: byte-identical
- pinned V25 parent SHA constant: unchanged
- `BUDGET=2**41`: unchanged
- final MSE ratio gate `<=0.95`: unchanged
- all-layer MSE ratio gate `<=0.98`: unchanged
- improved-layers gate `>=12`: unchanged
- max per-layer degradation gate `<=1.10`: unchanged
- candidate FLOPs `<= parent`: unchanged
- target-free residual gate: unchanged as
  `candidate <= 1.05 * parent + 0.005`
- no unknown timing default to zero remains
- frozen workflow blob remains
  `649e7b9184e0d8521636fd1af23fb9e4359b3a64`
- public `--residual-wall-time-limit 0.4`: unchanged
- fixture manifest blob remains
  `5a6eb7bbfc07bf9e6609ee6cfbb2b2ea9e17ebf8`
- candidate-spec blob remains
  `6bffbdfd113bba80cc72cd375cdc44138f9c0845`

Fixture seed/hash contract is therefore unchanged:
seed `254001`, weights SHA256
`199e5fd8c669ec927717a12f0a3bbcee83e37db8db6e61e8c50eb791f457b3f0`,
truth SHA256
`58354221cedab39e900d78040a8383df45672425389f3865b731eea7b0063f1d`.

## One offline regression check

Exactly one repair regression script was run locally:

`python test_r256_timing_boundary.py`

Result:

`R256_OFFLINE_REGRESSION_PASS`

The check is deliberately non-scientific and dependency-light. It exercises the
actual source/runtime-confirmed API shape (`summary()->str`,
`residual_wall_time_s->float|None`) and verifies:

1. measured numeric residual timing is preserved;
2. `None` remains `None` and creates a fail-closed gate failure rather than zero;
3. non-finite residual timing is rejected.

No R254 harness, candidate, fixture, benchmark, public data, or Actions workflow was
executed by this test.

## Disposition

A reliable supported timing source **was established**, so R256 is not blocked.
The patch is suitable for independent review only.

R256 does **not** authorize R257, a repaired scientific run, public access, or any
submission. R257 requires a separate coordinator instruction after independent review.

## Primary/source links

- R255 receipt:
  https://github.com/tim8es/arc-whitebox/blob/8a541a20acf9d3dfc60cf395ecf60e20160298bf/research/r255/R255_RECEIPT.json
- R254 executed harness:
  https://github.com/tim8es/arc-whitebox/blob/ff40219e132ce208428b7acfb1a03a79cd535be7/research/r254/r254_one_shot.py
- FlopScope 0.12.1 release:
  https://github.com/AIcrowd/flopscope/commit/b599f015b0bc005b1edb6d7a1b10e0814675e693
- FlopScope BudgetContext source:
  https://github.com/AIcrowd/flopscope/blob/b599f015b0bc005b1edb6d7a1b10e0814675e693/flopscope-client/src/flopscope/_budget.py
- WhestBench worker source:
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/subprocess_worker.py
