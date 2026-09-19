# E109 — spherical-Stein Jacobian control variate

Idempotency key: `ARC-E109-SPHERICAL-STEIN-JACOBIAN-CV-20260919`

Status: **PREREGISTERED / ONE TARGET-FREE PRODUCTION FALSIFIER ONLY**.

## Provenance and closed lanes

- Direct canonical parent: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- E105 measured the frozen two-Haar E104 production stochastic risk at
  `8.604586912926751e-06`, about 455x the raw target.
- E106 quartic angular controls increased risk by 16.85%; that feature class is closed.
- E108 exact first-layer-mean transport reduced risk by only 0.275%; fixed linear
  first-layer transport is closed.
- E109 therefore tests a genuinely later/deeper nonlinear quantity: the actual
  samplewise network Jacobian through the realized activation region.

No public/public-mini/scorer/holdout/full/benchmark target is used.

## Exact zero-mean identity

Let `q` be uniform on the unit sphere `S^(n-1)` and let `g_j(q)` be the
E104 antithetic analytic-radius response of final output coordinate `j`:

`g_j(q) = (F_j(mu_R q) + F_j(-mu_R q))/2`.

For any fixed unit vector `u`, spherical integration by parts gives

`E[ u^T grad_S g_j(q) - (n-1)(u^T q) g_j(q) ] = 0`.

Define the exact-zero-mean control

`c_j(q) = u^T grad_S g_j(q) - (n-1)(u^T q) g_j(q)`.

The tangential derivative is evaluated exactly almost everywhere by a forward
Jacobian-vector product through the *actual ReLU masks* of each sample. ReLU
region boundaries have spherical measure zero.

This is target-free and uses no Gaussian-closure approximation.

## Frozen activation-region direction

A single common direction is used; no K/rank sweep.

- anchor `q0 = ones(n)/sqrt(n)`;
- compute the gradient of the sum of final outputs of the antithetic response
  at `q0` through the exact realized ReLU masks;
- normalize that gradient to unit length and freeze it as `u`;
- `u` depends only on the synthetic network weights and the fixed anchor,
  never on Haar samples or targets.

This anchor makes the one-direction falsifier sensitive to a real deep
activation region rather than reusing the E108 mean-field transport.

## Cross-fit rule

Each E104 estimator contains two independent Haar bases. For each output
coordinate, fit one scalar coefficient on block 1,

`beta1_j = cov(c1_j,g1_j)/var(c1_j)`,

and apply it only to block 2. Symmetrically fit on block 2 and apply only to
block 1. Average the two corrected block means.

No ridge, clipping, fallback, coefficient sharing, seed/sample sweep, alternate
anchor, alternate direction, or tuning.

Because the coefficient applied to a block is measurable only with respect to
the other independent Haar block and `E[c_j(q)]=0`, the symmetric cross-fit
estimator remains unbiased.

## Frozen production falsifier

- width/depth: `1024/16`;
- 4096 trajectories per estimator = two Haar bases plus antipodes;
- analytic `E[chi_1024]` radius;
- synthetic zero-bias He-Gaussian network;
- weight seed: `109104`;
- estimator direction seeds: `109105`, `109106`;
- budget per estimator: `2^41`;
- float32 propagation, float64 means/risk;
- complete flopscope billing including Haar construction, anchor direction,
  base propagation, JVP propagation, control algebra, cross-fit, finalization.

Two independent estimators A/B measure target-free final-layer stochastic risk:

`Rhat = mean((M_A - M_B)^2)/2`.

The same A/B Haar draws also produce the uncorrected E104 baseline risk.
The entire A/B diagnostic is repeated once with identical seeds only for exact
deterministic replay, inside the same workflow run.

## Pre-code cost admission

E105 complete E104 billing was `149,114,550,960` FLOPs, util
`0.0678094470`. One JVP adds one dense `4096x1024 @ 1024x1024` product plus
one mask application per layer. A conservative pre-code estimate is below
`0.131 B`; the hard project gate is measured utilization `<=0.135`.

If measured utilization exceeds `0.135`, E109 is terminal NO-GO regardless
of risk.

## Frozen gates

All are required for GO:

1. candidate target-free final-layer risk `<=1.89e-8`;
2. candidate risk < uncorrected E104 baseline risk on the same four Haar bases;
3. measured per-estimator utilization `<=0.135`;
4. exact FLOP reconciliation;
5. finite predictions, controls and coefficients;
6. exact antithetic pairing;
7. anchor direction finite and unit norm within `2e-6`;
8. candidate/baseline predictions and risks deterministic exactly on replay;
9. no target/public/scorer/holdout/full access.

Any failed or unevaluable gate => **TERMINAL NO-GO / DROP E109**. No rescue,
rerun, anchor change, coefficient change, sample change, or successor under
this ID.
