# E117 — covariance-response compression of the exact final observable

Tracking ID: `ARC-E117-COVARIANCE-RESPONSE-OBSERVABLE-COMPRESSION-20260919`

Status: **PREREGISTERED / PROTOCOL-ONLY**.

Branch: `research/e117-covariance-response-observable-compression-20260919`.

Direct parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

This first commit authorizes no implementation workflow, production run, public/public-mini data, benchmark targets, scorer, holdout/full access, tuning, canonical mutation, ledger mutation or merge.

## One public clue, with scope

The only public mechanism imported into this protocol is the following measured clue from the ARC Phase-1 literature:

- Team Puffi's SSC / separate-universe response closure compressed a fourth-order joint object into at most four live covariance-response modes rather than materializing an `n^4` tensor.
- The public census reports that, on their matched panel, this response branch reduced layer-32 MSE materially versus factorized K3/K4 while remaining much cheaper than dense K4.
- The same sources explicitly report that SSC was **not** a frontier estimator and still missed the best deterministic carrier by a large margin.

E117 does **not** copy their fitted `Lambda`, training corpus, response coefficients, implementation, or any unpublished definition. Those details are neither needed nor assumed.

The transferable clue is narrower:

> joint dependence may be compressible in the directions to which the final observable responds, even when the full joint tensor is not compressible cheaply.

That statement is treated as a hypothesis generator, not as evidence that our network or E114 flux is low-rank.

## Why this is E114-compatible

E114 established an exact target-free representation of the mean of a zero-bias positively homogeneous ReLU network through activation-boundary flux on the input sphere.

E117 asks a different question from E115/E116:

> If joint dependence at an intermediate hidden layer is perturbed infinitesimally, is the **linear response of the exact final mean** concentrated in only four covariance directions, and can those directions be selected from weights alone?

The final observable is always evaluated by E114-style exact angular partition / analytic sector integration on a frozen small network. No Gaussian closure supplies the reference answer.

This is not:
- E115's output-flux subspace / backward-transport test;
- E116's fixed input projection theorem;
- a fitted cumulant closure;
- a control variate;
- a public-target regression.

## Frozen exact corpus

Eight independent synthetic networks:

- input dimension `d=2`;
- width `n=8`;
- depth `4` ReLU layers;
- all biases exactly zero;
- float64 He-normal weights from PCG64;
- seeds `117000, 117001, ..., 117007`;
- first layer scale `sqrt(2/2)`;
- square hidden-layer scale `sqrt(2/8)`.

The vector observable is the full 8-dimensional layer-4 activation mean

`m = E[h4(X)]`, `X ~ N(0, I2)`.

The joint-state perturbation is inserted **after layer 2 and before W3**.

No alternate layer, seed, width, depth, rank or gain may be tried under E117.

## Exact response operator

Let `h2(x)` be the frozen layer-2 activation and let `A` be a symmetric `8 x 8` matrix.

Define the perturbed network by replacing the input to `W3` with

`(I + eps A) h2(x)`.

For the unperturbed network, enumerate the complete E114-style angular partition of the unit circle induced by all four ReLU layers.

Inside one differentiable angular sector with frozen diagonal gate masks `D1..D4`,

`h2(x) = D2 W2 D1 W1 x`

and the exact first derivative of the final activation vector with respect to `eps` at zero is

`D4 W4 D3 W3 A D2 W2 D1 W1 x`.

Because the zero-bias ReLU network is continuous and piecewise linear, the first-order boundary-motion terms cancel at sector interfaces; the derivative of the Gaussian mean can therefore be obtained by analytically integrating this sectorwise JVP and multiplying by the exact Gaussian radial mean.

Use the Frobenius-orthonormal symmetric basis:

- `B_ii = e_i e_i^T`;
- `B_ij = (e_i e_j^T + e_j e_i^T)/sqrt(2)` for `i<j`.

There are exactly `q=36` basis elements.

For each basis element compute the exact response vector

`r_q = d/d eps E[h4_eps(X)] | eps=0`.

Stack them as

`R in R^(8 x 36)`.

`R` is the exact linear map from an infinitesimal symmetric hidden-state deformation to the final observable.

## Independent instrument checks

For every network:

1. E114 direct analytic sector mean and boundary-flux mean must agree coordinate-wise.
2. For four frozen test matrices `A_test` generated from PCG64 seed `117900 + network_index`, normalize each to Frobenius norm one.
3. Compare the analytic JVP response `L(A_test)` against exact re-enumerated sector means at `eps = +/- 2^-16` and `+/- 2^-17`.
4. The two centered finite-difference derivatives must converge toward the analytic JVP; use the finer derivative for the independent discrepancy report.

These matrices are instrument-only and cannot define candidate modes.

## Oracle capacity: can four response modes preserve the observable?

Compute the SVD of the exact response operator

`R = U Sigma V^T`.

The best possible four-dimensional covariance subspace captures

`C_oracle = (sigma_1^2 + ... + sigma_4^2) / sum_j sigma_j^2`.

