# R215 — protocol-first falsifier for factorized marginal characteristic-function closure

Date: 2026-09-22  
Idempotency: `ARC-R215-MARGINAL-CF-20260922`  
Branch: `research/r215-marginal-characteristic-function-20260922`  
Parent: R212 terminal branch.

## 0. Selected family and novelty

R215 selects exactly one estimator-level family that exists in immutable project history only
as an unexecuted documented lead:

**factorized marginal characteristic-function closure (FMCF-32).**

Immutable project source:

- `research/E125_APPEND_ONLY_LESSON.md`
- commit `7b1fa757c6bbad076d91b29009913f84cde441c4`
- blob `e81876b0f827450cb37ae2d168f28b6f72a93404`.

That lesson proposed scalar characteristic-function transport for later-layer ReLU
absolute moments and explicitly required a future protocol to prove transport closure,
tail/quadrature control, cost, and an exact-small non-Gaussian falsifier.

Repository branch/code searches before R215 found no executed branch for
`characteristic`, `fourier`, `fft`, `laplace transform`, or `cf transport`.

R215 is not:

- Strassen / Alternative-Basis Strassen;
- TA/LITA or any bilinear-rank sweep;
- contraction-DAG CSE/reassociation;
- dense Hermite chaos (E115);
- direct particle/cubature/QMC;
- Gaussian mixture/half-space mixture;
- K3/D21 carrier compression;
- target fitting.

## 1. Primary literature

The nonlinear scalar step is supported by primary characteristic-function literature:

Iosif Pinelis,
*Positive-part moments via characteristic functions, and more general expressions*,
Journal of Theoretical Probability 31 (2018), 527–555,
DOI `10.1007/s10959-016-0709-1`.

Also:

Iosif Pinelis,
*Characteristic function of the positive part of a random variable and related results,
with applications*, Statistics & Probability Letters 106 (2015), 281–286,
DOI `10.1016/j.spl.2015.07.031`.

For integrable real `U`:

[
E[operatorname{ReLU}(U)]
=
E[U_+]
=
rac12 E[U]+rac12 E|U|,
]

and absolute/positive-part moments admit integral representations in terms of the
characteristic function.

The primary literature validates the **scalar inversion step**. It does not claim that
univariate marginal characteristic functions are closed under dependent dense mixing.
That closure is exactly what R215 falsifies.

## 2. Frozen estimator family

Production constants:

- width `n=1024`;
- depth `L=16`;
- frequency count `K=32`;
- frequency grid
  [
  t_k = kpi/64,quad k=1,ldots,32.
  ]
  Thus (pi/2) is included at (k=32).

State per neuron:

- scalar mean;
- univariate marginal characteristic-function values
  [
  phi_i(t_k)=E[e^{it_k h_i}].
  ]

Frozen dense-mixing closure:

[
widehatphi_{z_j}(t_k)
=
prod_{i=1}^n phi_i(t_k W_{ji}),
]

using deterministic interpolation of the stored marginal grid when a scaled frequency is
not a grid node.

This is the exact independent-sum identity used as a **closure approximation** after
dependence has appeared. No joint characteristic-function state is retained.

Frozen nonlinear step:

- use a deterministic characteristic-function positive-part transform/integral to obtain
  the next ReLU mean and next marginal CF grid;
- no target fitting, particle correction, covariance/K3 side state, or learned
  dependence correction.

Only this marginal-factorized family is tested. A joint-CF or copula-augmented successor
would be a different family.

## 3. Conservative production FLOP screen

Budget:

[
B=2^{41}=2,199,023,255,552.
]

Current project all-in research cap used for estimator admission:

[
0.135B=296,868,139,499.52.
]

### Mandatory lower bound

For each layer/output/frequency, combining `n` complex marginal factors requires at least
`n-1` complex multiplications.

One complex multiply needs at least 4 real multiplies + 2 real additions = 6 FLOPs.

Therefore, before interpolation, nonlinear CF transformation, means, storage or any base
estimator work:

[
F_{LB}
=
6L n K(n-1).
]

For `L=16,n=1024,K=32`:

