# R252 frozen protocol — V25-CFSP4 final Cornish-Fisher sigma-point response

Status: **FROZEN BEFORE WORKFLOW CREATION OR SCIENTIFIC MEASUREMENT**  
Run ID: `R252-one-shot-actions-global-accuracy-20260923`  
Owner: `actions-accuracy-method-research`

## 1. Evidence basis and exclusions

R252 is a new scientific task. R251 remains terminal INCONCLUSIVE at queue revision 237 and
is used only as infrastructure evidence that its parent/candidate measurements were never
executed. R252 does not retry R251, does not reuse GFNP, and uses a new fixture and new
mechanism.

Full-history deduplication uses:
- `research/history.json`, Git blob
  `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`, 194 experiment IDs;
- original legacy ledger Git blob
  `040e52efe01efd7280180b7e2d72901b4c2f0532`;
- required R231/R239/R245/R249 receipts;
- queue metadata and immutable history for exclusions.

Explicitly excluded: R251 GFNP; R232 DRRE descendants; R238 RSRF descendants;
R247 2:4 D21 right-factor sparsity; R248 rank-1 Kronecker transport; R250 LEG2-R1;
R244 MP-R16; R223 V25-LF/local-feed lambda; and all closed/rejected history families.
R223/R244 candidate outputs/artifacts are not read. R230's only admissible leader finding is
that the relevant leader methods were not publicly evidenced; no leader method is inferred.

## 2. Exactly one hypothesis: V25-CFSP4

Pinned parent:
- repository: `504aldo/whest-p2-cumulant-k3`;
- commit: `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`;
- path: `estimators/estimator_v25.py`;
- Git blob: `195373a110215256b759d7c172ba8c923c62e5cc`;
- SHA256: `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`.

V25-CFSP4 leaves every V25 state, K3/K4 transport, rank, seed, source representation and
layers 0-14 unchanged. At the final layer only, after V25 has already computed the marginal
preactivation `mu`, `var`, third cumulant diagonal `D3`, and fourth connected-cumulant
diagonal `g4row`, replace the existing final Wick mean response with one fixed
Cornish-Fisher sigma-point expectation.

Let

`gamma1 = D3 / sigma^3`, `gamma2 = g4row / sigma^4`, `sigma=sqrt(var)`.

For fixed standard-normal node `z`,

`z_cf = z + a1(z)*gamma1 + a2(z)*gamma2 + a3(z)*gamma1^2`

where
- `a1=(z^2-1)/6`,
- `a2=(z^3-3z)/24`,
- `a3=-(2z^3-5z)/36`.

The candidate final mean is

`sum_k w_k * ReLU(mu + sigma*z_cf,k)`

using exactly these five precomputed nodes/weights and coefficient triples:

| z | w | a1 | a2 | a3 |
|---:|---:|---:|---:|---:|
| -2.8569700138728056 | 0.011257411327720693 | 1.1937129433613964 | -0.6145196865994386 | 0.8987198602957184 |
| -1.355626179974266 | 0.2220759220056126 | 0.13962038997193682 | 0.06565058435514533 | -0.04987782969646415 |
| 0 | 0.5333333333333333 | -0.16666666666666666 | 0 | 0 |
| 1.355626179974266 | 0.2220759220056126 | 0.13962038997193682 | -0.06565058435514533 | 0.04987782969646415 |
| 2.8569700138728056 | 0.011257411327720693 | 1.1937129433613964 | 0.6145196865994386 | -0.8987198602957184 |

There is no fitted coefficient, clipping, damping, node/rank/layer sweep, network-specific
selection, target use or fallback rule.

This differs from closed E033/E112 Edgeworth density closures and E098 K22 response:
CFSP4 preserves full V25 dependence/state and only swaps the final scalar response; it uses
a fixed Cornish-Fisher quantile map rather than a signed-density Edgeworth correction.

## 3. New exact production-shape target-free fixture

Fixture ID/seed: `252001`. Width 1024, depth 16, float32, zero bias.

Layer 0 is a two-tap cyclic Gaussian linear map:
- `W0[j,j]=float32(0.8)`;
- `W0[(j+17)%1024,j]=float32(0.6)`;
- all other entries are exactly +0.0f.

For layers `l=1..15`:
- `stride_l = 2*((37*l+13)%511)+1`;
- `q_j=((j*(2*l+3)+252001+97*l)%25)-12`;
- `scale_j=float32(1+q_j/512)`;
- `W_l[j,j]=float32(0.625)*scale_j`;
- `W_l[(j+stride_l)%1024,j]=float32(0.375)*scale_j`;
- all other entries are exactly +0.0f.

Layer 0 marginals are Gaussian, so their exact ReLU means are
`phi(0)*sqrt(sum_i W0[i,j]^2)`.
All later weight entries are nonnegative, hence all later preactivations are nonnegative
and ReLU is the identity; exact layer means follow by deterministic matrix-vector
transport. There is no Monte Carlo truth.

Frozen dense-byte SHA256:
- all 16 concatenated C-order float32 matrices:
  `de5fcc26bb7eaf45f29175cb292f27091b6b13ab6a4f3dc095be96cf402a8d4e`;
- exact C-order little-endian float64 truth tensor shape (16,1024):
  `623f35aaf0a3a9dfc7f9955ea0c45d02b118fc0fa20579f0747116b838d54450`.

The per-layer hashes are frozen in `R252_FIXTURE_MANIFEST.json`. The workflow must
reconstruct the fixture twice and verify all byte hashes before parent execution.

No alternate fixture, seed, scale, resize or second method is permitted.

## 4. Exactly one Actions run

