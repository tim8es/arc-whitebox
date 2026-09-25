# R380 — constructive shallow-readout transform audit

**Status:** COMPLETE  
**Verdict:** **STRICT_NO_GO_NO_CERTIFIED_ONE_HIDDEN_WHITE_BOX_TRANSFORM**  
**Mode:** theory/static audit only; zero benchmark tensors, zero estimator runs, zero downloads/installs  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `research/r380-r366-constructive-transform-20260925`

## Structured result

| Field | Result |
|---|---|
| Requested object | deterministic, target-free `T_m(W) -> (A,B)` with `g(x)=A ReLU(Bx)` and analytic Gaussian readout |
| Concrete admissible transform found | **NO** |
| Sample-fit/distillation used | **NO** |
| Benchmark tensors used/downloaded | **NO** |
| Exact deep-to-shallow construction found in primary literature | **YES, but not admissible:** Villani–Schoots converts a deep ReLU net to **three hidden layers**, uses extended-real weights, and requires activation-region enumeration |
| One-hidden-layer exact flattening of general bias-free deep ReLU | **not available; structurally false in general** |
| Quantitative one-hidden Gaussian-L2 construction for the ARC 1024x16 class | **NOT FOUND** |
| Phase-2 all-in cost/storage certificate | **NO**, because no admissible construction exists |
| Population-mean certificate implies Mini scorer improvement | **NO** |
| R366 status after R380 | **remains closed** |
| Missing constructive step | a deterministic weight-only algorithm producing a finite signed ridge/cosine representation of the relevant even component, with computable Gaussian-L2 error and width/construction-cost bounds inside Phase-2 limits, without sample/cubature fitting or exhaustive activation-region enumeration |

## 1. Scope and dedupe

R380 starts from, and does not repeat, the following conclusions.

- **R366** (`02305335c80161311e13839de3268be97a43e504`) already established the exact readout `E[A ReLU(BX)] = A [||b_j||]_j / sqrt(2*pi)` for `X ~ N(0,I)`, Jensen's population-mean bound, and the leading readout/storage costs. Its blocker was the missing constructive `T_m`.
- **R373** established the material scorer correction: a Gaussian-L2 certificate to the exact population mean does not by itself certify error to the fixed baked Mini target.
- **R375** established that a frozen target-free candidate can nevertheless be evaluated directly against public Mini labels in a later development test; no `eta_i` is needed for that direct scorer evaluation. It also confirmed that no R366 `T_m` existed.
- live `research/history.json` at main has blob `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`. Static term counts in that immutable history are zero for `ridgelet`, `Barron`, `shallow`, `distill`, `surrogate`, `two-layer`, `activation pattern`, `region`, and `hinge`; `ReLU` occurs but no earlier recorded experiment supplies the transform studied here.

R380 therefore asks only the missing constructive question: can the known deep weights be transformed directly into a finite one-hidden-layer ridge surrogate with a proof-grade error/cost certificate, without learning it from sampled `(x,f_W(x))` pairs?

## 2. New constructive literature result: it stops at three hidden layers, not one

A materially relevant primary result postdating the older R366 literature set is:

Mattia J. Villani and Nandi Schoots, **“Any ReLU Network Is Shallow,”** ECAI 2025 proceedings, first published online 2026-08-25, DOI 10.3233/FAIA251170.  
Primary source: https://journals.sagepub.com/doi/10.3233/FAIA251170

Their Theorem 2 is genuinely constructive: every deep ReLU network can be rewritten as a functionally identical network with **three hidden layers** and weights in the extended reals. Their Algorithm 1 obtains the local linear models by searching feasible activation patterns / regions and then explicitly builds the shallow network.

This resolves a weaker version of R366's question: a deterministic white-box flattening algorithm exists if three hidden layers, extended-real weights, and exhaustive region recovery are allowed.

It does **not** provide the required object `T_m(W)->(A,B)`, `g(x)=A ReLU(Bx)`. Three hidden layers do not have R366's one-dimensional analytic Gaussian readout. The construction also uses `infinity` as a selector weight; replacing it by a finite constant is explicitly not exact because neighboring regions approach boundaries arbitrarily closely.

For ARC there are `16*1024=16,384` ReLU units. The unreduced activation-pattern universe is therefore `2^16384`. Villani–Schoots supplies pruning heuristics, not a Phase-2 all-in complexity bound for this architecture. Hence this exact construction cannot be converted into an ARC estimator certificate.

**Disposition:** constructive, but **not an admissible R366 transform**.

## 3. Structural obstruction at exactly one hidden layer

The requested bias-free surrogate
`g(x)=A ReLU(Bx)`
obeys, at every width,

`g(x)-g(-x)=ABx`,

because `ReLU(t)-ReLU(-t)=t`. Thus its odd part is exactly linear:
`g_odd(x)=(1/2)ABx`.

This is a genuine approximation-class restriction.

### Primary positive-homogeneous result

**“Approximating positive homogeneous functions with scale invariant neural networks,”** Journal of Approximation Theory (2025), DOI 10.1016/j.jat.2025.106177.  
Primary source: https://doi.org/10.1016/j.jat.2025.106177

