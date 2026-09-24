# R366 — uncovered estimator frontier scout

**Status:** COMPLETE  
**Verdict:** **TERMINAL_NO_GO_MISSING_CERTIFIED_WHITE_BOX_SHALLOW_RIDGE_FLATTENING_THEOREM**  
**Mode:** report-only theory/method scout; no estimator or benchmark execution  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `review/r366-uncovered-estimator-frontier-scout-20260924`

## 1. Narrow research question

R366 asks whether one genuinely unoccupied algorithmic class remains for estimating

[
mu(W)=mathbb E_{Xsim N(0,I_{1024})}[f_W(X)]
]

for the given zero-bias, dense, width-1024/depth-16 ReLU MLPs, with a credible route to improve the strongest compatible internally verified estimator under the Phase-2 scorer.

R366 admits **one** distinct frontier class for analysis and no others:

> **white-box shallow-ridge flattening with analytic Gaussian readout**.

The class does **not** survive its theory gate, so R366 stops before implementation or any numeric falsifier.

This is an evidence-based feasibility NO-GO for this concrete route. It is **not** a theorem that no better estimator exists.

## 2. Immutable evidence and current traceability state

### Exact history

Read before method selection:

- `research/history.json`
- exact-main base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- Git blob SHA-1: `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`
- E100–E193 IDs parsed: **94**
- E100–E193 artifact records parsed: **468**

### Live consolidated R320

R320 was reread after it advanced during this desk audit. The final dedupe snapshot used by R366 is:

- branch: `review/r320-sidecar-research-traceability-20260924`
- live head: `7336ffb2a88ab38ebb96177d4bc7d8bfd5dd53e1`
- report blob: `870c9131a4e4bc745ea6ad6510d6a45115dcc5a8`
- receipt blob: `3fa12a194b1fd33361465bef815afe1eedc81460`
- `R366` occurrences before this task: **0**
- shallow/ridge-surrogate/distillation occurrences in the live R320 report: **0**

The live R320 snapshot already includes the corrected R352/R364 lineage, R361/R362/R363, current H185 gate state, and later UI attestations. R366 does not modify R320.

## 3. Strongest compatible internal baseline

The exact normalized development baseline remains R209 V25:

- artifact: `research/results/R209-v25-mini100.json`
- integration commit: `20fafab5471e6ed227562c651179dd2ef331ea22`
- Git blob SHA-1: `0183d0570f7c9965e00e8553ffc003c313865232`
- panel: `v2-phase2 mini:all-100`
- rows: 100
- failures: 0
- mean raw final-layer MSE: `2.22830349017044681e-8` (exact-decimal recomputation already independently preserved by R343/R342)
- mean adjusted score: approximately `8.170397440117225e-9`
- measured FLOPs per network: `806303721965`

R265 and R276 identify R209 as the strongest compatible normalized V25 reference in their same-panel screens. R366 makes **no** leaderboard comparison and does not use rounded public UI scores as a gap.

The relevant scorer formula is the pinned Phase-2 formula:

[
s_i=operatorname{MSE}_{i,mathrm{final}},
max(0.1,C_i/B),qquad
B=2^{41}=2{,}199{,}023{,}255{,}552.
]

For Phase 2, residual time is gated rather than priced.

## 4. Dedupe audit

The complete history and the specified post-history audits were checked before admitting the single frontier class.

### Already occupied / closed mechanism families

