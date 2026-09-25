# R389 — research portfolio decision memo

**Status:** COMPLETE  
**Purpose:** coordinator decision memo only; no new estimator search, implementation, benchmark, download, Actions, or submission  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `research/r389-portfolio-decision-20260925`

## Executive decision

**Primary path: R385 multi-shell clipped GELR.**

Evidence-based portfolio order at the time of this review:

1. **R385 — multi-shell clipped GELR**
2. **R386 — Gaussian-even weight-only shallow representation**
3. **R387 — low-cost quadratic envelopes / QGME rescue, currently evidence-incomplete**

This is a **research-priority ranking**, not a score/rank prediction and not a claim that any path beats R209 or any leaderboard entry.

The decisive reason is readiness:

- R385 already defines a target-free estimator/certificate, a strict mathematical improvement over the exact R376 single-shell certificate, a static Phase-2 compute/memory envelope, and an explicit fixed-panel certificate gate.
- R386 proves useful representation facts but still lacks the central algorithm (W	o
u_W) / coefficients; its transform cost is therefore unknown.
- R387 has no committed scientific artifact at review time. Its branch exists but is still exactly at main base, so only the inherited R381 QGME-SDP blocker is evidence.

If R387 later produces a committed sound low-cost quadratic survivor, this ranking should be revisited.

## 1. Exact evidence set

### R380 — one-hidden-layer odd-part constraint

- branch: `research/r380-r366-constructive-transform-20260925`
- head: `3161672099dbba6df02251ff287595dd792e59e2`
- report blob: `5f9bd8b15936947ea0de67377fb950c6aebd5c49`
- report:  
  https://github.com/tim8es/arc-whitebox/blob/3161672099dbba6df02251ff287595dd792e59e2/research/r380/R380_CONSTRUCTIVE_SHALLOW_READOUT.md

Operative result:
for every bias-free one-hidden ReLU surrogate
(g(x)=Aoperatorname{ReLU}(Bx)),

[
g(x)-g(-x)=ABx,
]

so its odd part is exactly linear. This blocks general whole-function flattening but **does not block population-mean recovery**, because the odd part integrates to zero under centered Gaussian input. The remaining escape is the even component.

Primary sources cited by R380 include:
- positive-homogeneous one-hidden restriction: https://doi.org/10.1016/j.jat.2025.106177
- exact three-hidden constructive flattening with activation-region recovery: https://journals.sagepub.com/doi/10.3233/FAIA251170

### R381 — QGME-SDP

- branch: `research/r381-new-estimator-search-20260925`
- head: `d2dca21dfd51911b9a131c175243820c435be5ff`
- report blob: `a0238ea75703aa05341c463bcbdc7e0e361cbf27`
- report:  
  https://github.com/tim8es/arc-whitebox/blob/d2dca21dfd51911b9a131c175243820c435be5ff/research/r381/R381_NEXT_ESTIMATOR.md

Verdict:
`NO_GO_QGME_SDP_PHASE2_SOLVER_AND_FIXED_SCORER_GATES_NOT_CLOSED`.

The mathematical representation is valid:
a certified quadratic lower/upper envelope has analytic Gaussian expectation and can escape R376's affine-intercept floor.

The blocker is all-output certified optimization:
- direct lifted dimension (p=17,409);
- one dense float64 matrix ~2.258 GiB;
- optimistic chordal adjacent-layer block (b=2,049);
- one optimistic chordal Cholesky-scale pass ~(4.5880	imes10^{10}) operations;
- QGME needs **2048 objectives** per MLP;
- even one such proxy pass per objective gives ~(9.395	imes10^{13}), about 42.73 Phase-2 budgets;
- no source-backed shared solver closes (2^{41}), 8 GB, 120 s, and 0.4 s simultaneously.

Primary SDP sources:
- Fazlyab et al.: https://arxiv.org/abs/1903.01287
- DeepSDP: https://arxiv.org/abs/1910.04249
- sparse verification: https://proceedings.mlr.press/v144/newton21a.html
- chordal sparsity: https://doi.org/10.1016/j.automatica.2023.111487

### R382 — no-download fixed-panel route

- branch: `research/r382-aicrowd-no-download-test-route-20260925`
- head: `491df3e98adb4c60077350ad0481ec2cd3b601ab`
- report blob: `0f6da35d7dd2de222ecda49a79c1223d1f43451d`
- report:  
  https://github.com/tim8es/arc-whitebox/blob/491df3e98adb4c60077350ad0481ec2cd3b601ab/research/r382/R382_NO_DOWNLOAD_EVALUATION_ROUTE.md

