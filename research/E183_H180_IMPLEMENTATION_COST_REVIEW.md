# E183 — H180 implementation / cost review for E181 protocol input

Date: 2026-09-21  
Branch: `research/e183-h180-implementation-cost-review-20260921`  
Parent: E180 head `805d11f8d59d9a502aab8b5bbf935d2f865fecea`  
Mode: **desk review only — no scientific run, no benchmark, no baseline/ledger mutation**

## 1. Scope and pinned inputs

Review only H180: one aggregate symmetric-CP inherited-K3 carrier at
`R = 3n = 3072`, deterministic target-free reprojection after each non-final
ReLU, with D3/D21 read directly from that carrier.

This note does not reopen E176/E178 and does not authorize a scientific run.
It is intended as implementation/cost input for E181.

Pinned evidence:

- E180 artifact:
  `research/E180_COST_WALL_CP_RESEARCH.md@672eeb5d4eb3f9a0921957db81439848728fae64`.
- public V29:
  `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`,
  `estimators/estimator_v29.py@17df1a073a24f96c4705b04bcf61ef60fa06dd0c`.
- official ARC K3 factorization:
  `alignment-research-center/mlp_cumulant_propagation@93d091a4c26c042bfffa28f2e76a81bc0aba94bb`,
  `src/mlp_kprop/factor_k3.py@ed7cddd91fcf3a744a02aacfba6f24f9f743c82a`.

## 2. Concrete carrier and layer operations

Freeze the carrier as:

`K3 = sum[q=1..R] lambda[q] * u[q] tensor u[q] tensor u[q]`

with `U = [u[1] ... u[R]]` of shape `(n,R)`.

At `n=1024`, one F86 unit is
`u = 2*n^3 = 2^31 = 2,147,483,648 FLOPs`.

### A. Linear transport

`U_pre = W @ U`.

A classical `(n,n) @ (n,R)` product at `R=3n` costs:

`2*n^2*R = 3u = 6,442,450,944 FLOPs`.

At most 15 carried transports:

`C_transport = 45u = 96,636,764,160 FLOPs`.

No second full `W @ U`-class operation is affordable in the projection path.

### B. D3 / D21 extraction

Mathematically, before applying the official repeated-slice normalization:

`D3[i] = sum_q lambda[q] * U_pre[i,q]^3`

`D21 = ((U_pre * U_pre) * lambda[None,:]) @ U_pre.T`.

The dense `(n,R) @ (R,n)` D21 contraction costs another `3u`.
V29 final-layer trim does not require D21 at the final layer, so at most
14 full D21 extractions cost:

`C_D21 = 42u = 90,194,313,216 FLOPs`.

D3, column weighting and the elementwise square/cube are `O(nR)`; they still
must be metered and charged to the integration allowance below.

**Normalization warning:** the official `DSTensor` repeated-index convention
contains scaling conventions; `FactoredTensor.from_dstensor` explicitly has
a factor 3 around the `(2,1)` bridge. E181 must not assume the displayed
mathematical D21 is byte-for-byte the V29 slice convention until G1 passes.

### C. Post-ReLU inherited part

For the equal-leg inherited K3 term, official Wick contraction specializes to:

`U <- w1[:,None] * U`.

This is `O(nR)`.

### D. Exact birth integration before compression

V29's structured K3 birth is:

`B1 = Sym(X1, P, Y1)`

`B3 = Sym(M, P, P)`.

V18 D21 feedback is folded into `X1,Y1`; V17 K4 regeneration feeds the same
structured source machinery.

A general symmetric triplet has the exact polarization identity:

`Sym(a,b,c) = ((a+b+c)^3 + (a-b-c)^3 + (-a+b-c)^3 + (-a-b+c)^3) / 24`

where `v^3` denotes `v tensor v tensor v`. Therefore rank-`n` B1 needs at
most `4n` symmetric CP atoms.

For the repeated-leg term:

