# E003 Fourth-Moment Constrained Antithetic Sampling Protocol

Status: development candidate frozen before first E003 score.

## Objective

Test whether a parameter-free radial correction to the frozen whitened-antithetic sampler reduces deep-layer sampling error at comparable measured FLOPs.

## Fixed environment

- Dataset: `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`
- Development split: `mini`
- Width/depth: 1024 / 16
- Per-MLP FLOP budget: `2**41`
- Seed policy: grader-provided `mlp.seed`; no seed sweep
- Holdout: untouched unless the development gate passes
- External experiment budget gate: `$6`

## Frozen baseline

`methods/whitened_antithetic.py` with its default target utilization `0.099`.
The existing ledger result is the reference development score:

- final-layer MSE: `7.39e-06`
- mean compute utilization: `0.09897964`

The experiment must also rerun the frozen baseline in the same workflow so environment drift is visible.

## Frozen E003 candidate

`methods/fourth_moment_antithetic.py` uses exactly one parameter-free correction:

1. Draw the same antithetic Gaussian pairs as the frozen sampler.
2. Whiten once so the empirical covariance is identity.
3. For each positive/negative pair, restore the radius implied by its original Gaussian draw.
4. Apply one global normalization so empirical `E[r^2] = width`.
5. Re-whiten once to restore exact empirical covariance identity.
6. Propagate the corrected samples through the MLP exactly as in the frozen sampler.

No coefficient, clipping threshold, seed search, feature selection, or post-result adjustment is allowed inside E003.

## Compute accounting

The candidate keeps target utilization at `0.099` but includes the second eigendecomposition/whitening and radial operations in its sample-count estimate.
At competition shape the frozen implementation computes `4810` trajectories. The earlier `4796` written before the first CI run was an arithmetic transcription error in the protocol/test expectation; CI run `34706298260` exposed the mismatch before any scorer step, and only this bookkeeping value was corrected. The estimator implementation and scientific candidate were unchanged.
Promotion decisions use the scorer's measured utilization, not this estimate.

## Development gate

Run exactly once on Phase-2 `mini` after contract/tests pass. Record:

- final-layer MSE
- all-layer MSE
- adjusted final-layer score
- mean compute utilization
- failures
- candidate sample count
- exact command and workflow/commit identifiers

Relative improvement is `(baseline_mse - candidate_mse) / baseline_mse` using the baseline rerun from the same workflow.

E003 passes development only if:

- final-layer MSE improves by at least `10%`;
- measured utilization is comparable and remains near the <=10% score-floor target;
- there is no material failure regression.

If the development gate fails, mark E003 `DONE/DROP` and do not access holdout. A positive development signal permits a separately preregistered one-shot holdout; any candidate change after observing this run requires a new experiment ID.
