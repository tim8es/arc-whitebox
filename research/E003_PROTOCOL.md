# E003 preregistration — radial fourth-moment correction

## Hypothesis

The whitened-antithetic sampler exactly matches the input mean and covariance, but whitening also suppresses finite-ensemble radial variation. A cheap adaptive row-space rotation can restore part of that higher-moment variation while leaving the sample Gram matrix exactly unchanged. If deep ReLU sampling error is sensitive to this fourth-moment deficit, a partially radial-spread ensemble should reduce final-layer MSE at essentially the same measured compute.

## Baseline

Frozen reproduced whitened-antithetic Phase-2 `mini` result from the E001 prerequisite:

- final-layer MSE: `7.39e-06`
- adjusted final-layer score: `7.39e-07`
- all-layers MSE: `1.03e-05`
- mean compute utilization: `0.09897964`
- failures: `0/100`
- target utilization: `0.099`

The E003 development gate is therefore `final_layer_mse <= 6.651e-06` (10% better than `7.39e-06`).

## Frozen correction

For each consecutive pair `(a, b)` in the positive half of the antithetic input ensemble, form the 2x2 row Gram block. Compute the orthogonal rotation that diagonalizes that block, which maximizes the pair's row-norm separation while preserving `a^T a + b^T b` as a matrix. Interpolate from identity to that rotation by a frozen strength `lambda`, then normalize the interpolated `(cos, sin)` pair back onto the unit circle.

The same transformed positive half is concatenated with its exact negative. Therefore:

- empirical mean remains exactly zero;
- every odd input moment remains exactly zero under the antithetic pairing;
- the full sample Gram matrix is exactly unchanged by the pairwise orthogonal rotations;
- the existing whitening step therefore still makes the empirical covariance exactly identity (up to numerical precision);
- only fourth and higher sample moments are changed.

No seed sweep is allowed. Per-MLP randomness remains `mlp.seed`, identical to the sampler baseline.

## Preregistered development grid

Run exactly once on Phase-2 `mini` with the official scorer and `runner=local`:

- `lambda=0.25`
- `lambda=0.50`
- `lambda=0.75`

All candidates retain sampler `target_utilization=0.099`. The extra pairwise norm/dot/rotation work is O(k * width), far below the O(k * width^2 * depth) propagation cost, but measured utilization is authoritative.

## Decision rule

Development KEEP signal requires all of:

1. best frozen candidate final-layer MSE `<= 6.651e-06`;
2. measured utilization remains comparable to the baseline and does not materially exceed the 10% score floor;
3. failures remain `0/100` (or no material regression if the scorer reports an infrastructure-only failure).

If the development gate fails, E003 is `DROP` and the holdout is not accessed. If it passes, freeze the winning `lambda` before a single holdout evaluation. Any parameter change after observing holdout creates a new experiment ID.

## Budget

External experiment budget gate: `$6` maximum. GitHub-hosted/local project evaluation is recorded as `$0` external experiment cost unless an external paid service is explicitly used.
