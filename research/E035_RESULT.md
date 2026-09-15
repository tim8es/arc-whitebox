# E035 result — full covariance + signed rank-4 K3 response

Status: **DONE / NO-GO / DROP**

Idempotency key: `ARC-FOLLOW-RESEARCH-20260915-E035`

## Provenance

- Branch: `research/e035-covariance-signed-k3-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-only first commit: `9774906921ae5efd7851eb2f502083963af0fcc7`
- Frozen scientific commit: `e52a1a02260a6bd332d780d5b12c059ec4c541aa`
- Public Phase-2 mini index: `0` only
- Scientific workflow run: `35006801573`
- Job: `104508485743`
- Artifact: `10411773650`
- Artifact zip SHA256: `2a7139c9ab376dbe852b0f83c945c22b1269e172d90b53de0492573b68fde8cc`

## Focused TDD

- RED: run `35006407098`, job `104507136872`; expected `ModuleNotFoundError` before implementation.
- Final implementation commit: `02af299687d94e25641f64fa9f9928932edc0973`.
- Pre-science GREEN: run `35006639818`, job `104507933900`: `7 passed in 1.34s`.
- Frozen scientific run repeated focused tests: `7 passed in 1.69s`.

No public-mini scientific metric was observed before focused GREEN.

## Frozen local diagnostic

Single allowed public-mini index-0 measurement:

- final-layer MSE: `4.920249745871731e-05`
- billed FLOPs: `133981506388`
- utilization: `0.06092773509772087`
- adjusted proxy: `4.920249745871731e-06`
- residual wall time: `0.03178843799994979 s`
- measured wall time: `3.1175735149999753 s`
- maximum absolute standardized skew: `0.018871310792180504`
- deterministic repeat max abs difference: `0.0`
- covariance diagonal max abs error: `1.3877787807814457e-17`
- finite: `true`
- frozen scope check: `true`
- selected newborn indices: `[0, 1016, 852, 128, 298, 351, 766, 136, 839, 125, 396, 278, 496, 354, 407, 217]`

## Gates

PASS:

- utilization `<=0.14`
- residual `<0.400 s`
- finite
- deterministic repeat
- frozen full-covariance/rank-4 scope

FAIL:

- raw final MSE `<=1.89e-08`: observed `4.920249745871731e-05`
- adjusted proxy `<2.5e-09`: observed `4.920249745871731e-06`
- literal covariance-diagonal identity `==0.0`: observed roundoff `1.3877787807814457e-17`

The raw accuracy gate misses by about `2603.3x`, independently making the experiment terminal. Full covariance improves materially over E034 (`2.431378853033713e-04` raw) but the first-order Gaussian response covariance closure remains far from the required precision.

## Decision

**NO-GO / DROP E035.**

No covariance-formula change, tolerance relaxation, rank/FIFO change, K4/D21 add-back, alternate quadrature, second mini index, rerun, official scorer, tuning, sweep, or rescue is allowed under E035. Any non-Gaussian or higher-order covariance response is a new E036+ experiment.

Canonical was not changed and no official scorer or holdout was used.
