# E160 PRIMARY-SOURCE SUPPORT — audit of public angular/radial gain vs E154/E157

Date: 2026-09-21  
Branch: `research/e160-primary-source-angular-support-20260921`  
Parent: `research/e157-owner-aik4-onebirth-20260921@2c23f27f17560829111ac51a30e0b70d592b790f`

Status:

**PRIMARY-SOURCE SUPPORT ONLY / NO OWNER PROTOCOL / NO EXECUTION AUTHORIZED.**

This note audits the public Phase-8 angular/radial implementation and the
official ARC cumulant-propagation equations against the terminal E154 and E157
results.

The purpose is attribution:

> Is the public reported angular gain evidence for recurrent K4 correction, or
> is it primarily evidence for a different state gauge / baseline / closure?

Conclusion:

**The public evidence does not identify recurrent K4 as the cause of the gain.**
The strongest public ablation shows a large angular gain with scalar K4 entirely
disabled. The public angular estimator also changes the K1/K2 state gauge and
final radial readout, while its recurrent scalar-K4 rule is a third-party
projection closure rather than an official ARC identity.

E154 and E157 therefore falsify two particular K4 hypotheses, but neither
falsifies the public angular-gauge effect itself.

No run is authorized by this note.

---

## 1. Source classes and labels

Labels below:

- **ARC PRIMARY** — official ARC paper/code/blog.
- **PUBLIC PRIMARY** — public third-party Phase-8 implementation/report/ledger.
- **PROJECT RECEIPT** — immutable E154/E157 result.
- **DERIVATION** — algebra derived from primary definitions.
- **HYPOTHESIS** — admissible future clean-room mechanism, not an executed result.

### 1.1 ARC PRIMARY

Paper:

<https://arxiv.org/abs/2605.05179>

Title:

*Estimating the expected output of wide random MLPs more efficiently than sampling*.

Official overview:

<https://www.alignment.org/blog/mechanistic-estimation-for-wide-random-mlps/>

Official repository:

<https://github.com/alignment-research-center/mlp_cumulant_propagation>

Audited commit:

`93d091a4c26c042bfffa28f2e76a81bc0aba94bb`.

Pinned code blobs:

- `src/mlp_kprop/factor_k4.py`  
  blob `a63b523e24a4cde520eed3e4ee443f61308ebcec`;
- `src/mlp_kprop/wick.py`  
  blob `2947a40c33fac64441dbc5b180bfe6a865cca452`;
- `src/mlp_kprop/kprop_harmonic.py`  
  blob `7e901ce069baf40e2bdcbfb325a3c1b2e93b6007`;
- `src/mlp_kprop/cumulants.py`  
  blob `03de57bd86ae680458054edfaad48a1e85e206fd`.

### 1.2 PUBLIC PRIMARY

Repository:

<https://github.com/barnobarno666/ARC-White-Box-Estimation-2026>

Audited commit:

`1558651e49d68b40821930f0f9c9a059f33d3a52`.

Pinned artifacts:

- `phase8report.md`  
  blob `3087457e972c0ea4692aeb9070c2a456cd1aed60`;
- angular K2, scalar K4 off:  
  `candidates/estimator_p8_a1_a_k2.py`  
  blob `be22c6b881bb154867ca66ba7c288d349cb6d093`;
- Gaussian K2, scalar K4 off:  
  `candidates/estimator_p8_a1_g_k2.py`  
  blob `116244b48085e3c4c7447cdca1354ef43a990212`;
- angular K2+scalar-K4:  
  `candidates/estimator_p8_a1_a_k2k4.py`  
  blob `67a4bee83517314cb122fe2691826ec910cdb21d`;
- Gaussian K2+scalar-K4:  
  `candidates/estimator_p8_a1_g_k2k4.py`  
  blob `384abab18ff39c11a7ce573276576bf091442f74`;
- angular K3C65+scalar-K4:  
  `candidates/estimator_p8_a1_a_k3c65.py`  
  blob `17faa6cfe84f26c28d8238c908e84e9ab3028c6e`;
- Gaussian K3C65+scalar-K4:  
  `candidates/estimator_p8_a1_g_k3c65.py`  
  blob `dbf1f6b662208a2624272c8c179cae86fbdde5d7`.

The public report also points to a Phase-8 ledger with per-candidate FLOP
receipts and settings. The audited entries are reproduced numerically below.

