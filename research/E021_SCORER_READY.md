# E021 scorer-ready protocol

Status: GO from the single frozen public MLP0 diagnostic.

Idempotency key: `ARC-E021-DEAD-FEEDBACK-20250915`

## Frozen candidate

- Research branch: `research/e021-dead-feedback-lane-20250915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Exact V25 ancestor: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- Exact V25 estimator blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- E021 implementation commit: `eff1a1b1ab37fb8cbbd0d0ed41aa941c05ff9ec8`
- Frozen diagnostic commit: `dcd9cee9ae823cdf86f97ad0e1b1c29b21eb5195`
- Frozen diagnostic run/job: `34975512772` / `104402105800`
- Diagnostic artifact: `10399750212`

## Candidate transformation

Starting from the exact V25 blob above, make exactly one semantic change to the V18 feedback transport:

Baseline:

```python
if Zf_st is not None:
    Zf_st = fnp.matmul(WDb, Zf_st)
```

Candidate:

```python
if Zf_st is not None:
    Zf_st = transport_feedback_without_source0(WDb, Zf_st)
```

where the helper preserves source row 0 as an exact zero row and applies the original `fnp.matmul(WDb, ...)` operation unchanged to source rows `1:`. Do not change source ordering/alignment, R_FB/R_RES ranks, old-source confinement, adaptive lambda, source birth arithmetic, dslice contractions, or any other source lane.

## Frozen public evidence

On public Phase-2 mini MLP0:

- exact V25 expected/observed blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- source-0 zero-birth invariant verified in exact source
- full estimator output max absolute difference: `0.0`
- relative Frobenius difference: `0.0`
- V25 billed FLOPs: `806303721965`
- E021 billed FLOPs: `805368064493`
- measured saving: `935657472` FLOPs/MLP
- projected utilization from frozen E007 reference: `0.3662389922432709`
- baseline residual wall: `0.2384812919997472 s`
- E021 residual wall: `0.2371761710000868 s`
- residual delta: `-0.001305120999660403 s`
- repeat candidate FLOPs: `805368064493`
- repeat output max absolute difference: `0.0`
- finite: true
- deterministic: true

All preregistered E021 development gates passed.

## Official scorer handoff

No official scorer has been run under E021. If separately authorized, scorer evaluation must use only the frozen candidate transformation above, with no additional optimization, tuning, rank changes, source-lane changes, arithmetic changes, or holdout-informed edits before the run. The scorer result must be attributed to the exact frozen candidate revision used for packaging.

This document authorizes no scorer execution by itself.