`Sym(m,p,p) = ((m+p)^3 + (m-p)^3 - 2*m^3) / 6`.

Therefore rank-`n` B3 needs at most `3n` atoms.

A literal exact merge can therefore expose:

`3n inherited + 4n B1 + 3n B3 = 10n = 10,240 atoms`

before reprojection. The polarization is only `O(n^2)`; the dangerous step is
compressing those atoms back to `3n`. The implementation should stream birth
atoms rather than materialize a `1024 x 10240` slab (~40 MiB float32).

### E. Reprojection

Reprojection is the only scientifically new approximation and the only
major H180 cost not specified by E180. It must deterministically map the
post-ReLU aggregate to exactly `R=3072` atoms using estimator state/weights
only.

A generic ALS/SVD/full-Gram fit is not admissible under the envelope below.

## 3. Conservative all-in budget

E180 conservatively preserves all non-young/non-old V29 groups:

| family | cost |
|---|---:|
| K3 thin / elementwise | 24.8u |
| covariance | 7.1u |
| closure + birth | 5.7u |
| **fixed remainder** | **37.6u** |
| 15 CP transports | 45.0u |
| 14 full D21 extractions | 42.0u |
| **base before CP integration/reprojection** | **124.6u** |

Numerically:

- `C_base = 124.6u = 267,576,462,540.8 FLOPs = 0.1216796875B`.
- hard cap `0.135B = 138.24u = 296,868,139,499.52 FLOPs`.
- all CP-specific integration + reprojection + normalization + extra
  bookkeeping together have only
  `13.64u = 29,291,676,958.72 FLOPs = 0.0133203125B`.

For a conservative E181 protocol, reserve `1.00u` for all lower-order
`O(nR)` / `O(n^2)` preparation, polarization, scaling, normalization and
bookkeeping. This leaves the frozen reprojection ceiling:

`C_reproject <= 12.64u = 27,144,193,310.72 FLOPs total`.

Across 15 carried states:

`12.64u / 15 = 0.8426667u ~= 1.810e9 FLOPs per reprojection`.

This is a ceiling, not a target. Any extra cost elsewhere reduces it.

### Immediate static cost kills

At `R=3n`:

- one extra `(n,n) @ (n,R)` multiply is `3u/layer`: **NO-GO**;
- one dense `U.T @ U` or equivalent `R^2` interaction is
  `2*n*R^2 = 9u/layer`: **NO-GO**;
- full `R x R` eigendecomposition/SVD/ALS normal equations are therefore
  outside the envelope before iterations are counted;
- one sketch contraction `(n,R) @ (R,r)` costs `(3r/n)u`.
  Under the `0.8427u` average ceiling, a single pass requires `r < 288`;
  `r=256` costs `0.75u` and is the largest sensible one-pass round point;
- two such passes require approximately `r<=128` merely to leave any room
  for other projection work.

These are necessary cost conditions, not evidence that such a projector is
scientifically valid.

## 4. Cost-wall correction for E181

E180 prose uses `153.0u` for the no-old parent and therefore writes a
`14.76u` required saving. The pinned F86 grouped ledger itself reports:

`115.6 + 24.8 + 7.1 + 5.7 = 153.2u`.

Using that source ledger gives the conservative gate:

`153.2u - 138.24u = 14.96u = 32,126,355,374.08 FLOPs`.

E181 should freeze **14.96u** as the non-old saving gate unless an exact
machine-readable F86 total supersedes the published grouped rounding. Do not
silently mix the `153.0u` and `153.2u` versions.

## 5. Minimal pre-science identity / kill gates

All gates are target-free exact-small checks. Failure should stop H180 before
an expensive scientific run.

### G1 — CP materialization / slice convention

For `n<=8`, materialize the CP tensor and compare full tensor, D3, both D21
orientations, repeated-index zeroing and scaling against official
`FactoredTensor.get_dslice` / `DSTensor`.

