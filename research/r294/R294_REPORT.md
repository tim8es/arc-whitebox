# R294 — repair of the malformed R291 WhestBench capture patch in draft PR #36

Status: **COMPLETE — PATCH FORMAT REPAIRED / PR REMAINS DRAFT / NO RUN**

Job: R294  
Owner: `v25-capture-workflow-patch-repair-r268`  
Run ID: `R294-r291-patch-format-repair-pr36-20260924`

## Scope and disposition

R294 repairs only blocking R292 finding F1 in draft PR #36.

Historical R291 artifacts are preserved unchanged. In particular:

- R291 patch blob:
  `a3d909540fc079908fcca9987c5cdb0252a1da8c`
- R291 patch SHA256:
  `20ff649b9c5eec3711b223496ee3eaef0d657cc4252de8690a20dc21557e464e`
- R291 patch remains malformed and is retained only as historical evidence.

Draft PR #36 remains open/draft. No merge, Actions run, benchmark, estimator run,
dataset access/download, dependency install, paid resource, result-branch creation,
submission, leaderboard edit, or canonical-result edit was performed.

## R292 finding reproduced and repaired

R292 independently established that the exact R291 patch fails parsing:

`error: corrupt patch at line 23`

because its unified-diff hunk counts are inconsistent.

R292 report:
- commit `660232b78410412c253286701190d831135370a1`
- blob `925a1d41c917f043e84a9c8a372fcd6199119ed0`
- SHA256 `424d37a4139421e46ce4c89df955b60014d153a8d3a55737d27f284527f5d757`

R292 receipt:
- commit `3d9684cc93449e9a411e86f14b8385939bdc33e6`
- blob `eca95be1a8907dedf5e04708a8c9c8db3906e32c`
- queue receipt SHA256 `906ba41a435b3c6cca9cde1af9a7af3fd3641d6ab523ebb21dc6ac051ca0be3d`

The R294 repair changes only the three unified-diff hunk headers needed to describe
the already-frozen inserted source correctly:

| Hunk | Historical R291 header | Correct R294 header |
|---|---|---|
| initializer | `@@ -681,6 +681,15 @@` | `@@ -681,6 +681,17 @@` |
| generic-exception pre-MSE seam | `@@ -816,6 +825,22 @@` | `@@ -816,6 +827,21 @@` |
| common pre-MSE seam | `@@ -945,6 +970,22 @@` | `@@ -945,6 +971,21 @@` |

The patch body itself is unchanged in intent and content:

- historical R291 source additions: **41**
- R294 source additions: **41**
- additions identical: **true**
- R294 official-source deletions: **0**
- capture calls inserted: **2**
- sidecar initializer import inserted: **1**

The corrected append-only artifact is:

`research/r294/R294_WHESTBENCH_0_16_1_INTEGRATION.patch`

- introducing commit:
  `8ad4094a5d6c0808308be3a1e7d39eb878bc03ef`
- Git blob SHA1:
  `65abb2e2040e44a7965f5123acd17bb838891532`
- SHA256:
  `bab98621f510520a0fe8539c41bb2d59dd4680eaa8237a63a81d082897934cf3`
- bytes: **3,080**

Pinned official source:

- WhestBench: `0.16.1`
- source commit:
  `4d08668b485c8a7d25a105c3c00d2f4fc2538f18`
- exact `src/whestbench/scoring.py` blob:
  `9cf7653a0267c4d048617c9045ac8be127f3c8bf`

Expected patched source blob:

`8493b7ff28110fb13f467400b6895c56bd7550bb`

## Real apply checker

R294 adds a new offline checker:

`scripts/r294_patch_apply_check.py`

- introducing commit:
  `c0553a11a6f2046485a2dcf03281b15f2ca18dd6`
- final checker identity pinned in protocol at commit:
  `41a6ff997e3985db5ad3902067c42aa0d43a4acc`
- Git blob SHA1:
  `547ec661b8cf0548ee080acca2f32f9eeef4537c`
- SHA256:
  `98479a811d8f36b6afb98ebc495a00b3a3727c438a90bea47e7b1cb69cef625d`
- bytes: **6,555**

The checker does materially more than the R291 text-only self-check:

1. verifies the exact pinned official source blob;
2. verifies exact old/new patch blob + SHA256 identities;
3. verifies the R291 patch has 41 intended additions;
4. verifies the R294 additions are exactly identical to those 41 R291 additions;
5. verifies R294 deletes zero official source lines;
6. verifies the exact three corrected hunk headers;
7. creates a temporary Git repository around the exact pinned `scoring.py`;
8. requires historical R291 `git apply --check` to fail;
9. runs actual `git apply --check` on R294;
10. runs actual `git apply` on R294;
11. verifies the resulting source blob is exactly
    `8493b7ff28110fb13f467400b6895c56bd7550bb`;
12. proves every original source line survives byte-for-byte and in order;
13. verifies official score/return/FLOP anchor counts are unchanged;
14. verifies exactly two capture calls and one sidecar initializer import.

## Exact-byte apply evidence

A separate independent offline verifier was run on the exact committed bytes identified
above. Its result, supplied to this R294 attempt, is:

- exact source blob:
  `9cf7653a0267c4d048617c9045ac8be127f3c8bf`
- exact R294 patch blob:
  `65abb2e2040e44a7965f5123acd17bb838891532`
- exact R294 patch SHA256:
  `bab98621f510520a0fe8539c41bb2d59dd4680eaa8237a63a81d082897934cf3`
