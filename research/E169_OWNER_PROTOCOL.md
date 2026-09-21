# E169 OWNER PROTOCOL — multi-seed production-shaped AGO with absolute reference precision

Date: 2026-09-21

Status: **PROTOCOL FROZEN / ONE SYNTHETIC OWNER RUN AUTHORIZED**

Branch:

`research/e169-multiseed-ago-20260921`

Scientific parent:

`research/e164-cleanroom-ago-20260921@342f2ab03ad5251971b17f8d8d43c1861774cbb6`

Independent mechanism verifier:

`E165_INDEPENDENT_VERIFIER_GO_E164_CLEANROOM_AGO`.

Idempotency key:

`ARC-E169-MULTISEED-PRODUCTION-AGO-20260921`

## 1. Purpose

E164/E165 established AGO on frozen exact-small synthetic fixtures.

E166 observed a positive production-shaped signal:

`MSE_AGO/MSE_parent = 0.9323073271`

but failed only its parent-relative reference-SE gate.

E167 is sealed and must not be rerun. It improved absolute reference precision
more than fivefold, but its new seed had a smaller parent error, making the
parent-relative `0.20*RMSE_parent` gate stricter before candidate evaluation.

E169 removes that seed-dependent gate by preregistration, not post-hoc.

Reference quality is judged only by an absolute precision requirement frozen
before the run:

`SE_ref <= 7e-4`

for every synthetic network.

Scientific evidence is judged separately by paired batch-level AGO-vs-parent
improvement tests and aggregate MSE ratios.

## 2. Frozen AGO mechanism

AGO remains byte-identical to E164.

Candidate:

`methods/e164_ago.py`

blob:

`ea9078eccc2e2bf2a2bea499ef10a4daf80ea0d4`

runtime source SHA256:

`533149d0a1c05be12097b997b8762270b299c574cf6c32324de7d17ec285169c`.

Mechanism:

1. full-covariance K2 parent;
2. exact Gaussian-to-angular K1/K2 gauge once, immediately after the first
   activation state;
3. identical K2 closure for all later layers;
4. exact final radial `a1(n)` readout.

No K4/D4/D22/c4, no recurrent higher-order state, no Strassen, no target fit.

## 3. Frozen production-shaped network panel

Three independent synthetic zero-bias networks.

Common shape:

- width/input: `1024`;
- depth: `16`;
- row-weight matrices;
- float64;
- He-Gaussian weights `N(0,2/n)`.

Frozen weight seeds:

1. `1691024`
2. `1692024`
3. `1693024`

No additional seed may be added or substituted.

## 4. Frozen reference design

Each network gets an independent target-free angular reference.

Per network:

- antithetic sphere samples: `196608`;
- 48 batches;
- 4096 samples per batch;
- antithetic pairs remain inside each batch;
- streaming evaluation only;
- exact final radial scaling by `a1(1024)`.

Frozen reference seeds:

1. network `1691024` -> reference seed `169196608`
2. network `1692024` -> reference seed `169296608`
3. network `1693024` -> reference seed `169396608`.

No adaptive sample count.

## 5. Absolute reference-quality gate

For each network, let the 48 batch final Gaussian-mean estimates be `m_b`.

Coordinatewise standard error:

`SE_j = std_b(m_b,j)/sqrt(48)`.

RMS reference standard error:

`SE_ref = sqrt(mean_j(SE_j^2))`.

Mandatory gate, independently for all three seeds:

`SE_ref <= 7.0e-4`.

There is **no parent-relative or candidate-relative reference-SE gate** in E169.

The threshold is frozen before the run.

## 6. Candidate/reference ordering

For each seed, in frozen order:

1. generate weights;
2. run parent;
3. run AGO;
4. replay parent;
5. replay AGO;
6. freeze candidate and parent hashes;
7. only then stream the independent angular reference;
8. compute reference absolute SE;
9. compute parent-vs-AGO final-mean MSE;
10. compute batch-level paired deltas.

This keeps the candidate isolated from reference values while avoiding any
post-reference change to sample count or gates.

Candidate code may not import the reference module.

## 7. Per-seed scientific metrics

For seed `s`:

`MSE_parent,s = mean((mu_parent,s - mu_ref,s)^2)`

`MSE_AGO,s = mean((mu_AGO,s - mu_ref,s)^2)`

`rho_s = MSE_AGO,s / MSE_parent,s`.

Mandatory per-seed gates:

1. `MSE_AGO,s < MSE_parent,s` for all 3 seeds;
2. at least 2 of the 3 seeds satisfy `rho_s <= 0.98`.

