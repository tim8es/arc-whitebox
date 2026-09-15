# E021 result — dead source-0 feedback transport elision

Status: **DONE / PASS**

Administrative integration idempotency key: `ARC-E021-INTEGRATE-20250915`

Scientific experiment key: `ARC-E021-DEAD-FEEDBACK-20250915`
Promotion key: `ARC-E021-PROMOTE-20250915`

## Provenance

- Canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Scientific GO branch: `research/e021-dead-feedback-lane-20250915`
- Frozen scorer-ready HEAD: `e7777cfbea41a7278b6d89c699858e96e75f5c77`
- Official scorer launch commit: `e42342217cadb7cc37f13e460430594c11bcae77`
- Exact upstream V25: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- Exact V25 estimator blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- Official E021 candidate blob: `261f93702393c5d8ec0f0c3896836aa8b6006a1e`
- Candidate SHA256: `b4805a8744a6e629b857f8e2ddfcb5e675a8d5ebc82d88423e4d514d5544f8ef`
- Candidate replacement count: exactly `1`

The only semantic change was the frozen E021 source-0 V18 feedback transport elision: the aligned source-0 `Zf_st` slot is kept as exact zero and the original `fnp.matmul(WDb, ...)` arithmetic is applied unchanged to source rows `1:`. No other source lane, rank, closure, adaptive-lambda logic, source birth arithmetic, or dslice contraction was changed.

## Frozen local GO evidence

Public mini MLP0 diagnostic run/job: `34975512772` / `104402105800`; artifact `10399750212`.

- output max absolute difference: `0.0`
- relative Frobenius difference: `0.0`
- V25 billed FLOPs: `806303721965`
- E021 billed FLOPs: `805368064493`
- measured saving: `935657472` FLOPs/MLP
- projected utilization: `0.3662389922432709`
- baseline residual wall: `0.2384812919997472 s`
- E021 residual wall: `0.2371761710000868 s`
- residual delta: `-0.001305120999660403 s`
- repeat candidate FLOPs: `805368064493`
- repeat output max absolute difference: `0.0`
- finite: true
- deterministic: true

All frozen development gates passed before scorer authorization.

## Official Phase-2 mini result

Exactly one scorer attempt was run.

- GitHub Actions run: `34976755661`
- job: `104406307076`
- artifact: `10401949418` (`e021-official-scorer-log`)
- terminal state: `completed / success`
- run attempt: `1`
- width/depth: `1024 / 16`
- MLPs: `100`
- FLOP budget per MLP: `2**41`
- adjusted final-layer score: `8.16e-09`
- raw final-layer MSE: `2.23e-08`
- all-layers MSE: `8.86e-09`
- mean compute utilization: `0.36626951`
- failures: `0/100`
- total estimator FLOPs: `8.05e13` as displayed by WhestBench
- estimator residual wall time: `12.849924 s` aggregate
- peak RSS: `14927248 KiB`

Runtime: Python `3.11.16`, NumPy `2.4.6`, flopscope `0.12.1+np2.4.6`, whestbench `0.16.1`.

## Strict gate versus E007

E007 comparator: run `34708297015`, job `103592271367`, artifact `10302524134`, commit `984d66987472a79f40f462962b5934b8305f837b`.

| Gate | E021 | E007 / requirement | Result |
| --- | ---: | ---: | --- |
| adjusted final-layer score | `8.16e-09` | `< 8.17e-09` | PASS |
| raw final-layer MSE | `2.23e-08` | `<= 2.23e-08` | PASS |
| failures | `0/100` | `0/100` | PASS |
| mean utilization | `0.36626951` | `<= 0.36666448` | PASS |
| residual wall aggregate | `12.849924 s` | E007 `15.094064 s` | PASS |
| peak RSS | `14927248 KiB` | E007 `15128328 KiB` | PASS |

The result is a compute-side improvement with unchanged estimator math for the dead source-0 feedback lane. The strict promotion gate passes.

## Decision

**PASS.** E021 is eligible for canonical result integration.

No scorer rerun, parallel scorer, tuning, sweep, holdout access, or scientific-candidate modification was performed during promotion or administrative integration. E003, E006, E010, E014, and E022 are out of scope and unchanged.
