# E027 — terminal result

Idempotency key: `ARC-RESEARCH-CONTINUE-NEXT-20250915`

Status: **NO-GO / DROP**.

- Branch: `research/e027-final-d3g4-prune-20250915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-only first commit: `66688516a97b882168458e7eb24d0fbf96a29f96`
- Implementation commit: `ddd644836089690f24776b1916c3b911c3291b7e`
- Frozen diagnostic harness commit: `469dc6490b7c250bd59b18dabb7feb15532cc7dc`
- Frozen workflow commit: `18beb5c55eb2a8db4b5179e497c5acce46472ad3`
- RED run/job: `34983508369` / `104429602478`.
- GREEN run/job: `34983599500` / `104429917817`, `3 passed in 0.06s`.
- Single frozen diagnostic run/job: `34983772270` / `104430508089`; focused tests inside measurement: `3 passed in 0.07s`.

## Frozen index-0 metrics

- baseline MSE: `2.2895591676535304e-08`
- candidate MSE: `2.2883104722531443e-08`
- MSE ratio: `0.9994546131770572`
- raw improvement: `0.0005453868229428` = `0.05453868229428%`
- baseline FLOPs: `806303721965`
- candidate FLOPs: `806303726061`
- FLOP delta: `4096`
- projected utilization: `0.36666448186264516`
- projected adjusted: `8.172158525853255e-09`
- baseline residual: `0.17795043899936047 s`
- candidate residual: `0.17233897200085835 s`
- residual delta: `-0.005611466998502124 s`
- max absolute output difference: `3.230571746826172e-05`
- deterministic repeat max difference: `0.0`
- finite: PASS
- exact patch scope: PASS
- pinned V25 blob: PASS

## Gate result

FAIL:
- MSE ratio gate `<=0.99919`: observed `0.9994546131770572`.
- projected adjusted `<8.17e-09`: observed `8.172158525853255e-09`.

PASS: utilization, FLOP-delta, residual, finite, deterministic, patch-scope, provenance gates.

Decision: **NO-GO / DROP E027**. No coefficient rescue, alternate final term under E027, rerun, scorer, holdout, sweep, or canonical mutation.
