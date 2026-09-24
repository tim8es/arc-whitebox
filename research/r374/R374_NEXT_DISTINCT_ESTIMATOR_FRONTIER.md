# R374 — next distinct estimator frontier

**Status:** COMPLETE  
**Final verdict:** **TERMINAL_NO_GO_NO_FINITE_RELU_CLOSED_LIFT_ZONOID_PROPAGATION_THEOREM**  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Live R320 evidence head:** `7336ffb2a88ab38ebb96177d4bc7d8bfd5dd53e1`  
**Mode:** report-only theory/method scout; no code or estimator execution

## 0. Correction of the transient branch draft

A parallel/transient R374 draft appeared on the target branch during this audit after the branch had been absent at task start.

That draft proposed **PCDF-MID**, an explicit activation-polytope output-CDF construction. R374 does **not** retain it as the final candidate because its sourced implementation explicitly enumerates activation cells / sign polytopes. Under the present task's stricter novelty firewall, that is inside the already occupied activation-region / orthant / boundary-geometry family documented by R317 and E114–E119, even though its final observable is a CDF.

The transient draft remains preserved in Git history:
- prior report blob: `69890a8662ad69aee440150c05517027db4d05d1`
- prior receipt blob: `441c0687ae8c9ef6daecbb422e6ecbbb4e39304f`
- prior branch head: `4f07ebdbda30aec981b50267fbcd65763590e1cf`

This final report replaces only the contents of the same two R374 paths. No third file is added.

## 1. Exact evidence read before selection

### Current history
- `research/history.json`
- Git blob SHA-1: `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`
- E100–E193 IDs parsed: **94**
- E100–E193 artifact records parsed: **468**

### Live R320
- head: `7336ffb2a88ab38ebb96177d4bc7d8bfd5dd53e1`
- report blob: `870c9131a4e4bc745ea6ad6510d6a45115dcc5a8`
- receipt blob: `3fa12a194b1fd33361465bef815afe1eedc81460`

### Explicit sidecar dedupe
The following were reread directly:
- R317 receipt blob `81f6adbc9cc64ab5ad3f4aaf230fe035fffa5ea5`
- R321 receipt blob `2c3d9f881d669ee924cecca106611c6c295a7243`
- R335 receipt blob `4e7d9523f1b08580358b9f2340f076977e611573`
- R347 receipt blob `9d318ea7e2d9c9727ba9c92f1bc0778d2439cf5a`
- corrected R352 receipt blob `ca4f4608a592594a321790e760aa2d7f6398476b`
- R361 receipt blob `f1c0951a382a195a367c01cddc850a9c55537aec`
- R362 receipt blob `19ae43635af9d9d69efdeaa49eb53d091c59c83a`
- R363 receipt blob `cc123000e37d8f57f0ed6f94da78ea333491f363`
- R366 receipt blob `1929547b16f922470cb81071446b3a43d3dea95c`
- R366 report blob `f2c512a04c1eb9b0d179cd04a5563e34a6f109aa`

Repository code search at the current repo found **0** hits for:
- `zonoid`
- `lift zonoid`
- `support function`
- `stop-loss`
- `convex body`
- `Hausdorff`

The R366 report contains **0** occurrences of `zonoid`, `lift zonoid`, `support function`, `Radon`, or `stop-loss`.

## 2. Dedupe conclusion

The following families are already occupied, terminally screened, or explicitly excluded here:

- Stein / JVP / control variates
- antithetic / Haar / radial Rao–Blackwell
- sampling / residual sampling / deterministic cubature / QMC
- conditional Gaussian / halfspace / orthant / mask-conditioned state
- cumulant K3/K4 / Edgeworth / higher-moment closure
- Hermite / polynomial chaos
- TT / CP / Tucker / TensorSketch / CountSketch and related low-rank tensor carriers
- characteristic-function / Hilbert propagation
- activation-boundary / boundary-flux / explicit activation-region geometry
- displacement structure
- response-aligned / adjoint / observable corrections
- source-age / window / tail compression
- randomized multilevel / telescoping
- H185 fast-arithmetic lane
- R366 white-box shallow-ridge flattening, including sampled-regression descendants

R317 is especially relevant to rejecting the transient PCDF draft: it explicitly records exact-mask / activation-region state as an occupied family and identifies E114–E119 as the exact activation-boundary geometry lineage.

## 3. Strongest confirmed internal parent

The strongest exact-panel normalized parent retained for comparison is **R209 V25**:

