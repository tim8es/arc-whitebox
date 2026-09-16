# E049 result — terminal NO-GO / DROP

## Provenance

- Branch: `research/e049-v29-reproduction-gap-20260916`.
- Canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Frozen upstream: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.
- Upstream estimator: `estimators/estimator_v29.py`, Git blob `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`, 93422 bytes.
- Protocol-only commit: `4566695144ddddcf0f751e3a803bab56e78a469f`.

## Exact vendor evidence

Vendoring workflow commit: `07d83920a87e272a9500a9741ea55a9a80a97e8a`.

GitHub Actions:

- run `35093529370`
- job `104785247051`
- conclusion: `success`

The workflow fetched the frozen upstream estimator and license directly from the pinned upstream commit and verified `git hash-object` before commit:

- estimator blob: `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`
- license blob: `2c843327a87b547245b566f02391295ba71ad26a`

Exact vendor commit: `1876fddfa86d29b6146fd29f51135799bc4fa3b6`.

`methods/e049_v29_upstream.py` is byte-for-byte the upstream V29 estimator. Algorithmic delta from upstream V29: zero lines. `research/E049_CODE_DELTA.md` records the feature-level delta relative to the canonical covariance baseline.

## Frozen small deterministic replay

Test commit: `07e3ed550773adc9aecb1ab9b92be6c984fc390d`.

Focused workflow commit: `d7399df15afc360f3015b7e40be7b71273968263`.

Frozen replay configuration:

- width 32
- depth 8
- PCG64 seed 49049
- float32 network weights with standard `1/sqrt(width)` scaling
- budget `2**41`
- two fresh estimator instances required for deterministic equality

GitHub Actions:

- run `35093649358`
- job `104785629529`
- conclusion: `failure`
- pytest: `1 failed, 2 passed, 14 warnings in 2.05s`

Passed before the numerical replay:

1. exact vendored file length = 93422 bytes;
2. exact Git blob SHA = `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`;
3. frozen V29 defaults/ranks/ages/Strassen parameters and kill-switch states matched upstream.

Failure during first numerical replay:

- overflow / invalid multiply warnings occur on the off-suite width-32/depth-8 path;
- covariance assembly becomes NaN;
- at upstream line 1405, `flops.as_symmetric(C, symmetry=(0, 1))` raises
  `flopscope.errors.SymmetryError` because the matrix contains NaNs;
- therefore finite/deterministic Stage-A replay does not pass.

This is not an import/package compatibility defect and cannot be repaired under the frozen E049 protocol without changing the tested numerical path. Consequently the Stage-A kill rule applies.

## Decision

**NO-GO / DROP before public-mini.**

The frozen public `mini[0]` diagnostic was not run. Therefore no E049 public raw MSE, adjusted score, or utilization metric is claimed.

No E050 optimization handoff is opened because the frozen V29 reproduction did not pass E049's preregistered local reproduction gate.

No rerun, rescue, rank/age/precision/term/lambda/Strassen change, tuning, sweep, holdout, full split, official scorer, canonical mutation, ledger mutation, or merge was performed.
