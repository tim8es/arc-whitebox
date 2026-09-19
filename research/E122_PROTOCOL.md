# E122 protocol — Haar-8 antipodal simplex source-code compression

Idempotency key: `ARC-E122-HAAR8-ANTIPODAL-SIMPLEX-SOURCE-CODE-20260920`

Status at freeze: **PROTOCOL ONLY / ONE TARGET-FREE FALSIFIER RUN AUTHORIZED AFTER CODE**.

Branch:
`research/e122-haar8-antipodal-simplex-source-code-20260920`.

Direct parent:
`research/e121-haar-plane-orbit-source-memory-20260919@e2c7473a2919b4444daa581b14d1ed706960f7d8`.

E122 branch occupancy was checked before creation; no E122 branch existed.

## E121 terminal fact being addressed

E121's 2-D Haar-plane cyclic source memory was exact-unbiased and budget-pass,
but on the frozen exact 8-D four-source block stress its pooled MSE was

`11.435172907952149 x`

the same-node iid spherical comparator. The measured blocker was insufficient
source-state dimension and strong within-plane correlation.

E122 is **not** a rescue of E121: it does not alter E121's plane phase count,
frame count, phase randomization, weighting, or cyclic-orbit construction.
E121 remains terminal.

## New mechanism

E122 propagates an **eight-source algebraic coefficient state**.

For input dimension `d>=8`, draw a Haar orthonormal 8-frame

`U in R^(d x 8), U^T U = I_8`.

In coefficient space `R^8`, construct the nine vertices
`a_0,...,a_8` of a unit regular simplex:

- `||a_j||=1`;
- `a_i^T a_j=-1/8` for `i!=j`;
- `sum_j a_j=0`.

Use the antipodal algebraic source code

`C={a_0,...,a_8,-a_0,...,-a_8}`,

so each Haar frame produces exactly `J=18` source states

`q_j = U a_j`.

Every `q_j` is propagated through the complete realized ReLU network.
There is no moment closure or layerwise re-Gaussianization.

The frame estimator is the equal-weight average of final outputs over the
18 codewords. E122 averages independent frames and multiplies by the exact
radial factor `E[chi_d]`.

### Why this is target-free and unbiased

For any fixed unit coefficient vector `a in R^8`, Haar-Stiefel invariance
implies `Ua` is uniform on `S^(d-1)`. Therefore every codeword has the
correct spherical marginal and

`E_U[(1/18) sum_{a in C} F(Ua)] = E_Q[F(Q)]`.

For zero-bias degree-one homogeneous ReLU networks,

`E[F(X)] = E[chi_d] E_Q[F(Q)]`.

Thus E122 is exactly unbiased in exact arithmetic.

The simplex source code is algebraic, fixed before weights and targets, and
uses an 8-dimensional common source state. It is not a cyclic 2-D orbit.

## Explicit exclusions / non-duplication

E122 performs none of the following:

- full activation sign-cone enumeration or mask-state tables;
- activation-boundary enumeration, root finding, flux compression, or
  omitted-boundary certificates;
- factorized cumulants or cumulant transport;
- Hermite/Wiener chaos;
- Gaussian-ReLU plug-in or Gaussian moment closure;
- target fitting, covariance/variance fitting, or learned control coefficients;
- E121 plane/phase rebalancing or any other E121 rescue;
- public/public-mini, benchmark target, scorer, holdout, or full-suite access.

The scientific object is a finite 8-source Haar coefficient code, not a
boundary representation or a distributional moment approximation.

## Frozen coefficient-code construction

Use the deterministic Helmert basis of the `1^perp` subspace in
`R^9`.

For column `j=0,...,7`:

- rows `0,...,j` equal `1/sqrt((j+1)(j+2))`;
- row `j+1` equals `-(j+1)/sqrt((j+1)(j+2))`;
- later rows are zero.

Scale every row by `sqrt(9/8)`. The resulting 9 row vectors are the regular
simplex vertices. Append their negatives to obtain 18 codewords.

Frozen algebraic gates:

- maximum norm error <= `2e-14`;
- maximum off-diagonal Gram error vs `-1/8` <= `2e-14`;
- `||sum_j a_j||_inf <=2e-14`;
- antipodal code second moment
  `(1/18) C^T C = I_8/8` to max abs <= `2e-14`.

## Frozen production candidate

- production input/width: `d=n=1024`;
- depth: `L=16`;
- source-state dimension: `K=8`;
- simplex codewords per frame: `J=18`;
- independent Haar-8 frames: `P=224`;
- propagated directions: `N=P*J=4032`;
- zero bias;
- production network propagation: float32;
- frame/source algebra and final reduction: float64 where needed;
- PCG64 Gaussian frame generation;
- deterministic modified Gram-Schmidt;
- no adaptive rank, no parameter sweep, no rescue.

## Frozen exact falsifier

Only synthetic exact-reference-friendly networks are used.

### 8-D four-source stress

Reuse the E121 exact construction:

- four independent 2-D width-2/depth-4 zero-bias He-normal subnetworks;
- subnetwork seeds:
  `121300,121301,121302,121303`;
