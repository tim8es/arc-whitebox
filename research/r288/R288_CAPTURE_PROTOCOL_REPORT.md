# R288 — minimal auditable V25 residual-capture protocol

Status: **PROTOCOL_READY / NO EXECUTION**

Job: R288  
Owner: `residual-capture-protocol`

This artifact specifies only a future runner-side capture for one public-development
`mini:all-100` V25 rerun. It does **not** modify the estimator or workflows and does
not authorize or execute a run, Actions, a dataset download, paid compute, private/
holdout/full access, submission, leaderboard edits, or canonical changes.

## Frozen inputs that must not change

R278 froze the diagnostic before any residual-vector computation:

1. use the immutable 100 `network_id` decimal strings;
2. sort those strings **lexicographically**;
3. first 50 = FIT, last 50 = EVAL;
4. FIT residual is `r_i = target_final_i - v25_pred_final_i`;
5. fit exactly one network-agnostic vector
   `d = mean_{i in FIT}(r_i)`;
6. evaluate only `pred_corrected_i = pred_i + d` on EVAL;
7. no per-network scalar, sign, selector, feature, normalization, or tuning.

R278 protocol/report:
- protocol blob `0ccc6b20fb4a8ad1c62a95d98dea4681970bb97d`;
- report blob `84a1186a70770b0480064f6d26703807b05b2f32`;
- receipt SHA256 `3294904ef96c263f3562c7b34de98d0379c56207a424ab5ac91a649b27dfbd81`.

R282 corrected the old R278 artifact identity and established the exact missing data:
the real R209 V25 artifact is `10617855153`, and no existing evidence contains the
required `float32[1024]` V25 final prediction / final target / signed residual vectors.
R282 receipt SHA256:
`07b3c78ac5ecb95827a48bba8443ab990bc9294f08dc7a6553a82f0bc3a9aab6`.

R284 established the rules boundary: fitting a fixed correction offline on public
development Mini data is allowed; if that correction is later used by an estimator,
its numerical application must occur in `predict()` through FlopScope and be metered.
This capture protocol does not apply any correction and must not feed information back
into the same scoring run. R284 receipt SHA256:
`65a6bd083657d6d07fa7dd340731bbb36733e14341f174768ec57ff3f832c81b`.

## Pinned future-run provenance

A valid future capture must record and match all of these:

- V25 source commit:
  `dff3dd65e9d2210e02418cca99e05556f6bf2c75`
- V25 source blob:
  `195373a110215256b759d7c172ba8c923c62e5cc`
- Python: `3.11.16`
- WhestBench: `0.16.1`
- WhestBench annotated tag:
  `66526b4c80d9aea6af981c7a0f92e9ec76c57238`
- WhestBench tag target commit:
  `4d08668b485c8a7d25a105c3c00d2f4fc2538f18`
- `src/whestbench/scoring.py` blob:
  `9cf7653a0267c4d048617c9045ac8be127f3c8bf`
- FlopScope: `0.12.1`
- NumPy environment identity used by the pinned R209 run:
  `2.4.6`
- public dataset:
  `aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`, exactly 100 rows
- dataset metadata SHA256:
  `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`
- exact 100-name/order SHA256:
  `18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce`

R224 defines each frozen `network_id` as the decimal exact int64 dataset
`mlp_seed`, and each existing target fingerprint as:

`SHA256(C-contiguous raw float32 all_layer_means bytes)`, shape `[16,1024]`.

R224 receipt:
https://github.com/tim8es/arc-whitebox/blob/8fb0afb77ae834d88bae29557a41356d4d98401f/research/r224/R224_RECEIPT.json

## Exact official capture seam

Primary source: WhestBench `v0.16.1`,
`evaluate_estimator()` in the pinned source commit:

https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/src/whestbench/scoring.py#L664-L955

The participant prediction is executed and materialized **inside** the participant
`BudgetContext` at lines 714-724. The context has exited before runner-side timing,
failure enforcement, scoring, and capture.

For the normal/common path, all post-predict failure-zeroing has already happened by
line 940. The exact capture seam is **after**:

- line 943: `pred_np = fnp.asarray(predictions, dtype=fnp.float32)`
- line 946: `final_pred = pred_np[-1]`
- line 947: `final_target = data.final_targets[i]`

and **before** line 948 computes `final_layer_mse`.

Direct source:
https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/src/whestbench/scoring.py#L942-L948

The baked dataset target is explicitly coerced to float32 at line 352:

https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/src/whestbench/scoring.py#L350-L352

Prediction materialization is explicitly a float32 coercion at lines 368-387:

https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/src/whestbench/scoring.py#L368-L387

### Exception-path seam

WhestBench has a separate generic-exception branch that zeroes the prediction and
scores it before the common seam. To guarantee **100 records even when a generic
exception occurs**, the same capture helper must also be invoked in that branch after:

- line 793: `predictions = fnp.zeros(...)`
- line 816: `pred_np = fnp.asarray(predictions, dtype=fnp.float32)`
- line 817: `final_target = data.final_targets[i]`

and before line 819 computes failure MSE. The captured `final_pred` there is
`pred_np[-1]`.

Direct source:
https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/src/whestbench/scoring.py#L790-L857

This second seam is required for an auditable all-100 artifact; instrumenting only
lines 943-948 would silently omit generic-exception rows.

## Failure-zeroing semantics

Capture the **scored prediction**, never a pre-failure participant output.

The official scorer replaces the prediction with zeros before scoring when:

- FLOP budget is exhausted: lines 739-763, zeroing at line 743;
- predict wall time is exhausted: lines 764-789, zeroing at line 768;
- a generic estimator/runner exception occurs: lines 790-857, zeroing at line 793;
- post-predict wall-time cap is exceeded: lines 888-895, zeroing at line 894;
- residual-wall-time cap is exceeded: lines 897-912, zeroing at line 904;
- combined budget is exhausted: lines 918-940, zeroing at line 932.

For every captured row persist the scorer's exact flags/fields:

- `budget_exhausted`
- `time_exhausted`
- `residual_wall_time_exhausted`
- `combined_budget_exhausted`
- `error_code` or null
- `flops_used`
- `effective_compute`

and a derived `scored_prediction_zeroed` boolean. Failed rows are retained; they are
never filtered from FIT/EVAL assignment. If a row is zeroed, its stored residual is
therefore the exact target minus the scored zero vector.

## Minimal vector contract

The capture artifact contains exactly one row for each of the 100 networks.

Canonical vector representation for all three arrays:

- dtype: IEEE-754 little-endian float32, `<f4`
- shape: `[1024]`
- C-contiguous
- residual sign: **`final_target - final_pred`**
- no rounding, decimal text conversion, normalization, or compression before hashing

Per row store:

1. `final_pred`: the final vector the official scorer is about to score;
2. `final_target`: the exact baked final target bound by the scorer;
3. `residual`: float32 `final_target - final_pred`.

The minimal implementation should snapshot `final_pred` and `final_target` at the
source seam without mutating them. To minimize perturbation of the official score path,
the residual payload may be derived **after that network's official MSE is computed**
(or after `evaluate_estimator()` returns) from the captured float32 bytes. It must not
be used by the scorer and must bitwise validate against the stored pred/target.

## Identity and hashes

Each of 100 manifest rows must contain:

- `scorer_mlp_index`: the zero-based `i` used by `evaluate_estimator()`;
- `mlp_name`;
- `network_id`: frozen R224 decimal exact-int64 `mlp_seed`, stored as a string;
- `split_role`: FIT or EVAL derived only from the frozen R278 lexicographic rule;
- `r224_target_all_sha256_expected`;
- `r224_target_all_sha256_observed`;
- `final_pred_sha256`;
- `final_target_sha256`;
- `residual_sha256`;
- `record_payload_sha256 = SHA256(pred_bytes || target_bytes || residual_bytes)`;
- the failure/meter fields listed above.

Before any diagnostic fitting, require:

1. exactly 100 rows;
2. exact `mlp_name` list/order hash equals
   `18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce`;
