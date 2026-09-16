# E053 Protocol — earlier-but-wider nested old tier

## Provenance

- canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- verified E051 baseline: exact upstream V29 f32 blob `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`, Phase-2 width=1024 depth=16, mini[0] raw `2.29004485946887e-08`, utilization `0.2670561845802695`, failures=0, finite/deterministic.
- E049-E052 are immutable and are not rerun, rescued, or modified.

## Single hypothesis

V29's nested old-source tier can trade less tier-1 work for at least preserved cumulant fidelity by moving sources into the nested tier one transport earlier while widening that nested subspace: freeze `AGE_OLD2=6` and `R_OLD2=256` instead of V29's `AGE_OLD2=7`, `R_OLD2=224`.

Mechanism: old sources are represented as `A_s = Qc U FA2_s`, `P_s = Qc U FP2_s`. Earlier nesting removes one layer of the more expensive tier-1 factor path for eligible sources; rank 256 compensates by preserving more of the old-source cumulant subspace. All other V29 arithmetic, source order, dtype, ranks, age gates, lambda logic, K3/K4/D21 terms, Strassen settings, fitted tables, and constants remain byte-for-byte/semantically identical.

Upstream evidence motivating the frozen choice: F73 reports 6:256 ahead of 7:224 on its frozen dump metric while the 192-256 nested-rank frontier is relatively flat. This evidence is motivation only, not E053 evaluation data.

## Frozen implementation

- upstream source commit: `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- upstream estimator Git blob: `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`
- dtype: exact upstream float32 behavior; no float64 port.
- adapter changes exactly two class attributes after exact source verification/load: `AGE_OLD2=6`, `R_OLD2=256`.
- forbidden: clipping, jitter, PSD repair, damping, rescue/fallback, parameter fitting, changes to any other constant/rank/age/lambda/term/order/dtype, public-derived adaptation.

## Gate 0 — package/import preflight

This is a separate gate before any Stage-A computation.

Required GREEN conditions:
1. adapter lives in an installed package-safe module under `methods/` and imports from repository/workflow root after `pip install -e .` with no `sys.path` injection.
2. exact upstream source fetch/load reports Git blob `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`.
3. baseline class has frozen V29 defaults `AGE_OLD=4`, `R_OLD=384`, `AGE_OLD2=7`, `R_OLD2=224`, `QPASS2=2`, `R_FB=16`, `R_RES=16`.
4. E053 class differs only in `AGE_OLD2=6`, `R_OLD2=256`.
5. package-safe import is exercised from workflow root.
6. official-shape synthetic smoke object construction succeeds for width=1024, depth=16 without accessing any benchmark/public split.

Any Gate-0 failure => terminal NO-GO/DROP; no repair/rerun/rescue.

## Stage-A — synthetic official-shape replay

Only after Gate 0 GREEN, run exactly one bounded Stage-A workflow/job.

Frozen input:
- width = 1024
- depth = 16
- NumPy `PCG64`
- seed = `53053`
- no biases
- weights sampled deterministically as float32 `N(0, 2/1024)` and shared identically by baseline and candidate
- budget = `2**41`
- no dataset/public/holdout/full/scorer access.

Execution in the single job:
1. exact V29 baseline once.
2. E053 candidate once.
3. E053 candidate deterministic repeat once inside the same job.
4. record finiteness, max absolute repeat difference, prediction FLOPs, all-in comparison/instrumentation FLOPs, utilization, wall/residual time, and baseline-vs-candidate all-layer/final output deltas.

All arithmetic/instrumentation that goes through flopscope is included in all-in FLOPs. No reference output is fed into either estimator.

## Stage-A gates

E053 Stage-A is GO only if all hold:

1. baseline and candidate outputs are finite.
2. candidate deterministic repeat max absolute difference = 0 (or <= `1e-12` only if a library operation is not bitwise deterministic).
3. candidate all-in utilization <= `0.2670561845802695` (verified E051 mini[0] utilization ceiling).
4. candidate prediction FLOPs are strictly lower than exact V29 baseline prediction FLOPs on the same synthetic MLP.
5. candidate output is non-identical to baseline (`max_abs_delta > 0`) proving the hypothesis path is active.
6. candidate remains a bounded perturbation: final-layer relative RMS delta vs baseline <= `0.02` and all-layer relative RMS delta <= `0.02`.
7. exact-source hash and frozen two-constant delta checks remain true at runtime.

Failure of any Stage-A gate => terminal NO-GO/DROP. No rerun, rescue, seed/tolerance/constant changes, tuning, sweep, public, holdout, full, or scorer.

If all Stage-A gates pass, stop for protocol/control review. Public remains forbidden in E053 at this stage.

## Repository discipline

- branch: `research/e053-oldtier-age6-r256-20260916`
- first E053 commit contains only this protocol.
- canonical and ledger are not modified.
