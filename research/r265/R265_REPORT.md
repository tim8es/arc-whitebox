# R265 method-theory scout result

Status: **EVIDENCE_BASED_NO_GO_BEFORE_EXECUTION**

Job: R265  
Owner: `method-theory-scout`  
Run: `R265-theory-screen-20260923`  
Protocol commit: `0b4406b79ba785ec716657c65ba75673dea99f92`

## Scope and pinned evidence

This pass was intentionally bounded to repository evidence plus primary literature. It did not access or execute R209/public benchmark data, did not run Actions/cloud, paid compute, holdout/private/full data, tuning, per-network selection, submission, canonical edits, or leaderboard edits.

Pinned inputs:

- `research/history.json` git blob `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`
- `AGENTS.md` git blob `6d9c61537a282a7d141af316dd8be438d1015a49`
- `research/RESEARCH_PROCESS.md` git blob `bf5a4676d8f36100e2dfdde32d544a39661eba8d`
- R261 actual report `research/r261/R261_TARGET_FREE_NO_GO.md` git blob `835eee8021cfc8760c50c1b6978dcdabf2e52a2e`
- R261 original receipt git blob `47b0d745cd31e8707256f0f7183d0d0212d9442e`
- R261 coordinator reconciliation git blob `5cce867616e893cce4859e26c832fd94e826f153`
- `research/results/R209-v25-mini100.json` git blob `0183d0570f7c9965e00e8553ffc003c313865232`
- `research/results/R223-v25-local-feed-mini100.json` git blob `c8b617c43ff1145977c38e7e1cca6d23985ec392`

The R261 report/receipt blob mismatch is preserved rather than silently repaired: the original receipt declared report blob `84df1b3ecbc86c4564a0c29148e49cf57a9a4528`, while the actual report blob is `835eee8021cfc8760c50c1b6978dcdabf2e52a2e`. The coordinator reconciliation records that mismatch and restores the queue provenance without rewriting the original evidence.

## Strongest compatible normalized record

The exact-panel normalized registry makes `R209-v25-mini100` the strongest compatible V25 reference currently loaded:

- 100 networks, failures `0/100`
- mean final MSE `2.228303490170447e-08`
- mean adjusted score `8.170397440117225e-09`
- mean measured FLOPs/network `806303721965`

`R223-v25-local-feed-mini100` is exactly panel-compatible but worse:

- mean final MSE `2.2284993050902814e-08`
- mean adjusted score `8.171116513490032e-09`
- mean measured FLOPs/network `806303829485`
- adjusted-score ratio vs R209: about `1.000088`
- development verdict: `SCIENTIFIC_REJECT`

No rank claim or transfer from a different panel is used.

## Full-history novelty check

The complete current `research/history.json` was parsed: **194 E-IDs (E000-E193), 631 artifact records, 45 MISSING entries and 4 LEGACY_ONLY entries**. The current R227-R261 queue evidence was also checked so that a post-history method is not reintroduced under a new label.

Mechanism families already represented include:

1. residual/control-variate sampling, antithetic sampling, orthogonal/Haar designs, QMC/Sobol, cubature/sigma-point/frame methods;
2. covariance, conditional-Gaussian, mixture, cumulant/K3/K4, Edgeworth, saddlepoint, gate-conditioned and exact-mask closures;
3. polynomial/TensorSketch, Hermite/chaos, shared-basis/DEIM, TT, CP, Kronecker, Legendre, hypergraph and other low-rank/compression families;
4. response-aligned, adjoint/JVP, gradient, observable and boundary-flux methods;
5. regression/calibration/cross-fit/shrinkage families;
6. source-age/window/tail truncations and young/old-tier sparsification;
7. exact/approximate arithmetic and fast-matmul/reassociation transformations, including the R260 BPK2k lane.

Recent R2xx evidence additionally closes or reserves SRM2, DRRE, RSRF, MP-R16, young-D21 right-sparsification, rank-1 Kronecker transport, rank-1 Legendre AP transport, GFNP, D21-CWG/CFSP4, and BPK2K. R261 separately rejected speculative removal of the public-fitted online mean-correction rider.

## One literature lead screened: randomized multilevel debiasing

The only family distinct enough to survive the lexical/mechanism deduplication long enough for a feasibility check was **randomized multilevel debiasing / randomized telescoping**.

Primary sources:

- Michael B. Giles, “Multilevel Monte Carlo Path Simulation,” *Operations Research* 56(3), 607-617 (2008), DOI `10.1287/opre.1070.0496`.
- Chang-Han Rhee and Peter W. Glynn, “Unbiased Estimation with Square Root Convergence for SDE Models,” *Operations Research* 63(5), 1026-1043 (2015), DOI `10.1287/opre.2015.1404`.

For a nested approximation sequence \(Y_0,Y_1,\ldots\) converging to \(Y\),

\[
E[Y_L] = E[Y_0] + \sum_{\ell=1}^{L} E[Y_\ell-Y_{\ell-1}].
\]

MLMC allocates effort across level differences according to their variance and cost. Rhee-Glynn randomization can remove truncation bias when a randomized telescoping construction has sufficiently decaying correction variance relative to level cost.

### Why it does not become an R265 candidate

A concrete V25-compatible hierarchy is mandatory before this is an estimator rather than a label. Every natural hierarchy available from the pinned code/history lands on an already-explored axis:

- **sample count / stochastic residual hierarchy** -> residual/control-variate sampling already tested (notably E001 and later antithetic/QMC work);
- **rank / basis / tensor-order hierarchy** -> extensive low-rank, TT/CP, response-aligned and recent R247/R248/R250 structural compression work;
- **source-age/window hierarchy** -> prior exact-window, age-tier and young/old-tier truncation work;
- **arithmetic precision/reassociation hierarchy** -> numerical-stability/arithmetic lanes including BPK2K.

More importantly, there is **no committed target-free evidence** showing a nested level-difference error/variance decay law for any non-duplicative hierarchy, and without such a hierarchy there is no honest full production FLOP expectation to bound. The core condition that makes MLMC/Rhee-Glynn useful—corrections getting cheaper in variance faster than they get expensive in cost—is therefore unestablished here.

Instantiating arbitrary levels now and running them merely to see what happens would violate the assignment's requirement for a pre-existing plausible target-free signal and would amount to method fishing. Reusing a rank/source/sampling hierarchy would also fail the novelty requirement.

## Decision

**NO_GO before prototype and before falsifier execution.**

R265 found no concrete estimator family that simultaneously satisfies:

- full-history novelty;
- a defensible target-free mechanism signal before execution; and
- a derivable, plausibly score-competitive production cost bound.

No estimator prototype was created and local synthetic falsifier count is zero. This is not a scientific rejection of randomized multilevel debiasing in general; it is a bounded rejection of launching it here without the required non-duplicative hierarchy and evidence.

## Accounting

- estimator prototypes created: `0`
- local synthetic falsifiers executed: `0`
- estimator/benchmark executions: `0`
- Actions/cloud runs: `0`
- public/R209 benchmark accesses: `0`
- private/holdout/full accesses: `0`
- paid compute: `0`
- tuning/per-network selection: `0`
- submissions: `0`
- canonical/leaderboard edits: `0`
