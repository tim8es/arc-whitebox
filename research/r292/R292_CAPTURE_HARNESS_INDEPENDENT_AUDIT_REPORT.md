# R292 — independent audit of the R291 V25 capture harness

Status: **FINDINGS_NOT_PASS / NO BENCHMARK**

Job: R292  
Owner: `capture-harness-independent-audit-r267`  
Run ID: `R292-r291-capture-harness-independent-audit-20260924`

## Scope and exact inputs

This was a static/source-only independent audit of the exact R291 receipt tree at
`54658e100314f398007e6ed7525550cc5db6706c`, against the frozen R288 capture contract
and the exact WhestBench 0.16.1 scorer. No harness, integration patch, workflow,
estimator, benchmark, dataset, dependency environment, Actions run, artifact upload,
paid resource, private/holdout/full data, submission, leaderboard, or canonical result
was changed or executed.

Pinned evidence checked:

- R288 receipt SHA256 `b3c6795d03996b79ffd1bc7d2766bec337e034b1f9a57eecc744de8b762b8f10`;
  protocol report blob `3b0d21fab8b668e22ae4d08022bfbf27452c8cb5`.
- R291 receipt commit `54658e100314f398007e6ed7525550cc5db6706c`;
  receipt blob `53251462138aab94d1cff51c284331eccec089d4`.
- R291 harness blob `3e438c0f6b87ab2fa90c1fc71bbf3cfea1e9052d`, SHA256
  `28526a56505beaa94183ea590810949a3a856639d3f6fa63d8869ddad419ad3e`, 16,789 bytes.
- R291 self-check blob `265688d5bd80dc05a0469cfdc3e6239ae5d3921d`, SHA256
  `6a6c9d16c6cc06eaeaa003e9b91c222e242c2abc9caaf766451fc4e8f6f1088f`, 5,641 bytes.
- R291 integration patch blob `a3d909540fc079908fcca9987c5cdb0252a1da8c`, SHA256
  `20ff649b9c5eec3711b223496ee3eaef0d657cc4252de8690a20dc21557e464e`, 3,080 bytes.
- R291 expected-panel blob `caf813cd5eab771108f105fe050fd6631b298733`, R291-recorded SHA256
  `ebeb221b71cf3842e807d5cf28b8c38493e53032c8e1fa897b7f5bef6b1be720`, 100 rows.
- R224 source fingerprint blob `9ecde34282c3fbef51ff3b11d4ec439012b3c52d`.
- WhestBench source commit `4d08668b485c8a7d25a105c3c00d2f4fc2538f18`, exact
  `src/whestbench/scoring.py` blob `9cf7653a0267c4d048617c9045ac8be127f3c8bf`.
- FlopScope source commit `b599f015b0bc005b1edb6d7a1b10e0814675e693`, cost-model blob
  `fee260eb5b65bf74f353a154e4fe0aac53762793`.

The three executable/text R291 files above were reconstructed from the exact committed
bytes; both Git blob SHA1 and SHA256 matched the R291 receipt before any local check.

## Finding F1 — the exact integration patch is syntactically corrupt

**Severity: blocking for using the exact R291 integration patch as prepared.**

The committed patch cannot be parsed by `git apply`. A static parse using the exact
committed patch returns:

`error: corrupt patch at line 23`

The defect is in the unified-diff hunk counts, not in the official scorer. Independent
counting gives:

| Hunk | Declared old/new lines | Actual old/new lines | Added lines |
|---|---:|---:|---:|
| `@@ -681,6 +681,15 @@` | 6 / 15 | 6 / 17 | 11 |
| `@@ -816,6 +825,22 @@` | 6 / 22 | 6 / 21 | 15 |
| `@@ -945,6 +970,22 @@` | 6 / 22 | 6 / 21 | 15 |

Thus the exact blob `a3d909...` is not an applyable integration patch. The committed
R291 self-check did not test patch parsing/application; its patch checks only inspect
textual properties (no removed lines, no apparent canonical-state assignment, two
`safe_capture()` call strings, no added return). This explains why the self-check can
pass while the integration patch is unusable.

No repair was made in R292. Per task scope, R292 only records the finding.

## Checks that otherwise pass by static/source inspection

### Exact scoring seams and failure-zeroing

The pinned official `scoring.py` blob is exactly
`9cf7653a0267c4d048617c9045ac8be127f3c8bf`.

