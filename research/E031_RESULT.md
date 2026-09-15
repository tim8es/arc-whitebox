# E031 terminal result — NO-GO / DROP

Idempotency key: `ARC-E031-K22-MEMORY-20260915`

## Frozen provenance

- Branch: `research/e031-k22-memory-preflight-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Pinned upstream: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- Pinned V25 blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- Protocol-first commit: `d820b3643c89d648b2ea9d8d0c7f281d03f6b272`
- Pre-data protocol clarification: `aa960063ef448e33e4e39ab4277c084f1f183d77`
- RED run/job: `35007979364` / `104512449097`
- GREEN run/job: `35008081629` / `104512795759`
- Frozen diagnostic commit: `3de497154b8aec5d269015149f49c3b0487b2aa9`
- Frozen diagnostic run/job: `35008254335` / `104513385285`
- Artifact: `10412856254`
- Artifact zip SHA256: `617161d80624d90cd7729d0540bbcb1f5ead3410b85662895edb7f83734789a4`
- Public mini index: `0` only

## TDD / scope

RED failed as preregistered because `methods.e031_k22_memory` did not yet exist (`ModuleNotFoundError`). GREEN completed successfully; frozen scientific run reported `3 passed in 0.17s` before the diagnostic.

The diagnostic performed exactly one pinned-V25 baseline prediction and one instrumented pinned-V25 prediction. The instrumentation only appended `(layer, K22, g_prev)` debug state after ordinary V25 K22/g_prev construction. No official scorer, holdout, rank sweep, alternate normalization, tuning, second MLP, or repeat prediction was run.

## Aggregate frozen metrics

- captured non-final layers: `15`
- prediction parity max abs: `0.0`
- median residual materiality `||R22||F / ||K22||F`: `0.9949454224624901`
- median rank-8 retained Frobenius energy: `0.5291800294236713`
- median transported relative error after `W^2 R W^2^T`: `0.004183010490728895`
- worst transported relative error: `0.023679359966096002`
- finite: `true`
- algebra deterministic from captured state: `true`

The residual geometry is therefore highly material, but it is not intrinsically rank 8 under the frozen residual-energy criterion. Its transported action is much easier to approximate than the residual matrix itself, but E031 preregistered both criteria and forbids rescue/redefinition after measurement.

## Frozen gates

1. pinned blob exact — PASS.
2. instrumented prediction parity `0.0` — PASS.
3. median materiality `0.9949454 >= 0.05` — PASS.
4. median rank-8 retained energy `0.5291800 >= 0.90` — **FAIL**.
5. transported error median `0.0041830 <= 0.05`, worst `0.0236794 <= 0.12` — PASS.
6. finite and deterministic — PASS.

**Decision: NO-GO / DROP E031.**

No rank increase, alternate residual definition, alternate normalization, or rerun is permitted under E031. The observed low error after exact pair-diagonal transport may motivate a separately preregistered future mechanism, but it is not used to rescue E031.

The branch workflow was sealed after terminal measurement at commit `5b4b4fea5966df22b64831c23c21f7da119486cb`; subsequent branch pushes run focused tests only and cannot rerun the E031 scientific diagnostic.