- path: `research/results/R209-v25-mini100.json`
- Git blob SHA-1: `0183d0570f7c9965e00e8553ffc003c313865232`
- integration commit: `20fafab5471e6ed227562c651179dd2ef331ea22`
- panel: `v2-phase2 mini:all-100`
- rows: 100
- failures: 0/100
- mean raw final-layer MSE: `2.22830349017044681e-8`
- mean adjusted score: approximately `8.170397440117225e-9`
- measured FLOPs/network: `806303721965`

R223 is same-panel but worse, so it is not substituted for R209.

R374 makes **no** leaderboard-gap, rank, or rounded-UI inference.

## 4. Exactly one genuinely distinct mechanism screened

### LZSP — lift-zonoid support propagation

Let
[
H_0=X,qquad Xsim N(0,I_n),
]
and for the zero-bias ReLU network
[
H_ell=ho(W_ell H_{ell-1}),qquad ho(t)=max(0,t),
]
with (n=1024), (L=16).

For an integrable random vector (Hinmathbb R^n), define its **lift zonoid**
[
K_H=mathbb E,[,0,(1,H),]subsetmathbb R^{n+1},
]
the Aumann expectation of the random segment from (0) to ((1,H)).

Its support function satisfies
[
oxed{
h_{K_H}(a,u)=mathbb E,(a+u^	op H)_+.
}
]

This is the central estimator identity.

If (w_{ell,i}^	op) is row (i) of (W_ell), then
[
oxed{
mathbb E[H_{ell,i}]
=
h_{K_{H_{ell-1}}}(0,w_{ell,i}).
}
]

Therefore an exact lift-zonoid state would yield each next-layer mean by support queries only.

### Why LZSP is genuinely different

LZSP does **not** approximate the original deep function by a shallow network as R366 did.

It does not store:
- moments/cumulants,
- Hermite coefficients,
- a characteristic function,
- activation masks/boundaries,
- tensor ranks,
- sampled network outputs.

Its state is a convex body representing the **entire hidden-vector probability law** through all one-dimensional stop-loss transforms.

Koshevoy–Mosler prove that the lift zonoid uniquely determines the underlying distribution. Their paper also notes that the distribution can be recovered from the support function by Radon inversion.

That makes the continuum representation exact and distribution-complete.

## 5. Primary-source derivation

### Koshevoy & Mosler 1998

Gleb Koshevoy and Karl Mosler,  
**“Lift zonoids, random convex hulls and the variability of random vectors,”**  
*Bernoulli* 4(3), 377–399 (1998).  
DOI: `10.2307/3318721`  
Primary PDF: https://wisotypo3.uni-koeln.de/sites/statistik/pdf_publikationen/1998_KoshevoyM98.pdf

The source establishes:

1. for a measure (F), zonoid support functions are positive-part expectations;
2. for the lift zonoid,
   [
   h_{hat Z(F)}(p_0,p)
   =
   int max(0,p_0+langle x,pangle),dF(x);
   ]
3. the lift-zonoid map is injective: the lift zonoid uniquely determines the measure;
4. inversion can be expressed through the Radon transform of second derivatives of the support function.

Those are exactly the identities used by LZSP.

### Siegel 2025

Jonathan W. Siegel,  
**“Optimal Approximation of Zonoids and Uniform Approximation by Shallow Neural Networks,”**  
*Constructive Approximation* 62, 441–469 (2025).  
DOI: https://doi.org/10.1007/s00365-025-09712-9

For a zonoid in (mathbb R^{d+1}), the paper proves existence of (N)-summand zonotope approximations with uniform support-function error rate
[
C(d),N^{-1/2-3/(2d)}.
]

At ARC lift dimension (1025), (d=1024), so the exponent is
[
alpha
=
rac12+rac{3}{2048}
=
0.50146484375.
]

This is useful evidence that finite support-function approximation is mathematically legitimate.

It does **not** supply the missing ReLU pushforward closure or an ARC-scale constructive cost/error theorem.

## 6. Exact estimator and error guarantee

Suppose a candidate can construct a convex approximation
[
widetilde K_{L-1}
]
to the true penultimate lift zonoid satisfying a certified Hausdorff bound
[
d_H(widetilde K_{L-1},K_{H_{L-1}})ledelta.
]

Define
[
widehatmu_j
=
h_{widetilde K_{L-1}}(0,w_{L,j}).
]

