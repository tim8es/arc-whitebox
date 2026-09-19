# E112 protocol — factorized fourth-cumulant joint-CGF closure

Idempotency key: `ARC-E112-CUMULANT-JOINTLAW-20260919`

Status at freeze: **BUDGET ADMISSION PASS / ONE EXACT TARGET-FREE SMALL-LAW FALSIFIER AUTHORIZED**.

## Provenance and non-overlap

- Branch: `research/e112-cumulant-jointlaw-20260919`.
- Direct parent: E111 terminal head
  `9d0dcc429fc4b62a6607ea28c97fbb44327dbaf2`.
- E111 proved that exact later-layer mean/variance plus a Gaussian ReLU plug-in
  has decisive shape bias. E112 therefore retains explicit non-Gaussian
  cumulants rather than Gaussianizing.
- This mechanism does **not** reuse Haar/Rao-Blackwell, Gaussian plug-in,
  Stein/JVP, E108 first-layer controls, QMC/cubature, latent mixtures,
  E091, or E100.
- No benchmark/public/public-mini target, scorer, holdout/full, tuning, sweep,
  rescue, canonical mutation, or ledger mutation is authorized.

## Mechanism

Represent the post-ReLU law at layer `l` by a product of non-Gaussian source
marginals with cumulants through order four:

`kappa_i = (kappa1_i, kappa2_i, kappa3_i, kappa4_i)`.

The factorized law is not Gaussian. Its joint cumulant generating function is

`K_h(t) = sum_i K_i(t_i)`

with each `K_i` truncated after fourth order.

For the next linear preactivation `z = h W`, the implied joint CGF is

`K_z(t) = sum_i K_i((W t)_i)`.

Therefore every order-r joint cumulant of `z` is propagated exactly under
this factorized-source closure. In particular the marginal cumulants used by
coordinate `j` are

`kappa_r(z_j) = sum_i W_ij^r kappa_r(h_i)`,  r=1..4.

The shared-source expression defines a non-Gaussian joint law before ReLU;
E112 then closes the hierarchy by re-factorizing the post-ReLU coordinates.

### Analytic non-Gaussian ReLU step

For one preactivation with mean `mu`, variance `sigma^2`, third cumulant
`kappa3` and fourth cumulant `kappa4`, standardize `Y=(Z-mu)/sigma`.
Use the frozen second-order Edgeworth signed-density correction

`phi(y) * [1 + gamma1 H3(y)/6 + gamma2 H4(y)/24 + gamma1^2 H6(y)/72]`

where `gamma1=kappa3/sigma^3` and
`gamma2=kappa4/sigma^4`.

For powers `p=1..4`, compute

`E[ReLU(Z)^p]`

analytically on `y >= -mu/sigma`. No numerical quadrature is used.
The implementation evaluates the required Gaussian-Hermite tail integrals
from the exact recurrence

`J_0(a)=1-Phi(a)`, `J_1(a)=phi(a)`,
`J_m(a)=a^(m-1) phi(a)+(m-1)J_(m-2)(a)`.

The four positive-part raw moments are converted back to cumulants and become
the next factorized source law.

This is a genuinely non-Gaussian closure: skewness and kurtosis affect every
later-layer ReLU transform and linear mixing.

## Exact small-law falsifier

Use the same exact target-free width-8/depth-4 angular fixture that exposed the
E111 Gaussian-shape failure, so the new mechanism is tested against an already
validated reference rather than a selected rescue network:

- latent Gaussian dimension: `2`;
- width: `8`;
- depth: `4`;
- zero bias;
- He-Gaussian float64 weights;
- frozen weight seed: `111111`;
- no Monte Carlo;
- no numerical quadrature;
- no benchmark/public target.

For every exact angular ReLU sector, the activation is

`h(theta,r)=r*(a cos(theta)+b sin(theta))`.

Recursively split the complete `[0,2pi)` circle at every exact preactivation
zero. Integrate powers 1..4 analytically on every sector using exact Rayleigh
radial moments `E[R^p]=2^(p/2) Gamma(1+p/2)`.

In addition, compute the exact full post-ReLU covariance matrix at every layer
by integrating pair products on each sector. This is the direct joint-law
falsifier: E112's post-ReLU refactorization predicts zero off-diagonal
covariance, whereas the exact reference measures the dependence discarded by
the closure.

## Frozen scientific gates

All are preregistered before execution:

1. exact reference finite and deterministic;
2. first-layer E112 mean must match exact reference with MSE `<=1e-24`;
3. every predicted post-ReLU mean must be non-negative;
4. every predicted post-ReLU variance must be non-negative;
5. final-layer mean-bias MSE `<=1.89e-8`;
6. every-layer mean-bias MSE `<=1.89e-8`;
7. final-layer mean-bias MSE must improve over the frozen E111 Gaussian
   plug-in final bias `1.6698051697168073e-3`;
8. closure remains finite through all four layers;
9. source/data firewall contains no benchmark/public/scorer/holdout/full
   access.

Any failed or unevaluable scientific gate => **TERMINAL NO-GO / DROP E112**.
No clipping, moment repair, variance flooring, alternate Edgeworth order,
dependence correction, seed/fixture change, tuning, sweep, rescue or rerun is
allowed under E112.

The exact off-diagonal covariance RMS is diagnostic evidence for the joint-law
blocker and is recorded layerwise; it is not itself a tuned threshold.

## Budget-first production admission

Production shape considered only as an accounting path:

- width `n=1024`;
- depth `L=16`;
- budget `B=2^41=2199023255552`;
- hard utilization cap `0.13`.

For each layer, the four marginal cumulant transforms need four dense
vector-matrix contractions plus construction of `W^2,W^3,W^4`.

Conservative dense arithmetic core:

- three elementwise weight-power products: `3 n^2`;
- four dense vector-matrix contractions: at most `8 n^2`;
- total core per layer: `11 n^2`.

Across 16 layers:

`F_core = 11 * 16 * 1024^2 = 184,549,376 FLOPs`.

Reserve a deliberately large additional `5,000,000,000 FLOPs` for
Hermite-tail transforms, pdf/cdf, cumulant conversion, finite checks, stacking,
and helper arithmetic.

Frozen upper bound:

`F_upper = 5,184,549,376 FLOPs`.

Admission utilization:

`u_upper = 5,184,549,376 / 2^41 = 0.0023576600942760706 <= 0.13`.

**BUDGET ADMISSION PASS.**

Because the exact small-law bias gate is prior to any production scientific
execution, a scientific failure closes E112 even though the cost path fits.

## Execution policy

Exactly one workflow run is authorized by creation of
`research/E112_RUN_ARM.json` with this idempotency key and
`execute_once=true`.

The sole workflow must:

- verify the one-shot arm;
- syntax-check the frozen falsifier;
- execute the exact target-free falsifier once;
- upload JSON/log/arm artifact;
- never access public/benchmark/scorer/holdout/full data.

A workflow success only means the falsifier executed. Scientific verdict is
read from the frozen gates.

