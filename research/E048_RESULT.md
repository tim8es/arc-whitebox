# E048 Result — terminal NO-GO / DROP

Branch: `research/e048-source-free-response-recurrence-20260916`
Canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`

## Protocol provenance

Protocol-only commit: `ba3282ac3da60ef7390705947f96f622c5f60e2c`.
Compare against canonical: ahead by exactly one commit; only `research/E048_PROTOCOL.md` added.

## Synthetic TDD evidence

Frozen test commit: `0aa10749a581382a3567193a0a68344ec18baaf0`.
Focused workflow commit: `3b93d9042d9de36d829e0f646bd75e7cc64d68a4`.

RED run/job: `35091923169` / `104780004734`.
Expected failure: `ModuleNotFoundError: No module named 'methods.e048_source_free_response_recurrence'`.

Synthetic implementation commit: `32ca0959618faae8c4e66f74ca8abf77ed0996b4`.
GREEN run/job: `35092071211` / `104780482850`.
Result: `6 passed in 0.26s`.

The focused tests enforce width 32, depth 8, zero bias, PCG64 seed 48048, float64; exact affine/angular claims; D21 relative-RMS gate; candidate-vs-K3+memK4 final-MSE gate; fixed-rank source-free state; deterministic output; and projected utilization gates.

## Frozen public mini0

Public runtime commit: `5e40ad5b95e2313f3ecc1187feb0e8bb72218578`.
Diagnostic script commit: `46a478a690f551236e1705d6de4f51424e03fbb0`.
One-shot workflow commit: `62c558e429408cbcee76a42f889ac1532d823dba`.

Run/job: `35092243375` / `104781043800`.
Artifact: `e048-public-mini0-log`, ID `10444921162`.
Artifact SHA256: `4f50bbef37a86710b8787b54ba71bab09cf2956f94ae0be1a19129696a5291c9`.

Observed terminal public result:

- `failures = 1`
- `local_go = false`
- error type: `SymmetryError`
- error: `Tensor not symmetric along axes (0, 1): max deviation = nan`
- preceding runtime warning: invalid value encountered in `arccos`
- public accuracy/utilization metrics are unevaluable because the frozen response recurrence became non-finite before completion.

Under the preregistered one-shot kill rule this is terminal `NO-GO / DROP`. The public failure may not be rescued by correlation clipping, damping, state clipping, alternate normalization, rerun, tuning, or topology change.

No holdout, full split, official scorer, tuning, sweep, rerun, rescue, canonical mutation, ledger mutation, or merge was performed.