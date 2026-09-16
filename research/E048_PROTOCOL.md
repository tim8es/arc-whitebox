# E048 Protocol — source-free response recurrence

Status: preregistered. No public data may be accessed before the synthetic falsifier is GREEN.

Base canonical: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
Branch: `research/e048-source-free-response-recurrence-20260916`
Date: 2026-09-16

## Hypothesis

Propagate finite-width non-Gaussian correction without a birth-source list by storing only observables already contracted with next-layer consumers. State is fixed-size: `D3_l`, `D21_l`, and minimal `R4_l`; no order-3/order-4 tensor is materialized or stored and state never grows by source count or depth.

Disjoint exclusions: source selection/backward leverage, replay/checkpoints, signed sigma, harmonic defect, connected-diagram DP, Gaussian mixtures, oracle SVD, adaptive low rank, cosmetic node pruning.

## Frozen arithmetic and consumers

- dtype `float64`.
- Synthetic architecture width 32, depth 8, zero biases.
- Synthetic RNG `numpy.random.Generator(numpy.random.PCG64(48048))`; weights iid `N(0,1/width)`.
- Public architecture, only if synthetic GREEN: width 1024, depth 16.
- No fitted constants, learned coefficients, public calibration, clipping, damping, pruning, topology/rank adaptation.
- At layer l, next affine rows are consumers. For row w_j, `u_j=w_j/sqrt(w_j^T Sigma_l w_j)` when denominator is nonzero; zero-norm consumers have zero response.
- State shapes are exactly `D3_l:(n,)`, `D21_l:(n,n)`, `R4_l:(n,)`.

## Exact claimed identities

For centered x with covariance Sigma and normalized projections `A=a^T x/sqrt(a^T Sigma a)`, `B=b^T x/sqrt(b^T Sigma b)`:

- `D3[a]=cum(A,A,A)`;
- `D21[a,b]=cum(A,A,B)`;
- `R4[a]=cum(A,A,A,A)`.

Affine transport is exact by cumulant multilinearity. For `y=W x`,

`cum(q^T y,q^T y,q^T y)=cum((W^T q)^T x,(W^T q)^T x,(W^T q)^T x)`,

`cum(q^T y,q^T y,r^T y)=cum((W^T q)^T x,(W^T q)^T x,(W^T r)^T x)`,

with the analogous fourth-cumulant identity. Every identity labeled exact must match explicit small-width contractions to maximum absolute error `<1e-12`.

For a zero-bias centered unit Gaussian pair with correlation rho, exact angular ReLU truth is

`E[ReLU(Z1)ReLU(Z2)] = (sqrt(1-rho^2)+(pi-acos(rho))*rho)/(2*pi)`.

Univariate zero-bias ReLU moments use

`E[ReLU(Z)^m] = 2^(m/2-1) Gamma((m+1)/2)/sqrt(pi)`.

These analytic identities define synthetic angular truth; Monte Carlo is not accepted as truth.

## Frozen recurrence

The Gaussian reference provides `(mu_l,Sigma_l)`. The response recurrence uses only current `(D3,D21,R4)`, current Gaussian correlations, and next weights.

1. `D3`: fixed sixth-order Gram-Charlier differential response at zero bias, retaining analytic linear response to `D3` and `R4` only; coefficients come from derivatives of the exact half-normal identities, never from fitting.
2. `D21`: exact affine transport followed by a fixed pair-response closure from the exact zero-bias bivariate ReLU angular kernel and its first derivatives with respect to standardized third-order perturbations. This step is explicitly approximate because general `cum(A,B,C)` is omitted.
3. `R4`: retain only consumer-diagonal fourth cumulant, transport on the same consumer, then analytic univariate ReLU fourth-cumulant response. General mixed fourth cumulants are not stored.
4. Mean correction: fixed local Edgeworth response through stored third/fourth observables. No historical source sum and no reference/oracle state at runtime.

Production state arrays have rank at most 2. Cardinality is independent of depth and number of cumulant births.

## FLOP accounting

All MLP-dependent arithmetic is billed: Gaussian mean/covariance propagation, consumer normalization, response transport GEMMs, all D3/D21/R4 updates, angular-kernel evaluation, and mean correction. Per layer is a frozen constant number of dense n-by-n GEMMs plus O(n^2) elementwise work; no O(n^3) state object and no O(n^k) tensor for k>=3.

Projected full-width gates:
- response core `<=0.100 * 2**41`;
- total `<=0.125 * 2**41`.

Synthetic tests compute the width-1024/depth-16 projected FLOP formula from production operation counts. Violation is terminal before public data.

## Synthetic falsifier

One deterministic width-32/depth-8 zero-bias PCG64(48048) case only. A test-only `K3+memK4` reference may build explicit higher-order objects at width 32; such states are forbidden from production runtime. Truth components use only the exact angular identities above.

Synthetic GREEN requires, in one focused CI run after expected RED import failure:

1. Every claimed exact affine/normalization/angular identity: max absolute error `<1e-12`.
2. Approximate `D21`: maximum relative RMS over layers 1..8 `<=0.022`, denominator `max(RMS(reference),1e-15)`.
3. Final synthetic mean-correction MSE `<=0.25` times the `K3+memK4` reference MSE against exact-angular truth.
4. No oracle/reference tensor/state imported or reachable from production runtime.
5. Runtime state has no ndarray rank >2 and no state/list growth with source count or depth.
6. Projected width-1024/depth-16 total utilization `<=0.125`, response-core utilization `<=0.100`.
7. Finite and bitwise deterministic repeated invocation.

Any failed synthetic gate is terminal `NO-GO / DROP`; no rescue, rerun, tuning, topology change, coefficient adjustment, alternate seed, or alternate synthetic case.

## Frozen public diagnostic

Only after synthetic GREEN, exactly one diagnostic may access `aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`, index 0, budget `2**41`.

Public GO gates:
- raw final-layer MSE `<=1.89e-08`;
- adjusted proxy `<2.5e-09`, `adjusted=raw*max(0.1,utilization)`;
- utilization `<=0.125`;
- response-core utilization `<=0.100`;
- failures `==0`;
- residual wall time `<0.400 s`;
- finite output;
- deterministic repeat max abs diff `==0.0`.

Any public gate failure is terminal `NO-GO / DROP`. No scorer, holdout, full split, tuning, sweep, rerun, rescue, canonical mutation, ledger mutation, or merge.