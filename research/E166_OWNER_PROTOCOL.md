# E166 OWNER PROTOCOL — synthetic production-shaped AGO transfer

Date: 2026-09-21

Status: **PROTOCOL FROZEN / ONE SYNTHETIC OWNER RUN AUTHORIZED**

Branch:

`research/e166-production-shaped-ago-20260921`

Parent scientific receipt:

`research/e164-cleanroom-ago-20260921@342f2ab03ad5251971b17f8d8d43c1861774cbb6`

Idempotency key:

`ARC-E166-PRODUCTION-SHAPED-AGO-20260921`

## 1. Scope

E166 is a synthetic production-shaped transfer test of the already frozen E164
AGO mechanism.

The candidate implementation is unchanged:

`methods/e164_ago.py`

frozen blob:

`ea9078eccc2e2bf2a2bea499ef10a4daf80ea0d4`.

Candidate delta remains exactly:

1. compute first activation with the same full-covariance K2 parent;
2. apply exact K1/K2 Gaussian-to-angular gauge once after that first activation;
3. propagate the same K2 closure for the remaining layers;
4. apply exact final radial `a1(n)` mean readout.

No K4/D4/D22/c4, no Strassen, no target fitting, no closure change.

## 2. Public-data firewall

E166 is synthetic only.

Forbidden in this owner:

- public benchmark weights;
- public target means;
- public-mini targets;
- scorer;
- holdout;
- full suite;
- submission;
- tuning against any benchmark result.

Even an E166 GO does **not** authorize public execution.

Public/benchmark work remains forbidden until a separate E165 independent
verifier has explicitly issued GO and a later owner protocol authorizes it.

## 3. Production-shaped synthetic fixture

Exactly one fixture:

- width/input: `1024`;
- depth: `16`;
- zero bias;
- row-weight matrices;
- deterministic He-Gaussian weights;
- network seed: `1661024`;
- float64.

Weight generation:

`W_l,ij ~ N(0, 2/n)`

from NumPy PCG64 with the frozen seed and no seed search.

No adversarial alternative, no second network, no sweep.

## 4. Target-free reference

Reference uses the exact radial/angular identity and deterministic sphere
sampling.

- angular reference distribution: uniform sphere of radius `sqrt(1024)`;
- deterministic antithetic Gaussian-normalized directions;
- total samples: `8192`;
- reference seed: `1668192`;
- eight contiguous equal batches of `1024` samples each.

For each sample direction `Y`, evaluate the exact zero-bias network.

Reference Gaussian-input final mean:

`mu_ref = a1(1024) * mean(F(Y))`.

This is target-free synthetic Monte Carlo and is used only after parent/AGO
outputs and hashes are frozen.

## 5. Candidate-before-reference ordering

Mandatory:

1. construct the frozen synthetic weights;
2. run parent;
3. run AGO;
4. replay parent;
5. replay AGO;
6. freeze final/state hashes and cost receipt;
7. only then import/materialize the sphere reference;
8. compute MSE and stability diagnostics;
9. emit one immutable result JSON.

The estimator module must not import the reference module.

## 6. Scientific metrics

`MSE_parent = mean((mu_parent-mu_ref)^2)`

`MSE_AGO = mean((mu_AGO-mu_ref)^2)`

Primary transfer ratio:

`rho = MSE_AGO / MSE_parent`.

Mandatory scientific gate:

`rho <= 0.98`.

A ratio that is nonfinite or has zero denominator fails.

## 7. Reference-stability gates

Let the eight batch reference means be `m_b`.

### 7.1 Mean-reference standard error

Compute coordinatewise standard error across the eight batch means and then its
RMS:

`SE_ref`.

Require

`SE_ref <= 0.20 * min(RMSE_parent, RMSE_AGO)`

or absolute

`SE_ref <= 1e-4`.

### 7.2 Batch transfer consistency

For each batch reference mean compute:

`Delta_b = MSE_parent,b - MSE_AGO,b`.

Require both:

- AGO improves at least `6/8` batch references;
- mean(`Delta_b`) > `2 * SE(Delta_b)`.

This prevents a noisy single aggregate reference from creating the GO.

No sample-count increase is allowed after the run.

## 8. Deterministic replay

Parent and AGO must replay bitwise exactly for:

- final mean;
- every layer mean;
- every layer covariance;
- AGO first angular state;
- production cost receipt.

## 9. Mechanism integrity

Mandatory:

- exact gauge round-trip error <= `2e-12`;
- positive-homogeneity spot check <= `2e-12`;
- candidate source blob remains the E164 frozen blob;
- no public/scorer/holdout/submission imports or I/O;
- no K4/D4/D22/c4/Strassen state.

## 10. Complete production all-in cost

Production shape is exactly the E166 fixture:

- `n=1024`;
- `L=16`.

Frozen estimator all-in upper:

### A. covariance linear transport

`68,719,476,736 FLOPs`

### B. mean matvec

`33,554,432 FLOPs`

### C. second-order nonlinear arithmetic

`402,653,184 FLOPs`

### D. normal CDF/PDF/Wick scalar work

`16,777,216 FLOPs`

### E. general helper/accounting reserve

`42,949,672,960 FLOPs`

### F. AGO gauge overlay

`9,437,184 FLOPs`

### Total

`112,131,571,712 FLOPs`

Budget:

`B=2^41=2,199,023,255,552 FLOPs`.

Cap:

`floor(0.135B)=296,868,139,499 FLOPs`.

Utilization:

`0.05099153518676758 B`.

Slack:

`184,736,567,787 FLOPs`.

The synthetic reference is verifier/test work and is not part of the deployed
estimator arithmetic. The estimator cost receipt must independently reconcile
to the complete production ledger above.

## 11. Standalone execution

No editable repository install.

Workflow must:

- use `actions/setup-python`;
- directly install frozen NumPy/PyTest versions;
- set `PYTHONPATH=.`;
- use the frozen E164 estimator blob;
- execute exactly one E166 production-shaped owner run.

## 12. Mandatory GO gates

All must pass:

1. frozen E164 candidate blob identity;
2. source/public firewall;
3. finite parent/AGO/reference;
4. parent bitwise replay;
5. AGO bitwise replay;
6. gauge round-trip <= `2e-12`;
7. homogeneity <= `2e-12`;
8. reference standard-error gate;
9. AGO improves >=6/8 batch references;
10. batch improvement mean >2 SE;
11. aggregate AGO/parent MSE ratio <= `0.98`;
12. independent all-in production cost reconciliation;
13. production cost <= `0.135B`;
14. exactly one external owner run;
15. no sweep/rescue/rerun;
16. no public/benchmark/scorer/holdout/full/submission access.

Any failed, skipped, or unevaluable mandatory gate:

**E166 TERMINAL NO-GO.**

All pass:

**E166 SYNTHETIC PRODUCTION-SHAPED OWNER GO — AGO.**

This GO remains synthetic-only pending E165 verifier GO and a separately
authorized later public protocol.

No canonical or ledger mutation.
