# E024 — terminal result

Idempotency key: `ARC-E024-SEARCH-20250915`

Status: **DONE / NO-GO / DROP**

Branch: `research/e024-final-feedback-r8-20250915`

Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

Protocol-only first commit: `5aebf890c00a562896733c29b6d95cb65185b813`.

Focused implementation commit: `90458c6b146dc0c10fe7eb04210023fcf1a1251c`.

Frozen diagnostic harness commit: `9424c1bb93d87edcea7a95328c9ac402bb1ea153`.

Frozen measurement workflow commit: `5d8d141069380c26056beb6a01f2a0065ad7a1ba`.

Pinned V25 source: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, blob `195373a110215256b759d7c172ba8c923c62e5cc`.

## Mechanism

E024 preregistered one intentional approximation: keep the V18 D21-feedback carrier at rank 16 for layers 0..14, then use only a fixed prefix rank 8 of each F1/F2 feedback half when evaluating the already mean-only final layer. No rank-8 basis recomputation, source removal, earlier-layer rank change, E021 zero-lane elision, or E023 F68-carrier rewrite was allowed.

Primary upstream F69 reports that V18 feedback is very low rank: on the port-faithful lean chain, no feedback is about `2.36e-08`, dense feedback `2.13e-08`, rank 32 `2.14e-08`, rank 16 `2.14e-08`, and rank 8 `2.17e-08`; the real V18 rank ladder on dumps 0/1 gives rank 8 `2.184e-08 @0.5013xB`, rank 16 `2.157e-08 @0.5093xB`, rank 32 `2.119e-08 @0.5473xB`.

## Quantitative preregistered path

For final-layer `k=15`, `n=1024`, `r:16 -> 8`, the frozen static saving estimate was

`8 * k * n^2 * (16-8) = 1,006,632,960 FLOPs/MLP`.

Using the E007 anchor (`raw=2.23e-08`, utilization `0.36666448`):

- projected utilization: `0.366206716328125`;
- projected adjusted at unchanged raw: `8.166409774117188e-09`;
- preregistered measured MSE-ratio gate: `<=1.0004`.

Thus E024 had a numerically explicit but narrow path below `8.17e-09` before measurement.

## TDD evidence

RED:

- run `34980389118`
- job `104418867253`
- expected failure: `ModuleNotFoundError: No module named 'methods.e024_final_feedback_r8'`
- no dataset/scientific diagnostic was executed.

GREEN:

- run `34980490214`
- job `104419210580`
- `3 passed in 0.12s`.

Frozen measurement run repeated the focused tests successfully (`3 passed in 0.18s`) before entering the scientific step.

## Single frozen local diagnostic

Frozen run: `34980699929`

Job: `104419941871`

Public Phase-2 mini index 0 only. No official scorer, holdout, tuning, sweep, alternate rank, or second mini index.

The exact V25 baseline execution completed. The E024 candidate then failed before producing `E024_SUMMARY`, candidate output, candidate MSE, or candidate FLOP total. The failure was:

`ValueError: all the input array dimensions except for the concatenation axis must match exactly, but along dimension 2, the array at index 0 has size 16 and the array at index 1 has size 32`

at the frozen candidate's final-feedback `fnp.concatenate` operation.

Therefore the measured scientific metrics that require a complete candidate run are **unavailable**:

- candidate final-layer MSE: not produced;
- measured MSE ratio: not produced;
- candidate billed FLOPs: not produced;
- measured FLOP saving: not produced;
- projected adjusted from measured MSE/saving: not produced;
- candidate residual time: not produced;
- candidate determinism/output-difference metrics: not produced.

The only numerical E024 performance quantities available are the preregistered static projections above; they are not substituted for measured metrics.

## Gate evaluation

PASS before scientific execution:

- exact canonical ancestry and pinned V25 provenance;
- protocol-only first commit;
- observed TDD RED then GREEN;
- one fixed mechanism/rank/index with no sweep.

FAIL / unevaluable because the frozen candidate did not complete:

- candidate finite/deterministic gate;
- measured MSE ratio `<=1.0004`;
- measured saving `>=9.0e8 FLOPs/MLP`;
- projected utilization `<=0.3662552` from measured saving;
- projected adjusted `<8.17e-09` from measured MSE ratio and saving;
- candidate residual-time gates;
- exact scope/runtime validation of the intended final-only rank change.

Under the frozen rule, any failed or unevaluable required gate after the single authorized diagnostic is terminal.

## Decision

**NO-GO / DROP E024.**

The candidate crash is an implementation-shape failure, not evidence that the underlying rank-8 scientific hypothesis is false. However, the protocol explicitly permits at most one frozen local diagnostic and forbids a second diagnostic/rescue. Fixing the slicing layout and rerunning would therefore be a new experiment ID, not E024.

No E024 rescue, second diagnostic, official scorer, holdout, tuning, sweep, canonical mutation, E023 modification, or branch rename was performed.
