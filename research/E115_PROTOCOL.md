# E115 — boundary-flux / backward-transport subspace falsifier

Tracking ID: `ARC-E115-BOUNDARY-FLUX-LYAPUNOV-COMPRESSION-20260919`

Status: **PREREGISTERED / PROTOCOL-ONLY**.

Branch: `research/e115-boundary-flux-lyapunov-compression-20260919`.

Direct parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

No implementation, workflow, scientific run, public data, scorer, holdout/full access, canonical mutation or ledger mutation is authorized by this commit.

## Why this lead exists

This protocol deliberately separates three evidence levels.

### A. Internally verified ARC evidence

E114 (`research/e114-activation-boundary-flux-20260919@b9f64030f65da9b32fc7718d04fb108ee1a73dab`) established an exact identity for zero-bias positively homogeneous ReLU networks: the Gaussian mean can be represented by activation-boundary flux on the input sphere. On its frozen 2-D deep fixture, direct sector integration and boundary-flux reconstruction agreed below `1e-14`.

E114 explicitly left one question open: whether output-relevant boundary flux has a compressible weight-derived representation that avoids enumerating all activation regions.

### B. Public measured clue, not adopted as fact

AIcrowd topic 18182 reports that, on its Phase-1 corpus, a backward transport operator had effective rank about `2.74`; the Phase-1 technique census (topic 18157) further reports a roughly six-dimensional, weight-computable subspace carrying a large fraction of final deterministic error.

Those measurements come from another team's estimator/corpus. E115 does **not** copy the numerical claim, assume that it transfers to Phase 2, or use their target data.

A public reply to the same discussion also points out the key logical risk: low effective rank of activations/transport does not imply that the estimation error or variance itself is low-dimensional. E115 is specifically designed to test that missing implication rather than presume it.

### C. Hypothesis introduced by E115

For a deep zero-bias ReLU network, the **vector activation-boundary flux that determines the final mean is concentrated in the leading left-singular subspace of the weight-only mean-gain backward transport**.

This is a new, falsifiable bridge between E114's exact boundary representation and the public low-rank-transport clue.

It is target-free: the candidate subspace is computed from weights only. Exact boundary flux is used only as a synthetic structural reference for falsification, never to construct the candidate subspace.

## Frozen small exact corpus

E115 is a structural gate, not a production estimator.

- input dimension: `2`;
- hidden/output width: `16`;
- depth: `4` ReLU layers;
- biases: exactly zero;
- weights: iid He-normal float64, `N(0, 2/width)` for square hidden layers; first layer uses the corresponding fan-in scaling `N(0, 2/2)`;
- network seeds: `115000..115007` (8 networks);
- final object: the 16-vector of layer-4 activation means.

The two-dimensional input is intentional: every activation boundary intersects the unit circle in finitely many points, so the complete angular partition and every derivative jump can be enumerated without Monte Carlo or numerical quadrature.

No seed, width, depth or rank sweep is allowed.

## Exact boundary-flux reference

For each frozen network, enumerate the complete unit-circle partition induced by all four ReLU layers.

Within each current angular sector, every preactivation is of the form

`a cos(theta) + b sin(theta)`.

A new zero is therefore solved analytically from `atan2` and admitted only if it lies strictly inside the current sector. Coincident roots are merged with a deterministic angular tolerance `2^-40`.

At each unique final partition boundary `theta_j`:

1. evaluate the left and right final-output angular derivatives analytically from the two adjacent affine sectors;
2. record the vector jump `j_j in R^16`;
3. form the exact vector flux sum `s = sum_j j_j`;
4. independently integrate each affine sector analytically over angle and verify the E114 boundary identity coordinate-wise.

Define the flux-energy matrix

`C_flux = sum_j j_j j_j^T`.

This matrix is an internal structural diagnostic. It is not available to the deployable candidate.

## Frozen weight-only candidate subspace

Let `W_l` denote the square weight matrix from layer `l-1` to layer `l` for layers 2..4.

Use the zero-bias mean-gain linearization `g = 1/2` and define the layer-1-to-output transport

`T = (0.5 W_4) (0.5 W_3) (0.5 W_2)`.

