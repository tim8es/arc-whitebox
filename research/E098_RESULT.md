# E098 result — terminal NO-GO / DROP

Idempotency key: `ARC-E098-LATE-K22-EDGEWORTH-20260918`

Branch: `research/e098-late-k22-edgeworth-response-20260918`

Canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`

Protocol commit: `e4c19feb3818f46228036760b7b035a0414d2089`

Implementation commit: `ad264dba3eadfafdc20c1e7800dd30365fc900c6`

Frozen workflow/arm commit: `ae510a0f626801606f5698393232b93e9a1d5661`

## Sole frozen Stage-A evidence

- run: `35286318728`
- job: `105419339739`
- workflow terminal: `failure` because frozen scientific gates failed
- artifact: `e098-stage-a`
- artifact ID: `10523249916`
- artifact ZIP SHA256: `0d74cedeb12f2420efddb8e0a451130c0bcc4f9cce4c06c7fd5277cfeaa24eaf`
- artifact size: `1932` bytes
- width/depth: `128/7`
- Monte-Carlo samples per network: `32768`
- rank: exactly `8`
- weight seeds: `98098, 98198`
- input seeds: `198098, 198198`
- evaluated late source layers: `3,4,5`
- no benchmark/public/scorer/holdout/full data and no target fitting.

## Frozen metrics

Representation/response preservation:

- median rank-8 K22 captured energy: `0.8236292789867994` — PASS vs `>=0.80`
- median rank-8 response-vs-full-K22 relative L2 error: `0.07095046559271997` — PASS vs `<=0.20`
- all six K22 observations finite and signal-eligible
- deterministic replay max abs scalar delta: `0.0`

Accuracy:

- aggregate Gaussian mean-closure MSE: `1.967596823118082e-05`
- aggregate full-K22 Edgeworth MSE: `2.1563156194261287e-05`
- aggregate rank-8 K22 Edgeworth MSE: `2.1944391748876592e-05`
- rank-8 / Gaussian aggregate ratio: `1.115289041486709` — FAIL vs `<=0.95`
- rank-8 improves Gaussian on only `1/6` transitions — FAIL vs `>=4/6`
- worst rank-8 / Gaussian ratio: `1.2153780139388275` — PASS vs `<=1.25`

Per-transition rank-8 / Gaussian ratios:

- network 0, 3->4: `1.0293920775566636`
- network 0, 4->5: `1.2153780139388275`
- network 0, 5->6: `1.2063847571392738`
- network 1, 3->4: `1.0803947874852344`
- network 1, 4->5: `1.1542153675778744`
- network 1, 5->6: `0.9985612814758977`

Cost:

- conservative per-layer late-K22 factor+response bound: `101,974,016` scalar FLOPs
- total for 12 remaining width-1024 layers: `1,223,688,192` FLOPs
- utilization fraction vs `2^41`: `0.0005564689636230469` — PASS vs `<0.01`

## Interpretation

The rank-8 representation premise is viable *late*: it preserves the full pair-K22 Edgeworth response well and is computationally cheap. The frozen response mechanism itself is not useful. Both full-K22 and rank-8 pair-cumulant Edgeworth corrections increase mean-closure error in aggregate; compression is not the cause.

Therefore the failure is scientific, not technical.

## Decision

**E098 = terminal NO-GO / DROP.**

No rank change, later birth layer, shrinkage/gain, alternate seeds/samples, alternate Edgeworth coefficient, second synthetic family, rerun, rescue, public diagnostic, holdout/full, scorer, merge, canonical mutation, or ledger mutation is allowed under E098.

A successor must use a materially different accuracy mechanism; it may treat E098 only as evidence that late K22 is compressible but the fixed pair-only first-order Edgeworth response has the wrong practical effect.
