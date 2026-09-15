# E019 — exact dead-feedback-lane transport elision

Status: preregistered local diagnostic only.

Idempotency key: `ARC-E019-DEAD-FEEDBACK-LANE-20260915`.

Base: canonical `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

Frozen upstream comparator: `504aldo/whest-p2-cumulant-k3` commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, V25 estimator blob `195373a110215256b759d7c172ba8c923c62e5cc`.

Canonical E007 comparator: raw final-layer MSE `2.23e-08`, adjusted final-layer score `8.17e-09`, all-layers MSE `8.86e-09`, mean compute utilization `0.36666448`, failures `0/100`.

## Motivation after E017/E018

E017 shared-quadratic-basis preflight has no viable cost/fidelity path and is NO-GO. E018 unbiased importance sampling ran its frozen diagnostic and failed fidelity by orders of magnitude. E019 therefore does not introduce another approximation. It targets arithmetic that is provably applied to an identically-zero state in exact V25.

## Structural invariant

In V25, the first source is born while `mode == 0`. In that branch, the V18 D21-feedback factors are explicitly set to zero:

- `F1_b = zeros((n, rfb))`
- `F2_b = F1_b`
- `R1T_b = F1_b`
- `R2T_b = F1_b`

with `rfb = 16` in the frozen V25 configuration. The stored feedback transport is `Ff_b = [F1_b | F2_b]`, hence the first source owns an exact `n x 32` zero feedback lane.

Subsequent V25 code nevertheless applies the same dense transport to that lane as to active feedback lanes: the first propagation performs `W @ Ff`, and later layers transport the stack through `WDb @ Zf_st`. A linear map of an exact zero matrix is exactly zero, so these dense products cannot affect estimator values.

E019 changes **only this transport**:

1. keep source slot 0 and its downstream feedback lane represented as exact zeros;
2. at its first propagation, materialize the zero `n x 32` lane without a dense matmul;
3. on later layers, apply the existing feedback transport only to `Zf_st[1:]`, while keeping slot 0 zero;
4. do not change `_dslices`, reduction shapes, source ordering, D21/K4 formulas, old-tier ranks, lambda, QPASS, R_RES, R_FB, seeds, or any other estimator arithmetic.

The first E019 diagnostic is deliberately limited to this one dead lane. It must not additionally prune zero Rres/K4-feed columns, thin contractions, or any other candidate dead work.

## Frozen cost calculation

Official Phase-2 shape is width `n=1024`, depth `16`, per-MLP budget `B=2**41` FLOPs.

FLOPScope bills a float32 matrix multiply `(m,k) @ (k,n)` as `(2k-1)mn` FLOPs. One `1024 x 1024` by `1024 x 32` dead-lane transport therefore costs

`(2*1024 - 1) * 1024 * 32 = 67,076,096` FLOPs.

The first source is propagated through this zero feedback lane 15 times over a depth-16 network: once when the first newborn feedback lane is propagated at layer 1, then once on each remaining layer 2..15.

Frozen gross removable cost:

`15 * 67,076,096 = 1,006,141,440` FLOPs per MLP.

This corresponds to utilization

`1,006,141,440 / 2**41 = 0.0004575401544570923`.

Subtracting only this gross dead arithmetic from E007 gives a mean-utilization projection of approximately

`0.36666448 - 0.0004575401544570923 = 0.3662069398455429`.

For reference, using the public score gate `8.17e-09 / 2.23e-08`, unchanged raw error requires utilization below approximately `0.3663677130`. Thus the dead-lane saving has about `3.54e8` FLOPs of gross margin above the approximately `6.53e8` FLOPs needed to cross the displayed E007 score at unchanged raw MSE.

Because Phase 2 scores the per-MLP product of MSE and compute multiplier rather than the product of suite means, the above score projection is only a cost-path diagnostic. Official promotion remains based on the actual scorer metric.

## Local diagnostic

No official scorer and no holdout are permitted in E019 local work.

Use exactly one public Phase-2 mini MLP, index `0`, with the pinned V25 source above. Run baseline V25 and E019 under identical Python/NumPy/whestbench/flopscope versions and the same `2**41` FLOP budget. The diagnostic may invoke the estimator directly; it must not call `whest run`.

Record:

- output finite/shape validity;
- maximum absolute and relative output difference against exact V25;
- total estimator FLOPs for baseline and E019;
- FLOP saving and projected utilization from E007;
- residual wall time for the paired calls;
- peak/persistent candidate state attributable to E019;
- confirmation that source-0 `F1/F2/R1T/R2T` and the carried source-0 `Zf` lane are exactly zero at every observed layer.

No seed, MLP index, rank, lane count, source index, or implementation variant sweep is allowed.

## Local GO gates

All must pass:

1. Source-0 feedback invariant is exact: all recorded source-0 feedback factors/transport values are zero at every observed layer.
2. Candidate output is finite, same shape, and numerically identical to baseline within `max_abs <= 1e-7` and relative Frobenius error `<= 1e-7`.
3. Measured billed-FLOP saving is at least `8.0e8` FLOPs on the frozen MLP-equivalent path. This leaves margin for any billed zero-fill/data-movement overhead while still exceeding the approximately `6.53e8` FLOPs needed by the displayed E007 comparator.
4. Projected utilization from E007 is `<= 0.36630`.
5. No residual-wall-time regression: paired candidate residual wall time must be `<=` paired baseline residual wall time.
6. No persistent memory/resource regression beyond the already-existing `Zf` representation; E019 may reuse/preallocate buffers but may not add another persistent `n x n` state.
7. No changes to any estimator math outside source-0 V18 feedback-lane transport.

Any failure is `NO-GO / DROP E019`. No retry with another source index, extra lane pruning, alternative slicing scheme, rank change, parameter change, MLP subset, or scorer run is permitted under E019.

## Conditional official promotion gate

Only after the frozen local diagnostic passes and the exact implementation/provenance is frozen may a separate authorization run exactly one official Phase-2 mini scorer.

Official PASS requires all:

- `adjusted_final_layer_score < 8.17e-09` strictly;
- raw `final_layer_mse <= 2.23e-08`;
- failures `0/100`;
- mean compute utilization `< 0.3663677130` and preferably `<= 0.36630`;
- no residual-wall-time/resource regression or exhaustion;
- provenance remains the exact pinned V25 ancestor plus only the E019 dead-lane transport elision;
- no rerun, tuning, sweep, holdout, alternate dead-source selection, or post-result parameter change.

If local GO is obtained but the official score does not beat E007, E019 is DROP without rescue tuning.
