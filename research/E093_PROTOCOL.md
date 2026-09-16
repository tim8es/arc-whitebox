# E093 — memory-bounded deep-Strassen leaf feasibility

Idempotency key: `ARC-E093-DEEP-STRASSEN-LEAF-20260917`

Status: **PROTOCOL / PRE-PUBLIC ONLY**.

## Objective

Determine whether the dense leaf GEMMs left by V29's pooled Strassen implementation contain enough billed FLOPs to make the E051 frontier computationally capable of reaching the portfolio target without changing the estimator's statistical model.

Reference evidence (already frozen elsewhere): E051 exact V29 Phase-2 shape reproduction observed `predict_flops=587262754287`, `raw_final_mse=2.29004485946887e-08`, `utilization=0.2670561845802695`, finite and deterministic. Portfolio target is `raw <= 1.89e-08` and `utilization <= 0.135` under `B=2^41`.

E093 addresses **compute only**. It does not claim an accuracy improvement. If viable, a later independently gated accuracy mechanism must provide the raw-MSE improvement.

## Provenance / non-duplication

- Branch: `research/e093-deep-strassen-leaf-feasibility-20260917`.
- Direct base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Upstream V29 source must be pinned to commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, blob `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`.
- E048 is terminal NO-GO/DROP and must not be rescued or reused.
- E052/E053 alter old-tier approximation ranks/ages; E093 does not.
- E062 uses structure-aware chassis/FWHT approximation; E093 does not.
- E091/E092 are residual-calibration lanes; E093 does not fit targets or alter predictions in its attribution stage.

## Frozen mechanism class

V29 currently stops recursive pooled Strassen at `STRASSEN_MIN=32`; its fused leaf then executes seven dense matrix multiplications on the 32x32 quadrants. E093 asks whether replacing those **dense leaf products only** with an exact algebraic, memory-bounded deeper Strassen schedule could remove enough scalar multiply/add work to make `util <= 0.135` feasible.

No low-rank approximation, sparsification, target-conditioned choice, learned routing, precision reduction, or data-dependent branch is permitted under E093.

## Stage A — attribution / feasibility falsifier

Run exact unmodified V29 on exactly one deterministic synthetic Phase-2-shape MLP:

- width = 1024
- depth = 16
- PCG64 seed = 93093
- weights iid Normal(0, sqrt(2/1024)), cast float32
- budget = `2^41`

Instrument `flopscope.numpy.matmul` transparently: call the original operation unchanged and record operand shapes plus a deterministic arithmetic estimate. The wrapper must not alter operands, outputs, V29 environment constants, or evaluation logic.

Record at minimum:

1. BudgetContext `predict_flops` and utilization.
2. Total estimated scalar FLOPs in intercepted matmul calls.
3. Estimated scalar FLOPs for dense products whose matrix core has all dimensions `<=32` (`leaf32_flops`).
4. The fraction `leaf32_flops / predict_flops`.
5. An optimistic lower-bound candidate FLOP estimate assuming every identified 32x32 dense leaf product can be recursively replaced down to 1x1 using pure Strassen arithmetic. For the multiplication term use factor `(7/8)^5` relative to conventional 32x32 cubic multiplication; explicitly include a conservative bound for the additional Strassen additions rather than pretending they are free.
6. `optimistic_utilization_lower_bound` under the same `2^41` budget.
7. finite output and deterministic replay equality.

The profiler may classify calls but may not skip, replace, fuse, reorder, or approximate any V29 operation in Stage A.

## Frozen decision gate

**GO to implementation** only if all hold:

- exact V29 output is finite;
- replay is bitwise deterministic;
- source hash matches the frozen upstream blob;
- measured `predict_flops` is within 0.5% of the frozen E051 587262754287 reference;
- `leaf32_flops > 0`;
- after counting a conservative recursive-Strassen addition bound, `optimistic_utilization_lower_bound <= 0.135`.

Otherwise E093 is terminal **NO-GO/DROP**. No attempt may widen the mechanism, change matrix classes, introduce approximation, or tune thresholds to rescue the lane.

## Stage B — only if Stage A GO

Implement one fixed memory-bounded recursive leaf kernel with recursion depth exactly 5 below the current 32x32 leaf. It must compute the same matrix product algebraically; no benchmark/public targets are read. Before any benchmark access it must pass deterministic synthetic parity against dense products and a full synthetic Phase-2 V29 comparison.

Frozen numerical gates for Stage B:

- finite baseline/candidate/repeat;
- deterministic candidate replay (`max_abs == 0` if backend execution is deterministic; otherwise the lane terminates rather than loosening the gate);
- final-layer relative RMS delta vs exact V29 `<= 5e-5`;
- all-layer relative RMS delta vs exact V29 `<= 5e-5`;
- measured all-in utilization `<= 0.135`;
- no target/data-dependent choices.

## Prohibited

No public/public-mini dataset, no official scorer, no holdout/full split, no benchmark labels, no target fitting, no sweep, no threshold search, no rerun-as-rescue, no E048 resurrection, no canonical mutation, and no merge are authorized by this protocol.

## Terminal rule

A failed frozen feasibility gate or failed Stage-B numerical/compute gate is terminal for E093. The failure receipt must be committed before any materially different mechanism is attempted under a new experiment ID.
