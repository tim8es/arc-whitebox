# E183 — H180 implementation / cost review for E181 protocol input

Date: 2026-09-21  
Branch: `research/e183-h180-implementation-cost-review-20260921`  
Parent: E180 head `805d11f8d59d9a502aab8b5bbf935d2f865fecea`  
Mode: **desk review only — no scientific run, no benchmark, no baseline/ledger mutation**

## 1. Scope

Review only H180:

> one aggregate symmetric CP carrier for inherited K3, fixed
> `R = 3n = 3072`, deterministic target-free reprojection after each non-final
> ReLU, with D3/D21 read directly from the carrier.

This note does not reopen E176/E178 and does not authorize a scientific run.
It is intended as implementation/cost input for E181.

Pinned evidence:

- E180 research artifact blob:
  `research/E180_COST_WALL_CP_RESEARCH.md@672eeb5d4eb3f9a0921957db81439848728fae64`.
- public V29:
  `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`,
  `estimators/estimator_v29.py@17df1a073a24f96c4705b04bcf61ef60fa06dd0c`.
- official ARC K3 factorization:
  `alignment-research-center/mlp_cumulant_propagation@93d091a4c26c042bfffa28f2e76a81bc0aba94bb`,
  `src/mlp_kprop/factor_k3.py@ed7cddd91fcf3a744a02aacfba6f24f9f743c82a`.

## 2. Concrete carrier and layer operations

Freeze the carrier as

[
K_3 = sum_{q=1}^{R} lambda_q,u_q^{otimes 3},qquad
U=[u_1,ldots,u_R]inmathbb R^{n	imes R}, R=3072.
]

At Phase-2 shape `n=1024`, define one F86 unit

[
u = 2n^3 = 2^{31}=2,147,483,648 {m FLOPs}.
]

One non-final layer should have exactly these CP-specific stages.

### A. Linear transport

[
U_{m pre}=W U.
]

A classical `(n,n) @ (n,R)` product costs

[
2n^2R = 3u = 6,442,450,944 {m FLOPs}.
]

There are at most 15 carried transports in a 16-layer network:

[
C_{m transport}=45u=96,636,764,160.
]

No second full `W @ U`-class operation is affordable in the projection path.

### B. Slice extraction

Fold (lambda) into the columnwise square for

[
D_{21}=((U_{m pre}odot U_{m pre}),lambda),U_{m pre}^{T}.
]

The dense `(n,R) @ (R,n)` contraction is another `3u` per full
D21. V29 final-layer trim does not require D21 at the final layer, hence at
most 14 full extractions:

[
C_{D21}=42u=90,194,313,216.
]

The diagonal slice is lower order:

[
D_3[i]=sum_qlambda_q U_{m pre}[i,q]^3.
]

Squaring/cubing, column scaling, D3 reduction and Wick row scaling are
`O(nR)`; they must nevertheless be metered and charged to the integration
allowance below.

**Normalization warning:** the formulas above are mathematical tensor slices.
The official `DSTensor` repeated-index convention contains scaling conventions
(the official `FactoredTensor.from_dstensor` explicitly carries a factor 3 for
the `(2,1)` slice). E181 must not hard-code the displayed D21 formula as the
V29 convention until the identity gate in section 5 passes.

### C. Post-ReLU inherited part

For the inherited K3 term, equal Wick contraction on all three legs is

[
u_q leftarrow d(w_1)u_q,
]

which is only a row scaling of `U`. This is the symmetric-CP specialization
of the official `FactoredTensor.contract_wick` operation.

### D. Exact birth integration before compression

V29's K3 birth has the structured hubs

[
B_1=operatorname{Sym}(X_1,P,Y_1),qquad
B_3=operatorname{Sym}(M,P,P),
]

with the V18 D21 feedback folded into (X_1,Y_1), and the V17 K4 regeneration
feeding the same structured source machinery.

A general symmetric rank-one triplet has the exact polarization

[
operatorname{Sym}(a,b,c)=rac1{24}left[
(a+b+c)^{otimes3}+(a-b-c)^{otimes3}
+(-a+b-c)^{otimes3}+(-a-b+c)^{otimes3}ight].
]

Thus a rank-(n) B1 birth can be converted exactly to at most `4n` symmetric
CP atoms.

For the repeated-leg B3 term,