Verdict:
`NO_DOCUMENTED_NO_SLOT_PUBLIC50_VALIDATION_ROUTE`.

Important portfolio consequence:

- `whest run` without `--dataset` is **synthetic/local**, not Mini-100 and not public-50.
- fixed development Mini-100 is a real scorer panel, but needs the published dataset locally/cached; a first fetch is ~7.03 GB.
- live public-50 evidence comes through an ordinary submission on the audited official participant surface.
- no documented participant-facing no-slot public-50 scoring endpoint was found.

Therefore, under a strict **no-download/no-submission** research allocation, the next useful evidence must be target-free/static or use already-local network payloads. None of R385/R386/R387 can honestly claim fixed-target public-50 validation from a synthetic local run.

### R383 — affine escape

- branch: `research/r383-gelr-independent-redteam-20260925`
- head: `31b79a0896de889b190b141a2f5c2a7da0967346`
- report blob: `6e8216e136924553a24f81d165abdebaf0941ae8`
- report:  
  https://github.com/tim8es/arc-whitebox/blob/31b79a0896de889b190b141a2f5c2a7da0967346/research/r383/R383_GELR_REDTEAM.md

R383 confirms R376 only as a **narrow** single-shell/zero-lower-endpoint no-go.

Two concrete escapes are valid:
1. clip the affine lower bound with network nonnegativity, ([ell(x)]_+);
2. use nested symmetric truncation shells, which strictly reduce the affine upper certificate while reusing one homogeneous affine relaxation.

Primary bound-propagation / Gaussian-affine sources:
- Fast-Lin: https://proceedings.mlr.press/v80/weng18a.html
- CROWN: https://proceedings.neurips.cc/paper/2018/hash/d04863f100d59b3eb688a11f95b0ae60-Abstract.html
- PROVEN: https://proceedings.mlr.press/v97/weng19a.html

This is the key reason R385 is not merely a retest of the failed R376 certificate.

### R384 — package/evaluator reconciliation

- branch: `research/r384-r223-package-reconcile-20260925`
- head: `cc24aef868c354feb45910e01233ed7d287e467c`
- report blob: `6fb4a79a68ba339e9dfd419f76e6381a489c69ec`
- report:  
  https://github.com/tim8es/arc-whitebox/blob/cc24aef868c354feb45910e01233ed7d287e467c/research/r384/R384_R223_PACKAGE_RECONCILIATION.md

Portfolio implication:
packaging-version mismatch is **not** presently a scientific blocker.

Official WhestBench manifest generation records the **local packager environment** versions. The current starter kit is on 0.16.1/0.12.1 while the published live evaluator statement remains 0.16.0/0.12.0; the v0.16.0 package validator checks schema/API/entrypoint/files/hashes rather than equality of those provenance version fields.

Primary sources:
- WhestBench packaging source:  
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/packaging.py
- current starter-kit version explanation:  
  https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/pyproject.toml
- WhestBench changelog:  
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/CHANGELOG.md

R384 does not make R223 scientifically viable; it only removes an incorrect package-existence/version inference.

## 2. Active path A — R385 multi-shell clipped GELR

Exact artifact:

- branch: `research/r385-multishell-clipped-gelr-20260925`
- head: `2ba08cb916cc504f1c38673971c2aa811b2da48c`
- report blob: `08a04c634f9b489092d4f3636799908cdf51a1a6`
- report:  
  https://github.com/tim8es/arc-whitebox/blob/2ba08cb916cc504f1c38673971c2aa811b2da48c/research/r385/R385_MULTISHELL_CLIPPED_GELR.md

Verdict:
`CONDITIONAL_GO_FOR_EXPLICIT_CERTIFICATE_AND_STATIC_COMPUTE_ENVELOPE__NO_GO_FOR_SCORE_IMPROVEMENT_CLAIM_WITHOUT_FIXED_NETWORK_AND_TARGET_TENSORS`.

### Concrete candidate

R385 is already an explicit estimator/certificate:
[
L_{m MS}lemule U_{m MS},
qquad
widehatmu=(L_{m MS}+U_{m MS})/2.
]

Its radius strictly improves the R376 single-shell radius iff
[
Delta U_{m shell}+L_{m MS}>0.
]

The lower shell certificate uses only Gaussian PDF/CDF, norms, probabilities and sound loss terms; it does not pretend the exact oblique cube-shell integral is one-dimensional.

### Implementability without data download

**Relative assessment: HIGHEST of the three; qualitative confidence MEDIUM, not a statistical probability.**

