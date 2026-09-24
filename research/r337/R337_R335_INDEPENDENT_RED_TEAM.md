# R337 — independent red-team of R335 theory-only NO-GO

**Status:** COMPLETE  
**Verdict:** **PASS_WITH_MATERIAL_CORRECTION — EVIDENCE_BASED_FEASIBILITY_NO_GO_UNCHANGED**  
**Exact R335 head audited:** `9e01cb63dc2a4e662422b3ae98af67d1830505b7`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `review/r337-r335-independent-red-team-20260924`

## Scope

R337 is a targeted red-team of R335's single theory candidate, characteristic-function positive-part propagation (CFPP). It is not a new broad estimator scout.

R337 checks four questions:

1. Is R335's scalar positive-part/characteristic-function identity correct?
2. For a generic dense ReLU network, what object is actually needed at the next layer?
3. Does exact propagation force explicit orthant enumeration, or is there a known alternative representation?
4. Does any primary-source construction establish a generic-dense width-1024/depth-16 path with rigorous propagated error and all-in Phase-2 feasibility below (2^{41}) FLOPs and (0.4) s residual?

Only primary literature is used for external mathematical claims. Project artifacts are used only to identify the exact R335 target and its frozen re-entry gate.

No implementation, synthetic run, benchmark, download, Actions run, paid compute, private/holdout/full access, submission, participant contact, or main/PR/control/queue mutation was performed.

## 1. Exact R335 target

R335 exact head:

`9e01cb63dc2a4e662422b3ae98af67d1830505b7`

Artifacts:

- `research/r335/R335_ACCURACY_SIDE_ESTIMATOR_SCOUT.md`
  - Git blob `1477f3be912bf8c641e3e51c9812cc4833a603d1`
- `research/r335/R335_RECEIPT.json`
  - Git blob `d4d1891d2f13dd51b38032baacd7cb8dd92066b5`

R335 is one commit ahead of the exact base, behind by zero, and its diff contains only those two files.

Its terminal claim is explicitly an **evidence-based NO-GO**, not an implementation result.

## 2. Scalar positive-part formula — PASS

Primary source:

Iosif Pinelis, **“Positive-part moments via the characteristic functions, and more general expressions,”** *Journal of Theoretical Probability* 31 (2018), 527–555. DOI:
https://doi.org/10.1007/s10959-016-0709-1

Author preprint:
https://arxiv.org/abs/1603.07365

Pinelis gives characteristic-function representations for positive-part and absolute moments. For (p=1), the standard absolute-moment specialization is

[
mathbb E|X|
=
rac{2}{pi}
int_0^infty
rac{1-operatorname{Re}phi_X(t)}{t^2},dt,
]

under (mathbb E|X|<infty).

Using (X_+=(X+|X|)/2),

[
oxed{
mathbb E[X_+]
=
rac{mathbb E[X]}{2}
+
rac{1}{pi}
int_0^infty
rac{1-operatorname{Re}phi_X(t)}{t^2},dt
}
]

follows exactly.

**R337 result: R335's scalar formula and finite-first-absolute-moment assumption are correct.**

Pinelis's Theorem 2.3 is also important to the deeper audit: it permits a complex-valued random multiplier (Y) in generalized expectations (mathbb E[Y X_+^p]). That shows the scalar positive-part calculus can be embedded in joint expectations; an exact multivariate treatment is not logically restricted to explicitly listing sign masks.

## 3. What the next dense layer actually needs — PASS

Let (H_ellinmathbb R^n) denote the post-ReLU vector at layer (ell), and let a future dense row be (w_j^	op).

For

[
Z_j=w_j^	op H_ell,
]

the scalar characteristic function is

[
phi_{Z_j}(t)
=
mathbb E e^{itw_j^	op H_ell}
=
Phi_{H_ell}(t w_j),
]

where

[
Phi_{H_ell}(u)
=
mathbb E e^{iu^	op H_ell}
]

is the **joint** characteristic function of the post-ReLU vector.

Therefore a scalar marginal CF for each coordinate of (H_ell) is not enough in general. A later arbitrary dense row queries the joint law along a new ray (u=t w_j).

The same affine identity is stated explicitly in the primary CF-network literature:

Joshua Pilipovsky, Vignesh Sivaramakrishnan, Meeko Oishi, Panagiotis Tsiotras, **“Probabilistic Verification of ReLU Neural Networks via Characteristic Functions,”** L4DC 2023, PMLR 211, 966–979:
https://proceedings.mlr.press/v211/pilipovsky23a.html

Author preprint:
https://arxiv.org/abs/2212.01544

Their Eq. (8) is the multivariate affine rule

[
Phi_{WH+b}(t)
=
e^{it^	op b}Phi_H(W^	op t).
]

**R337 result: R335 is correct that exact generic-dense reuse requires joint-CF information at future row-ray arguments.**

## 4. Exact ReLU update: material correction to R335

R335 gives an exact activation-mask/orthant decomposition of

