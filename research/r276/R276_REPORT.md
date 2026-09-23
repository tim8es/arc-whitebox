# R276 — global V25 accuracy research screen

Status: **EVIDENCE_BASED_NO_GO_BEFORE_IMPLEMENTATION**

Job: R276  
Owner: `v25-accuracy-research`  
Run: `R276-v25-global-accuracy-screen-20260923`  
Protocol commit: `4749fd4a28ecd4e717b93e76c0efc2794370229b`

## Pinned evidence

- V25 source commit: `dff3dd65e9d2210e02418cca99e05556f6bf2c75`
- V25 source blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- R209 normalized mini:all-100 blob: `0183d0570f7c9965e00e8553ffc003c313865232`
- current full history blob: `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`
- R265 report blob: `e9b5df06173bf70a587774f9374042962847d9e2`
- R269 report blob: `8ea0fdf39e80483d005b0a9828f75a4eae291ee3`
- R273 receipt SHA256: `3c74ead349c98eab12e971feb9f7dd74c7f1e4f2520338880a3a83df57a89f8e`

R209 remains the pinned development reference: 100 networks, 0 failures, mean final-layer MSE `2.228303490170447e-8`, mean adjusted score `8.170397440117225e-9`, mean measured FLOPs `806303721965`.

## Full-history deduplication

The current history contains 194 E-IDs / 631 artifact records in the last complete full-history screen, plus the post-history R2xx work. Mechanism classes already represented include:

1. residual/control-variate, antithetic, orthogonal/Haar, QMC, cubature/frame sampling;
2. covariance, conditional-Gaussian/mixture, cumulant K3/K4, Edgeworth, saddlepoint, gate-conditioned and exact-mask closures;
3. polynomial/TensorSketch, Hermite/chaos, shared-basis/DEIM, TT, CP, Kronecker, Legendre and other low-rank/compression families;
4. response-aligned, adjoint/JVP, gradient/observable and boundary-flux corrections;
5. regression/calibration/cross-fit/shrinkage;
6. source-age/window/tail truncation, young/old-tier sparsification;
7. arithmetic/reassociation/fast-matmul transformations.

Recent explicit R2xx lanes additionally cover or reserve:

- R223: V25 local-feed lambda — worse same-panel score;
- R227: SRM2 / second regeneration mode — pre-science cost/deployability NO-GO;
- R232: DRRE — no valid measurement, protocol-terminal execution failure;
- R238: RSRF — base-executability failure before candidate;
- R244: MP-R16 — valid mini:all-100 measurement, worse adjusted score and MSE;
- R247: young-D21 right sparsification — target-free fidelity failure;
- R248: rank-1 Kronecker transport — target-free fidelity failure;
- R250: rank-1 Legendre AP transport — target-free fidelity failure;
- R251: GFNP — no parent measurement in the pinned runtime;
- R252: D21-CWG / CFSP4 — infrastructure-invalid, no scientific measurement;
- R260: BPK2K — valid target-free execution, accuracy gates failed;
- R261: removal of V25's public-fitted online mean-correction rider screened and rejected as speculative without a mechanism signal;
- R265: full-history accuracy-first screen found only one abstractly distinct survivor, randomized multilevel debiasing;
- R269: that survivor was made concrete as a depth-prefix telescope and rejected before execution because it necessarily adds MSE variance, lacks a same-quantity correction-decay rationale, and lacks a committed exact production cost split.

The R273 result is new descriptive evidence, not a new mechanism: V25 error is broad-based. Worst 10% of networks contribute only 12.47% of total adjusted score and the remaining 90% contribute 87.53%. This makes tail special-casing less attractive and raises the bar for a useful candidate: it must move the central bulk under one fixed global configuration.

## Candidate search outcome

No concrete candidate survives the frozen R276 gates.

The remaining obvious moves are not genuinely new:

- globally scaling/removing the existing online correction is a calibration/shrinkage variant and directly overlaps the R261 screen plus earlier calibration families;
- adding another K3/K4 correction or regeneration channel is a cumulant/transport descendant already covered by V25 history, SRM2 and multiple K3/K4 lanes;
- another low-rank/basis/tensor compression is inside the extensively tested low-rank family and the recent MP-R16/D21/Kronecker/Legendre lanes;
- rank/source-age/sample-count hierarchies merely instantiate axes already covered and were explicitly rejected as non-distinct in R265;
- randomized multilevel/depth-prefix is specifically closed by R269;
- per-network or tail-conditioned selection is disallowed here and is also unsupported by R273's broad error concentration.

Launching one of these on mini:all-100 merely to see whether it works would be method fishing and would violate the requested deduplication requirement.

## Decision

**NO-GO before implementation and before mini-100 execution.**

No genuinely distinct, concrete, globally applicable accuracy-improvement hypothesis was found after the current full-history dedupe. Therefore R276 does not invent a new label, does not run an estimator, and does not publish a normalized candidate result.

This NO-GO is scientific/novelty based, not caused by the absence of a local checkout or by compute availability.

## Next distinguishable evidence

The next useful step is not another estimator family rename. A future task should first obtain a new mechanism-level signal that is absent from current evidence — for example, a preregistered **global residual-structure diagnostic** that retains V25 prediction/target residual vectors and tests whether one fixed, network-agnostic output-space correction direction explains a material fraction of error across the central bulk. That diagnostic must be deduplicated against the earlier response-aligned/output-subspace work before any estimator is proposed. If it shows no common global mode, the calibration/output-correction family should remain closed; if it exposes a genuinely new invariant not represented in history, that invariant can define a separately versioned candidate.

R209's archive explicitly lacks raw prediction tensors, so this signal cannot be reconstructed from the current immutable normalized rows alone.

## Accounting

- estimator implementations created: 0
- estimator executions: 0
- mini:all-100 candidate evaluations: 0
- normalized candidate result: not created
- Actions/cloud runs: 0
- new competition data access: 0
- paid compute: 0
- private/holdout/full access: 0
- per-network selection/tuning: 0
- submissions: 0
- leaderboard/canonical edits: 0