[
operatorname{Sym}(m,p,p)=rac16left[
(m+p)^{otimes3}+(m-p)^{otimes3}-2m^{otimes3}ight],
]

so B3 needs at most `3n` atoms.

Therefore a literal exact merge of the inherited `3n` carrier plus the two
newborn hubs can expose as many as

[
3n+4n+3n=10n=10,240
]

atoms before reprojection. The polarization itself is only `O(n^2)`, but a
generic CP fit of those 10,240 atoms is not affordable. The implementation
should stream these atoms; materializing a `1024 x 10240` float32 factor slab
would be about 40 MiB and is unnecessary.

### E. Reprojection

This is the only scientifically new approximation and the only cost component
not specified by E180. It must map the post-ReLU aggregate back to exactly
`R=3072` atoms using estimator state/weights only.

The protocol must freeze its equations **before** any target-bearing execution.
A generic ALS/SVD/Gram solve is not admissible under the cost envelope below.

## 3. Conservative all-in budget

E180 conservatively keeps every non-young/non-old V29 family:

- K3 thin/elementwise: `24.8u`;
- covariance: `7.1u`;
- closure + birth: `5.7u`.

Fixed remainder:

[
C_{m fixed}=37.6u=80,745,385,164.8.
]

CP dense core:

[
C_{m CP-core}=45u+42u=87u=186,831,077,376.
]

Before reprojection/integration overhead:

[
C_{m base}=124.6u
=267,576,462,540.8
=0.1216796875B.
]

Hard cap:

[
0.135B=138.24u=296,868,139,499.52.
]

So **all CP-specific integration + reprojection + normalization + extra
bookkeeping together have only**

[
C_{m integration,max}=13.64u
=29,291,676,958.72
=0.0133203125B.
]

For a conservative implementation protocol, reserve `1.00u` of that envelope
for all `O(nR)` / `O(n^2)` CP preparation, polarization, scaling,
normalization and bookkeeping. That leaves a frozen **reprojection ceiling**

[
C_{m reproj,max}=12.64u
=27,144,193,310.72.
]

With 15 non-final carried states, the average reprojection allowance is only

[
12.64u/15=0.8426667u
approx 1.810	imes10^9 {m FLOPs/layer}.
]

This is a ceiling, not a target. Any cost charged elsewhere reduces it.

### Immediate cost-kill patterns

At `R=3n`:

- one extra `(n,n)@(n,R)` multiply = `3u` per layer: **dead**;
- one dense `U^T U` or `(n,R)@(R,R)`-scale interaction costs
  `2nR^2=9u` per layer: **dead**;
- full `R x R` eigendecomposition/SVD/ALS normal equations are therefore
  outside the envelope before solver iterations are counted;
- one sketch contraction `(n,R)@(R,r)` costs
  `(3r/n)u`. Under the `0.8427u` average ceiling, a single pass has the
  mathematical bound `r < 288`; `r=256` costs `0.75u` and is the largest
  sensible one-pass round point;
- two such passes require approximately `r<=128` merely to leave any room for
  other projection work.

These are necessary cost conditions only; they do not establish a valid
reprojection.

## 4. Cost-wall correction for E181

E180's prose uses `153.0u` for the no-old parent and therefore writes a
required saving of `14.76u`. The pinned F86 ledger itself reports

[
115.6+24.8+7.1+5.7=153.2u.
]

Using the source ledger rather than the rounded prose gives the conservative
requirement

[
153.2-138.24=14.96u
=32,126,355,374.08 {m FLOPs}.
]

E181 should freeze **14.96u** as the non-old saving gate unless it can recover
an exact machine-readable F86 total that supersedes the published grouped
rounding. Do not silently mix the `153.0u` and `153.2u` versions.

This correction does not change H180's CP plan: the proposed `124.6u` base is
still below the cap, but the projection margin remains tight.

## 5. Minimal pre-science identity / kill gates

These gates need no benchmark target and should run on exact-small synthetic
objects only. Failure of any gate should terminate the implementation before
an expensive scientific run.

### G1 — CP materialization / slice convention

For small `n<=8`, materialize
(sum_qlambda_q u_q^{otimes3}) and compare:

- full tensor;
- D3;
- both D21 orientations;
- repeated-index zeroing/scaling;

against the official `FactoredTensor.get_dslice` / `DSTensor` convention.

Required: float64 max-abs `<=1e-12` and deterministic replay.