Let `U_w in R^(16 x 3)` be the three leading **left singular vectors** of `T`, ordered by descending singular value with deterministic sign canonicalization (largest-magnitude coordinate non-negative).

Rank is frozen at exactly `k=3`. It is motivated only by the public effective-rank clue and is not fitted on E115 flux results.

For capacity diagnosis only, define `U_oracle` as the top-three eigenvectors of `C_flux`. `U_oracle` is never a candidate estimator and cannot authorize production use.

## Frozen measurements

Per network record:

1. boundary count;
2. exact boundary-identity max absolute and relative discrepancy;
3. `trace(C_flux)`;
4. **oracle rank-3 flux capture**
   `trace(U_oracle^T C_flux U_oracle) / trace(C_flux)`;
5. **weight-derived rank-3 flux capture**
   `trace(U_w^T C_flux U_w) / trace(C_flux)`;
6. subspace overlap
   `||U_w^T U_oracle||_F^2 / 3`;
7. exact flux mean vector `s`;
8. projected flux mean `U_w U_w^T s`;
9. relative squared mean loss
   `||s - U_w U_w^T s||_2^2 / max(||s||_2^2, 1e-30)`;
10. singular values of `T`;
11. finite/deterministic checks.

Aggregate capture metrics are formed from pooled numerator and denominator sums, not by averaging per-network ratios.

## Frozen gates

### Gate 0 — exact instrument

All 8 networks must satisfy:

- finite sector coefficients, jumps and flux matrices;
- boundary-flux mean equals independent analytic sector integration with max relative discrepancy `<=1e-10`;
- deterministic repeat max abs `==0` for partition angles, jump vectors, `C_flux`, `U_w` and all reported metrics after sign canonicalization.

Failure => **INSTRUMENT NO-GO**. Do not interpret the hypothesis.

### Gate 1 — low-rank capacity exists

The oracle rank-3 subspace must achieve:

- pooled flux-energy capture `>=0.80`;
- capture `>=0.70` on at least `6/8` networks.

Failure => **TERMINAL SCIENTIFIC NO-GO** for rank-3 boundary-flux compression on this frozen corpus. Do not build a weight-derived production approximation.

### Gate 2 — weight-only transport finds the flux subspace

The candidate `U_w` must achieve all of:

- pooled flux-energy capture `>=0.60`;
- capture `>=0.50` on at least `6/8` networks;
- pooled oracle-overlap metric `>=0.45`;
- pooled relative squared loss of the exact flux mean after projection `<=0.25`;
- relative squared mean loss `<=0.50` on at least `6/8` networks.

Failure => **TERMINAL NO-GO / CLOSE THIS LEAD**. No alternate rank, layer, gain, transport definition, seed, centering rule or learned alignment may be tried under E115.

## Production relevance gate

E115 itself does not enumerate production boundaries and makes no production-accuracy claim.

If Gates 0–2 pass, a successor may test a production representation only if it first proves an all-in cost path below utilization `0.13` at width 1024/depth 16.

The only pre-authorized way to obtain the rank-3 weight subspace in such a successor is fixed four-step subspace iteration using applications of `T` and `T^T`; no full SVD is assumed free. All matmul/matvec, orthogonalization, RNG (if any), flux-statistic construction and estimator arithmetic must be billed.

Passing E115 therefore means only:

> exact deep boundary flux is materially low-rank on the frozen exact corpus, and a simple weight-only backward transport recovers enough of that subspace to justify one separately preregistered production-compression experiment.

It does **not** mean the remaining flux can already be estimated without boundary enumeration.

## Kill / scope rules

- exactly one implementation path and one frozen small-exact execution after independent protocol review;
- no public/public-mini dataset;
- no benchmark target/final_means;
- no official scorer;
- no holdout/full split;
- no rank/seed/width/depth/gain sweep;
- no post-result transport redefinition;
- no learned or target-fitted alignment;
- no rescue or scientific rerun;
- no canonical/ledger mutation;
- no merge.

If the weight-derived subspace misses Gate 2 while the oracle passes Gate 1, record the result as a **lawful-observable failure**: the boundary flux has low-rank capacity, but this target-free transport statistic does not find it. That outcome closes this lead rather than licensing oracle-guided tuning.
