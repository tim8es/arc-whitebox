# E159 OWNER PROTOCOL — published angular/radial K2 ablation

Status: **FROZEN BEFORE IMPLEMENTATION / ONE TARGET-FREE RUN AUTHORIZED AFTER ARM**  
Date: 2026-09-21  
Experiment: `ARC-E159-PUBLISHED-ANGULAR-ABLATION-20260921`

## Research question

Primary-source reconstruction shows that the reported full-K3 ~7.92% improvement
came from toggling the public `is_angular` switch while `use_k4=True` in both
arms. That comparison does not causally isolate K4.

The published K2 four-arm ablation does isolate the mechanisms. E159 therefore
falsifies one narrower hypothesis:

[
H_{159}: 	ext{the radial/angular gauge alone improves a deterministic K2 closure
on an exact target-free synthetic reference.}
]

Recurrent scalar K4 is reconstructed as a separate diagnostic. It cannot rescue a
failed gauge-only gate.

## Clean-room firewall

Allowed:
- formulas reconstructed from the pinned public implementation evidence in
  `E159_PRIMARY_SOURCE_NOTE.md`;
- numpy float64 synthetic arithmetic;
- analytic Gaussian radial/angular identities;
- exact activation-sector integration in 2D;
- dense verifier-only angular K4 materialization on small fixtures.

Forbidden:
- imports, copies, or execution of E151/E154/E157 code/workflows/artifacts;
- public benchmark networks, predictions, targets, labels, mini data;
- scorer, holdout, full suite, submission;
- benchmark-target fitting or post-result fitting;
- sampling or Monte Carlo reference;
- Strassen;
- seed/rank/threshold sweep;
- second scientific run or rescue after failure.

## Frozen four reconstructed arms

All four use the same K2 closure and weights.

1. `G-K2`: Gaussian state, scalar K4 off.
2. `A-K2`: angular state, scalar K4 off.
3. `G-K2K4`: Gaussian state, recurrent scalar K4 on, initial `c4=0`.
4. `A-K2K4`: angular state, recurrent scalar K4 on, initial
   [
   c4=-6/(n+2).
   ]

For small synthetic width (n), use the exact radial factor
[
a_1(n)=sqrt{2/n}exp(lgamma((n+1)/2)-lgamma(n/2)).
]
At width 1024 this agrees with the public `A1_CONST` to its float32 precision.

### Common K2 propagation

Input:
[
mu_0=0,qquad C_0=I.
]

For an internal linear layer:
[
mu^- = Wmu,qquad C^-=WCW^T,qquad M=WW^T.
]

With K4 off, the incoming K3/K4 slices are zero. Let
[
v=operatorname{diag}C^-,qquad C_o=C^- - operatorname{diag}(v),
]
and (w_{k,p}=E[partial^k ReLU(Z)^p]) under the matching marginal Gaussian.

The marginal powers are
[
P_p=w_{0,p}
]
and the off-diagonal second raw cross moment is
[
P_{11}
=C_o(w_{1,1}otimes w_{1,1})
+rac12 C_o^{odot2}(w_{2,1}otimes w_{2,1}).
]

Then
[
mu=P_1,qquad
operatorname{diag}C=P_2-P_1^2,qquad
C_{ij}=P_{11,ij} (i
e j).
]

The terminal layer computes only the marginal mean.

### Angular/radial gauge

Only for the angular arms, immediately after the first nonlinear state update:
[
muleftarrow mu/a_1,
]
[
Cleftarrow C-(a_1^{-2}-1)mu_Gmu_G^T,
]
where (mu_G) is the pre-conversion first-layer mean.

Every reported/final angular mean is converted back by
[
mu_G^{out}=a_1mu_A^{out}.
]

This is the clean-room reconstruction of the public gauge switch.

### Recurrent scalar-K4 diagnostic

For K4 arms only:
[
s4=c4,operatorname{diag}(M)^2,
]
[
s22=rac{c4}{3}operatorname{zeroDiag}
left(d,d^T+2M^{odot2}ight),qquad d=operatorname{diag}M.
]

The public fourth-order Wick additions are reconstructed in (P_1,ldots,P_4),
(P_{11}), and (P_{21}). After moment-to-cumulant conversion, the scalar state is
updated by the published isotropic projection
[
c4leftarrow rac{3}{n(n+2)}
left(sum_i K4_i+sum_i r22_iight).
]

