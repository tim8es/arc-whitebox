# E033 — diagonal four-cumulant Edgeworth carrier

Idempotency key: `ARC-FOLLOW-RESEARCH-20260915`

Status: preregistered single frozen local diagnostic.

## Provenance and firewall

- Branch: `research/e033-diagonal-edgeworth-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Dataset: public Phase-2 mini, index **0 only**.
- E023/E024/E026/E027/E029/E032 are terminal and immutable. E028 remains reviewed local GO and is not modified. E030/E031 are disjoint/occupied and are not used.
- No official scorer, holdout, second mini index, fitting, tuning, sweep, or post-result rescue is permitted under E033.

## Hypothesis

The source-tensor cost of K3 propagation may be unnecessary if the part of finite-width non-Gaussianity that matters to the mean is predominantly coordinatewise. E033 therefore carries exactly four scalar moments per neuron and discards all cross-neuron cumulant state.

At each layer the state is `(mu, var, k3, k4)`, where `k3` and `k4` are the third and connected fourth central cumulants of each neuron.

For a linear map under the frozen coordinate-independence closure:

- `mu_pre = W @ mu`
- `var_pre = (W**2) @ var`
- `k3_pre = (W**3) @ k3`
- `k4_pre = (W**4) @ k4`

The ReLU update is a frozen univariate Edgeworth quadrature. Standardize with `z=(x-mu)/sigma`; use the density multiplier

`1 + gamma1 H3(z)/6 + gamma2 H4(z)/24 + gamma1^2 H6(z)/72`,

where `gamma1=k3/sigma^3` and `gamma2=k4/sigma^4`. Integrate ReLU raw moments 1..4 using exactly the embedded 16-node standard-normal Gauss-Hermite rule, then convert them back to `(mu,var,k3,k4)`.

The Edgeworth quadrature weights are allowed to be signed; there is no clipping, damping, learned coefficient, source tensor, covariance state, rank selection, layer-specific parameter, or output calibration. The sole numerical guard is `var_pre >= 1e-12` before a square root.

## Quantitative path

The estimator performs four dense `n x n` matrix-vector contractions per layer plus O(16 n) scalar-quadrature work. At `n=1024`, `L=16`, this is O(`1.4e8`) billed arithmetic before elementwise power construction, orders of magnitude below `0.14 * 2^41`.

The frozen win target is deliberately strict:

- final-layer raw MSE `<= 1.89e-08`;
- utilization `<= 0.14`;
- adjusted proxy `raw * max(0.1, utilization) < 2.5e-09`.

Because utilization is expected below the 0.1 score floor, the effective raw requirement for the adjusted gate is `<2.5e-08`; the separate `1.89e-08` raw gate remains mandatory.

## Focused tests before scientific data

Tests must establish on synthetic inputs:

1. the embedded 16-node normal rule has total weight 1, zero odd first moment, and unit second moment to `1e-12`;
2. the linear cumulant transport is exact for independent synthetic scalar variables at the algebraic level;
3. with `gamma1=gamma2=0`, the Edgeworth multiplier is identically one and the ReLU update is finite/positive;
4. central-moment conversion returns finite nonnegative variance and deterministic output;
5. no state larger than O(n) persists between layers.

Focused tests must be GREEN before the scientific harness is armed.

## Single frozen local diagnostic

Run E033 exactly once on public mini index 0 under `flopscope.BudgetContext` with fixed thread/hash settings. Record:

- final-layer MSE against baked `final_means`;
- billed FLOPs and utilization;
- adjusted proxy;
- residual and wall time;
- maximum absolute standardized skew/kurtosis seen during propagation;
- finite status;
- deterministic repeat max-abs difference.

## Frozen gates

All must pass:

1. final-layer raw MSE `<= 1.89e-08`;
2. utilization `<= 0.14`;
3. adjusted proxy `< 2.5e-09`;
4. residual `< 0.400 s`;
5. finite output and finite moment state;
6. deterministic repeat max-abs difference `== 0`;
7. exactly four O(n) persistent moment vectors and the frozen 16-node rule;
8. no MLP-dependent arithmetic outside flopscope operations in the estimator path.

Any failed or unevaluable gate => **NO-GO / DROP E033**. There is no alternate node count, variance floor, clipping, damping, coefficient change, second index, or rerun under E033. A new idea requires E034+.
