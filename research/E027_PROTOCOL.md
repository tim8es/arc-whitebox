# E027 — final-layer mixed D3×G4 Wick-term prune

Idempotency key: `ARC-RESEARCH-CONTINUE-NEXT-20250915`

Status: preregistered bounded local diagnostic.

## Provenance

- Branch: `research/e027-final-d3g4-prune-20250915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Pinned upstream V25: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- Exact `estimator_v25.py` blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- E007 anchor: raw `2.23e-08`, utilization `0.36666448`, reported adjusted `8.17e-09`.

E023/E024/E026 are closed and immutable. E025 is occupied by another session and is not touched.

## Primary-source motivation

The companion-paper audit recorded in upstream F48 explicitly identifies **score-driven term selection** as a valid budget lever: the nonlinear Wick/Hermite program contains diagram terms of different asymptotic grade, and the tracked set may be adapted to the score rather than only changing cumulant order. V25's `(1,)` mean program contains five terms, including the mixed product

`('d3', 'g4', wick_index=20, coefficient=1/144)`.

At the final layer V19/V25 is already mean-only, so changing this one contribution cannot alter any propagated state. Both `D3` and `g4row` are approximate higher-cumulant channels; their mixed product is therefore the cleanest single final-only diagram to test for over-correction without changing the K3/K4 propagation itself.

## Frozen mechanism

Layers 0..14 are byte-for-byte V25 behavior. On layer 15 only, after the ordinary V25 `PK1` evaluation, subtract exactly the contribution of the single `(1,)` mixed `D3×G4` row:

`delta_31_4 = D3 * g4row * (WT[20] / 144)`

`pk1v_candidate = pk1v_v25 - delta_31_4`.

No other Wick term, lambda, rank, source, basis, covariance, D3, G4, or propagation equation changes. No coefficient sweep and no partial damping: the term is either present (V25 comparator) or absent (E027 candidate).

The bounded diagnostic may implement the prune as a final vector subtraction even though a production implementation could omit that row structurally. Measured diagnostic FLOPs, including that subtraction, are used for the projected score.

## Quantitative path

At unchanged utilization, strict adjusted `<8.17e-09` from the E007 anchor requires

`mse_ratio < 8.17e-09 / (2.23e-08 * 0.36666448) = 0.99919063064`,

about **0.081%** raw-MSE improvement. The diagnostic adds only O(n) work, so raw improvement is the intended score path.

## Frozen diagnostic

Public Phase-2 mini **index 0 only**, exactly once.

Run pinned V25 baseline and E027 candidate under the same flopscope budget, followed by one unmetered identical candidate repeat for determinism. Record baseline/candidate final MSE, ratio, billed FLOPs, residual times, output difference, deterministic difference, projected utilization and projected adjusted score.

No scorer, holdout, second mini index, alternate term, coefficient damping, teacher forcing, tuning, or sweep.

## Frozen gates

All must pass:

1. candidate/V25 final MSE ratio `<= 0.99919`;
2. projected adjusted `< 8.17e-09`;
3. projected utilization `<= 0.3666655`;
4. diagnostic billed-FLOP increase `<= 1.0e7`;
5. residual delta `<= 0.005 s` and candidate residual `< 0.400 s`;
6. finite outputs;
7. deterministic repeat max absolute difference `== 0`;
8. source patch is exactly one final-only subtraction of the frozen `D3×G4` contribution.

Any failed or unevaluable gate => **NO-GO / DROP E027**. No rescue under E027.

## Execution budget

Protocol-only first commit, focused tests, then at most one frozen local diagnostic. No official scorer, hidden/full holdout, tuning, sweep, canonical mutation, or modification of E023–E026.