- assemble their weights block-diagonally into one 8-D width-8/depth-4 network;
- exact final Gaussian mean is the concatenation of four E114 exact 2-D means;
- candidate receives only assembled weights, never the block decomposition or
  exact mean.

Frozen E122 candidate frame seeds:
`122400,122401,122402,122403`.

Frozen same-node iid spherical comparator seeds:
`122500,122501,122502,122503`.

Both use exactly `N=4032` propagated directions per estimate.

### 16-D eight-source stress

Construct eight independent 2-D width-2/depth-4 subnetworks with seeds

`122300,122301,122302,122303,122304,122305,122306,122307`

and assemble an exact 16-D width-16/depth-4 block network.

Exact mean is again verifier-only concatenation of exact 2-D means.

Candidate frame seeds:
`122600,122601,122602,122603`.

Same-node iid comparator seeds:
`122700,122701,122702,122703`.

Again both use `4032` propagated directions per estimate.

The 16-D case ensures that the 8-source state is not merely a full ambient
basis special case.

## Frozen scientific gates

All gates must pass:

1. simplex algebraic gates above;
2. candidate outputs finite;
3. every Haar-8 frame satisfies
   `max_abs(U^T U-I)<=2e-12`;
4. deterministic replay is bitwise exact for predictions and exact for the
   candidate accounting ledger;
5. exact 8-D pooled final-output MSE / same-node iid pooled MSE <= `0.90`;
6. exact 16-D pooled final-output MSE / same-node iid pooled MSE <= `0.95`;
7. candidate source audit finds no exact-reference, target, dataset, boundary,
   sign-cone, cumulant, Hermite, or Gaussian-plug-in dependency;
8. complete production all-in upper FLOPs <=
   `136,758,472,261`;
9. no public/public-mini/benchmark/scorer/holdout/full access.

The raw `1.89e-8` scale is diagnostic only and cannot change any frozen
parameter.

Any failed scientific or accounting gate gives:

**E122 TERMINAL NO-GO / CLOSE HAAR-8 ANTIPODAL SIMPLEX SOURCE CODE.**

If all pass:

**E122 LOCAL SCIENTIFIC GO — MULTI-SOURCE ALGEBRAIC SOURCE CODE.**

A GO authorizes no production or benchmark run; it only establishes the frozen
small-width exact mechanism.

## Complete production all-in FLOP proof

Required hard cap:

`C = 136,758,472,261 FLOPs`.

Frozen dimensions:
`d=n=1024, L=16, K=8, J=18, P=224, N=4032`.

### 1. Static simplex setup

Conservative one-time algebraic charge:

`8*K*(K+1)+256 = 832`.

This covers Helmert coefficients, square roots/scales, antipodal copy and
weights.

### 2. Haar-8 frame generation

Per frame charge:

`d*(2*K^2 + 17*K) + 64*K`.

Interpretation:

- `16*d*K`: Gaussian source generation;
- `3*d*K`: norms/normalization;
- `2*d*K*(K-1)`: all modified-Gram-Schmidt dot/AXPY work;
- `64*K`: scalar sqrt/division/bookkeeping upper.

For `K=8,d=1024` and `P=224`:

`60,669,952 FLOPs`.

### 3. Algebraic source materialization

Each frame forms all 18 ambient directions by dense
`U @ C^T`.

Charge:

`P * 2*d*K*J = 66,060,288 FLOPs`.

No trigonometric orbit generation exists.

### 4. Complete deep propagation

Use the established physical dense-layer convention:

`2*n^2 + 2*n = 2,099,200 FLOPs`

per direction per square ReLU layer.

Thus:

`N*L*(2*n^2+2*n)
 = 135,423,590,400 FLOPs`.

### 5. Final reduction / radial materialization

Conservative charge:

`N*n + 2*N + 5*n
 = 4,141,952 FLOPs`.

This covers output summation, frame/code averaging and exact radial scaling.

### All-in

`832
 + 60,669,952
 + 66,060,288
 + 135,423,590,400
 + 4,141,952
 = 135,554,463,424 FLOPs`.

Hard-cap slack:

`136,758,472,261 - 135,554,463,424
 = 1,204,008,837 FLOPs`.

Therefore protocol admission is

`135,554,463,424 <= 136,758,472,261`: **PASS**.

The executable must independently recompute every term. Any additional
candidate operation class absent from this ledger is an accounting failure and
terminal NO-GO.

Verifier-only exact references and iid comparators are not deployable candidate
cost and are reported separately.

## Immutable run discipline

1. This commit changes **only this protocol file**.
2. Only after this protocol commit may minimal method/tests/falsifier/workflow
   code be committed.
3. Exactly one GitHub Actions scientific run is authorized.
4. No rerun, seed change, K/J/P change, ratio-gate change, precision change,
   fixture change, tuning, sweep, or rescue after execution.
5. Commit one immutable result receipt with run/job/artifact/digest and explicit
   VERIFIED/UNEXECUTED classification.
6. No canonical/ledger mutation or merge.
