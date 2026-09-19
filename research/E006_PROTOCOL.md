# E006 — Gram-preserving radial fourth-moment rotation

## Administrative re-key

This experiment was originally claimed and measured as a competing E003 in Issue #8 / PR #13. While its preregistered Phase-2 `mini` grid was running, the canonical E003 from Issue #10 / PR #12 completed and was integrated into `research/bootstrap`. The E003 protocol requires a new ID for any materially different radial/kurtosis rule, so the already-frozen pairwise Gram-preserving rotation is recorded as **E006**.

This re-key does not change the hypothesis, estimator implementation, hyperparameters, seed policy, dataset/split, scorer run, decision threshold, measured result, or decision. The scorer is not rerun during E006 integration.

## Hypothesis

The whitened-antithetic sampler exactly matches the input mean and covariance, but whitening suppresses part of the finite-ensemble radial variation. A cheap adaptive row-space rotation can increase fourth-moment/radial spread while leaving the sample Gram matrix unchanged. If deep ReLU sampling error is materially sensitive to that fourth-moment deficit, a partially radial-spread ensemble should reduce final-layer MSE at essentially unchanged measured compute.

## Frozen baseline and gate

Reproduced whitened-antithetic Phase-2 `mini` baseline:

- final-layer MSE: `7.39e-06`
- adjusted final-layer score: `7.39e-07`
- all-layers MSE: `1.03e-05`
- mean compute utilization: `0.09897964`
- failures: `0/100`
- target utilization: `0.099`

Preregistered development gate: `final_layer_mse <= 6.651e-06`, i.e. at least a 10% improvement over `7.39e-06`, with comparable utilization and no material reliability regression. Holdout access was forbidden unless this gate passed.

## Frozen estimator change

For each consecutive pair `(a, b)` in the positive half of the antithetic ensemble, form its 2x2 row Gram block. Compute the orthogonal rotation that diagonalizes that block, maximizing the pair's row-norm separation while preserving the pair contribution to the full sample Gram matrix. Interpolate from the identity to that rotation by a frozen strength `lambda`, then renormalize the `(cos, sin)` pair onto the unit circle.

The transformed positive half is concatenated with its exact negative. Therefore the empirical mean and odd moments remain antithetically zero, the sample Gram matrix is preserved by the pairwise orthogonal rotations, and the existing whitening step retains its covariance contract. The change targets fourth and higher sample moments only.

Frozen grid, with no seed sweep:

- `lambda=0.25`
- `lambda=0.50`
- `lambda=0.75`

Per-MLP randomness remains `mlp.seed`.

## Frozen measurement

One-shot GitHub Actions run `34706339487` used experiment commit `a1a8cd593ca02090fb08a02a3a4e3d1f3f413f4e` on `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`, `runner=local`, 100 MLPs, width 1024, depth 16 and FLOP budget about `2.20e12` per MLP. Environment: Python 3.11.16, NumPy 2.4.6, whestbench 0.16.1, flopscope 0.12.1.

| lambda | final-layer MSE | adjusted score | all-layers MSE | mean utilization | total estimator FLOPs | failures | artifact |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.25 | `7.36e-06` | `7.36e-07` | `1.03e-05` | `0.09899029` | `2.18e13` | `0/100` | `10301906850` |
| 0.50 | `7.45e-06` | `7.45e-07` | `1.04e-05` | `0.09899029` | `2.18e13` | `0/100` | `10302006731` |
| 0.75 | `7.53e-06` | `7.53e-07` | `1.04e-05` | `0.09899029` | `2.18e13` | `0/100` | `10302251505` |

Best candidate: `lambda=0.25`, MSE `7.36e-06`, approximately 0.41% lower than the `7.39e-06` frozen baseline. This is far below the preregistered 10% gate.

## Decision

**DROP.**

The development gate failed. Holdout was not accessed; there was no seed sweep, replication, or post-result tuning. External experiment cost was `$0`.

## Integration record

The frozen implementation is restored from closed PR #13 head `1dd38bb984629819ccb7e86cc95232dcff270fdb`; the measurement provenance remains the frozen scorer commit `a1a8cd593ca02090fb08a02a3a4e3d1f3f413f4e`. E006 integration is administrative only: normal lint/tests/estimator-contract CI is allowed, but the scorer must not be rerun and no scoring workflow is restored.