The intended patch content targets the correct two pre-MSE locations:

- generic exception: after official zero prediction materialization and
  `final_target`/`all_target` binding, before `final_layer_mse_fail`;
- common path: after all budget/time/residual/combined failure zeroing and
  `pred_np`/`final_pred`/`final_target` binding, before `final_layer_mse`.

The official source independently confirms all failure-zeroing classes required by
R288: FLOP budget, caught time exhaustion, generic exception, post-predict wall-time,
residual wall-time, and combined-budget exhaustion. Generic exceptions bypass the
common seam, so the second intended call is necessary. The intended common call passes
the official failure flags plus already-computed `flops_used` and `effective_compute`;
the intended generic-exception call passes the scorer's official zero prediction,
`error_code`, and zero compute fields.

### Harness vector contract and fail isolation

The exact harness enforces float32 shapes `[1024]` for final prediction/target and
`[16,1024]` for the all-layer target fingerprint; little-endian host/native float32
bytes are serialized in C order. Residual bytes are `final_target - final_pred` and are
revalidated bitwise at seal time. Fixed raw payload arithmetic is exactly
`100 * 3 * 1024 * 4 = 1,228,800` bytes; manifest and SHA256SUMS caps reproduce the R288
uncompressed maximum `1,363,968` bytes.

Capture errors are fail-isolated: `safe_capture()` catches exceptions, disables the
sidecar, and writes a best-effort error marker; sealing refuses any capture with that
marker. Staged payload sealing rechecks row count/order, per-vector hashes, record hash,
residual bytes, offsets, name-order hash, network-ID uniqueness, and R224 target hashes.

### R224 identities, target fingerprints, and frozen split

The R291 expected panel points to the exact R224 fingerprint blob
`9ecde34282c3fbef51ff3b11d4ec439012b3c52d`. Independent row-by-row comparison of all
100 entries found **0 mismatches** for scorer index, MLP name, decimal network ID, target
SHA256, dtype `float32`, and target shape `[16,1024]`.

The panel retains 100 unique network IDs and the harness implements the frozen R278/R288
rule literally: lexicographically sort decimal network-ID strings; first 50 FIT, last 50
EVAL. Independent split counting is 50/50.

### Score/FLOP non-interference of the intended inserted calls

The intended patch text deletes no official scorer line and adds no scorer return. The
sidecar receives scorer objects/values but the exact harness only snapshots arrays with
`.tobytes(order="C")`; it does not write into prediction/target arrays or assign scorer
state. WhestBench has already exited the participant `BudgetContext` before both intended
capture seams. The pinned FlopScope cost-model source explicitly states that inherited
`FlopscopeArray.tobytes()` is outside the metered `fnp.*` surface; in this integration it
is additionally evaluator-side after participant timing/FLOP values are read. Therefore
nothing in the intended sidecar content changes official scorer inputs, MSE/score
expressions, participant FLOP count, or effective-compute fields.

This conclusion is about the intended inserted code. F1 prevents the exact committed
patch file from being applied as-is.

## Exact committed self-check replay

Only the committed stdlib R291 self-check was executed. It imports the exact committed
harness and reads the exact committed integration patch; it does not import WhestBench,
FlopScope, NumPy, V25, or dataset code.

Result: **PASS 16/16**, reproducing all recorded R291 booleans, including 100-row
serialization, 1,228,800-byte raw payload, storage bound, 50/50 split, zeroed synthetic
exception row, input/output non-mutation, residual/hash checks, target-hash check,
fail-isolated capture error, and the four textual patch checks.

Captured stdout SHA256:
`41cbc638fdac1c8be245f2c120c08cb1e0e7e23d320e48f3782089e35b7d8e8d`.

The replay does not cure F1 because the committed self-check never invokes a unified-diff
parser or applies the patch.

## Disposition

**FINDINGS_NOT_PASS.** The harness logic, expected-panel mapping, frozen split,
serialization/hash/size invariants, failure-zeroing semantics, intended pre-MSE seams,
and intended score/FLOP non-interference are consistent with R288 under static review,
and the exact committed self-check reproduces PASS 16/16. However, the exact R291
integration-patch blob is malformed and cannot be applied. A later separately assigned
repair must correct and independently verify the patch format against the exact pinned
WhestBench source before any capture run is authorized.
