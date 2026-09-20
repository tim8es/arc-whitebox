# E028 — final-layer D3² Wick-term prune

Idempotency key: `ARC-RESEARCH-CONTINUE-NEXT-20250915`

Status: preregistered bounded local diagnostic.

## Provenance

- Branch: `research/e028-final-d3sq-prune-20250915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Pinned upstream V25: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- Exact `estimator_v25.py` blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- E007 anchor: raw `2.23e-08`, utilization `0.36666448`, reported adjusted `8.17e-09`.

E023/E024/E026/E027 are closed and immutable. E025 is occupied by another session and is not touched.

## Primary-source motivation

The companion-paper audit recorded in upstream F48 explicitly permits score-driven diagram-term selection. V25's `(1,)` mean Wick program includes the self-interaction term

`('d3', 'd3', wick_index=18, coefficient=1/72)`.

`D3` is an approximate K3 diagonal-slice channel. Since V19/V25 final layer is already mean-only, pruning its quadratic self-interaction changes no propagated estimator state. E027 separately tested the mixed `D3×G4` term and is closed; E028 tests the mechanistically distinct hypothesis that squaring the approximate K3 slice over-corrects the final mean.

## Frozen mechanism

Layers 0..14 are unchanged V25. On layer 15 only, after ordinary V25 `PK1` evaluation, subtract exactly the `(d3,d3)` contribution:

`delta_d3sq = (D3 * D3) * (WT[18] / 72)`

`pk1v_candidate = pk1v_v25 - delta_d3sq`.

No other Wick term, rank, lambda, source, basis, covariance, D3, G4, feedback, or propagation equation changes. No coefficient damping or alternate term diagnostic is permitted.

The bounded diagnostic implements the structural prune as an O(n) final subtraction. Measured diagnostic FLOPs, including this subtraction, are used in score projection.

## Quantitative path

At unchanged compute, strict adjusted `<8.17e-09` from the E007 raw/utilization anchor requires

`mse_ratio < 8.17e-09 / (2.23e-08 * 0.36666448) = 0.99919063064`,

about **0.081%** raw-MSE improvement. The candidate adds only O(n) diagnostic work, so raw-MSE improvement is the intended path.

## Frozen diagnostic

Public Phase-2 mini **index 0 only**, exactly once.

Run pinned V25 baseline and E028 candidate under identical flopscope budget, then one unmetered identical candidate repeat solely for determinism. Record final MSEs, ratio, billed FLOPs, residuals, output difference, deterministic difference, projected utilization, and projected adjusted score.

No scorer, holdout, second mini index, teacher forcing, alternate term, coefficient sweep, tuning, or post-result patch/rerun.

## Frozen gates

All must pass:

1. candidate/V25 final MSE ratio `<= 0.99919`;
2. projected adjusted `< 8.17e-09`;
3. projected utilization `<= 0.3666655`;
4. diagnostic billed-FLOP increase `<= 1.0e7`;
5. residual delta `<= 0.005 s` and candidate residual `< 0.400 s`;
6. finite outputs;
7. deterministic repeat max absolute difference `== 0`;
8. source patch is exactly one final-only subtraction of the frozen `D3²` contribution.

Any failed or unevaluable gate => **NO-GO / DROP E028**. No rescue under E028.

## Execution budget

Protocol-only first commit, focused tests, then at most one frozen local diagnostic. No official scorer, hidden/full holdout, tuning, sweep, canonical mutation, or modification of E023–E027.