### 1.3 PROJECT RECEIPTS

E154 terminal receipt:

- branch `research/e154-clean-angular-radial-k4-20260921`;
- terminal commit
  `c599aa6deb7fc7630951be88bac9e0ce1afbe949`;
- receipt blob
  `4d89b9ac96f59b1dc0d357d414e8b6e26d454ada`.

E157 terminal receipt:

- branch `research/e157-owner-aik4-onebirth-20260921`;
- terminal commit
  `2c23f27f17560829111ac51a30e0b70d592b790f`;
- receipt blob
  `8e7147db9687a7b9043fa28e981de5d171c8f56d`.

---

## 2. Exact angular/radial identities

### 2.1 Gaussian radius / sphere direction

Let

[
Xsim N(0,I_n),
qquad
R=|X|_2,
qquad
Y=sqrt n,X/|X|_2.
]

Then exactly

[
X=rac{R}{sqrt n}Y,
]

with (R) independent of (Y), and (Y) uniform on the sphere of radius
(sqrt n).

Define

[
a_p(n)
=
mathbb E[(R/sqrt n)^p]
=
left(rac{2}{n}ight)^{p/2}
rac{Gamma((n+p)/2)}{Gamma(n/2)}.
]

In particular,

[
a_2=1,
qquad
a_4=rac{n+2}{n}.
]

For a zero-bias ReLU network (F), positive homogeneity gives

[
F(X)=rac{R}{sqrt n}F(Y).
]

Therefore

[
mathbb E[F(X)]
=
a_1(n),mathbb E[F(Y)].
]

This is exact and independent of any K4 approximation.

### 2.2 Exact K1/K2 gauge conversion

Let

[
H_G = F(X),
qquad
H_A = F(Y),
qquad
S=R/sqrt n.
]

Then (H_G=S H_A), (Sperp H_A), (mathbb E[S]=a_1), and
(mathbb E[S^2]=1).

If

[
m_G=mathbb E[H_G],
qquad
C_G=operatorname{Cov}(H_G),
]

then exactly

[
m_A=rac{m_G}{a_1},
]

and

[
C_A
=
C_G-
left(rac{1}{a_1^2}-1ight)m_Gm_G^T.
]

This is precisely the structural transform implemented in the public angular
code after layer 0:

- divide the mean by `A1_CONST`;
- subtract
  ((A1^{-2}-1),m m^T) from covariance;
- report Gaussian-input predictions by multiplying the angular mean by
  `A1_CONST`.

This transform exists even when scalar K4 is disabled.

### 2.3 Exact angular input K4

For (Y) uniform on the radius-(sqrt n) sphere,

[
mathbb E[Y_iY_j]=delta_{ij},
]

and

[
operatorname{Cum}_4(Y_i,Y_j,Y_k,Y_l)
=
kappa_n
(
delta_{ij}delta_{kl}
+delta_{ik}delta_{jl}
+delta_{il}delta_{jk}
),
]

where

[
kappa_n=-rac{2}{n+2}.
]

Thus

[
K_{4,iiii}=-rac{6}{n+2}.
]

For the first linear preactivation (Z=WY), define

[
M=WW^T
]

in the public row-weight convention. Then

[
K^Z_{4,abcd}
=
kappa_n
(
M_{ab}M_{cd}
+M_{ac}M_{bd}
+M_{ad}M_{bc}
).
]

The exact repeated-index slices are

[
D4_i
=
3kappa_n M_{ii}^2
=
-rac{6}{n+2}M_{ii}^2,
]

and

[
D22_{ij}
=
kappa_n
(
M_{ii}M_{jj}
+2M_{ij}^2
).
]

E157 verified these identities, including the dense K4 and selected Wick-term
parities, to floating-point precision.

---

## 3. Official ARC equations versus scalar `c4`

### 3.1 ARC linear transport

**ARC PRIMARY.**

ARC propagates cumulants through a linear layer by contracting every tensor leg
with the weight matrix.

For the factorized fourth cumulant, official `FactoredTensor4` represents

[
T_{ijkl}
=
operatorname{Sym}
left(
sum_r A_{ijr}B_{klr}
ight).
]

Its official `contract_W` maps both matrix factors by the dense linear
contraction corresponding to

