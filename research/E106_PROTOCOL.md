# E106 — cross-fitted quartic spherical control variate on E104 Haar blocks

Idempotency key: `ARC-E106-CROSSFIT-QUARTIC-HAAR-CV-20260919`

Status: protocol-first; no implementation or scientific measurement at this commit.

## Provenance

- Branch: `research/e106-crossfit-quartic-haar-cv-20260919`
- Direct canonical parent: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Parent evidence: E104 production law + E105 terminal risk certificate.
- E105 measured target-free raw stochastic risk `8.604586912926751e-06` at utilization
  `0.06780944702768466`, so sample-count scaling cannot close the raw target within
  `util<=0.14`.

## Candidate

Keep the E104 analytic-radius, antithetic, two-independent-Haar-block law unchanged.
Add an unbiased angular control variate built from degree-4 spherical harmonics.

For a unit direction `q` and frozen unit vector `u`,

`z_u(q) = (q^T u)^4 - 3/(n(n+2))`

has exact spherical expectation zero.

Freeze `K=256` directions `u_k` as the normalized first 256 first-layer weight rows.
No feature/rank sweep.

For each network layer, define paired antithetic responses within each Haar block,

`g(q) = (H(r q) + H(-r q))/2`, with `r=E[chi_n]`.

Use block 1 only to fit 256 independent scalar regression coefficients for every output
coordinate, and apply those coefficients only to block 2. Symmetrically fit on block 2 and
apply only to block 1. The two corrected block estimates are averaged.

Because each fitted coefficient is measurable with respect to the *other* independent Haar
block and every `z_u` has known expectation zero, the symmetric cross-fit estimator is
unbiased without holdout targets or fitted benchmark coefficients.

Frozen coefficient rule for training block `b`:

- center each feature column by its block sample mean;
- center each output coordinate by the block response mean;
- `beta[k,j] = sum_i zc[i,k] yc[i,j] / sum_i zc[i,k]^2`;
- no ridge, clipping, shrinkage, fallback, feature dropping, alternate basis, or tuning.

## Production shape

- width: 1024
- depth: 16
- estimator trajectories: 4096
- exactly two Haar blocks + antipodes per estimator
- analytic `E[chi_1024]` radius
- feature count: 256
- feature directions: normalized rows `weights[0][:256]`
- budget: `2**41`
- all Gaussian sampling and all candidate numerical transforms under flopscope.

## Frozen diagnostic

Use two independent estimator realizations to measure target-free stochastic MSE:

- weight seed: `104104` (same frozen synthetic production network)
- estimator A direction seed: `106105`
- estimator B direction seed: `106106`

For candidate predictions `M_A, M_B`,

`Rhat_candidate = mean((M_A[-1]-M_B[-1])^2)/2`

is an unbiased target-free estimator of the final-layer coordinate variance/MSE from
estimator randomness. Compute the same paired risk for the uncorrected E104 block averages
from the exact same four Haar blocks.

Repeat the entire A/B diagnostic once with identical seeds only for deterministic replay.
This is one workflow run and one frozen scientific diagnostic; no workflow rerun.

## Gates

All must pass for GO:

1. candidate target-free raw-MSE risk `<=1.89e-8`;
2. candidate adjusted-risk proxy `<2.5e-9`;
3. measured per-estimator utilization `<=0.14`;
4. candidate raw risk < baseline raw risk on the same four blocks;
5. finite outputs and coefficients;
6. exact antithetic pairs;
7. exact accounting reconciliation;
8. deterministic candidate predictions/risk/FLOP ledgers;
9. no public/public-mini/scorer/holdout/full/benchmark targets.

Any failed/unevaluable gate => terminal NO-GO / DROP E106. No rescue, rerun, rank/feature
sweep, tuning, or coefficient alteration under E106.

## Execution discipline

Protocol-only first commit, focused RED, frozen implementation, GREEN + exactly one bounded
diagnostic. No canonical or ledger mutation and no official scorer.