3. exact one-to-one join to the immutable R224
   `mlp_name -> network_id -> target_all_sha256` mapping;
4. 100 unique `network_id` values;
5. 100 observed all-layer target hashes equal their R224 expected hashes;
6. every per-vector and per-record SHA256 verifies;
7. every stored residual bitwise equals the canonical float32 subtraction of the
   stored target and prediction.

A mismatch makes the capture **INVALID** and aborts fitting. Do not reorder, repair,
drop, or substitute rows after observing residuals.

## Artifact layout and integrity manifest

Minimal uncompressed content:

- `vectors.f32le` — fixed layout `[100,3,1024]`, axis 1 ordered
  `[final_pred, final_target, residual]`;
- `manifest.json` — provenance plus the 100 metadata/hash rows;
- `SHA256SUMS` — SHA256 for both files.

The top-level manifest additionally records:

- capture protocol ID/version and future capture-code commit/blob;
- future run ID and workflow/run provenance;
- exact V25 source commit/blob;
- Python / WhestBench / FlopScope / NumPy versions;
- WhestBench tag target and scoring.py blob;
- dataset repo/revision/split and metadata/name-order hashes;
- exact official `report.json` SHA256 from the same run;
- payload SHA256 and byte count;
- `rows=100`, `dtype=<f4`, `vector_shape=[1024]`;
- frozen R278 split/fit rule text/hash;
- R284 metering-boundary reference.

The future durable receipt must record the SHA256 of `SHA256SUMS` and, if wrapped in
a transport archive, the archive SHA256. The transport archive is not the identity of
the vectors; the uncompressed file hashes are.

## Storage upper bound

Raw vector payload is fixed exactly:

`100 networks * 3 vectors * 1024 values * 4 bytes = 1,228,800 bytes`
= **1.171875 MiB**.

Impose these protocol limits:

- `vectors.f32le`: exactly 1,228,800 bytes;
- `manifest.json`: at most 131,072 bytes;
- `SHA256SUMS`: at most 4,096 bytes.

Therefore the capture's uncompressed protocol content is at most
**1,363,968 bytes = 1.30078125 MiB**. Transport/container framing is separate and must
be hashed in the future receipt.

## Metering and score non-interference

R284's first-party rule audit pins the estimator boundary:

- participant numerical work belongs in `predict()` through FlopScope;
- a future fitted correction, if ever evaluated, must be applied in that metered path;
- this diagnostic capture is runner/evaluator-side and must never be used to perform
  participant computation outside metering.

Primary starterkit sources pinned by R284:

- allowed-code commit/blob:
  `5eb9aa1455fcb3216af55994bdf25dc242b95797` /
  `525276e8e5bc7f6a7dd54e876140ab0df514be32`
  https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/concepts/allowed-code.md
- estimator-contract blob:
  `43c1494420b46aad4bc1dbbab83528eca6b89668`
  https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/estimator-contract.md
- code-patterns blob:
  `2d1aa532af6f160fd0942da34f78595216a596de`
  https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/code-patterns.md

The WhestBench source itself shows why capture does not alter participant FLOP
accounting: `estimator.predict()` and prediction materialization are inside
`with budget_ctx:` (lines 714-724); the capture seam is later, after that context
has exited. The capture must be read-only with respect to predictions, targets, budget
statistics and failure flags. Official MSE/score must be computed by the unchanged
existing expressions on the unchanged objects.

No score from the capture artifact is official by itself. Any later correction test is
a separate estimator evaluation and must obey R284's metered runtime boundary.

## R288 disposition

**READY AS A CAPTURE CONTRACT; NO RUN AUTHORIZED OR PERFORMED.**

The smallest auditable future artifact is a ~1.30 MiB uncompressed bundle containing
the scored final prediction, exact final target and signed residual for every public
Mini network, tied to the immutable R224 panel fingerprints and exact evaluator/source
versions. The future runner instrumentation needs two source seams only because
WhestBench's generic-exception control flow bypasses the common scoring seam.

R278's frozen split/global fit rule and R284's metering boundary are preserved byte-for-
meaning; this task introduces no estimator method, tuning rule, workflow change, or run.
