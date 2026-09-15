# E022 — oversampled spectral shared-basis rebuild

Idempotency key: `ARC-E022-OVERSAMPLED-BASIS-20250915`

Status: frozen bounded local diagnostic only.

## Provenance

- Branch: `research/e022-oversampled-shared-basis-20250915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Scientific ancestor: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- Exact V25 blob: `estimators/estimator_v25.py` @ `195373a110215256b759d7c172ba8c923c62e5cc`
- Frozen comparator: E007 raw `2.23e-08`, adjusted `8.17e-09`, utilization `0.36666448`, failures `0/100`.

No E019/E020 branch or experiment ID may be touched. No canonical mutation is authorized.

## Mechanism

Change only the tier-1 V25 shared-basis rebuild used when one source crosses the age gate.

Frozen parameters:

- `R_OLD = 384`
- age gate unchanged from V25
- oversample `p = 16`
- `ell = R_OLD + p = 400`
- exactly one `G @ Omega` application
- no power iteration / second `G` pass
- no rank, age, seed, oversampling, or truncation sweep.

For the same weighted PSD leg Gram operator `G` used by V25, replace the one-pass rank-384 QR sketch with:

1. `Omega = w32[:, :400]` (same deterministic weight-slice sketch family as V25, widened only by the frozen 16 columns),
2. `Y = G @ Omega` using exactly one application of the existing factored Gram action,
3. `H = Y.T @ Y`,
4. eigendecompose symmetric `H`, select the top 384 eigenpairs in descending eigenvalue order,
5. construct `Q = Y @ V_r @ diag(lambda_r ** -1/2)`,
6. continue with the ordinary V25 shared-basis factor rotation, tier-2 logic, K3/K4 equations, and contractions unchanged.

The candidate may use only deterministic sign canonicalization needed to make the eigentruncation repeatable. It may not add clipping, jitter, alternate fallback bases, adaptive rank, or a second Gram pass.

## Diagnostic

Public Phase-2 mini only. No scorer.

- Smoke set: indices `0..3`.
- Validation set: indices `4..7` exactly once.
- Baselines on every index: exact/unconfined V25 path where available in the diagnostic harness and the frozen q1 shared-basis V25 comparator.
- Record final-layer MSE for q1 and E022, per-index ratios, aggregate validation ratio, deterministic repeat difference, measured FLOPs/residual-time proxy, and temporary/persistent memory accounting.
- At every tier-1 rebuild, construct an exact dense weighted Gram matrix only in the diagnostic harness and obtain its top-384 eigenspace as a teacher. This teacher is used solely for principal-subspace error measurement and never feeds estimator state.
- Principal-subspace error is the normalized Frobenius projector distance `||QQ^T-UU^T||_F / ||UU^T||_F`.

## Frozen gates

All gates must pass simultaneously:

1. Validation aggregate final-layer MSE ratio `E022/q1 <= 0.990`.
2. No validation dump has final-layer MSE ratio `> 1.02`.
3. Mean principal-subspace error on validation rebuilds improves by at least `20%` relative to q1, i.e. `err_E022 <= 0.80 * err_q1`.
4. Projected mean utilization `<= 0.3697`.
5. Projected adjusted score `<= 8.16e-09` and strictly `< 8.17e-09`, using canonical E007 raw multiplied by the measured validation raw-MSE ratio and projected utilization.
6. Candidate outputs and diagnostics are finite; repeated identical evaluation is deterministic.
7. No persistent-memory regression: post-rebuild stored basis remains exactly `n x 384`; oversampled `n x 400` and `400 x 400` objects are temporary only.
8. No residual-time regression: candidate whole-path residual proxy must not exceed q1 by more than measurement noise; frozen operational threshold is `candidate <= q1 + 0.005 s/MLP-equivalent`.
9. Exactly one weighted-Gram application per E022 tier-1 rebuild. Any observed second application is automatic FAIL.

Any failed gate => `NO-GO / DROP E022`. No rescue tuning, rerun on alternate indices, parameter sweep, q2 fallback, scorer, holdout, or protocol mutation.

## Execution budget

Focused tests plus one frozen local diagnostic only. No official scorer, no hidden/full holdout, no estimator submission, no canonical ledger edit.
