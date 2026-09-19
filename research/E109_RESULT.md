# E109 Result — terminal NO-GO / DROP

Idempotency key: `ARC-E109-LATE-GATEPAIR-SIGN-CV-20260919`

Decision: **TERMINAL NO-GO / DROP**

## Frontier rationale

E104/E105 isolate a large production-shape angular stochastic error after exact radial Rao–Blackwellization. E106 closed first-layer quartic angular controls, E107 closed exact fourth-moment cubature by cost, and E108 showed that an exact first-layer mean fluctuation transported through a fixed linear 0.5 Jacobian explains only 0.275% of the final-layer risk.

Before opening E109, the seemingly simpler deep quadratic spherical-control lane was rejected analytically: one complete Haar basis integrates every quadratic form exactly, so the block mean of a centered quadratic control is identically zero and cannot change the two-Haar estimator.

E109 therefore tested a genuinely different even angular object: **centered pairwise sign/gate correlations** of deterministic layer-12 mean-field pullback normals. This targets late/deep gate geometry rather than first-layer moment error.

## Provenance

- Branch: `research/e109-late-gatepair-sign-cv-20260919`
- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-first commit: `2b1533fbba2234d773f8d3d73dcb1c0cbce6506f`
- RED tests commit: `158b3a99057ca55467cd2b83690c001b26c82566`
- RED workflow commit: `d91dbaced692d63eba366740cdbc917fc07b8270`
- Implementation commit: `03b01f12eb4208b52fa4f317a76f87fba184030e`
- Frozen verifier commit: `154c115a859e415fa8ad7c03c8fed2942054d23c`
- Sole scientific arm/workflow commit: `cf6322f4fb4dce677b3d0167d0337b759a5a36e0`

## Exact-zero-mean identity

For deterministic unit normals `u,v` and a uniform spherical direction `q`,

`E[sign(u^T q) sign(v^T q)] = (2/pi) asin(u^T v)`.

Thus

`z(q)=sign(u^T q)sign(v^T q)-(2/pi)asin(u^T v)`

has exact zero spherical mean. It is even under `q -> -q`, so it survives antithetic pairing.

The frozen deep normals came from the layer-12 mean-field prefix

`P_12=(0.5W_12)...(0.5W_2)W_1`.

Exactly the first 128 normalized rows were paired in order into 64 controls. Coefficients were learned independently on the opposite Haar block and cross-applied. No ridge, clipping, pair/K/layer/seed/sample sweep, or target fitting was used.

## TDD

Actual RED:

- run `35453090155`
- job `105923542438`
- conclusion: failure
- expected cause: `ModuleNotFoundError: No module named 'methods.e109_late_gatepair_sign_cv'`

Focused GREEN:

- run `35453170740`
- job `105923754523`
- conclusion: success
- `5 passed in 0.23s`

## Sole frozen production-shape verifier

- run: `35453256948`
- job: `105923980639`
- run attempt: 1
- scientific computation step: success
- terminal workflow conclusion: failure only because frozen scientific exit code was `2`
- no rerun

Artifact:

- name: `e109-late-gatepair-sign-cv`
- ID: `10587218508`
- size: `3581` bytes
- GitHub ZIP SHA256:
  `3b3e88ffe457e084f78d620bb08092ec8479fdd7c2d22d42a5f9f11286a9a328`
- independently downloaded ZIP SHA256: identical
- extracted JSON SHA256:
  `93891361e5ceec1220f0d9c36b1ba65db2381852d85a3db6c7a5f7640144f0b7`
- frozen artifact exit code: `2`

## Frozen instance

- width/depth: `1024 / 16`
- trajectories per estimator: `4096`
- weight seed: `109104`
- independent direction seeds: `109105, 109106`
- late-prefix layer: `12`
- deep direction rows: `128`
- sign-pair controls: `64`
- public/public-mini/scorer/holdout/full targets: none

## Measured target-free risk

Final-layer independent-estimator stochastic risk:

- unchanged E104-style baseline:
  `9.279444815115177e-06`
- E109 candidate:
  `9.508501368316554e-06`
- candidate / baseline:
  `1.0246842949944883`
- relative change:
  **+2.4684294994% risk**
- candidate / competition raw target scale `1.89e-8`:
  `503.09531049293935x`

The controls were active rather than numerically zero:

- max absolute fitted beta, seed A: `0.037384603716228225`
- max absolute fitted beta, seed B: `0.035316795582932034`
- block control-mean RMS values: about `0.0238–0.0254`
- analytic centered-control means ranged from `-0.1897986680` to `0.1410783976`

But cross-fitted correction worsened rather than reduced independent-estimator risk.

## Measured complete compute

Per estimator realization:

- input construction: `11,541,346,992` FLOPs
- frozen late-prefix/control setup: `24,163,124,480` FLOPs
- 16 network layers: `137,573,171,200` FLOPs
- finalization/cross-fit: `552,150,656` FLOPs
- total/reconciled: `173,829,793,328` FLOPs
- utilization: `0.07904863802104956`
- exact accounting reconciliation: true

Pre-code upper:

- `175,236,871,088` FLOPs
- utilization `0.07968850290490082`

The pre-code bound was conservative by `1,407,077,760` FLOPs and the hard `<=0.13` admission gate passes with large headroom.

## Integrity

PASS:

- all arrays/coefficients finite
- exact antithetic inputs
- deep direction max norm error `9.244663878860138e-08 <= 2e-6`
- analytic control means in `[-1,1]`
- candidate predictions bitwise deterministic
- baseline predictions bitwise deterministic
- candidate risk repeat delta `0.0`
- baseline risk repeat delta `0.0`
- deterministic FLOP ledgers
- exact accounting reconciliation
- baseline final re-composition max abs `0.0`
- measured utilization `<=0.13`
- no targets read

FAIL:

- material explanation gate `candidate/baseline <=0.90`: observed `1.0246842949944883`
- candidate risk < baseline: false
- competition-scale risk `<=1.89e-8`: false

## Interpretation

The exact centered sign-pair controls are valid and the late-prefix construction fits comfortably inside the compute cap, but these mean-field layer-12 pairwise gate correlations do **not** explain the dominant E104 angular error. Their fitted signal is nonzero, yet applying it cross-fitted increases final-layer stochastic risk.

This closes the tested family of **pairwise late mean-field gate-sign controls**. It does not reopen E106 quartic controls, E107 cubature, or E108 first-layer transport, and none may be rescued from this result.

The surviving frontier constraint is sharper: a successor must model a deeper nonlinear component that is not captured by first-layer moments, low-order polynomial angular controls, or pairwise gate correlations of a fixed mean-field prefix, while preserving target-free unbiasedness and production utilization `<=0.13`.

No public/public-mini, benchmark target, official scorer, holdout/full, tuning, sweep, rescue, canonical/ledger mutation, merge, or scientific rerun occurred.