[
Amapsto WAW^T,
qquad
Bmapsto WBW^T.
]

For the special isotropic angular input K4 above, the first transported K4 has
an exact one-pair ARC carrier:

[
A=M,
qquad
B=3kappa_n M.
]

Because ARC symmetrization averages the three matrix pairings,

[
operatorname{Sym}(Motimes 3kappa_n M)
=
kappa_n
(M_{ab}M_{cd}+M_{ac}M_{bd}+M_{ad}M_{bc}).
]

This exact identity is what E157 verified.

### 3.2 ARC nonlinear step

**ARC PRIMARY.**

Official `nonlin_kprop`:

1. expands around a Gaussian with matching mean and variance;
2. uses Wick coefficients
   [
   w_{k,p}
   =
   mathbb E_{Zsim N(mu,v)}
   [partial^koperatorname{ReLU}(Z)^p];
   ]
3. sums the retained diagram terms;
4. converts power cumulants back to ordinary cumulants;
5. projects to the configured harmonic/cumulant representation.

That is a tensor/diagonal-slice cumulant closure.

It is **not** an official equation saying that post-ReLU K4 remains an
isotropic scalar multiple of
(
C_{ij}C_{kl}+C_{ik}C_{jl}+C_{il}C_{jk}
).

The official factorized K4 code additionally warns that factorized AUGMENT is
not equivalent to the full unfactorized AUGMENT algorithm: some leading-order
diagrams do not admit the cheap factorization and are dropped.

Therefore a recurrent one-scalar K4 state is a projection approximation, not
an ARC identity.

---

## 4. What the public implementation actually changes

### 4.1 Public angular K2 with K4 disabled

In `estimator_p8_a1_a_k2.py`:

- `is_angular = True`;
- `use_k4 = False`;
- `k3_mode = "zero"`;
- hence `c4=0`, `s4=0`, and `s22=0`.

Nevertheless the implementation still performs the angular gauge conversion:

[
mleftarrow m/a_1,
]

[
Cleftarrow
C-(a_1^{-2}-1)mm^T
]

after layer 0, and reports

[
m_G^{m out}=a_1m_A.
]

Thus its difference from Gaussian K2 is not a K4 correction.

### 4.2 Public recurrent scalar K4

With `use_k4=True`, the public implementation uses

[
s4_i=c4,M_{ii}^2,
]

and

[
s22_{ij}
=
rac{c4}{3}
left(
M_{ii}M_{jj}+2M_{ij}^2
ight)
]

for the current linear covariance/metric matrix (M).

After the nonlinear cumulant conversion, it computes a new scalar

[
c4_{m next}
=
rac{3}{n(n+2)}
left(
sum_i k4_i+t22_{m sum}
ight),
]

where `t22_sum` is constructed from the post-ReLU covariance/K3/K22-related
terms in lines 313--332 of the audited angular K3C65 implementation.

This is a **recurrent isotropic scalar projection of the current fourth-order
state**.

It is neither:

- E154's fixed memoryless rule
  [
  K4_{iiii}=-6v_i^2/(n+2)
  ]
  at every layer; nor
- E157's one-birth exact input K4 followed by destroying K4 forever.

### 4.3 Public K3 closure is also different

The reported (-7.92%) K3 gain compares:

- Gaussian `k3_mode="c65"`, scalar K4 on;
- angular `k3_mode="c65"`, scalar K4 on.

The retained K3 source-bank/compression schedule remains active.

Therefore that pair measures an angular-state change **inside a particular
high-cost K3 closure**. It does not isolate K4.

---

## 5. Public ablation attribution

The public Phase-8 ledger gives:

| candidate | raw MSE | FLOPs |
|---|---:|---:|
| Gaussian K2, K4 off | (4.1256859002	imes10^{-6}) | 95,869,616,160 |
| Angular K2, K4 off | (3.4236054451	imes10^{-6}) | 95,874,876,448 |
| Gaussian K2, scalar K4 on | (4.0639238716	imes10^{-6}) | 96,986,797,088 |
| Angular K2, scalar K4 on | (3.4302800226	imes10^{-6}) | 96,992,057,376 |
| Gaussian K3C65, scalar K4 on | (3.7858506108	imes10^{-8}) | 1,730,262,343,006 |
| Angular K3C65, scalar K4 on | (3.4859498399	imes10^{-8}) | 1,730,267,603,294 |

