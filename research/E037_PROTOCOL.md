# E037 protocol — full covariance + signed rank-4 K3/K4 response

Status: **PREREGISTERED**

Idempotency key: `ARC-KEEP-GOING-RESEARCH-20260915-E037`

## Base and firewall

- Fresh branch: `research/e037-signed-k3-k4-response-20260915`.
- Exact canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Public Phase-2 mini index `0` only for the single frozen scientific diagnostic.
- No official scorer, holdout, fit, teacher forcing, sweep, tuning, alternate rank, alternate Edgeworth order, or second scientific diagnostic.
- E019–E036 remain immutable. Any failed/unevaluable gate closes E037; any later mutation requires E038+.

## Non-duplication

E016 tested a fitted rank-1 **off-diagonal K4 regeneration mode inside V25**, with seven fitted layer scalars `gamma_8..gamma_14` against a dense K4 teacher. E037 does none of that: no V25 K4 regeneration, no teacher tensor, no fit, no gamma table, and no layer window.

E037 extends the fit-free carrier family E034–E036 with genuinely non-Gaussian fourth-order cross-neuron state: a signed global CP K4 block propagated through all layers. This is not a Price-order or covariance-rank mutation of E036.

## Hypothesis

E033 showed diagonal K3/K4 alone is useless; E034 showed global K3 response without covariance is also insufficient; E035 restored covariance and improved raw error materially, while E036 showed adding higher Gaussian Price terms does not help. The remaining candidate is non-Gaussian cross-neuron fourth-cumulant content.

E037 carries both

`K3 ~= diag_residual_3 + sum_{r=1}^4 s3_r a3_r^(x3)`

and

`K4 ~= diag_residual_4 + sum_{r=1}^4 s4_r a4_r^(x4)`

without source histories. Under a dense linear layer `W`, the global factors contract exactly within this representation as `(W a3)^3` and `(W a4)^4`.

## Frozen estimator

State per layer:

- mean `mu`;
- full covariance `cov`;
- diagonal residual connected third cumulant `k3_diag`;
- exactly four signed K3 atoms `A3 in R^(n x 4)` and signs `S3`;
- diagonal residual connected fourth cumulant `k4_diag`;
- exactly four signed K4 atoms `A4 in R^(n x 4)` and signs `S4`.

Linear update, with `W = weight.T`:

- `mu_pre = W @ mu`;
- `cov_pre = W @ cov @ W.T`;
- `var_pre = diag(cov_pre)`;
- `A3_pre = W @ A3`;
- `k3_pre = (W**3) @ k3_diag + sum_r S3_r*A3_pre[:,r]**3`;
- `A4_pre = W @ A4`;
- `k4_pre = (W**4) @ k4_diag + sum_r S4_r*A4_pre[:,r]**4`.

ReLU marginal update uses the fixed embedded 16-node standard-normal Gauss-Hermite rule and exactly the first-order bivariate cumulant-free Edgeworth density

`1 + gamma1*H3/6 + gamma2*H4/24`,

where `gamma1=k3/sigma^3`, `gamma2=k4/sigma^4`, `H3=z^3-3z`, and `H4=z^4-6z^2+3`. No H6 cross term, clipping, damping, positivity repair, or coefficient fitting is permitted.

Moments 1 through 4 determine:

- `mu_post`;
- `var_post`;
- connected `k3_total`;
- connected `k4_total = central_m4 - 3*var_post^2`.

Cross-neuron covariance uses the frozen E035 first Price term only:

`cov_post_ij = Phi(alpha_i) Phi(alpha_j) cov_pre_ij`,

followed by functional diagonal overwrite with `var_post`. E036 already falsified higher Gaussian Price terms, so no Price-order sweep is part of E037.

Carrier response update:

- old K3 and K4 atoms are multiplied coordinatewise by the same frozen Gaussian local response `p=Phi(alpha)`;
- exactly one leverage-selected residual K3 birth and one leverage-selected residual K4 birth occur per layer;
- K3 birth score: `|k3_diag_j| * sum_i |W_ij|^3`, atom scale `|k3_diag_j|^(1/3)`;
- K4 birth score: `|k4_diag_j| * sum_i |W_ij|^4`, atom scale `|k4_diag_j|^(1/4)`;
- connected K4 sign is `sign(k4_diag_j)`; exact zero has frozen sign `+1`;
- K3 and K4 use independent exact rank-4 FIFO blocks, no SVD/rotation/refit;
- post-ReLU diagonal residuals are defined by exact marginal subtraction of the propagated CP blocks.

No K5+, D21/source tensor, old-source basis, sampling, fitting, post-hoc correction, or output calibration.

## Focused tests before science

Before any mini data are read, tests must verify:

1. signed CP K3 and K4 marginals match explicit signed powers;
2. K3 and K4 leverage birth indices/scales/signs and zero-sign rules are exact;
3. both FIFO blocks retain exactly four slots;
4. linear full covariance equals `W C W.T`;
5. zero-skew/zero-kurtosis ReLU moments are finite and near analytic Gaussian ReLU mean/variance;
6. connected fourth cumulant algebra from raw moments is correct on a hand case;
7. covariance diagonal overwrite is accurate within `1e-12`;
8. synthetic carrier repeats bit-identically.

Focused tests may iterate before science. Once GREEN, exactly one frozen index-0 diagnostic is allowed.

## Frozen gates

All must pass:

- final-layer raw MSE `<=1.89e-08`;
- utilization `<=0.14`;
- adjusted proxy `raw_mse * max(0.1, utilization) <2.5e-09`;
- residual wall time `<0.400 s`;
- finite output/state;
- deterministic repeat max abs `==0.0` and identical K3/K4 newborn sequences;
- covariance diagonal max abs error `<=1e-12`;
- static/runtime scope confirms full covariance, rank-4 K3, rank-4 K4, H3+H4 first-order Edgeworth only, and no NumPy import in estimator method.

Any failed or unevaluable gate => **NO-GO / DROP E037**. No rerun or rescue under E037.
