# E051 Protocol — exact V29 Phase-2-shape reproduction

## Provenance

- Canonical parent is exactly `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Branch is exactly `research/e051-v29-phase2-shape-reproduction-20260916`.
- Upstream estimator is 504aldo V29 from commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.
- Frozen upstream estimator Git blob is exactly `17df1a073a24f96c4705b04bcf61ef60fa06dd0c` (`estimators/estimator_v29.py`).
- E049 and E050 are immutable terminal NO-GO/DROP and are not modified, rerun, rescued, or reused as experiment state by E051.

## Research question

Does the byte-identical public V29 float32 estimator reproduce as finite, deterministic, and within the preregistered accuracy/cost gates on the official Phase-2 network shape where V29's suite-shape riders are active?

## Frozen estimator rules

1. Use the exact byte-identical upstream V29 source blob `17df1a073a24f96c4705b04bcf61ef60fa06dd0c` with no algorithmic source edits.
2. Preserve float32 working dtype exactly. No float64 conversion or mixed-precision substitution is permitted.
3. Preserve all V29 constants, tables, operation order, ranks, age gates, source tiers, K3 factorization, D21 feedback, memoryless K4 regeneration, adaptive lambda rule, Strassen/Winograd settings, final-layer trim, and control flow exactly.
4. Forbidden: clipping introduced by E051, covariance clipping, jitter, PSD repair, renormalization, damping, shrinkage, fallback estimators, exception-based rescue, parameter changes, rank changes, age changes, lambda changes, term changes, precision changes, optimization, or tuning.
5. Existing upstream safeguards and frozen fitted constants are part of V29 provenance and must remain unchanged.
6. Compatibility code may only instantiate the estimator, load the frozen benchmark item, measure determinism/finiteness/FLOPs, and serialize evidence. It may not alter estimator arithmetic or network inputs.

## Shape and benchmark gate

- Required network shape: width `1024`, depth `16`.
- This is the V29 suite-shape path for which the riders are active, including regenerated K4 and old-source tiers.
- The single bounded reproduction target is `aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`, index `0`.
- No other public example, seed search, holdout, full split, official scorer, or alternate network is permitted.

## Required preflight tests

Before the bounded reproduction, focused tests must verify:

1. the vendored estimator file has Git blob hash exactly `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`;
2. the official Phase-2 item used by the harness has width `1024` and depth `16`;
3. the V29 suite-shape gate is therefore active (`n == 1024` and depth equals the 16-row correction table);
4. frozen constants and switches match upstream defaults, including `AGE_OLD=4`, `R_OLD=384`, `AGE_OLD2=7`, `R_OLD2=224`, `QPASS2=2`, `R_FB=16`, `R_RES=16`, `STRASSEN_LEVELS=5`, `STRASSEN_MIN=32`, `BETA=1.0`, `NO_REGEN=False`, `NO_FB=False`, `NO_CONFINE=False`;
5. the compatibility harness contains no float64 conversion, clipping, jitter, repair, damping, parameter overrides, or estimator mutation;
6. all-in FLOP accounting uses flopscope for estimator execution and includes compatibility/instrumentation arithmetic that is part of the measured reproduction.

## Single bounded reproduction

After protocol/control verification and focused preflight GREEN, execute exactly one bounded mini[0] workflow job. Within that one job, the exact same frozen item may be evaluated twice solely to establish deterministic repeat; this is one Stage-A/public reproduction attempt, not a second experiment run.

Required evidence:

- final-layer raw MSE against the benchmark target;
- finite prediction status;
- benchmark failure count;
- exact-repeat maximum absolute difference;
- estimator FLOPs and all-in billed FLOPs;
- utilization = all-in FLOPs / `2**41`;
- residual wall time if exposed by the accounting context;
- confirmation that width=1024/depth=16 activated the suite-shape riders.

## Frozen GO / kill rule

E051 reproduction is GO only if all conditions hold:

- finite output;
- failures `== 0`;
- raw final-layer MSE `<= 2.30e-08`;
- utilization `<= 0.30` of budget `2**41`;
- deterministic repeat with exact equality or maximum absolute difference `<= 1e-12`.

If any condition fails, E051 is terminal `NO-GO/DROP`. No rerun, rescue, alternate precision, tolerance change, clipping, optimization, tuning, sweep, holdout, full split, official scorer, or second public example is permitted.

## Repository discipline

- This protocol is the first and only file in the first E051 commit.
- After this commit, only exact vendoring, compatibility harness, focused tests, and one bounded reproduction workflow may be added.
- Do not mutate canonical, ledger, E049, E050, or any prior experiment branch.
- Do not merge E051 in this experiment.
