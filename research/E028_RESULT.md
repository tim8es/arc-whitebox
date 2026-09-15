# E028 terminal result — local GO evidence / promotion blocked

Idempotency key: `ARC-E028-TERMINAL-20250915`

## Frozen provenance

- Branch: `research/e028-final-d3sq-prune-20250915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Frozen diagnostic commit: `8f4e380e83109a85f840561b54f0bfe3b4907046`
- Pinned upstream: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- Pinned `estimator_v25.py` blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- Authoritative frozen diagnostic run: `34984554189`
- Authoritative frozen diagnostic job: `104433192579`
- Public Phase-2 mini index: `0` only

The authoritative frozen diagnostic completed successfully and produced the measurements below.

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

All preregistered E028 scientific gates passed on the authoritative frozen run:

1. MSE ratio `0.9980881437446972 <= 0.99919` — PASS.
2. projected adjusted `8.160985427370592e-09 < 8.17e-09` — PASS.
3. projected utilization `0.36666448186264516 <= 0.3666655` — PASS.
4. FLOP delta `4096 <= 1.0e7` — PASS.
5. residual delta `0.00020162499924936128 <= 0.005 s` and candidate residual `0.17592392699945947 < 0.400 s` — PASS.
6. finite outputs — PASS.
7. deterministic repeat diff `0.0` — PASS.
8. patch scope/provenance checks — PASS.

**Scientific local decision on the frozen run: GO.**

This is a bounded one-index local result only. It is not official-scorer evidence and does not supersede the E007 canonical result.

## Independent-review protocol finding

During PR #30 review, Codex identified that the branch-specific workflow remained armed after the frozen result. A later lint-only push (`d9830c75da4d6b76044db2f46f81852fe4ee821b`) therefore triggered E028 workflow run `35001635266` after the authoritative frozen run. That is an unintended post-result diagnostic rerun and violates the preregistered exactly-once/no-rerun rule.

This review finding does **not** change the numerical measurements of authoritative run `34984554189`, but it invalidates the previous claim that no rerun occurred and blocks promotion under the frozen E028 protocol. The unintended run is not used to select, tune, validate, or replace any metric above.

The workflow was subsequently sealed at commit `26c964bb26d70e5e8dca833d392fed5256a67cc0`. Verification run `35006895057`, job `104508806452`, contains only `Focused E028 tests only` and `Frozen E028 diagnostic is sealed`; both completed successfully. Generic PR CI run `35006899868` also completed successfully.

**Promotion status: BLOCKED by protocol violation. No official scorer is authorized for E028.**

Do not rerun, tune, rescue, or reinterpret E028. Any further scientific mechanism requires a new experiment lane and protocol.

No official scorer, holdout, coefficient sweep, alternate diagram-term selection, E026/E027 rescue, or canonical mutation was performed.
