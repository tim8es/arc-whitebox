# E035 — full covariance + signed rank-4 K3 response

Idempotency key: `ARC-FOLLOW-RESEARCH-20260915-E035`

Status: preregistered; protocol-only first commit.

## Provenance and firewall

- Branch: `research/e035-covariance-signed-k3-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Public Phase-2 mini index **0 only** for the single scientific diagnostic.
- E029–E034 are terminal and immutable. E028 remains review-only local GO.
- No official scorer, holdout, second mini index, rank sweep, coefficient fitting, tuning, clipping/damping rescue, or canonical mutation under E035.

## Hypothesis

E033 proved coordinatewise non-Gaussian moments are essentially free but fail because cross-neuron dependence is absent. E034 retained a global signed K3 response and improved the raw error from O(1) to `2.43e-4`, but still discarded covariance. E035 tests the minimal representation that contains both dominant second-order dependence and a compact persistent third-order response:

1. the **full n x n covariance** carried by the frozen official covariance-propagation algebra; and
2. one **global signed rank-4 K3 response carrier**, with the same fixed leverage birth and FIFO rule as E034.

E035 is a new method from canonical, not a mutation/rerun of E034.

## Frozen state

Persistent state after each ReLU:

- `mu`: n-vector;
- `cov`: full symmetric n x n covariance;
- `k3_diag`: n-vector diagonal residual third cumulant;
- `A`: n x 4 signed K3 response atoms;
- `sgn`: four signs, each exactly -1 or +1.

Represented K3:

`K3 ~= Diag3(k3_diag) + sum_r sgn[r] A[:,r]^(x3)`.

Initial state:

- `mu = 0`
- `cov = I`
- `k3_diag = 0`
- `A = 0`
- `sgn = +1`.

## Linear step

For `z = W h`:

- `mu_pre = W @ mu`
- `cov_pre = W @ cov @ W.T`, evaluated with the canonical baseline contraction
- `var_pre = diag(cov_pre)`
- `A_pre = W @ A`
- `k3_pre = (W**3) @ k3_diag + sum_r sgn[r] * A_pre[:,r]**3`.

No source stack, D21 matrix, K4 state, old-source basis, sampling, or fitted table exists.

## Frozen ReLU closure

Marginal raw moments 1..3 are evaluated with the same fixed embedded 16-node standard-normal Gauss-Hermite first-order Edgeworth density used by E034:

`density(z) = 1 + gamma1 H3(z)/6`, `gamma1 = k3_pre / sigma^3`.

This produces `mu_post`, exact represented marginal `var_post`, and `k3_total`.

Cross-neuron covariance uses the canonical Gaussian-response closure:

- `gain = Phi(mu_pre / sigma)` from `flops.stats.norm.cdf`;
- `cov_post = outer(gain,gain) * cov_pre`;
- overwrite its diagonal with the Edgeworth `var_post`;
- wrap as symmetric.

The K3 response atoms use the same frozen Gaussian response gain:

`A_post = gain[:,None] * A_carrier_pre`.

## Frozen signed birth/FIFO

At each linear step choose exactly one diagonal-residual source from the previous post-ReLU `k3_diag`:

`score_j = abs(k3_diag[j]) * sum_i abs(W[i,j])**3`.

Choose the exact argmax, define

`newborn = cbrt(abs(k3_diag[j])) * W[:,j]`,

with sign `-1` iff `k3_diag[j] < 0`, otherwise `+1` (including exact zero). Push it into the four-slot FIFO and drop the oldest slot.

After ReLU:

`k3_diag_new = k3_total - sum_r sgn[r] * A_post[:,r]**3`.

Thus the closure preserves its own marginal third cumulant while retaining four all-distinct response atoms.

## Quantitative path

The official full-covariance baseline already has a compute multiplier comfortably below the required `0.14`; E035 adds only O(n^2 * 4) and O(n^2) K3 work per layer. Therefore compute is not the speculative part of this hypothesis.

Mandatory competitive gates:

- raw final-layer MSE `<=1.89e-08`;
- utilization `<=0.14`;
- adjusted proxy `raw * max(0.1, utilization) <2.5e-09`;
- residual `<0.400 s`.

## Focused tests

Before mini data:

1. full-covariance linear transport equals explicit `W C W^T` on a small synthetic case;
2. signed CP marginal identity;
3. deterministic leverage birth and zero-birth sign invariant;
4. FIFO remains exactly rank 4;
5. Gaussian (`k3=0`) marginal ReLU mean/variance agrees with analytic univariate Gaussian ReLU moments within the frozen 16-node rule tolerance;
6. covariance diagonal after update equals the frozen marginal variance;
7. deterministic synthetic repeat.

## Single frozen diagnostic

After focused GREEN, run exactly once on public Phase-2 mini index 0 under `flopscope.BudgetContext`, with one identical repeat inside the same diagnostic solely for determinism. Record:

- final-layer MSE;
- billed FLOPs/utilization and adjusted proxy;
- residual/wall time;
- max standardized skew;
- selected newborn indices;
- covariance-diagonal identity error;
- finite status;
- deterministic repeat max absolute difference;
- frozen scope checks.

## Frozen decision rule

All gates must pass. Any failed or unevaluable gate => **NO-GO / DROP E035**. No rank/FIFO change, alternate covariance formula, K4 add-back, D21 add-back, alternate quadrature, clipping/damping, second index, rerun, or rescue under E035. Any such proposal is E036+.
