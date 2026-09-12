# E001 Residual Control-Variate Development Protocol

Status: completed — DROP.

## Objective

Test whether a covariance-centered control-variate residual estimated from
whitened-antithetic trajectories improves final-layer MSE by at least 15% at
comparable adjusted compute.

## Fixed environment

- Dataset: `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`
- Development split: `mini`
- Width/depth: 1024 / 16
- Per-MLP FLOP budget: `2**41`
- Seed policy: use the grader-provided `mlp.seed`; no seed sweep
- Holdout: not accessed during this development screen

## Baselines

The promotion comparison is against the strongest reproducible development
baseline available before candidate scoring:

1. E000 official covariance propagation: final-layer MSE `4.05e-06`, mean
   utilization `0.02351464`, failures `0/100`.
2. Frozen whitened-antithetic sampler: `target_utilization=0.099`, exactly
   5708 trajectories at the competition shape. Phase-2 mini run `34693987776`
   measured final-layer MSE `7.39e-06`, adjusted final-layer score `7.39e-07`,
   all-layers MSE `1.03e-05`, mean utilization `0.09897964`, failures `0/100`.

The sampler is therefore weaker than E000 on this development split. The E001
promotion comparison remains E000, and the preregistered >=15% improvement gate
corresponds to final-layer MSE <= `3.4425e-06`.

## Candidate definition

`methods/residual_control_variate.py` computes the official covariance branch,
then uses whitened-antithetic trajectories to form per-layer control-adjusted
sample means:

`cv = sample_relu_mean - gain * (sample_pre_mean - deterministic_pre_mean)`

The returned estimate is:

`deterministic_mean + residual_weight * (cv - deterministic_mean)`

The Gaussian ReLU gain is `Phi(alpha)` from the deterministic covariance
propagation state.

Sampling parameters were fixed for every candidate:

- `target_sampling_utilization=0.075`
- `min_samples=512`
- `max_samples=400000`
- competition-shape sample count: 4230 trajectories
- estimated sampler utilization: `0.07498941`
- E000 covariance utilization plus estimated sampler utilization:
  `0.09850405` before the small control-vector overhead

## Preregistered grid

Every setting was run exactly once on the development split:

- `residual_weight=0.5`
- `residual_weight=1.0`
- `residual_weight=1.5`

No additional coefficient was added after observing scores. The grid ran as
GitHub Actions run `34699262095` from commit
`8b641586afc9418870fb12071de0dd0e9de42b06`.

## Development results

| residual_weight | final-layer MSE | adjusted score | all-layers MSE | mean utilization | failures |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.5 | `4.00e-06` | `4.00e-07` | `2.83e-06` | `0.09854008` | `0/100` |
| 1.0 | `4.42e-06` | `4.42e-07` | `5.29e-06` | `0.09854008` | `0/100` |
| 1.5 | `5.31e-06` | `5.31e-07` | `9.59e-06` | `0.09854008` | `0/100` |

The best candidate was `residual_weight=0.5`. Against the E000 development
baseline (`4.05e-06`), its rounded MSE improvement is approximately `1.23%`.
This is far below the preregistered `15%` gate and above the required
`3.4425e-06` maximum MSE.

The coefficient trend is also adverse after `0.5`: increasing residual weight
to `1.0` and `1.5` progressively worsened both final-layer and all-layer MSE.
This is a measured negative result for this fixed linear residual correction,
not evidence that every possible control-variate construction must fail.

## Decision

`DROP` E001.

- Development gate failed.
- Measured utilization remained below 10% for every grid point.
- No failures occurred.
- Holdout was not accessed.
- Replication budget was not consumed.
- External experiment cost recorded in the ledger is `$0`.

Any follow-up coefficient search or materially changed residual estimator must
use a new experiment ID rather than modifying E001 after observing this grid.