Lemma 5.8 places all one-hidden-layer bias-free ReLU realizations in a proper closed subspace: their antipodal difference is linear. The paper proves that two hidden layers have the relevant universal approximation property while one hidden layer does not.

### Spherical-harmonic form

The NeurIPS 2022 supplementary derivation for *Learning sparse features can lead to overfitting in neural networks* shows that the spherical-harmonic coefficients of bias-free ReLU ridge functions vanish at all odd degrees `k>1`:  
https://proceedings.neurips.cc/paper_files/paper/2022/file/3d3a9e085540c65dd3e5731361f9320e-Supplemental-Conference.pdf

Equivalently, one-hidden bias-free ReLU sums can carry arbitrary even components plus degree-1 odd structure, but no higher odd harmonics.

For a deep target `f`, define `f_odd(x)=(f(x)-f(-x))/2`. Then every requested surrogate satisfies

`E||f(X)-g(X)||^2 >= inf_L E||f_odd(X)-LX||^2`, `X~N(0,I)`.

So nonlinear odd structure creates a width-independent floor on R366's **whole-function** Gaussian-L2 certificate. R380 does not claim a numerical value for this floor on ARC instances; no benchmark weights were inspected.

## 4. Why this does not itself kill population-mean estimation

The Gaussian law is antipodally symmetric, so `E[f_odd(X)]=0`. Only

`f_even(x)=(f(x)+f(-x))/2`

contributes to the exact population mean.

Therefore R366's whole-function L2 certificate is stronger than necessary for the mean. A serious rescue would construct a shallow ridge approximation only to `f_even`.

That leads to the closest one-hidden mathematical route found by R380.

## 5. Closest one-hidden route: signed cosine/ridge representation of the even part

Paired ridge directions satisfy

`ReLU(b^T x)+ReLU(-b^T x)=|b^T x|`.

Finite signed sums of these atoms are finite signed cosine-transform representations. On the unit sphere,

`H(mu)(x)=integral |<u,x>| d mu(u)`.

Breiding et al., **“The zonoid algebra, generalized mixed volumes, and random determinants,”** Advances in Mathematics (2022), Theorem 2.26, prove that the cosine transform on signed even measures is injective and its image is dense in continuous even functions on projective space.  
Primary source: https://doi.org/10.1016/j.aim.2022.108361

Thus, at the existence/approximation level, the even restriction of a continuous positive-homogeneous deep ReLU function can be approximated by signed `|b^T x|` atoms, hence by paired bias-free ReLUs.

Mhaskar et al., **“Function approximation with zonal function networks with activation functions analogous to the rectified linear unit functions,”** Journal of Complexity 51 (2019), give constructive spherical approximation formulas.  
Primary source: https://doi.org/10.1016/j.jco.2018.09.002

But those constructions obtain coefficients from target-function data/evaluations. Applied here, evaluating `f_W(x_q)` on a deterministic sphere design and solving for coefficients is still a sampled/cubature surrogate fit. It is not the requested direct weight-only flattening and collides with the occupied sampling/cubature/regression family.

Sonoda & Murata, **“Neural network with unbounded activation functions is universal approximator,”** ACHA 43(2), 2017, give ridgelet/Radon reconstruction and discretization machinery.  
Primary source: https://doi.org/10.1016/j.acha.2015.12.005

Again, the theorem does not provide an ARC-specific algorithm that reads a 1024x16 weight stack and emits finite `A,B` with a computable error constant and bounded construction cost without either evaluating the represented function or first recovering its polyhedral/activation-region decomposition.

### Exact missing bridge

A direct weight-only rescue must:

1. derive the even component from the deep weights without sample fitting;
2. compute/invert its signed cosine/ridge measure, or an equivalent finite coefficient object;
3. deterministically sparsify/discretize it to `m` atoms;
4. emit `A,B`;
5. compute a proof-grade Gaussian error bound;
6. do 1–5 inside Phase-2 FLOP, memory, wall and residual-time limits.

No primary theorem found supplies this chain for a deep ReLU weight representation.

The obvious exact route to step 1 is Villani–Schoots activation-region decomposition, which reintroduces exhaustive polyhedral enumeration with no Phase-2 bound. The obvious numerical route is deterministic function sampling/cubature, which R380 excludes.

This is the **specific missing constructive step**.

## 6. Phase-2 cost and storage gate

Official first-party Phase-2 limits:

- `n=1024`, depth `16`;
- per-MLP `B=2^41=2,199,023,255,552` FLOPs;
- score multiplier `max(0.1,F/B)` for valid Phase-2 rows;
- 10% floor reached at integer `F<=219,902,325,555`;
- per-`predict()` wall cap `120 s`;
- residual wall cap `0.4 s`;
- solution-process memory `8 GB`;
- server single-array guard `4 GiB`.

First-party sources:

