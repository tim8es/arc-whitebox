# E003 Radial Marginalisation Development Protocol

Status: in progress.

## Objective

Test whether exact Gaussian radial marginalisation on top of the frozen
whitened-antithetic sampler improves Phase-2 mini final-layer MSE by at least
10% at comparable adjusted compute.

## Claim

E003 was claimed in Issue #10 after checking the current ledger, open Issues,
open PRs, and branch names. E002 was already occupied by Issue #6 / PR #7, and
no E003 issue, PR, or branch existed before the claim.

## Fixed environment

- Dataset: `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`
- Development split: `mini`
- Width/depth: 1024 / 16
- Per-MLP FLOP budget: `2**41`
- Seed policy: use the grader-provided `mlp.seed`; no seed sweep
- Holdout: not accessed during this development screen

## Baseline

Frozen `methods/whitened_antithetic.py` at `target_utilization=0.099`:

- competition-shape sample count: 5708 trajectories
- Phase-2 mini final-layer MSE: `7.39e-06`
- adjusted final-layer score: `7.39e-07`
- all-layers MSE: `1.03e-05`
- mean utilization: `0.09897964`
- failures: `0/100`

The E003 promotion threshold is therefore final-layer MSE <= `6.651e-06`.

## Frozen candidate

`methods/radial_marginalized_antithetic.py` keeps the baseline antithetic
pairing and covariance whitening. For the whitened ensemble `x_tilde`, it uses
positive homogeneity of a bias-free ReLU MLP to integrate the Gaussian radius
analytically with a per-sample weight

`w_s = E[chi_width] / ||x_tilde_s||`.

The same antithetic-symmetric weight is applied to every layer contribution.
Whitened norms are recovered from the positive half using
`x_half @ (U * lambda**-0.5)`; the right orthogonal factor is unnecessary for
norms.

No coefficient or radial-rule grid is allowed inside E003. Any materially
different radial/kurtosis correction requires a new experiment ID.

## Cost model

The candidate retains the baseline fixed whitening cost and adds, per full
sample:

- `width**2` FLOPs for the half-sample whitened-norm matmul;
- `depth * width` FLOPs for weighted layer reductions;
- `4 * width` FLOPs of conservative radial-norm slack.

At the competition shape and `target_utilization=0.099`, the frozen candidate
uses 5542 trajectories versus the baseline's 5708.

## Decision rule

KEEP only if all conditions hold on the development run:

- final-layer MSE improves by at least 10% versus `7.39e-06`;
- adjusted compute remains comparable and near/below the 10% score floor;
- no material failure regression.

Otherwise DROP. A failed development gate means no holdout run and no
replication-budget spend.

## Prior evidence

Public Phase-1 work reported exact radial marginalisation as positive but small
(~1.013x against whitened-antithetic sampling) and left it disabled because the
gain did not pay for its extra norm pass. E003 tests whether Phase 2's width
1024 / depth 16 regime changes that conclusion.