Why:
- formulas are explicit;
- affine bounds are standard CROWN/Fast-Lin-type objects;
- shell readout is fully specified and target-free;
- no competition target is needed to construct the estimator;
- no additional network-evaluation sampling is part of the mechanism.

What is still missing:
- a concrete allowed-code implementation of the affine pass;
- exact FlopScope trace;
- measured wall/residual/RSS;
- network-specific certificate widths.

The weights themselves must of course be available to `predict()`; “no data download” here means no separate benchmark/target dataset is required to define the candidate.

### Expected Phase-2 budget

R385 inherits the frozen R376 affine acquisition envelope:
[
C_{m affine}le138,512,695,296.
]

For (K=64),
[
C_{m read}le16,015,232,
]
so
[
C_{m total}(64)le138,528,710,528.
]

That is
[
0.0629955641343258321,B
]
of the full (B=2^{41}) budget, hence below the 10% scorer multiplier floor **if the affine implementation realizes the frozen envelope**.

Memory is also statically modest:
R376 acquisition envelope (le256) MiB plus only single-digit MiB of representative shell workspace for (K=64).

This is still **not a measured production ledger**. Wall and residual time remain unknown.

### Fixed-target scorer testability

**Best-defined of the three, but not executable under R389's no-download/no-run restriction.**

R385 already states an exact sufficient same-panel certificate gate:
[
rac1{100}sum_i H_i^2
max!left(0.1,C_i/2^{41}ight)
<
8.170397440117225	imes10^{-9}.
]

If all rows are below the compute floor, it simplifies to
[
rac1{100}sum_i H_i^2
<
8.170397440117225	imes10^{-8}.
]

This is a certificate-level gate against the stored R209 same-panel number, not a score claim.

Actual fixed-target MSE still needs fixed targets or an official scorer result. Per R382:
- no-dataset `whest run` cannot answer this;
- Mini-100 can answer it only if the dataset is already cached/otherwise authorized;
- public-50 requires the normal submission route.

### Most decisive next falsifier

Use **already-local exact network payload only, with targets hidden**:

1. freeze (K) and radii;
2. implement one vectorized allowed-code affine pass plus R385 readout;
3. measure only:
   - exact all-in FlopScope cost,
   - residual time,
   - wall time,
   - peak RSS,
   - (L,U,h,H_i^2);
4. stop on any resource failure;
5. only if the aggregate certificate gate is viable should a later separately authorized fixed-target scorer test occur.

This is the shortest path from theory to a candidate without spending a submission slot.

## 3. Active path B — R386 Gaussian-even weight-only shallow representation

Exact artifact:

- branch: `research/r386-gaussian-even-weight-only-20260925`
- head: `f04cd5096aad9824df495d34f509898810c3f5d9`
- report blob: `ebfe68a4329f2c73106ddaaaed06dd583fab8381`
- report:  
  https://github.com/tim8es/arc-whitebox/blob/f04cd5096aad9824df495d34f509898810c3f5d9/research/r386/R386_GAUSSIAN_EVEN_WEIGHT_ONLY.md

Verdict:
`NARROW_NO_GO_MISSING_WEIGHT_TO_CONTROLLED_COSINE_MEASURE`.

Primary mathematical sources:
- cosine transform density: https://doi.org/10.1016/j.aim.2022.108361
- finite zonoid/shallow approximation: https://doi.org/10.1007/s00365-025-09712-9
- zonal construction: https://doi.org/10.1016/j.jco.2018.09.002
- ridgelet reconstruction: https://doi.org/10.1016/j.acha.2015.12.005
- exact CPWL flattening route: https://journals.sagepub.com/doi/10.3233/FAIA251170
- depth-separation warning: https://proceedings.mlr.press/v49/eldan16.html

### Concrete candidate probability without data download

**Relative assessment: LOW.**

R386 establishes:
- existence/density of signed cosine representations for even spherical functions;
- analytic Gaussian readout;
- finite-(r) sparsification **if** a finite-variation measure is already known.

But it does **not** supply the candidate-generating algorithm:
[
W	o
u_W	o{(a_j,u_j)}.
]

That missing bridge is not an implementation detail; it is the central scientific object.

Function-evaluation fitting would collapse back into sampled/cubature regression, while exact activation-region recovery has exponential worst-case structure.

### Expected Phase-2 budget

**UNKNOWN / not established.**

Readout is cheap conditional on atoms:
- direct cosine storage: (8192r) bytes;
- leading readout ~(4096r) scalar FLOPs;
- memory binds before readout FLOPs.

