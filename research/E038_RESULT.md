# E038 terminal result — NO-GO / DROP

Idempotency key: `ARC-E038-SOBOL-QMC-20260915`

## Frozen provenance

- Branch: `research/e038-sobol-trajectory-qmc-20260915`
- Canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-only first commit: `d28ab349d2c5e45571c4dd4cd4e5be585636e897`
- RED workflow head: `63fed0d92403b23005a99c2e1703420323288655`
- Frozen implementation commit: `a1481abf1929ec31bf38408c76ff882da9805922`
- Frozen diagnostic harness commit: `a27cf981a9b42a431c4657ba75606f705c0c18aa`
- Frozen measurement arm commit: `240b59aba9ad79fb8e0cc39e7cbff77e35bbd4f5`
- Public Phase-2 mini index: `0` only

No official scorer, holdout/full split, second mini index, sample-count/seed/scramble sweep, fit, tuning, post-hoc calibration, canonical mutation, or ledger mutation was used.

## TDD evidence

RED:

- run `35011288385`
- job `104523598430`
- expected failure: `ModuleNotFoundError: No module named 'methods.e038_sobol_trajectory_qmc'`
- public-mini data were not accessed.

GREEN:

- run `35011414418`
- job `104524030079`
- focused tests: success.

The frozen harness tests-only run also passed before science:

- run `35011548601`
- job `104524470000`
- no public-mini diagnostic was armed in that workflow version.

## Single frozen diagnostic

- run `35011659770`
- job `104524844430`
- scientific HEAD: `240b59aba9ad79fb8e0cc39e7cbff77e35bbd4f5`
- focused tests immediately before science: `4 passed in 1.86s`
- artifact: `10414001823` (`e038-frozen-result`)
- artifact ZIP SHA256: `d4c02343796e2178182e949e7be8af44b58125f7723d6e9e24948c07449a8048`

Frozen setup/sample evidence:

- dimension: `1024`
- samples: `8192`
- Sobol power: `13`
- scramble seed: `38038`
- setup time: `0.18045724699999255 s`
- repeated setup time: `0.1635662540000027 s`
- repeated samples bit-identical: `true`
- finite, exact `(8192,1024)` float32 samples: `true`

Measured index-0 metrics:

- final-layer raw MSE: `5.988316972738756e-06`
- billed FLOPs: `275012141056`
- utilization: `0.1250610426068306`
- adjusted proxy: `7.489051640708883e-07`
- residual wall time: `0.005280733999910581 s`
- predict wall time: `1.5024619860000143 s`
- deterministic prediction repeat max abs difference: `0.0`
- failures: `0`
- finite: `true`
- scope check: `true`

## Gates

PASS:

- utilization `0.1250610426068306 <= 0.14`
- residual `0.005280733999910581 < 0.400 s`
- predict wall `1.5024619860000143 < 120 s`
- setup and repeat setup `<4.5 s`
- failures `=0`
- finite
- deterministic setup and prediction
- frozen scope: exactly 8192 equal-positive scrambled Sobol trajectories, seed 38038, `m=13`, `ndtri`, no fitted/signed/control-variate correction.

FAIL:

- raw MSE `<=1.89e-08`: observed `5.988316972738756e-06`
- adjusted proxy `<2.5e-09`: observed `7.489051640708883e-07`.

## Decision

**NO-GO / DROP E038.**

The direct positive-weight trajectory estimator is computationally excellent but its deterministic quadrature error is orders of magnitude above the competitive finite-width mean target. E038 is closed. No larger/smaller sample count, alternate seed, scramble mode, antithetic augmentation, control variate, sample reweighting, hybrid cumulant correction, rerun, second index, holdout, or official scorer is permitted under E038.
