# E173 OWNER PROTOCOL — AGO integration into official local Phase-2 mini

Date: 2026-09-21

Status: **PROTOCOL FROZEN / LOCAL PUBLIC-MINI INTEGRATION AUTHORIZED**

Branch:

`research/e173-official-mini-ago-integration-20260921`

Scientific parent:

`research/e171-verifier-ready-ago-20260921@fea2747b04bd8027bdd98c9680ebce1dc1bb022c`

Independent verifier:

`E172_INDEPENDENT_VERIFIER_GO_E171_VERIFIER_READY_AGO`.

Idempotency key:

`ARC-E173-OFFICIAL-MINI-AGO-INTEGRATION-20260921`

## 1. Scope

E173 integrates the verified E164/E171 Angular Gauge Only mechanism into the
current WhestBench / starter estimator interface and evaluates it locally on a
pinned minimal fixture from the official public Phase-2 Mini split.

E173 must not:

- modify `baselines/covariance_propagation.py`;
- modify the repository's generic `estimator.py`;
- import or use rejected E154/E157/E162/E166/E167 branches;
- import E169/E170 execution artifacts into the mechanism;
- submit externally;
- package or upload a challenge submission;
- access holdout/full/private grader data;
- alter a leaderboard.

Public Mini is explicitly authorized in E173 because E172 independently
verified E171.

## 2. Frozen mechanism

The mathematical parent and AGO mechanism is the E164/E171 clean line.

Parent:

- full-covariance K2 closure;
- zero-bias standard-normal input;
- exact marginal Gaussian ReLU K1/K2;
- second-order off-diagonal Wick term
  `0.5 C_ij^2 (phi_i/sigma_i)(phi_j/sigma_j)`.

AGO candidate:

1. execute the same parent first activation;
2. apply exact Gaussian-to-angular K1/K2 gauge after the first activation only;
3. propagate the same K2 closure for later layers;
4. use exact radial `a1(n)` readout for every returned hidden-layer mean row.

The row-wise radial readout is justified by positive homogeneity at every
prefix depth; it does not introduce a new fitted correction.

No K4, D4, D22, c4, recurrent higher-order state, Strassen, public fitting, or
per-MLP tuning is allowed.

## 3. Starter / V29 interface compatibility

The production adapter must satisfy:

`class Estimator(BaseEstimator)`

and

`predict(self, mlp: MLP, budget: int) -> fnp.ndarray`.

Return shape is exactly

`(mlp.depth, mlp.width)`.

WhestBench runtime orientation is the official starter orientation:

row activations use `x @ weight`, equivalently column means use
`weight.T @ mean`.

Therefore the E164 row-weight formulas are ported with
`W_e164 = weight.T`.

All benchmark arithmetic uses `flopscope.numpy` and float32, matching the
Phase-2 MLP dtype contract.

## 4. Shape gate and fallback

AGO is enabled iff:

`mlp.width == 1024 and mlp.depth == 16 and len(mlp.weights) == 16`.

For every other valid shape, the AGO entrypoint must execute exactly the parent
path.

Mandatory unit gate:

on a non-suite smoke MLP the AGO and parent entrypoints return bitwise-identical
arrays.

This fallback exists for `whest validate` and other starter smoke shapes.

## 5. Pinned toolchain

The workflow must install directly, without mutating project dependency files:

- Python 3.11;
- `flopscope==0.12.1`;
- `whestbench==0.16.1`;
- `numpy==2.1.3`;
- `pytest==8.3.5`.

One BLAS/OpenMP thread:

- `OPENBLAS_NUM_THREADS=1`;
- `OMP_NUM_THREADS=1`;
- `MKL_NUM_THREADS=1`;
- `NUMEXPR_NUM_THREADS=1`.

The workflow records `whest version --json`, Python/platform/package versions,
and hashes all evidence.

## 6. Validation gates

Both production entrypoints must independently pass:

`whest validate --estimator <entrypoint> --json`.

Entrypoints:

- E173 parent;
- E173 AGO.

The validation smoke shape must use parent fallback for the AGO entrypoint.

## 7. Official local Mini fixture

Pinned dataset:

`hf://aicrowd/arc-whestbench-public-2026@v2-phase2`.

Split:

`mini`.

Minimal bounded fixture:

the first **5** Mini MLPs in official dataset order.

Both parent and AGO use the exact same dataset coordinates and CLI limits:

- `--streaming`;
- `--n-mlps 5`;
- `--runner local`;
- `--flop-budget 2199023255552`;
- `--wall-time-limit 120`;
- `--residual-wall-time-limit 0.4`;
- `--max-threads 1`;
- `--format json`.

No `full`, holdout, scorer service, submission, or leaderboard action.

## 8. Mandatory vector evidence

A separate research-only capture script loads the same first 5 official Mini
rows and calls the exact E173 core implementation directly.

For every MLP it must save immutable float arrays:

