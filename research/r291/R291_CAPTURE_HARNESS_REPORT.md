# R291 — evaluator-side V25 residual capture harness preparation

Status: **PREPARED / SYNTHETICALLY VERIFIED / NO BENCHMARK**

Job: R291  
Owner: `v25-capture-harness-preparation`  
Run ID: `R291-v25-capture-harness-preparation-20260923`

R291 prepares, but does not execute, the smallest evaluator-side sidecar needed to
implement the frozen R288 capture contract on a future authorized public
`mini:all-100` V25 rerun.

No estimator, workflow, PR #35, benchmark, dataset, dependency environment, Actions,
paid resource, submission, leaderboard, canonical result, private/holdout/full data, or
competition artifact was changed or executed.

## Inherited frozen constraints

The harness preserves these prior decisions without modification:

- **R278**: sort decimal `network_id` strings lexicographically; first 50 FIT,
  last 50 EVAL; fit only
  `d = mean_FIT(target_final - v25_pred_final)`; evaluate `pred + d` only on
  EVAL; no per-network tuning.
  Receipt SHA256:
  `3294904ef96c263f3562c7b34de98d0379c56207a424ab5ac91a649b27dfbd81`.
- **R282**: no existing R209/R223 evidence contains the required raw V25
  `float32[1024]` vectors; actual R209 V25 artifact is `10617855153`.
  Receipt SHA256:
  `07b3c78ac5ecb95827a48bba8443ab990bc9294f08dc7a6553a82f0bc3a9aab6`.
- **R284**: any future fitted correction arithmetic remains participant computation
  inside metered `predict()`; the present evaluator-side capture performs no
  correction and cannot feed back into the scoring run.
  Receipt SHA256:
  `65a6bd083657d6d07fa7dd340731bbb36733e14341f174768ec57ff3f832c81b`.
- **R288**: exact per-network capture is little-endian float32
  `final_pred[1024]`, `final_target[1024]`, and
  `residual = target - pred[1024]`, plus R224 identity/fingerprints and integrity
  metadata. Raw payload is exactly 1,228,800 bytes; protocol content cap is
  1,363,968 bytes.
  Receipt SHA256:
  `b3c6795d03996b79ffd1bc7d2766bec337e034b1f9a57eecc744de8b762b8f10`.

## Prepared branch and artifacts

Isolated branch: `research/r291-v25-capture-harness`.

The branch contains only R291 preparation files:

| Path | Git blob SHA1 | SHA256 |
|---|---|---|
| `research/r291/r291_capture_harness.py` | `3e438c0f6b87ab2fa90c1fc71bbf3cfea1e9052d` | `28526a56505beaa94183ea590810949a3a856639d3f6fa63d8869ddad419ad3e` |
| `research/r291/r291_capture_selfcheck.py` | `265688d5bd80dc05a0469cfdc3e6239ae5d3921d` | `6a6c9d16c6cc06eaeaa003e9b91c222e242c2abc9caaf766451fc4e8f6f1088f` |
| `research/r291/R291_WHESTBENCH_0_16_1_INTEGRATION.patch` | `a3d909540fc079908fcca9987c5cdb0252a1da8c` | `20ff649b9c5eec3711b223496ee3eaef0d657cc4252de8690a20dc21557e464e` |
| `research/r291/R291_EXPECTED_PUBLIC_MINI100.json` | `caf813cd5eab771108f105fe050fd6631b298733` | `ebeb221b71cf3842e807d5cf28b8c38493e53032c8e1fa897b7f5bef6b1be720` |

The expected-panel file contains only the already committed R224 100-row identity
mapping: scorer index, MLP name, decimal exact-int64 `network_id`, and R224
all-layer-target SHA256. It contains no target bytes.

## Exact evaluator seam

Pinned official evaluator:

- WhestBench `0.16.1`
- annotated tag object
  `66526b4c80d9aea6af981c7a0f92e9ec76c57238`
- source commit
  `4d08668b485c8a7d25a105c3c00d2f4fc2538f18`
- `src/whestbench/scoring.py` blob
  `9cf7653a0267c4d048617c9045ac8be127f3c8bf`

Primary source:
https://github.com/AIcrowd/whestbench/blob/4d08668b485c8a7d25a105c3c00d2f4fc2538f18/src/whestbench/scoring.py

The exact official source was re-read and the patch anchors occur exactly once.

Common path:

- participant `predict()` and prediction materialization are inside
  `BudgetContext` at lines 714-724;
- all post-predict budget/time failure zeroing is complete by line 940;
- `pred_np`, `final_pred`, and `final_target` are bound at lines 943/946/947;
- official final-layer MSE begins at line 948.

The prepared sidecar call is inserted after the line-947 binding and before line 948.

Generic-exception path:

- the scorer zeroes the prediction at line 793;
- materializes the scored zero prediction and binds target/all-target at lines 816-818;
- failure MSE begins at line 819.

