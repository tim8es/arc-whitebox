# E018 — terminal result

Status: **DONE / NO-GO / DROP**

Branch: `research/e018-importance-old-d21-20260915`

Frozen diagnostic run: `34912459914`, job `104202751388`, artifact `10375460886`.

Comparator: E007 raw `2.23e-08`, adjusted `8.17e-09`, utilization `0.36666448`, failures `0/100`.

## Frozen mechanism

384 with-replacement row samples per old-source D21 contraction using inverse-probability weighting and probabilities proportional to stacked AP/AA/PP column Frobenius norm. Frozen dumps 4..7, layers 8..14, deterministic seed rule. No target fitting, no official scorer, no holdout, no tuning or sweep.

## Measured result

- focused tests: `5 passed in 0.14s`
- record count: `180`
- aggregate old-D21 relative RMS: `1.3590123715287898` vs gate `<=0.015` — **FAIL**
- median relative RMS: `1.2548678404793345`
- worst relative RMS: `1.8626966195629133` vs gate `<=0.022` — **FAIL**
- projected utilization under frozen idealized cost arithmetic: `0.3231398132564398` vs gate `<=0.325` — PASS
- projected adjusted at unchanged E007 raw: `7.206017835618608e-09` vs gate `<=7.25e-09` — PASS
- target family ratio: `0.44668458781362` vs exact frozen max `0.4466845878` — numerical boundary miss in script gate
- finite/deterministic contract: PASS
- diagnostic completed without exhaustion: PASS
- no persistent candidate n×n state: PASS
- frozen dump/layer observation completeness: FAIL because layer 14 has no captured old-D21 records in the instrumented V25 path.

The scientific failure is decisive independently of the bookkeeping misses: aggregate and worst contraction errors are roughly two orders of magnitude above the preregistered fidelity limits.

## Decision

**NO-GO / DROP E018.**

Do not rescue under E018 by changing sample count, probability rule, clipping/flooring, seed, averaging multiple sketches, changing the layer/dump set, fitting targets, tuning, holdout access, or scorer execution. The mechanism is also conceptually redundant with the previously closed old-source importance/HT route, so it should not be revived under a new identifier.
