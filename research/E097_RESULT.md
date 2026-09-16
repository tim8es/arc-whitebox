# E097 Result — terminal NO-GO / DROP

Branch: `research/e097-rank8-k22-memory-feasibility-20260917`

Canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`

Protocol commit: `d08d3c3d2007fb8d1a4cb61984e79950b0ff6603`

Implementation/workflow commit: `d245fe0012b1d46d9c2748b3f6a0d86ab41aee9c`

## Frozen Stage-A evidence

- workflow run: `35159806767`
- job: `105007698413`
- artifact: `e097-stage-a`, ID `10472257557`
- artifact SHA256: `f6904b4f0644ce965f766eef6301777df0a5b07ed927eb7f20cbb73b9fbee907`
- synthetic MLPs: width `128`, depth `6`, weight seeds `97097/97197`
- Monte-Carlo samples per MLP: `32768`, input seeds `197097/197197`
- rank: exactly `8`
- challenge/public/scorer/holdout/full data: none

All 12 layer observations were finite and signal-eligible. Complete replay was deterministic with scalar-metric max-abs delta `0.0`. The conservative width-1024/depth-16 rank-8 transport bound was only `557842432` FLOPs, utilization `0.0002536773681640625`, so production arithmetic is not the blocker.

## Observed rank-8 representation quality

Aggregate:

- median rank-8 captured off-diagonal K22 Frobenius energy: `0.7629525956209191`
- median rank-8 relative Frobenius error: `0.4856766493094599`
- worst final-three-layer rank-8 energy: `0.7961154094555292`
- worst all-layer rank-8 energy: `0.3530164767297047`

Per-network rank-8 energy by layer:

- network 0: `[0.3633615036, 0.5321483407, 0.7019547292, 0.8130528372, 0.8940839112, 0.9142927751]`
- network 1: `[0.3530164767, 0.5390600535, 0.7297897818, 0.7961154095, 0.8164702260, 0.8330042998]`

Effective rank likewise collapsed with depth: network 0 from `61.92` at layer 0 to `3.70` at layer 5; network 1 from `63.91` to `8.14`.

## Frozen gates

PASS:

- all observations finite
- all observations signal-eligible
- deterministic replay `<=1e-12`
- static rank-8 transport utilization `<0.01`

FAIL:

- median rank-8 energy `>=0.90`: observed `0.7629525956`
- worst final-three-layer rank-8 energy `>=0.80`: observed `0.7961154095`
- median rank-8 relative Frobenius error `<=sqrt(0.10)`: observed `0.4856766493`

## Decision

`E097 = terminal NO-GO / DROP` for the hypothesis **persistent rank-8 K22 memory across all layers**.

No rank increase, alternate seed, larger sample, threshold change, selective-layer rescue, benchmark run, or rerun is allowed under E097.

The measurement does expose a materially different future hypothesis class: K22 becomes sharply more low-rank with depth, so a separately preregistered **late-onset** K22 mechanism may test whether fourth-order memory should be born only after the representation has entered this low-effective-rank regime. That would be a new experiment ID, not an E097 rescue, and still requires a valid closed propagation/response rule plus synthetic accuracy evidence before any challenge access.

No canonical/ledger mutation or merge was performed.
