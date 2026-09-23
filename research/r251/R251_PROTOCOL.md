# R251 frozen protocol — V25-GFNP Gaussian fixed-point null projection

Status: FROZEN BEFORE MEASUREMENT
Run ID: `R251-global-accuracy-full-history-method-20260923`

## 1. Motivation and evidence boundary

R231 shows V25 mini-100 raw error is diffuse, compute-only improvement cannot reach the cited numerical orientation at fixed raw MSE, and a global-accuracy method is the appropriate research direction. R230 found no public method disclosure for leading submissions, so no leader method is inferred.

Full immutable history was deduplicated from:
- `research/history.json`, blob `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`, 194 experiment IDs;
- `research/legacy-ledger.csv`, blob `040e52efe01efd7280180b7e2d72901b4c2f0532`.

Required evidence read: R231, R232, R238, R239, R245, R249, R250. R223/R244 candidate outputs/artifacts are excluded and will not be inspected.

## 2. Exactly one candidate family

**V25-GFNP — Gaussian Fixed-point Null Projection.**

Pinned parent:
- repository `504aldo/whest-p2-cumulant-k3`
- commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- `estimators/estimator_v25.py`
- Git blob `195373a110215256b759d7c172ba8c923c62e5cc`
- SHA256 `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`

V25 already contains a 16x13 ridge-fitted public-data mean rider `CORR_BETA`. GFNP does not fit a new model. Let

`g = [1,0,1,1,0,0,phi0,1/2,phi0,0,0,0,phi0]`,
`phi0 = 0.3989422804014327`.

This is the exact feature vector for a zero-mean unit-variance Gaussian preactivation with zero D3/D21/K4, where the exact ReLU mean equals `phi0`. For every layer row `beta_l`, freeze

`beta'_l = beta_l - g (beta_l^T g)/(g^T g)`.

Therefore `beta'_l^T g = 0` analytically. No target, public score, network ID, sweep, seed choice, learned coefficient, or per-network rule enters the projection. The exact projected table is frozen in `R251_GFNP_SPEC.json`; maximum numerical null residual at freeze time is <= 1e-18.

Novelty distinction: E092 learned a new target-trained residual ridge on a covariance baseline and was closed after a worst-network gate failure. GFNP has no target fitting, no new feature map and no fitted parameter; it imposes a symbolic exactness constraint on V25's pre-existing rider. All explicitly prohibited R232/R238/R247/R248/R250/R244/R223 descendants remain excluded.

## 3. Frozen production-configuration target-free fixture

Exactly one fixture, `R251_FIXTURE_MANIFEST.json`:
- width 1024, depth 16, float32 weights;
- seed/id 251001;
- all-positive monomial/permutation matrices, exact construction in `r251_fixture.py`;
- V25 suite-only riders are enabled because shape is exactly 1024x16;
- no competition target/network is used;
- concatenated dense weight-byte SHA256: `3b94abf468e6d829c5caf55096cbb13946a3ed042a92815eb718c5c8c501ff1a`;
- exact mean-truth byte SHA256: `8e326c2c124ac70b41afb64ada24317430bb18c0a459428044094b1d954b0876`.

The weight matrices are positive monomial transforms. For `x0 ~ N(0,I)`, after the first ReLU every later layer is a positive scale/permutation of that half-normal variable, so every layer mean is exact and deterministic without Monte Carlo.

No resize, rescale, alternate seed, second fixture or retry is permitted.

## 4. Mandatory unchanged-parent gate — FIRST measurement

Before candidate construction:
1. reconstruct fixture and verify every layer hash plus aggregate/truth hashes;
2. fetch/verify the exact pinned V25 bytes;
3. run the **unchanged** V25 parent once under pinned Phase-2 development runtime: NumPy 2.4.6, FlopScope 0.12.1, WhestBench 0.16.1;
4. externally instrument, without editing parent source, every `flops.as_symmetric` call to retain per-call/layer:
   - all-finite boolean,
   - max absolute input,
   - max absolute antisymmetry `max|A-A.T|`,
   - shape and call order;
5. retain prediction finite/max-abs by layer, exact fixture hashes, parent output hash, FLOPs and timing.

Parent GO requires:
- exact fixture/source/runtime hashes;
- prediction shape (16,1024);
- every recorded checkpoint finite;
- every symmetry residual <= `1e-5 * max(1,max_abs)`;
- all predictions finite;
- no exception/budget/time failure.

**Any parent failure => terminal R251 INCONCLUSIVE.** Preserve forensic trace and stop. Do not construct GFNP, change fixture/seed/scale, retry, or move this gate to Actions.

## 5. Single target-free GFNP falsifier — only after parent GO

Construct exactly one candidate by replacing the frozen `CORR_BETA` literal with the frozen `projected_corr_beta` table. No other scientific mechanism changes.

Run exactly once on the identical fixture/runtime. Compare both outputs against the exact layer means.

Frozen scientific gates, all mandatory:
- deterministic replay is byte-identical within the single process for the GFNP coefficient projection artifact and fixture reconstruction;
- candidate prediction finite, shape (16,1024), no failures;
- candidate final-layer MSE <= 0.95 * parent final-layer MSE;
- candidate all-layer MSE <= 0.98 * parent all-layer MSE;
- at least 12/16 layer MSEs strictly improve;
- max layer degradation ratio <= 1.10;
- candidate analytical/metered FLOPs <= parent on the fixture;
- candidate residual wall time < 0.4 s is **not** required for this local synthetic falsifier (the parent workload itself is production-sized); instead no candidate residual increase > 5% is allowed. Public promotion retains the strict <0.4 s gate.

Any target-free gate failure => terminal DEVELOPMENT NO-GO / SCIENTIFIC_REJECT. No second method, no rescue.

## 6. Source eligibility gate

R249 is binding. GFNP itself adds **zero new runtime arithmetic**: it replaces static constants consumed by the existing metered `fnp` feature matmul. No `math.*`, Python scalar coefficient computation, or new numerical branch is introduced by GFNP.

Before any public execution, the integrated candidate source must nevertheless be audited fail-closed against R249. Any unresolved output-affecting Python scalar arithmetic in the integrated estimator is a source-gate failure and forbids public execution. No organizer contact is authorized.

## 7. Production cost bound

Scientific GFNP delta changes only constants; its operation graph is the parent operation graph. Thus the preregistered delta bound is `C_GFNP = C_parent` before any compliance-only rewrite. Public promotion additionally requires measured mean FLOPs <= exact R209 parent `806303721965`.

No cost claim may hide source-compliance rewrites; if a compliant integrated source needs extra metered work, its measured public cost must still satisfy the frozen gate.

## 8. Public mini-100 gate — conditional only

Only if parent GO + every target-free GFNP gate + source gate + cost gate pass:
- verify free/existing compute before trigger;
- at most ONE standard Actions workflow;
- exactly the R209 public mini:all-100 panel;
- no retry.

Frozen development gates:
- exact R209 row/order/network_id/target hash identity;
- 0/100 failures;
- mean adjusted score <= 0.95 * R209 V25;
- >=55/100 rows improved;
- paired parent-candidate adjusted-score gain > 2 descriptive SE;
- mean measured FLOPs <= R209;
- max residual wall time <0.4s.

This is development evidence only. Do not infer official rank or exact leaderboard comparability.

## 9. Stop rules / prohibitions

No paid compute, private/holdout, submission, leaderboard mutation, canonical V25 edit, R223/R244 output/artifact access, per-network tuning, leader-method invention, gate relaxation, candidate #2, resize/rescale/reseed, or scientific retry.
