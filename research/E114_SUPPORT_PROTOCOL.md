# E114 support protocol — deterministic observability-compressed boundary flux residual

Idempotency key: `ARC-E114-OBSERVABILITY-FLUX-RESIDUAL-SUPPORT-20260919`

Status at freeze: **ONE SMALL EXACT FALSIFIER AUTHORIZED**.

## Provenance and purpose

- Branch: `research/e114-observability-flux-residual-support-20260919`.
- Parent: sealed E114 activation-boundary-flux positive-closure head
  `b9f64030f65da9b32fc7718d04fb108ee1a73dab`.
- The parent established the exact identity expressing a deep zero-bias ReLU
  Gaussian mean through activation-boundary flux, but did not establish a
  compact production representation.
- This support lane tests one concrete compression mechanism for the **final
  observable only**, without fitting to benchmark targets or storing a global
  activation-mask state table.

Excluded:
- target/public/public-mini/scorer/holdout/full access;
- fitted regression coefficients;
- empirical covariance or variance division;
- Gaussian plug-in closure for later-layer ReLU moments;
- explicit full mask-state message tables;
- QMC/cubature tuning;
- seed/rank rescue or post-result sweep;
- canonical/ledger mutation.

## Mechanism

Let `F:R^2 -> R^m` be the fixed vector output of a zero-bias deep ReLU
network. On each angular linear region of the unit circle,

`F(q(theta)) = q(theta)^T A_r`,

with `A_r in R^{2 x m}`.

E114 gives the exact Gaussian mean vector from derivative jumps at angular
activation boundaries:

`mu = E[R]/(2*pi) * sum_k Delta_k`.

### Deterministic output observability subspace

Construct a weight-only downstream observability Gramian in output space.

Let `D_L = I_m`. Working backward through the frozen weight matrices,

`D_{l-1} = 0.5 * W_l D_l`.

Accumulate

`G = sum_l D_l^T D_l`.

The factor `0.5` is only a deterministic mean-gate sensitivity convention
used to rank output directions; it is **not** a Gaussian activation plug-in and
is never used to approximate the network mean.

Take the top `r=2` eigenvectors of `G` and form the orthogonal projector

`P = U_r U_r^T`, `Rperp = I-P`.

The projector depends only on observable frozen weights. No target output,
sample covariance, sample variance, ridge solve or fitted coefficient appears.

### Hybrid estimator

Use the exact E114 boundary-flux identity only for the compressed component

`mu_parallel = mu P`.

Estimate only the orthogonal residual with the ordinary radial
Rao-Blackwellized antithetic angular estimator

`B(q) = E[chi_2] * 0.5 * (F(q)+F(-q))`.

For `N` angular samples,

`m_hat = mu_parallel + (1/N) sum_i B(q_i) Rperp`.

Because `P` is deterministic and `E[B(Q)]=mu`,

`E[m_hat] = mu P + mu Rperp = mu`.

Thus the estimator is exactly unbiased and target-free.

## Stability

- `P` and `Rperp` are orthogonal projectors, so their operator norms are
  exactly one.
- No stochastic denominator exists.
- There is no `cov/var` division or fitted regression.
- The only spectral stability gate is an eigengap check on the deterministic
  weight-only Gramian:
  `(lambda_r-lambda_{r+1})/max(lambda_r,1e-300) >= 1e-6`.
- Failure of that eigengap is terminal for this specific construction.

## Frozen exact small falsifier

Network:
- input dimension: `2`;
- hidden/output width: `8`;
- depth: `4` ReLU layers;
- zero bias;
- W1 shape `2x8`, W2-W4 shape `8x8`;
- iid He-normal float64 weights;
- weight seed: `114214`;
- compression rank: `r=2`.

Exact angular reference:
- propagate linear-region coefficient matrices over `theta in [0,2*pi)`;
- split only at analytically solved zeros of current layer preactivations;
- no Monte Carlo or numerical quadrature in the scientific reference;
- no global mask table is stored: only the current angular interval and its
  local coefficient matrix are propagated;
- merge adjacent identical coefficient regions;
- collect final derivative-jump vectors `Delta_k in R^8`.

Verify:
1. boundary-flux mean equals direct analytic sector integral;
2. radial-RB paired angular mean equals the same exact mean;
3. all partitions cover the full circle without gap/overlap;
4. deterministic replay is exact.

## Exact target-free variance calculation

Build the common angular partition for `F(q)` and `F(-q)`. On each interval,
`B(q(theta))` is linear in `(cos theta, sin theta)`, so both its first and
second moments are integrated analytically.

Let

`Sigma_B = Var_Q[B(Q)]`.

Then the baseline per-sample pooled variance is

`V_base = mean(diag(Sigma_B))`.

The residual estimator covariance is exactly

`Sigma_res = Rperp Sigma_B Rperp`,

and

`V_res = mean(diag(Sigma_res))`.

For the production-reference trajectory count `N=4096`, define exact
small-network stochastic-risk diagnostics

`R_base_4096 = V_base / 4096`,
`R_res_4096 = V_res / 4096`.

No fitted coefficient or target labels are used in these quantities.

## Frozen gates

Integrity:
1. all region coefficients, jumps, means and moments finite;
2. complete angular partition;
3. boundary-flux mean and direct sector mean max abs difference `<=1e-11`;
4. paired angular mean and boundary-flux mean max abs difference `<=1e-11`;
5. projector symmetry/idempotence errors each `<=1e-11`;
6. deterministic eigengap relative value `>=1e-6`;
7. deterministic replay exact;
8. no target/public/scorer/holdout/full access.

Scientific support:
9. residual pooled variance strictly below baseline;
10. material variance ratio `V_res/V_base <=0.50`;
11. exact small-network `R_res_4096 <= 1.89e-8`.

All eleven pass =>
**E114_OBSERVABLE_STRUCTURE_SUPPORT_GO**.

Any failed or unevaluable gate =>
**TERMINAL_SUPPORT_NO_GO / DROP THIS E114 COMPRESSION MECHANISM**.

No rank change, alternate Gramian, seed change, width/depth change, mask
enumeration rescue, fitted coefficient, rerun or sweep after the frozen result.

A GO would only support a separate production-cost gate; it would not authorize
public/full evaluation.

## Required receipt

Record:
- executed SHAs/blobs and sole run/job;
- final angular region count and boundary count;
- observability eigenvalues and relative eigengap;
- projector integrity;
- exact mean cross-checks;
- exact baseline/residual pooled variance and ratio;
- 4096-sample risk diagnostic and ratio to `1.89e-8`;
- all scope flags and final verdict.
