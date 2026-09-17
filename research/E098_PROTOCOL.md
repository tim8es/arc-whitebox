# E098 — late-onset rank-8 K22 Edgeworth response feasibility

Idempotency key: `ARC-E098-LATE-K22-EDGEWORTH-20260918`

Status: **PRE-PUBLIC / SYNTHETIC NECESSARY-CONDITION TEST ONLY**.

## Motivation

E097 closed the hypothesis that rank-8 K22 memory is uniformly adequate across *all* layers, but its frozen evidence showed a strong depth trend: rank-8 captured-energy rose from roughly 0.35–0.36 at the first layer to 0.83–0.91 at the deepest measured layer, and the final-three-layer worst energy was 0.7961154095. E097 explicitly left a new late-onset K22 mechanism as a distinct successor class.

E098 does not revive E097. It asks a narrower necessary question: once K22 has entered the late low-effective-rank regime, does its off-diagonal pair-cumulant slice induce a useful, stable, target-free correction to the next ReLU mean, and does rank 8 preserve that effect?

## Frozen mechanism

For source activations H with empirical mean mu, covariance C, and off-diagonal pair fourth-cumulant slice

`K22[i,j] = cum(h_i,h_i,h_j,h_j)`, diagonal forced to zero,

and next-layer row weight w, define the pair-only fourth-cumulant contribution

`kappa4_pair(w) = 3 * (w^2)^T K22 (w^2)`.

For a Gaussian baseline preactivation with mean m and variance s2, let
`sigma=sqrt(s2)`, `a=-m/sigma`, and `phi(a)=exp(-a^2/2)/sqrt(2*pi)`.

The fixed first-order fourth-cumulant Edgeworth correction to `E[ReLU(Y)]` is

`delta = kappa4_pair * phi(a) * (a^2 - 1) / (24 * sigma^3)`.

No coefficient is fit and no gain/shrinkage/tuning is allowed.

Two responses are evaluated:
1. **full-K22 response** using the full empirical off-diagonal K22;
2. **rank-8 response** using the optimal symmetric rank-8 approximation from the eight largest-absolute eigenpairs.

The Gaussian baseline uses the *same empirical source* mu and C and the exact next-layer weight matrix. This isolates whether the K22 response itself adds predictive information.

## Frozen Stage-A corpus

Exactly two new synthetic networks, never used by E097:

- width n=128
- depth L=7
- He weights iid Normal(0, sqrt(2/n)), float32
- weight seeds 98098 and 98198
- input seeds 198098 and 198198
- N=32768 iid N(0,I) input samples per network
- NumPy PCG64 only
- no benchmark/challenge/public data.

Evaluate exactly three late transitions per network:
source post-ReLU layers 3,4,5 -> target post-ReLU layers 4,5,6 (0-based).

For every evaluated transition, materialize source empirical mu/C/K22 from the same Monte-Carlo sample cloud, construct Gaussian/full-K22/rank-8 next-layer mean predictions, and compare all three to the empirical target-layer coordinate mean.

## Frozen metrics

Per transition record:

- source rank-8 K22 captured energy and relative Frobenius error;
- Gaussian baseline MSE to empirical target mean;
- full-K22 corrected MSE and ratio vs Gaussian;
- rank-8 corrected MSE and ratio vs Gaussian;
- rank-8 response-vs-full-response relative L2 error;
- max absolute correction, min sigma, finite state.

Aggregate across all six transitions:

- aggregate Gaussian, full-K22, and rank-8 MSE;
- aggregate rank-8 / Gaussian MSE ratio;
- worst per-transition rank-8 / Gaussian ratio;
- number of transitions where rank-8 improves Gaussian;
- median response-preservation relative error;
- deterministic replay max absolute scalar-metric delta.

## Frozen GO gates

All must pass:

1. all six transitions finite;
2. all six source K22 observations satisfy signal eligibility
   `||K22_off||_F / max(||C||_F^2,1e-30) >= 1e-5`;
3. median rank-8 captured K22 energy over the six source layers >= 0.80;
4. median rank-8 response-vs-full-response relative L2 error <= 0.20;
5. aggregate rank-8 corrected MSE <= 0.95 * aggregate Gaussian MSE;
6. at least 4/6 transitions improve Gaussian;
7. worst per-transition rank-8 / Gaussian MSE ratio <= 1.25;
8. deterministic replay scalar metrics agree to <=1e-12 absolute;
9. conservative production arithmetic bound for a late-onset rank-8 K22 state plus response over at most 12 remaining width-1024 layers is <0.01 * 2^41 FLOPs.

Any failed gate => **terminal NO-GO / DROP E098**. No rank change, later birth layer, gain/shrinkage, seed/sample change, alternate Edgeworth formula, second synthetic family, rerun-as-rescue, or benchmark run under E098.

## Cost bound

For each remaining production layer, conservatively bill:

- two dense n x n by n x r factor transports: `4 n^2 r` scalar FLOPs;
- factor maintenance: `20 n r^2`;
- pair-response for n outputs using rank-r symmetric factors: `8 n^2 r`.

Use n=1024, r=8, and 12 remaining layers. This is a ceiling, not a measured production implementation cost.

## If Stage A passes

A later **new experiment ID** may test a deterministic late-onset K22 propagation rule inside an estimator. Stage-A GO does not authorize public/public-mini, official scorer, holdout/full, target fitting, tuning, merge, or canonical/ledger mutation.

## Non-duplication

- E097 persistent all-layer rank-8 K22 is terminal and unchanged.
- E033 diagonal Edgeworth discarded cross-neuron K22; E098 explicitly uses off-diagonal pair cumulants.
- E037 signed K3/K4 response used a different mechanism/state.
- E094 source-axis compression is a compute lane.
- E095 projected residual sampling is a stochastic estimator lane.
- E091/E092 are residual calibration lanes; E098 performs no target calibration.

