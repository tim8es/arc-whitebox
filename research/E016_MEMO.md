# E016 research memo — diagonal-residual rank-1 K4 response

Idempotency key: `ARC-E016-RESEARCH-20260915`

Decision: **GO for one bounded development diagnostic only.** No official scorer, holdout, tuning sweep, estimator integration, canonical/ledger edit, or E012/E013/E014/E015 mutation is authorized by this memo.

## Frozen provenance and non-duplication

- Canonical base inspected for this memo: `research/bootstrap` at `52eacc67dcc9af4813136ff641ea9b71c36c626f`.
- Canonical frontier comparator: E007, raw final-layer MSE `2.23e-08`, mean billed utilization `0.36666448`, adjusted final-layer score `8.17e-09`, failures `0/100`.
- Exact scientific ancestor: upstream V25, `504aldo/whest-p2-cumulant-k3` commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, V25 estimator blob `195373a110215256b759d7c172ba8c923c62e5cc`.
- E012 is scheduling-only pair batching; E013 rewrites the scalar adaptive-lambda sufficient statistic without changing the estimator; E014 is the E012 schedule plus one level-1 Strassen joiner; E015 is rank-3 MZ/Prony old-source memory. E016 uses none of those mechanisms.
- E016 does **not** alter K3 source ranks, old-source bases, scheduling, Strassen depth, scalar-lambda law, explicit old-source history, covariance path, final trim, sampling, or scorer policy.

## Mechanism

V25/V29 regenerates the off-diagonal fourth-cumulant core with one spatial mode,

`G_off ~= lambda_l * C_off`,

while keeping the K4 diagonal `dG` explicitly. Upstream F68 measured that this one-mode closure carries most, but not all, of the dense augmented-K4 signal: `C_off` alone gave a projected-chain final MSE around `2.230e-08`, while a larger nine-mode oracle basis reached about `2.205e-08` (about 1.1% lower raw error). Upstream F75 then found that across MLPs the scalar lambda deviation is strongly controlled by `mean(dG)/mean(var)`, but adapting only that scalar buys about 0.3–1.0% and is not the raw bottleneck.

E016 tests whether the *within-MLP neuronwise residual* of the same sufficient statistic carries the missing fourth-order spatial mode.

For each pre-activation layer define

`rho_l = mean(dG_l) / mean(var_l)`

and a centered neuronwise fourth-order residual

`q_l = (dG_l - rho_l * var_l) / sqrt(mean(var_l**2))`.

`q_l` has the units of a covariance entry and zero mean by construction. The candidate closure is

`G_off^E016 = lambda_l * C_off + gamma_l * offdiag(q_l q_l^T)`.

The diagonal remains the exact transported `dG_l`; only the off-diagonal K4 regeneration changes. `lambda_l` is the frozen V25 law and is not refit or modified under E016.

The new term is rank one. Under a dense linear transport it remains rank one: `(W q)(W q)^T`. In K4->K3 feed contractions it can be represented by vector matvecs plus a rank-1/thin leg rather than a dense n^3 matrix product. Therefore the proposed scientific content is new while its intended production cost is O(n^2) per active layer.

## Exact target

Primary scientific target: recover enough of the missing finite-width fourth-cumulant structure to lower raw final-layer MSE while adding at most a negligible fraction of one Phase-2 budget.

The score path is numerical, not qualitative. With projected utilization capped at `0.36866448` (E007 plus at most `0.002` absolute), beating E007 requires

`raw_MSE < 8.17e-09 / 0.36866448 ~= 2.216e-08`.

Relative to E007 raw `2.23e-08`, that is only about a `0.6%` raw reduction. The upstream F68 one-mode-to-nine-mode oracle gap is about `1.1%`, so a single targeted mode can plausibly clear the score threshold if it captures more than roughly half of that residual at O(n^2) cost.

This is intentionally a narrow target. E016 is not preregistered as a route to the ~1.7x cost jump identified by F86/F88; it is a low-cost raw-MSE lever that could beat the canonical E007 adjusted score without touching E014.

## Minimal diagnostic

Development data only; no official scorer.

1. Use public Phase-2 mini dumps/indices `0..7` and the exact dense augmented-K4 teacher instrumentation already used for the upstream F68 projection analysis.
2. Fit set: dumps `0,1,2,3`. Validation set: dumps `4,5,6,7`.
3. Layers scored: `8..14` inclusive.
4. Keep the existing V25 `lambda_l` law frozen.
5. On fit dumps, compute the exact dense teacher `G_off`, baseline residual `R_l = G_off - lambda_l C_off`, and the single candidate basis matrix `B_l = offdiag(q_l q_l^T)`.
6. Fit exactly one shared scalar `gamma_l` per layer by Frobenius least squares over dumps 0..3. No per-MLP coefficient, no alternate feature, no regularizer, no rank sweep.
7. Freeze the seven `gamma_l` values. On dumps 4..7 evaluate both:
   - direct K4-core relative RMS versus the exact dense teacher;
   - one lean end-to-end V25-style development trajectory in which only the new rank-1 K4 mode is added, using precise public development final means already permitted by the project protocol.
