# E014 protocol — batched joiner schedule + one level-1 Strassen product

Idempotency key: `ARC-E014-INTEGRATION-20260914`

## Frozen provenance

- Canonical base: `research/bootstrap` at `52eacc67dcc9af4813136ff641ea9b71c36c626f`.
- Exact upstream V29: `504aldo/whest-p2-cumulant-k3` commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, `estimators/estimator_v29.py` git blob `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`.
- Proven E012 local result: pair-batched joiner schedule is bit-identical to separate scheduling, numeric calls 7 -> 4, billed FLOPs unchanged, residual 0.244019 ms -> 0.153275 ms (ratio 0.62813, -37.19%).
- E007 official comparator: adjusted final-layer score `8.17e-09`; raw final-layer MSE `2.23e-08`; utilization `0.36666448`; failures `0/100`.

## Single estimator change

Keep exact V29 except for the old-tier joiner range-finder block.

1. Apply the E012 schedule only to the joiner A/P pair: create an interleaved two-item `[Aj, Pj]` view, compute `[Aj, Pj]^T @ Omega` as one dense batched matmul, apply the existing `dAj/dPj` row weights in-place, and accumulate the two forward products.
2. Change exactly one priced operation: compute the forward pair `[Aj, Pj] @ weighted_inner` as one `_Strassen.mm(...)` family at **level 1**.
3. Leave the confined-old-tier `Qp Sfull Qp^T Omega` contribution unchanged and add it after the pair result exactly as V29 does.
4. Freeze `rank=384`, `QPASS`, tier-2 ranks/gates, coefficients, seeds, all other Strassen levels/defaults, and every non-joiner path. No level/rank/seed sweep. No second optimization.

The level-1 choice is fixed before code because it is the smallest legal priced Strassen transform for `(1024 x 1024) @ (1024 x 384)` and uses the E012 residual saving to absorb only one additional recursive family.

## TDD gate

Before production patch code, add focused tests that fail until a patcher produces an E014 estimator with all of the following structural invariants:

- exact upstream V29 hash is required;
- joiner pair transpose is batched once;
- joiner forward pair calls `_Strassen.mm` with literal level `1`/an equivalent frozen level-1 expression;
- the old-tier `Qp` contribution remains present;
- no other V29 constants/ranks/coefficients are changed.

## Local estimator-integration diagnostic

One fixed development record only: public Phase-2 mini index `0`. This is a direct estimator invocation, **not** `whest run`, official scoring, or holdout access.

Run exact V29 and E014 candidate under identical process/environment and a `flopscope.BudgetContext` with `flop_budget=2**41`; record final-layer target MSE, billed FLOPs, residual wall time, finiteness and output shape.

Promote only if every gate passes:

- finite output and exact expected shape;
- `candidate_mse <= 1.01 * baseline_v29_mse` on index 0;
- `candidate_flops / baseline_flops <= 0.9995` (at least 0.05% real billed reduction);
- `candidate_residual_s / baseline_residual_s <= 1.0` (residual overhead does not return above exact-V29 baseline).

Any local gate failure is an immediate E014 DROP. No scorer, no retry, no alternative level, no tuning.

## Conditional official mini gate

If and only if the local gate passes, run exactly one:

`whest run --estimator <frozen E014 candidate> --dataset hf://aicrowd/arc-whestbench-public-2026@v2-phase2 --split mini --runner local`

Official PASS requires all:

- adjusted final-layer score **strictly less than `8.17e-09`**;
- raw final-layer MSE `<= 2.23e-08` (no preregistered accuracy tradeoff);
- failures `0/100`;
- mean compute utilization **strictly less than `0.36666448`**.

Failure of any official gate => DROP. No rerun, holdout, tuning, sweep, parallel scorer, or post-result parameter change.

## Isolation

Do not modify canonical, E003, E006, E010, or E011 during this experiment. Canonical integration is out of scope until evidence exists.