Because Hausdorff distance bounds support-function error,
[
|h_K(p)-h_{widetilde K}(p)|
le
delta|p|_2,
]
hence
[
|widehatmu_j-mu_j|
le
delta|w_{L,j}|_2.
]

Therefore the final-layer mean MSE has the deterministic certificate
[
oxed{
mathrm{MSE}_{m final}
le
delta^2,
rac{|W_L|_F^2}{n}.
}
]

If (widetilde K_{L-1}=K_{H_{L-1}}), then (delta=0) and the estimator is exact, not merely unbiased.

No target means enter the estimator or the certificate.

## 7. Exact same-panel GO inequality

Let, for R209 panel row (i),

- (delta_i) be the certified Hausdorff error of the candidate penultimate lift-zonoid state;
- (S_i=|W_{L,i}|_F^2/1024);
- (C_i) be **all-in** candidate FLOPs.

A sufficient exact-panel improvement condition is

[
oxed{
rac1{100}
sum_{i=1}^{100}
delta_i^2 S_i
max!left(0.1,rac{C_i}{2^{41}}ight)
<
8.170397440117225	imes10^{-9}.
}
]

Every row must additionally satisfy:
- (C_i<2^{41});
- wall time (le120) s;
- residual wall time (le0.4) s;
- solution-process memory (le8) GB.

At the score multiplier floor, a sufficient condition becomes
[
rac1{100}sum_idelta_i^2S_i
<
8.170397440117225	imes10^{-8}.
]

Under the He law only as a planning orientation,
[
mathbb E[S_i]=2,
]
so a common (delta) would need to be on the order of
[
delta<2.021187452973774	imes10^{-4}.
]

That last number is **not** an exact same-panel gate because the actual (S_i) values were not read from the panel in R374.

## 8. Phase-2 cost and memory accounting

Official Phase-2 source blobs:
- scoring: `9cf7653a0267c4d048617c9045ac8be127f3c8bf`
- generation: `38397fae458acfd46b5642866481672c7fce6f2d`
- rounds: `c2891dae7c21f27fdcaaab239c7bfd5d8cfc0890`
- memory-limit changelog: `fb2e2ababe42c7764fad4b99681445b65c75f7ad`

Phase-2:
- width: 1024
- depth: 16
- FLOP budget: (B=2^{41}=2,199,023,255,552)
- score floor: (0.1)
- wall cap: 120 s
- residual cap: 0.4 s
- solution-process memory: 8 GB

### Finite (N)-generator lift-zonotope readout

A natural finite representation is
[
P=sum_{r=1}^N[0,g_r],
qquad g_rinmathbb R^{1025}.
]

Then
[
h_P(0,w)
=
sum_{r=1}^N
max(0,w^	op g_{r,1:}).
]

For all 1024 final output rows, the scalar multiply/add count for the dot products and accumulation is
[
oxed{
C_{m read}(N)
=
2n^2N-n
=
2,097,152N-1,024,
}
]
before comparisons/max operations and any construction/certification work.

Float32 state storage is
[
oxed{
M_{m state}(N)=4(n+1)N=4,100N {m bytes}.
}
]

Float64 doubles this.

Even granting **zero** cost to construction and certification:
- to remain at the (0.1B) score floor, support readout alone requires
  [
  Nle104,857;
  ]
- under the full (B) budget,
  [
  Nle1,048,576.
  ]

At (N=104,857), float32 state storage is (429,913,700) bytes.

At (N=1,048,576), float32 state storage is (4,299,161,600) bytes; float64 state storage is (8,598,323,200) bytes, already at/about the official memory ceiling depending on byte convention.

### If generators are pushed as pseudo-atoms

If each generator is interpreted as a discrete pseudo-sample and directly propagated through all 16 dense matrices, dense matrix-vector arithmetic alone is approximately

[
C_{m particle}
ge
16N(2n^2-n),
]

before ReLU, certification and readout.

That implies roughly:
- (Nlesssim6.6	imes10^3) at the score floor;
- (Nlesssim6.6	imes10^4) at the full budget.

More importantly, this implementation is a deterministic particle / cubature / discrete-measure propagation method and is therefore **excluded by the R374 novelty firewall**.

It is not an admissible rescue of LZSP.

## 9. Why the distinct continuum mechanism fails

The exact lift-zonoid state is complete but infinite-dimensional.

To advance one layer, one needs
[
K_{ell}
=
K_{ho(W_ell H_{ell-1})}.
]

