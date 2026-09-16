# E049 — 504aldo V29 reproduction gap

Status: PREREGISTERED / protocol-only.

## Provenance

- Canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- External public reference: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.
- Frozen reference implementation: `estimators/estimator_v29.py` at that commit.
- Public reference point recorded by upstream: submission #330093, raw final-layer MSE `2.13e-8`, adjusted `5.40e-9`, `C/B=0.2526`.
- This experiment is a reproduction-gap audit, not a claim that V29 is superior to the current leader.

## Frozen method features to reproduce

The legal reproduction must preserve the upstream V29 algorithmic structure rather than replacing it with a local surrogate:

1. exact/simple K3 factorization and its transported source machinery;
2. memoryless K4 regeneration from transported diagonal content plus covariance off-diagonal structure;
3. D21 feedback thin legs;
4. old-source compression tiers, including the nested oldest-source tier;
5. the V25 online lambda rule exactly as embedded by upstream; no refitting;
6. pooled/batched Strassen-Winograd transport products used by V26-V29;
7. V29 covariance/newborn slots riding the shared transport family and block-symmetric `C_pre` construction;
8. V19 final-layer trim and V20/V27 residual-time buffer/fusion engineering where present in V29.

No coefficients, ranks, ages, lambda tables, beta, term-pruning thresholds, or scheduling constants may be tuned from ARC White-Box project data.

## Code-level reproduction rule

The first implementation action after this protocol is to vendor or mechanically adapt the exact public V29 source from the frozen upstream commit. Any compatibility edits required by the local package layout must be enumerated in `research/E049_CODE_DELTA.md` as a line-level semantic delta from upstream.

Allowed compatibility changes are limited to:

- import/package-path adaptation;
- class/export naming needed by the local harness;
- deterministic instrumentation that does not alter numerical values;
- explicit FLOP-accounting wrappers where the upstream operation is otherwise uncounted by the local harness;
- small-network shape guards needed only for deterministic synthetic replay.

No algorithmic rescue, parameter changes, rank changes, term-list changes, precision changes, clipping, damping, refitting, retuning, or removal of expensive components is allowed before the frozen reproduction verdict.

## FLOP accounting

Budget `B = 2**41 = 2199023255552`.

All operations executed by the estimator count, including:

- K3 factor/source construction and updates;
- K4 regeneration;
- D21 feedback and thin-leg formation;
- old-source range-finder / basis rebuilds / rotations;
- both old-source tiers;
- Strassen/Winograd pre-adds, recursive products, and post-adds;
- covariance transport and block assembly;
- contractions, closures, nonlinear term evaluation, factor construction, QR/range-finder work, and final-layer work.

No FLOP exclusion is permitted merely because work is setup-like, cached, factor-building, closure, or bookkeeping if it performs floating-point arithmetic used by the prediction.

The frozen public reproduction utilization gate is `flops_used / B <= 0.30`.

## Deterministic replay stages

### Stage A — code-level and small deterministic replay

Before public data, verify:

- the vendored source corresponds to upstream V29 at the frozen commit;
- compatibility delta is fully recorded;
- deterministic repeated prediction agrees exactly (`max_abs_diff == 0`) on a fixed small network supported by the implementation;
- outputs are finite;
- the V29 feature switches/constants remain identical to upstream.

Failure here is terminal NO-GO unless the failure is purely an import/package compatibility defect in the just-added adapter; no algorithmic rescue is permitted.

### Stage B — exactly one frozen public-mini diagnostic

Dataset: `aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`, index `0` only.

Run exactly one diagnostic after Stage A GREEN.

Frozen gates:

- raw final-layer MSE `<= 2.30e-08`;
- utilization `<= 0.30`;
- failures `== 0`;
- all outputs finite;
- deterministic repeated prediction (`max_abs_diff == 0`).

Adjusted score is recorded but is not a GO gate for E049. V29 must not be described as a project win unless its adjusted result is better than the current public leader at the time of comparison.

If any frozen gate fails, E049 is terminal `NO-GO / DROP` before optimization. No rerun, rescue, parameter change, precision change, clipping, rank change, term change, or alternate public index is allowed.

## E050 handoff rule

Only if the frozen V29 reproduction passes all E049 gates, profile the honest FLOP ledger and identify exactly one concrete dominant cost bottleneck for a separate E050 protocol. Do not optimize it inside E049.

## Forbidden

- holdout or full split;
- official scorer;
- tuning or sweeps;
- rerun/rescue after the frozen diagnostic;
- canonical or ledger mutation;
- merging this branch;
- claiming leaderboard superiority from reproduction alone.
