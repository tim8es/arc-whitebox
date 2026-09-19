# Breakthrough research evidence classification — E109–E113

Snapshot key: `ARC-BREAKTHROUGH-E109-E113-20260919`

This file is an archive classification only. It does not rename historical experiment branches, rerun experiments, or mutate canonical/ledger.

## Unique hypothesis identity

The repository contains multiple scientifically distinct mechanisms reusing the same experiment IDs E109, E110, E112 and E113. The archive therefore assigns a separate immutable `hypothesis_uid` to every mechanism. Original experiment IDs and branches are preserved as historical facts; metrics from same-ID branches must never be merged.

The authoritative machine-readable mapping is:

`research/archive/e109_plus/BREAKTHROUGH_E109_E113_EVIDENCE_INDEX_20260919.jsonl`

## VERIFIED research

Fifteen hypothesis identities have actual protocol/falsifier execution evidence and terminal repository results. Each index record gives the exact protocol commit, falsifier/arm commit, workflow run/job, artifact digest when one exists, result commit, receipt commit, measured metrics and blocker.

Two VERIFIED terminal executions have no GitHub Actions artifact:

- **E110A Householder**: scientific calculations completed, but JSON serialization failed on a nested `numpy.bool_` before upload. Independent exact reconstruction and an append-only verifier receipt exist; no second run occurred.
- **E113B folded-ridge**: the preregistered zero-gradient integrity gate raised before the JSON payload was written. The terminal receipt and Actions log are the evidence; rerun is forbidden.

These are explicit artifact gaps, not fabricated artifact IDs.

## SPECULATIVE / pre-execution

Only one currently observed hypothesis remains speculative:

- `ARC-HYP-20260919-E109A-COUPLED-HAAR-HADAMARD`
- branch: `research/e109-coupled-haar-hadamard-design-20260919`
- protocol commit: `4b249887503862889448858093b8b374d8510bba`
- state: protocol only; no falsifier, run, artifact or result.

It must not be cited as VERIFIED research.

## Frontier evidence

The verified negative evidence now separates several failure modes:

- deep Stein/Jacobian and late gate-pair CVs: coefficient degeneracy or anti-helpful risk;
- exact deep line Rao–Blackwell: real variance reduction but explosive breakpoint cost;
- Gaussian / cumulant / Edgeworth / conditional-moment closures: substantial deterministic later-layer bias remains;
- exact activation-mask message passing: structurally exact but exponential treewidth state;
- radial sufficiency: exact only after annealing over future weights, not for realized white-box weights;
- gate conditioning improves Gaussian closure substantially, but even top-4 conditioning remains orders of magnitude above target.

No public/public-mini/scorer/holdout/full execution is introduced by this archive consolidation.
