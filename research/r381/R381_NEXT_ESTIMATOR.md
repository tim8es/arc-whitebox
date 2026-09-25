# R381 — next estimator search after R374/R376

**Status:** COMPLETE  
**Verdict:** **NO_GO_QGME_SDP_PHASE2_SOLVER_AND_FIXED_SCORER_GATES_NOT_CLOSED**  
**Branch:** `research/r381-new-estimator-search-20260925`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Mode:** independent theory/search only; no estimator, benchmark, download, install, Actions, or submission run

## 1. Evidence read before candidate selection

### Live history

- `research/history.json`
- live Git blob: `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`
- source: https://github.com/tim8es/arc-whitebox/blob/main/research/history.json

The live history was searched for the requested closed families and for the candidate vocabulary used below. In addition to the user-listed exclusions, two especially relevant earlier results were re-read:

- **E000** already reproduced the official Phase-2 covariance baseline; this prevents relabeling ordinary covariance propagation as a new estimator.
- **E111** is terminal NO-GO for deterministic Gaussian-ReLU moment plug-in: even when supplied the exact pre-ReLU mean and variance on an exact small reference, final mean-bias MSE was `1.6698051697168073e-3`, about `8.8349e4` times its frozen raw target.
- **E113** proves an exact annealed radial closure but shows that conditioning on the realized dense weight matrix destroys that scalar sufficiency; the frozen annealed-radial plug-in failed even when only the final layer was annealed.

Relevant exact internal sources:

- E111 result blob `61f4e243352fe9d7b505777d2503313700af77f0`:  
  https://github.com/tim8es/arc-whitebox/blob/research/e111-late4-gaussian-relu-plugin-cost-20260919/research/E111_RESULT.md
- E113 protocol blob `d117946ef36520bbeb20154874f1bc3d8c7835ad`:  
  https://github.com/tim8es/arc-whitebox/blob/research/e113-annealed-radial-sufficiency-20260919/research/E113_PROTOCOL.md
- E113 receipt blob `5cb50037b1c98cf02783b2ba8f186c175637497f`:  
  https://github.com/tim8es/arc-whitebox/blob/research/e113-annealed-radial-sufficiency-20260919/research/E113_RECEIPT.json

### Required R366/R373/R374/R375/R376 chain

| task | exact branch head | report blob | operative conclusion |
|---|---|---|---|
| R366 | `02305335c80161311e13839de3268be97a43e504` | `f2c512a04c1eb9b0d179cd04a5563e34a6f109aa` | shallow-ridge white-box flattening stopped for missing constructive certified map |
| R373 | `99a7e683ce4d0f0a603ecf601d9a2faf7d0b49cf` | `a77e81ad577ffcd655c0a8f5b44a58f00b309a6f` | material correction: population-mean certificate alone does not certify the fixed baked scorer target |
| R374 | `659ab891e1e7a27f0edadb8768b1e094420247ac` | `bcf7b9369628e85cff7fb0585a27e895f99a12a7` | lift-zonoid state is complete but lacks a finite ReLU-closed Phase-2 propagation theorem |
| R375 | `d917feba20206d5866981b84844e45a53fa24d93` | `45b69554fd53b9323b894fb391b5b9c334285c22` | a frozen target-free candidate may be evaluated directly against public Mini baked labels; no local labels/candidate were available |
| R376 | `3e61563bf46d09081dfae133407219763f27bf7f` | `999de9d6203ac263a5da1c9d1b1e20daba43488d` | single-global-affine Gaussian relaxation has a structural certificate floor and did not clear its fixed-panel admission gate |

Exact reports:

- R366: https://github.com/tim8es/arc-whitebox/blob/review/r366-uncovered-estimator-frontier-scout-20260924/research/r366/R366_UNCOVERED_ESTIMATOR_FRONTIER_SCOUT.md
- R373: https://github.com/tim8es/arc-whitebox/blob/review/r373-r366-shallow-ridge-independent-redteam-20260924/research/r373/R373_R366_SHALLOW_RIDGE_INDEPENDENT_REDTEAM.md
- R374: https://github.com/tim8es/arc-whitebox/blob/review/r374-next-distinct-estimator-frontier-20260924/research/r374/R374_NEXT_DISTINCT_ESTIMATOR_FRONTIER.md
- R375: https://github.com/tim8es/arc-whitebox/blob/research/r375-r366-fixed-scorer-test-20260924/research/r375/R375_R366_FIXED_SCORER_TEST.md
- R376: https://github.com/tim8es/arc-whitebox/blob/research/r376-new-estimator-frontier-20260924/research/r376/R376_NEW_ESTIMATOR_FRONTIER.md

## 2. Dedupe boundary

R381 excludes, without rescue or renaming:

- Monte Carlo, residual sampling, deterministic particles, cubature, sigma points, QMC/Sobol, spherical designs;
- control variates, Stein/JVP, antithetic/Haar/radial Rao–Blackwell;
- conditional-Gaussian/halfspace/orthant/mask-conditioned states;
- K3/K4/cumulant/Edgeworth/saddlepoint descendants;
- Hermite/PCE, TT/CP/Tucker, CountSketch/TensorSketch;
- characteristic-function/Hilbert-transform propagation;
- activation masks, activation regions, boundary flux, branch-and-bound over ReLU regions;
- response-aligned/adjoint observable corrections already in history;
- ordinary first-two-moment Gaussian/ReLU plug-in and official covariance propagation (E000/E111);
- annealed radial/fresh-weight closure (E113);
- R366 deterministic shallow-ridge flattening;
- R374 lift-zonoid / stop-loss distribution-state propagation;
- R376 GELR single-global-affine relaxation.

Repository-wide code search at the live state returned zero matches for:

- `DeepSDP`
- `semidefinite`
- `quadratic constraint`
- `SDP relaxation`
- `S-procedure`
- `Chordal-DeepSDP`
- `quadratic envelope`

Thus the one class below is not present in the audited ARC history.

## 3. Exactly one new class screened

### QGME-SDP — Quadratic Gaussian Mean Envelopes via semidefinite relaxation

The proposed representation is **not a propagated distribution state**.

For one fixed final output coordinate (f_j(x)) of the supplied zero-bias ReLU network, choose a deterministic Gaussian truncation radius (R) and define

[
K_R={xinmathbb R^{1024}:|x|_2le R}.
]

Use ReLU quadratic constraints plus the S-procedure/SDP machinery to seek two quadratic functions

[
ell_j(x)=x^	op A_jx+a_j^	op x+alpha_j,
qquad
u_j(x)=x^	op B_jx+b_j^	op x+eta_j
]

such that

[
ell_j(x)le f_j(x)le u_j(x)
qquad orall xin K_R.
]

This differs materially from R376 GELR:

1. the envelope is quadratic, not affine;
2. its Gaussian expectation contains a trace term, so the lower expected bound need not collapse to the affine intercept at (x=0);
3. the certificate is obtained from global quadratic constraints, not activation-region enumeration;
4. no samples, cubature nodes, Hermite coefficients, characteristic function, cumulant state, or shallow surrogate are introduced.

### Primary-source basis

Fazlyab, Morari & Pappas derive a quadratic-constraint/S-procedure SDP framework for feed-forward neural networks with general activations:

- Mahyar Fazlyab, Manfred Morari, George J. Pappas, **“Safety Verification and Robustness Analysis of Neural Networks via Quadratic Constraints and Semidefinite Programming,”** IEEE TAC 67(1), 2022.  
  Primary preprint: https://arxiv.org/abs/1903.01287  
  DOI: https://doi.org/10.1109/TAC.2020.3046193

Their probabilistic companion explicitly studies random input with known first two moments:

- Mahyar Fazlyab, Manfred Morari, George J. Pappas, **“Probabilistic Verification and Reachability Analysis of Neural Networks via Semidefinite Programming,”** CDC 2019.  
  Primary preprint: https://arxiv.org/abs/1910.04249  
  DOI: https://doi.org/10.1109/CDC40024.2019.9029310

Sparsity work proves that the cascade structure admits chordal SDP decompositions, while still emphasizing that scalability is the central issue:

- Matthew Newton, Antonis Papachristodoulou, **“Exploiting Sparsity for Neural Network Verification,”** L4DC 2021, PMLR 144.  
  Primary source: https://proceedings.mlr.press/v144/newton21a.html
- Anton Xue, Lars Lindemann, Rajeev Alur, **“Chordal Sparsity for SDP-based Neural Network Verification,”** Automatica 161 (2024), 111487.  
  Primary preprint: https://arxiv.org/abs/2206.03482  
  DOI: https://doi.org/10.1016/j.automatica.2023.111487

These sources justify the **sound quadratic-relaxation mechanism**. They do not claim that 16×1024 ARC networks can be solved inside the Phase-2 estimator budget, and they do not provide the Gaussian-mean objective used here. The expectation conversion below is R381's derivation.

## 4. Exact target-free Gaussian readout if the envelopes exist

Let

[
Xsim N(0,I_n),qquad n=1024,qquad S=|X|_2^2simchi_n^2.
]

Define

[
p_R=P(Sle R^2)
=rac{gamma(n/2,R^2/2)}{Gamma(n/2)}
]

and

[
	au_R
=rac1n E[S,1_{{Sle R^2}}]
=rac{2}{n}
rac{gamma(n/2+1,R^2/2)}{Gamma(n/2)}.
]

Rotational symmetry gives exactly

[
E[X,1_{K_R}]=0,
qquad
E[XX^	op 1_{K_R}]=	au_R I_n.
]

Therefore the core expectations of the certified quadratic envelopes are analytic:

[
L^{m core}_j
=
	au_R,operatorname{tr}(A_j)+p_Ralpha_j,
]

[
U^{m core}_j
=
	au_R,operatorname{tr}(B_j)+p_Reta_j.
]

The final ARC output is nonnegative because every layer ends in ReLU.

Let (Lambda_j) be any certified coordinate Lipschitz constant satisfying

[
0le f_j(x)le Lambda_j|x|_2.
]

The Gaussian radial tail moment is

[
ho_R
=
E[|X|_2,1_{{|X|_2>R}}]
=
sqrt2,
rac{Gamma((n+1)/2,R^2/2)}{Gamma(n/2)}.
]

Hence

[
oxed{
L_j(R)=max(0,L^{m core}_j)
}
]

and

[
oxed{
U_j(R)=U^{m core}_j+Lambda_jho_R
}
]

satisfy

[
L_j(R)le mu_j:=E[f_j(X)]le U_j(R).
]

The target-free point estimator is

[
oxed{
widehatmu_j(R)=rac{L_j(R)+U_j(R)}2
}
]

with exact population-mean certificate

[
oxed{
|widehatmu_j-mu_j|
le
h_j(R):=rac{U_j(R)-L_j(R)}2.
}
]

No target labels enter envelope construction or readout.

### Why this escapes the specific R376 theorem

R376's structural lower-bound failure is tied to a **single global affine** lower/upper relaxation. For an affine lower bound, symmetry kills the linear term in expectation and (f(0)=0) forces the useful lower intercept to be nonpositive.

QGME-SDP has

[
E[X^	op A X,1_{K_R}]=	au_Roperatorname{tr}(A),
]

so a valid quadratic lower envelope can have a positive expected trace contribution even though its value at the origin is nonpositive.

Therefore R376's affine (4.607%) certificate-floor derivation does not apply to QGME-SDP.

R381 does **not** claim that a sufficiently tight quadratic envelope exists at Phase-2 scale; that is the new gate.

## 5. Fixed Phase-2 scorer criterion

R373's correction is binding here.

The interval above certifies error against the mathematical population mean (mu_i). The official scorer uses the fixed baked target vector (y_i). Therefore R381 does **not** assert

[
operatorname{MSE}(widehatmu_i,y_i)
le
rac1{1024}sum_j h_{ij}^2
]

without an additional target-vs-population certificate.

R375 supplies the correct operational bridge: after a target-free estimator is completely frozen, direct evaluation against the fixed public Mini labels is valid development evaluation.

For a future authorized test, the exact GO criterion would be

