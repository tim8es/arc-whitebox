# R259 terminal report - fixture-path successor

Status: **INFRA_ERROR before parent/candidate science; no retry**

## Frozen control

- run ID: `R259-BPK2K-ONE-SHOT-20260923-A1`
- protocol commit: `13a44d9cd19ecafc769c9eb8968cfd6ed5cd7a98`
- workflow commit: `65394e2679bebd7005e7fba13de3166a2c5800d2`
- arm commit: `b1244e81d954c0fb960e5bf3df9160cabf51a501`
- branch: `research/r259-bpk2k-fixture-path-one-shot-20260923`
- immutable R258 terminal base: `d99a52d0d3cf0f1c946de78173588bc258e74b54`
- R258 receipt SHA256:
  `60e0ed2e62a400c5738a1da63c88b59c47352c5e872ec8f1e7935f60091472ef`

Coordinator preflight approved this exact protocol/workflow before arming. The arm commit
was the only post-workflow branch change and triggered exactly one workflow/attempt.

## Sole Actions execution

- run: `35841937858`
- job: `107118816693`
- attempt: `1`
- head: `b1244e81d954c0fb960e5bf3df9160cabf51a501`
- standard GitHub-hosted runner: `ubuntu-24.04`
- workflow conclusion: **failure**
- artifact: `10742010727` (`r259-one-shot-evidence`)
- artifact ZIP SHA256:
  `4d209b72457431f9e0636165da23e58b59f7f61ee2f8e58521e06c2b73277cd8`

Exactly one R259 Actions run exists. No rerun or second workflow was dispatched.

## Passed pre-science controls

The following completed successfully:
- full-history checkout (`fetch-depth: 0`);
- frozen protocol ancestry and changed-path guard;
- all frozen Git-blob/SHA256 source checks;
- static AST fixture-manifest filename preflight;
- Python 3.11.16 setup;
- pinned NumPy 2.4.6 / FlopScope 0.12.1 / WhestBench 0.16.1 wheel hashes and runtime checks;
- pinned V25 parent source download/hash;
- fixture generator execution.

The static preflight retained:

`R259_FIXTURE_PATH_PREFLIGHT_PASS expected=R254_FIXTURE_RUNTIME_MANIFEST.json emitted=R254_FIXTURE_RUNTIME_MANIFEST.json`

so the R258 filename defect is repaired.

## Exact R259 infrastructure failure

The immutable fixture runtime manifest was generated at the correct path and has SHA256:

`4c14e8b3907907c73d061a9d46575d0847971aa8fda3ef642826c7118b33e105`.

The workflow then evaluated this stale assertion:

`assert d["independent_replay"]["all_layer_hashes_equal"] is True`

but the immutable runtime manifest has no key named
`independent_replay["all_layer_hashes_equal"]`.

GitHub log terminates the fixture verification step with:

`KeyError: 'all_layer_hashes_equal'`

The retained manifest actually records:
- top-level `replay_equal: true`;
- 16 top-level `layer_sha256` values;
- 16 `independent_replay.layer_sha256` values;
- the two 16-layer hash arrays are exactly equal;
- top-level and replay truth SHA256 are equal;
- top-level and replay concatenated-weight SHA256 are equal.

Thus fixture generation/replay evidence itself is internally consistent. The failure is
a workflow-side replay-schema assertion mismatch, not evidence about BPK2K science.

## Execution accounting

Not executed:
- V25 parent estimator execution;
- BPK2K candidate construction;
- BPK2K candidate execution;
- target-free MSE/FLOP/residual gates;
- candidate validation;
- live R209 identity;
- public mini-100;
- public gates.

Counts:
- parent executions: 0
- candidate constructions: 0
- candidate executions: 0
- target-free measurements: 0
- public measurements: 0

The workflow receipt decision is
`INFRA_ERROR_BEFORE_TARGET_FREE_RESULT`; target-free/public fields are null.

Scientific status is **UNEVALUATED**. No BPK2K MSE, FLOP, timing, public-score,
improved-row, paired-gain or rank claim is made.

## Artifact integrity

The downloaded ZIP independently matches the GitHub artifact digest above.
It contains 16 files. `R259_ARTIFACT_HASHES.json` maps 15 files and all 15 hashes
recompute with zero mismatches.

Key hashes:
- workflow receipt:
  `b74dda95f641fdd145352ea8f25834d54f9452a8e6239c3b8cf80f2e7b5c94f8`
- artifact hash map:
  `95d730051381125cf5300eeedc931015716b0342a5092b65da93ef053be8ac6e`
- runtime versions:
  `e9f9d943b5aa2ac563ce1c62fa685a99c482c1dc406e380709eb9fe8d835eda7`
- runtime fixture manifest:
  `4c14e8b3907907c73d061a9d46575d0847971aa8fda3ef642826c7118b33e105`
- pinned V25 source:
  `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`

## Terminal disposition

R259 is terminal **INFRA_ERROR** under the exactly-one-workflow/no-rerun rule.
Workflow conclusion: **failure**.
Research status: **INFRA_ERROR**.
Scientific status: **UNEVALUATED**.

No tuning, paid/private/holdout/full run, R223/R244 artifact access, submission,
leaderboard/canonical edit, or R254/R257/R258 history rewrite occurred.
