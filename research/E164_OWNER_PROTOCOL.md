# E164 OWNER PROTOCOL — clean-room Angular Gauge Only

Date: 2026-09-21

Status: **PROTOCOL FROZEN / STANDALONE ONE-RUN EXECUTION AUTHORIZED AFTER CODE FREEZE**

Branch:

`research/e164-cleanroom-ago-20260921`

Clean bootstrap parent:

`research/bootstrap@7a0034088ebbffbd74b441e1797c272e9d33cbff`

Idempotency key:

`ARC-E164-CLEANROOM-AGO-20260921`

## 1. Clean-room boundary

E164 is a new owner from bootstrap.

Forbidden as implementation sources or runtime dependencies:

- E162 code, workflow, tests, falsifier, receipt, artifacts, or branch ancestry;
- E154 code/artifacts;
- E157 code/artifacts;
- K4, D4, D22, scalar c4, recurrent K4;
- public benchmark targets, scorer, holdout, full suite, submission;
- target fitting, sweep, rescue, rerun.

The only carried scientific statement is the independently derivable H160
angular/radial identity:

For a zero-bias positively homogeneous ReLU network,

`X=(R/sqrt(n))Y`

with `R` independent of sphere direction `Y`, hence

`F(X)=(R/sqrt(n))F(Y)`.

Let

`a1(n)=E[R/sqrt(n)]`.

Then exactly:

`mu_G = a1 mu_A`

and, because `E[(R/sqrt(n))^2]=1`,

`C_G = C_A + (1-a1^2) mu_A mu_A^T`.

Therefore the exact gauge map is

`mu_A = mu_G/a1`

`C_A = C_G - (1/a1^2 - 1) mu_G mu_G^T`.

Final Gaussian-input mean readout is exactly

`mu_G,out = a1 mu_A,out`.

## 2. Frozen parent

The parent is a clean-room full-covariance K2 Wick closure.

Input:

`mu=0`, `C=I_n`.

Each zero-bias layer uses row-weight matrix `W`:

`mu_pre=W mu`

`C_pre=W C W^T`

`v=diag(C_pre)`.

For each coordinate:

`sigma=sqrt(v)`

`alpha=mu_pre/sigma`

`phi=exp(-alpha^2/2)/sqrt(2pi)`

`Phi=NormalCDF(alpha)`.

Gaussian ReLU moments:

`p1=sigma*phi + mu_pre*Phi`

`p2=(mu_pre^2+v)*Phi + mu_pre*sigma*phi`.

Off-diagonal K2 Wick closure:

`C_out,ij
 = C_pre,ij Phi_i Phi_j
 + 0.5 C_pre,ij^2 (phi_i/sigma_i)(phi_j/sigma_j)`

for `i != j`.

Diagonal:

`C_out,ii=p2_i-p1_i^2`.

Mean:

`mu_out=p1`.

This arithmetic is identical between parent and AGO except for the one gauge
transform and final radial readout below.

## 3. Frozen AGO candidate delta

After the **first activation state only**:

`(mu_G1,C_G1) -> (mu_A1,C_A1)`

using the exact gauge equations above.

No later gauge refresh is allowed.

Layers 2..8 use exactly the same K2 Wick update as the parent.

At the end:

`mu_AGO = a1(n) * mu_A,final`.

No other candidate arithmetic is permitted.

## 4. Target-free fixtures

Exactly one standalone Actions run contains all fixtures.

### F0 — exact2D

- width/input: 2;
- depth: 8;
- zero bias;
- row-weight He-Gaussian matrices;
- seed: `164002`;
- float64.

Reference:

- exact piecewise-linear integration over the radius-`sqrt(2)` circle;
- exact final Gaussian mean = exact angular mean times `a1(2)`;
- exact first-activation angular mean/covariance by analytic sector integration.

### F1 — dense32

- width/input: 32;
- depth: 8;
- zero bias;
- He-Gaussian row weights;
- seed: `164032`;
- deterministic antithetic sphere reference;
- sample count: `32768`;
- reference seed: `164320`.

### F2 — adversarial16

- width/input: 16;
- depth: 8;
- zero bias;
- seed: `164016`;
- each layer:
  `W=Q_L diag(g) Q_R^T`;
- `Q_L,Q_R`: deterministic canonicalized QR factors;
- `g`: frozen linearly spaced vector on `[0.5,1.5]`, RMS-rescaled to
  `sqrt(2)`, cyclically shifted by layer;
- deterministic antithetic sphere reference;
- sample count: `32768`;
- reference seed: `164160`.

