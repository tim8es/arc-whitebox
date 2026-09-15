# E038 protocol — fixed two-component half-space Gaussian location-mixture closure

Status: **PREREGISTERED / NOT YET RUN**

Idempotency key: `ARC-E037-OWNER-20260915-E038`

## Provenance and firewall

- Branch: `research/e038-halfspace-gaussian-mixture-20260915`.
- Direct parent canonical: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- This is a fresh experiment from canonical; it inherits no commits, code, data products, fitted parameters, or state from E021, E028, or E029–E037.
- E021 and E028 remain separate review-only lanes and must not be merged into, cherry-picked into, or used as mutable inputs to E038.
- Public Phase-2 mini index `0` only is permitted for one frozen local scientific diagnostic after focused GREEN.
- No official scorer, holdout/full split, second mini index, tuning, sweep, adaptive search, coefficient fitting, canonical mutation, or ledger mutation is authorized.
- Any failed or unevaluable gate closes E038 permanently; any materially different mechanism requires E039+.

## Hypothesis

Recent low-cost closures failed for a common reason: coordinatewise cumulants or compact global K3/K4 carriers did not preserve enough cross-neuron distributional structure, while the output-Hessian correction around the ReLU kink was not a near-frontier perturbation. E038 tests a different representation class: a deterministic **location mixture** with two persistent conditional means and one shared full covariance.

The mixture is intended to represent a coarse non-Gaussian half-space split while retaining the second-order cross-neuron dependence that cheap diagonal-only methods lost. It is not a Gaussian scale mixture, not a K3/K4 carrier, not a source-stack method, and not an output-Hessian correction.

## Frozen representation

At every layer carry exactly:

- mixture weights `w_minus = w_plus = 0.5`;
- two means `mu_minus`, `mu_plus`;
- one shared symmetric covariance `C`.

No extra components, component-specific covariance matrices, cumulants, source histories, low-rank carriers, learned weights, or fitted correction coefficients are permitted.

### Initial split

Input is standard Gaussian in width `n=1024`.

Use one fixed deterministic unit direction

`v = (1/sqrt(n)) * [1,1,...,1]`.

Approximate the exact Gaussian conditioned on the sign of `v^T X` by two Gaussian components with the exact first two conditional moments of the half-space split:

- `a = sqrt(2/pi)`;
- `mu_plus = +a v`;
- `mu_minus = -a v`;
- shared covariance `C = I - (2/pi) v v^T`.

The equal-weight mixture therefore has exact global mean zero and exact global covariance `I` at initialization.

The direction `v`, weights, and all constants are frozen before any mini-data access. No alternate direction, learned rotation, random sign, leverage selection, or layerwise reselection is allowed.

## Frozen layer update

For each dense linear layer with matrix `W`:

1. propagate component means independently:
   - `m_minus_pre = W @ mu_minus`;
   - `m_plus_pre = W @ mu_plus`;
2. propagate the single shared covariance once:
   - `C_pre = W @ C @ W.T`;
   - `var_pre = diag(C_pre)`;
3. for each component separately, apply exact univariate Gaussian ReLU mean/variance formulas using that component mean and the common `var_pre`;
4. for each component form the frozen first-order Gaussian-response covariance approximation
   `C_component = outer(Phi(alpha), Phi(alpha)) * C_pre`, then overwrite its diagonal with that component's exact ReLU variance;
5. set the next shared covariance to the equal-weight average of the two within-component covariances only:
   `C_next = 0.5*(C_minus + C_plus)`;
6. keep the two component means separate after ReLU; do not collapse or re-split them;
7. the predicted layer mean is exactly `0.5*(mu_minus + mu_plus)`.

The between-component mean spread is represented explicitly by the two means and is **not** folded into the shared within-component covariance. No moment-matching reset, adaptive split, extra Price term, K3/K4 add-back, damping, clipping, or fitted scalar is allowed.

## Structural preflight and focused TDD

Before public-mini science, focused tests must establish:

1. initial equal-weight mixture mean is zero to `<=1e-14`;
2. initial global covariance reconstructed as `C + 0.5*mu_minus mu_minus^T + 0.5*mu_plus mu_plus^T` equals identity to `<=1e-12`;
3. split direction is exactly the normalized all-ones vector and deterministic;
4. shared linear covariance transport equals explicit `W C W.T` on a synthetic case;
5. Gaussian ReLU component mean/variance matches analytic formulas on synthetic vectors;
6. covariance diagonal overwrite equals the component variances to `<=1e-12`;
7. weights remain exactly `(0.5,0.5)` and exactly two components persist through all layers;
8. deterministic synthetic repeat is bit-identical and finite;
9. static compute preflight estimates total utilization `<=0.14` under one shared dense covariance transport per layer plus two O(n^2) response updates.

RED must be established before estimator implementation. Focused tests may iterate before scientific data. No public mini access is allowed until GREEN and cost preflight both pass.

## Single frozen diagnostic

After focused GREEN, run exactly one local scientific diagnostic on public Phase-2 mini index `0` under normal billed FLOP accounting. One identical unmetered repeat is permitted only to verify determinism.

Record exactly:

- final-layer raw MSE;
- billed FLOPs and utilization;
- adjusted proxy `raw_mse * max(0.1, utilization)`;
- residual and total wall time;
- maximum component-mean separation by layer;
- shared-covariance diagonal consistency error;
- initialization mean/covariance reconstruction errors;
- deterministic repeat maximum absolute difference;
- finite status and local failure count;
- exact two-component/weights/direction/scope checks.

## Frozen GO gates

All gates are mandatory:

- raw final-layer MSE `<=1.89e-08`;
- adjusted proxy `<2.5e-09`;
- measured utilization `<=0.14`;
- residual wall time `<0.400 s`;
- local failures `=0`;
- all outputs and state finite;
- deterministic repeat maximum absolute difference `==0.0`;
- initialization mean error `<=1e-14`;
- initialization covariance reconstruction max abs error `<=1e-12`;
- component/shared covariance diagonal consistency max abs error `<=1e-12`;
- exactly two equal-weight components and exact frozen all-ones split direction throughout;
- no scorer/holdout/tuning/sweep/second-index access.

## Kill rule

Any failed or unevaluable structural preflight or quantitative gate is **NO-GO / DROP E038**.

After terminal NO-GO there is no rescue under E038: no alternate split direction, more mixture components, unequal/adaptive weights, component-specific covariance, re-splitting, covariance/K3/K4 add-back, damping/clipping, second mini index, rerun, scorer, holdout, or tuning. Any such mechanism requires a fresh experiment ID from the then-current canonical.

If E038 reaches GO, the only next step is independent review handoff and at most one scorer handoff record; no automatic scorer execution or canonical merge is authorized.
