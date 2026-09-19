# E109 protocol — deep Gaussian-Stein directional-JVP control variate

Idempotency key: `ARC-E109-DEEP-STEIN-JVP-CV-20260919`

Status at freeze: **BUDGET ADMISSION PASS / ONE TARGET-FREE FALSIFIER AUTHORIZED**.

## Provenance and exclusions

- Branch: `research/e109-deep-stein-jvp-cv-20260919`.
- Direct parent: E108 terminal head
  `073c6b66064a12fdcd18ab939002ab5458f48f69`.
- E108 blocker: first-layer exact-mean linear transport reduced frozen final-layer
  target-free risk by only 0.275%; the successor must attack an actually deep
  nonlinear component.
- This lane does **not** reuse Haar/Rao-Blackwell, E108's first-layer exact
  mean, E091, E100 orthogonal sampling, latent mixtures, or QMC/cubature.
- No public/public-mini target, scorer, holdout/full, tuning, sweep, rescue,
  canonical mutation, or ledger mutation is authorized.

## Mechanism: exact deep Stein control

Let `X ~ N(0,I_n)` and let `F_j(X)` be final-layer activation coordinate
`j` of the fixed zero-bias ReLU network. For any fixed vector `v` that
depends only on network weights, Gaussian integration by parts gives

`E[(v · grad F_j(X)) - (v · X) F_j(X)] = 0`.

A finite ReLU MLP is continuous, piecewise linear and Lipschitz for fixed
weights, so the weak directional derivative exists almost everywhere and the
Stein identity applies.

Define the exact-zero-mean control

`C_{v,j}(x) = D_v F_j(x) - (v · x) F_j(x)`.

Unlike E108, `D_v F(x)` is propagated through the **actual sample-dependent
ReLU gates at every layer**:

- `h_0=x`, `t_0=v`;
- `p_l = h_{l-1} W_l`;
- `s_l = t_{l-1} W_l`;
- `h_l = ReLU(p_l)`;
- `t_l = s_l * 1[p_l>0]`.

Thus the control targets later/deep nonlinear gate error directly. No target
mean or benchmark label appears.

## Frozen network-derived directions

Use `K=8` fixed directions. Partition the 1024 final coordinates into eight
contiguous groups of 128. For group `k`, start with a unit-norm indicator
vector `g_16^(k)` on that output group and backpropagate a target-free
mean-field sensitivity:

`g_{l-1}^(k) = 0.5 * W_l * g_l^(k)`, for `l=16,...,1`.

Normalize the resulting input vector:

`v_k = g_0^(k) / ||g_0^(k)||_2`.

The `0.5` factors are used **only to choose fixed Stein directions**. They are
not an estimator, transported first-layer mean, or fitted coefficient. The
control itself uses exact realized ReLU gates via the JVP above.

Any zero/non-finite direction norm is a terminal integrity failure.

## Frozen sampling and cross-fit

Use ordinary iid Gaussian antithetic sampling, not Haar/orthogonal/QMC:

- total trajectories `N=3968`;
- `1984` iid positive `N(0,I)` draws and exact negatives;
- eight equal groups, `248` antithetic pairs per direction `v_k`;
- within each direction group split the 248 pairs into two fixed halves of 124.

For each pair, average final response and Stein control across `x,-x`.
For each direction group independently, fit one scalar coefficient per final
output coordinate on each half:

`beta_A = cov(C_A,Y_A) / var(C_A)`,
`beta_B = cov(C_B,Y_B) / var(C_B)`.

No ridge, clipping, fallback, feature selection or post-result alteration.

Cross-apply only to the opposite half:

`M_k = 0.5 * [(mean Y_A - beta_B mean C_A)
             + (mean Y_B - beta_A mean C_B)]`.

The final candidate is the equal average of the eight `M_k`. Because each
coefficient is fitted from an independent half and each Stein control has exact
zero expectation, the correction is target-free and unbiased. Earlier-layer
outputs remain the ordinary iid-antithetic sample means.

The baseline is the ordinary iid-antithetic mean on the exact same 3968
trajectories.

## Budget-first admission

Production constants:

- width `n=1024`;
- depth `L=16`;
- budget `B=2^41=2199023255552`;
- hard admission cap `u<=0.13`.

For `N=3968`, one forward layer upper accounting core is

`2*N*n^2 + 2*N*n = 8,329,625,600 FLOPs`.

Sixteen forward layers:

`133,274,009,600 FLOPs`.

One JVP stream per trajectory has the same dominant matmul size. Using a full
second copy of the forward-layer bound is conservative:

`133,274,009,600 FLOPs`.

Reserve an additional `5,000,000,000 FLOPs` for billed Gaussian RNG,
eight mean-field direction backprops, normalization, dot products, gate
comparisons/multiplies, cross-fit reductions and final stacking.

Frozen admission upper bound:

`F_upper = 271,548,019,200 FLOPs`.

`u_upper = 271548019200 / 2^41 = 0.1234857423696667 <= 0.13`.

**ADMISSION PASS.**

No code/run is allowed if the measured estimator exceeds 0.13.

## Frozen target-free falsifier

Single synthetic production-shape network:

- width/depth: `1024/16`;
- iid He-Gaussian float32 weights;
- weight seed: `109104`;
- independent estimator seeds: `109105`, `109106`;
- NumPy PCG64 / flopscope billed Gaussian draws;
- float32 forward and JVP states, float64 output reductions.

Run two independent estimator realizations `A,B`. Define

`R_candidate = mean((C_A[-1]-C_B[-1])^2)/2`,
`R_baseline  = mean((M_A[-1]-M_B[-1])^2)/2`.

These are target-free stochastic MSE-risk estimates for the candidate and its
same-sample iid-antithetic baseline.

Repeat the exact two realizations once inside the same workflow only to verify
bitwise determinism; this is not a tuning/rerun arm and uses no target.

## Frozen gates

Integrity/admission gates, all required:

1. pre-code admission upper utilization `<=0.13`;
2. measured utilization per estimator `<=0.13`;
3. exact FLOP reconciliation;
4. finite predictions, controls, coefficients and direction norms;
5. prediction shape exactly `(16,1024)`;
6. exact antithetic input pairing;
7. all eight direction norms finite and positive;
8. deterministic predictions, risks and FLOP ledgers on exact replay;
9. source/data firewall: no benchmark/public/scorer/holdout/full access.

Scientific GO additionally requires:

10. `R_candidate < R_baseline`;
11. material risk reduction: `R_candidate/R_baseline <= 0.80`;
12. adjusted-risk proxy improves the same-sample baseline:
    `R_candidate * max(0.1,u_candidate) <
      R_baseline * max(0.1,u_baseline)`.

The competition raw target `1.89e-8` is recorded only as a scale diagnostic;
it is not substituted for benchmark evidence.

Any failed/unevaluable gate => **TERMINAL NO-GO / DROP E109**. No rescue,
seed/sample/K change, coefficient change, rerun, sweep, public diagnostic,
scorer, holdout/full or target access.

A pass means only **TARGET-FREE DEEP-NONLINEAR RISK GO** and would justify a
separate successor; it does not authorize public evaluation.
