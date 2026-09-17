# E100 — Haar-orthogonal Gaussian antithetic sampling

Idempotency key: `ARC-E100-ORTHOGONAL-GAUSSIAN-ANTITHETIC-20260918`

Status: **PRE-PUBLIC / SYNTHETIC VARIANCE-REDUCTION TEST ONLY**.

## Motivation

E095 established that ordinary antithetic trajectory averaging is substantially more accurate than hard projection of the same sampled residual, while remaining plausibly within the Phase-2 compute envelope. E100 changes the input sampling law across trajectories without changing any single trajectory's marginal law or discarding output components.

This is not E095 rescue: no output subspace, no projection, no fitted correction, no target-dependent selector.

## Frozen estimator

For input dimension n, generate positive samples in blocks of n.

For each block:

1. draw G in R^(n x n) with iid N(0,1);
2. QR factorize G=QR;
3. multiply each column of Q by sign(diag(R)) so Q is a deterministic Haar representative;
4. draw independent radii r_i with r_i^2 ~ chi-square(n);
5. set positive samples x_i = r_i * Q[i,:];
6. append their antithetic partners -x_i.

Each individual x_i is exactly marginal N(0,I), while samples within a positive block are orthogonal in direction. The sample mean estimator is therefore unbiased; only cross-sample dependence changes.

Comparator: ordinary iid antithetic Gaussian pairs with exactly the same trajectory count.

## Frozen Stage-A corpus

Use exactly eight independently seeded synthetic He-ReLU MLPs:

- width n=32
- depth L=6
- weight seeds 100000..100007
- high-sample reference: 65536 iid-antithetic trajectories
- candidate/comparator trajectories: 2048 total each
- candidate RNG seeds: 200000..200007
- comparator RNG seeds: 300000..300007
- reference RNG seeds: 400000..400007
- float32 forward propagation; float64 reductions
- NumPy PCG64
- no benchmark/public/scorer/holdout/full data.

Reference, comparator, and candidate seeds are disjoint.

Measure final-layer coordinate mean only.

## Frozen metrics

Per network:

- iid-antithetic MSE vs high-sample reference;
- orthogonal-antithetic MSE vs the same reference;
- orthogonal/iid MSE ratio;
- max absolute mean error for each estimator;
- deterministic replay equality;
- finite state.

Aggregate:

- MSE pooled over all 8 x 32 final coordinates;
- orthogonal/iid aggregate ratio;
- orthogonal wins among 8 networks;
- worst per-network ratio.

## Frozen GO gates

All must pass:

1. all outputs finite;
2. deterministic replay max absolute scalar-metric delta <= 1e-12;
3. aggregate orthogonal/iid MSE ratio <= 0.75;
4. orthogonal wins on >=6/8 networks;
5. worst per-network orthogonal/iid MSE ratio <=1.25;
6. conservative width-1024/depth-16/N=4096 production cost <=0.12 * 2^41 FLOPs, counting the full dense forward trajectories plus two square QR factorizations for the 2048 positive samples, chi-square/radial scaling, and output reduction.

Any failed gate => **terminal NO-GO / DROP E100**. No block-size change, scrambling, partial orthogonalization, sample-count change, seed change, radial coupling, blend with iid, rerun-as-rescue, or public run under E100.

## Conservative production cost model

For N=4096 total trajectories and n=1024:

- forward dense matmuls: `2 * N * depth * n^2` scalar multiply/add FLOPs;
- two square QR factorizations for 2048 positive samples, each billed as `(4/3) n^3`;
- radial scaling and reductions billed as `4 N n`.

No covariance/V29 state is included; this is a standalone unbiased sampling estimator.

## Non-duplication

- E095 projected residual sampling is terminal; E100 retains the full sample mean.
- E038 collided Sobol branch is non-authoritative and is not reused.
- E029 angular representation is a deterministic layer representation, not cross-trajectory Haar sampling.
- E091/E092 are fitted residual calibration lanes.
- E094 is source-axis deterministic compression.