This scalar is recurrent. It is deliberately distinct from E157's one-birth K4.

## Frozen fixtures

One external scientific run contains all fixtures plus an in-process replay.

### F0 exact2d/depth8

- width/input 2;
- depth 8;
- zero bias;
- seed `159002`;
- PCG64 Gaussian weights scaled by (sqrt{2/n});
- float64.

Reference: exact sector enumeration on the unit circle. On each sector the zero-bias
ReLU network is linear in ((cos	heta,sin	heta)); integrate analytically and
multiply the angular mean by (E[chi_2]=sqrt{pi/2}). No sampling.

All four reconstructed arms are evaluated against this same exact Gaussian mean.

### F1 dense32/depth8

- width/input 32;
- depth 8;
- seed `159032`;
- Gaussian weights scaled by (sqrt{2/n}).

Identity/replay fixture only.

### F2 adversarial16/depth8

- width/input 16;
- depth 8;
- seed `159016`;
- each layer (Q_L diag(g) Q_R^T);
- QR signs canonicalized;
- (g) linearly spaced 0.5..1.5 and RMS-rescaled to (sqrt2).

Identity/replay fixture only.

## Mandatory identities

1. radial homogeneity:
   [
   f(x)=|x|/sqrt n, f(sqrt n,x/|x|)
   ]
   max relative error <= `2e-12`.
2. first-layer angular mean conversion versus exact radial identity <= `2e-12`.
3. first-layer angular covariance conversion versus exact raw-second-moment identity
   <= `2e-12`.
4. for K4-on angular state, layer-0 `s4` and `s22` versus dense exact angular
   K4 slices <= `2e-12`.
5. K4-off arms contain no `c4/s4/s22` arithmetic.
6. all four output arrays and metrics replay bitwise identically.

## Scientific gate and attribution

Define exact-2D MSEs (E_G,E_A,E_{GK4},E_{AK4}).

Frozen primary gate:
[
E_Ale0.98E_G.
]

Report, without post-hoc threshold changes:
[
Delta_{m gauge}=E_A-E_G,
]
[
Delta_{m K4|A}=E_{AK4}-E_A,
]
[
Delta_{m K4|G}=E_{GK4}-E_G.
]

K4 diagnostics do not rescue a failed primary gate. If the primary gate fails, E159
is terminal NO-GO even if a K4 arm improves.

## Complete production cost gate

Budget:
[
B=2^{41}.
]

Production width/depth:
[
n=1024,quad d=16.
]

For one reconstructed estimator arm, the exact dense GEMM envelope is
[
C_{m GEMM}=(6d-8)n^3=88n^3.
]

This counts:
- first internal layer: one (WW^T) GEMM;
- each of the next (d-2) internal layers: (WC), ((WC)W^T), and (WW^T);
- terminal layer: one (WC) GEMM.

A deliberately conservative complete blanket reserve covers every remaining
matvec, reduction, special-function Wick evaluation, K4 recurrence, elementwise
(n^2) expression, symmetrization, copy/materialization, and scalar bookkeeping:
[
C_{m nonGEMM}le10000,d,n^2+10000,n^2.
]

Therefore the frozen all-in upper bound for the most expensive K4 arm is
[
C_{m all}
=88n^3+10000dn^2+10000n^2
=272747200512
]
FLOPs, or
[
C_{m all}/B=0.12403106689453125<0.135.
]

The four research arms are diagnostic alternatives, not four computations inside a
production estimator. The cost gate applies to the maximum complete cost of any
single reconstructed arm. The exact reference and dense verifier tensors are
verifier-only and are not production estimator arithmetic.

No Strassen credit is used.

## Decision

All identity, replay, firewall, primary scientific, and cost gates pass:
[
oxed{	ext{E159 TARGET-FREE SCIENTIFIC GO — ANGULAR GAUGE}}
]

Any mandatory failure or execution exception:
[
oxed{	ext{E159 TERMINAL NO-GO}}
]

Exactly one external scientific run is authorized after implementation hashes and
the immutable arm are frozen. No rerun, rescue, seed replacement, or sweep.
