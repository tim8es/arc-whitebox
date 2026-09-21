# E155 PRIMARY-SOURCE SUPPORT — clean-room angular/radial K4

Date: 2026-09-21  
Branch: `research/e155-cleanroom-angular-k4-support-20260921`  
Base: `main@2af54da98045e36b37330e1f7c9f36f0943f3661`

## Scope and clean-room boundary

This lane checks one angular/radial K4 mechanism against the official ARC reference
equations and one public Phase-2 implementation. It does not reuse E151 code,
workflow, run artifacts, Strassen arithmetic, or its failed execution path.

This is primary-source support only. No estimator implementation, benchmark target,
public mini, scorer, holdout, full suite, submission, or scientific run is authorized
here. Execution remains blocked until an owner freezes a parent estimator and an
owner protocol.

Labels used below:
- **ARC PRIMARY** — official ARC source/code.
- **PUBLIC IMPLEMENTATION EVIDENCE** — open third-party implementation/receipts.
- **DERIVATION** — algebra derived from those definitions.
- **HYPOTHESIS** — not established by source evidence.

## Pinned sources

### Official ARC

Repository:
https://github.com/alignment-research-center/mlp_cumulant_propagation

Audited commit:
`93d091a4c26c042bfffa28f2e76a81bc0aba94bb`

Pinned files:
- `src/mlp_kprop/kprop_harmonic.py` — blob `7e901ce069baf40e2bdcbfb325a3c1b2e93b6007`
- `src/mlp_kprop/factor_k4.py` — blob `a63b523e24a4cde520eed3e4ee443f61308ebcec`
- `src/mlp_kprop/wick.py` — blob `2947a40c33fac64441dbc5b180bfe6a865cca452`
- `src/mlp_kprop/tensor_utils.py` — blob `7133c29ef60d7ea0f0a65198a3dcfa747f6a521b`
- `src/mlp_kprop/cumulants.py` — blob `03de57bd86ae680458054edfaad48a1e85e206fd`

Official overview:
https://www.alignment.org/blog/mechanistic-estimation-for-wide-random-mlps/

The official code says:
1. linear cumulant propagation contracts every tensor leg with the weight matrix;
2. the nonlinear step is a Wick expansion around a Gaussian with matching mean and
   variance, followed by cumulant conversion/projection;
3. `FactoredTensor4` represents
   `T_ijkl = Sym(sum_r A_ijr B_klr)`;
4. `FactoredTensor4.contract_W` maps both matrix factors by `A -> W A W^T`;
5. the ReLU Wick coefficients are
   `E[d^k ReLU(Z)^p]` under the matching Gaussian.

These are the reference equations used below. ARC's code also explicitly warns that
factored AUGMENT drops some leading-order diagrams; E155 therefore does not claim
that a cheap K4 carrier makes full K4 propagation exact.

### Public implementation evidence

Repository:
https://github.com/barnobarno666/ARC-White-Box-Estimation-2026

Audited commit:
`1558651e49d68b40821930f0f9c9a059f33d3a52`

Pinned artifacts:
- `phase8report.md` — blob `3087457e972c0ea4692aeb9070c2a456cd1aed60`
- `candidates/estimator_p8_final.py` — blob `fc743f80329c00cf2f0985333918496c006af2a2`
- `candidates/estimator_p8_a1_a_k3c65.py` — blob `17faa6cfe84f26c28d8238c908e84e9ab3028c6e`

The public report records:
- Gaussian K2 raw `4.1257e-6`;
- angular K2 with scalar K4 **off** raw `3.4236e-6` (-17.02%);
- Gaussian K2+scalar-K4 raw `4.0639e-6`;
- angular K2+scalar-K4 raw `3.4303e-6`;
- Gaussian K3C65 raw `3.7859e-8`;
- angular K3C65 with scalar K4 on raw `3.4859e-8` (-7.92%).

The K2 ablation is important: angular K2 without recurrent scalar K4 is slightly
better than angular K2+scalar-K4 (`3.4236e-6` versus `3.4303e-6`, about 0.196%
lower error). Therefore the public evidence supports the **angular gauge**, but does
not establish that recurrent scalar K4 is the cause of the gain. The K3 result also
does not isolate K4 because its angular variant keeps scalar K4 on.

## Exact angular/radial identities

Let
[
Xsim N(0,I_n),qquad X=(R/sqrt n)Y,
]
where (Y) is uniform on the sphere of radius (sqrt n), and (R=|X|_2)
is independent of (Y).

For every zero-bias ReLU MLP (f), positive homogeneity gives
[
f(X)=(R/sqrt n)f(Y),
qquad
E[f(X)]=a_1(n)E[f(Y)],
]
with
[
a_p(n)=E[(R/sqrt n)^p]
      =(2/n)^{p/2}rac{Gamma((n+p)/2)}{Gamma(n/2)}.
]

In particular (a_2=1), (a_4=(n+2)/n).

