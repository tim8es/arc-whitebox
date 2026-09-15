# E023 — terminal result

Idempotency key: `ARC-E023-SEARCH-20250915`

Status: **DONE / NO-GO / DROP**

Branch: `research/e023-f68-zero-elision-20250915`

Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

Protocol commit: `0889792c3d5e266869551f275360c50fdcff690e`.

Frozen measurement commit: `724c3808afbcba6844067adb6038023846f2ee93`.

Pinned V25 source: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, blob `195373a110215256b759d7c172ba8c923c62e5cc`.

## Mechanism

E023 removes only exact structural-zero work in the F68 K4->K3 feed carrier embedded in `Z_st`: the transported-y column has an identically zero static `L_st` right factor in generic residual contractions, and source 0 has exactly zero F68 `u/y/c1/c2/w1sq` quantities because it is born before any prior source exists. This is distinct from E021's V18 feedback `Zf_st` lane and from E022 shared-basis rebuilding.

## TDD evidence

RED:

- run `34977224120`
- job `104407921174`
- expected failure: `ModuleNotFoundError: No module named 'methods.e023_f68_zero_elision'`
- scientific diagnostic skipped.

GREEN before measurement:

- final run `34977477445`
- job `104408800575`
- `3 passed in 0.16s`.

An intermediate infrastructure run `34977378524` had `3 passed` and then stopped because the diagnostic script had not yet been committed; it produced no scientific metric and is not used for the decision.

## Frozen local diagnostic

Public Phase-2 mini index 0 only. Exact pinned V25 and frozen E023 candidate were run under identical deterministic setup. No holdout, fit, tuning, sweep, or official scorer.

Measured:

- baseline final MSE: `2.291432634416339e-08`
- candidate final MSE: `2.2896903815820573e-08`
- candidate/baseline MSE ratio: `0.9992396665701125`
- baseline billed FLOPs: `806303721965`
- candidate billed FLOPs: `805388399085`
- billed saving: `915322880` FLOPs/MLP
- projected utilization from E007 anchor: `0.36624823934511425`
- projected adjusted at frozen E007 raw: `8.167335737396049e-09`
- baseline residual: `0.22947815099999502 s`
- candidate residual: `0.2263260859995455 s`
- residual delta: `-0.003152065000449511 s`
- repeated candidate max absolute difference: `0.0`
- max absolute output difference vs exact V25: `3.814697265625e-06`
- relative Frobenius output difference: `4.838123334596194e-07`
- finite: yes
- pinned blob: matched.

## Gate evaluation

PASS:

- saving >= `6.60e8`: `9.1532288e8`
- projected utilization <= `0.3663677`: `0.3662482393`
- projected adjusted < `8.17e-09`: `8.1673357374e-09`
- residual delta <= `5 ms`: `-3.152 ms`
- finite, deterministic, pinned provenance.

FAIL:

- max absolute output error <= `1e-7`: observed `3.814697265625e-06`
- relative Frobenius error <= `1e-7`: observed `4.838123334596194e-07`
- MSE ratio within `[0.999999, 1.000001]`: observed `0.9992396665701125`.

Although the real-arithmetic terms removed are structural zeros, changing the contraction shapes/reduction path caused a non-negligible floating-point trajectory change. The measured MSE happens to improve by about `0.076%`, but the preregistered hypothesis is exact zero-elision, not a numerical-perturbation accuracy rider, so this cannot be counted as a pass.

## Decision

**NO-GO / DROP E023.**

The frozen kill rule forbids rescue by changing contraction association/fusion, source subset, ranks, implementation variant, using another mini index, combining with E021, or treating the observed floating-point drift as a new approximation. No second scientific diagnostic, official scorer, holdout, tuning, sweep, or canonical mutation was performed.