**Kills:** normalization/orientation mistakes, especially the official
`(2,1)` scaling.

### G2 — linear transport identity

Materialize both

[
(W^{otimes3})K_3
quad	ext{and}quad
sum_qlambda_q(Wu_q)^{otimes3}.
]

Required max-abs `<=1e-12`.

**Kills:** orientation mistakes (`W` versus `W.T`) before any network run.

### G3 — Wick contraction identity

Compare official equal-leg K3 Wick contraction with

[
Uleftarrow d(w_1)U
]

on the same small carrier.

Required max-abs `<=1e-12`.

**Kills:** an invalid assumption that the inherited post-ReLU term remains the
same symmetric CP object under the frozen convention.

### G4 — exact birth polarization

On frozen small V29 birth factors, separately materialize B1 and B3 from the
original factored formulas and from the 4-atom / 3-atom polarization identities
above. Include nonzero V18 feedback factors and V17-regeneration inputs in the
birth-factor construction; do not test only the degenerate base case.

Required full-tensor and D3/D21 max-abs `<=1e-12`.

**Kills:** wrong symmetrization coefficients or a birth term that is not
actually covered by the proposed aggregate carrier.

### G5 — projector no-op / idempotence

For an input whose exact symmetric CP rank is already `<=R`, reprojection
must not damage representable state.

Required:

- deterministic identical replay;
- D3/D21 relative error `<=1e-12`;
- applying the projector twice changes D3/D21 by `<=1e-12`.

**Kills:** a projector whose own normalization or canonicalization injects
error even before rank pressure exists.

### G6 — exact-small overcomplete structural falsifier

Construct one frozen target-free small case by exact birth merge, so the
preprojection carrier exceeds the scaled rank cap. Materialize the exact tensor
before projection and compare the projected carrier.

Required before any target-bearing run:

- finite output;
- deterministic replay;
- pooled D21 relative RMS `<=0.015` (E180's frozen structural threshold);
- D3 finite and recorded;
- no reference target, MSE label, lambda refit, rank change or rescue.

Failure is terminal H180 structural NO-GO.

### G7 — static operation-ledger gate

Before production shape, enumerate every projection primitive and substitute
`n=1024,R=3072`. Reject without running if:

- all-in symbolic total exceeds `138.24u`;
- integration overhead exceeds `13.64u`;
- reprojection exceeds `12.64u` after the `1u` lower-order reserve;
- the graph contains a per-layer dense `R^2` interaction or an additional
  full `n x n` by `n x R` product not already counted.

This gate is deliberately stricter than “meter it later”: H180 has too little
headroom to discover an obvious cubic projection after a benchmark run.

## 6. Implementation constraints for E181

A protocol derived from this review should freeze:

1. exactly one deterministic reprojection algorithm at `R=3072`;
2. exact atom-generation/polarization equations;
3. whether (lambda) is stored explicitly or absorbed into signed/scaled
   factors, including cube-root/sign handling;
4. D3/D21 normalization against the official implementation;
5. event count: at most 15 carried transports, 14 full D21 extractions and
   15 reprojections; final layer remains V29 mean-only trim;
6. named FLOP namespaces:
   `cp_transport`, `cp_d21`, `cp_d3`, `cp_wick`, `cp_birth`,
   `cp_reproject`, `cp_normalize`, plus the preserved V29 remainder;
7. the `14.96u` conservative non-old saving gate;
8. terminal behavior: no rank sweep, alternate projector, AGO, lambda refit,
   source-age hybrid or benchmark rescue after a failed identity/cost gate.

## 7. Review decision

**IMPLEMENTATION-WORTHY ONLY IF THE REPROJECTOR FITS THE STATIC CEILING.**

The dense CP core is arithmetically feasible:

[
124.6u = 0.12168B
]

before CP integration/reprojection overhead. The remaining all-in allowance is
only `13.64u`, and a conservative projector allowance after lower-order
reserve is `12.64u` total / `0.8427u` per carried layer.

The main implementation risk is therefore not `W@U` or D21 extraction; those
are already priced. It is the deterministic compression of an exact
post-birth carrier that can transiently contain up to `10n` symmetric atoms
back to `3n` **without any dense R-by-R interaction** and without moving D21
by more than the frozen structural threshold.

E181 should kill H180 before scientific execution if G1–G7 cannot all be
specified and passed. This review authorizes no benchmark or target-bearing
run.
