# E034 result — signed rank-4 global K3 response carrier

Status: **DONE / NO-GO / DROP**

Idempotency key: `ARC-FOLLOW-RESEARCH-20260915`

## Provenance

- Branch: `research/e034-signed-k3-response-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-first HEAD family: `c761f2bf254bf4040e277ed2ee3dd49aca19f416`
- Frozen scientific commit: `cf8ef2949e6d080115f4f118973385e26740ae46`
- Public Phase-2 mini index: `0` only
- Scientific workflow run: `35003483612`
- Job: `104497349620`
- Artifact: `10410960615`
- Artifact zip SHA256: `22fd2f485b12fda44ba822b24c83942924175ad38c60a265a0348323c0070b3c`

## TDD evidence

- Initial RED: run `35002820811` before implementation.
- Initial GREEN: run `35003096426`, job `104496051366`.
- Protocol-invariant RED: run `35003223048`, job `104496477517`; exactly the zero-birth sign test failed because `sign(0)=0` violated the frozen ±1 signed-state invariant (`1 failed, 5 passed`).
- Minimal invariant fix: commit `dde2af6b7d12bc98519c9627c952dbb96ef1bc54`.
- Final pre-science GREEN: run `35003350938`, job `104496906408`.
- Frozen scientific run focused tests: `6 passed in 1.55s`.

No scientific data were measured before the final focused GREEN.

## Frozen local diagnostic

Single allowed public-mini index-0 measurement:

- final-layer MSE: `0.0002431378853033713`
- billed FLOPs: `788760402`
- utilization: `0.0003586867032936425`
- adjusted proxy: `2.431378853033713e-05`
- residual wall: `0.02700914400006127 s`
- wall time: `1.0279476620000025 s`
- maximum absolute standardized skew: `0.01910919068543831`
- deterministic repeat max abs difference: `0.0`
- selected newborn indices: `[0, 1016, 852, 393, 298, 401, 911, 230, 458, 286, 73, 546, 880, 1015, 972, 176]`
- repeat selected indices: identical
- finite: `true`
- frozen scope check: `true`

## Gates

PASS:

- utilization `<=0.14`
- residual `<0.400 s`
- finite
- deterministic repeat
- exact frozen rank-4 / FIFO / selector scope

FAIL:

- raw final MSE `<=1.89e-08`: observed `2.431378853033713e-04`
- adjusted proxy `<2.5e-09`: observed `2.431378853033713e-05`

The raw error is about `1.29e4` times the target MSE. The signed global K3 response state is materially better than the O(1)-error coordinate-only closures, but omitting cross-neuron covariance remains fatal at the required precision.

## Decision

**NO-GO / DROP E034.**

No rank/FIFO/selector increase, alternate leverage score, covariance add-back, K4 add-back, clipping/damping, second mini index, rerun, official scorer, tuning, sweep, or rescue is allowed under E034. A covariance-retaining response method is a distinct E035+ experiment.

Canonical was not changed and no official scorer was launched.
