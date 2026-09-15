# E028 terminal result — GO / scorer-ready handoff

Idempotency key: `ARC-E028-TERMINAL-20250915`

## Frozen provenance

- Branch: `research/e028-final-d3sq-prune-20250915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Frozen diagnostic commit: `8f4e380e83109a85f840561b54f0bfe3b4907046`
- Pinned upstream: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- Pinned `estimator_v25.py` blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- Frozen diagnostic run: `34984554189`
- Frozen diagnostic job: `104433192579`
- Public Phase-2 mini index: `0` only

The workflow and scientific diagnostic both completed successfully. No rerun was performed.

## Frozen mechanism

V25 is unchanged through layers 0..14. On mean-only layer 15, subtract exactly the frozen D3-squared Wick contribution after ordinary `PK1` evaluation:

```python
if last and mode == 1:
    pk1v = pk1v - (D3 * D3) * (WT[18] * (1.0 / 72.0))
```

No coefficient damping, alternate term, rank change, propagation change, teacher forcing, tuning, or sweep is authorized under E028.

## Measured terminal metrics

| metric | V25 baseline | E028 candidate |
|---|---:|---:|
| final MSE | `2.2904698131576138e-08` | `2.2860907641177464e-08` |
| billed FLOPs | `806303721965` | `806303726061` |
| residual | `0.1757223020002101 s` | `0.17592392699945947 s` |
| wall time | `30.347163784999992 s` | `30.525235822000013 s` |

Derived frozen metrics:

- MSE ratio: `0.9980881437446972`
- raw-MSE improvement: `0.19118562553027685%`
- raw-MSE delta: `-4.37904903986744e-11`
- FLOP delta: `+4096`
- projected utilization: `0.36666448186264516`
- projected adjusted score: `8.160985427370592e-09`
- residual delta: `+0.00020162499924936128 s`
- deterministic repeat max absolute difference: `0.0`
- baseline/candidate max absolute output difference: `8.296966552734375e-05`

## Frozen gate decision

All preregistered E028 gates passed:

1. MSE ratio `0.9980881437446972 <= 0.99919` — PASS.
2. projected adjusted `8.160985427370592e-09 < 8.17e-09` — PASS.
3. projected utilization `0.36666448186264516 <= 0.3666655` — PASS.
4. FLOP delta `4096 <= 1.0e7` — PASS.
5. residual delta `0.00020162499924936128 <= 0.005 s` and candidate residual `0.17592392699945947 < 0.400 s` — PASS.
6. finite outputs — PASS.
7. deterministic repeat diff `0.0` — PASS.
8. patch scope/provenance checks — PASS.

**Terminal local decision: GO.**

This is a bounded one-index local promotion only. It is not official-scorer evidence and does not supersede the E007 canonical result.

## Scorer-ready handoff

When and only when an official-scorer run is explicitly authorized:

1. start from the exact pinned V25 source/blob above;
2. apply `methods/e028_final_d3sq_prune.patch_v25_source` exactly once;
3. verify the resulting source contains only the frozen final-layer D3-squared subtraction above relative to pinned V25;
4. run the unchanged official Phase-2 scorer configuration used for the canonical comparison;
5. report raw final-layer MSE, adjusted score, all-layer MSE if emitted, billed FLOPs/utilization, residual failures, and failures/100;
6. promotion requires at minimum raw final MSE `<= 2.23e-08`, adjusted `< 8.17e-09`, and failures `0/100`; otherwise DROP without rescue under E028.

No official scorer, holdout, rerun, tuning, coefficient sweep, alternate diagram-term selection, or E026/E027 rescue is authorized by this handoff.