[
Phi_{operatorname{ReLU}(Z)}(u).
]

That decomposition is valid, and an **explicit mask-indexed representation** can indeed contain up to (2^n) sign regions.

However, the stronger reading

> exact update necessarily requires an explicitly enumerated (2^n)-mask state

is **not proved** and should not be used.

There is an alternative exact functional representation. Pinelis gives exact scalar positive-part CF/Hilbert-transform identities, and his generalized (Y)-weighted formulas allow a coordinate transform to be embedded in expectations involving the remaining coordinates. In principle, repeated coordinate-wise transforms act on the full joint CF rather than on an explicit table of orthants.

Thus the correct distinction is:

- **explicit orthant state:** may have up to (2^n) components;
- **full joint CF:** is also an exact representation and need not enumerate those components explicitly;
- **finite reusable polynomial-size state:** is a separate question and is not supplied by either fact.

The full joint CF is an infinite-dimensional functional object. R337 found no primary-source theorem compressing it, for arbitrary dense ReLU propagation, into a finite polynomial-size state with a rigorous layer-to-layer approximation-error guarantee.

**Exact correction:** R335 should say that exact ReLU propagation requires retaining information equivalent to the relevant joint nonlinear/sign structure, not that every exact representation must explicitly enumerate orthants. No exponential lower bound for all possible representations is established.

This correction narrows the argument but does **not** by itself supply a feasible estimator.

## 5. Material literature omission: Pilipovsky et al. 2023

R335's literature screen omitted a directly relevant primary source: Pilipovsky et al. 2023 explicitly propose propagating characteristic functions through deep ReLU networks using Hilbert transforms.

This is a real omission and must be recorded.

Their construction contains:

1. the exact multivariate affine-CF rule;
2. Pinelis-based scalar ReLU-CF transforms;
3. a numerical Hilbert-transform/grid implementation;
4. deep-network examples.

But it does **not** close the R335 generic-dense requirement.

### 5.1 Component-wise state versus joint dependence

The paper says that after a ReLU it computes the **component-wise CF**. Its own property P6 factorizes a joint CF into products of scalar CFs only for **independent** scalar variables.

Later, for a linear output, the paper uses

[
phi_{c^	op X}(t)
=
prod_j phi_{X_j}(c_jt).
]

That product is exact under the independence condition stated by P6. Generic dense affine mixing does not, in general, preserve independence of hidden coordinates.

Therefore the published component-wise grid construction does not establish an exact recurrence for the full joint CF of a generic dense hidden layer.

This is an inference from the paper's own equations and stated independence condition; it is not attributed to the authors as an explicit limitation.

### 5.2 Numerical evidence is useful but not the required theorem

The paper's examples include:

- a network with 2 inputs, one hidden layer of 10 neurons, one output;
- a deeper example with 2 inputs, 5 hidden layers of 50 neurons each, 2 outputs.

For the two-layer example, a (10^4)-point grid with (10^3) Hilbert-transform terms takes about 3.55 s in the reported CPU setup; coarser settings reduce time while worsening reported error. In the 5×50 example, the paper explicitly notes that numerical errors propagate after each max/ReLU layer.

The conclusion lists studying propagation of Hilbert-transform numerical errors as future work.

Therefore this paper is a genuine prior deep-CF realization, but it does not provide:

- an exact generic-dense dependency-preserving finite state;
- a theorem controlling final mean error through 16 dense ReLU layers;
- a width-1024 propagated-error guarantee;
- a FlopScope-compatible all-in bound below (2^{41}) FLOPs/network;
- a credible residual-time bound below (0.4) s.

**Effect on R335 verdict:** material citation/scope correction, **NO change to the evidence-based Phase-2 feasibility NO-GO**.

## 6. Single query versus persistent composable state

These must not be conflated.

Primary source:

Ben Cousins and Santosh Vempala, **“A Cubic Algorithm for Computing Gaussian Volume,”** SODA 2014:
https://arxiv.org/abs/1306.5829

Their Theorem 1.1 gives a randomized ((1+arepsilon))-approximation to Gaussian volume of a suitable convex set in (O^*(n^3)) membership-oracle complexity; the paper also gives (O^*(n^3)) first-sample and (O^*(n^2)) subsequent-sample complexity under its stated assumptions.

The same paper notes prior polynomial-time work for a Gaussian restricted to the positive orthant.

Therefore:

- a **single high-dimensional Gaussian/orthant-type query can be polynomial-time** in appropriate randomized oracle models;
- it is incorrect to argue that “one orthant query is exponentially hard”;
- this does not provide a reusable exact/controlled post-ReLU state from which arbitrary future dense row rays can be answered after repeated nonlinear layers.

The exponential count in an explicit all-mask representation is an output-size observation about that representation, **not a lower bound on every algorithm or representation**.

R337 makes no exponential lower-bound claim.

## 7. Supporting exact-closure evidence, not an impossibility theorem

Primary source:

Jan Macdonald and Stephan Wäldchen, **“A Complete Characterisation of ReLU-Invariant Distributions,”** AISTATS 2022, PMLR 151:
https://proceedings.mlr.press/v151/macdonald22a.html

Their exact invariant-family result rules out ordinary regular finite-parameter invariant families under their framework unless one of special conditions holds (including width one, finite support, or non-locally-Lipschitz parametrization).

This supports skepticism about a simple exact finite-parametric closure.

It does **not** prove:

- an exponential lower bound;
- impossibility of controlled approximation;
- impossibility for every special bias-free/task-specific construction;
- a Phase-2 FLOP lower bound.

R337 uses it only as supporting context.

A recent exact analytical result also remains shallow rather than generic-deep:

Andrew Thompson and Miles McCrory, **“Uncertainty propagation through trained multi-layer perceptrons: Exact analytical results,”** arXiv:2601.16830:
https://arxiv.org/abs/2601.16830

Its stated exact result is for a ReLU MLP with a **single hidden layer** under multivariate-Gaussian input. It does not furnish the required depth-16 generic-dense persistent state.

## 8. Phase-2 feasibility check

R337 found **no primary-source method** that simultaneously supplies all of the following:

1. dependency-correct propagation for generic dense hidden layers;
2. a reusable finite polynomial-size post-ReLU state;
3. rigorous composable approximation-error control through depth 16;
4. a width-1024 error guarantee tied to final neuron means/raw MSE;
5. a derivable all-in cost below
   [
   2^{41}=2{,}199{,}023{,}255{,}552
   ]
   FLOPs/network;
6. a credible residual path below (0.4) s.

Pilipovsky et al. is the closest omitted CF-specific method, but its published component-wise numerical construction does not establish items 1–6 as a package.

Accordingly, R337 does **not** promote a candidate to implementation.

## 9. R335 re-entry gate — PASS, clearly unexecuted

R335's receipt explicitly records:

- `executed: false`;
- future exact-small fixture only;
- generic dense zero-bias ReLU;
- width 8, depth 4;
- no contest targets.

The first GO threshold is exactly:

`candidate raw mean-vector MSE <= 0.94 * matched parent raw MSE`.

The remaining preregistered gates include median-error non-worsening, production extrapolation below (2^{41}) FLOPs/network, a credible width-1024 residual path below (0.4) s, and no fallback to occupied families.

R335 execution accounting also records:

- estimator runs: 0;
- synthetic runs: 0;
- benchmark runs: 0;
- code created: false;
- downloads: false;
- Actions: 0.

**R337 result: the <=0.94× width-8/depth-4 gate is clearly a future re-entry condition and was not executed.**

## 10. Final red-team verdict

**PASS_WITH_MATERIAL_CORRECTION — EVIDENCE_BASED_FEASIBILITY_NO_GO_UNCHANGED.**

### Confirmed

- Pinelis scalar positive-part mean formula: **correct**.
- Dense next-row query (phi_{w^	op H}(t)=Phi_H(tw)): **correct**.
- Generic dense propagation needs joint dependence information, not just coordinate marginals: **correct**.
- No primary source audited supplies the required generic-dense width-1024/depth-16 propagated-error plus (<2^{41}) FLOP and (<0.4) s residual path: **none found**.
- R335 re-entry falsifier: **unexecuted as stated**.

### Corrections required to the reasoning

1. **R335 omitted Pilipovsky et al. 2023**, a directly relevant published deep-ReLU CF/Hilbert-transform propagation method.
2. **Explicit orthant enumeration is not proved necessary.** Full joint-CF/Hilbert-transform representations can encode the exact transform without an explicit mask table.
3. The (2^n) mask count is only the size of an explicit mask-indexed realization, not an algorithmic lower bound.
4. The defensible terminal claim is therefore **evidence-based feasibility NO-GO**, not an impossibility theorem.

These corrections do not change the execution decision because the omitted method does not establish a dependency-correct finite polynomial-size generic-dense state with the required propagated-error and Phase-2 cost/timing guarantees.

## Primary literature

- Pinelis 2018: https://doi.org/10.1007/s10959-016-0709-1
- Pinelis author preprint: https://arxiv.org/abs/1603.07365
- Pilipovsky et al. 2023, PMLR: https://proceedings.mlr.press/v211/pilipovsky23a.html
- Pilipovsky et al. author preprint: https://arxiv.org/abs/2212.01544
- Cousins & Vempala 2014: https://arxiv.org/abs/1306.5829
- Macdonald & Wäldchen 2022: https://proceedings.mlr.press/v151/macdonald22a.html
- Thompson & McCrory 2026: https://arxiv.org/abs/2601.16830

## Execution accounting

- code / estimator implementation: **0**
- estimator runs: **0**
- synthetic/falsifier runs: **0**
- benchmark runs: **0**
- dataset/dependency downloads: **0**
- GitHub Actions: **0**
- paid compute: **NO**
- private/holdout/full access: **NO**
- competition submissions: **0**
- main edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**
