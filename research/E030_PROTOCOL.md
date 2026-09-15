# E030 — rank-8 conditional-Gaussian latent carrier

Idempotency key: `ARC-WIN-RESEARCH-20260915`

Status: preregistered; protocol-only first commit.

## Provenance

- Branch: `research/e030-r8-conditional-gaussian-carrier-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Phase-2 public mini: `aicrowd/arc-whestbench-public-2026@v2-phase2`
- Frozen diagnostic index: `0` only
- Width/depth: `1024 x 16`
- Budget `B = 2**41 = 2,199,023,255,552`
- Target adjusted score: `<2.5e-09`

E029 is closed NO-GO. E030 does not reuse E029 angular support or signed weights and does not use K3/K4 cumulant machinery.

## Motivation / method class

Public Phase-2 evidence says Gaussian marginal closure is insufficient, while current high-accuracy cumulant methods spend most of their compute carrying dependence information. E030 tests a different representation: retain dependence as a **low-rank latent Gaussian carrier plus exact diagonal residual**, then integrate the ReLU nonlinearity conditionally.

State after each ReLU is

`h ~= mu + U xi + eps`,

where `xi ~ N(0,I_8)`, `eps ~ N(0,diag(d))`, and `U` is `n x 8`. Marginal mean and variance are carried exactly under the Gaussian state; cross-neuron dependence is represented only by the rank-8 latent factor.

## Frozen rank and covariance carrier

`R = 8` throughout. No rank sweep or oversampling.

Given state `(mu,d,U)` and weight matrix `W`, preactivation mean is

`m = W mu`.

The represented covariance is

`C = W diag(d) W^T + (W U)(W U)^T`.

Its diagonal is computed exactly from the represented state. Its rank-8 correlated carrier is the one-shot Nyström approximation using the first eight coordinate probes `Omega = I[:, :8]`:

`Y = C Omega`, `G = Omega^T Y`,

`U_pre = Y G^(-1/2)`

using the ordinary symmetric eigendecomposition of the `8 x 8` Gram matrix. No power iteration, oversampling, jitter, clipping, pseudoinverse, alternate probes, or fallback is allowed. Non-positive/nonfinite Gram eigenvalues are immediate NO-GO.

The diagonal residual is

`d_pre = diag(C) - rowsum(U_pre**2)`.

Any materially negative residual (`min(d_pre) < -1e-6`) is immediate NO-GO. No clipping rescue is permitted.

Input state is exactly `(mu=0, d=1, U=0)`.

## Frozen conditional ReLU closure

For each preactivation marginal `N(m_i, v_i)` with `v_i = d_pre_i + ||U_pre[i]||^2`, compute the exact Gaussian ReLU marginal mean and second moment analytically.

To carry dependence through ReLU, integrate only over the eight latent variables with the fixed spherical-radial cubature

`xi in {+sqrt(8)e_j, -sqrt(8)e_j}`, `j=1..8`, equal weight `1/16`.

At each of the 16 latent nodes, integrate the independent diagonal noise `eps_i ~ N(0,d_pre_i)` analytically to obtain conditional ReLU means. The covariance of those 16 conditional-mean vectors is compressed to rank 8 by an exact eigendecomposition of their `16 x 16` Gram matrix. The post-ReLU diagonal residual is the exact marginal Gaussian ReLU variance minus the retained rank-8 factor diagonal.

Any nonfinite value, non-positive required variance, or post-ReLU residual `< -1e-6` is an immediate NO-GO. No clipping/jitter/fallback.

## Quantitative path

The hot path is `O(L n^2 R)`: matrix-vector/skinny-matrix actions for the rank-8 carrier plus elementwise conditional ReLU formulas. With `L=16,n=1024,R=8`, the intended bill is comfortably below `0.105 B`, hence the score multiplier should remain at or near the `0.1` floor.

At multiplier `0.1`, adjusted `<2.5e-09` requires raw final-layer MSE `<2.5e-08`. The frozen local raw gate is `<=2.45e-08` for margin.

## Focused tests

Before scientific data, tests must verify:

1. Nyström factor reconstructs an exactly rank-8 PSD covariance when probed by a full-rank coordinate minor;
2. represented covariance diagonal is preserved by `diag + U U^T` bookkeeping;
3. conditional ReLU update agrees with exact univariate Gaussian ReLU means/variances on its marginals;
4. deterministic shape/rank invariants and no forbidden stabilization branches.

## Exactly one frozen local diagnostic

Run public mini index `0` once under flopscope, plus one identical repeat solely for determinism. Record:

- final-layer raw MSE;
- billed FLOPs/utilization and adjusted proxy;
- residual wall time;
- minimum pre/post diagonal residual seen;
- maximum marginal identity error;
- deterministic repeat max absolute difference;
- finite/scope status.

## Frozen GO gates

All must pass:

1. final-layer MSE `<= 2.45e-08`;
2. adjusted proxy `<2.5e-09`;
3. utilization `<=0.105`;
4. residual `<0.400 s`;
5. all required Gram eigenvalues finite and strictly positive;
6. minimum carried diagonal residual `>= -1e-6`;
7. marginal ReLU identity error `<=1e-5` relative;
8. finite outputs;
9. deterministic repeat max absolute difference `==0`;
10. exact frozen rank/probe/cubature scope, with no clipping, jitter, fallback, rank/probe change, or alternate closure.

Any failed or unevaluable gate => **NO-GO / DROP E030**. No rescue or rerun under E030.

## Execution budget

Protocol-only first commit, focused RED/GREEN tests, exactly one scientific diagnostic. No official scorer, holdout, tuning, sweep, second mini index, or canonical mutation.