[
oxed{
S_{m QGME}
=
rac1{100}sum_{i=1}^{100}
left[
rac1{1024}|widehatmu_i-y_i|_2^2
ight]
maxleft(0.1,rac{C_i}{2^{41}}ight)
<
8.170397440117225	imes10^{-9}.
}
]

That is tied to the actual fixed scorer target, not a random-weight or population-mean theorem.

R381 performs no such evaluation.

Official Phase-2 scoring source:

- https://github.com/AIcrowd/whest-starterkit/blob/main/docs/concepts/scoring-model.md
- current blob observed by R381: `f65e3700ad1874e563f4ef9d91bd2e0a8aa0ae7e`

It states:

- (B=2^{41}=2,199,023,255,552) FLOPs per MLP;
- (C_m=F_m) in Phase 2;
- valid per-MLP multiplier (max(0.1,C_m/B));
- final score is the suite mean of budget-adjusted final-layer MSE;
- residual cap 400 ms;
- wall cap 120 s.

Round source:

- https://github.com/AIcrowd/whest-starterkit/blob/main/docs/reference/rounds.md
- current blob observed by R381: `2aaf38a54b5d6ed83ce2604870dcac59e62cee59`
- solution-process memory cap: **8 GB**.

## 6. Phase-2 compute/memory/time gate

This is where QGME-SDP fails R381.

### 6.1 Dense lifted dimension

A direct lifted quadratic relaxation that keeps the input plus all 16 width-1024 activation vectors has an optimistic lifted matrix dimension

[
p=1+17cdot1024=17,409.
]

A single dense (p	imes p) float64 matrix contains

[
p^2=303,073,281
]

entries, or about

[
2.2581 {m GiB}.
]

Thus one matrix alone is below 8 GB, but a conventional SDP solver requires multiple primal/dual/work matrices plus factorization state; no source above gives an 8-GB guarantee for this ARC instance.

More importantly, dense cubic linear algebra is already outside a comfortable budget. Arithmetic proxies are:

[
p^3/3
approx1.7587	imes10^{12}
=0.7998,B
]

for one Cholesky-scale factorization, and

[
4p^3/3
approx7.0349	imes10^{12}
=3.1991,B
]

for one symmetric eigendecomposition-scale pass.

These are **arithmetic proxies, not FlopScope measurements**. They are used only to reject an unsupported assumption that a generic dense SDP solve is cheap.

### 6.2 Optimistic chordal proxy

The cited chordal work shows that neural-network SDP structure can be decomposed.

Give QGME-SDP the optimistic benefit of adjacent-layer blocks of only

[
b=2cdot1024+1=2,049
]

with 16 such blocks.

The resident float64 storage for one copy of those blocks is about

[
16b^2cdot8
approx0.5005 {m GiB}.
]

An optimistic one-pass arithmetic proxy is then

[
16b^3/3
approx4.5880	imes10^{10}
=0.02086,B
]

for Cholesky-scale work, or

[
16(4b^3/3)
approx1.8352	imes10^{11}
=0.08346,B
]

for eigen/projection-scale work.

This shows that **chordalization prevents an immediate memory impossibility**. It does not close the estimator budget.

### 6.3 The 1024-output obstruction

ARC needs 1024 final means.

QGME-SDP as derived needs a lower and an upper quadratic objective for every output coordinate: **2048 certified objectives per MLP**.

The primary sources formulate scalar safety/verification objectives. R381 found no source-backed theorem or algorithm that returns all 2048 expectation-optimal quadratic envelopes in one shared solve with certified gaps.

Even under the unrealistically favorable assumption of only **one** chordal Cholesky-scale pass per bound, independent objectives would cost

[
2048	imes4.5880	imes10^{10}
approx9.395	imes10^{13}
approx42.73,B.
]

Using the eigen/projection proxy gives about (170.92,B).

A real SDP solve is iterative, so these are not upper bounds; they are deliberately optimistic scale checks.

The exact missing computational result is therefore:

> a deterministic, FlopScope-admissible, shared multi-output quadratic-envelope solver that produces all 1024 lower and 1024 upper certificates for a 16×1024 dense ReLU MLP with total (Fle2^{41}), process memory (le8) GB, wall time (le120) s, and residual time (le0.4) s.