| Family | Direct evidence checked | R366 disposition |
|---|---|---|
| residual/control-variate, Stein/JVP | E108–E109 and earlier history | occupied / closed descendants |
| antithetic, orthogonal/Haar, radial Rao–Blackwell | E100, E104, E110, E113; AGO lineage E164–E176 | occupied |
| QMC/cubature/frame/static quadrature | E004, E100–E107, E121–E126 | occupied |
| conditional Gaussian / halfspace / gate conditioning / orthant state | E111–E113; R317/R321 | occupied; R317 core NO-GO retained with R324 caveat |
| cumulant K3/K4 / Edgeworth / moment closure | E112, E132–E159, E178; R223/R251 descendants | occupied |
| dense Hermite / polynomial chaos | E115; R347 | terminally covered |
| low-rank/tensorized Hermite | corrected R352/R364 plus R361/R362/R363 | evidence-based NO-GO for currently audited TT/Hermite paths |
| TensorSketch / CountSketch / TT / CP / Tucker / low-rank carriers | E008, E137, E148, H180/E181 and inventory in R265/R276/R308 | occupied |
| characteristic-function / Hilbert-transform propagation | R335/R338, independent R337 | evidence-based feasibility NO-GO; no universal impossibility claim |
| activation-boundary flux / output flux | E114, E118, E119 | occupied |
| response-aligned / adjoint / observable | E116–E119, E142–E152 | occupied |
| source-age/window/tail and young/old tier sparsification | E127–E135 plus R247 etc. | occupied |
| structured Kronecker/Legendre/basis transport | R244/R247/R248/R250, R308 inventory | occupied |
| randomized multilevel / telescope | R265 then R269 | concrete depth-prefix path closed |
| displacement / low-displacement-rank weight arithmetic | E192 | terminal desk NO-GO; even weight-operation relief did not close the preserved cost gate |
| fast arithmetic / reassociation | prior fast-matmul lanes; H185 E185/E187/E190 | occupied; H185 remains blocked at G2 |
| public-method copying | multiple R3xx audits | not a method source; no public method imported |

R265 report blob `e9b5df06173bf70a587774f9374042962847d9e2`, R276 report blob `4970614c1ac789b008260d726a2bbd5272116434`, and R308 report blob `e07ddccdf3744c741a571556d7597ac15b460c4b` were specifically reread because they are broad prior-family screens.

### Current corrected Hermite boundary

The corrected/live R352 lineage is preserved:

- branch `review/r352-tensorized-hermite-frontier-20260924`
- corrected head after R364: `c51af6c62639503d326f4cbda5b2d59116bbb718`
- corrected report blob: `f384caa56b1a43212bf909ccfd3567fa86a7b4e4`
- corrected receipt blob: `ca4f4608a592594a321790e760aa2d7f6398476b`
- verdict: `EVIDENCE_BASED_NO_GO_NO_CERTIFIED_LOW_RANK_TT_HERMITE_PATH`

R366 does not reinterpret that narrow verdict as universal impossibility.

### H185 boundary

E185/E187/E190 and the later R351/R356 consolidation were reread. H185 remains blocked because its exact dense-parent denominator/component ledger is not proof-grade reconstructed; it has no authorization to run. R366 does not rename or rescue H185.

## 5. The one distinct frontier class

### Name

**WSRF-AGR: white-box shallow-ridge flattening with analytic Gaussian readout.**

This is a **function-representation** route, not a hidden-state moment closure.

Given the known deep zero-bias ReLU network (f_W:mathbb R^n	omathbb R^n), seek a deterministic, target-free, white-box transformation

[
T_m(W_1,ldots,W_L)mapsto (A,B)
]

with

[
Ainmathbb R^{n	imes m},qquad
Binmathbb R^{m	imes n},
]

such that the whole deep function is approximated in Gaussian (L^2) by the one-hidden-layer homogeneous ridge network

[
g_{A,B}(x)=A,ho(Bx),
qquad ho(t)=max(0,t).
]

The transformation must be derived from the supplied weights only. If (A,B) are fitted from sampled input/output pairs, the proposal collapses into the already occupied sampling/regression/distillation family and loses R366 novelty.

### Why it is distinct

WSRF-AGR does **not**:

- propagate K1/K2/K3/K4 moments;
- store a Hermite/PCE, TT, CP, Tucker, sketch, or characteristic-function state;
- enumerate activation masks or integrate one orthant at a time;
- use a response/JVP/Stein control variate;
- alter the dense multiplication schedule as H185 does;
- approximate the weight matrices by low displacement rank;
- choose QMC/sample points as the estimator.

Instead it asks for a deterministic **global depth-flattening map** from the known deep network to a shallow sum of ridge ReLUs, after which Gaussian integration is analytic.

