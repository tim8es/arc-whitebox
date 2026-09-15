# E038 protocol — conditional-Gaussian full-covariance ReLU kernel

Idempotency key: `ARC-E037-RESEARCH-20260915-E038`

Status: **PREREGISTERED / NOT YET RUN**

## Provenance and firewall

- Branch: `research/e038-conditional-gaussian-cov-20260915`.
- Exact canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- E019–E037 are immutable; E037 is occupied independently and is not inherited.
- Public Phase-2 mini index **0 only** for exactly one frozen scientific diagnostic.
- No holdout/full split, scorer, fit, coefficient search, node-count search, tuning, sweep, second mini index, canonical mutation, or ledger mutation.

## Disjoint mechanism

E035 showed that carrying full covariance is materially better than coordinatewise closures but its post-ReLU covariance was only the first Price term `Phi(alpha_i) Phi(alpha_j) C_ij`, leaving raw MSE `4.920249745871731e-05` at utilization `0.06092773509772087`.

E038 removes K3/K4/source state entirely and instead spends the available compute on the **full nonlinear Gaussian covariance transform**. At each layer, the preactivation state is approximated as one multivariate Gaussian `(mu,C)`. The affine transform is exact within that state. Each ReLU marginal mean/variance is computed from the analytic univariate Gaussian formula. Each pairwise second moment is computed by a frozen 16-node conditional-Gaussian integral, preserving arbitrary nonzero means and the full correlation matrix rather than truncating Price's series.

This is not an angular carrier, source-stack compression, K3/K4 response carrier, output Hessian, or Price-order micro-edit.

## Frozen transform

For `z = W h`:

- `mu_pre = W @ mu`;
- `C_pre = (W @ C) @ W.T`;
- `sigma_i = sqrt(C_pre[ii])`.

For each coordinate, with `alpha=mu/sigma`, use exactly

- `E[relu(X)] = sigma*phi(alpha) + mu*Phi(alpha)`;
- `E[relu(X)^2] = (mu^2+sigma^2)*Phi(alpha) + mu*sigma*phi(alpha)`.

For every pair `(i,j)`, define `rho_ij=C_ij/(sigma_i sigma_j)`, clipped only to the mathematical correlation interval `[-1,1]`. With the fixed existing 16-node standard-normal Gauss-Hermite rule `(z_q,w_q)`, compute

`E[relu(X_i)relu(X_j)] ~= sum_q w_q relu(mu_i+sigma_i z_q) * E[relu(Y_j) | Z_i=z_q]`,

where

- conditional mean `m_j|q = mu_j + sigma_j*rho_ij*z_q`;
- conditional std `s_j|i = sigma_j*sqrt(max(1-rho_ij^2, 1e-15))`;
- `E[relu(Y)|q] = s*phi(m/s) + m*Phi(m/s)`.

The resulting second-moment matrix is symmetrized once as `0.5*(M+M.T)`. Post-ReLU covariance is `M - mu_post mu_post.T`, then its diagonal is overwritten exactly by the analytic univariate variance. There is no damping, PSD projection, eigenvalue clipping, fitted scalar, K3/K4 correction, or source memory.

Initial state is exactly `mu=0`, `C=I`. The same transform is applied to all 16 layers.

## Quantitative hypothesis

E035 demonstrates that the dominant full-covariance affine carrier itself fits comfortably below the target compute gate (`0.06093 B`). E038 replaces the cheap first-Price post-ReLU update by 16 sequential `n x n` conditional moment updates per layer, still `O(16 L n^2)` on top of the same `O(L n^3)` covariance transport. Conservatively this should remain below utilization `0.14`.

The scientific hypothesis is that the roughly 2600x E035 raw miss is dominated by truncation of the nonlinear covariance map rather than by missing persistent K3/K4 state. If the full conditional-Gaussian covariance transform is the correct representation class, the frozen target is simultaneously:

- raw final-layer MSE `<=1.89e-08`;
- utilization `<=0.14`;
- adjusted proxy `raw_mse * max(0.1, utilization) <2.5e-09`.

## Focused tests before public data

Tests must establish before any mini-data access:

1. analytic univariate ReLU mean/variance match high-accuracy synthetic Monte Carlo / numerical reference on fixed hand cases;
2. zero-correlation pair moment factorizes into the product of univariate means;
3. covariance update is symmetric and its diagonal equals analytic marginal variance to `<=1e-12`;
4. affine covariance transport equals `(W C) W.T`;
5. fixed GH node/weight tables are exactly length 16 and deterministic;
6. repeated synthetic network calls are bit-identical and finite;
7. no K3/K4/source state exists in the estimator path.

Focused tests may iterate before science. After GREEN, exactly one public-mini index-0 diagnostic is allowed.

## Frozen local diagnostic and gates

Record final-layer MSE, billed FLOPs/utilization, adjusted proxy, residual and wall time, finite status, deterministic repeat max abs difference, covariance diagonal error, maximum absolute correlation before mathematical clipping, and scope checks.

All gates must pass:

- raw final MSE `<=1.89e-08`;
- utilization `<=0.14`;
- adjusted proxy `<2.5e-09`;
- failures `==0`;
- residual wall time `<0.400 s`;
- all outputs/state finite;
- deterministic repeat max abs difference `==0.0`;
- covariance diagonal max abs error `<=1e-12`;
- exact 16-node conditional kernel and scope unchanged.

Any failed or unevaluable gate => **NO-GO / DROP E038**. No alternate quadrature order, epsilon, symmetrization, PSD repair, K3/K4 add-back, source add-back, rerun, rescue, second index, scorer, holdout, tuning, or sweep under E038. Any material mutation requires E039+ from canonical.