## 5. Mandatory candidate-before-reference ordering

Within the sole run:

1. generate frozen weights;
2. run parent;
3. run AGO;
4. replay parent and AGO;
5. freeze state hashes and cost receipt;
6. only then import/materialize verifier references;
7. evaluate identities/MSE;
8. emit one result JSON.

The candidate module must not import the verifier module.

## 6. Gauge and homogeneity gates

All must pass.

### Algebraic round trip

For the candidate first state:

`G -> A -> G`

relative Frobenius error for both mean and covariance:

`<=2e-12`.

### Exact2D first-state identity

Using the verifier's analytic first-activation angular K1/K2:

- reconstruct the corresponding Gaussian K1/K2 via exact radial moments;
- apply the frozen gauge map;
- recover analytic angular K1/K2.

Maximum relative error:

`<=2e-12`.

### Positive homogeneity

For frozen verifier rays/scales on every fixture:

`||F(sY)-sF(Y)||_F / ||sF(Y)||_F <=2e-12`.

## 7. Parent-vs-AGO scientific gate

For each fixture:

`MSE_parent = mean((mu_parent-mu_ref)^2)`

`MSE_AGO = mean((mu_AGO-mu_ref)^2)`.

Mandatory individual gate:

`MSE_AGO < MSE_parent`

on F0, F1, and F2.

Additionally define pooled squared error by concatenating the final mean
coordinates of all three fixtures.

Mandatory pooled gate:

`MSE_AGO_pooled <= 0.98 * MSE_parent_pooled`.

If any parent MSE is numerically zero, nonfinite, or the ratio is unevaluable,
E164 fails.

No fixture averaging can rescue an individual regression.

## 8. Reference stability

For F1/F2 split the deterministic 32768 sphere samples into four equal
contiguous batches.

Let `SE_ref` be RMS standard error of the four final Gaussian-mean batch
estimates.

Require either:

`SE_ref <= 0.20 * min(RMSE_parent, RMSE_AGO)`

or

`SE_ref <= 1e-4`.

If the sole reference is too noisy, E164 fails; sample count cannot be changed.

## 9. Deterministic replay

Parent and AGO replay must be bitwise identical for:

- final mean;
- every layer mean;
- every layer covariance;
- AGO first angular gauge state;
- production cost receipt.

## 10. Complete production cost upper

Production shape:

- `n=1024`;
- `L=16`;
- full covariance;
- no Strassen;
- no higher-order cumulant state.

Budget:

`B=2^41=2,199,023,255,552 FLOPs`.

Cap:

`floor(0.135B)=296,868,139,499 FLOPs`.

### A. Full covariance transport

Two square GEMMs per layer:

`16 * 4 n^3 = 68,719,476,736`.

### B. Mean matvec

`16 * 2 n^2 = 33,554,432`.

### C. K2 nonlinear arithmetic

Conservative:

`16 * 24 n^2 = 402,653,184`.

### D. CDF/PDF/Wick scalar work

Conservative:

`16 * 1024 n = 16,777,216`.

### E. Parent helper/accounting reserve

Twenty `2n^3` units:

`42,949,672,960`.

### F. AGO overlay

`8n^2 + 64Ln = 9,437,184`.

### Total

`112,131,571,712 FLOPs`.

Utilization:

`0.05099153518676758 B`.

Slack to cap:

`184,736,567,787 FLOPs`.

Pre-run cost gate: **PASS**.

Any runtime operation class outside this ledger must fit in the helper reserve
or the cost gate fails.

## 11. Standalone execution contract

E164 must not run `pip install -e .` and must not require `setup.py` or
`pyproject.toml`.

The workflow may:

- use `actions/setup-python`;
- install explicit runtime/test packages directly (numpy, pytest);
- set `PYTHONPATH=.`;
- execute `python -m pytest ...`;
- execute the falsifier directly from repository root.

Workflow is created only after protocol/candidate/reference/tests/falsifier
blobs are frozen.

Arm commit must modify only `research/E164_RUN_ARM.json`.

## 12. One-run terminal policy

Exactly one external run is authorized.

If any mandatory gate fails, is skipped, or is unevaluable:

**E164 TERMINAL NO-GO / CLOSE AGO.**

No workflow repair, rerun, new seed, threshold change, sample increase, closure
change, or rescue under E164.

If every gate passes:

**E164 TARGET-FREE SCIENTIFIC GO — AGO.**

Even GO does not authorize public/scorer/holdout/full/submission execution.

No canonical or ledger mutation.
