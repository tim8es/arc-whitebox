# E039 protocol — two-component half-space Gaussian location mixture

Idempotency key: `ARC-RESOLVE-E038-E039-OWNER-20260915`

Status: **PREREGISTERED / NOT YET RUN**

## Provenance and firewall

- Branch: `research/e039-halfspace-gaussian-mixture-20260915`.
- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- This is a fresh re-key of the independent half-space hypothesis only. It inherits no commits, tests, implementation, measurements, workflow state, artifacts, or code from either E038 branch.
- Authoritative E038 is `research/e038-conditional-gaussian-cov-20260915`; E039 must never share its files, implementation, workflow, diagnostic evidence, or experiment state.
- Public Phase-2 mini index **0 only** is permitted for the single frozen scientific diagnostic after focused GREEN.
- No official scorer, holdout/full split, second mini index, fitting, tuning, sweep, adaptive search, canonical mutation, or ledger mutation is authorized under E039.

## Hypothesis

A fixed two-component location mixture may preserve a dominant non-Gaussian dependence direction more faithfully than single-Gaussian or low-rank cumulant closures while retaining full second-order covariance information at acceptable cost.

E039 freezes a symmetric two-component Gaussian location mixture defined by an exact half-space split of the standard Gaussian input along one deterministic direction. The two component means are propagated separately while a single shared full covariance is propagated for both components.

## Frozen mechanism

Input width is `n=1024`.

1. Frozen split direction is exactly `u = ones(n) / sqrt(n)`.
2. Initial component weights are exactly `0.5` and `0.5`.
3. For `X ~ N(0, I)` split on the sign of `u^T X`, use the exact conditional first moments:
   - `m_plus = sqrt(2/pi) * u`;
   - `m_minus = -m_plus`.
4. The shared within-component covariance is the exact half-space conditional covariance:
   - `C_shared = I - (2/pi) * u u^T`.
5. The mixture must reconstruct the original first two moments before any network layer:
   - weighted mean exactly zero within tolerance;
   - `C_shared + m_plus m_plus^T = I` within tolerance.
6. For each dense linear layer `W`, propagate both means separately: `m_k_pre = W @ m_k`.
7. Propagate the single shared covariance exactly once: `C_pre = W @ C_shared @ W.T`.
8. For each component, compute Gaussian ReLU marginal means/variances from its own preactivation mean and the common diagonal variance.
9. Cross-neuron within-component covariance uses the fixed first Gaussian response only: `C_k_post_ij = Phi(alpha_k_i) Phi(alpha_k_j) C_pre_ij`, with exact diagonal overwrite to that component's Gaussian ReLU marginal variance.
10. The next shared covariance is exactly the arithmetic mean `0.5 * C_plus_post + 0.5 * C_minus_post`.
11. Component means remain separate across all layers; component weights remain fixed at `0.5/0.5`.
12. Final prediction at each layer is exactly the component-weighted mean `0.5*m_plus + 0.5*m_minus`.

No K3/K4 state, source stack, D21 tensor, output-Hessian term, scale mixture, component-weight adaptation, split-direction adaptation, extra components, fitted coefficient, clipping, damping, sampling, or post-hoc calibration is permitted.

## Focused pre-science tests

Before any public-mini access, focused RED/GREEN tests must establish:

1. exact frozen all-ones direction and `0.5/0.5` weights;
2. initial mixture weighted mean max abs error `<=1e-14`;
3. initial second-moment reconstruction max abs error `<=1e-12`;
4. linear shared covariance transport equals explicit `W C W.T` on a synthetic case;
5. component Gaussian ReLU marginal moments are finite and agree with analytic univariate formulas;
6. covariance diagonal overwrite equals each component marginal variance within `1e-12`;
7. exactly two components persist with no weight or split-direction changes;
8. deterministic synthetic repeat is bit-identical and finite.

RED must be committed before the estimator module exists and must fail only because the E039 module is absent. Public-mini data must not be accessed during RED/GREEN iteration.

## Single frozen public diagnostic

If and only if focused GREEN passes, run exactly one scientific diagnostic on public Phase-2 mini index `0` under normal billed FLOP accounting. One identical unmetered repeat is permitted solely for determinism.

Record exactly:

- final-layer raw MSE;
- billed FLOPs and utilization;
- adjusted proxy `raw_mse * max(0.1, utilization)`;
- failures count;
- residual and total wall time;
- initialization mean reconstruction error;
- initialization covariance reconstruction max abs error;
- maximum shared/component covariance-diagonal identity error;
- deterministic repeat max absolute difference;
- finite status;
- exact component count, weights, split direction, scope and no-hidden-fit checks.

## Frozen quantitative GO gates

Every gate is mandatory:

- raw final-layer MSE `<= 1.89e-08`;
- adjusted proxy `< 2.5e-09`;
- measured utilization `<= 0.14`;
- failures `= 0`;
- residual wall time `< 0.400 s`;
- all outputs and persistent states finite;
- deterministic repeat maximum absolute difference `== 0.0`;
- initialization weighted-mean max abs error `<= 1e-14`;
- initialization covariance reconstruction max abs error `<= 1e-12`;
- covariance-diagonal identity max abs error `<= 1e-12`;
- exact two components, exact weights `0.5/0.5`, and exact frozen all-ones split direction;
- no scorer/holdout/tuning/sweep/second-index access.

A GO requires every gate to pass.

## Kill rule

Any failed or unevaluable structural preflight or quantitative gate is **NO-GO / DROP E039**.

After terminal NO-GO there is no rescue under E039: no alternate split direction, adaptive direction, different component weights, additional components, per-component covariance persistence, covariance-rank change, fitted mixing weight, K3/K4 add-back, damping/clipping, second mini index, rerun, scorer, holdout, tuning, or sweep. Any materially different mechanism requires a fresh experiment ID from the then-current canonical.

If E039 reaches GO, the only next step is independent review handoff and at most one scorer handoff record. No automatic scorer execution or canonical merge is authorized.
