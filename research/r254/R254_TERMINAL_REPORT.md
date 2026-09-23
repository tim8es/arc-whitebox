# R254 terminal report — V25-BPK2K one-shot

Status: **INFRA_ERROR; scientific comparison unevaluated; no retry**

## Frozen method

R254 selected exactly one history-deduplicated global-accuracy hypothesis:
`V25-BPK2K-BALANCED-CUMULANT-REDUCTION`.

The candidate leaves the V25 moment/cumulant terms, coefficients, ranks, sources,
lambda logic and rider unchanged. It changes only the parenthesization of the repeated
`PK2K_TABLE` contribution sums from sequential accumulation to a fixed adjacent-pair
balanced binary tree. In real arithmetic the formulas are identical and the addition
count remains m-1 for m contributions.

Frozen protocol/spec/novelty/fixture evidence precedes the sole workflow trigger.

## Sole authorized workflow

- workflow: `.github/workflows/r254-one-shot.yml`
- branch: `research/r254-balanced-rider-reduction-20260923`
- workflow head: `ff40219e132ce208428b7acfb1a03a79cd535be7`
- GitHub Actions run: `35834163527`
- job: `107093511576`
- run attempt: 1
- runner: standard GitHub-hosted `ubuntu-24.04`
- artifact: `10737609819`, `r254-one-shot-evidence`
- artifact ZIP SHA256:
  `9512985e1af5a98afa9d4ca4e87f6935d8e15ac9c73a28a3a7f0c3ddc5db05e7`

There is exactly one R254 Actions run. No retry or second workflow was triggered.

## Pre-science/runtime evidence

All three pinned wheel digests passed before installation. Distribution-metadata
version checks also passed:

- Python 3.11.16
- NumPy 2.4.6
- FlopScope raw/normalized 0.12.1 / 0.12.1
- WhestBench 0.16.1

The pinned V25 parent was fetched and verified:
Git blob `195373a110215256b759d7c172ba8c923c62e5cc`,
SHA256 `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`.

The production-shape fixture reconstructed successfully and its independent second
implementation agreed on all 16 layer hashes, concatenated weight hash
`199e5fd8c669ec927717a12f0a3bbcee83e37db8db6e61e8c50eb791f457b3f0`
and truth hash
`58354221cedab39e900d78040a8383df45672425389f3865b731eea7b0063f1d`.
Truth generation uses only fixed-order scalar monomial/path products and no BLAS
reduction.

## What executed

The unchanged parent executed first. The harness constructs the candidate only after
`parent_gate` returns true. The retained artifact contains
`R254_CANDIDATE_SOURCE.py` SHA256
`55cc395d69309dcb13c38ae3b91032dd4b8d0d6b6caf5eb09f0dad03328723e0`;
therefore the parent gate passed in control flow and candidate construction occurred.

The candidate then executed far enough to emit its own V25 nonlinear/symmetry warnings.
However the harness crashed while evaluating the frozen candidate gate, before writing
`R254_TARGET_FREE_RESULT.json`.

Exact terminal exception:

`AttributeError: 'str' object has no attribute 'get'`

at `r254_one_shot.py` candidate-gate residual-time extraction:

`p.get("budget_summary", {}).get("residual_wall_time_s", 0.0)`.

The runtime `BudgetContext.summary()` value retained in the in-memory parent result was
a string, while the harness incorrectly assumed a mapping. Target-free exit code is 1.
The workflow receipt therefore correctly records
`INFRA_ERROR_BEFORE_TARGET_FREE_RESULT`.

This is a harness/integration defect, not a scientific BPK2K result.

## Scientific accounting

Because the crash occurred before the target-free JSON was serialized:

- parent execution count: 1;
- candidate construction count: 1;
- candidate execution count: 1;
- **persisted parent scientific measurements: 0**;
- **persisted candidate scientific measurements: 0**;
- persisted parent/candidate MSE ratio: unavailable;
- persisted parent/candidate FLOP ratio: unavailable;
- persisted target-free gate verdict: unavailable;
- validation: skipped;
- public identity access: skipped;
- public mini-100: skipped;
- public measurements: 0.

The parent/candidate numerical values that existed only in process memory are not
reconstructed or inferred from warnings. BPK2K accuracy is therefore **UNEVALUATED**,
not accepted and not scientifically rejected.

## Immutable artifact hashes

- workflow receipt SHA256:
  `42fe988f6ce8f011d1f59e7ff4b582c94a0a554caf79dd2effcb50ad60bbb922`
- target-free stderr SHA256:
  `f0cdc771a5aee2138284e809fbbc5c2e769698bd31ddda1907bafc0b50b2a386`
- runtime versions SHA256:
  `e9f9d943b5aa2ac563ce1c62fa685a99c482c1dc406e380709eb9fe8d835eda7`
- runtime fixture manifest SHA256:
  `4c14e8b3907907c73d061a9d46575d0847971aa8fda3ef642826c7118b33e105`
- candidate source SHA256:
  `55cc395d69309dcb13c38ae3b91032dd4b8d0d6b6caf5eb09f0dad03328723e0`

## Terminal disposition

R254 is terminal **INFRA_ERROR** under the one-workflow/no-retry rule. No repair or
rerun is authorized inside R254. No second method is substituted.

No paid/larger/private runner, holdout/private/full panel, R223/R244 output/artifact
access, submission, leaderboard/canonical mutation, R252 workflow edit, per-network
tuning or gate relaxation occurred.
