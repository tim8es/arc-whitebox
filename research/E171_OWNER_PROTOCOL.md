# E171 OWNER PROTOCOL — verifier-ready multi-seed production-shaped AGO

Date: 2026-09-21

Status: **PROTOCOL FROZEN / ONE SYNTHETIC OWNER RUN AUTHORIZED**

Branch:

`research/e171-verifier-ready-ago-20260921`

Scientific parent:

`research/e164-cleanroom-ago-20260921@342f2ab03ad5251971b17f8d8d43c1861774cbb6`

E170 verifier finding motivating E171:

`E170_INDEPENDENT_VERIFIER_UNEVALUATED_E169_NUMERIC_RECOMPUTATION_EVIDENCE_INCOMPLETE`.

Idempotency key:

`ARC-E171-VERIFIER-READY-MULTISEED-AGO-20260921`

## 1. Purpose

E171 is not an E169 rerun and must not use E169's frozen weight/reference seeds.

It tests the same byte-identical AGO mechanism on a new preregistered
production-shaped synthetic panel, while retaining all numeric vectors required
for a later independent verifier to recompute:

- absolute reference standard error;
- parent final-mean MSE;
- AGO final-mean MSE;
- per-batch parent-vs-AGO MSE deltas;
- panel aggregate statistics.

The evidence gap identified by E170 is therefore closed by construction.

## 2. Frozen AGO implementation

Candidate:

`methods/e164_ago.py`

required git blob:

`ea9078eccc2e2bf2a2bea499ef10a4daf80ea0d4`

required runtime source SHA256:

`533149d0a1c05be12097b997b8762270b299c574cf6c32324de7d17ec285169c`.

Mechanism remains exactly:

1. full-covariance K2 parent;
2. exact Gaussian-to-angular K1/K2 gauge once after the first activation;
3. identical K2 closure thereafter;
4. exact final radial `a1(n)` readout.

Forbidden:

- K4;
- D4;
- D22;
- scalar c4;
- recurrent higher-order state;
- Strassen;
- target fitting;
- closure modification.

## 3. Frozen production-shaped panel

Three independent synthetic zero-bias networks.

Common shape:

- width/input `n=1024`;
- depth `16`;
- float64;
- row-weight matrices;
- He-Gaussian weights `N(0,2/n)`.

Frozen weight seeds:

1. `1711024`
2. `1712024`
3. `1713024`

No alternate or replacement seed is allowed.

## 4. Frozen angular reference design

Per network:

- uniform radius-`sqrt(1024)` sphere directions;
- antithetic generation;
- total samples: `196608`;
- batches: `48`;
- samples per batch: `4096`;
- antithetic pairs stay inside each batch;
- streaming evaluation only;
- exact radial multiplication by `a1(1024)`.

Frozen reference seeds:

1. weight seed `1711024` -> reference seed `171196608`
2. weight seed `1712024` -> reference seed `171296608`
3. weight seed `1713024` -> reference seed `171396608`.

No adaptive reference budget.

## 5. Absolute reference-SE gate

For each network, let the 48 Gaussian-input batch reference means be

`R[b,j]`, shape `48 x 1024`.

Coordinatewise standard-error vector:

`SE[j] = std_b(R[:,j], ddof=1) / sqrt(48)`.

RMS reference SE:

`SE_ref = sqrt(mean_j(SE[j]^2))`.

Mandatory for every seed:

`SE_ref <= 7.0e-4`.

No parent-relative or candidate-relative SE gate exists in E171.

## 6. Mandatory verifier-ready immutable numeric payloads

Before a GO or NO-GO receipt can be written, the sole run must materialize and
upload, for each of the three seeds, the following float64 `.npy` arrays.

All vectors are Gaussian-input output means after exact radial scaling where
applicable.

### 6.1 Final vectors

- `parent_final_mean.npy`, shape `[1024]`;
- `ago_final_mean.npy`, shape `[1024]`;
- `reference_final_mean.npy`, shape `[1024]`.

### 6.2 Per-batch mean vectors

- `reference_batch_means.npy`, shape `[48,1024]`;
- `parent_batch_means.npy`, shape `[48,1024]`, each row equal to the frozen
  parent final mean;
- `ago_batch_means.npy`, shape `[48,1024]`, each row equal to the frozen AGO
  final mean.

The repeated parent/AGO arrays are mandatory even though they are redundant.
They make the later verifier's batch-MSE recomputation self-contained and
literal.

### 6.3 Per-batch error vectors

- `parent_batch_errors.npy = parent_batch_means-reference_batch_means`,
  shape `[48,1024]`;
- `ago_batch_errors.npy = ago_batch_means-reference_batch_means`,
  shape `[48,1024]`.

### 6.4 Reference precision payload

- `reference_coordinate_se.npy`, shape `[1024]`.

### 6.5 Mandatory manifest

For every persisted array, save in the immutable result/manifest:

- relative path;
- dtype;
- shape;
- byte count;
- SHA256 of the exact file bytes;
- SHA256 of the raw contiguous array bytes.

Also retain:

- per-seed weight SHA256;
- parent/AGO state hashes;
- reference final-mean raw-array hash.

The owner receipt may be committed only after the workflow artifact containing
all these files has successfully uploaded and its artifact digest is known.

If any required payload is missing or hash/shape validation fails, E171 is
terminal NO-GO.