A second sidecar call is inserted between lines 818 and 819. Without this second seam,
a generic-exception row would bypass the common path and the capture would not be
all-100 complete.

Static integration verification against the exact official blob passed:

- official source blob equals the pinned
  `9cf7653a0267c4d048617c9045ac8be127f3c8bf`;
- initializer, exception seam, and common seam each have exactly one matching anchor;
- integration patch deletes **zero** official source lines;
- integration patch contains exactly two `safe_capture()` calls;
- official MSE expressions remain present and unchanged;
- patch adds no assignment to canonical scorer state and no return-path change.

## Harness behavior

`r291_capture_harness.py` is Python-standard-library only. It does not import
WhestBench, FlopScope, NumPy, or any benchmark dependency.

At each seam it snapshots already-materialized arrays via `.tobytes(order="C")` and
requires:

- `final_pred`: float32 shape `[1024]`;
- `final_target`: float32 shape `[1024]`;
- `all_target`: float32 shape `[16,1024]` only to verify the existing R224
  all-layer target fingerprint. These all-layer bytes are **not persisted**.

Persisted vector payload is only:

`[final_pred, final_target, target_minus_pred]`

for 100 rows, exactly `100 * 3 * 1024 * 4 = 1,228,800` bytes.

Each row additionally records MLP/index/network identity, frozen FIT/EVAL role,
prediction/target/residual/payload hashes, R224 expected/observed target hash,
failure-zeroing flags, error code, FLOPs and effective compute.

Capture failures are **fail-isolated**: `safe_capture()` catches and disables the
sidecar and writes a best-effort `capture_error.txt`; it never raises into the
scorer. A disabled/incomplete/error capture cannot be sealed after the run.

Sealing is a separate post-run action. It requires exactly 100 valid rows, re-verifies
all byte hashes/residuals/target fingerprints/name order, binds the SHA256 of the
unchanged official report from the same future run, emits `vectors.f32le`,
`manifest.json`, and `SHA256SUMS`, and enforces the R288 uncompressed size cap.

The official FlopScope 0.12.1 cost-model documentation confirms that inherited ndarray
`.tobytes()` is outside the `fnp.*` metered-op surface. Here the call is evaluator
side after the participant `BudgetContext`, so it is not participant numerical work
or participant residual time.

Pinned FlopScope tag target:
`b599f015b0bc005b1edb6d7a1b10e0814675e693`.

Primary source:
https://github.com/AIcrowd/flopscope/blob/b599f015b0bc005b1edb6d7a1b10e0814675e693/docs/reference/cost-model.md

## Synthetic offline self-check

Only the committed stdlib self-check was executed. It creates 100 synthetic
float32-like byte arrays in a temporary directory; it does not import or execute
WhestBench, FlopScope, V25, the public dataset, or any benchmark code.

Final exact-byte self-check result: **PASS 16/16**:

- serialization seals successfully;
- 100 rows retained;
- raw payload exactly 1,228,800 bytes;
- sealed content stays within R288 storage bound;
- frozen split yields 50 FIT / 50 EVAL;
- synthetic exception row preserves a scored zero prediction;
- scorer input bytes are unchanged;
- synthetic scorer outputs before/after capture are identical;
- residual bytes reproduce exact float32 target-minus-pred serialization;
- record payload hash verifies;
- R224-style all-target hash verifies;
- deliberate malformed capture is isolated and disables only the sidecar;
- patch deletes no scorer code;
- patch assigns no canonical scorer state;
- patch contains the two required pre-MSE calls;
- patch does not alter the scorer return.

An initial self-check invocation exposed a checker-only false positive: its static regex
mistook keyword arguments such as `flops_used=...` in the `safe_capture()` call for
assignment statements. The checker was narrowed to distinguish keyword arguments and
the exact committed bytes then passed all 16 checks. No harness/scorer semantics were
changed to make that check pass.

The final exact committed blobs used by the successful check are the hashes in the
artifact table above.

## Scope and disposition

**HARNESS_PREPARED_SYNTHETICALLY_VERIFIED_NO_BENCHMARK.**

The prepared patch is intentionally not applied to any repository evaluator or workflow
in R291. It is a pinned recipe for a later separately authorized capture-only run.
Runtime integration against a real WhestBench installation and public Mini is therefore
not claimed here; dependency installation, dataset access, benchmark execution and
Actions were explicitly out of scope.

No blocker requiring evaluator-semantic change was found. The exact official source
seams support a fail-isolated evaluator-side sidecar without changing the scorer's
failure-zeroing, score expressions, return values, or participant FLOP boundary.

One attempted network fetch of the small already-committed branch source files from the
local container failed before transfer because DNS was unavailable; the same exact
GitHub-committed bytes were then read via the repository connector and used for the
successful local stdlib self-check. No dependency or dataset download occurred.
