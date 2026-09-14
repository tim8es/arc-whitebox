# E003 Radial Marginalisation Development Protocol

Status: completed — DROP.

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
- Python: 3.11.16
- NumPy: 2.4.6
- whestbench: 0.16.1
- flopscope: 0.12.1

## Baseline

Frozen `methods/whitened_antithetic.py` at `target_utilization=0.099`:

- competition-shape sample count: 5708 trajectories
- Phase-2 mini final-layer MSE: `7.39e-06`
- adjusted final-layer score: `7.39e-07`
- all-layers MSE: `1.03e-05`
- mean utilization: `0.09897964`
- failures: `0/100`

The E003 promotion threshold was therefore final-layer MSE <= `6.651e-06`.

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

No coefficient or radial-rule grid was allowed inside E003. Any materially
different radial/kurtosis correction requires a new experiment ID.

## Cost model

The candidate retains the baseline fixed whitening cost and adds, per full
sample:

- `width**2` FLOPs for the half-sample whitened-norm matmul;
- `depth * width` FLOPs for weighted layer reductions;
- `4 * width` FLOPs of conservative radial-norm slack.

At the competition shape and `target_utilization=0.099`, the frozen candidate
uses 5542 trajectories versus the baseline's 5708.

## Preregistered decision rule

KEEP only if all conditions hold on the development run:

- final-layer MSE improves by at least 10% versus `7.39e-06`;
- adjusted compute remains comparable and near/below the 10% score floor;
- no material failure regression.

Otherwise DROP. A failed development gate means no holdout run and no
replication-budget spend.

## Development run

The frozen candidate was evaluated exactly once by GitHub Actions run
`34706304538` from commit
`58111872eddf9c510310f8f623a21f973587887d` with command:

`whest run --estimator methods/radial_marginalized_antithetic.py --dataset hf://aicrowd/arc-whestbench-public-2026@v2-phase2 --split mini --runner local`

Artifact: `e003-radial-log`, artifact ID `10300934998`.

| estimator | samples | final-layer MSE | adjusted score | all-layers MSE | mean utilization | failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| frozen whitened-antithetic baseline | 5708 | `7.39e-06` | `7.39e-07` | `1.03e-05` | `0.09897964` | `0/100` |
| E003 radial marginalisation | 5542 | `7.63e-06` | `7.63e-07` | `1.06e-05` | `0.09897092` | `0/100` |

The radial candidate is approximately `3.25%` worse in final-layer MSE than the
frozen baseline. The preregistered 10% gate required `<=6.651e-06`; the measured
`7.63e-06` is about `14.72%` above that threshold. Compute utilization is
essentially unchanged (absolute difference `-8.72e-06`) and failures remain
zero, so the negative result is attributable to estimator accuracy rather than
a compute-floor or reliability mismatch.

The scorer reported total estimator FLOPs `2.18e13`, effective compute
`2.18e13`, scorer duration `126.506847s`, and the timed command wall clock was
`13:32.27` including dataset preparation/generation. The run exited successfully.
Repository verification also passed: Ruff clean, `8 passed` in pytest, and the
estimator contract validated.

## Decision

`DROP` E003.

- Development gate failed.
- Holdout was not accessed.
- No post-score retuning or second development measurement was performed.
- Replication budget was not consumed.
- External experiment cost recorded in the ledger is `$0`.

Any different radial/kurtosis construction must receive a new experiment ID.