For any direction ((a,u)),
[
h_{K_ell}(a,u)
=
mathbb E
left[
a+u^	opho(W_ell H_{ell-1})
ight]_+.
]

This is itself an expected output of a nonlinear ReLU composition.

The Koshevoy–Mosler injectivity theorem says the full previous lift zonoid determines the law, and Radon inversion can in principle recover that law. It does **not** provide a finite, polynomial-cost ReLU-closed update.

The Siegel zonotope theorem provides approximation of **one already-defined zonoid**. It does not provide an operator
[
(widetilde K_{ell-1},W_ell)
mapsto
widetilde K_ell
]
with:
- a computable error recurrence;
- finite construction complexity;
- Phase-2 memory bounds;
- no discrete-particle/cubature reduction.

Therefore the full all-in cost is
[
oxed{
C_{m all}
=
C_{m build}
+
C_{m certify}
+
C_{m read},
}
]
but the two dominant admissibility terms,
[
C_{m build},quad C_{m certify},
]
cannot be bounded from the audited theory because the required finite nonlinear closure theorem does not exist in the evidence base.

R374 does **not** set those terms to zero.

That missing bound is the terminal gate.

## 10. Exact missing theorem

Re-entry requires a source-backed or independently proved deterministic finite-state operator (Phi_W) such that, for a certified approximation
[
d_H(widetilde K,K_H)ledelta,
]
it produces (widetilde K') satisfying

[
oxed{
d_H!left(
widetilde K',
K_{ho(WH)}
ight)
le
A(W)delta+	au(N,W)
}
]

with explicit computable (A,	au), **without**:
- sampled network evaluations,
- discrete particle/cubature pushforward,
- activation-region enumeration,
- Hermite/CF/moment/tensor state.

The theorem must also supply
[
C_Phi(N,1024),qquad M_Phi(N,1024)
]
and constants strong enough that after 15 hidden-state updates the R209 same-panel GO inequality in Section 7 is satisfied while all Phase-2 limits hold.

No such theorem was found.

## 11. Preregistered cheapest falsifier

### F374-LZ-CLOSURE — zero-run theorem falsifier

This is the cheapest possible falsifier and is **not executed**.

A future re-entry submission must provide, before any code:

1. the finite-state definition;
2. exact nonlinear update (Phi_W);
3. proof of the Hausdorff error recurrence above;
4. complete (C_Phi) and memory formula;
5. proof that the representation is not merely a discrete pseudo-sample/cubature state;
6. constants that make the exact R209 inequality satisfiable.

### GO

All six items are present, and their constants leave a nonempty region of ((N,delta,C)) satisfying:
[
rac1{100}sum_i
delta_i^2 S_i
max(0.1,C_i/2^{41})
<
8.170397440117225	imes10^{-9},
]
with all Phase-2 limits.

### NO-GO

Any of:
- no finite ReLU-closed update;
- no composable Hausdorff error bound;
- finite realization reduces to particle/cubature/sampling;
- construction/certification cost cannot be bounded;
- derived constants cannot satisfy the same-panel score inequality.

Current result: **NO-GO at item 2/3/4**.

No numerical falsifier is justified before this gate is repaired.

## 12. Scientific conclusion

Exactly one genuinely distinct mechanism survived dedupe long enough for a mathematical screen:

> **LZSP — lift-zonoid support propagation.**

It has a strong theoretical attraction:
- exact continuum state;
- exact ReLU mean as a support query;
- direct deterministic final-mean error bound from Hausdorff error;
- zero dependence on targets.

But it does not become a finite Phase-2 estimator.

The missing object is not another approximation constant. It is a **finite ReLU-closed lift-zonoid propagation theorem with composable error and construction cost**.

The obvious finite generator pushforward is a discrete particle/cubature method and is excluded.

Therefore:

**TERMINAL_NO_GO_NO_FINITE_RELU_CLOSED_LIFT_ZONOID_PROPAGATION_THEOREM.**

No formal control-queue job is proposed because the candidate does not pass the pre-execution theorem gate.

## 13. Execution accounting

- code created or run: **NO**
- estimator implementation: **NO**
- synthetic runs: **0**
- benchmark runs: **0**
- Actions runs: **0**
- downloads: **0**
- dependency installs: **0**
- paid resources: **NO**
- private/holdout/full access: **NO**
- submissions: **0**
- main edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**
- R320 edits: **0**
- historical verdicts changed: **NO**
