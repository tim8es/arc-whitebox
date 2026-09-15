# E019 — Final-layer univariate saddlepoint closure

Idempotency key: `ARC-E019-IMPLEMENT-20250915`

## Branch and ancestry

- Branch: `research/e019-final-saddlepoint-20250915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Exact V25 ancestor repository: `504aldo/whest-p2-cumulant-k3`
- Exact V25 ancestor commit: `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- Exact V25 blob: `estimators/estimator_v25.py` @ `195373a110215256b759d7c172ba8c923c62e5cc`

The diagnostic must verify the fetched file's Git blob identity before use. No canonical mutation is allowed.

## Scientific question

Does replacing only V25's **final-layer univariate mean closure**, while holding the entire upstream V25 propagated state fixed, reduce public-mini final-layer error enough to improve projected adjusted score?

This is a teacher-state bounded diagnostic. It is not a production estimator integration and it must not change any earlier-layer propagation, source machinery, lambda law, or state update.

## Frozen teacher state

At the final preactivation of exact V25, capture for every neuron:

- `kappa1 = mu`
- `kappa2 = var`
- `kappa3 = D3`
- `kappa4 = g4row`

These are the same quantities consumed by the exact V25 final univariate nonlinear program. The exact V25 emitted final row is the baseline prediction. The candidate is evaluated from the same captured state.

Dataset: `aicrowd/arc-whestbench-public-2026`, revision `v2-phase2`, split `mini`.

- Smoke-only dumps: `0,1,2,3`
- Single validation set: `4,5,6,7`

There is no fit, refit, per-MLP parameter, learned constant, hyperparameter search, or subset search.

## Frozen saddlepoint closure

For each neuron, let `sigma = sqrt(kappa2)` and standardize:

- `c3 = kappa3 / sigma^3`
- `c4 = kappa4 / sigma^4`

Use the fourth-order standardized CGF

`K(t) = t^2/2 + c3 t^3/6 + c4 t^4/24`.

Thus

- `K'(t) = t + c3 t^2/2 + c4 t^3/6`
- `K''(t) = 1 + c3 t + c4 t^2/2`.

Quadrature is fixed to exactly 32-point Gauss-Legendre on `[-8, 8]`.

At every quadrature node `x`, initialize `t0 = x` and perform **exactly six** Newton iterations:

`t <- t - (K'(t) - x) / K''(t)`.

Forbidden: damping, clipping, bracket search, alternate initializer, learned constants, fallback, retry, adaptive iteration count, or sweep.

The saddlepoint density approximation is

`f_sp(x) = exp(K(t) - t*x) / sqrt(2*pi*K''(t))`.

The candidate ReLU mean uses an exact Gaussian control term plus the fixed quadrature correction:

`m_sp = m_gauss + integral_{-8}^{8} relu(kappa1 + sigma*x) * (f_sp(x) - phi(x)) dx`,

where

`m_gauss = sigma*phi(kappa1/sigma) + kappa1*Phi(kappa1/sigma)`.

The integral is evaluated only by the fixed GL32 nodes/weights. The analytic Gaussian term is part of the frozen formula, not a fallback. In the Gaussian limit `c3=c4=0`, the correction vanishes identically.

## Numerical diagnostics

Normalized Newton residual is frozen as

`abs(K'(t)-x) / (1 + abs(x))`.

Report the maximum over all neurons and all 32 nodes.

For every smoke and validation dump report:

- exact V25 baseline final MSE
- saddlepoint candidate final MSE
- candidate/baseline MSE ratio
- finite-state flag
- minimum observed `K''`
- maximum normalized Newton residual

Also report the global Gaussian-limit error from deterministic synthetic states with `kappa3=kappa4=0` as maximum absolute error versus the analytic Gaussian ReLU mean.

## Production-cost proxy

Measure only the final-layer saddlepoint closure algebra at width 1024 using `flopscope.numpy`, with the same GL32 nodes and exactly six Newton iterations. Use one warmup and seven measured repetitions; report median residual wall time.

Projection anchor:

- `B = 2^41`
- E007 raw final-layer MSE = `2.23e-8`
- E007 utilization = `0.36666448`

Compute:

- `projected_util = 0.36666448 + extra_flops / B`
- `validation_ratio = mean(candidate MSE on 4..7) / mean(baseline MSE on 4..7)`
- `projected_raw = 2.23e-8 * validation_ratio`
- `projected_adjusted = projected_raw * projected_util`

## Frozen gates

All gates must pass:

1. Gaussian-limit max absolute error `<= 1e-6`.
2. Every observed `K''` is finite and strictly positive.
3. Maximum normalized Newton residual `<= 1e-5`.
4. Validation aggregate MSE ratio `<= 0.99`.
5. No validation dump has MSE ratio `> 1.02`.
6. Projected utilization `<= 0.3670`.
7. Median residual-time proxy `<= 0.005 s`.
8. Projected adjusted score `<= 8.11e-09`.

Any failed gate => `NO-GO / DROP E019`.

## Execution constraints

- Focused tests must follow RED -> GREEN.
- Run one smoke pass on dumps 0..3 and one validation pass on 4..7.
- No scorer.
- No holdout.
- No tuning, sweep, damping, clipping, learned constants, fallback, rescue, second validation, or protocol mutation after measurement starts.
- No canonical mutation.
