# E026 — final-layer K4 use damping

Idempotency key: `ARC-RESEARCH-CONTINUE-NEXT-20250915`

Status: preregistered bounded local diagnostic.

## Provenance

- Branch: `research/e026-final-k4-damp-20250915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Pinned upstream V25: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- Exact `estimator_v25.py` blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- E007 anchor: raw `2.23e-08`, utilization `0.36666448`, reported adjusted `8.17e-09`.

E023 is closed and must not be changed or reused. E024 is closed. E025 is occupied by another session and is not touched.

## Mechanism

V25's final layer is already mean-only. Its `(1,)` Wick program consumes the already-computed K4 diagonal-use vector `g4row = dG * METRIC_C`. E026 makes exactly one intentional approximation:

- layers 0..14: unchanged V25;
- layer 15 only (`last == True`): replace `g4row` by `0.95 * g4row` before the mean-only Wick program;
- `D3`, covariance state, lambda adaptation, shared bases, feedback ranks, source machinery, and all earlier-layer state remain unchanged.

Frozen damping factor: **0.95**. It is not tuned in E026. The value is transferred from V25/F75's independently selected global K4-lambda shrink factor; no alternate 0.9/0.92/0.97/1.0 diagnostic is allowed.

This is not an E019 saddlepoint mechanism, E020 Hermite residual rider, E021 zero-lane elision, E022 basis rebuild, E023 F68 zero-elision, or E024/E025 feedback-rank mechanism.

## Quantitative path

At unchanged billed utilization, strict adjusted `< 8.17e-09` from the E007 rounded raw/util anchor requires

`mse_ratio < 8.17e-09 / (2.23e-08 * 0.36666448) = 0.99919038...`

so the candidate needs only about **0.081%** raw-MSE improvement. The added work is one length-1024 scalar-vector multiply on the final layer, negligible relative to the `2**41` budget; nevertheless measured billed FLOPs are recorded and used in the projected score.

## Frozen diagnostic

Public Phase-2 mini **index 0 only**, exactly once.

Run the pinned V25 baseline and E026 candidate under the same flopscope budget. Run the candidate a second time only as a deterministic-repeat check (unmetered). Record:

- baseline and candidate final-layer MSE;
- MSE ratio;
- baseline and candidate billed FLOPs;
- residual time and delta;
- max absolute output difference;
- deterministic repeat max difference;
- projected utilization `E007_UTIL + (candidate_flops - baseline_flops) / 2**41`;
- projected adjusted `E007_RAW * mse_ratio * projected_utilization`.

No scorer, holdout, second mini index, teacher forcing, parameter sweep, alternate damping factor, or post-result patch/rerun.

## Frozen gates

All must pass:

1. final-layer MSE ratio `candidate / V25 <= 0.99919`;
2. projected adjusted `< 8.17e-09`;
3. projected utilization `<= 0.3666655`;
4. candidate billed FLOPs increase `<= 1.0e7`;
5. residual delta `<= 0.005 s` and candidate residual `< 0.400 s`;
6. finite baseline/candidate outputs;
7. deterministic repeat max absolute difference `== 0`;
8. patch scope proves only final-layer `g4row` damping and no other V25 equation/state change.

Any failed or unevaluable gate => **NO-GO / DROP E026**. No rescue under E026.

## Execution budget

Protocol-only first commit, focused tests, then at most one frozen local diagnostic. No official scorer, hidden/full holdout, tuning, sweep, canonical mutation, or changes to E023/E024/E025.
