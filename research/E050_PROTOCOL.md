# E050 Protocol — stable float64 V29 port

## Provenance

- Canonical parent is exactly `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Upstream estimator is 504aldo V29 from commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.
- Frozen upstream V29 Git blob is exactly `17df1a073a24f96c4705b04bcf61ef60fa06dd0c` (`estimators/estimator_v29.py`).
- E049 is immutable NO-GO/DROP and is not modified or rerun by E050.

## Research question

Does a purely mechanical float64/stable-accumulation port make the frozen V29 estimator finite and deterministic on the fixed Stage-A replay while preserving V29's algorithm and constants?

## Frozen port rules

1. Preserve V29 algorithm, control flow, estimator structure, ranks, age gates, source tiers, K3 factorization, D21 feedback, memoryless K4 regeneration, Strassen/Winograd structure, lambda tables, fitted tables, and all scalar constants exactly.
2. Replace V29 working dtype `float32` with `float64` mechanically. Constants retain the same mathematical values; no coefficient refit or retuning is permitted.
3. Stable accumulation may only change arithmetic evaluation precision/order where required for float64 execution; it may not change the mathematical expression being evaluated.
4. Forbidden: clipping introduced by E050, covariance clipping, PSD repair, diagonal jitter, renormalization, damping, shrinkage, adaptive rescue, fallback estimator, exception-based recovery, constant changes, rank changes, age-gate changes, Strassen-level changes, or any data-dependent tuning.
5. Existing upstream V29 safeguards/constants remain frozen as part of upstream provenance; E050 must not add new safeguards.
6. Every arithmetic operation used by the port and instrumentation is billed in the all-in FLOP count under the same flopscope accounting model.

## Stage-A frozen replay

- Deterministic synthetic MLP: width `32`, depth `8`.
- Generator: NumPy `PCG64`, seed `50050`.
- Weight generation is fixed before execution and is identical for reference/local paths.
- No biases are introduced.
- Reference path: exact frozen upstream V29 logic with its original float32 dtype.
- Local path: mechanical E050 float64/stable-accumulation port only.
- Execute each path once. No rerun, rescue, alternate seed, alternate width/depth, or parameter change is allowed.

## Required deterministic instrumentation

Stage-A must emit, for both reference and local paths where the reference remains evaluable:

- per-layer K3 source-output diagnostics sufficient to compare the transported/source contribution before final nonlinear assembly;
- per-layer `D21` diagnostics;
- per-layer regenerated K4 diagnostics (`dG`/equivalent regenerated K4 state used by V29);
- final prediction tensor;
- finite/non-finite status;
- deterministic replay identity for the local path;
- all-in FLOPs, including factor construction, QR/range-finder work, closures, contractions, Strassen/Winograd additions/products, dtype-conversion work, and instrumentation arithmetic.

Instrumentation must be observational only: it may copy/record already-computed states but may not feed oracle/reference state into runtime or alter estimator evolution.

## Fixed comparison and kill rule

Stage-A is GREEN only if all of the following hold:

1. The local float64 port is finite at every recorded component and at the final output.
2. The local path is deterministic under the fixed replay: repeated local evaluation performed inside the single Stage-A job with identical frozen inputs must agree exactly in shape and bitwise float64 output, or with maximum absolute difference `<= 1e-12` if an upstream library operation is not bitwise reproducible while remaining deterministic to that tolerance.
3. Wherever the float32 upstream reference component remains finite, component deltas between local float64 and reference, after comparison in float64, satisfy both maximum absolute error `<= 1e-10` and maximum relative RMS error `<= 1e-8` for K3 source outputs, `D21`, regenerated K4 diagnostics, and final output. A reference component that becomes non-finite is recorded as such and is not silently omitted.
4. The all-in projected/full replay utilization is `<= 0.30` of budget `2**41` under the same billing convention.
5. No forbidden stabilization or algorithm/constant change is present.

If any condition fails, E050 is terminal `NO-GO/DROP` before any public-mini action. No rescue, rerun, precision ladder, tolerance change, seed change, clipping, tuning, sweep, holdout, full split, or official scorer is permitted.

## Public gate

No public-mini run is allowed until Stage-A is GREEN. If Stage-A is GREEN, exactly one frozen `aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`, index `0` diagnostic may be run. Required public gates are:

- raw final-layer MSE `<= 2.30e-08`;
- adjusted score `< 5.40e-09`;
- utilization `<= 0.30`;
- failures `== 0`;
- finite and deterministic.

Failure of any public gate is terminal `NO-GO/DROP`. No rerun/rescue/tuning/sweep/holdout/full split/official scorer follows.

## Repository discipline

- Branch: `research/e050-stable-float64-v29-20260916`.
- This protocol is the first and only file in the first E050 commit.
- Do not mutate canonical, ledger, E049, or any prior experiment branch.
