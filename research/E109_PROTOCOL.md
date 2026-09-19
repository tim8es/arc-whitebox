# E109 Protocol — late-prefix gate-pair sign control variate

Idempotency key: `ARC-E109-LATE-GATEPAIR-SIGN-CV-20260919`

Status: **PREREGISTERED / PRODUCTION-SHAPE SYNTHETIC ONLY**.

## Provenance and disjointness

- Branch: `research/e109-late-gatepair-sign-cv-20260919`.
- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- E104/E105 establish that the remaining dominant error of the analytic-radius two-Haar estimator is angular rather than radial, with production-shape stochastic risk orders of magnitude above the competition target.
- E106 is terminal for **first-layer-row quartic polynomial controls**.
- E107 is terminal for **exact global fourth-moment cubature**.
- E108 is terminal for **first-layer exact-mean fluctuations transported by a fixed linear 0.5 Jacobian**.
- E109 does not reopen any of those lanes. It uses a different exact-zero-mean function class: centered **pairwise sign/gate correlations** of deterministic input-space normals derived from a late network prefix.

No public/public-mini, benchmark target, official scorer, holdout/full, fitted benchmark coefficient, tuning, sweep, or rescue is authorized.

## Mechanism

Use the frozen E104 production sampling law:

- width `n=1024`;
- depth `L=16`;
- `4096` trajectories = two complete `1024x1024` Haar blocks, each with antipodes;
- analytic `E[chi_1024]` radius;
- float32 network propagation and float64 reductions.

For a zero-bias fixed network, define the mean-field late-prefix linearization through layer
`ell=12` in column convention

`P_12 = (0.5 W_12)(0.5 W_11)...(0.5 W_2) W_1`.

Take exactly the first `128` rows of `P_12`, normalize them to unit vectors in input space, and pair them in order:
`(u_0,u_1), (u_2,u_3), ..., (u_126,u_127)`.
This gives exactly `K=64` frozen deep gate-pair controls.

For a unit spherical direction `q`, define for pair `k`

`z_k(q) = sign(u_a^T q) sign(u_b^T q) - c_k`

with

`c_k = (2/pi) asin(rho_k)`, `rho_k = u_a^T u_b`.

Because a uniform spherical direction is a normalized isotropic Gaussian and signs are radial-invariant,

`E_q[sign(u^T q) sign(v^T q)] = (2/pi) asin(u^T v)`.

Therefore each `z_k` has **exact zero spherical mean** for the fixed network-derived directions. It is even under `q -> -q`, so it survives antithetic pairing and targets angular gate/co-activation structure rather than radial noise.

## Cross-fit rule

For each complete Haar block separately:

1. compute final-layer antipodal-paired responses `Y_1,Y_2`, each shape `1024 x 1024`;
2. compute sign-pair controls `Z_1,Z_2`, each shape `1024 x 64`;
3. on each block, fit one univariate scalar coefficient per control/output coordinate:
   `beta[k,j] = sum_i (Z_ik-Zbar_k)(Y_ij-Ybar_j) / sum_i (Z_ik-Zbar_k)^2`;
4. apply coefficients learned on block 1 only to block 2 mean controls, and vice versa;
5. average the two corrected block means.

No ridge, clipping, coefficient shrinkage, multivariate solve, fallback, or coefficient reuse across independent estimator realizations.

The baseline is the unchanged E104 two-Haar analytic-radius estimator from the same trajectories.

## Frozen production-shape corpus

- width: `1024`
- depth: `16`
- trajectories per estimator realization: `4096`
- weight seed: `109104`
- independent E109/E104 estimator direction seeds: `109105`, `109106`
- deterministic replay repeats the exact same two seeds
- late-prefix layer: `12`
- late-prefix rows used: `0..127`
- controls: `64`
- budget: `2**41`
- utilization cap: `0.13`
- competition raw target scale: `1.89e-8`

## Pre-code admission

Inherited complete E104/E105 production estimate:
`149,114,550,960` billed FLOPs.

Conservative additional allowance:

- eleven full `1024x1024` float32 prefix matrix products:
  `11 * 2 * 1024^3 = 23,622,320,128`;
- prefix scaling/normalization and 128 deep normals: `<=0.1B`;
- two-block projection to 128 normals, sign-pair formation, and exact means: `<=0.8B`;
- final-layer cross-fit covariance/corrections for 64 controls: `<=0.6B`;
- bookkeeping margin: `<=1.0B`.

Frozen pre-code upper:
`175,236,871,088` FLOPs,
utilization `0.079688` approximately, safely below `0.13`.

Implementation is authorized only because this admission gate passes before code.

## TDD / verifier sequence

1. Protocol commit first.
2. RED tests import absent `methods.e109_late_gatepair_sign_cv`.
3. Focused RED workflow must fail for the expected missing module.
4. Minimal helper implementation only.
5. Focused GREEN must pass before scientific execution.
6. Add one frozen production-shape verifier/driver and one path-isolated workflow.
7. Execute exactly one scientific production-shape synthetic run. No rerun.

Focused tests must cover:

- analytic sign-pair mean for orthogonal, identical, and antipodal normals;
- deep-prefix shape and deterministic row normalization;
- control evenness under `q -> -q`;
- cross-fit identity when controls are zero;
- deterministic E104 input construction.

## Frozen gates

Integrity gates, all required:

1. all predictions, controls, coefficients and ledgers finite;
2. exact antipodal inputs;
3. normalized deep directions max norm error `<=2e-6`;
4. analytic sign-pair means finite and in `[-1,1]`;
5. candidate and baseline predictions bitwise deterministic on replay;
6. candidate and baseline risk replay absolute difference `==0`;
7. exact FLOP reconciliation and deterministic FLOP ledgers;
8. measured utilization `<=0.13`;
9. no targets read.

Scientific later-layer-explanation GO requires:

10. candidate target-free final-layer stochastic risk / baseline E104 risk `<=0.90`;
11. candidate risk is strictly below baseline risk.

Competition GO additionally requires:

12. candidate target-free risk `<=1.89e-8`.

A pass of 10–11 without 12 is **LOCAL MECHANISM GO ONLY / competition_go=false**.
Failure of 10 or 11 is **TERMINAL NO-GO / DROP E109**.

No parameter change, late-layer change, pair change, K change, ridge/clipping, seed/sample change, rescue, tuning, sweep, public diagnostic, scorer, holdout/full, or scientific rerun is allowed after the frozen result.