This is an **impossible oracle diagnostic only**. Its singular vectors may never be used to construct a deployable candidate.

If `C_oracle` is small, the public SSC clue does not transfer to the E114 observable and the lead closes immediately.

## Frozen lawful weight-only four-mode candidate

No target, exact flux, exact response matrix or synthetic reference may select the candidate directions.

Use only downstream weights.

Define the downstream linear proxy from the perturbed layer-2 state to the final pre-gate output:

`P = W4 W3`.

Define

`G = P^T P`.

Let `u1..u4` be the top four eigenvectors of `G`, descending by eigenvalue, with deterministic sign canonicalization: the largest-magnitude coordinate is non-negative, ties broken by lowest coordinate index.

The four symmetric covariance modes are

`A_k = u_k u_k^T`, `k=1..4`.

Because the `u_k` are orthonormal, the `A_k` are Frobenius-orthonormal.

Let `P_cand` be the orthogonal projector in the 36-dimensional symmetric-matrix coordinate system onto the span of these four `A_k`.

The candidate response-energy capture is

`C_weight = ||R P_cand||_F^2 / ||R||_F^2`.

Also report the oracle-normalized recovery

`Q = C_weight / C_oracle`.

No gate fractions, sampled activations, exact sector information, fitted coefficients or target values enter `A_k`.

## Frozen measurements

Per network record:

- angular sector count;
- E114 boundary-flux/direct-mean max absolute and relative discrepancy;
- four analytic-JVP vs finite-difference response discrepancies at both step sizes;
- `||R||_F^2`;
- singular values of `R`;
- numerical rank of `R` at relative threshold `1e-12` (diagnostic only);
- `C_oracle`;
- `C_weight`;
- `Q=C_weight/C_oracle`;
- the four eigenvalues of `G` used by the candidate;
- exact deterministic replay deltas.

Aggregate captures use pooled energy numerators and denominators across all eight networks, not the arithmetic mean of ratios.

## Frozen gates

### Gate 0 — exact instrument

All eight networks must satisfy:

- finite exact sector coefficients and response entries;
- E114 boundary-flux/direct-mean relative discrepancy `<=1e-10`;
- finer-step finite-difference vs analytic-JVP relative discrepancy `<=2e-5` for all 32 instrument checks;
- halving `eps` must not increase the response discrepancy by more than `1.25x`;
- deterministic replay max absolute delta `==0` for partitions, `R`, candidate modes and reported metrics after sign canonicalization.

Failure => **INSTRUMENT NO-GO**. Do not interpret scientific gates and do not rerun with a different tolerance/step.

### Gate 1 — four-mode observable-response capacity

The oracle four-dimensional covariance subspace must achieve:

- pooled `C_oracle >= 0.80`;
- `C_oracle >= 0.70` on at least `6/8` networks.

Failure => **TERMINAL SCIENTIFIC NO-GO / CLOSE RESPONSE-MODE LEAD**.

This means the E114 final observable itself needs more than four independent covariance-response directions on the frozen exact corpus; no lawful selector can rescue a four-mode state.

### Gate 2 — weight-only selector recovers the capacity

The frozen downstream-Gram modes must achieve all of:

- pooled `C_weight >= 0.50`;
- `C_weight >= 0.40` on at least `6/8` networks;
- pooled `Q = C_weight/C_oracle >= 0.60`;
- `Q >= 0.50` on at least `6/8` networks.

Failure => **TERMINAL NO-GO / LAWFUL-SELECTION FAILURE**.

If Gate 1 passes but Gate 2 fails, record explicitly:

> low-dimensional covariance-response capacity exists for the exact observable, but this simple target-free weight-only selector does not find it.

No oracle-guided rotation, fitted `Lambda`, alternative downstream product, gate-weighted product, rank increase or layer change is allowed under E117.

## What a pass would and would not mean

Passing Gates 0–2 would establish only that, on the frozen exact corpus:

1. the exact final observable has a strongly four-dimensional first-order response to intermediate symmetric joint-state perturbations; and
2. a simple weight-only downstream Gram statistic recovers a material fraction of that response subspace.

A pass does **not** establish:

- that the full hidden joint law is four-dimensional;
- that finite non-infinitesimal cumulants are represented exactly;
- that SSC's fitted coefficients transfer;
- that E114 boundary flux can already be computed at production width;
- that a production estimator beats E104;
- any public/private competition accuracy.

A successor would need a separate protocol proving how to propagate or estimate the four response amplitudes without exact boundary enumeration and with all-in utilization `<=0.13`.

## Kill / scope rules

- exactly one implementation path;
- exactly one frozen small-exact execution after independent protocol review;
- no public/public-mini dataset;
- no benchmark `final_means` or other labels;
- no scorer;
- no holdout/full split;
- no rank/seed/layer/width/depth/tolerance/finite-difference sweep;
- no fitted response coefficients;
- no oracle-guided candidate construction;
- no post-result rescue or scientific rerun;
- no canonical/ledger mutation;
- no merge.

Any failed scientific gate closes E117.