### 5.1 Angular gauge effect with K4 exactly off

[
rac{3.4236054451e-6}{4.1256859002e-6}
=
0.8298269737.
]

So angular K2 with **no K4 at all** reduces raw MSE by

[
17.0173%.
]

This is direct evidence that recurrent K4 is not necessary for the reported
angular effect.

### 5.2 Scalar K4 on the angular K2 parent

[
rac{3.4302800226e-6}{3.4236054451e-6}
=
1.0019495756.
]

Turning recurrent scalar K4 on makes this angular K2 result approximately

[
0.195%
]

worse.

Thus this public ablation is evidence **against** attributing the main angular
K2 gain to recurrent scalar K4.

For comparison, on the Gaussian K2 baseline, scalar K4 improves raw MSE by
about (1.50%). Its sign is baseline-dependent.

### 5.3 Full K3 pair

The angular K3C65 result is better than the Gaussian K3C65 result by

[
7.9216%.
]

But scalar K4 is enabled in **both** members of this pair, so this comparison
cannot identify K4 as the cause.

The changed representation includes the angular K1/K2 state gauge and radial
readout while keeping the C65 K3 closure.

---

## 6. Relation to E154 failure

E154 tested:

[
K4_{iiii,l}^{m E154}
=
-rac{6}{n+2}v_{i,l}^2
]

as a recurrent memoryless covariance-matched sphere approximation.

Its exact radial homogeneity and input K4 identities passed, but:

- deep K4 diagonal relative RMS was about (1.28)--(1.30);
- dense32 final mean improved only slightly;
- adversarial16 final mean worsened.

Therefore E154 falsifies:

> "After every ReLU, the current angular fourth cumulant can be replaced by the
> covariance-matched sphere-linear K4 law."

It does **not** falsify the public angular gauge, because public K2 already gains
with K4 off.

It also does not exactly falsify the public scalar-`c4` recurrence, because
that recurrence is state-dependent and is recomputed from post-ReLU fourth-order
summary terms rather than resetting to (-2/(n+2)).

---

## 7. Relation to E157 failure

E157 tested the exact input K4 through one linear transport and one nonlinear
birth, then destroyed K4.

Every identity gate passed:

- radial homogeneity;
- dense angular K4;
- ARC one-pair carrier;
- D4;
- D22;
- selected Wick terms.

But on the exact 2D synthetic network,

[
rac{mathrm{MSE}_{AIK4-1}}
{mathrm{MSE}_{parent}}
=
1.27716888197.
]

So the one-birth exact K4 overlay worsened the frozen parent by about
(27.7%).

E157 therefore falsifies:

> "The public angular gain can be transferred to this parent by adding only the
> exact first K4 birth."

It does **not** falsify a gauge-only transform, because E157's parent was already
an angular K2 parent and the candidate delta was specifically the K4 overlay.

---

## 8. Cost transfer audit

### 8.1 Measured public angular-gauge delta

For K2:

[
95{,}874{,}876{,}448
-
95{,}869{,}616{,}160
=
5{,}260{,}288
]

FLOPs.

For K3C65:

[
1{,}730{,}267{,}603{,}294
-
1{,}730{,}262{,}343{,}006
=
5{,}260{,}288
]

FLOPs again.

The same measured delta across these two very different parents strongly
supports the interpretation that angularization is a small low-order state
transform/readout overlay, not an expensive recurrent K4 mechanism.

Relative to the project budget (B=2^{41}),

[
5{,}260{,}288/B
=
2.3921020	imes10^{-6}.
]

### 8.2 Measured recurrent scalar-K4 delta

On angular K2:

[
96{,}992{,}057{,}376
-
95{,}874{,}876{,}448
=
1{,}117{,}180{,}928
]

FLOPs.

This is roughly 212 times the measured angular-gauge delta, while slightly
worsening the angular K2 raw MSE.

### 8.3 Full public K3 closure is not transferable under the project cap

The public K3C65 angular estimator costs

[
1.7302676	imes10^{12}
]

FLOPs, approximately (0.7868B).

That is far above the project limit (0.135B).

Therefore E160 does **not** admit the public full K3C65 implementation as a
candidate.

Only the low-cost angular gauge mechanism is potentially transferable.

### 8.4 Conservative clean-room overlay budget

