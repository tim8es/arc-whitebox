# E096 — exact V29 matmul callsite attribution

Idempotency key: `ARC-E096-V29-MATMUL-CALLSITE-20260917`

Status: **PRE-PUBLIC DIAGNOSTIC / PROTOCOL-ONLY**.

## Purpose

E051 measures exact upstream V29 at `587262754287` billed predict FLOPs (`util=0.26705618458` under `B=2^41`), while the portfolio target requires `util<=0.135`. E093 proves that blindly deepening Strassen leaves cannot bridge the gap. E094 and E095 are occupied by independent source-axis and sampling lanes.

E096 performs one transparent synthetic official-shape run of unmodified V29 and attributes intercepted `flopscope.numpy.matmul` arithmetic to the **actual upstream source callsite and operand shape**. It changes no prediction and tests no accuracy hypothesis. Its only role is to identify the largest not-yet-attacked compute classes so the next experiment is chosen from measured evidence rather than intuition.

## Provenance

- branch: `research/e096-v29-matmul-callsite-attribution-20260917`
- direct base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- upstream source: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- expected V29 blob: `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`
- E048 terminal NO-GO remains immutable.
- E093 terminal deep-Strassen result is not rescued.

## Frozen Stage A

One deterministic synthetic MLP only:

- width `1024`
- depth `16`
- PCG64 seed `96096`
- weights iid `N(0,sqrt(2/1024))`, float32
- budget `2^41`

Monkey-patch only `flopscope.numpy.matmul` with a transparent wrapper that immediately calls the original operation unchanged. Before the call, record:

- caller function and source line in the pinned V29 module;
- operand shapes;
- independent conventional multiply/add estimate `batch*m*n*(2*k-1)` for matrix core `(m,k)@(k,n)`.

Aggregate by `(caller_function, caller_line, m,k,n,batch)` and report the top 30 groups by estimated arithmetic, plus totals by caller line.

The wrapper may inspect Python frames and operand metadata but may not alter arrays, kwargs, outputs, execution order, environment constants, or V29 source.

## Frozen integrity gates

All must pass:

- upstream blob exact;
- output finite;
- measured `predict_flops` within `0.5%` of frozen E051 `587262754287`;
- at least `80%` of measured `predict_flops` covered by independently estimated intercepted matmul arithmetic (E093 observed ~91%, so a lower gate catches profiler breakage without claiming equal cost models);
- at least one callsite group records nonzero arithmetic;
- all reported arithmetic nonnegative and aggregation totals reconcile exactly.

Failure => terminal diagnostic invalid; no rerun/rescue under E096.

## Required decision output

The receipt must name:

1. the top three callsite groups and their fraction of total predict FLOPs;
2. cumulative top-3 fraction;
3. the minimum fraction of those groups that must be removed/replaced, holding all other FLOPs fixed, to meet `0.135 B`;
4. whether the measured dominant class overlaps E094 source-axis compression, E095 residual sampling, or neither;
5. one materially disjoint next mechanism class justified by the measured callsite/source semantics, or `NO_ADMISSIBLE_NEW_MECHANISM` if none exists.

## Prohibited

No public/public-mini dataset, official scorer, holdout/full split, benchmark labels, target fitting, source pruning, approximation, sweep, tuning, rerun, canonical mutation, ledger mutation, merge, or result-conditioned change inside E096.
