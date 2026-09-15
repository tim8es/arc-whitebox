# E021 — source-0 dead V18 feedback-lane elision

Idempotency key: `ARC-E021-DEAD-FEEDBACK-20250915`

## Base and scope

- Branch: `research/e021-dead-feedback-lane-20250915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Exact V25 ancestor: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- Exact V25 estimator blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- Public development data only: `aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`, MLP index 0 only.

No canonical mutation. No E019/E020 continuation. No official scorer, holdout, tuning, sweep, rank changes, source-lane changes, or arithmetic changes outside the source-0 V18 feedback transport lane.

## Hypothesis

In exact V25, source 0 is born through the no-prior-source branch where the V18 feedback factors are assigned exactly zero:

```python
F1_b = zeros((n, rfb))
F2_b = F1_b
R1T_b = F1_b
R2T_b = F1_b
```

The corresponding transported feedback block is `Ff_b=[F1_b|F2_b]`, shape `n×(2*R_FB)=n×32`. Because both its left and static right factors are exactly zero, its contribution to all later V18 feedback contractions is mathematically zero. Exact V25 nevertheless includes that source-0 block in the shared `Zf_st = WDb @ Zf_st` dense transport on each subsequent layer.

E021 removes only that source-0 `n×32` block from the dense transport. The source-0 slot remains exactly zero for alignment with `R1T_st/R2T_st`; source rows 1+ execute the unchanged V25 transport and all downstream arithmetic is unchanged.

For a 16-layer Phase-2 MLP, source 0 has 15 subsequent transports. The predicted gross saving is one `n×n @ n×32` transport per remaining layer, about `15 * 2*n^2*32` FLOPs at `n=1024`, before exact flopscope accounting.

## Frozen implementation

1. Add one helper implementing source-0-preserving-zero feedback transport:
   - input `WDb`, `Zf_st` with shape `(k,n,32)`;
   - row 0 is returned as an exact zero row without dense matmul;
   - rows 1+ are transported by the same `fnp.matmul(WDb, ...)` arithmetic as V25;
   - no other rows, ranks, operands, or operations change.
2. The diagnostic loads the exact V25 blob above and verifies the observed blob hash before execution.
3. Build a patched in-memory V25 variant by replacing only the shared `Zf_st` transport call with the E021 helper. No other source text may differ.
4. Run exact V25 and E021 on public mini MLP0 with the same deterministic setup/seed and budget.
5. Compare complete estimator outputs and flopscope billed FLOPs. Measure focused helper residual time separately with repeated deterministic local calls.

## Focused tests

RED before implementation. Tests must establish:

- source-0 row remains bit-exact zero;
- rows 1+ equal the original dense transport within exact floating-point equality for the same operation;
- deterministic repeated calls;
- the helper does not mutate inputs.

## Frozen gates

GO requires all gates:

1. Exact output max absolute error `<= 1e-7`.
2. Exact output relative Frobenius error `<= 1e-7`.
3. Measured billed saving `>= 8.0e8 FLOPs/MLP` on MLP0.
4. Projected utilization `<= 0.36630` using frozen E007 utilization `0.36666448` minus measured saving / `2**41`.
5. No residual/resource regression: focused helper median wall time must be no slower than the unelided dense transport path by more than 5 ms per MLP-equivalent and must not add persistent state beyond the existing source-0 zero slot.
6. Deterministic and finite.

Any failed gate => `NO-GO / DROP E021`. No rescue, tuning, sweep, source changes, rank changes, arithmetic changes, second diagnostic, holdout, or scorer.

If all gates pass, prepare scorer-ready protocol only; do not run the official scorer.
