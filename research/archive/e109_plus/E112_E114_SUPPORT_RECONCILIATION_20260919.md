# E112–E114 support reconciliation — 2026-09-19

Snapshot: `ARC-ARCHIVE-E112-E114-SUPPORT-20260919`

This is an append-only archive reconciliation. It does not modify source experiment branches, `research/bootstrap`, or `research/ledger.csv`.

## Unique hypothesis identities

Historical experiment IDs are preserved, but every distinct mechanism is indexed by a unique immutable `hypothesis_uid`.

### E112 — all VERIFIED terminal NO-GO

- `ARC-HYP-20260919-E112A-CUMULANT-JOINTLAW`
- `ARC-HYP-20260919-E112B-EDGEWORTH4-RELU-PLUGIN`
- `ARC-HYP-20260919-E112C-EXACT-MASK-MESSAGE-TREEWIDTH`

These are distinct mechanisms and their metrics must not be merged. The Edgeworth-4 mechanism is the strongest failed E112/E113 portfolio member by the existing owner support receipt, but it still misses the exact-small-width target by `15891.9496x`.

### E113 — all VERIFIED terminal NO-GO

- `ARC-HYP-20260919-E113A-ANNEALED-RADIAL-SUFFICIENCY`
- `ARC-HYP-20260919-E113B-DEEP-FOLDED-RIDGE-RESIDUAL`
- `ARC-HYP-20260919-E113C-TOP2-GATE-CONDITIONAL-MOMENTS`
- `ARC-HYP-20260919-E113D-TOP4-GATE-CONDITIONED-PLUGIN`

The folded-ridge run has no artifact because the frozen zero-gradient terminal gate fired before JSON creation. This is an explicit artifact gap, not missing archive work.

## VERIFIED support receipt

The owner portfolio receipt is indexed as support evidence rather than as a new scientific hypothesis:

- support UID: `ARC-SUPPORT-20260919-E112-E113-PORTFOLIO`
- markdown commit: `777308b93fd8da3a2c0607d614acda5711032ac3`
- JSON commit: `95620e9feee01f953e94c131305b68d34149f0da`
- source E112 head: `58c4f203990d3336a41d060a5a9d7bbf05e0ad58`
- source E113 head: `b94cceb787715bafe3736d77798b1a4afeffc4a7`
- production gate authorized: **false**

## E114A — VERIFIED positive exact-small-width closure

Unique hypothesis UID:

`ARC-HYP-20260919-E114A-ACTIVATION-BOUNDARY-FLUX`

Evidence:

- protocol: `2ef10a3cc00c7f1e6b8b967d3c0ced210ee1b11c`
- executable exact falsifier: `800fc858c0a0b142f5ceecc18d929dffaaabe911`
- workflow head: `d9d37664bcd3f89d5dece2473a1614203ae0d99c`
- run/job: `35455223230 / 105929190535`
- artifact: `10588126544`
- artifact SHA256: `dd7a49166fe7f3cc469b145914e8b8b00680bfbeaa574b8539cdbad50defb84f`
- result: `3cb02a60b16848af14e0c0dd9199509af9fb0767`
- sealed receipt: `b9f64030f65da9b32fc7718d04fb108ee1a73dab`

The exact frozen fixture verifies the activation-boundary flux identity to floating-point roundoff. This is a real **scientific exact-small-width GO** for the identity, but:

- `production_go=false`
- `competition_go=false`
- no production run
- no public/public-mini/scorer/holdout/full access.

The current blocker is the production representation cost of the activation-boundary set and flux weights.

## E114B — speculative/unmaterialized alias

Branch:

`research/e114-exact-reference-output-compression-20260919`

currently points to the same head as E114A:

`b9f64030f65da9b32fc7718d04fb108ee1a73dab`

That head explicitly identifies itself as `ARC-E114-ACTIVATION-BOUNDARY-FLUX-20260919`. No separate output-compression protocol, falsifier, run, artifact, result, or receipt was found.

Therefore the branch-name idea receives a unique archive UID

`ARC-HYP-20260919-E114B-EXACT-REFERENCE-OUTPUT-COMPRESSION`

but is classified **SPECULATIVE_UNMATERIALIZED_ALIAS**, not VERIFIED research.

The machine-readable source of truth for this snapshot is
`research/archive/e109_plus/E112_E114_SUPPORT_RECONCILIATION_20260919.jsonl`.
