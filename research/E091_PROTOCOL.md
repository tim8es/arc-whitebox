# E091 — leakage-free leave-one-out ridge residual calibration readiness

Idempotency key: `ARC-E091-READINESS-20260916`

Status: **READINESS GO / PROTOCOL-ONLY**. No public run, scorer, holdout, tuning, sweep, or canonical mutation is authorized by this file.

## Provenance

- Branch: `research/e091-loo-ridge-readiness-20260916`
- Direct canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- E091 was unoccupied at readiness start: no E091 branch/issue/commit was found.
- This lane contains no scientific candidate implementation and reads no public/evaluation target.

## Frozen method class

E091 is restricted to a fixed, target-free feature map plus a linear ridge residual calibrator.

For calibration examples `i=1..N`:

- `b_i in R^q` is the frozen base-estimator prediction;
- `y_i in R^q` is a calibration target from an explicitly disjoint synthetic/reference corpus only;
- `z_i = y_i - b_i` is the residual target;
- `x_i in R^p` is computed only from the MLP/input and frozen base prediction/state, never from `y_i`, `z_i`, public targets, scorer outputs, or holdout results;
- `X` stacks `x_i^T`, `Z` stacks `z_i^T`;
- feature preprocessing and ridge `lambda > 0` are frozen before reading any calibration target;
- `p <= 16` is the hard readiness cap. No feature/rank/lambda sweep is allowed under E091.

The ridge matrix and fit are

`A = X^T X + lambda I_p`,

`B = A^{-1} X^T Z`,

with fitted calibration residuals `Zhat = X B`.

The deployable estimator, if a later protocol authorizes implementation, is `b(x) + x^T B_frozen`. It must not compute leave-one-out quantities at public/scorer inference time and must not read an evaluation target.

## Exact leave-one-out identity

Let row `i` be `x_i^T`, define

`h_i = x_i^T A^{-1} x_i`,

`zhat_i = x_i^T B`,

`e_i = z_i - zhat_i`.

Deleting row `i` gives

`A_{-i} = A - x_i x_i^T`,

`X_{-i}^T Z_{-i} = X^T Z - x_i z_i^T`.

By Sherman-Morrison, provided `1-h_i != 0`,

`A_{-i}^{-1} = A^{-1} + (A^{-1} x_i x_i^T A^{-1}) / (1-h_i)`.

Therefore the exact leave-one-out coefficient matrix is

`B_{-i} = B - (A^{-1} x_i e_i^T) / (1-h_i)`.

The exact leave-one-out fitted residual at the omitted point is

`zhat_i^{(-i)} = x_i^T B_{-i}`

`                 = zhat_i - h_i e_i / (1-h_i)`

`                 = (zhat_i - h_i z_i) / (1-h_i)`.

Equivalently the leave-one-out residual is the PRESS identity

`e_i^{(-i)} = z_i - zhat_i^{(-i)} = e_i / (1-h_i)`.

For the final prediction,

`yhat_i^{(-i)} = b_i + zhat_i^{(-i)}`.

### No-self-target-leakage identity

The same prediction can be written without `z_i` at all:

`zhat_i^{(-i)} = x_i^T (X_{-i}^T X_{-i} + lambda I)^{-1} X_{-i}^T Z_{-i}`.

Thus `d zhat_i^{(-i)} / d z_i = 0` exactly when `X`, preprocessing, and `lambda` are target-independent and frozen. The apparent `z_i` in the PRESS form cancels algebraically against the `z_i` contribution inside the full fit.

This identity is invalid for E091 if any of the following is target-dependent: feature selection, feature normalization, lambda choice, row weighting, model selection, early stopping, rank choice, or corpus membership.

## Target-leakage prohibition

E091 MUST NOT use any public-mini/evaluation/scorer target in fitting, feature selection, hyperparameter selection, normalization, stopping, or model choice.

Allowed calibration targets must come from a separately generated synthetic/reference corpus whose manifest/hash is frozen before any public diagnostic. Public/scorer inputs may be used only as unlabeled inference inputs after `B_frozen` exists.

A leave-one-out evaluation on a labeled corpus prevents self-target leakage for the omitted row, but it does **not** legalize training on benchmark evaluation labels. Therefore benchmark/public target labels are categorically excluded rather than merely leave-one-out excluded.

## Minimal bounded local falsifier already executed

A deterministic float64 synthetic problem with `N=7`, `p=3`, `q=4`, `lambda=1` was used. No repository/public/benchmark data was read.

Checks and observed values:

1. PRESS identity vs seven direct leave-one-out ridge refits:
   - max absolute difference: `2.220446049250313e-16`;
   - relative Frobenius difference: `2.7398555018662083e-16`.
2. Leverage safety:
   - `min(h_i)=0.17206119322816163`;
   - `max(h_i)=0.6129070762130224`;
   - `min(1-h_i)=0.38709292378697757`.
3. Self-target perturbation test: adding `[11,-7,5,13]` only to the omitted row target changed its LOO prediction by at most `2.2065682614424986e-15` (float64 roundoff).

Readiness gates for the algebraic falsifier are therefore PASS.

## Arithmetic readiness

For fixed `p <= 16`:

- calibration sufficient statistics: `O(N p^2 + N p q + p^3)` offline;
- all LOO leverages from one inverse/factorization: `O(N p^2)` offline;
- deploy-time correction: `O(p q)`.

At Phase-2 shape `q <= 16*1024 = 16384`, the dense multiply/add work for `p=16` is at most about `2*p*q = 524,288` scalar FLOPs per MLP before minor elementwise overhead, versus budget `2^41 = 2,199,023,255,552`; this is about `2.38e-7` of budget and cannot by itself threaten the `utilization <= 0.14` target.

Arithmetic readiness is PASS. Accuracy readiness is deliberately **unevaluated**: no public diagnostic is allowed in this readiness lane.

## Focused implementation test plan for a later authorized implementation

Before any public run, implementation must pass only synthetic/disjoint tests:

1. **Identity parity** — direct `N` leave-one-out refits vs PRESS formula, `max_abs <= 1e-12`, `rel_frob <= 1e-12` in float64.
2. **Self-target invariance** — perturb only `z_i`; `zhat_i^{(-i)}` must change by `<=1e-12` absolute.
3. **Feature purity** — feature builder API accepts only MLP/base-prediction/state objects; no target argument/path/environment variable exists.
4. **Frozen preprocessing** — preprocessing metadata and `lambda` are committed by hash before any calibration target is loaded.
5. **Corpus separation** — calibration manifest must be synthetic/reference-only and must reject public-mini/scorer/holdout identifiers.
6. **Leverage denominator** — require `min_i(1-h_i) >= 1e-6`; fail closed, no clipping/jitter/pseudoinverse rescue.
7. **Determinism** — repeated calibration from the same frozen manifest is bitwise-identical or, if the linear algebra backend is not bitwise deterministic, coefficient and prediction parity must be predeclared and <=`1e-12`; no seed sweep.
8. **Arithmetic audit** — `p <=16`; deploy correction bill must be recorded separately and remain negligible relative to `0.14 B`.
9. **No public test** — these tests must complete before any public-mini execution is proposed.

## Readiness decision

**READINESS GO / PROTOCOL-ONLY.** The exact LOO identity and the bounded synthetic falsifier pass, and a target-leakage-free execution path exists only if calibration labels are from a disjoint frozen synthetic/reference corpus. This is not a scientific GO and does not authorize a public run or scorer.