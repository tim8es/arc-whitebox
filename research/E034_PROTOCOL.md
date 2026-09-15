# E034 — signed rank-4 global K3 response carrier

Idempotency key: `ARC-FOLLOW-RESEARCH-20260915`

Status: preregistered single frozen local diagnostic.

## Provenance and firewall

- Branch: `research/e034-signed-k3-response-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Public Phase-2 mini index **0 only** for the single scientific diagnostic.
- E023/E024/E026/E027/E029/E032/E033 are terminal and immutable. E028 remains reviewed local GO. E030/E031 are occupied and untouched.
- No official scorer, holdout, second index, fitting, tuning, sweep, coefficient search, rank search, or post-result rescue under E034.

## Motivation

E033 showed that a virtually free coordinatewise `(mu,var,k3,k4)` closure has tiny standardized marginal skew/kurtosis but O(1) final mean error. The missing information is therefore cross-neuron dependence. Independent conditional-cumulance work identifies signed low-rank residual cumulant response factors as the next representation after rank-4 conditional covariance: directional K3 contractions can be represented as sums of signed cubes `(a_s^T w)^3` without forming an n^3 tensor.

E034 tests that representation directly in an end-to-end carrier. It is not a compression of V25/V29 per-source hub tensors: there is one global rank-4 signed K3 response state, refreshed online, with no source stack, shared old basis, D21 matrix, or K4 state.

## Frozen representation

Persistent state per layer:

- `mu` — n-vector mean;
- `var` — n-vector diagonal variance;
- `k3_diag` — n-vector residual diagonal third cumulant;
- `A` — exactly four n-vectors of signed global K3 response atoms;
- `sgn` — exactly four signs in {-1,+1}.

The represented third-cumulant tensor is

`K3 ~= Diag3(k3_diag) + sum_{r=0}^3 sgn[r] * A[:,r]^(x3)`.

### Linear layer

For `z = W h`:

- `mu_pre = W @ mu`;
- `var_pre = (W*W) @ var`;
- transported response atoms `A_pre = W @ A`;
- marginal third cumulant
  `k3_pre = (W**3) @ k3_diag + sum_r sgn[r] * A_pre[:,r]**3`.

No covariance matrix or source tensor is formed.

### ReLU use/update

Use a fixed embedded 16-node standard-normal Gauss-Hermite Edgeworth rule with *only* the frozen marginal skew `gamma1=k3_pre/sigma^3` to compute ReLU raw moments 1..3, hence `(mu,var,k3_total)`.

Transported global response atoms are multiplied coordinatewise by the frozen local response derivative

`p_i = sum_q w_q * 1[mu_pre_i + sigma_i z_q > 0]`.

This is the Gaussian ReLU response probability evaluated by the same fixed quadrature; no fitted coefficient is used.

### One adaptive signed birth per layer

The diagonal residual `k3_diag` represents exact rank-1 source atoms after the next linear map:

`a_j = cbrt(abs(k3_diag[j])) * W[:,j]`, sign `sign(k3_diag[j])`.

E034 chooses **exactly one** newborn source per layer: the coordinate j maximizing the fixed leverage score

`abs(k3_diag[j]) * sum_i abs(W[i,j])**3`.

After the linear layer, the newborn atom is its exact `a_j`. The four-slot response carrier is a fixed FIFO: append the newborn and discard the oldest slot. There is no energy/rank threshold and no comparison among alternate carriers.

After ReLU, subtract the represented CP marginal from `k3_total`:

`k3_diag_new = k3_total - sum_r sgn[r] * A_post[:,r]**3`.

Thus the frozen carrier exactly preserves its own computed marginal K3 while retaining four signed all-distinct response atoms across layers.

## Quantitative path

The state uses O(4n) response storage. Per layer the dominant work is a constant number of n^2 matrix-vector/matrix-thin products plus one n-by-4 atom transport, so expected utilization is far below 0.14. A successful representation therefore has a direct path to the score floor.

Mandatory local win gates:

- raw final-layer MSE `<= 1.89e-08`;
- utilization `<= 0.14`;
- adjusted proxy `raw * max(0.1, utilization) < 2.5e-09`.

## Focused tests before mini data

1. signed CP marginal equals `sum s_r A_r^3` exactly;
2. linear atom transport agrees with explicit `(W a)^(x3)` directional marginal;
3. newborn leverage selector is deterministic and returns the fixed score argmax;
4. FIFO always has exactly four slots/signs;
5. Gaussian (`k3=0`) ReLU update is finite with nonnegative variance;
6. repeated synthetic calls are deterministic.

## Single frozen diagnostic

After focused GREEN, run exactly once on public Phase-2 mini index 0 under `flopscope.BudgetContext`. Record final MSE, billed FLOPs/utilization, adjusted proxy, residual/wall time, maximum absolute standardized skew, selected newborn indices, finite status, deterministic repeat difference, and frozen scope checks.

## Frozen gates

All must pass:

1. raw final MSE `<=1.89e-08`;
2. utilization `<=0.14`;
3. adjusted proxy `<2.5e-09`;
4. residual `<0.400 s`;
5. finite state/output;
6. deterministic repeat max abs difference `==0`;
7. carrier remains exactly four signed atoms plus three n-vectors;
8. no MLP-dependent numerical arithmetic outside flopscope operations in the estimator path.

Any failed/unevaluable gate => **NO-GO / DROP E034**. No rank change, FIFO change, selector change, alternate leverage score, extra K4/covariance state, clipping/damping, second index, or rerun under E034. A subsequent mutation must be E035+.
