# E015 protocol — rank-3 operator-valued Mori–Zwanzig / Prony old-tier memory

Idempotency key: `ARC-E015-MZ-DIAGNOSTIC-20260914`

Status: preregistered local feasibility diagnostic only.

## Frozen provenance and isolation

- Canonical base: `research/bootstrap` at `52eacc67dcc9af4813136ff641ea9b71c36c626f`.
- Exact upstream V29 source: `504aldo/whest-p2-cumulant-k3` commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, `estimators/estimator_v29.py` git blob `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`.
- E007 scientific comparator remains adjusted score `8.17e-09`, raw final-layer MSE `2.23e-08`, utilization `0.36666448`, failures `0/100`.
- E012/E014 are scheduling/Strassen joiner lanes. E015 does not batch joiners, use Strassen/Hopcroft–Kerr, alter ranks/bases, revive E011, or revisit E001–E010 mechanisms.
- `research/ledger.csv`, canonical estimator, canonical branch, official scorer, holdout and submission state must not be modified in this phase.

Official Phase-2 contract reference: width 1024, depth 16, per-MLP budget `2**41`, CPU grading, output `(16,1024)`, final-layer MSE primary accuracy term. E015 does not invoke `whest run`; it uses direct estimator calls only to expose public development trajectories.

## Single hypothesis

Keep V29 young-source machinery, covariance path, regenerated K4, D21 feedback/thin terms and final-layer trim unchanged. Replace only the expensive explicit old-source **dense A/P contribution to D21** with a three-state matrix-valued causal memory closure.

At each layer let:

- `U_l` be the exact V29 dense **young-tier** D21 contribution (the `ka:` A/P contractions, before thin feedback terms);
- `Y_l` be the exact V29 dense **old-tier** D21 contribution (the `inner @ Qc.T` shared-basis contraction, before thin feedback terms).

The proposed order-3 direct-form-II realization is shared globally across every MLP and layer:

```text
w_l = U_l + c1*w_{l-1} + c2*w_{l-2} + c3*w_{l-3}
Yhat_l = d0*w_l + d1*w_{l-1} + d2*w_{l-2} + d3*w_{l-3}
```

`w_{l-1:l-3}` are the only three auxiliary matrix states. The poles are the roots of

`z^3 - c1 z^2 - c2 z - c3 = 0`.

All seven scalar coefficients are shared across MLPs; there are no per-MLP, per-layer or per-neuron fitted coefficients. This is an operator-valued Prony/Mori–Zwanzig memory in the sense that the latent states and input/output are matrices while the temporal realization is a shared rank-3 rational kernel.

## Development fit and frozen validation

Public Phase-2 mini records are used only as development diagnostics.

- Fit set: dumps / indices `0,1,2,3`.
- Recursive validation set: dumps / indices `4,5,6,7`.
- Fit/score layers: `8..14` inclusive.
- The recurrence is initialized with zero states before the first old-tier layer and rolled forward from the first available old-tier/young-tier pair through layer 14.
- Fit coefficients exactly once by global least squares over all Frobenius inner products from dumps 0–3, equivalent to regressing every matrix entry jointly on `[Y_{l-1},Y_{l-2},Y_{l-3},U_l,U_{l-1},U_{l-2},U_{l-3}]`. No coefficient is fit on dumps 4–7.
- After fit, freeze coefficients and poles. Validation on 4–7 uses only current/past `U` and the three predicted memory states. It must never feed true `Y` back into the recurrence.
- No regularization grid, order sweep, pole clipping, seed sweep, alternate target decomposition or post-validation refit is allowed. If the one least-squares realization is unstable/nonfinite, E015 is NO-GO.

## Extraction boundary

The diagnostic may instrument a byte-for-byte pinned V29 source only to record `U_l` and `Y_l`. The instrumentation must not alter the values used by V29 itself. K4, feedback/thin D21 terms, covariance and trim are not targets and are not approximated.

The exact V29 git-blob hash must be verified before instrumentation. Any source mismatch is a hard blocker.

## Local gates

GO requires every condition simultaneously on frozen validation dumps 4–7:

1. mean old-tier D21 relative RMS across layers 8–14 `<= 0.015`;
2. worst single-layer relative RMS across all validation dumps/layers 8–14 `<= 0.022`;
3. exactly three or fewer auxiliary matrix states (this realization uses three);
4. no per-MLP coefficients and one frozen coefficient vector/pole set from dumps 0–3;
5. deterministic repeated recursive validation (bit-identical coefficient vector and predictions under identical inputs);
6. all coefficients, poles and predicted matrices finite;
7. projected total utilization `<= 0.21` of the `2**41` budget;
8. no residual/resource regression in the frozen local proxy: three-state recurrence median residual time must not exceed the exact old-tier dense-contraction proxy at the same `n=1024`, and persistent candidate state must be no larger than the explicit old-history storage it replaces.

Relative RMS is `sqrt(mean((Yhat-Y)^2)) / sqrt(mean(Y^2))`. The mean gate is the arithmetic mean of the 28 validation record/layer relative-RMS values.

## Compute projection

Use the pinned upstream V29 cost anatomy, not a fitted post-hoc cost model. Its normalized cubic-unit totals are:

- total V29: `260.09` units;
- explicit old-source shared-basis tier: `106.79` units;
- preserved non-old work: `153.30` units.

The E015 recurrence adds only O(3*n^2) state arithmetic per active layer. Projected utilization is computed from direct V29 billed utilization on the same development records multiplied by the frozen normalized retained-work ratio plus explicitly metered recurrence O(n^2) FLOPs. No arithmetic may be hidden from the projection.

## Residual/resource proxy

For the one frozen `n=1024`, `r=384`, float32 shape, after one warm-up measure seven repetitions of:

- baseline proxy: one exact old-tier dense contraction `(1024,384) @ (384,1024)`;
- candidate: one full three-state recurrence update/output on `(1024,1024)` matrices.

Use median residual wall time. Candidate must be `<=` baseline. Persistent candidate state is exactly three float32 1024x1024 matrices (`12 MiB`); temporary output/current-state buffers do not count as persistent history.

## Kill rule

Any failed gate => `NO-GO` and E015 stops. No alternate recurrence order, coefficient regularization, pole stabilization, different fit split, layer window, teacher forcing, scorer, holdout, rank/order sweep or tuning is permitted under E015.

## GO handoff boundary

If all local gates pass, prepare but do not execute a scorer-ready handoff describing the exact frozen coefficients/poles, estimator patch boundary, expected compute projection, tests and a separate future scorer gate. Official scoring remains forbidden until separately authorized and canonical state remains unchanged.
