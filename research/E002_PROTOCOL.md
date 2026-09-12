# E002 Network-Conditioned Adaptive Blend Protocol

Status: baseline phase preregistered before any E002 score.

## Objective

Test whether a low-capacity, cheap network-conditioned blend between the
analytic covariance estimator and whitened-antithetic sampling improves over a
globally fixed blend at comparable adjusted compute.

## Fixed environment

- Dataset: `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`
- Development split: `mini`
- Width/depth: 1024 / 16
- Per-MLP FLOP budget: `2**41`
- Seed policy: use the grader-provided `mlp.seed`; no seed sweep
- Holdout: untouched during baseline/development screening
- External experiment budget gate: `$6`

## Baseline definition

The ledger names the E002 baseline `fixed_0.75_0.25_blend`. For this experiment
that means, per layer and neuron:

`prediction = 0.75 * covariance_prediction + 0.25 * sampling_prediction`

The sampling branch is the frozen whitened-antithetic implementation, but its
sample budget is reduced so the *combined* estimator remains near the 10%
score-floor boundary:

- covariance branch: the pinned `CovarianceEstimator`
- sampling branch: `WhitenedAntitheticEstimator(target_utilization=0.075)`
- competition-shape sample count: 4230 trajectories
- fixed covariance weight: `0.75`
- fixed sampling weight: `0.25`

E001 measured the same covariance + 0.075 sampling compute envelope at mean
utilization `0.09854008`, so this baseline is expected to remain below 10%, but
E002 promotion decisions use measured utilization rather than this estimate.

## Baseline gate

Before designing or scoring an adaptive rule:

1. TDD-implement the fixed blend.
2. `whest validate` it.
3. Score it once on Phase-2 `mini` with the official local runner.
4. Record final-layer MSE, all-layer MSE, adjusted score, utilization and
   failures in the ledger.

No adaptive parameter search starts before this baseline is measured.

## Adaptive phase constraints

After the fixed baseline is frozen, preregister before scoring candidates:

- the exact cheap weight-derived features;
- feature normalization/clipping;
- the low-capacity mapping from features to blend weight;
- the development candidate grid/rules;
- a development promotion threshold and tail guard;
- the untouched holdout protocol.

Any materially new feature family or post-result coefficient search requires a
new experiment ID or an explicitly logged E002 sub-experiment before execution.

## Final acceptance criterion

The ledger acceptance criterion remains authoritative: promote only with at
least 8% median gain versus the fixed blend on the preregistered holdout and no
>10% tail regression, at comparable adjusted compute and without material
failure regression.