[
F_{LB}=3,218,079,744,
]

[
F_{LB}/B=0.0014634132385253906.
]

This does **not** kill the family.

### Conservative implementation upper envelope

To establish that the synthetic falsifier is genuinely cost-admissible rather than merely
not lower-bound-killed, freeze a deliberately generous estimator-only arithmetic envelope:

- scaled-frequency interpolation + complex accumulation:
  [
  24LKn^2;
  ]
- nonlinear CF transform on a `K x K` deterministic quadrature grid:
  [
  32LnK^2;
  ]
- mean/absolute-moment reduction:
  [
  8LnK.
  ]

Total:

[
F_{upper}
=
13,425,967,104,
]

[
F_{upper}/B
=
0.0061054229736328125.
]

This is far below `0.135B`; therefore the frozen exact-small synthetic check is
authorized.

This is only an algorithmic arithmetic envelope. It is not a production accuracy claim.

## 4. Exact-small dependence falsifier

Use two exact joint laws over ((X,Y)), each supported on two equiprobable points.

### Law C — perfectly correlated

Let (Sin{-1,+1}) uniformly and

[
(X,Y)=(S,S).
]

### Law A — perfectly anti-correlated

With the same `S`:

[
(X,Y)=(S,-S).
]

For **both** laws, each coordinate marginal is Rademacher:

[
P(X=pm1)=P(Y=pm1)=1/2,
]

hence for every real `t`:

[
phi_X(t)=phi_Y(t)=cos t.
]

So the entire FMCF-32 input state is identical for C and A, not merely the 32 frozen
samples.

Now use the frozen dense linear observable

[
U=X+Y.
]

True laws:

- correlated: (U=2S), so
  [
  E[operatorname{ReLU}(U)]=1;
  ]
- anti-correlated: (U=0), so
  [
  E[operatorname{ReLU}(U)]=0.
  ]

At the frozen grid point (t=pi/2):

[
phi_X(pi/2)=phi_Y(pi/2)=0.
]

FMCF factorized closure predicts for **both** laws:

[
widehatphi_U(pi/2)=0.
]

But the exact preactivation CFs are:

- correlated:
  [
  phi_U(pi/2)=cospi=-1;
  ]
- anti-correlated:
  [
  phi_U(pi/2)=1.
  ]

Thus the two inputs are indistinguishable to the complete marginal-CF state but have
different next preactivation laws and different next ReLU means.

This is an information/nonclosure falsifier; increasing `K` cannot repair it because the
full univariate marginal CFs are identical for the two joint laws.

## 5. Frozen synthetic check

Because the production cost envelope is feasible, exactly one target-free synthetic check
is authorized.

The executable must verify:

1. both joint laws have exactly identical per-coordinate marginal support/probabilities;
2. the full frozen 32-point marginal-CF grids agree to <= `2e-15`;
3. factorized preactivation CF grids agree to <= `2e-15`;
4. at (t=pi/2), exact true preactivation CF is `-1` vs `+1`;
5. exact ReLU means are `1` vs `0`;
6. deterministic replay is bitwise-identical;
7. cost lower/upper arithmetic exactly matches the frozen integers above.

Primary scientific gate:

A deterministic estimator whose entire carried state is the FMCF marginal state must
produce the same candidate output on the two laws. Since exact outputs differ by 1, its
worst-case absolute ReLU-mean error across the pair is at least

[
1/2.
]

Frozen pass-to-continue criterion would require worst-case absolute error <= `1e-6`.

Therefore observing the exact indistinguishability witness is a scientific
**TERMINAL NO-GO** for FMCF-32 and, in fact, for any finite/infinite univariate-marginal-CF
grid without joint dependence state.

No rescue by changing K, grid, quadrature, interpolation, or scalar positive-part formula
is allowed under R215.

## 6. Safety

Forbidden:

- holdout;
- public/public-mini benchmark;
- official scorer;
- paid compute;
- submission;
- target fitting;
- second synthetic seed/law;
- parameter sweep;
- canonical/leaderboard mutation.

One exact-small synthetic workflow run only.
