# Research hypotheses

All hypotheses are provisional until reproduced with the official Phase 2 scorer. A candidate is promoted only after a preregistered holdout test.

## H1 — Residual control variate (priority: P0)

Use a deterministic white-box propagator as a control variate and spend sampling FLOPs on estimating only its residual error.

**Why:** public results show analytic closure and sampling have materially different error structures; a fixed blend already improves over either branch. A control-variate formulation should exploit correlation more directly than an output-space blend.

**Falsifier:** residual variance per FLOP is not at least 15% below the strongest reproducible sampling baseline.

## H2 — Network-conditioned blend (P0)

Replace a single global analytic/sampling blend coefficient with a coefficient derived from cheap network statistics: layerwise weight norms, preactivation variance proxies, covariance concentration, and predicted closure risk.

**Why:** fixed 0.75/0.25 blending has a measured benefit, but different randomly initialized networks need not share the same optimal bias/variance tradeoff.

**Falsifier:** <8% median improvement on a preregistered holdout or >10% degradation in the worst decile.

## H3 — Fourth-moment constrained antithetic sampling (P1)

Extend whitening/antithetic moment matching with a cheap radial or kurtosis correction that preserves first/second moments while reducing fourth-moment discrepancy.

**Why:** first/second-moment matching is already validated; the cheapest next question is whether a controlled higher-moment correction lowers deep-layer sampling noise.

**Falsifier:** <10% final-layer MSE improvement at comparable measured FLOPs.

## H4 — Network-dependent low-rank QMC (P1)

Identify a low-dimensional active subspace from the network weights and apply QMC/cubature in that subspace while treating the orthogonal complement analytically or stochastically.

**Why:** static high-dimensional cubature appears close to saturated. Network-dependent dimensionality reduction is a different method class and may make QMC useful again.

**Falsifier:** no >15% gain per FLOP over whitened antithetic sampling on a development subset.

## H5 — Third-cumulant predictor as control variate (P2)

Reproduce or independently implement a skew-aware propagation estimator and test it as a control variate rather than as the final predictor.

**Why:** a public Phase 2 result reports 1.066e-7 adjusted without sampling, indicating significantly better deterministic correlation with truth than the bundled covariance baseline. Even if closure itself has a floor, that predictor may be valuable for residual variance reduction.

**Falsifier:** residual variance is not materially lower than with covariance propagation after accounting for the additional FLOPs.

## Evaluation protocol

1. Develop on an explicitly recorded development subset.
2. Freeze hyperparameters/decision rules before holdout.
3. Run the official scorer on the holdout.
4. Record raw final-layer MSE, adjusted score, FLOP utilization, failures, and wall time.
5. Promote only reproducible gains; record negative results permanently.