Repository search at the exact history/base found no prior `shallow`, `ridge function`, `distill`, `surrogate network`, or `two-layer` artifact matching this white-box whole-function flattening mechanism.

## 6. Exact analytic estimator if the surrogate exists

Let (b_j^	op) be row (j) of (B), and let (a_j) be column (j) of (A). For

[
Xsim N(0,I_n),
]

we have

[
b_j^	op Xsim N(0,|b_j|_2^2).
]

The one-dimensional truncated-normal/ReLU moment is

[
mathbb E[ho(b_j^	op X)]
=
rac{|b_j|_2}{sqrt{2pi}}.
]

Therefore the surrogate expectation is available without sampling:

[
oxed{
widehatmu_{mathrm{WSRF}}
=
mathbb E[g_{A,B}(X)]
=
rac{1}{sqrt{2pi}}A
egin{bmatrix}
|b_1|_2\
dots\
|b_m|_2
end{bmatrix}.
}
]

The formula is exact **for (g_{A,B})**. It is not unbiased for the original deep (f_W) unless (g_{A,B}=f_W) in expectation.

Tallis (1961) supplies the primary truncated-normal moment framework; the displayed scalar identity is its elementary zero-mean one-dimensional special case.

## 7. Rigorous controlled final-mean error

Define the Gaussian function-approximation error

[
delta^2(W;A,B)
=
mathbb E_{Xsim N(0,I_n)}
|f_W(X)-g_{A,B}(X)|_2^2.
]

By Jensen,

[
|mathbb E f_W(X)-mathbb E g_{A,B}(X)|_2^2
le
delta^2(W;A,B).
]

Since the benchmark final-layer MSE is the mean over (n=1024) output coordinates, a certificate

[
oxed{
rac{delta^2(W;A,B)}{n}learepsilon^2
}
]

implies the rigorous mean-estimation bound

[
oxed{
operatorname{MSE}_{mathrm{mean}}
le arepsilon^2.
}
]

This is the useful feature of the class: a target-free **function approximation certificate** would immediately become a final-mean certificate.

## 8. Exact Phase-2 score gate relative to R209

No leaderboard target is used.

On the exact same R209 Mini-100 development panel, a sufficient certified condition to improve R209's stored adjusted score is

[
rac1{100}sum_{i=1}^{100}
rac{delta_i^2}{1024}
max(0.1,C_i/2^{41})
<
8.170397440117225	imes10^{-9}.
]

This is a sufficient condition because the candidate's raw final-mean MSE is upper-bounded by (delta_i^2/1024).

Two useful special cases:

### If every candidate row reaches the scorer floor

For integer FLOPs (C_ile 219{,}902{,}325{,}555), the multiplier is (0.1). It is sufficient that

[
oxed{
rac1{100}sum_irac{delta_i^2}{1024}
<
8.170397440117225	imes10^{-8}.
}
]

Equivalently, the average total-output Gaussian (L^2) squared error must be below approximately

[
8.36648697868004	imes10^{-5}.
]

### To dominate R209 raw final-mean accuracy itself

The stricter sufficient condition is

[
oxed{
rac1{100}sum_irac{delta_i^2}{1024}
<
2.22830349017044681	imes10^{-8}.
}
]

R366 makes neither claim; these are predeclared theory gates.

## 9. Compute and memory accounting

Official first-party Phase-2 parameters used:

- width (n=1024)
- depth (L=16)
- per-MLP FLOP budget (B=2^{41}=2{,}199{,}023{,}255{,}552)
- wall-time cap: 120 s
- residual-time cap: 0.4 s
- solution-process memory: 8 GB
- score multiplier floor: 0.1

The benchmark generator uses dense (1024	imes1024) weight matrices with entries drawn from (N(0,2/1024)).

### Readout cost once (A,B) exist

For a bias-free (m)-ridge surrogate:

- compute all (m) row norms of (B): approximately (2mn) scalar FLOPs;
- multiply (A) by the (m)-vector of expected ridge activations: approximately (2mn) scalar FLOPs;
- remaining scaling/scalar-normal work: (O(m+n)).

