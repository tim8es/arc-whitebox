# R247 — H-R246 network-agnostic V25 efficiency test

## Outcome

**DEVELOPMENT NO-GO before public measurement.** The frozen target-free falsifier failed by a large margin, so the protocol forbids implementing/running the public mini-100 candidate or launching Actions.

## Ownership and scope

R247 was claimed as `network-agnostic-efficiency-research` and started as `R247-h-r246-network-agnostic-efficiency-20260923`. The work read current process/history plus the immutable R209 V25 baseline and R246 diagnostic. It did **not** read R223 or R244 candidate outputs/artifacts.

No estimator, benchmark, ARC targets, public mini-100 candidate measurement, Actions workflow, paid compute, private/holdout data, submission, leaderboard action, canonical V25 mutation, or retry occurred.

## History deduplication

The pinned 504aldo findings log and project history close the obvious V25 cost families: age/rank confinement and nested tiers, source dropping/windowing, memoryless slice closure, hub-column caps/CP merge, randomized Hadamard contraction estimation, structured projection/FWHT, deeper Strassen, precision changes, and further V25 rank knobs. R223 V25-LF and R244 MP-R16 were excluded by assignment.

One mechanism with no matching 2:4/N:M/magnitude-pruning experiment in the pinned findings history was frozen:

**V25-NM24-YOUNG-D21-RIGHT-SPARSIFY** — in young dense-source D21 contractions only, replace each A/P right-factor row by deterministic groupwise 2-of-4 magnitude pruning with per-group L2-energy rescaling. All other V25 paths remain unchanged. The rule is fixed globally and uses no target, network ID, row score, or per-network parameter.

Frozen candidate spec: `research/r247/R247_CANDIDATE_SPEC.json`, blob `b52dafbc77714276de5dbd14332426f3c664df47`.

## Static cost gate

R209 V25 mean measured FLOPs: `806,303,721,965` = `375.4644291312434` units of `2*n^3`.

F72/F73 anatomy attributes 108 units to the two young dense D21 right-factor contractions (54 young source-pairs × 2 contraction units). Ideal 2:4 arithmetic removes 54 units. Even reserving 10 units for selection/rescaling/sparse-kernel overhead gives:

- conservative candidate: `331.4644291312434` units;
- conservative ratio to R209: `0.8828118016350895`;
- required ratio: `<= 0.9`.

Therefore the **static cost gate passed**. This is a planning bound, not a metered result.

## Frozen target-free falsifier

Protocol: `research/r247/R247_PROTOCOL.json`, blob `112c6716ec45a445bbe493ff2942210f9d423d88`.

Falsifier: `scripts/r247_nm24_falsifier.py`, blob `426f96d271f95cfccab968cf232861b595c81bdb`.

It evaluates only the affected D21 contraction on deterministic synthetic states: four fixed seeds × two fixture families (`iid` and `v25_like_correlated`), n=128, eight young sources. No dataset or targets are used.

Frozen GO gate:

- finite and deterministic in 8/8 cases;
- identity control RRMS <= 1e-14;
- every candidate D21 RRMS <= 0.015;
- mean candidate D21 RRMS <= 0.012.

The 1.5% screen is conservative relative to the historical F71/F72 eps² diagnostic linking roughly 2.2% D21 RMS error to about +10% raw-MSE at this closure.

## Falsifier result

Result: `research/r247/R247_FALSIFIER_RESULT.json`, blob `e8bd5d527f1bb20617b37a3879fefdbdc1a13e49`.

Identity, finite, and deterministic gates passed. Accuracy-preservation gates failed:

| fixture | seed | D21 relative RMS error |
|---|---:|---:|
| iid | 247001 | 0.3726602999561968 |
| iid | 247002 | 0.37126109558787107 |
| iid | 247003 | 0.37536843453518165 |
| iid | 247004 | 0.38016503271515556 |
| V25-like correlated | 247001 | 0.36133862381167436 |
| V25-like correlated | 247002 | 0.3676833135842606 |
| V25-like correlated | 247003 | 0.373725657958854 |
| V25-like correlated | 247004 | 0.37255166261631883 |

Mean D21 RRMS = **0.37184426509568913**; maximum = **0.38016503271515556**. The mean is about 31× the frozen 0.012 mean gate and every case is about 24× or more above the 0.015 per-case gate.

This is sufficiently far from the prerequisite structural fidelity that no public mini-100 measurement is scientifically justified under the frozen protocol.

## Frozen public gates that were not exercised

Had the falsifier passed, a single verified-free standard Actions workflow could have run validation plus exactly one candidate public mini-100 panel. Scientific GO additionally required exact R209 row/hash identity, 0 failures, mean adjusted score <= `8.12954545291664e-9`, >=55/100 improved, paired gain >2 descriptive SE, mean FLOPs <= `725,673,349,768.5`, max residual <0.4 s, and raw-MSE degradation strictly <11.111111111111116%.

Because the target-free falsifier failed, none of these public gates were measured and no retry/second mechanism is authorized under R247.

## Conclusion

The tested configuration is rejected: **2:4 magnitude sparsification of young-source D21 right factors offers enough nominal FLOP reduction but destroys the D21 contraction far beyond the preregistered structural-error budget.**

This rejects only `V25-NM24-YOUNG-D21-RIGHT-SPARSIFY`; it does not reinterpret R223, R244, or the canonical V25 baseline.
