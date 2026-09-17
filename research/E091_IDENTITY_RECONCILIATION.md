# E091 identity reconciliation

Status: **CURRENT-HEAD IDENTITY FREEZE / SUCCESSOR CLARIFICATION**

This file does not edit or invalidate earlier immutable receipts. It states which identities are
scientifically active at the current E091 production bridge and which earlier identities are
readiness-only historical evidence.

## Active production identity

The active production candidate is the one frozen by
`research/E091_PRODUCTION_BRIDGE_FREEZE.json`:

- base estimator: **E043** at commit
  `d0108f7faccaa656d3908f5afeaa90e056881c71`, adapter blob
  `8777dde2b848dd8ae855f9040ca27b4c6f235989`;
- final-layer target-free feature map: `final_layer_coordinate_features_v1`;
- feature dimension: `p=16`;
- coefficient sharing: one `beta in R^16` shared across all final-layer coordinates and across
  calibration networks;
- ridge `lambda=1.0`, no preprocessing, no feature/rank/lambda tuning;
- calibration/evaluation separation unit: **whole synthetic network**;
- deploy identity: E043 base prediction plus final-layer `X @ beta` correction only.

The production-shape exact-family falsifier is separately frozen in
`research/E091_PRODUCTION_SHAPE_EXACT_FAMILY_FREEZE.json` before its calibration/evaluation
targets are materialized.

## Superseded statements, not deleted

`research/E091_SYNTHETIC_ACCURACY_RECEIPT.json` is a tiny local/readiness result (`N=7,p=4,q=2`).
Its statement that no admissible complete production base was frozen was true for that earlier
state but is **superseded for current-head identity** by the later E043 production bridge freeze.
Its 112-FLOP correction number and tiny synthetic raw MSE must never be reported as production
whole-candidate metrics.

Likewise the original `E091_READINESS_RECEIPT.jsonl` p=3/p=4 tiny LOO algebra is retained only as
leakage/identity readiness evidence. It is not the active production feature identity.

Any E051/V29 feasibility receipts on this branch are separate negative base screens and must not
be combined with the E043 production candidate's cost or accuracy evidence.

## Current scientific accounting

Production cost must include the entire selected E043 base plus production feature extraction,
correction, reconstruction/output add where applicable, and instrumentation required by the
measurement contract. Correction-only utilization is forbidden.

Scientific accuracy must be evaluated on targets disjoint from calibration at the whole-network
level. Public/scorer/benchmark holdout/full labels remain forbidden in E091.

The active hard gates remain:

- whole-candidate utilization `<=0.135`;
- held-out raw final-layer MSE `<=1.89e-8` on a preregistered admissible falsifier/evaluation;
- finite output and zero execution failures.

A failed frozen production-shape falsifier is terminal E091 NO-GO: no seed rescue, feature/lambda
change, second family, or rerun tuning under E091.