For a future owner, do not rely on the public measured delta as the production
proof.

Freeze a conservative gauge-only allowance

[
C_{m gauge}(n,L)
le
8n^2+64Ln.
]

This covers:

- mean scaling/division;
- the one-time (mm^T) outer product;
- covariance correction;
- final radial scaling;
- finite/symmetry/bookkeeping overhead.

At (n=1024,L=16):

[
C_{m gauge}
le
9{,}437{,}184
]

FLOPs.

A future owner parent must therefore satisfy

[
C_{m parent}
le
296{,}868{,}139{,}499
-
9{,}437{,}184
=
296{,}858{,}702{,}315.
]

This is the cost-transfer condition for the hypothesis below.

As a cost-only example, adding this conservative overlay to the E157 parent
upper (74{,}238{,}787{,}584) would give

[
74{,}248{,}224{,}768
]

FLOPs, still far below the project cap. This is **not** a recommendation to
reuse the scientifically poor E157 parent; it only demonstrates that the gauge
overlay itself is not a cost obstacle.

---

## 9. One admissible clean-room hypothesis

### H160 — AGO: Angular Gauge Only

**HYPOTHESIS. No owner exists yet. No run is authorized.**

The public ablation evidence supports testing the exact low-order angular gauge
without any K4 correction.

A future owner may define exactly one clean-room candidate:

1. freeze one deterministic, target-free parent estimator whose complete
   production cost leaves room for (C_{m gauge});
2. parent and candidate have identical non-K4 closure arithmetic;
3. candidate introduces **no K4 state, no D4/D22 birth, no scalar c4, and no
   K4 recurrence**;
4. at the first owner-defined Gaussian activation state, apply only the exact
   K1/K2 gauge transform
   [
   m_A=m_G/a_1,
   ]
   [
   C_A=C_G-(a_1^{-2}-1)m_Gm_G^T;
   ]
5. continue the same frozen parent closure from that angular K1/K2 state;
6. convert the final angular mean back with
   [
   m_G^{out}=a_1m_A^{out};
   ]
7. if the parent has K3/D21 state, that state is not refit, re-ranked, or
   corrected by E160; the only candidate delta is the exact K1/K2 gauge and
   final radial readout;
8. no public target, mini, scorer, holdout, full suite, submission, fitting,
   sweep, or post-result rescue.

### Why this hypothesis survives E154/E157

- E154 changed recurrent K4 and failed; H160 has no K4.
- E157 added one exact K4 birth to an already-angular parent and failed; H160's
  candidate delta is the angular gauge itself.
- Public K2 evidence shows the gauge effect while K4 is exactly disabled.
- The public full-K3 result suggests, but does not prove, that the gauge can
  interact favorably with a richer parent closure.

### What H160 does not claim

It does not claim:

- that the public K3C65 gain transfers to a cheap parent;
- that angular K1/K2 conversion makes a K3 carrier exact;
- that recurrent scalar K4 is useful;
- that E154 or E157 should be rerun;
- that the public benchmark results may be used as tuning targets.

Any execution requires a separate owner protocol that freezes:

- parent commit/blob;
- exact location of the gauge transform;
- complete all-in parent+overlay cost;
- target-free exact-small references and gates;
- one-run/no-rescue discipline.

---

## 10. Audit conclusion

The source-supported attribution is:

[
oxed{
	ext{public angular gain}

eq
	ext{evidence for recurrent K4 as the causal mechanism}
}
]

The public implementation combines:

1. exact radial/angular homogeneity;
2. an exact K1/K2 angular state-gauge conversion;
3. exact radial mean readout;
4. a particular K3 source-bank closure in the full candidate;
5. a separate recurrent scalar-K4 projection heuristic when `use_k4=True`.

The cleanest public ablation turns item 5 completely off and still obtains the
largest relative K2 gain.

Official ARC equations validate the full cumulant/Wick framework and the exact
special input-K4 carrier, but they do not validate a recurrent isotropic scalar
`c4` closure.

E154 and E157 correctly close two K4-specific hypotheses. They leave one
distinct, minimal mechanism untested:

[
oxed{	ext{H160: exact angular K1/K2 gauge only, no K4}}
]

This note is support-only. No workflow, run arm, scientific execution, public
target access, or canonical/ledger mutation is authorized.