No audited primary source supplies such a result.

### 6.4 Time

No benchmark is allowed in R381, so no wall time is measured.

The cited DeepSDP literature explicitly identifies scalability as the main difficulty and develops chordal decompositions to improve it. None of the cited results establishes a 120-second bound for a 16×1024 dense network, much less 2048 output-bound objectives under the ARC execution model.

Therefore the time gate is **UNPROVEN**, not silently treated as zero.

## 7. Theory gate and falsifiability

QGME-SDP passes only the narrow mathematical representation gate:

- target-free construction: **YES**, conditional on solving the certified envelope problems;
- exact Gaussian readout of a certified quadratic envelope: **YES**;
- population-mean error interval: **YES**;
- distinct from GELR/shallow-ridge/lift-zonoid/sampling/moment-state/activation-region methods: **YES**.

It fails the required end-to-end estimator gate:

- Phase-2 all-output compute bound: **NO**;
- 8-GB solver-memory proof: **NO**;
- 120-s wall proof: **NO**;
- 0.4-s residual proof: **NO**;
- fixed-baked-target score improvement: **NOT EVALUATED and NOT CLAIMED**.

### Cheapest re-entry falsifier

No benchmark run is justified yet.

A future re-entry must first provide a **static shared-solver certificate**:

1. exact lifted/chordal formulation for one 16×1024 MLP;
2. a single deterministic algorithm that returns all 2048 envelope objectives;
3. exact FlopScope-countable operation schedule with (Fle2^{41});
4. peak candidate-owned memory (le8) GB including solver workspaces;
5. a deterministic iteration cap strong enough to imply wall (le120) s and residual (le0.4) s under the allowed execution path;
6. soundness proof for every returned quadratic envelope.

Only if those six items pass should a later, separately authorized experiment freeze (R) and all solver tolerances, then evaluate the frozen target-free estimator directly against the exact public `v2-phase2 mini:all-100` baked targets using the R375 scorer criterion.

No score improvement may be claimed before that direct fixed-target evaluation.

## 8. Why this NO-GO is different from R366/R374/R376

- **R366:** missing compact deterministic deep-to-shallow ridge flattening theorem.
- **R374:** complete lift-zonoid state exists, but no finite ReLU-closed propagation/certification operator.
- **R376:** single-global-affine Gaussian relaxation has a structural expectation-certificate floor.
- **R381:** quadratic envelopes avoid the specific affine floor and have an exact analytic Gaussian readout, but the certificate-generation problem is an SDP with no source-backed Phase-2-feasible **1024-output** solve. The blocker is scalable certified optimization, not absence of an expectation formula and not the R376 affine intercept argument.

This is an evidence-based feasibility NO-GO for QGME-SDP, not a theorem that all quadratic relaxations or all future ARC estimators are impossible.

## 9. Final verdict

[
oxed{	ext{NO_GO_QGME_SDP_PHASE2_SOLVER_AND_FIXED_SCORER_GATES_NOT_CLOSED}}
]

QGME-SDP is the sole genuinely distinct candidate found after the required dedupe.

It has a valid target-free mathematical estimator **if** certified quadratic envelopes can be produced, and its Gaussian readout is exact. It also genuinely escapes the specific single-affine structural argument from R376.

However, no primary source or project artifact supplies the missing shared 2048-objective Phase-2 solver theorem. Generic dense SDP scaling is already incompatible with the budget, while even optimistic chordal arithmetic requires a nontrivial multi-output amortization theorem that is absent. Time and full solver memory are likewise unproved.

R381 therefore stops before implementation or any numeric experiment.

## 10. Execution accounting

- candidate families screened after dedupe: **1**
- estimator implementation created: **NO**
- estimator runs: **0**
- synthetic runs: **0**
- benchmark runs: **0**
- scorer runs: **0**
- Actions runs: **0**
- downloads: **0**
- dependency installs: **0**
- submissions: **0**
- private/holdout/full access: **NO**
- R320 edits: **0**
- main edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**
- files added on R381 branch: **1**
