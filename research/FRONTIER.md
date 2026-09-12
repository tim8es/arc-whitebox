# Public research frontier — 2026-09-09

This document is a working map of **publicly disclosed** methods only. Hidden leaderboard methods may be stronger.

## Official Phase 2 setting

- Random ReLU MLPs
- Width 1024, depth 16
- Standard-normal input
- Predict expected post-ReLU activation of every hidden neuron
- Primary score focuses on final-layer MSE
- Per-MLP compute budget: `2**41` FLOPs
- Score multiplier bottoms out at 10% budget utilization
- CPU-only evaluation; submissions run without network access
- Phase 2 close: 2026-10-17 23:59 UTC

## Reproducible public reference points

### Bundled covariance propagation

Publicly reported control score: approximately `3.93e-7` adjusted on Phase 2.

Use: baseline sanity check and cheap analytic branch.

### Exact bivariate ReLU covariance + per-layer calibration

Public submission #329951 reports `1.32e-7` adjusted, about 3x better than the bundled covariance baseline. Exact pairwise covariance alone helped only modestly; calibration carried much of the improvement.

Implication: fixing a local moment formula does not remove the dominant Gaussian-closure error.

### Third-cumulant propagation

Public submission #330001 reports `1.066e-7` adjusted with zero sampling and zero fitted constants, using a rank-4608 channel that propagates inherited third cumulants.

Implication: skew-aware deterministic propagation is materially better than the simple covariance closure, but the author also reports an apparent closure-family floor above the strongest unknown leaders.

### Whitened antithetic sampling

Phase 1 work reports large gains over naive analytic closure from antithetic sampling plus exact empirical covariance matching. This established variance-per-FLOP as a strong axis.

### Analytic + sampling blend

Phase 2 submission #328274 reports a fixed 0.75/0.25 covariance + whitened-antithetic blend reducing adjusted final-layer MSE from about `4.05e-7` to `3.04e-7`, with measured residual correlation near zero between branches.

Implication: complementary error fields are real; hybrid methods deserve priority.

## Saturated or weak directions

- Static high-dimensional Kerdock/MUB-style cubature has strong public results but published theory/experiments suggest that simple node movement/reweighting in that static class is close to exhausted.
- Naive exactification of individual bivariate moments can fail because different approximation errors partially cancel.
- Blindly increasing Monte Carlo samples past the scoring-rule corner is inefficient; variance per FLOP matters more than sample count.
- High-order moment propagation without measuring the projection/closure error risks spending FLOPs on the wrong bottleneck.

## Current research thesis

The highest-value unexplored territory for this project is **network-dependent hybrid estimation**:

1. build the strongest cheap deterministic predictor we can reproduce;
2. measure its per-network residual structure;
3. spend sampling FLOPs specifically where that predictor is weak;
4. use control variates / adaptive blending rather than independent full estimators;
5. keep utilization near the score-optimal region and measure every change with the official harness.