But the unknown construction/certification cost
(C_{m transform})
dominates the decision. No all-in Phase-2 bound exists.

### Fixed-target scorer testability

**LOW until a candidate exists.**

The conditional population certificate
[
mathrm{MSE}_{m population}le V^2/(1024r)
]
is not a fixed-Mini certificate.

After a target-free (W	o)atoms algorithm is frozen, R382/R375 logic permits later direct Mini scoring if the fixed Mini data are locally available/authorized; live public-50 still requires submission.

At present there is nothing concrete to score.

### Most decisive next falsifier

Do **not** run an ARC benchmark.

Require a proposed bridge on a tiny exact zero-bias deep ReLU fixture (2D/3D, depth ~3):
- emit signed atoms,
- emit variation (V), width (r), operation/workspace formula,
- compare claimed spherical error against exact conical-region reference,
- verify analytic Gaussian readout,
- extrapolate cost to 1024×16.

Immediate failure if:
- coefficients require a fitted target-evaluation grid;
- exact recovery requires unbounded activation-region enumeration;
- no (V(W))/width bound exists;
- no construction FLOP/workspace bound exists.

### Stop criterion

**Stop allocating implementation time now.**

Reopen R386 only when a concrete weight-only (W	o
u_W) / coefficient algorithm is written down with:
1. finite error certificate,
2. explicit variation/width control,
3. exact/upper-bounded construction cost and memory,
4. no target/function-sample fitting.

Existence/density theory alone is no longer sufficient for another research cycle.

## 4. Active path C — R387 low-cost quadratic envelopes

Expected branch:
`research/r387-qgme-cheap-certificates-20260925`.

At R389 review time:

