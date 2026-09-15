# E031 — memoryful K22 residual carrier preflight

Idempotency key: `ARC-E031-K22-MEMORY-20260915`

Status: preregistered; protocol-only first commit.

## Provenance

- Branch: `research/e031-k22-memory-preflight-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Pinned upstream: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- Pinned `estimator_v25.py` git blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- Public Phase-2 mini diagnostic index: `0` only
- No official scorer, holdout, sweep, tuning, or canonical mutation.

E029 signed/angular cubature and E030 rank-8 conditional-Gaussian carrier are terminal NO-GO and are not reused.

## Hypothesis

V25 computes the post-ReLU pairwise fourth-cumulant slice `K22` at every non-final layer. Its memoryless K4 closure then discards the matrix geometry and retains principally the row-sum contribution inside `g_prev`, rebuilding the next preactivation pair slice from the memoryless core.

E031 tests one representation claim before any estimator implementation: the part of post-ReLU `K22` not represented by V25's rank-2 memoryless pair-slice ansatz is both material and approximately rank 8 under the exact pair-diagonal linear transport `(W**2) R (W**2)^T`.

If true, one persistent rank-8 matrix carrier can preserve missing K4 structure in `O(n^2 r)` per layer without a per-source K4 tensor. If false, close the lane without building a cosmetic final-layer correction.

## Frozen residual definition

After V25 forms post-ReLU `K22` and `g_prev` at layer `l`, define

`K22_ml[i,j] = (METRIC_C / 6) * (g_prev[i] + g_prev[j])`, with diagonal set to zero.

Define `R22 = K22 - K22_ml`.

No fitted coefficient, centering, row-sum projection, damping, clipping, alternate normalization, or layer-dependent rule is allowed.

## Frozen rank-8 representation diagnostic

For each non-final layer with a following weight matrix, compute the exact best rank-8 Frobenius approximation of `R22` by SVD in the diagnostic only. The SVD is oracle/preflight measurement, not a proposed runtime operation.

Using the next linear map `W = weight[l+1].T`, set `W2 = W * W` and compare:

- exact pair-diagonal transport: `T = W2 @ R22 @ W2.T`
- rank-8 transport: `T8 = W2 @ R22_rank8 @ W2.T`.

Record per layer:

- `||R22||F / max(||K22||F, eps)`;
- rank-8 retained Frobenius energy of `R22`;
- relative transported error `||T-T8||F / max(||T||F, eps)`.

The diagnostic must verify the patched V25 prediction is bit-identical to uninstrumented V25. Instrumentation may only append debug snapshots after `K22` and `g_prev` are computed.

## Focused tests

Before scientific data:

1. best-rank reconstruction is exact on a synthetic rank-8 matrix;
2. transport error is zero when the input residual has rank <=8;
3. source patch inserts exactly one debug append and otherwise restores byte-for-byte to pinned V25 when removed;
4. rank is frozen at 8 and no fitted coefficient/stabilization branch exists.

## Exactly one bounded scientific diagnostic

Run public mini index `0` exactly once. A deterministic algebra repeat may operate on already-captured matrices without re-running the estimator; no second prediction is allowed.

## Frozen GO gates

All must pass:

1. pinned V25 blob matches exactly;
2. instrumented prediction max absolute difference vs baseline V25 is `0.0`;
3. residual K22 content is material: median `||R22||F / ||K22||F >= 0.05`;
4. rank-8 residual energy retained: median `>= 0.90`;
5. transported rank-8 error: median `<= 0.05` and worst `<= 0.12`;
6. all metrics finite and deterministic from captured state.

GO only means a full carrier implementation is justified. It does not authorize a scorer and does not claim the competition target has been met.

Any failed or unevaluable gate => **NO-GO / DROP E031**. No rank sweep, alternate rank, normalization rescue, or second MLP under E031.

## Competitive relevance

Any subsequent implementation must still demonstrate a path to utilization `<=0.14` and raw MSE `<=1.89e-08`, targeting adjusted `<2.5e-09`. E031 is deliberately a representation preflight so an unsupported K4-memory implementation does not consume another scorer cycle.
