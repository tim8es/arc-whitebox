# E002 Network-Conditioned Adaptive Blend Protocol

Status: DONE / DROP. Fixed blend retained as a stronger measured baseline; the
network-conditioned adaptive extension failed its development feasibility gate
before internal validation or holdout access.

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
- External experiment budget gate: `$6`

## Fixed baseline definition

The E002 baseline is `fixed_0.75_0.25_blend`:

`prediction = 0.75 * covariance_prediction + 0.25 * sampling_prediction`

Branches:

- covariance: pinned `CovarianceEstimator`
- sampling: frozen `WhitenedAntitheticEstimator(target_utilization=0.075)`
- competition-shape sample count: 4230 trajectories
- covariance weight: `0.75`
- sampling weight: `0.25`

### Measured baseline

Frozen estimator commit:

`f829eb59cd5237679d20a42982e1c2c3dac93c08`

GitHub Actions:

- run: `34706447352`
- job: `103587246914`
- artifact: `10302525674`

Official Phase-2 mini result, 100 MLPs:

- adjusted final-layer score: `3.02e-07`
- raw final-layer MSE: `3.02e-06`
- all-layers MSE: `2.19e-06`
- mean compute utilization: `0.09850853`
- total estimator FLOPs: `2.17e13`
- best MLP adjusted score: `1.77e-07`
- worst MLP adjusted score: `4.97e-07`
- failures: `0/100`
- scorer duration: `251.872890s`
- wall clock: `18:04.15`

The benchmark/scoring step completed successfully. The workflow's final verify
step failed only because the frozen snapshot still contained an import-order
Ruff defect in `tests/test_fixed_blend.py`. That defect was fixed separately in
commit `8e4e47968c063b881354aaf1ef2206dac182c538` without changing estimator
logic; subsequent branch CI is green. Therefore the scorer result above is the
frozen baseline measurement.

Relative to E000 covariance MSE `4.05e-06`, this fixed blend improves raw
final-layer MSE by about 25.4% while remaining below the 10% score floor.

## Public-frontier constraint

The public fixed-blend write-up reports a global least-squares covariance weight
near `0.7341`, and the preregistered `0.75` weight is only about 0.118% worse
than that global optimum. Therefore E002 must not spend a candidate on merely
retuning a single global coefficient. Any promoted E002 candidate must be
genuinely network-conditioned.

## Adaptive diagnostic phase — preregistration

Before scoring any adaptive estimator, use only a fixed development subset of
the public `mini` split to test whether cheap network features predict the
per-network oracle blend weight.

### Development partition

- Diagnostic/fit subset: the first 20 MLP records in deterministic dataset order.
- Internal validation subset: the remaining 80 mini MLP records.
- No `full` split access during feature discovery or coefficient fitting.
- No seed sweep.

The 80-record internal validation subset is not used to select feature families
or fit coefficients. It is evaluated only after the rule is frozen.

### Oracle target on the 20-record diagnostic subset

For final-layer vectors, let:

- `c` = covariance prediction
- `s` = frozen whitened-antithetic prediction
- `y` = ground truth

For prediction `s + w * (c - s)`, compute the clipped per-network oracle:

`w_oracle = clip(dot(y-s, c-s) / dot(c-s, c-s), 0, 1)`

This target is diagnostic only; ground truth is never available to the submitted
estimator.

### Allowed cheap feature family

Use only statistics already available from the deterministic covariance pass or
directly from known weights. Initial feature family is restricted to:

1. late-layer ReLU uncertainty:
   `mean(4 * Phi(alpha) * (1 - Phi(alpha)))` over the final four layers;
2. late-layer covariance off-diagonal energy ratio:
   `sum(offdiag(cov)^2) / sum(cov^2)` over the final four layers;
3. final-layer versions of the same two quantities.

No neural/meta-model, tree ensemble, hidden labels, seed feature, or arbitrary
feature search is allowed in E002.

### Model capacity and freeze rule

Fit only a linear/ridge mapping from standardized allowed features to covariance
weight. Standardization means mean/std from the 20-record diagnostic subset
only. Candidate regularization grid is frozen to:

`ridge_lambda in {0.0, 1.0, 10.0}`

Select lambda by leave-one-out MSE on the 20 diagnostic records. Clip predicted
network covariance weight to `[0.55, 0.90]`.

After this fit, freeze:

- selected features;
- diagnostic means/stds;
- coefficients/intercept;
- selected ridge lambda;
- clipping bounds.

No coefficient or feature changes are permitted after observing the 80-record
internal validation result under E002.

## Diagnostic result

GitHub Actions run `34707605404`, job `103590387429`, commit
`692b261479c72d4c226590fb7c37ad93954051d8` completed successfully after a
pure test-loader fix. The diagnostic used exactly the preregistered first 20
`mini` records.

Per-network oracle covariance weights varied from `0.59351436` to `0.81176923`
(mean `0.72630691`, std `0.05255466`), so heterogeneity exists. However that
heterogeneity has very little exploitable value within the scalar blend family:

- fixed 0.75 aggregate MSE on the 20 records: `3.139994410056683e-06`
- per-network oracle aggregate MSE: `3.094269192767133e-06`
- oracle upper-bound aggregate gain: about `1.456%`

Thus even an impossible estimator that knew the ground-truth-optimal scalar
blend weight for every network would remain far below the E002 8% target.
This is a structural negative result, not merely a weak feature-model result.

The preregistered cheap features also showed weak linear association with the
oracle weight:

- late ReLU uncertainty: `r=0.0383`
- late off-diagonal ratio: `r=0.1265`
- final ReLU uncertainty: `r=-0.1157`
- final off-diagonal ratio: `r=0.0596`

The selected ridge model used `lambda=10.0`; leave-one-out weight MSE was
`0.00329592`, while the oracle-weight variance is only about `0.002762`, so the
feature rule does not beat a constant-weight predictor reliably enough to
justify scoring the untouched 80-record subset.

## Decision

`DROP` the network-conditioned scalar blend hypothesis under E002. Do not run
the 80-record internal validation and do not access the `full` holdout for this
experiment. The fixed 0.75/0.25 blend remains useful as a stronger measured
baseline (`3.02e-06` raw MSE), but the remaining error cannot be removed at the
required scale by choosing a better scalar covariance-vs-sampling weight per
network.

## Mechanistic implication

The negative oracle bound is the main scientific result: the two estimator
vectors are already too geometrically aligned for scalar mixing to expose a
large unused degree of freedom. Future work should change the estimator's error
direction or resolution — e.g. layer/neuron/subspace-conditional corrections,
higher-order closure, or structured residual estimation — rather than spend
compute predicting a single network-level mixing coefficient.
