# E098 — late-onset rank-8 K22 response relevance

Idempotency key: `ARC-E098-LATE-K22-RESPONSE-RELEVANCE-20260918`

Status: **PREREGISTERED / PROTOCOL-ONLY**.

## Provenance

- Branch: `research/e098-late-k22-response-relevance-20260918`.
- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- E097 is terminal NO-GO for **persistent** rank-8 K22 memory across every layer. Its negative result is not rescued or rerun here.
- E097 nevertheless measured a sharp late-depth collapse in K22 effective rank; its result explicitly leaves a separately preregistered late-onset K22 class as a new hypothesis.
- E094 is the occupied source-axis K3 compute-compression lane.
- E095 is the occupied covariance + projected-sampling accuracy lane.
- E098 is disjoint from both: it asks whether a late-layer pairwise fourth-cumulant slice is output-relevant under a fixed analytic response, before any deployable propagation rule is coded.
- No public/public-mini benchmark, official scorer, holdout/full split, benchmark labels, fitted production coefficients, canonical mutation, ledger mutation, or merge is authorized.

## Scientific question

E097 showed that carrying rank-8 K22 from layer 0 is not a valid representation premise, but the same synthetic evidence showed much stronger low-rank concentration late in depth.

E098 tests the next necessary condition:

> If the exact late-layer K22 slice were available, does its fixed rank-8 component materially improve a one-step ReLU mean prediction under a parameter-free fourth-order Edgeworth response?

This is an **oracle value-of-information falsifier** on synthetic networks only. It does not claim that E098 can obtain K22 in production. A PASS would justify a separate successor experiment deriving a closed late-onset K22 birth/transport rule. A FAIL kills this response path before implementation work.

## Frozen K22 definition

For source-layer activation samples `H`:

1. `mu = mean(H, axis=0)`;
2. `Z = H - mu`;
3. `C = E[Z Z^T]`;
4. `Q = Z**2`;
5. `M22 = E[Q Q^T]`;
6. `K22 = M22 - outer(diag(C), diag(C)) - 2*(C*C)`;
7. set the diagonal exactly to zero;
8. symmetrize as `(K22 + K22.T)/2`.

Let `K22_r = U diag(lambda) U^T` be the symmetric rank-8 approximation using the eight eigenpairs with largest absolute eigenvalues. No rank sweep or eigenvalue threshold is allowed.

Signal eligibility requires

`||K22_off||_F / max(||C||_F^2, 1e-30) >= 1e-5`.

An ineligible observation is a gate failure.

## Fixed one-step response

For one next-layer output column `w`, define

- preactivation mean `m = w^T mu`;
- preactivation variance `s2 = w^T C w`;
- `s = sqrt(s2)`;
- `t = -m/s`.

The Gaussian moment-matched ReLU mean is

`g = s * phi(m/s) + m * Phi(m/s)`.

For the pairwise K22 slice, the contribution to the scalar fourth cumulant is

`kappa4_K22 = 3 * (w**2)^T K22_off (w**2)`.

For the rank-8 approximation,

`kappa4_K22_r = 3 * sum_a lambda[a] * (U[:,a]^T (w**2))**2`.

The fixed fourth-order Edgeworth correction to the ReLU mean is

`Delta(kappa4) = kappa4 / (24*s**3) * phi(t) * (t**2 - 1)`.

This follows from

`integral_t^inf (m+s z) H4(z) phi(z) dz = s phi(t) (t**2 - 1)`.

The E098 candidate is

`g_r = g + Delta(kappa4_K22_r)`.

The full-K22 response

`g_full = g + Delta(kappa4_K22)`

is recorded only as an oracle diagnostic. It is not a second candidate.

No clipping, damping, fitted scalar, blending, sign flip, per-network gate, adaptive rank, or learned coefficient is allowed.

## Frozen synthetic corpus

Use exactly three independently seeded He-ReLU MLPs:

- width `n=128`;
- depth `L=6`;
- weights iid `Normal(0, sqrt(2/n))`, generated in float64;
- network seeds: `98098, 98198, 98298`;
- moment-sample count per network: `32768`;
- reference-sample count per network: `32768`;
- moment input seeds: `198098, 198198, 198298`;
- reference input seeds: `298098, 298198, 298298`;
- inputs iid `N(0,I)`, float64;
- NumPy PCG64;
- source layers: exactly `l=3` and `l=4` (0-based post-ReLU layers), predicting layers 4 and 5 respectively;
- rank: exactly `r=8`.

Moment samples and reference samples are disjoint. K22, `mu`, and `C` are computed only from the moment stream. The next-layer reference mean is computed only from the independent reference stream.

There are exactly six network-transition observations.

## Recorded measurements

For each of six observations record:

- signal eligibility ratio;
- K22 Frobenius norm;
- rank-8 captured K22 Frobenius-energy fraction;
- spectral effective rank of K22;
- Gaussian-base one-step final-vector MSE versus independent reference mean;
- full-K22 Edgeworth MSE;
- rank-8-K22 Edgeworth MSE;
- rank8/base MSE ratio;
- full/base MSE ratio;
- maximum absolute rank-8 correction;
- minimum preactivation sigma;
- finite state.

Aggregate squared error across all output coordinates before forming aggregate MSE ratios.

The complete diagnostic is executed twice in the same process from the same frozen seeds. Scalar metrics must reproduce to absolute tolerance `1e-12`.

## Frozen GO gates

All gates must pass:

1. all six observations finite and signal-eligible;
2. every preactivation sigma is `>1e-10`;
3. median rank-8 K22 energy across the six observations `>=0.82`;
4. worst rank-8 K22 energy across the six observations `>=0.70`;
5. aggregate rank8-K22 MSE / Gaussian-base MSE `<=0.90`;
6. aggregate full-K22 MSE / Gaussian-base MSE `<=0.90`;
7. rank8-K22 candidate beats Gaussian base on at least `4/6` observations;
8. worst per-observation rank8/base MSE ratio `<=1.35`;
9. complete-repeat scalar max absolute difference `<=1e-12`;
10. all frozen cost bounds below are satisfied.

A 10% aggregate one-step improvement is required because this experiment is only a value-of-information test; a marginal effect does not justify inventing a new persistent state.

## Static cost envelope

This experiment does not implement K22 birth/propagation, but it freezes a necessary arithmetic envelope for a possible successor.

At Phase-2 width `W=1024`, rank `r=8`, budget `B=2**41`:

### One late-layer rank-8 response

Using `K22_r = U diag(lambda) U^T`, all output K22 scalar cumulants can be formed from `U^T (W_weight**2)`.

Conservative response bound:

`C_response = (2*r + 4)*W**2 + 16*r*W + 32*W`.

Required: `C_response / B < 1e-5`.

### Two late transitions with hypothetical factor transport

For feasibility only, bill two dense `W x W` by `W x r` products per late transition plus factor arithmetic and the response:

`C_two_late = 2 * (4*r*W**2 + 16*r*r*W) + 2*C_response`.

Required: `C_two_late / B < 1e-4`.

These are necessary cost bounds only; PASS does not establish a correct closed propagation law.

## Decision rule

- **STAGE_A_GO**: all frozen gates pass. E098 then closes as a successful value-of-information experiment. The only admissible successor is a new experiment ID that derives and falsifies a deterministic late-onset K22 birth/transport rule on synthetic data before any benchmark access.
- **STAGE_A_NO_GO**: any gate fails. E098 closes terminal NO-GO / DROP. No rank/layer/seed/sample/tolerance change, damping, sign change, alternate Edgeworth formula, fitting, rescue, rerun, public diagnostic, or second synthetic family is allowed under E098.

## Execution discipline

- Protocol-only first commit is mandatory.
- Stage A may be implemented only after this commit exists.
- Exactly one path-isolated scientific Stage-A workflow run is allowed.
- Workflow failure or scientific gate failure is terminal E098 NO-GO / DROP.
- No public/public-mini, official scorer, holdout/full, tuning, sweep, canonical/ledger mutation, merge, or rerun-as-rescue.
