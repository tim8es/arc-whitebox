# E036 protocol — fourth-order Price covariance response + signed K3

Status: **PREREGISTERED**

Idempotency key: `ARC-KEEP-GOING-RESEARCH-20260915-E036`

## Base and firewall

- Fresh branch: `research/e036-price4-covariance-20260915`.
- Exact canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Public Phase-2 mini index `0` only for the one frozen scientific diagnostic.
- No official scorer, holdout, fit, sweep, tuning, alternate order, alternate rank, or second scientific diagnostic.
- E019–E035 remain immutable. Any failure closes E036; any later mutation requires E037+.

## Hypothesis

E035 showed that full covariance plus a signed rank-4 global K3 carrier reduces index-0 raw MSE from E034's `2.431378853033713e-04` to `4.920249745871731e-05`, but its off-diagonal ReLU covariance used only the first Price term

`Cov(ReLU(X_i),ReLU(X_j)) ~= p_i p_j c_ij`.

For Gaussian preactivations, Price's theorem gives a covariance-power expansion around `c_ij=0`. E036 freezes orders 1 through 4:

`Cpost_ij = c p_i p_j + c^2/2 q_i q_j + c^3/6 r_i r_j + c^4/24 s_i s_j`,

where, with `a=mu/sigma` and standard-normal pdf `phi(a)`,

- `p = Phi(a)`,
- `q = phi(a)/sigma`,
- `r = -a*phi(a)/sigma^2`,
- `s = (a^2-1)*phi(a)/sigma^3`.

The diagonal is overwritten by the same fixed 16-node first-order Edgeworth marginal variance used for the K3 response. This is a new cross-neuron response mechanism, not a tolerance/rank/FIFO repair of E035.

## Frozen estimator

State per layer:

- full covariance `cov`;
- mean `mu`;
- diagonal residual third cumulant `k3_diag`;
- exactly four signed K3 atoms `A in R^(n x 4)` with signs in `{+1,-1}`.

Linear update:

- `mu_pre = W @ mu`;
- `cov_pre = W @ cov @ W.T`;
- `var_pre = diag(cov_pre)`;
- `A_pre = W @ A`;
- `k3_pre = (W**3) @ k3_diag + sum_r sign_r*A_pre[:,r]**3`.

ReLU marginal update:

- fixed embedded 16-node standard-normal Gauss-Hermite rule;
- first-order Edgeworth density using standardized K3 only;
- moments 1,2,3 produce `mu_post`, `var_post`, `k3_total`;
- `p,q,r,s` use Gaussian `Phi/phi` only and are not tuned by K3.

Cross-neuron covariance update is exactly the frozen order-4 Price polynomial above, symmetrized once, then its diagonal is functionally overwritten by `var_post`.

K3 carrier update:

- old atoms are multiplied by `p` coordinatewise;
- one leverage-selected residual diagonal K3 atom is born per layer using the fixed E034/E035 rule;
- exact rank 4 FIFO, no atom recomputation/rotation/SVD;
- zero residual has frozen sign `+1`.

No K4, D21, source stack, old-source basis, sampling, fitting, clipping, damping, correlation clipping, or post-hoc stabilization is allowed.

## Focused tests before science

Tests must establish:

1. Price coefficients `p,q,r,s` match their frozen analytic definitions.
2. Order-4 covariance polynomial matches explicit scalar outer-product construction.
3. Covariance update is symmetric and its diagonal matches supplied marginal variance to absolute tolerance `1e-12` (machine-roundoff identity; this tolerance is frozen before science).
4. Linear full-covariance contraction matches `W C W^T`.
5. Signed K3 CP marginal, leverage birth, zero-sign, and rank-4 FIFO invariants.
6. Gaussian zero-skew marginal ReLU rule remains finite and close to analytic mean/variance.
7. Synthetic carrier repeats exactly.

Focused tests may be iterated before any mini data are read. Once GREEN, the scientific harness is frozen and exactly one index-0 diagnostic is permitted.

## Frozen gates

All must pass:

- final-layer raw MSE `<= 1.89e-08`;
- utilization `<= 0.14`;
- adjusted proxy `raw_mse * max(0.1, utilization) < 2.5e-09`;
- residual wall time `< 0.400 s`;
- finite state/output;
- deterministic repeat max abs difference `== 0.0` and identical newborn sequence;
- covariance diagonal max abs error `<= 1e-12`;
- static/runtime scope confirms exact order 4, full covariance, rank 4, no NumPy in estimator method.

Any failed or unevaluable gate => **NO-GO / DROP E036**. No rerun or rescue under E036.