- https://github.com/AIcrowd/whest-starterkit/blob/main/docs/reference/score-report-fields.md
- https://github.com/AIcrowd/whest-starterkit/blob/main/docs/how-to/validate-run-package.md
- https://github.com/AIcrowd/whestbench/blob/main/CHANGELOG.md
- https://github.com/AIcrowd/whest-starterkit/blob/main/docs/troubleshooting/faq.md

For `A in R^(1024xm)`, `B in R^(mx1024)`:

- float32 coefficient storage = `8192m` bytes;
- norms + final matrix-vector readout = about `4096m+O(m+1024)` FLOPs.

Ignoring every other allocation, 8 GiB gives the absolute coefficient-only ceiling

`m<=1,048,576`.

At that ceiling each of `A` and `B` is 4 GiB, so actual feasible `m` is strictly smaller after the original ~64 MiB deep weights, output, temporaries, runtime, and construction workspace are counted.

Readout is not the primary FLOP bottleneck. The score-floor readout-only inequality permits

`m<=floor(219,902,325,555/4096)=53,687,091`,

far above the memory ceiling. The unresolved term is construction/certification cost `C_Tm` and its workspace/wall time.

## 7. Error certificate and Mini scorer

If a future transform supplies

`delta^2=E||f_W(X)-A ReLU(BX)||^2`,

Jensen gives the population-mean guarantee

`||E f_W-E g||^2/1024 <= delta^2/1024`.

Per R373, that is **not** a certificate against the fixed baked Mini target and therefore does not prove Mini scorer improvement.

Per R375, after a target-free candidate is completely frozen, a later public-development scorer test may evaluate it directly against Mini labels. The same-panel GO inequality is then

`(1/100) sum_i MSE(p_i,y_i)*max(0.1,F_i/2^41) < 8.170397440117225e-9`,

with all 100 rows valid.

R380 performs no such measurement and makes no improvement claim.

## 8. Exact GO / NO-GO criterion

### GO

Reopen R366 only if, **before benchmark evaluation**, a source-backed or independently proved algorithm is supplied that for an arbitrary ARC weight stack:

1. deterministically computes finite `A,B` from `W` alone;
2. uses no sampled/cubature `(x,f_W(x))` fit and no target labels;
3. provides a computable per-instance Gaussian population-mean error certificate;
4. proves `m` plus construction workspace fit the 8 GB process limit and 4 GiB single-array guard;
5. proves all-in `C_Tm+C_readout+C_aux<=2^41`, wall `<=120 s`, residual `<=0.4 s`;
6. supplies constants strong enough to make an R209-beating fixed-Mini test scientifically plausible, while explicitly keeping the population certificate distinct from Mini proof.

### NO-GO

If any of 1–5 is absent, do not benchmark this mechanism.

**Current R380 result: NO-GO at 1, 3, 4 and 5.**

## 9. Cheapest future falsifier

The cheapest falsifier remains entirely target-free and must precede Mini access.

Given a proposed concrete `T_m`, apply it to a symbolic/small exact zero-bias deep-ReLU fixture and require `A,B`, its claimed certificate, and an exact operation/storage ledger. Check:

1. determinism from weights only;
2. no function-sample/cubature fitting;
3. analytic Gaussian readout identity;
4. claimed error bound against an exact polyhedral Gaussian integral on the tiny fixture;
5. closed-form extrapolation `C_Tm(n,L,m)` and workspace to `n=1024,L=16`.

Reject before benchmark access if the construction requires unbounded activation-region enumeration, hides sampled function evaluations in coefficient recovery, or cannot state the construction FLOPs/workspace.

The object this falsifier tests is precise: **weight-stack -> finite signed cosine/ridge coefficients with certified error and bounded construction complexity**.

## 10. Conclusion

R380 adds a new constructive fact to R366/R373/R375: Villani–Schoots now provides an exact deterministic deep-to-shallow conversion, but only to three hidden layers with extended-real selector weights and activation-region enumeration. It does not produce `A ReLU(Bx)` or analytic Gaussian readout.

At one bias-free hidden layer, the antipodal identity imposes a real expressivity restriction. For population means the odd component integrates to zero, so the mathematically relevant rescue is the even component. Signed cosine-transform theory establishes density/existence for that even component, but available constructive recipes require function evaluations or an explicit polyhedral decomposition. The former is sample/cubature fitting; the latter has no ARC-scale Phase-2 complexity bound.

Therefore there is still **no concrete admissible deterministic target-free ARC-scale `T_m(W)->(A,B)`** satisfying the R366 mechanism and Phase-2 cost/certificate gates.

**R380 verdict: STRICT_NO_GO_NO_CERTIFIED_ONE_HIDDEN_WHITE_BOX_TRANSFORM.**

## 11. Execution accounting

- benchmark tensors accessed/downloaded: **0**
- private/holdout/full access: **0**
- dependencies installed: **0**
- estimator/benchmark/scorer/synthetic numerical runs: **0**
- GitHub Actions: **0**
- submissions: **0**
- paid resources: **0**
- R366/R320/main/PR/control/queue edits: **0**
- R380 repository artifact: **this Markdown report only**