Gate: float64 max-abs `<=1e-12`, deterministic replay.

Kills normalization/orientation errors.

### G2 — linear transport identity

Compare materialized `(W tensor W tensor W) K3` with the tensor reconstructed
from `U <- W @ U`.

Gate: max-abs `<=1e-12`.

Kills `W` / `W.T` mistakes.

### G3 — Wick contraction identity

Compare official equal-leg K3 Wick contraction with
`U <- w1[:,None] * U`.

Gate: max-abs `<=1e-12`.

Kills an invalid inherited-state transformation.

### G4 — exact birth polarization

On frozen small V29 birth factors, compare B1/B3 from the original factored
formulas against the 4-atom / 3-atom polarization formulas. Include nonzero
V18 feedback and V17-regeneration inputs; do not test only a degenerate base
case.

Gate: full tensor and D3/D21 max-abs `<=1e-12`.

Kills missing birth terms or wrong symmetrization coefficients.

### G5 — projector no-op / idempotence

For an input whose exact symmetric CP rank is already `<=R`, reprojection
must not damage representable state.

Gate:

- deterministic identical replay;
- D3/D21 relative error `<=1e-12`;
- second projection changes D3/D21 by `<=1e-12`.

Kills a projector that corrupts state even before rank pressure.

### G6 — one exact-small overcomplete structural falsifier

Construct one frozen target-free small case by exact birth merge so the
preprojection carrier exceeds the scaled rank cap. Materialize the exact
tensor before projection.

Gate:

- finite result and deterministic replay;
- pooled D21 relative RMS `<=0.015` (E180 frozen threshold);
- D3 finite and recorded;
- no target, MSE label, lambda refit, rank change or rescue.

Failure is terminal H180 structural NO-GO.

### G7 — static operation-ledger gate

Before production shape, enumerate every projection primitive and substitute
`n=1024,R=3072`.

Reject without scientific execution if:

- all-in symbolic total exceeds `138.24u`;
- integration overhead exceeds `13.64u`;
- reprojection exceeds `12.64u` after the `1u` lower-order reserve;
- the graph contains a per-layer dense `R^2` interaction or an additional
  full `(n,n)@(n,R)` product not already counted.

## 6. Protocol inputs E181 should freeze

1. Exactly one deterministic reprojection algorithm at `R=3072`.
2. Exact birth polarization and normalization equations.
3. Whether `lambda` is explicit or absorbed into signed/scaled factors,
   including cube-root/sign handling.
4. D3/D21 convention verified against the official implementation.
5. Event counts: <=15 transports, <=14 full D21 extractions, <=15
   reprojections; final layer remains V29 mean-only trim.
6. FLOP namespaces:
   `cp_transport`, `cp_d21`, `cp_d3`, `cp_wick`, `cp_birth`,
   `cp_reproject`, `cp_normalize`, plus preserved V29 remainder.
7. Conservative non-old saving gate `>=14.96u`.
8. Terminal behavior: no rank sweep, alternate projector, AGO, lambda refit,
   source-age hybrid or benchmark rescue after a failed identity/cost gate.

## 7. Review decision

**IMPLEMENTATION-WORTHY ONLY IF THE REPROJECTOR FITS THE STATIC CEILING.**

The dense CP core is arithmetically feasible at
`124.6u = 0.12168B` before CP integration/reprojection overhead. The remaining
all-in allowance is only `13.64u`; after a conservative `1u` lower-order
reserve, reprojection gets `12.64u` total / `0.8427u` per carried layer.

The main implementation risk is not `W@U` or D21 extraction; those are already
priced. It is deterministic compression of a post-birth carrier that can
transiently contain up to `10n` symmetric atoms back to `3n` without any
dense `R x R` interaction and without moving D21 beyond the frozen structural
threshold.

E181 should kill H180 before scientific execution if G1-G7 cannot all be
specified and passed. This review authorizes no benchmark or target-bearing
run.
