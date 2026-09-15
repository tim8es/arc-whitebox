# E031 result — deterministic source-axis moment closure

Status: **DONE / NO-GO / DROP**

Idempotency key: `ARC-CONTINUE-LEAD-20260915`

## Provenance

- Branch: `research/e031-source-axis-moment-closure-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-first commit: `989031c8f78153498202b0413b55c220b12d10cf`
- RED tests commit: `41b89cf8f9a757549222091f2522b5bcd92a3e9b`
- RED workflow commit: `fc453b19d45c80723845ec8c75bec93c42bc4a20`
- Frozen algebra commit: `265bd1d90405074ac44d95bb6ba12ed23e404050`
- Diagnostic harness commit: `7b66adef4d82f29289be58e5e56adb5454e3ef6e`
- Single diagnostic launch commit: `d4a8988c3abfb2c29d137194bc28fc00d0fda03e`
- Workflow freeze commit: `fbd905d1deac34d278441afcfcf2ae090907ce20`
- Exact V25 blob: `195373a110215256b759d7c172ba8c923c62e5cc`

## TDD evidence

RED:

- run `35001019409`
- job `104489137370`
- expected failure: `ModuleNotFoundError: No module named 'methods.e031_source_axis_moment'`.

GREEN:

- run `35001139565`
- job `104489527220`
- `4 passed in 0.17s`.

## Single frozen local diagnostic

- run `35001458611`
- job `104490580689`
- public Phase-2 mini index `0` only
- focused tests in the scientific run: `4 passed in 0.17s`
- artifact `10409807652`, `e031-source-axis-result.zip`
- artifact zip SHA256 `3de843e7e247d9bd5e02a48fcb4edc0c269464c5c2554ce8c0ae52bba346a6f5`
- exact V25 trajectory remained unmodified; instrumentation only observed live A/P source-stack Gram statistics.

Measured source-axis degree-2 / rank-3 closure:

- D21-capable calls: `14`
- aggregate source-axis RMS loss: `0.7426063360381435`
- gate: `<=0.010` — **FAIL**
- worst-layer RMS loss: `0.879881863372162`
- gate: `<=0.022` — **FAIL**
- the basis is exact for `k<=3`, then loss jumps to `0.4922` at `k=4` and rises monotonically to `0.8799` at `k=14`.

Frozen optimistic compute path:

- V29/V25 anatomy total: `260.1 u`
- old tier removed at zero cost: floor `153.3 u = 0.14970703125 B`
- exact E021 dead-feedback saving credited: `935,657,472` FLOPs = `0.435699462890625 u`
- projected optimistic floor after that proven exact saving: `152.8643005371094 u = 0.14928154349327089 B`
- target: `<=0.14 B`
- additional exact saving still required from the non-old floor: `9.94 u`
- compute gate — **FAIL**.

E023 is explicitly not credited: although its intended terms were structural zeros, its frozen implementation changed floating reduction association and failed its exact-output gate, so it is a terminal DROP rather than a proven exact saving.

Finite/scope gates passed. Both scientific fidelity gates and the compute-path gate failed by large margins.

## Decision

**NO-GO / DROP E031.**

The source axis is not remotely degree-2/three-dimensional once four or more historical K3 sources are live, and even an impossible zero-cost deletion of the entire old tier plus the exact E021 saving remains above the required `0.14` utilization. A full estimator rewrite therefore has no preregistered path to the public-leader target.

No rescue with a larger source rank, alternate polynomial family, randomized source sketch, importance weighting, source dropping, HT, spatial sketch, Strassen/joiner retry, second mini index, or alternate cost credit is allowed under E031. Any such proposal is a new experiment.

No official scorer, holdout, tuning, sweep, or canonical mutation was performed.