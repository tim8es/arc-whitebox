# E020 — fixed quadratic/Hermite residual rider on V25

Status: **preregistered development diagnostic**

Idempotency key: `ARC-E020-QUADRATIC-RIDER-20250915`

Base: canonical `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

## Frozen comparator

E007/V25 remains the fixed comparator:

- raw final-layer MSE: `2.23e-08`
- adjusted score: `8.17e-09`
- mean utilization: `0.36666448`
- failures: `0/100`

At unchanged utilization, the displayed E007 adjusted gate is crossed at raw `<2.2281951063271794e-08`, only `0.08094%` below `2.23e-08`. E020 therefore uses a stricter raw-gain gate of `0.25%` to stay clear of rounding/noise.

## Motivation and novelty

Upstream F47 showed that a cheap online linear mean-error rider on a pre-K4 K3 chain generalized strongly (test `3.65e-08 -> 2.52e-08`, about `1.45x`). After F68 memoryless K4 regeneration, refitting the same *linear* rider retained only about `1%` test gain and was called strategically dead because the old leaderboard needed much larger gains. Against today's E007 comparator, however, even a fraction of that residual predictability is enough to improve adjusted score.

E020 does **not** rerun the F47 linear rider. It tests one new fixed nonlinear closure of the remaining per-neuron mean residual using second-order Hermite interactions of already-live V25 observables. No new K3/K4 state is transported.

## Frozen base observables

At each post-ReLU layer, use exactly seven dimensionless/live features already available in V25:

1. `alpha = mu_pre / sigma`
2. `abs_alpha = abs(alpha)`
3. `phi = normal_pdf(alpha)`
4. `Phi = normal_cdf(alpha)`
5. `pred_scaled = predicted_post_mean / sigma`
6. `d3_scaled = D3 / sigma^3` (zero where D3 is unavailable)
7. `d21_scaled = (mean_j |D21_ij|) / sigma^3` (zero where D21 is unavailable)

No weight-derived identity, MLP name/seed, per-MLP coefficient or future-layer feature is allowed.

For each layer, fit means/scales of these seven features on fit dumps only, standardize to `z`, then use the fixed 36-dimensional map

`[1, z_1..z_7, (z_1^2-1)..(z_7^2-1), z_i z_j for i<j]`.

This is a single predetermined degree-2/Hermite map: no interaction selection, polynomial-degree search or regularization sweep.

## Frozen fit and validation

Official public Phase-2 mini rows contain `all_layer_means`; use them directly.

- fit indices exactly `0,1,2,3`;
- validation indices exactly `4,5,6,7`;
- all 16 layers are eligible and fitted once;
- fit trajectory is teacher-forced **only in the post-ReLU mean state**: after recording a layer's base prediction/features and target residual, the mean passed to the next layer is replaced by that row's `all_layer_means[layer]`; all other V25 cumulant/covariance states remain the unmodified model states;
- fit one pooled ordinary least-squares coefficient vector per layer from all fit neurons;
- freeze feature means/scales and coefficients before validation;
- validation is fully free-running: candidate corrections are applied online and propagate to later layers;
- baseline validation is the identical pinned V25 source with its historical mean-correction rider disabled (the shipped E007 setting).

Ordinary least squares is deterministic float64 SVD least-squares with no ridge. If a layer's fixed design is rank-deficient or has condition number `>1e8`, E020 is immediate NO-GO; do not regularize or delete features.

## Pinned source

Use `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, `estimators/estimator_v25.py` blob `195373a110215256b759d7c172ba8c923c62e5cc`.

The development harness may instrument that exact source to expose the seven live observables and to replace only the post-ReLU mean during teacher forcing / candidate replay. It must not change V25 lambda, source ranks, K4 logic, old-tier scheduling or any other state update.

## GO gates

All gates must pass:

1. Fixed design full rank at every fitted layer and condition number `<=1e8`.
2. Validation mean final-layer raw MSE gain `>=0.25%` versus the identical uncorrected V25 replay.
3. No individual validation dump final-layer MSE regresses by more than `1.0%`.
4. Validation all-layer MSE does not regress by more than `0.25%`.
5. Measured/projected total utilization `<=0.36670`.
6. Projected adjusted score using E007 raw scaled by the measured validation raw ratio and measured candidate utilization is strictly `<8.17e-09`.
7. Correction is finite and deterministic; repeated evaluation from the same features is bit-identical.
8. Exactly the frozen seven base observables and 36-dimensional map are used; one pooled coefficient vector per layer only; no per-MLP fit.
9. Added production persistent state is only the embedded feature normalization/coefficient tables; no `n x n` candidate state.
10. Focused added-correction residual proxy median `<=0.005 s` per MLP-equivalent.

## Kill rule

Any failed gate => `NO-GO / DROP E020`. No rescue under E020 by changing the feature set, degree, normalization, condition threshold, fit split, validation split, regularization, coefficient clipping, layer subset, target definition, or teacher-forcing rule. No official scorer, holdout, tuning or sweep.

## Primary-source evidence

- Public upstream F47/F68 research log at `504aldo/whest-p2-cumulant-k3@18c17e...`: the linear online correction is predictable only when K3/K4 non-Gaussian observables are present; on the V17 regeneration base the refit retained about `1%` test gain, establishing a quantitative residual-signal prior for this cheap rider.
- The official WhestBench dataset schema stores `all_layer_means` (`float32[depth,width]`) in public baked datasets, enabling an explicit fit/validation split without holdout access.
- Companion cumulant-propagation work, arXiv:2605.05179, uses Hermite/Wick structure for nonlinear moment corrections; E020's degree-2 residual map is an empirical rider, not a claim from that paper.

The hypothesis is GO for exactly one bounded development diagnostic because a ~1% prior signal is materially larger than the ~0.081% raw break-even against E007 and the production feature-map cost is only `O(n)` per layer.