8. Meter the rank-1 production algebra separately at n=1024 and project the total billed utilization. Do not run `whest run` or any official scorer.

## Preregistered GO gates

All gates must pass simultaneously:

1. **K4 structural gain:** on validation dumps 4..7, layers 8..14, the mean Frobenius relative-RMS error of `G_off^E016` must be at least `20%` lower than the frozen one-mode `lambda C_off` closure; worst validation layer may not regress by more than `5%` relative to that baseline.
2. **End-to-end raw gain:** validation final-layer MSE of the lean candidate must be `<= 0.99 x` the frozen V25-style validation baseline on the same dumps. This 1% gate exceeds the approximately 0.6% raw gain needed to beat E007 at the maximum allowed overhead.
3. **Projected adjusted-score path:** using the measured validation raw-MSE ratio applied to canonical E007 raw `2.23e-08`, and the metered projected utilization, the projected adjusted score must be strictly `< 8.17e-09`.
4. **Compute:** projected total utilization must be `<= 0.36866448` (no more than `+0.002` absolute versus E007).
5. **Representation:** exactly one new rank-1 K4 response mode; seven frozen layer scalars `gamma_8..gamma_14`; no per-MLP, per-neuron fitted coefficients and no modification of lambda.
6. **Determinism/finite:** repeated evaluation with identical inputs is bit-identical at the coefficient/closure level; all coefficients and outputs finite.
7. **Resource/residual:** persistent extra state is at most two n-vectors plus one existing thin-leg slot; no material residual-time regression in the focused n=1024 proxy (candidate median <= baseline + 5 ms per MLP-equivalent projected total).

## Kill rule

Any failed GO gate => **NO-GO / DROP E016**. Do not respond by changing the feature definition, adding a second response mode, fitting per-MLP gamma, changing the layer window, refitting lambda, increasing K3 ranks, running a gamma/rank grid, using teacher forcing on validation, or launching the official scorer under E016.

If all gates pass, the only allowed next artifact is a scorer-ready handoff freezing the exact gamma table, algebraic fold into the existing K4 feed/use path, projected utilization, tests, and a separate official-run gate. The scorer still requires separate authorization.

## Budget

- External cost: `$0`.
- One read-only/project-source research pass and one future bounded local diagnostic only.
- Public development dumps 0..7 only.
- No holdout.
- No official scorer.
- No parameter sweep.
- No canonical/ledger mutation in this phase.

## Why this is numerically credible

Upstream experimental evidence establishes three useful facts.

1. F68: the fourth-cumulant gain is real and its off-diagonal core is dominated by covariance response, but `C_off` is not a mathematically exact basis; the measured one-mode versus nine-mode projected-chain gap is about 1.1% raw.
2. F75: `dG/var` is the strongest observed sufficient statistic for cross-MLP lambda deviations, with pooled correlations around 0.89 and residual scalar spread around 1–2%, while scalar adaptation itself is too small to solve the remaining error. E016 uses the same observable at neuron resolution rather than changing the scalar lambda.
3. F86/F88: n^2 closure work is only a few percent of the bill and the current K3 representation is cost-bound elsewhere. Therefore a rank-1 K4 mode can afford a small O(n^2) overhead; it does not need to solve the 107-unit old-tier problem to beat E007.

The hypothesis is therefore falsifiable with a cheap diagnostic and has a concrete score inequality before any scorer use.

## Primary-source citations

Finite-width/non-Gaussian motivation:

- Joseph M. Antognini, **Finite size corrections for neural network Gaussian processes**, arXiv:1908.10030. Shows that the leading finite-width departure from the Gaussian limit is a fourth-Hermite / fourth-cumulant correction with scale O(1/n): https://arxiv.org/abs/1908.10030
- Sho Yaida, **Non-Gaussian processes and neural networks at finite widths**, arXiv:1910.00019. Develops layer-by-layer propagation of finite-width non-Gaussian corrections rather than a purely Gaussian closure: https://arxiv.org/abs/1910.00019
- Boris Hanin, **Random Fully Connected Neural Networks as Perturbatively Solvable Hierarchies**, arXiv:2204.01058. Establishes a cumulant hierarchy in which higher cumulants propagate from lower/equal orders and whose importance grows with depth/width ratio: https://arxiv.org/abs/2204.01058
- Lucia Celli, **Optimal Non-Asymptotic Edgeworth Expansions for Multivariate Neural Network Outputs**, arXiv:2605.24072. Gives finite-width multivariate Edgeworth expansions with higher-order cumulants as explicit corrections to the Gaussian limit: https://arxiv.org/abs/2605.24072

Primary project evidence:

- Upstream F68/F75/F86/F88 in `504aldo/whest-p2-cumulant-k3`, commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, `docs/findings_log.md`.
- Exact V29/V25 implementation provenance in the same commit under `estimators/estimator_v29.py` and `estimators/estimator_v25.py`.
- Canonical ARC ledger: `tim8es/arc-whitebox`, `research/bootstrap` at `52eacc67dcc9af4813136ff641ea9b71c36c626f`, `research/ledger.csv`.