## 7. Candidate/reference ordering

For each seed:

1. generate and hash frozen weights;
2. execute parent;
3. execute AGO;
4. execute parent replay;
5. execute AGO replay;
6. freeze parent/AGO state hashes;
7. only then stream the angular reference;
8. materialize all mandatory verifier-ready numeric arrays;
9. hash and validate every payload;
10. compute scientific metrics only from the same arrays that are persisted.

Candidate code may not import the E171 reference module.

## 8. Per-seed scientific gates

From the persisted final vectors:

`MSE_parent,s = mean((P_s-R_s)^2)`

`MSE_AGO,s = mean((A_s-R_s)^2)`

`rho_s = MSE_AGO,s/MSE_parent,s`.

Mandatory:

1. AGO strictly improves all three seeds:
   `MSE_AGO,s < MSE_parent,s`;
2. at least two of three seeds satisfy
   `rho_s <= 0.98`.

Nonfinite or zero parent MSE fails.

## 9. Pooled panel gate

Concatenate the three persisted 1024-coordinate parent error vectors and the
three persisted AGO error vectors.

Mandatory:

`rho_panel = pooled_MSE_AGO/pooled_MSE_parent <= 0.98`.

## 10. Independent paired batch-level improvement test

For each of 144 persisted batch pairs:

`Delta_(s,b)
 = mean(parent_batch_errors[s,b,:]^2)
 - mean(ago_batch_errors[s,b,:]^2)`.

Mandatory:

1. at least `96/144` deltas positive;
2. `mean(Delta)>0`;
3. `mean(Delta) > 3*SE(Delta)`,
   where
   `SE(Delta)=std(Delta,ddof=1)/sqrt(144)`;
4. within every seed separately,
   `mean_b Delta_(s,b)>0`.

The later independent verifier must be able to reproduce this test from the
uploaded error arrays alone.

## 11. Exact identities

All three seeds must pass:

### 11.1 Gauge round trip

At first AGO state:

`G -> A -> G`

maximum relative mean/covariance error:

`<=2e-12`.

### 11.2 Positive homogeneity

64 frozen synthetic sphere rays per seed:

`||F(cY)-cF(Y)||_F / ||cF(Y)||_F <=2e-12`.

### 11.3 Radial readout

`a1(1024)
 = sqrt(2/1024) Gamma(1025/2)/Gamma(1024/2)
 = 0.9997558892135413`

within `1e-15`.

Candidate final AGO mean must equal

`a1(1024) * final_angular_state_mean`

to relative error `<=2e-12`.

## 12. Deterministic replay

Parent and AGO must replay bitwise exactly for every seed:

- final mean;
- all layer means;
- all layer covariance matrices;
- first angular gauge state;
- production cost receipt.

Reference generation is deterministic from its frozen seed; the persisted
reference payload hashes are the immutable replay target for the later
verifier. E171 itself does not run a second reference execution.

## 13. Complete candidate production cost

Unchanged E164 deployed estimator ledger:

- covariance linear transport: `68,719,476,736`;
- mean matvec: `33,554,432`;
- nonlinear second-order arithmetic: `402,653,184`;
- normal/Wick scalar work: `16,777,216`;
- helper/accounting reserve: `42,949,672,960`;
- angular gauge overlay: `9,437,184`.

All-in:

`112,131,571,712 FLOPs`.

Budget:

`B=2^41=2,199,023,255,552 FLOPs`.

Cap:

`296,868,139,499 FLOPs = 0.135B`.

Utilization:

`0.05099153518676758 B`.

Slack:

`184,736,567,787 FLOPs`.

Independent formula reconciliation is mandatory.

## 14. Reference research cost

Per-seed dense reference upper:

`6,597,069,766,656 FLOPs`.

Three-seed reference upper:

`19,791,209,299,968 FLOPs`.

This is research/reference work, explicitly separate from deployed candidate
cost.

## 15. Standalone execution

No editable repository install.

Workflow must:

- use `actions/setup-python`;
- install pinned NumPy/PyTest directly;
- set `PYTHONPATH=.`;
- set one BLAS/OpenMP thread;
- run E164 mechanism tests;
- run E171 reference/payload tests;
- execute exactly one E171 owner script;
- upload result JSON, manifest JSON, and all mandatory `.npy` payload files;
- use one immutable artifact.

The artifact upload step is mandatory even when scientific gates fail.

## 16. Public firewall

E171 is synthetic and target-free only.

Forbidden:

- public target;
- public benchmark weights;
- public-mini;
- official scorer;
- holdout;
- full suite;
- submission;
- benchmark tuning.

E171 GO does not authorize public work.

A separate independent E171 verifier must recompute the retained numeric
evidence and issue GO before any later public/benchmark owner protocol.

## 17. One-run terminal policy

Exactly one external E171 owner run.

Any failed/skipped/unevaluable mandatory gate, including evidence-payload
completeness/hash failure:

**E171 TERMINAL NO-GO.**

Forbidden after result:

- rerun;
- sample increase;
- threshold change;
- seed replacement;
- batch-rule change;
- evidence regeneration;
- rescue;
- E169 rerun.

All gates pass:

**E171 SYNTHETIC VERIFIER-READY MULTI-SEED PRODUCTION-SHAPED OWNER GO — AGO.**

No canonical or ledger mutation.
