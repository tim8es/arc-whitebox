# E113 protocol — deterministic deep folded-ridge residual control

Idempotency key: `ARC-E113-DEEP-FOLDED-RIDGE-RESIDUAL-20260919`

Status at freeze: **BUDGET ADMISSION PASS / ONE SMALL-WIDTH TARGET-FREE FALSIFIER AUTHORIZED**.

## Provenance and exclusions

- Branch: `research/e113-deep-folded-ridge-residual-20260919`.
- Direct parent: E111 terminal head
  `9d0dcc429fc4b62a6607ea28c97fbb44327dbaf2`.
- E112 exact-mask/treewidth is a separate concurrent structural lane.
- E104 target-transfer is closed and is not repeated.
- No Gaussian-ReLU plug-in or later-layer Gaussian moment closure.
- No benchmark/public target, scorer, holdout/full data, target fitting, fitted
  regression coefficient, empirical covariance division, empirical variance
  division, ridge solve, tuning, sweep, rescue, canonical mutation or ledger
  mutation.
- E113 is not the E109 late gate-pair sign control and is not the E110
  Householder orbit sampler.

## Base estimator law

For a zero-bias ReLU network `F:R^n -> R^n`, write a standard Gaussian input
as `X=RQ`, where `R~chi_n`, `Q` is uniform on the unit sphere and
`R independent Q`.

Positive homogeneity gives the E104-style radial Rao-Blackwell contribution

`B(q) = mu_R * 0.5 * (F(q) + F(-q))`

with `mu_R=E[R]`.

E113 changes only the angular contribution by subtracting an exactly centered,
network-derived folded-ridge residual.

## Frozen deep direction from observable realized gates

Use one deterministic probe

`p = 1/sqrt(n) * ones(n)`.

Forward `p` through the actual frozen network and record every realized ReLU
gate. Define the scalar final observable

`s(x) = (1/sqrt(n)) * sum_j F_j(x)`.

Backpropagate its exact realized-gate gradient at `p`:

`g_L = ones(n)/sqrt(n)`,
`g_{l-1} = (g_l * 1[z_l(p)>0]) W_l^T`.

Set

`v = g_0 / ||g_0||_2`.

This is an observable deep-network direction: all layers and actual gates at
the frozen probe contribute. A non-finite or norm `<=1e-12` direction is a
terminal integrity failure.

## Deterministic coefficient: exact two-ray secant

Evaluate the actual full network only at the two unit rays `v` and `-v`.

Define

`a = 0.5 * (F(v) + F(-v))`.

No sample output, target, covariance or variance is used to construct `a`.
There is no fitted scalar multiplier.

The deterministic coefficient is the exact even network response on the deep
axis itself.

## Exact centered folded spherical control

For uniform `Q` on `S^(n-1)` and any fixed unit `v`,

`m_n = E|v^T Q|
      = Gamma(n/2) / (sqrt(pi) Gamma((n+1)/2))`.

Therefore

`C(q) = |v^T q| - m_n`

has **exactly zero expectation**.

The candidate angular contribution is

`Y(q) = B(q) - mu_R * a * C(q)`.

Hence, exactly and without fitted parameters,

`E[Y(Q)] = E[B(Q)] = E[F(X)]`.

This is not a Gaussian plug-in for a later-layer activation law. The only
analytic moment is the exact marginal of a fixed projection of a uniform
sphere direction.

## Stability proof

The coefficient has no stochastic denominator.

For every unit `q,v`,

`0 <= |v^T q| <= 1` and `0 < m_n < 1`, so

`|C(q)| < 1`.

Thus every per-direction correction obeys the deterministic bound

`||mu_R a C(q)||_2 <= mu_R ||a||_2`.

Also

`E[C(Q)^2] = 1/n - m_n^2`

exactly. There is no empirical `cov/var` ratio and no condition number in the
coefficient construction.

## Production budget admission

Inherited measured E104 production cost reference:

- `F_base = 149047442096 FLOPs`;
- budget `B = 2^41 = 2199023255552`.

E113 precompute requires one single-trajectory probe forward, one
single-trajectory backprop through all 16 layers, two single-trajectory ray
forwards, direction normalization, 2048 projection dots, centered-control
reduction and final vector correction.

Freeze a deliberately conservative overhead allowance of

`F_overhead_upper = 200000000 FLOPs`.

Then

`F_upper = 149247442096 FLOPs`,
`u_upper = F_upper / 2^41 = 0.06786987891973695 < 0.13`.

**ADMISSION PASS.**

No production-shape run is authorized by E113; this budget calculation only
establishes that the estimator family itself is not excluded by cost.

## Frozen small-width falsifier

Synthetic law only:

- width `n=8`;
- depth `L=4`;
- zero bias;
- iid He-Gaussian float64 weights, `N(0,2/n)`;
- weight seed `113104`;
- fixed probe above;
- `1024` independent estimator realizations;
- each realization uses exactly two independent Haar `8x8` bases;
- root Haar RNG seed `113105`;
- QR in float64 with sign(diag R) canonicalization;
- analytic `mu_R=E[chi_8]`;
- no target/reference predictions and no fitted parameters.

For each realization `r`, average the 16 Haar rows:

`M_base[r] = mean_q B(q)`,
`M_e113[r] = mean_q Y(q)`.

Target-free pooled stochastic risks are the across-realization final-coordinate
sample variances:

`R_base = mean_j Var_r(M_base[r,j])`,
`R_e113 = mean_j Var_r(M_e113[r,j])`.

The matched realization seeds are identical for baseline and candidate.

## Frozen gates

Integrity / exact-law gates:

1. deep direction norm finite and `>1e-12`;
2. `||v||_2` agrees with one to `<=1e-12`;
3. all outputs/coefficient/risks finite;
4. Haar orthogonality max error `<=1e-12`;
5. exact analytic control second moment
   `1/n-m_n^2 > 0`;
6. deterministic exact replay of predictions, risks and diagnostics;
7. source/data firewall: no target/public/scorer/holdout/full access.

Scientific gates:

8. `R_e113 < R_base`;
9. material variance ratio `R_e113/R_base <=0.80`;
10. across the 1024 realizations, the candidate-vs-baseline mean shift must be
    statistically consistent with zero under the exact-unbiased law:
    pooled RMS mean shift across final coordinates
    `<= 4 * sqrt(R_base/1024)`.

All ten gates pass => **SMALL_WIDTH_DETERMINISTIC_DEEP_RESIDUAL_GO**.

Any failed or unevaluable gate => **TERMINAL_NO_GO / DROP E113**. No change to
probe, direction, coefficient scale, seeds, realization count, width/depth or
control definition; no rerun/rescue/sweep.

A GO would authorize only a separate production-shaped successor. It would
not establish competition raw MSE.

## Required immutable evidence

The sole workflow records focused tests, executed SHAs/blobs, deep-direction
norm, ray coefficient norms, `m_n`, exact control second moment, Haar
orthogonality, baseline/candidate risk, risk ratio, mean-shift diagnostic,
deterministic replay, scope flags and final verdict.