Exactly one workflow run is authorized. It must:
- run on standard GitHub-hosted `ubuntu-24.04`;
- use `actions/setup-python` with exact Python `3.11.16`;
- install and verify:
  - NumPy 2.4.6 CPython-3.11 Linux wheel SHA256
    `89cd468399cfd2504718f0ba50e410dca55a170b61a02ad92bb18c8a65186e93`;
  - FlopScope 0.12.1 wheel SHA256
    `cd08df7e0eb468117b9a48b82d076130a9a9858ec20fdc0d015e2bd477519582`;
  - WhestBench 0.16.1 wheel SHA256
    `1a8e2620880221eb357056b0fdd65425b026dab222657f54ee202bd75dab987e`;
- verify the pinned V25 Git blob and SHA256;
- use no larger/self-hosted runner and no retry.

The repository is public. The authorization relies on GitHub's current documentation that
standard GitHub-hosted runners are free for public repositories and that `ubuntu-24.04`
is a standard x64 runner. This is not authorization for a paid or larger runner.

The workflow is path-isolated and can be triggered only by creating
`research/r252/R252_EXECUTE_TRIGGER.txt`. That file may be created exactly once.
No rerun API or second trigger is authorized.

## 5. Parent-first forensic gate

Before candidate construction, execute the **byte-identical pinned V25 parent** once on the
frozen fixture under `flopscope.BudgetContext`.

Externally wrap, without editing the parent source, every
`flops.as_symmetric(..., symmetry=(0,1))` call and retain:
- call order and mapped stage;
- shape;
- all-finite boolean;
- max absolute input value;
- `max(abs(A-A.T))`.

Expected calls are exactly 16:
`initial_cov` then `post_layer_0` through `post_layer_14`.
Also retain per-layer prediction finite/max-abs, output SHA256, measured FLOPs,
residual wall time and wall time.

Parent PASS requires all:
1. exact runtime/source/fixture identities;
2. output shape exactly (16,1024);
3. all prediction values and every symmetry checkpoint finite;
4. exactly 16 symmetry checkpoints;
5. every symmetry residual
   `<= 1e-6 + 1e-5*max_abs`;
6. measured FLOPs >0 and <=2**41;
7. no exception or wall/budget failure.

Any parent failure => terminal **INCONCLUSIVE**. Do not construct the candidate, access
public data, alter fixture/source/seed, or retry.

## 6. Candidate construction and target-free gates

Only after parent PASS, generate the candidate from the pinned V25 bytes by one exact source
insertion immediately before the final Wick-matrix block. No other source text changes.

R252-delta source compliance is fail-closed:
- no new `math.*`;
- all output-affecting candidate numerical operations use `fnp` arrays/primitives/operators;
- the CF constants above are static literals; no output-affecting Python-scalar coefficient
  calculation is performed in `predict`;
- no target/name/network ID is read by candidate inference.

The candidate branch runs only when `last` is true and breaks after appending the CFSP4
mean. Thus parent rows 0-14 must remain byte-identical.

Conservative static cost admission:
- new CFSP4 elementwise work is bounded by `100*n = 102,400` FLOPs;
- the candidate skips the parent's final Wick-response tail, which contains at minimum
  three dense small matrix products
  `APOW@C1`, `APOW@C2`, and `SB@SELC`, totaling at least
  `1024*21*(6+6+11)=494,592` multiply-scale units even under a one-unit-per-product
  lower-bound convention.
Therefore the preregistered operation-count direction is candidate <= parent; the measured
FlopScope gate below remains authoritative.

Target-free PASS requires all:
1. exact fixture replay hashes on two reconstructions;
2. candidate source diff confined to the single frozen insertion;
3. source-compliance checks above;
4. candidate output shape (16,1024), all finite, no exception;
5. candidate rows 0-14 exactly byte-identical to parent rows 0-14;
6. final-layer truth MSE <= 0.95 * parent final-layer truth MSE;
7. candidate final-layer max absolute truth error <= parent final-layer max absolute truth error;
8. candidate symmetry diagnostics pass the same finite/tolerance gate;
9. measured candidate FLOPs <= parent measured FLOPs;
10. candidate residual wall time <= 1.05 * parent residual wall time.

Any failed/unevaluable gate => terminal DEVELOPMENT NO-GO / SCIENTIFIC_REJECT and no
public dataset access.

## 7. Conditional public R209 mini-100 stage

Only if every parent, target-free, source and cost gate passes, the **same workflow run**
may continue once to public development data.

Pinned parent record:
`research/results/R209-v25-mini100.json`,
SHA256 `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`.

The workflow must independently re-extract from exactly
`aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`:
- metadata SHA256
  `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`;
- exact row order/name;
- `network_id = decimal exact int64 mlp_seed`;
- target SHA256 = SHA256 of C-contiguous raw float32 `all_layer_means` bytes.

Exact identity must match all 100 normalized R209 rows before the candidate score is accepted.

All public gates are mandatory:
1. exact 100-row name/order/network_id/target_sha256 identity;
2. 0 failures;
3. mean adjusted score <= 0.95 * R209 V25 adjusted score;
4. candidate adjusted score better on >=55/100 rows;
5. paired gain `parent_score - candidate_score` mean > 2 * descriptive paired SE;
6. mean measured FLOPs <= R209 V25 mean `806303721965`;
7. max residual wall time < 0.4 seconds.

Any public gate failure => DEVELOPMENT NO-GO. Paired SE is descriptive across the 100
development networks, not a held-out significance claim. No official rank or same-panel
leaderboard comparability may be inferred.

## 8. Absolute prohibitions

No workflow retry; no second method; no gate relaxation; no paid/larger/self-hosted runner;
no local network workaround; no private/holdout/full split; no R223/R244 candidate
outputs/artifacts; no submission; no leaderboard mutation; no canonical V25 edit; no
per-network tuning; no invented leader method.
