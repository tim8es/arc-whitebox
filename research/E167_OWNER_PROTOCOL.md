# E167 OWNER PROTOCOL — pre-certified production-shaped AGO reference

Date: 2026-09-21

Status: **PROTOCOL FROZEN / ONE SYNTHETIC OWNER RUN AUTHORIZED**

Branch:

`research/e167-precertified-reference-ago-20260921`

Scientific parent:

`research/e164-cleanroom-ago-20260921@342f2ab03ad5251971b17f8d8d43c1861774cbb6`

Independent E165 verifier receipt:

`review/e165-e164-independent-verifier-20260921`
with decision
`E165_INDEPENDENT_VERIFIER_GO_E164_CLEANROOM_AGO`.

Idempotency key:

`ARC-E167-PRECERTIFIED-REFERENCE-AGO-20260921`

## 1. Purpose

E166 is sealed and must not be rerun.

E166 observed a positive synthetic production-shaped AGO signal at width 1024,
depth 16:

`MSE_AGO/MSE_parent = 0.9323073271`

but failed its preregistered reference standard-error gate by a factor of about
3.68.

E167 addresses only the reference-design failure.

The AGO estimator is unchanged from E164.

No E166 estimator code, workflow, falsifier, receipt arithmetic, or runtime
artifact is reused.

## 2. Frozen AGO implementation

Candidate file:

`methods/e164_ago.py`

blob:

`ea9078eccc2e2bf2a2bea499ef10a4daf80ea0d4`

runtime source SHA256:

`533149d0a1c05be12097b997b8762270b299c574cf6c32324de7d17ec285169c`.

Mechanism remains exactly:

1. full-covariance K2 parent;
2. exact Gaussian-to-angular K1/K2 gauge after the first activation only;
3. identical K2 closure for all later layers;
4. exact final radial `a1(n)` mean readout.

No K4/D4/D22/c4, no recurrent higher-order state, no Strassen.

## 3. Synthetic production-shaped fixture

Exactly one network:

- width/input `n=1024`;
- depth `16`;
- zero bias;
- row-weight He-Gaussian matrices;
- NumPy PCG64 seed `1671024`;
- float64;
- no alternate seed;
- no sweep.

Weights:

`W_l,ij ~ N(0, 2/n)`.

## 4. A-priori reference budget

Reference distribution is the exact angular distribution:

uniform on the radius-`sqrt(1024)` sphere.

Reference Gaussian mean is reconstructed exactly as

`mu_ref = a1(1024) E[F(Y)]`.

Frozen reference budget:

- total antithetic angular samples: `196608`;
- reference RNG seed: `167196608`;
- 48 contiguous batches;
- 4096 samples per batch;
- antithetic pairs remain within each batch;
- streaming chunk size: `4096`;
- no sample-count adaptation;
- no rerun.

This is 24 times the E166 reference sample budget.

Under ordinary Monte-Carlo `1/sqrt(N)` scaling this would reduce the E166
observed standard error by `sqrt(24) ~= 4.899`, which is larger than the
reported 3.68-fold shortfall.

That scaling argument is **design motivation only**. It is not itself a GO
criterion.

## 5. Reference must certify before AGO candidate runs

Within the sole E167 workflow the order is frozen:

1. generate and hash synthetic weights;
2. run the Gaussian K2 parent;
3. replay and freeze the parent;
4. generate the entire frozen streaming angular reference;
5. compute reference mean and 48 batch means;
6. compute reference standard error and parent RMSE;
7. apply the pre-candidate reference-certification gates below;
8. **only if every pre-candidate gate passes**, execute AGO;
9. replay AGO;
10. freeze AGO state;
11. compute parent-vs-AGO MSE and batch significance;
12. reconcile cost and write the receipt payload.

If a pre-candidate reference gate fails, AGO must not be evaluated and the
single run becomes terminal E167 NO-GO.

This ordering prevents the candidate result from influencing reference sample
count or acceptance.

## 6. Pre-candidate reference-certification gates

Let `m_b` be the 48 batch Gaussian-input mean estimates.

Coordinatewise reference standard error is

`SE_j = std_b(m_b,j)/sqrt(48)`.

Define