- baked `all_layer_means` target, shape `[16,1024]`;
- parent prediction, shape `[16,1024]`;
- AGO prediction, shape `[16,1024]`;
- parent final-layer error, shape `[1024]`;
- AGO final-layer error, shape `[1024]`;
- parent final-layer squared error, shape `[1024]`;
- AGO final-layer squared error, shape `[1024]`.

For parent and AGO, the capture script executes the estimator twice and requires
bitwise-identical replay before accepting the payload.

For every file, the manifest records:

- MLP id/name/input seed;
- path;
- dtype;
- shape;
- byte count;
- file SHA256;
- raw contiguous-array SHA256.

## 9. Per-MLP MSE and SE

All numeric diagnostics are recomputed from the persisted target/prediction
arrays.

For each MLP and method:

`MSE = mean_j(error_j^2)`.

Coordinatewise squared-error standard error:

`SE_MSE = std_j(error_j^2, ddof=1) / sqrt(1024)`.

The captured MSE must match the official WhestBench per-MLP
`final_layer_mse` to:

`abs(captured - official) <= 5e-10`

or relative error `<= 5e-5`.

If this reconciliation fails, E173 fails even if the headline report looks
better.

## 10. Scientific Mini gates

Let the five official per-MLP final-layer MSE values be
`P_i` for parent and `A_i` for AGO.

Mandatory:

1. both official runs report 5 MLPs;
2. zero failed MLPs for both;
3. no budget, wall-time, residual-time, combined-budget, or estimator error;
4. AGO improves at least 3 of 5 MLPs;
5. mean AGO final-layer MSE / mean parent final-layer MSE `<= 0.98`;
6. paired mean improvement
   `mean_i(P_i-A_i) > 0`.

Report, but do not require, paired MLP-level uncertainty:

`SE_delta = std_i(P_i-A_i, ddof=1)/sqrt(5)`.

No post-result gate change is allowed.

## 11. FLOP gates

Deployed analytic candidate ledger remains:

`112,131,571,712 FLOPs`.

Budget:

`B=2^41=2,199,023,255,552`.

Frozen analytic utilization:

`0.05099153518676758 B`.

Frozen cap:

`0.135 B = 296,868,139,499 FLOPs`.

Additionally, every official AGO Mini per-MLP report must satisfy:

`flops_used <= 296,868,139,499`.

Every parent run must also remain below the same cap.

The workflow reports both analytic and WhestBench-metered FLOPs; any adapter
overhead counted by WhestBench is included in the runtime gate.

## 12. Identity and implementation gates

Focused tests must prove:

- E164 radial `a1` identity;
- Gaussian/angular round trip;
- correct starter weight orientation;
- small-shape numerical agreement with the E164 clean-room implementation;
- suite shape enables AGO;
- non-suite shape is exact parent fallback;
- deterministic output;
- no mutation of the vendored official baseline;
- output shape and finiteness.

Tolerance for mathematical identity round trips:

`<=2e-6` in the float32 starter adapter.

The E164 scientific source remains unchanged.

## 13. Evidence manifest and receipt

The workflow must upload one E173 evidence artifact containing:

- validation JSON/stderr for parent and AGO;
- official parent report JSON/stderr;
- official AGO report JSON/stderr;
- exact target/prediction/error arrays for all 5 MLPs;
- vector manifest;
- environment/version records;
- E173 summary JSON;
- SHA256 map for all evidence files.

The receipt is committed only after the artifact upload completes and the
artifact digest is known.

## 14. Infrastructure repair rule

E173 is not a one-run scientific experiment.

If a run fails for a demonstrably infrastructural reason before valid
parent-vs-AGO Mini evidence is produced, the owner must fix the root cause in
this branch and rerun the pinned protocol.

Allowed infrastructure repairs include:

- packaging/import path fixes;
- incorrect CLI syntax;
- capture/manifest plumbing bugs;
- dataset-loader API compatibility;
- evidence-path bugs.

Forbidden repair changes:

- AGO mathematics;
- parent mathematics;
- Mini MLP count/order;
- public dataset revision;
- scientific gates;
- FLOP cap;
- comparison method.

All failed infrastructure attempts and their fixes must be recorded in the
receipt.

## 15. Decision

**GO** iff every mandatory validation, evidence, replay, MSE-reconciliation,
scientific, failure, identity, and FLOP gate passes.

Otherwise:

**E173 NO-GO**, with the exact failed gate(s).

If the official Mini scientific gate fails after infrastructure is valid, the
next minimal experiment is frozen as:

- no full split;
- no new public MLPs;
- inspect the retained 5-MLP layerwise target/prediction vectors;
- identify the earliest layer at which AGO error exceeds parent;
- run one new separately-numbered synthetic mechanism experiment reproducing
  that layer-local failure before any wider benchmark run.

No external submission or leaderboard change is authorized.
