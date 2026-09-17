# E100 Protocol — cross-fit two-subspace residual shrinkage

Idempotency key: `ARC-E100-CROSSFIT-TWO-SUBSPACE-SHRINKAGE-20260918`

Status: **PREREGISTERED / SYNTHETIC STAGE-A ONLY**.

## Provenance and independence

- Branch: `research/e100-crossfit-two-subspace-shrinkage-20260918`.
- Direct base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Deterministic base: `baselines/covariance_propagation.py@f547b378faa56e299559bcefc89909fd401b8026`.
- E095 is terminal and immutable. E100 is not a rank/sample/seed rescue of E095: E095 hard-projected the sampled residual into a rank-6 covariance eigenspace and zeroed the orthogonal component. E100 keeps both components and applies independently estimated soft shrinkage.
- E092 is a fitted cross-network residual calibrator. E100 fits no coefficient from targets or another network.
- E077 used an input-space Stein zero-mean control. E100 is finite-sample output-mean shrinkage and uses no Stein control function.
- No V29/K3/K4/source-state machinery is reused.

## Motivation from frozen E095 evidence

E095 measured, on its frozen synthetic corpus:

- covariance baseline MSE `1.9303277496159283e-03`;
- same-trajectory full-sample MSE `1.3024242688774502e-04`;
- mean rank-6 oracle residual-energy capture `0.8137756235978275`.

Hard projection failed because it discarded useful orthogonal sampled signal. A scalar additive-noise oracle using those aggregate baseline/noise scales would have

`a*=B/(B+V)=0.9367930156551441`

and oracle risk `B*V/(B+V)=1.2201019585041528e-04`, about `6.3207%` below the full-sample MSE. This is only a pre-code plausibility calculation, not E100 evidence.

## Frozen estimator

Run covariance propagation to obtain final mean `b` and final covariance `C`. Let `U` be the top `k=6` eigenvectors of `C`, with deterministic sign canonicalization. Define projectors implicitly:

`P r = U(U^T r)`, `Q r = r - P r`.

Generate one antithetic candidate stream of exactly `N=2048` final activations, organized into antithetic pairs. Split pairs deterministically by pair index parity into disjoint halves A and B; each half contains complete `x,-x` pairs.

For a half with `n=N/2` samples, mean `m), and centered samples `z_i=h_i-m`, define target-free mean-noise energy estimates

`tau_P = sum_i ||U^T z_i||^2 / (n(n-1))`

`tau_total = sum_i ||z_i||^2 / (n(n-1))`

`tau_Q = max(0, tau_total - tau_P)`.

For residual `r=m-b`, define

`e_P=||Pr||^2`, `e_Q=||Qr||^2`

and frozen positive-part shrink factors

`a_P = clip(1 - tau_P/max(e_P,1e-30), 0, 1)`

`a_Q = clip(1 - tau_Q/max(e_Q,1e-30), 0, 1)`.

Cross-fit them:

- coefficients from A are applied to `m_B-b`;
- coefficients from B are applied to `m_A-b`.

The final estimate is the average of the two cross-fitted corrected half-means:

`b + 0.5 * [aP_A P(m_B-b) + aQ_A Q(m_B-b) + aP_B P(m_A-b) + aQ_B Q(m_A-b)]`.

The ordinary full-sample mean from the same 2048 trajectories is the comparator.

No target/reference value participates in `U`, `tau`, shrink coefficients, or inference.

## Frozen Stage-A corpus

Synthetic only:

- width `32`
- depth `6`
- He Gaussian weights
- network seeds `100000..100007`
- reference antithetic samples `65536`
- candidate antithetic samples `2048`
- reference input seed `2_100_000 + network_seed`
- candidate input seed `3_100_000 + network_seed`
- subspace rank `6`
- NumPy PCG64
- float64 moment/sample arithmetic

No seed/rank/sample sweep.

## TDD

RED first: focused tests import absent `methods.e100_crossfit_shrinkage` and cover pair-preserving split, deterministic covariance subspace, noise-energy algebra, coefficient clipping, cross-fit identity limits, and deterministic sample stream.

GREEN: implement only the frozen helper algebra.

Scientific Stage-A runs exactly once after GREEN from a path-isolated workflow and writes one immutable JSON artifact.

## Frozen scientific gates

All must pass:

1. all outputs/coefficients finite;
2. deterministic replay max abs diff `==0`;
3. aggregate E100 MSE / covariance baseline MSE `<=0.20`;
4. aggregate E100 MSE / same-trajectory full-sample MSE `<=0.95`;
5. E100 beats the full-sample mean on at least `6/8` networks;
6. worst per-network E100/full-sample MSE ratio `<=1.25`;
7. all shrink coefficients lie in `[0,1]`;
8. at least one group coefficient is strictly below `0.99` on at least `4/8` networks, proving the mechanism is active rather than numerically equal to the full sample;
9. conservative Phase-2 utilization upper bound `<=0.12`.

Any failed gate => terminal **NO-GO / DROP E100**. No coefficient formula change, rank change, sample-count change, seed change, alternate split, clipping change, tuning, rescue, rerun, public diagnostic, or holdout/full/scorer.

## Conservative Phase-2 cost upper bound

At width `W=1024`, depth `D=16`, candidate samples `N=4096`, rank `k=6`, budget `B=2**41`:

- covariance: `5 D W^3`
- eigenspace/sign handling: `10 W^3 + 4 W^2`
- antithetic forward samples: `2 N D W^2 + 2 N D W`
- all split/group statistics and cross-fit projections: bounded by `8 N W k + 12 N W + 20 W k + 20 W`.

Total frozen upper bound: `234465931264` FLOPs, utilization `0.10662276111543179`.

## Promotion rule

Stage-A GO authorizes only a new Phase-2-shape local implementation/falsifier under a new successor ID. It does not authorize public/public-mini, official scorer, holdout/full, canonical mutation, ledger mutation, merge, or tuning.