`SE_ref = sqrt(mean_j(SE_j^2))`.

Let

`RMSE_parent = sqrt(mean((mu_parent-mu_ref)^2))`.

Both must pass before AGO evaluation:

### Gate R1 — absolute precision

`SE_ref <= 7.0e-4`.

### Gate R2 — parent-relative precision

`SE_ref <= 0.20 * RMSE_parent`.

These thresholds are frozen before any E167 candidate output exists.

If either fails, E167 stops before AGO evaluation.

## 7. Candidate scientific gates

After reference pre-certification, run the unchanged AGO candidate.

Define:

`MSE_parent = mean((mu_parent-mu_ref)^2)`

`MSE_AGO = mean((mu_AGO-mu_ref)^2)`

`rho = MSE_AGO/MSE_parent`.

Mandatory aggregate gate:

`rho <= 0.98`.

### Post-candidate reference gate

Require

`SE_ref <= 0.20 * min(RMSE_parent, RMSE_AGO)`.

### Batch paired-difference gate

For each of the 48 frozen batch references:

`Delta_b = MSE_parent,b - MSE_AGO,b`.

Require:

1. `Delta_b>0` in at least 36 of 48 batches;
2. `mean(Delta_b) > 3 * SE(Delta_b)`.

No post-result replacement of these gates is allowed.

## 8. Mechanism identities

Mandatory:

- AGO gauge round-trip relative error <= `2e-12`;
- positive-homogeneity spot-check relative error <= `2e-12`;
- candidate source SHA equals the frozen E164 source SHA;
- candidate imports no reference module;
- no benchmark/public/scorer I/O.

## 9. Deterministic replay

Parent replay must be bitwise exact before reference generation.

AGO replay must be bitwise exact after reference pre-certification.

Replay includes:

- final mean;
- every layer mean;
- every layer covariance;
- first angular gauge state;
- estimator cost receipt.

## 10. Candidate production cost

The deployed candidate arithmetic remains the fully reconciled E164 ledger:

- covariance linear transport: `68,719,476,736`;
- mean matvec: `33,554,432`;
- nonlinear second-order arithmetic: `402,653,184`;
- normal scalar work: `16,777,216`;
- helper/accounting reserve: `42,949,672,960`;
- angular gauge overlay: `9,437,184`.

All-in:

`112,131,571,712 FLOPs`.

Budget:

`B=2^41=2,199,023,255,552`.

Cap:

`296,868,139,499 FLOPs = 0.135B`.

Utilization:

`0.05099153518676758 B`.

Slack:

`184,736,567,787 FLOPs`.

Candidate-cost gate is independent of the synthetic reference computation.

## 11. Reference-only test cost

The large reference is verifier/test work and is not deployed estimator cost.

For transparency, charge its dominant dense evaluation upper separately.

Each of 196608 samples crosses 16 dense 1024x1024 layers:

`C_ref_dense
 = 196608 * 16 * 2 * 1024^2
 = 6,597,069,766,656 FLOPs`.

This reference-test bill is intentionally separate from the candidate
production cap.

Streaming is mandatory so the workflow never materializes the full
196608x1024 trajectory.

## 12. Standalone execution

No editable repository installation.

Workflow must:

- use `actions/setup-python`;
- install explicit NumPy/PyTest versions;
- set `PYTHONPATH=.`;
- run frozen E164 tests;
- run one E167 script;
- use one BLAS thread;
- upload one immutable artifact.

## 13. Public firewall

E167 is synthetic-only.

No public target, benchmark weights, public-mini, official scorer, holdout,
full suite, or submission may be accessed.

E165 verified E164, but E167 production-shaped evidence itself must receive a
separate independent verifier GO before any later public/benchmark owner could
be authorized.

E167 GO alone does not authorize public work.

## 14. One-run terminal policy

Exactly one external E167 owner run.

Any failed/skipped/unevaluable mandatory gate:

**E167 TERMINAL NO-GO.**

No sample increase, threshold change, rerun, seed change, rescue, or E166 rerun.

All gates pass:

**E167 SYNTHETIC PRODUCTION-SHAPED OWNER GO — AGO WITH PRE-CERTIFIED REFERENCE.**

No canonical or ledger mutation.