A zero/nonfinite parent MSE fails that seed.

## 8. Panel aggregate gate

Concatenate all 3072 output-coordinate error vectors across the three seeds.

Define panel MSEs from the concatenated errors.

Mandatory:

`rho_panel = MSE_AGO,panel / MSE_parent,panel <= 0.98`.

## 9. Independent paired batch-level improvement test

This gate is frozen before the run and is separate from reference SE.

For each network and each of its 48 frozen reference batches:

`Delta_(s,b)
 = MSE_parent,(s,b) - MSE_AGO,(s,b)`.

There are exactly 144 paired deltas.

Mandatory panel batch gates:

1. at least `96/144` deltas are positive;
2. the mean of all 144 deltas is positive;
3. `mean(Delta) > 3 * SE(Delta)`, where
   `SE(Delta)=std(Delta,ddof=1)/sqrt(144)`.

Additional seed-stratified guard:

For every one of the three seeds,

`mean_b Delta_(s,b) > 0`.

This prevents one seed with a large positive effect from hiding a systematic
negative effect on another seed.

No batch gate can be changed after results exist.

## 10. Exact mechanism identities

All must pass independently on all three networks:

### Gauge round trip

At the first AGO state:

`G -> A -> G`

maximum relative mean/covariance error:

`<= 2e-12`.

### Positive homogeneity

On 64 frozen synthetic sphere rays per network:

`||F(cY)-cF(Y)||_F / ||cF(Y)||_F <= 2e-12`

for positive frozen scales.

### Radial identity

The implementation must retain

`a1(n)=sqrt(2/n) Gamma((n+1)/2)/Gamma(n/2)`

and final readout exactly

`mu_G,out = a1(n) mu_A,out`.

Candidate source SHA must match the frozen E164 source SHA.

## 11. Deterministic replay

Parent and AGO replay must be bitwise exact for every seed:

- final mean;
- all 16 layer means;
- all 16 layer covariance matrices;
- first AGO angular state;
- production cost receipt.

Weight generation must also reproduce byte-identical SHA256 for the frozen seed
within the sole workflow.

## 12. Candidate production cost

Deployed estimator cost is unchanged from E164.

### A. Covariance linear transport

`68,719,476,736 FLOPs`

### B. Mean matvec

`33,554,432 FLOPs`

### C. Nonlinear second-order arithmetic

`402,653,184 FLOPs`

### D. Normal/Wick scalar work

`16,777,216 FLOPs`

### E. Helper/accounting reserve

`42,949,672,960 FLOPs`

### F. Angular gauge overlay

`9,437,184 FLOPs`

### Complete candidate all-in

`112,131,571,712 FLOPs`

Budget:

`B=2^41=2,199,023,255,552 FLOPs`.

Cap:

`296,868,139,499 FLOPs = 0.135B`.

Utilization:

`0.05099153518676758 B`.

Slack:

`184,736,567,787 FLOPs`.

The candidate production cost is per estimator execution and does not multiply
by the number of synthetic research seeds.

## 13. Reference-only research cost

Per seed dominant dense reference upper:

`196608 * 16 * 2 * 1024^2
 = 6,597,069,766,656 FLOPs`.

Three-seed reference upper:

`19,791,209,299,968 FLOPs`.

This is research/verifier cost, not deployed candidate arithmetic.

It is reported separately and does not count against the `0.135B` candidate
cap.

## 14. Standalone execution

No editable install.

Workflow must:

- use `actions/setup-python`;
- install pinned NumPy/PyTest directly;
- set `PYTHONPATH=.`;
- set one BLAS/OpenMP thread;
- run E164 mechanism tests;
- run E169 reference tests;
- execute one E169 owner script;
- stream all references;
- upload one immutable artifact.

## 15. Public firewall

E169 is synthetic only.

Forbidden:

- public targets;
- public benchmark weights;
- public-mini;
- official scorer;
- holdout;
- full suite;
- submission;
- benchmark tuning.

Even E169 GO does not authorize public work.

A separate independent verifier must verify E169 production-shaped evidence
before any later public/benchmark owner protocol.

## 16. One-run terminal policy

Exactly one external owner run.

Any failed, skipped, or unevaluable mandatory gate:

**E169 TERMINAL NO-GO.**

No sample increase, reference-threshold change, seed replacement, batch-rule
change, rerun, rescue, or E167 rerun.

All gates pass:

**E169 SYNTHETIC MULTI-SEED PRODUCTION-SHAPED OWNER GO — AGO.**

No canonical or ledger mutation.
