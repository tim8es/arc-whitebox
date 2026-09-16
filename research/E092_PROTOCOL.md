# E092 — frozen target-free residual ridge calibrator

Idempotency key: `ARC-E092-FROZEN-RESIDUAL-CALIBRATOR-20260917`

Status: **PREREGISTERED / PROTOCOL-ONLY**.

## Provenance and scope

- Branch: `research/e092-frozen-loo-residual-calibrator-20260917`.
- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Readiness precursor only: E091 protocol `ceb7d53fbed3a0c5366fed0da878a8d6b11b8055` and receipt `203e154cbb75d9e7d071df48b507a0def18408ac` established leakage-free fixed-lambda ridge algebra; E091 supplies no accuracy evidence and is not inherited as scientific GO.
- Base predictor for this lane: pinned canonical `baselines/covariance_propagation.py` blob `f547b378faa56e299559bcefc89909fd401b8026`.
- No public-mini, scorer, holdout or full-split target may be read by E092.

## Independent mechanism

E092 tests a **post-hoc, target-free feature residual calibrator** over the covariance baseline. It is not a V29 reproduction/rescue, old-tier rank/age change, float64 stabilization, K3/K4 transport lane, harmonic correction, connected-diagram DP, source cubature, FWHT transport, or any closed E045–E090 mechanism.

For each final-layer neuron `j`, let `b_j` be the frozen covariance-baseline prediction, `u` the previous-layer baseline mean vector, and `w_j` the incoming final-layer weight column. Define the fixed eight-dimensional feature vector:

1. `1`;
2. `b_j / rms(b)`;
3. `(b_j / rms(b))^2`;
4. signed weight skew proxy `sum(w_j^3)/(sum(w_j^2)^(3/2)+eps)`;
5. weight concentration `sum(w_j^4)/(sum(w_j^2)^2+eps)`;
6. normalized first projection `(w_j·u)/(||w_j||*||u||+eps)`;
7. normalized energy projection `(w_j^2·u^2)/(sum(w_j^2)*mean(u^2)+eps) - 1`;
8. interaction `(b_j/rms(b))*signed_skew`.

`eps = 1e-12`. Feature dimension is frozen at `p=8`. No feature selection or feature sweep is permitted.

Residual targets are normalized by the final-layer baseline RMS. Ridge lambda is frozen at `lambda=1e-2`. Feature normalization uses training-feature means/scales only and is target-independent. Intercept feature is not centered or scaled.

## Frozen synthetic/reference corpus

Scientific Stage-A uses only synthetic MLPs generated from fixed seeds and exact declared distribution:

- width `8`, depth `4`;
- each weight entry iid `N(0, 1/width)`;
- training MLP seeds: `92000..92015` (16 networks);
- held-out MLP seeds: `92100..92107` (8 networks);
- reference-input seed for network seed `s`: `1_000_000 + s`;
- antithetic standard-normal input pairs;
- `32768` total input samples per MLP (16384 iid positive draws plus their negatives);
- reference means computed in float64.

Corpus membership, seeds, architecture, sample count, feature map, normalization and lambda are frozen before any reference target is computed.

## TDD / execution stages

### RED engineering check

Before implementation, focused tests must be committed while `methods.e092_frozen_residual_calibrator` does not exist. A dedicated CI workflow may run once and must fail for that missing module. This RED run is an engineering/TDD receipt only, not the scientific Stage-A falsifier.

### GREEN engineering check

After RED, add the minimal implementation. The same focused tests must pass. Engineering tests cover feature determinism/shape/finite values, ridge direct-vs-closed-form behavior, self-target separation API constraints and deterministic synthetic generator/reference behavior.

### Scientific Stage-A — exactly one bounded synthetic falsifier

Only after GREEN, run one deterministic Stage-A command over the frozen training + held-out corpus. It must write one machine-readable receipt artifact containing coefficients, preprocessing statistics, baseline/adjusted MSE, per-network MSEs, determinism checks and FLOP estimate.

No Stage-A rerun/rescue is allowed. Any Stage-A workflow failure or gate failure is terminal E092 `NO-GO / DROP`.

## Frozen scientific gates

All must pass:

- all outputs and coefficients finite;
- repeated feature/calibration computation is deterministic (`max_abs_diff == 0` in the same environment);
- held-out aggregate final-layer MSE ratio `adjusted_mse / baseline_mse <= 0.95`;
- at least `6/8` held-out networks have adjusted MSE strictly below baseline MSE;
- maximum held-out network degradation ratio `adjusted_mse_i / baseline_mse_i <= 1.25`;
- ridge coefficient L2 norm `<= 5.0` after normalized-target fit;
- no reference/target information enters feature extraction or inference;
- all-in deploy correction FLOP fraction remains `< 1e-5` of `B=2**41` for Phase-2 width 1024.

The 5% aggregate improvement gate is deliberately material: small Monte-Carlo noise-level wins do not justify promotion.

## FLOP accounting

At Phase-2 width `W=1024`, final-layer E092 deploy overhead is billed in addition to the covariance baseline:

- `rms(b)`: square `W`, reduction `W-1`, divide/sqrt <= `2W+4` scalar FLOPs;
- per-column moments across the final `W x W` weight matrix: powers/products/reductions for second/third/fourth moments <= `8W^2` FLOPs;
- `w·u`, norms and energy projection <= `8W^2 + 8W` FLOPs;
- feature assembly/interactions <= `16W` FLOPs;
- standardized dense ridge correction with `p=8`: <= `2pW + 4p + 4W` FLOPs.

Frozen conservative upper bound: `17W^2 + 64W + 64`. At `W=1024`, this is `17,891,392` FLOPs, fraction `8.136e-6` of `2**41`, below the `1e-5` gate. Offline synthetic reference generation/training is research cost and is never executed by the submission estimator; it is nevertheless fully specified above for reproducibility.

## Terminal rule and promotion

- Any RED/implementation mismatch must be corrected before scientific Stage-A without changing the protocol, corpus, features, lambda or gates.
- Any scientific Stage-A failure/gate miss => terminal `NO-GO / DROP`; no parameter/feature/lambda/sample-count/seed rescue or rerun.
- Stage-A GO does **not** authorize public/scorer access. It only permits a separate successor lane to freeze the resulting coefficients and test architecture-transfer/generalization under a new preregistered non-public protocol.
- No canonical or `research/ledger.csv` mutation, merge, scorer, public-mini, holdout/full, tuning, sweep, rescue or rerun is authorized by E092.
