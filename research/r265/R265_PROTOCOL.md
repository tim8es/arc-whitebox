# R265 protocol-first theory screen

Job: R265  
Owner: `method-theory-scout`  
Mode: offline/read-only theory + repository evidence screen. No public/R209 data access, no Actions/cloud, no paid resources, no private/holdout/full data, no tuning, no per-network selection, no submission, no canonical/leaderboard edits.

## Pinned repository inputs

- control claim base: `829887822daf04f5d88ed43c9568d24a4a5e3407`
- `research/history.json` blob: `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`
- `AGENTS.md` blob: `6d9c61537a282a7d141af316dd8be438d1015a49`
- `research/RESEARCH_PROCESS.md` blob: `bf5a4676d8f36100e2dfdde32d544a39661eba8d`
- R261 report `research/r261/R261_TARGET_FREE_NO_GO.md`: actual blob `835eee8021cfc8760c50c1b6978dcdabf2e52a2e`
- R261 original receipt blob: `47b0d745cd31e8707256f0f7183d0d0212d9442e`
- R261 coordinator reconciliation blob: `5cce867616e893cce4859e26c832fd94e826f153`
- normalized `R209-v25-mini100` blob: `0183d0570f7c9965e00e8553ffc003c313865232`
- normalized `R223-v25-local-feed-mini100` blob: `c8b617c43ff1145977c38e7e1cca6d23985ec392`

R261's receipt/report blob mismatch is treated as preserved provenance evidence; the actual report blob above and the coordinator reconciliation are authoritative for this screen.

## Strongest compatible normalized reference

On the identical 100-network Phase-2 mini development panel:

- R209 V25: mean final MSE `2.228303490170447e-08`, mean adjusted score `8.170397440117225e-09`, mean measured FLOPs/network `806303721965`, failures `0/100`.
- R223 V25 local-feed: mean final MSE `2.2284993050902814e-08`, mean adjusted score `8.171116513490032e-09`, mean measured FLOPs/network `806303829485`, failures `0/100`; development verdict SCIENTIFIC_REJECT.

Therefore any surviving R265 candidate would use R209 V25 as immediate parent/strongest compatible comparator. No public panel will be read or executed in R265.

## Full-history novelty screen

The complete current `research/history.json` was parsed, including all 194 E000-E193 entries and every recorded artifact/ref/legacy row. The screen also checks completed/current R227-R261 method jobs.

Already occupied families include: residual/control-variate sampling; antithetic/orthogonal/Haar designs; QMC/Sobol/cubature/sigma-point/frame methods; covariance and conditional-Gaussian closure; cumulant/K3/K4/Edgeworth/saddlepoint methods; mixture and gate-conditioned closure; polynomial/Hermite/chaos methods; low-rank/shared-basis/DEIM/TT/CP/Kronecker/Legendre/hypergraph compression; response/adjoint/JVP/gradient/boundary-flux methods; regression/calibration/cross-fit/shrinkage; and arithmetic/reassociation/fast-matmul compute transforms including BPK2K.

## Single external literature lead

The only distinct accuracy-first family retained long enough for a feasibility check is randomized multilevel debiasing / randomized telescoping.

Primary sources:
- M. B. Giles, “Multilevel Monte Carlo Path Simulation,” *Operations Research* 56(3), 2008, DOI 10.1287/opre.1070.0496.
- C.-H. Rhee and P. W. Glynn, “Unbiased Estimation with Square Root Convergence for SDE Models,” *Operations Research* 63(5), 2015, DOI 10.1287/opre.2015.1404.

Mathematically, for a nested approximation sequence (Y_0,Y_1,dots) converging to (Y), the telescoping identity
[
E[Y_L]=E[Y_0]+sum_{ell=1}^L E[Y_ell-Y_{ell-1}]
]
permits allocating more samples to cheap coarse differences and fewer to expensive fine differences. Rhee-Glynn randomization can remove finite-level truncation bias when correction variance decays sufficiently relative to level cost.

### Pre-execution feasibility gate

This family is allowed to proceed only if all are true before coding:
1. a V25-compatible, network-agnostic nested hierarchy is specified without reusing a closed rank/compression/sampling family under another name;
2. a deterministic target-free fixture provides a pre-existing signal that level-difference error/variance decreases with level fast enough to justify the expected added work;
3. a full metered production FLOP bound can be derived for the randomized/telescoping estimator; and
4. the resulting score tradeoff is plausibly favorable relative to R209 without per-network selection.

If any item is unavailable, R265 terminates evidence-based NO_GO before prototype/falsifier execution. No speculative run is permitted.