The angular input has
[
E[Y_iY_j]=delta_{ij}
]
and fourth moment
[
E[Y_iY_jY_kY_l]
=rac{n}{n+2}
(delta_{ij}delta_{kl}+delta_{ik}delta_{jl}+delta_{il}delta_{jk}).
]
Hence its exact fourth cumulant is
[
K^{Y}_{4,ijkl}
=kappa_n
(delta_{ij}delta_{kl}+delta_{ik}delta_{jl}+delta_{il}delta_{jk}),
qquad
kappa_n=-rac{2}{n+2}.
]
Thus (K^Y_{4,iiii}=-6/(n+2)).

## Smallest exact K4 carrier

Let the first linear preactivation be (Z=WY) and define
[
M=WW^T.
]
By multilinearity of cumulants,
[
K^Z_{4,abcd}
=kappa_n(
M_{ab}M_{cd}+M_{ac}M_{bd}+M_{ad}M_{bc}).
]

This is a full, generally dense K4 tensor, but it has an **exact one-pair
matrix-factor representation** in ARC's `FactoredTensor4` convention:
[
A=M,qquad B=3kappa_n M,
]
because ARC's `Sym` averages the three pairings for symmetric (A,B).

This is not a low-rank K3 hypothesis and not a low-rank matrix approximation:
(M) may have full rank. The compression is an exact identity special to the
isotropic angular input K4.

The only diagonal slices required by the public K1/K2/K3 birth formulas are
[
D4_i=K^Z_{4,iiii}=3kappa_n M_{ii}^2
=-rac{6}{n+2}M_{ii}^2,
]
and
[
D22_{ij}=K^Z_{4,iijj}
=kappa_n(M_{ii}M_{jj}+2M_{ij}^2).
]

These are exactly the `s4` and `s22` layer-0 formulas present in the pinned
public angular implementation.

## What is exact and what is not

**Exact:**
- Gaussian radial/angular factorization and final (a_1) conversion;
- angular covariance and K4 tensor;
- dense linear transport of that input K4;
- the one-pair matrix-factor carrier ((M,3kappa M));
- D4 and D22 readout;
- ARC ReLU Wick coefficients and the selected first-birth K4 terms once their
  term set is frozen.

**Not exact / not established:**
- replacing the post-ReLU K4 by one scalar `c4`;
- propagating that scalar through all later layers;
- dropping all post-first-ReLU K4 while claiming the whole estimator is exact;
- any claim that angular K4 improves a leader-grade raw MSE.

The public K2 ablation is evidence against treating recurrent scalar K4 as the
essential mechanism. It is not evidence against the exact input K4 source itself.

## E155 candidate: AIK4-1

**AIK4-1 = Angular Isotropic K4, one birth only.**

This is the smallest clean-room candidate that preserves the exact angular K4
information without introducing a recurrent K4 state.

For a future owner-frozen parent that already computes the first-layer Gram/covariance
matrix (M=WW^T):

1. switch the input representation to the exact angular gauge;
2. use the exact final radial conversion (a_1(n));
3. at the first preactivation only, form exact (D4) and (D22) from (M);
4. inject only those K4 contributions into the parent's first nonlinear K1/K2/K3
   birth terms using the ARC Wick coefficients;
5. after that first nonlinearity, carry **no K4 state at all**; continue the
   unchanged owner-frozen K1/K2/K3 parent.

This deliberately differs from the public implementation: the public code updates a
scalar `c4` after every nonlinearity, whereas AIK4-1 has no recurrent scalar K4.

### Why this is the smallest candidate worth falsifying

- Angular K4 itself is known exactly and needs no fit.
- Its first linear transport is already encoded by (M); no K4 materialization is
  needed.
- D4/D22 are (O(n^2)) elementwise readouts.
- No new matrix multiplication is required if the parent already owns (M).
- The public evidence says angularization can improve raw error, while its K2
  ablation does not support recurrent scalar K4. One-birth-only is therefore the
  minimal separation test between the exact angular source and the unsupported
  recurrence.

This is a **HYPOTHESIS**, not a raw-MSE result.

## Conservative production cost envelope

AIK4-1 is admissible only for a parent that already materializes (M=WW^T) at the
first layer. A conservative implementation-independent allowance for all extra
first-birth elementwise work, Wick multiplications, conversions, and bookkeeping is
[
C_{m overlay}(n)le 20n^2+100n.
]

At (n=1024):
[
C_{m overlay}le 21{,}073{,}920 {m FLOPs}
=9.5833092928	imes10^{-6}cdot 2^{41}.
]

Therefore a future owner may freeze AIK4-1 only if the measured all-in parent cost is
at most
[
0.135-9.5833092928	imes10^{-6}
=0.1349904166907072
]
of the challenge budget, or if a tighter complete flopscope accounting proves the
combined candidate below 0.135.

If (M) is not already present, this support note does not authorize adding a new
dense Gram multiply; that would be a different costed candidate.

## Support conclusion

[
oxed{	ext{AIK4-1 is admissible for one target-free owner-frozen falsifier only}}
]

The exact representation identity survives the ARC reference-equation check. The
public evidence supports angularization but **does not validate recurrent scalar
K4**. The smallest clean-room hypothesis is therefore the exact isotropic input-K4
source injected once, with no recurrent K4 state.

No execution is authorized by this note.