- `git apply --check`: **PASS / exit 0**
- `git apply`: **PASS / exit 0**
- resulting patched source blob:
  `8493b7ff28110fb13f467400b6895c56bd7550bb`
- source additions: **41**
- source deletions: **0**
- original-source order preservation: **PASS**
- official score/return/FLOP anchor preservation: **PASS**
- historical R291 patch: still rejected as corrupt at patch line 23.

### Platform-specific checker note

On a Windows local invocation, the committed checker stopped only because Git formatted
the historical-malformed-patch stderr as:

`error: corrupt patch at <path>:23`

instead of the Linux-oriented literal:

`error: corrupt patch at line 23`.

A temporary local comparison that changed only this stderr matching condition confirmed
the remainder of the checker. That temporary change was **not committed** and did not
modify PR #36.

I attempted to replay the unchanged committed checker in the available Linux execution
environment. The prior temp files were not present, and the source-only retrieval
attempt failed before the checker could run with:

`curl: (6) Could not resolve host: raw.githubusercontent.com`

Therefore this report does **not** claim a second local Linux execution of the checker.
The apply/semantic PASS above is the independent exact-byte verifier result, while
current-branch static identity/pin checks were re-run directly against GitHub committed
bytes.

## PR #36 wiring

R294 modifies only the existing draft PR #36 repair lane after the R293 receipt head.

Commits after R293 head `114e08d49943c309fe09830af0a5e24095af9246`:

1. `8ad4094a5d6c0808308be3a1e7d39eb878bc03ef`
   — add corrected R294 patch.
2. `c0553a11a6f2046485a2dcf03281b15f2ca18dd6`
   — add real git-apply/semantic checker.
3. `0a47870e0129159cbea8557b91f36cb519db7cff`
   — select R294 patch in protocol.
4. `0959ba102ce83b445757b66961589d0b0e37ec90`
   — wire corrected patch/apply gate into workflow.
5. `42f485b2761297c78376f2ad05fb2ab4d2d6ed22`
   — pin R294 patch in workflow preflight.
6. `41a6ff997e3985db5ad3902067c42aa0d43a4acc`
   — pin checker identity in protocol.

Current exact PR files before this R294 report:

| Path | Git blob SHA1 | SHA256 |
|---|---|---|
| `.github/workflows/r293-v25-residual-capture.yml` | `8339eeb42e9a37dbea3c7aae6ad0c4ef6edfa7be` | `6dbe23e2637de7e196002af17de3e193630f41032e5a1f75eab58c1ab9473efe` |
| `research/r293/R293_PROTOCOL.json` | `fa31b93944d75604a7a096e308ddc0d28092acd7` | `9c2b066e71da6e81f7d667c8000646d71a6aa4822c61149aed73fb7589061420` |
| `scripts/r293_capture_workflow_preflight.py` | `67d440beac3c4fee85e796b09fcd77849e0f00f2` | `d6655c54c94daf984c46aabefaadedf88948edb8ed396c4bcbe6022db429e2e9` |
| `scripts/r294_patch_apply_check.py` | `547ec661b8cf0548ee080acca2f32f9eeef4537c` | `98479a811d8f36b6afb98ebc495a00b3a3727c438a90bea47e7b1cb69cef625d` |
| `research/r294/R294_WHESTBENCH_0_16_1_INTEGRATION.patch` | `65abb2e2040e44a7965f5123acd17bb838891532` | `bab98621f510520a0fe8539c41bb2d59dd4680eaa8237a63a81d082897934cf3` |

Current static checks confirm:

- protocol `active_integration_patch` selects the R294 patch;
- workflow verifies R294 blob and SHA256;
- workflow invokes `scripts/r294_patch_apply_check.py`;
- workflow passes the historical R291 patch only as `--old-patch` evidence;
- workflow runs a second explicit `git apply --check` on the staged exact evaluator
  source before applying R294;
- workflow applies only the R294 patch;
- workflow preflight pins the R294 patch exact blob/SHA256;
- the historical R291 patch remains present and unchanged.

## Semantic boundary

The R294 patch makes **no official-source deletion**. It inserts only:

1. one fail-isolated capture-sidecar initializer near the evaluator setup;
2. one capture call on the generic-exception zeroed-prediction path before failure MSE;
3. one capture call on the common path after all failure zeroing and before final MSE.

The exact 41 added source lines are identical to the intended R291 additions already
audited by R292. No official MSE expression, score aggregation, scorer return path,
participant BudgetContext, FLOP accounting assignment, failure-zeroing statement, or
effective-compute calculation is changed.

## Remaining gates

R294 authorizes no execution.

Before any future run:

1. PR #36 must remain under independent review;
2. any further PR-head change must invalidate the recorded R294 file hashes and require
   re-review;
3. the merged workflow, if separately authorized, must still verify the exact official
   source blob and execute the R294 real-apply checker;
4. result-branch creation, workflow dispatch, benchmark execution, and scientific use of
   the capture remain separate coordinator gates.

## Accounting

- historical R291 files modified: 0
- R294 corrected patch artifacts added: 1
- R294 real apply checkers added: 1
- workflow/protocol/preflight repairs: only R294 patch/check wiring
- PR #36 merged: 0
- Actions runs: 0
- benchmark/estimator runs: 0
- datasets accessed/downloaded: 0
- dependencies installed/downloaded: 0
- paid resources: 0
- result branch created: 0
- submissions: 0
- leaderboard edits: 0
- canonical-result edits: 0
