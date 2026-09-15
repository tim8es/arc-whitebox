# E036 result — fourth-order Price covariance response + signed K3

Status: **DONE / NO-GO / DROP**

Idempotency key: `ARC-KEEP-GOING-RESEARCH-20260915-E036`

## Provenance

- Branch: `research/e036-price4-covariance-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-only first commit: `88d39d6a67fe36ff0a8dd4c34e46748c8a3c54fb`
- Frozen scientific commit: `757319df9560d4a5e7c659467e667442d2f29748`
- Public Phase-2 mini index: `0` only
- Scientific run: `35007444652`
- Job: `104510668311`
- Artifact: `10411764531`
- Artifact zip SHA256: `b093e9d051afd568e956118ccf6d166834c4fc821a8a4fd35349a20f45ea8c52`

## Focused TDD

- RED run `35007189251`, job `104509796114`: expected `ModuleNotFoundError` before implementation.
- Implementation commit: `712da88b717a2d45563ab633377c6d91a9ca1d5c`.
- Pre-science GREEN run `35007308151`, job `104510204013`: `7 passed in 1.52s`.
- Frozen run focused tests: `7 passed in 1.12s`.

## Frozen local diagnostic

- final-layer MSE: `4.9459251622589696e-05`
- billed FLOPs: `130083214164`
- utilization: `0.05915499703587557`
- adjusted proxy: `4.94592516225897e-06`
- residual wall: `0.03654599399904157 s`
- wall: `2.4481897929999974 s`
- max absolute standardized skew: `0.01885377962734678`
- deterministic repeat max abs: `0.0`
- covariance diagonal max abs error: `1.3552527156068805e-20`
- finite: `true`
- scope: `true`
- newborn indices: `[0, 1016, 852, 128, 298, 351, 766, 136, 839, 125, 396, 278, 496, 354, 407, 217]`

PASS: utilization, residual, finite, deterministic, covariance diagonal tolerance, frozen scope.

FAIL:

- raw MSE `<=1.89e-08`;
- adjusted proxy `<2.5e-09`.

Compared with E035 raw `4.920249745871731e-05`, the fixed Price orders 1–4 produce no material improvement. Nonlinear Gaussian cross-covariance response is therefore not the missing order on this lane.

## Decision

**NO-GO / DROP E036.**

No higher Price order, coefficient change, rank/FIFO change, second mini index, rerun, scorer, holdout, tuning, or rescue is permitted under E036. A further lane must introduce genuinely non-Gaussian cross-neuron information under a new ID.

Canonical was not changed.