- live head: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`;
- ahead of exact base: **0**;
- changed files: **0**;
- committed `research/r387/` report/receipt: **none**.

Therefore **R387 has no completed evidence artifact to synthesize**. R389 does not infer a survivor or a no-go from an assignment description.

### What can be inherited safely

Only R381 can be used:
- quadratic Gaussian envelopes are mathematically sound if certified;
- Gaussian readout is analytic;
- quadratic envelopes can evade the exact R376 affine-floor argument;
- generic/full QGME-SDP is not Phase-2 feasible as audited;
- the missing object is a shared all-output certified solver/relaxation.

R387's intended low-cost structures — diagonal, bounded block-diagonal, low-rank-plus-diagonal, or cached/shared objectives — are precisely possible ways to attack that blocker, but **none has a committed R387 soundness/cost/tightness result yet**.

### Concrete candidate probability without data download

**UNKNOWN; portfolio priority LOW until a report exists.**

The mechanism does not inherently require target data, but no committed low-cost certificate has yet been shown to be:
- sound through the full 16×1024 network;
- sufficiently expressive to escape the useful affine/GELR limitation;
- bounded under Phase-2 resources.

### Expected Phase-2 budget

**UNKNOWN for R387.**

Inherited full QGME-SDP is a no-go:
one optimistic 2048-objective chordal proxy is already ~(9.395	imes10^{13}), far above (2^{41}).

A structured low-cost variant could change that conclusion only if its exact decision-variable count, solve/arithmetic schedule and memory are explicitly proved.

### Fixed-target scorer testability

**Not yet available.**

If a low-cost quadratic estimator is eventually frozen, its output can use the same fixed-target scorer route as any estimator. R381 already gives the formal fixed-Mini criterion. R382 still blocks no-slot public-50 validation.

No R387 estimator exists today to exercise that route.

### Most decisive next falsifier

The next step is **desk completion, not implementation**.

For one proposed structured family only, require:
1. sound lower and upper quadratic envelopes;
2. exact number of stored/optimized variables;
3. exact worst-case all-output arithmetic schedule;
4. peak memory;
5. deterministic iteration/solve bound or closed-form solve;
6. proof that all 2048 output bounds share enough work to fit (2^{41});
7. explicit reason the restricted quadratic family can produce a strictly tighter expectation interval than the relevant GELR certificate.

### Stop criterion

Close R387 immediately if no one structured family satisfies all of:
- soundness,
- all-output Phase-2 compute/memory bound,
- deterministic wall/residual plausibility,
- a non-vacuous escape from the affine certificate limitation.

Do **not** allocate implementation time to generic SDP or to a structured family whose only argument is “fewer variables.”

If a committed R387 report later establishes one survivor, compare it directly against R385 before any run.

## 5. Four-criterion portfolio comparison

The words below are qualitative evidence assessments, not calibrated probabilities.

| Priority | Path | (a) Concrete implementable candidate without data download | (b) Expected Phase-2 budget | (c) Fixed-target scorer testability | (d) Most decisive next falsifier |
|---|---|---|---|---|---|
| **1** | **R385 multi-shell GELR** | **MEDIUM / highest**: explicit formulas and implementation schedule; no target data needed for construction | **Conditional favorable**: (K=64) static total (le138,528,710,528approx0.0630B), memory small; exact timing/billing still unknown | **Best-defined**: explicit R209 certificate gate; real fixed target still needs cached/authorized Mini or ordinary submission | Implement one target-hidden, vectorized affine+shell pass on already-local network payload; measure cost/time/RSS and (H_i^2) only |
| **2** | **R386 Gaussian-even ridge** | **LOW**: representation exists but (W	o
u_W) algorithm absent | **UNKNOWN**: readout cheap, transform cost unbounded/unknown | **LOW** until a transform exists; population bound is not Mini bound | Tiny exact 2D/3D weight-only bridge test with (V,r,epsilon), operation/workspace proof |
| **3** | **R387 low-cost QGME** | **UNKNOWN**: no committed R387 candidate at review time | **UNKNOWN / inherited full-SDP bad**: full QGME far over budget; cheap structures unaudited | **Unavailable today**; formal scorer route exists only after a candidate is frozen | Static soundness + exact all-output complexity proof for exactly one structured quadratic family |

## 6. Coordinator recommendation

### Primary allocation: R385

Allocate the next bounded scientific implementation/falsifier slot to **R385**, not to a scorer run.

The implementation should be target-blind and should terminate before fixed-target scoring unless it passes resource and certificate gates.

Recommended first configuration:
- modest frozen shell count such as (K=16) or (64);
- one vectorized allowed-code affine pass;
- vectorized FlopScope Gaussian readout;
- no target labels during candidate construction.

**R385 stop immediately if**:
1. the actual affine implementation cannot fit (2^{41}), 8 GB, 120 s, or 0.4 s residual;
2. it cannot stay at/near the expected low compute multiplier for a practical (K);
3. intervals are so wide on target-hidden fixed networks that the R385 aggregate certificate gate cannot be plausibly approached;
4. implementation requires forbidden/unmetered scalar numerical work.

Only after passing that stage should a separately authorized fixed-Mini scorer comparison be considered.

### R386: hold / stop

Do not spend implementation or benchmark resources on R386 now.

Reopen only on presentation of the missing direct weight-only controlled-measure algorithm with width/error/cost bounds. Otherwise the line remains mathematically interesting but operationally non-candidate.

### R387: theory-only stop gate

Do not implement R387 yet.

Allow only the narrow static completion already defined by the R387 research question. If no single structured quadratic family yields a proof-grade sound certificate with all-output Phase-2 resource bounds and a meaningful affine-floor escape, close the line.

If such a survivor is committed, it may replace R386 as the secondary implementation candidate, but it should still be compared against R385's much more mature cost envelope first.

## 7. Testing and submission assumptions

R389 assumes:

1. no benchmark/data download is authorized here;
2. no estimator/synthetic/official run is authorized here;
3. no submission is authorized here;
4. R382 remains binding: synthetic no-dataset `whest run` is not fixed-panel evidence and no documented no-slot public-50 route exists;
5. R384 means package-tool version provenance is manageable and should not drive research selection;
6. R209's stored score is used only as a **same-panel future gate value**, not as a prediction of public-50 performance;
7. no path is assigned a leaderboard score, public-50 gap, or contest rank.

## 8. Bottom line

**Choose R385 as the primary research path.**

It is the only one of the three that currently has all of:
- a concrete target-free estimator/certificate definition;
- a proved strict improvement over its immediate failed parent certificate;
- a plausible static all-in Phase-2 compute/memory envelope;
- an explicit scorer-level falsification inequality;
- a short target-hidden implementation falsifier before any slot or fixed-target run.

R386 has a theorem/algorithm gap before it becomes an estimator.

R387 may still become competitive, but at review time it has no committed result beyond the inherited R381 problem statement and cost blocker. Treat it as theory-only until that changes.

No score, leaderboard rank, or public-50 improvement is claimed for any path.

## 9. Execution accounting

- new estimator search: **NO**
- estimator implementation: **NO**
- estimator/synthetic/benchmark/scorer runs: **0**
- Actions: **0**
- downloads: **0**
- dependency installs: **0**
- paid resources: **NO**
- private/holdout/full access: **NO**
- submissions: **0**
- R320/main/PR/control/queue edits: **0**
- R389 artifact: exactly this Markdown memo
