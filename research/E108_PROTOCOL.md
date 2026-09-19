# E108 protocol — exact-mean first-layer transported control variate

Idempotency key: `ARC-E108-FIRSTLAYER-EXACTMEAN-TRANSPORT-CV-20260919`

Status at protocol freeze: **ADMISSION PASS / IMPLEMENTATION AUTHORIZED**

## Provenance and scope

- Branch: `research/e108-firstlayer-exactmean-transport-cv-20260919`
- Direct parent: `research/e105-two-haar-risk-cert-20260919`
- Parent mechanism: frozen E104 analytic-radius two-Haar antithetic estimator plus E105 target-free risk identity.
- Closed lanes not reused: E038 Sobol/QMC, E100 stochastic shrinkage, E105 risk-only certificate, E106 quartic spherical cross-fit, E107 exact degree-4 cubature.
- No public/public-mini, benchmark targets, official scorer, holdout/full, tuning, sweep, rescue, canonical mutation, or ledger mutation.

## Why this lane is distinct

E108 uses an exact population mean that is available only at the first ReLU layer and transports that zero-mean fluctuation through a fixed network-derived mean-field Jacobian. It does **not** fit benchmark targets, does not use quartic/angular polynomial features, does not reweight cubature nodes, and does not change the E104 sampling law.

For one E104 analytic-radius spherical sample `x = r q`, where `r=E[chi_n]` and `q` is marginally uniform on the sphere, first-layer preactivation coordinate `z_j=x^T w_j` obeys positive homogeneity. Therefore

`E_q[ReLU(r q^T w_j)] = E_X[ReLU(X^T w_j)] = ||w_j|| / sqrt(2*pi)`

for `X~N(0,I)`.

For each antithetic pair define

`a(q) = (ReLU(x W1) + ReLU(-x W1))/2`.

Then `E[a(q)] = mu1` exactly, with `mu1_j=||W1[:,j]||/sqrt(2*pi)`.

Define the fixed downstream mean-field transport

`T = (0.5 W2)(0.5 W3)...(0.5 W16)`.

The output-shaped control

`z(q) = (a(q)-mu1) T`

has exact spherical expectation zero. This gives a target-free control variate tied to actual network weights rather than generic angular moments.

## Frozen cross-fit rule

E104 supplies two independent Haar blocks. For each block `b`, keep its final antithetic-pair responses `y_b(q)` and transported scalar-per-output control `z_b(q)`.

Fit one scalar coefficient per output coordinate on each block:

`beta_b[j] = sum_i (z_b[i,j]-mean z_b[:,j]) (y_b[i,j]-mean y_b[:,j]) / sum_i (z_b[i,j]-mean z_b[:,j])^2`.

No ridge, clipping, fallback, feature selection, rank selection, or alternate coefficient rule.

Apply coefficients only across blocks:

`m1_corr = mean(y1) - beta2 * mean(z1)`
`m2_corr = mean(y2) - beta1 * mean(z2)`
`candidate = (m1_corr + m2_corr)/2`.

Because `beta2` is measurable with respect to block 2 and block 1 is independent with `E[mean(z1)]=0` (and vice versa), the correction is unbiased under the frozen E104 law.

Only the final-layer estimate is corrected. Earlier returned layer means remain the unmodified E104 block average.

## Budget-first admission check

Frozen production constants:

- width `n=1024`
- depth `L=16`
- trajectories per estimator `4096`
- budget `B=2^41=2199023255552`
- admission cap `u<=0.13`
- inherited fully billed E105/E104 base: `149114550960` FLOPs, `u=0.06780944702768466`

Conservative incremental bound before code:

1. Build `W2...W16` transport: 14 dense `1024x1024` products.
   Using `2 n^3` each gives `30,064,771,072` FLOPs.
2. Apply transport to the two `1024x1024` paired first-layer blocks:
   at most one equivalent `2048x1024 @ 1024x1024` product,
   `4,294,967,296` FLOPs.
3. Reserve `1,000,000,000` FLOPs for exact-mean construction, centering,
   scalar cross-fit coefficients, reductions, stacking, and helper transforms.

Conservative total upper estimate:

`149114550960 + 30064771072 + 4294967296 + 1000000000 = 184474289328` FLOPs.

Admission utilization:

`184474289328 / 2^41 = 0.08388919437857112 <= 0.13`.

Remaining cap headroom is over `101B` FLOPs even under this conservative bound.

**Admission decision: PASS.**

## Frozen falsifier

One synthetic production-shape network and two independent E108 estimator realizations:

- width/depth: `1024 x 16`
- weight seed: `108104`
- estimator direction seeds: `108105`, `108106`
- E104 law: exactly two Haar blocks + antipodes, analytic `E[chi_1024]` radius
- no target data.

For independent candidate predictions `C_A,C_B` and baseline predictions `M_A,M_B`:

`R_candidate = mean((C_A[-1]-C_B[-1])^2)/2`
`R_baseline  = mean((M_A[-1]-M_B[-1])^2)/2`.

These are target-free stochastic MSE-risk estimators for the respective unbiased randomized estimators.

## Frozen gates

All must pass for E108 GO:

1. measured utilization per estimator `<=0.13`;
2. complete FLOP reconciliation;
3. candidate risk `<=1.89e-8`;
4. adjusted-risk proxy `candidate_risk * max(0.1, utilization) < 2.5e-9`;
5. candidate risk < baseline risk on the same four Haar blocks;
6. finite predictions/coefficients/control values;
7. exact antithetic pairs;
8. deterministic prediction, risk, and FLOP-ledger replay;
9. exact-mean first-layer formula checked numerically on a small synthetic Monte Carlo fixture;
10. source firewall contains no benchmark/public/scorer/holdout/full access.

Any failed or unevaluable scientific gate => terminal **NO-GO / DROP E108**. No rescue, rerun, coefficient alteration, seed/sample/rank sweep, or public evaluation.
