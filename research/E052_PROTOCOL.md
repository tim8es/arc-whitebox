# E052 Protocol — oldest-tier rank 256

## Provenance

- Parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Verified E051 baseline evidence: exact upstream V29 f32 blob `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`, Phase-2 shape width=1024/depth=16, mini[0] raw `2.29004485946887e-08`, utilization `0.2670561845802695`, failures=0, finite=true, deterministic=true.
- E049/E050/E051 are not modified, rerun, rescued, or reused as experiment branches.

## Hypothesis

V29's nested oldest-source tier uses `R_OLD2=224` inside the tier-1 rank-384 basis. Upstream V24 evidence describes the same mechanism at rank 256 as essentially accuracy-neutral relative to the less-compressed path. The working hypothesis is that V29's final 224 truncation discards cumulant signal in late layers; increasing only `R_OLD2` from 224 to 256 should reduce old-tier projection loss while preserving the V29 equations, float32 arithmetic, age gates, lambda rule, source ordering, and all other constants. The expected trade is a small FLOP increase that must remain below the E051 utilization gate.

## Frozen method delta

Starting from the byte-identical upstream V29 source blob above, E052 may make exactly one scientific change:

`Estimator.R_OLD2: 224 -> 256`

Everything else is frozen byte-for-byte/semantically identical: float32 working dtype; `AGE_OLD=4`, `R_OLD=384`, `AGE_OLD2=7`, `QPASS2=2`, `R_FB=16`, `R_RES=16`, `STRASSEN_LEVELS=5`, `STRASSEN_MIN=32`, `BETA=1.0`, lambda tables/rule, term ordering, source birth/order, K3/D21/K4 equations, riders, covariance transport, and final-layer trim. No clipping, jitter, PSD repair, damping, rescue, fallback, refit, tuning, or other parameter change.

## Stage-A only before review

No public, holdout, full, scorer, leaderboard, or canonical/ledger access is allowed in Stage-A.

Stage-A uses one deterministic synthetic MLP with official shape width=1024, depth=16, NumPy PCG64 seed `52052`, zero biases, and weights sampled once from the same standard-normal scaling used by the benchmark domain. The same MLP is fed to exact V29 baseline (`R_OLD2=224`) and E052 (`R_OLD2=256`). Both run with the same `2**41` FLOP budget and float32 estimator arithmetic.

Required observations:

- exact upstream source Git-blob SHA verification before patching;
- static proof that the only scientific source change is the single integer `224 -> 256` at `Estimator.R_OLD2`;
- baseline and E052 finite outputs;
- E052 deterministic replay inside the one Stage-A job;
- baseline and E052 all-in FLOPs/utilization;
- final-layer max-abs and RMS output delta between E052 and baseline;
- per-layer RMS output delta, with late-layer delta reported separately;
- all instrumentation FLOPs billed separately and not counted as estimator utilization.

## Frozen Stage-A gates

Stage-A is GO only if all hold:

1. exact upstream V29 blob is verified and only `R_OLD2=256` differs scientifically;
2. E052 prediction is finite and deterministic (`max_abs_repeat <= 1e-12`);
3. E052 estimator utilization `<= 0.30` of `2**41`;
4. E052 produces a non-zero late-layer effect: final-layer RMS delta versus V29 `>= 1e-8` (otherwise the hypothesis does not materially alter the bottleneck);
5. no forbidden stabilization or secondary parameter change occurs.

Any failure is terminal E052 NO-GO/DROP before public. No rerun, rescue, seed change, rank sweep, tuning, holdout/full/scorer, canonical or ledger mutation.

If Stage-A passes, stop for protocol/control review. Public evaluation is not authorized by this protocol stage.