Thus

[
C_{mathrm{readout}}(m)approx 4mn+O(m+n).
]

At (n=1024),

[
C_{mathrm{readout}}(m)approx 4096m.
]

The float32 coefficient storage for (A) and (B) alone is

[
M_{A,B}=4(nm+mn)=8nm
=8192m;	ext{bytes}.
]

Example: (m=131072) requires exactly (1{,}073{,}741{,}824) bytes (1 GiB) for (A+B) and about (536{,}870{,}912) leading-order readout FLOPs. The original 16 dense float32 weight matrices themselves occupy about 64 MiB.

Therefore **analytic readout is not the bottleneck**. The bottleneck is producing a certified (A,B) from the deep weights.

### Missing all-in term

The full estimator cost is

[
C_{mathrm{all}}=
C_{T_m}(W)
+
C_{mathrm{readout}}(m)
+
C_{mathrm{aux}}.
]

No admissible primary-source theorem found by R366 bounds (C_{T_m}), (m), and (delta^2) simultaneously for the Phase-2 He-Gaussian deep-network ensemble.

## 10. Primary-source literature audit

### Truncated Gaussian moments

G. M. Tallis, **“The Moment Generating Function of the Truncated Multi-Normal Distribution,”** JRSS Series B 23(1), 223–229 (1961).  
DOI: https://doi.org/10.1111/j.2517-6161.1961.tb00408.x

Use here: analytic truncated-normal moments; the scalar zero-mean ReLU expectation follows directly.

### Shallow positively homogeneous ReLU representations

Francis Bach, **“Breaking the Curse of Dimensionality with Convex Neural Networks,”** JMLR 18(19), 1–53 (2017).  
Primary source: https://jmlr.org/papers/v18/14-546.html

Bach gives approximation/estimation theory for single-hidden-layer positively homogeneous activations, including ReLU, but also explicitly identifies the computational difficulty of the infinite-dimensional unit-addition subproblem and does not supply the required polynomial-time white-box flattening theorem for arbitrary deep networks.

### Quantitative limits for shallow random ReLU features

Daniel Hsu, Clayton Sanford, Rocco Servedio, Emmanouil Vlatakis-Gkaragkounis, **“On the Approximation Power of Two-Layer Networks of Random ReLUs,”** COLT 2021, PMLR 134.  
Primary source: https://proceedings.mlr.press/v134/hsu21a.html

This work gives near-matching upper/lower width bounds for broad Lipschitz/Sobolev classes and shows that shallow approximation can require exponentially many random ReLU features in general. Its distribution/domain is not the ARC He-Gaussian-network ensemble, so R366 does **not** use it as a direct impossibility theorem for ARC.

### Depth separation

Ronen Eldan and Ohad Shamir, **“The Power of Depth for Feedforward Neural Networks,”** COLT 2016, PMLR 49.  
Primary source: https://proceedings.mlr.press/v49/eldan16.html

This gives an explicit depth-separation result: some compact depth-3 networks require exponentially large depth-2 networks for constant approximation accuracy under the paper's probability measure. That measure is not the ARC standard Gaussian input law. R366 uses this only to reject an unsupported *universal* “deep always flattens compactly” premise.

Matus Telgarsky, **“Benefits of Depth in Neural Networks,”** COLT 2016, PMLR 49.  
Primary source: https://proceedings.mlr.press/v49/telgarsky16.html

This independently establishes exponential depth/width separations for ReLU/semi-algebraic networks in its setting; again, it is not an ARC He-Gaussian ensemble theorem.

### Gaussian-input learning hardness is not a white-box lower bound

Sitan Chen, Aravind Gollakota, Adam Klivans, Raghu Meka, **“Hardness of Noise-Free Learning for Two-Hidden-Layer Neural Networks,”** NeurIPS 2022.  
Primary source: https://proceedings.neurips.cc/paper_files/paper/2022/hash/45a7ca247462d9e465ee88c8a302ca70-Abstract-Conference.html

