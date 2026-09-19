# E106 terminal result — cross-fitted quartic Haar control variate

Idempotency key: `ARC-E106-CROSSFIT-QUARTIC-HAAR-CV-20260919`

Decision: **TERMINAL NO-GO / DROP**

## Provenance

- Branch: `research/e106-crossfit-quartic-haar-cv-20260919`
- Canonical parent: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-first commit: `3413ac3715c8de0ca15269439b9e746ef64e46af`
- RED test commit: `21fe71f444e3ddf6d82b21a06688ccee8600b513`
- RED workflow commit: `86abeb89dddab3da4c57cfb88bd57fd02a0b0def`
- Frozen implementation commit: `a04b066ab25fb9063dbd2ff3d46958d55845b176`

## TDD evidence

RED:
- run `35447172293`
- job `105907990454`
- expected `ModuleNotFoundError: No module named 'methods.e106_crossfit_quartic'`
- scientific diagnostic skipped.

GREEN + sole frozen production-shape diagnostic:
- run `35447293057`
- job `105908318459`
- `4 passed in 0.23s`
- workflow/job: success
- no rerun.

Artifact:
- name: `e106-crossfit-quartic`
- ID: `10585795400`
- size: `1400` bytes
- ZIP SHA256: `a3d5ddb4cab5c94dbc55b68bebafd882e3e03e3645d62f5ee513600b03509542`
- expiry: `2026-12-18T13:57:54Z`

## Frozen method

The E104 two-Haar analytic-radius estimator was augmented with K=256 exact-zero-mean quartic
spherical controls

`z_u(q) = (q^T u)^4 - 3/(n(n+2))`

using normalized first-layer weight rows as frozen directions. Coefficients were independently
fit on the opposite Haar block and cross-applied symmetrically. No ridge, clipping, fallback,
feature/rank sweep, tuning, public data, or targets were used.

## Production-shape target-free measurement

Fixed synthetic network:
- width/depth: `1024 x 16`
- weight seed: `104104`
- two independent estimator direction seeds: `106105`, `106106`
- trajectories per estimator: `4096`
- exact E104 analytic chi-radius / antithetic law.

Target-free raw stochastic MSE-risk estimates at the final layer:

- uncorrected E104 baseline: `1.3979116556251261e-05`
- E106 candidate: `1.6334871771532102e-05`
- candidate / baseline: `1.168519606071056`

Thus the frozen quartic cross-fit increases measured stochastic risk by about 16.85%.

Competition raw gate:
- target: `<=1.89e-08`
- candidate target-free risk: `1.6334871771532102e-05`
- gate: **FAIL**

Adjusted-risk proxy:
- score multiplier: `0.1`
- candidate adjusted-risk proxy: `1.6334871771532103e-06`
- target: `<2.5e-09`
- gate: **FAIL**

## Complete billed compute

Each independent E106 estimator execution:

- input construction: `11,541,346,992` FLOPs
- frozen quartic feature setup: `1,077,674,240` FLOPs
- 16 layer total: `154,870,652,928` FLOPs
- finalization: `65,536` FLOPs
- total/reconciled: `167,489,739,696` FLOPs
- utilization: `0.07616551542741945`
- utilization <= 0.14: **PASS**
- exact accounting reconciliation: true

Execution walls:
- A: `2.287193911000031 s`
- B: `2.260826599999973 s`
- deterministic repeats: `2.270644457000003 s`, `2.2589398779999783 s`

Structural/replay gates:
- exact antithetic pair max abs: `0.0`
- feature unit-norm max error: `9.12105200256974e-08`
- candidate predictions bitwise deterministic: true
- baseline predictions bitwise deterministic: true
- candidate risk repeat abs: `0.0`
- baseline risk repeat abs: `0.0`
- FLOP ledgers deterministic: true
- finite: true

## Decision

**E106 = TERMINAL NO-GO / DROP.**

The fixed K=256 first-layer quartic angular controls do not explain the dominant deep-network
Haar-block error; under the preregistered cross-fit rule they increase rather than decrease
production-shape stochastic risk. No E106 rescue, coefficient modification, K sweep, rerun,
or scorer is permitted.

No public/public-mini, benchmark target, official scorer, holdout/full, canonical mutation,
ledger mutation, or merge occurred.
