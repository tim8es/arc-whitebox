# E044 protocol — fixed-checkpoint exact K3 replay

Idempotency key: `ARC-E044-START-20260916`

Status: **PREREGISTERED / NOT YET RUN**

## Provenance and firewall

- Branch: `research/e044-fixed-checkpoint-k3-replay-20260916`.
- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Pinned upstream estimator: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, `estimators/estimator_v25.py`, git blob `195373a110215256b759d7c172ba8c923c62e5cc`.
- E038–E043 are immutable/occupied and are not inherited or reopened.
- Public Phase-2 mini index **0 only**, exactly one frozen scientific diagnostic.
- No holdout/full split, scorer, rerun, tuning, sweep, checkpoint search, checkpoint-count search, coefficient fitting, canonical mutation, or ledger mutation.

## Disjoint hypothesis

Continuous inherited-K3 source transport dominates V25 cost. E044 tests whether inherited K3 feedback needs to be materialized only at three fixed depth checkpoints while the ordinary local Gaussian/Wick/K4/birth operations run at every layer.

This is **not** source subset selection: every K3 birth is retained. It is **not** terminal-only replay: inherited K3 is injected at three depths. It is **not** conditional Gaussian / half-space / angular quadrature. No source is dropped, reweighted or rank-compressed.

Freeze zero-based checkpoint layers exactly as

`CHECKPOINTS = (7, 11, 15)`.

At non-checkpoint layers inherited source feedback is absent (`D3=D21=0` from inherited sources), but the pinned V25 source-free/local computations, regenerated K4 channel, Wick program, covariance/mean update and new-source birth construction remain unchanged. A source born on any layer is retained as a complete pending source record.

At each checkpoint, all inherited K3 source records are reconstructed exactly under the candidate's own intervening local trajectory and injected through the unchanged pinned V25 `_dslices` / Wick machinery.

## Frozen replay transport

For the V25 source transport map, an already-live source leg advances by

`X <- WD_l @ X`, where `WD_l = W_l * w1_{l-1}[None, :]`.

A newborn source first advances through the next linear layer by the raw `W`, exactly as pinned V25, and only subsequent transitions use `WD`.

Between checkpoints E044 stores the exact per-layer `W` / `WD` operators and complete pending birth descriptors. At checkpoint `c` it builds exact dense composed suffix operators by ordinary matrix multiplication:

- inherited checkpoint-state sources use the one segment product `WD_c @ ... @ WD_{s+1}`;
- a birth `b` inside the segment uses `WD_c @ ... @ WD_{b+2} @ W_{b+1}`;
- the same composed left operator is applied to all left-transported pieces of that source record (`A`, `P`, `Z`, `Zf` as applicable); static right factors / scalar metadata are preserved exactly;
- after replay, source stacks must have identical cardinality across `A/P/Z/L`, feedback factors and every scalar/vector metadata list.

No V21/V24 old-source confinement is allowed in E044: freeze `V21_NO_CONFINE=1`. There is no approximation inside a replayed source record; the approximation being tested is **temporal sparsification of inherited feedback only**.

After a checkpoint, the reconstructed full source state is retained as the checkpoint state, while subsequent inherited feedback is again suppressed until the next checkpoint. New births in the following segment accumulate as pending records and are merged exactly at the next checkpoint.

## Cost path

Continuous V25 has 120 source-layer uses over 15 births. At checkpoints `(7,11,15)`, the numbers of live births are `7 + 11 + 15 = 33`, so source contraction/use occurs only 33 times rather than 120.

The exact composed-transfer construction requires at most 12 dense segment/suffix matrix products across the three frozen segments. Counting two dense source-leg transport actions plus two dense source contractions per live source at checkpoints and the transfer-build overhead gives approximately 30% of the continuous dense source core.

Using the established F86 decomposition that about 95% of V25 cost is source machinery, the preregistered first-order utilization path is

`0.36666448 * (0.05 + 0.95 * 0.30) = 0.1228326008`,

leaving about `0.01717` utilization headroom to the hard `0.14` gate for replay bookkeeping/thin legs. This estimate is a hypothesis only; the measured flopscope utilization is authoritative.

At the projected `0.1228326008` utilization, raw MSE `1.89e-08` would give adjusted `2.321536154e-09`, below `2.5e-09`. Thus the lane has a quantitative path to both accuracy and score gates without relying on the `0.1` multiplier floor.

## Mandatory local GO gates

Every gate must pass on the single frozen public-mini index-0 diagnostic:

- raw final-layer MSE `<=1.89e-08`;
- measured utilization `<=0.14`;
- adjusted proxy `raw_mse * max(0.1, utilization) <2.5e-09`;
- failures `==0`;
- residual wall time `<0.400 s`;
- finite outputs/state;
- deterministic repeat max absolute output difference `==0.0`;
- checkpoints exactly `(7,11,15)`;
- every birth `0..14` is present at final checkpoint; no subset/source pruning;
- replayed source-stack cardinalities are equal across all complete record components;
- pinned V25 blob and all textual patch target counts exact;
- `V21_NO_CONFINE=True` and no other V25 numerical environment mutation.

Any failed or unevaluable gate => **NO-GO / DROP E044**.

## Focused tests before public data

Before any public-mini access, tests must establish:

1. pinned commit/path/blob and checkpoint tuple are exact;
2. checkpoint schedule reports live-source counts `(7,11,15)` and total checkpoint source uses `33`;
3. exact composed `WD` segment transport equals explicit layer-by-layer transport on synthetic matrices;
4. exact newborn replay `WD_c ... WD_{b+2} W_{b+1}` equals explicit raw-first / WD-after transport;
5. a synthetic complete source record replay preserves cardinality and applies the identical left operator to every transported component;
6. all 15 births survive to checkpoint 15; no selector/rank/capacity logic exists;
7. pinned V25 patch targets are unique and freeze `V21_NO_CONFINE=True`;
8. replay algebra executes under `flopscope.numpy` without fallback.

RED must be committed before the E044 module exists and must fail only because that module is absent. No public mini data may be accessed during RED/GREEN/preflight.

## Single frozen public diagnostic

After focused GREEN, execute exactly once on public Phase-2 mini index 0. The replay bookkeeping, segment products, source replay and candidate V25 execution must all be inside one `flopscope.BudgetContext` for the measured run. One identical unmetered repeat is permitted solely for deterministic equality and must not alter checkpoints or state rules.

Record raw final MSE, adjusted proxy, total billed FLOPs/utilization, residual and wall time, failures/finite status, deterministic repeat max abs difference, checkpoint source counts, final birth set, replay/cardinality scope checks, pinned blob and patch counts.

## Kill rule

No rescue under E044: no alternate checkpoint tuple/count, no adding/removing checkpoint 15, no source subset, no rank compression, no source reweighting, no gain/damping, no alternate K4/lambda setting, no partial metadata filtering, no rerun/second index, no holdout/scorer, and no tuning/sweep. Any material mutation requires the next free experiment ID directly from canonical.
