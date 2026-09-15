# E029 terminal result — NO-GO / DROP

Idempotency key: `ARC-WIN-RESEARCH-20260915`

## Frozen provenance

- Branch: `research/e029-signed-layer1-angular-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-only first commit: `856b3d0199e5a7261d6ce7344e5e36ff5d742485`
- Frozen diagnostic commit: `277f0d8ff23889249391928d310717719463e03c`
- Frozen run: `34994691187`
- Frozen job: `104467863533`
- Public mini index: 0 only

## Measured metrics

- final-layer MSE: `1.3173209365449812`
- billed FLOPs: `214396499292`
- utilization: `0.09749624009236868`
- adjusted proxy: `0.13173209365449812`
- residual: `0.008202136999926779 s`
- wall time: `2.426755598999989 s`
- layer-1 max absolute analytic-mean mismatch: `1.1879386363489175e-14`
- layer-1 max relative mismatch: `2.146406046545097e-14`
- signed-weight sum: `0.9999999999999594`
- signed-weight L1: `1.0392354449969052`
- min/max weight: `-0.0003982488447938591` / `0.000997776342138583`
- deterministic repeat max absolute difference: `0.0`
- support: 3072 antipodal pairs / 6144 endpoints

Compute, residual, exact layer-1 matching, normalization, L1 stability, finite, deterministic and scope gates passed. Accuracy gates failed catastrophically: final MSE `1.3173 >> 2.45e-08`, adjusted proxy `0.1317 >> 2.5e-09`.

**Decision: NO-GO / DROP E029.**

Interpretation: exact matching of every first-layer marginal plus stable signed weights is not a transferable observable for the deep network. E029 is closed; no support-count, ridge, frame-family, clipping, or other rescue is permitted.