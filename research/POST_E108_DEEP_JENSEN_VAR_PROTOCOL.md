# Post-E108 protocol — final-layer Jensen residual variance decomposition

Idempotency key: `ARC-POST-E108-DEEP-JENSEN-VAR-20260919`

Status at freeze: **BUDGET ADMISSION PASS / ONE TARGET-FREE FALSIFIER AUTHORIZED**.

## Provenance and exclusions

- Parent branch: `research/e108-firstlayer-exactmean-transport-cv-20260919`.
- E108 terminal blocker: first-layer exact-mean transported CV reduced final-layer
  target-free risk by only ~0.275%.
- This successor does **not** use E108's first-layer exact mean, transported
  0.5-Jacobian, fitted CV coefficient, Stein/JVP control, target fitting, or
  benchmark labels.
- It keeps the frozen E104/E105 two-Haar analytic-radius sampling law.
- No public/public-mini, scorer, holdout/full, tuning, sweep, rescue,
  canonical mutation, or ledger mutation.

## Mechanism: exact final-layer nonlinear residual

For one independent Haar block b, let (H_b) denote all penultimate-layer
activations for that block's positive directions and exact antipodes, and let
(W_L) be the final-layer weight matrix.

Define the block final mean

[
Y_b = \frac{1}{|H_b|}\sum_{h\in H_b} \operatorname{ReLU}(hW_L^T).
]

Define the mean-state propagated final activation

[
G_b = \operatorname{ReLU}(\bar H_b W_L^T),
\qquad
\bar H_b = \frac{1}{|H_b|}\sum_{h\in H_b}h.
]

The exact final-layer Jensen residual is

[
J_b = Y_b-G_b.
]

This is an identity for every realized block:

[
Y_b = G_b + J_b.
]

No population mean, target, fitted coefficient, or approximation is required.

For the two independent Haar blocks, the standard target-free two-block risk is

[
R_Y = \frac1p\left\|\frac{Y_1-Y_2}{2}\right\|_2^2.
]

The decomposition induced by the exact identity is

[
R_Y = R_G + R_J + C_{GJ},
]

where

[
R_G = \frac{1}{4p}\|G_1-G_2\|_2^2,
\qquad
R_J = \frac{1}{4p}\|J_1-J_2\|_2^2,
]

and

[
C_{GJ}
=
\frac{1}{2p}(G_1-G_2)^T(J_1-J_2).
]

The primary deep-nonlinear statistic is (R_J). It estimates the sampling
variance contribution of the realized final-layer Jensen residual. This is a
deep nonlinear residual/variance diagnostic, not a control variate and not a
competition-target error estimate.

## Budget-first admission

Frozen production constants inherited from E105:

- width n = 1024
- depth L = 16
- trajectories = 4096
- budget B = 2^41
- inherited fully billed E104/E105 base = 149,114,550,960 FLOPs
- inherited base utilization = 0.06780944702768466
- hard cap = 0.13

The overlay reuses already-computed penultimate activations and final weights.
Before code, reserve a deliberately loose 50,000,000 FLOPs for:

1. four 1024-row penultimate reductions;
2. two block-mean combinations;
3. two 1024-vector by 1024x1024 final matrix products;
4. two final ReLUs;
5. final block means, residual vectors, quadratic terms, cross term,
   deterministic hashes and helper reductions.

Frozen upper bound:

[
F_{upper}=149114550960+50000000=149164550960.
]

This is below the hard (0.13\cdot2^{41}) cap by more than 136 billion FLOPs.
Implementation is authorized only under this frozen cost reserve.

## Frozen production-shape falsifier

One synthetic zero-bias He-Gaussian network:

- width/depth: 1024/16
- weight seed: 110104
- E104 two-Haar direction seed: 110105
- analytic E[chi_1024] radius
- 4096 trajectories = two 1024-direction Haar blocks plus antipodes
- float32 propagation, float64 reductions
- no target/reference mean

Run the exact same estimator twice inside the sole workflow only to verify
determinism. This is not a tuning/rerun arm.

## Frozen gates

Integrity/admission, all required:

1. pre-code utilization upper bound <= 0.13;
2. measured complete utilization <= 0.13;
3. measured overlay FLOPs <= 50,000,000;
4. exact FLOP reconciliation;
5. finite all arrays/scalars;
6. exact antithetic input pairing;
7. deterministic point estimate, decomposition and FLOP ledger replay;
8. exact identity max_abs(Y_b-G_b-J_b) <= 1e-12 for both blocks;
9. exact risk decomposition
   |R_Y-(R_G+R_J+C_GJ)| <= 1e-12 * max(1,R_Y);
10. no benchmark/public/scorer/holdout/full target access.

Scientific falsifier gate:

11. material deep nonlinear component:
    (R_J/R_Y >= 0.10).

If gate 11 fails, this lane is **TERMINAL NO-GO** as an estimator of a
material deep nonlinear variance component on the frozen production-shape
probe. No rescue, seed/sample/depth change, alternate nonlinear residual,
coefficient fitting, tuning, rerun, or public diagnostic.

A pass means only **TARGET-FREE DEEP NONLINEAR VARIANCE GO**: the final-layer
Jensen residual is measurable, material, target-free, and cheap enough to
layer on E104. It does not establish competition raw MSE <= 1.89e-8.