This supplies super-polynomial statistical-query lower bounds under Gaussian inputs for learning certain two-hidden-layer ReLU networks. R366 does **not** transfer that black-box/SQ lower bound to the present white-box setting; it only confirms that sample-based distillation cannot be assumed generically easy.

## 11. Exact missing theorem / inequality

WSRF-AGR would become an admissible estimator only if a source-backed or independently proved **white-box construction theorem** supplied, for the actual Phase-2 network class, a deterministic map (T_m) with a computable certificate satisfying both:

[
oxed{
rac1{100}sum_{i=1}^{100}
rac{
mathbb E_{Xsim N(0,I)}
|f_{W_i}(X)-A_iho(B_iX)|_2^2
}{1024}
max(0.1,C_i/2^{41})
<
8.170397440117225	imes10^{-9}
}
]

on the same verified panel, and

[
oxed{
C_i=C_{T_m,i}+C_{mathrm{readout},i}+C_{mathrm{aux},i}
<2^{41},
quad
M_ile 8;mathrm{GB},
quad
t_{mathrm{wall},i}le120;mathrm{s},
quad
t_{mathrm{residual},i}le0.4;mathrm{s}.
}
]

For a generic, pre-panel theorem, the analogous requirement must hold with an explicit high-probability statement for (W_ellstackrel{iid}{sim}N(0,2/1024)), plus a per-instance certifier that does not use target means.

**No primary source found by R366 proves such a theorem, or a weaker theorem with constants close enough to certify the R209 threshold for width 1024/depth 16.**

This is the exact blocker.

## 12. Why no numerical falsifier is launched

The cheapest valid falsifier is **the theory/certificate gate above**, and it fails before numerical work.

Without a constructive (T_m) and a pre-existing bound connecting its output to Gaussian (L^2) error:

- selecting a shallow architecture/width and fitting it on sampled evaluations of (f_W) would revert to sampling/regression method search already occupied in history;
- choosing (m), optimization, or training data after observing outcomes would be method fishing;
- a synthetic test could show one fixture works but would not repair the missing construction/error theorem needed for a general Phase-2 path.

Therefore the preregistered numerical falsifier count is **zero**.

### Re-entry gate

A future task may reopen this exact class only after supplying, before execution:

1. a deterministic white-box (T_m(W)), not sample-fit distillation;
2. a computable Gaussian-(L^2) certificate (delta^2(W;A,B));
3. an explicit all-in (C_{T_m}+4mn+O(m+n)) bound and memory bound;
4. constants that make the R209 same-panel inequality above achievable.

Only then should a cheapest exact-small target-free numerical falsifier be frozen.

## 13. Scientific conclusion

**TERMINAL NO_GO for R366.**

One unoccupied class was found and made mathematically concrete: **white-box shallow-ridge flattening + analytic Gaussian readout**.

Its readout formula is exact, its conversion from function-(L^2) error to final-mean error is rigorous, and the readout itself is cheap enough that it would be attractive if a compact certified surrogate were available.

But the decisive part is missing: neither the audited primary literature nor the ARC evidence supplies a constructive, target-free, white-box depth-flattening theorem for the actual 1024×16 He-Gaussian ReLU network class with a strong enough Gaussian-(L^2) error constant and bounded construction cost.

Generic shallow approximation theory does not close that gap; known depth-separation results specifically warn against assuming it away, while not proving impossibility for this random-network ensemble.

So R366 does **not** invent a candidate by choosing a width and fitting it empirically. The class is stopped at the exact theory gate above.

## 14. Execution accounting

- estimator implementation: **NO**
- repository code created/run: **NO**
- synthetic estimator/falsifier runs: **0**
- official/public benchmark runs: **0**
- GitHub Actions runs: **0**
- dataset/dependency downloads: **0**
- paid resources: **NO**
- private/holdout/full access: **NO**
- competition submissions: **0**
- leaderboard access used for method comparison: **NO**
- main edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**
- R320 edits: **0**
- historical verdicts changed: **NO**
