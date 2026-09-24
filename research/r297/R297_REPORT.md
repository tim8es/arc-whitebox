# R297 — independent final static review of PR #36

Status: **COMPLETE — PASS (STATIC/READ-ONLY); REVIEWER REPLAY OF GIT APPLY/CAS NOT RUN**

Job: R297  
Run ID: `R297-pr36-final-independent-review-20260924-r4553b`  
Owner: `r297-independent-final-review-r4553b`  
Reviewed PR: #36  
Exact reviewed PR head: `f6fb9018504632edffa1fb80d14ce8a68f442602`  
PR state observed through GitHub connector: open / draft / unmerged.

## Verdict

**PASS** for the requested independent final review of the exact PR head above.

This verdict is based on direct GitHub API inspection of the exact committed blobs and workflow/protocol text, plus explicit reliance on the committed R294 and corrected R302 execution receipts where this reviewer did not execute local Git replay. The reviewer does **not** claim an independent local `git apply` or CAS adversarial replay.

## Evidence and findings

### 1. R291 preservation and R294 patch

Direct tree inspection at the reviewed head shows the historical R291 patch is still present unchanged as Git blob:

- `research/r291/R291_WHESTBENCH_0_16_1_INTEGRATION.patch`
- blob `a3d909540fc079908fcca9987c5cdb0252a1da8c`

The R294 receipt identifies that exact historical blob as malformed historical evidence with the known `git apply` corruption at patch line 23. The old patch was not rewritten.

The active repaired patch is:

- `research/r294/R294_WHESTBENCH_0_16_1_INTEGRATION.patch`
- blob `65abb2e2040e44a7965f5123acd17bb838891532`
- receipt SHA-256 `bab98621f510520a0fe8539c41bb2d59dd4680eaa8237a63a81d082897934cf3`

The workflow and protocol both pin WhestBench 0.16.1 scoring blob `9cf7653a0267c4d048617c9045ac8be127f3c8bf`, the repaired patch blob above, and patched scoring blob `8493b7ff28110fb13f467400b6895c56bd7550bb`.

The committed R294 checker pins the same identities, requires the R291 old patch to fail, requires the R294 patch to contain exactly three expected hunks, 41 additions and zero official-source deletions, and checks that official source order and score/return/FLOP anchor counts remain unchanged.

R294 committed receipt records independent exact-byte verification with `git apply --check=PASS`, `git apply=PASS`, patched blob `8493b7ff...`, 41 additions, zero deletions, and historical R291 rejection.

**Reviewer execution status:** local `git apply` replay = **NOT RUN**. The apply PASS above is attributed to the committed R294 verifier evidence, not to this reviewer.

### 2. R294/R302 exact identities and corrected self-check

At the reviewed PR head, direct Git tree/API inspection gives:

- workflow blob `19f6f95ceb2cacef5497eafd5e31e20e86cfad8c`
- protocol blob `cc51198550b0d35b7fb0e34e8b072d74a456476c`
- preflight blob `ba27e0a6f6e13e24344b3cec6b60a5717e45b51f`
- R294 apply checker blob `547ec661b8cf0548ee080acca2f32f9eeef4537c`
- corrected R296 security self-check blob `e6c975a72f8f4863b476bfe5b636984fe1169713`

R302 records that the original R296 checker blob `dc09a5c...` did **not** successfully execute its CAS matrix because of an argument-order TypeError. Therefore the original R296 receipt is not treated as sufficient execution proof for CAS behavior.

R302 records the one-line argument-order correction only, then exact replay of the corrected checker against the exact workflow/protocol bytes, with 21/21 checks passing and no failed checks. Its recorded SHA-256 identities for the exact reviewed workflow/protocol and corrected checker are:

- workflow: `23cb8b2a4db23b6dd030b6148cfaa8d6d2cb45e31ff264195c970117fd69f863`
- protocol: `e0e36f5107676326529359f238b678b03d5faf25fae913d102387dc6ba1f3a74`
- corrected self-check: `0392e2c88d7c9f6cb75813cc330cdd699217d9537957d428d3d183edd9673da0`

**Reviewer execution status:** independent SHA-256 recomputation and execution of the R302 checker = **NOT RUN**. Exact Git blob identities were checked directly at the final head; SHA-256 and 21/21 execution results are attributed to the committed R302 receipt.

### 3. Workflow, preflight, and protocol alignment

Direct static inspection of the final workflow and protocol shows consistent values for:

- trigger: `workflow_dispatch` only
- required ref: `refs/heads/main`
- confirmation input: `RUN_R293_V25_CAPTURE_ONCE`
- result branch: `research/r293-v25-capture-result`
- result branch must be pre-created externally
- branch creation by workflow: false
- runner: `ubuntu-24.04`
- Python 3.11.16 and exact direct dependency pins
- exact R291 historical blob, exact R294 active patch blob, exact R294 patched-scoring blob
- no Actions artifact storage, LFS, PAT, or cache
- default permissions none; preflight contents:read; persist contents:write
- secrets disabled in protocol

The workflow invokes both the R293 static preflight and the corrected R296 security self-check before benchmark-capable work.

### 4. Rerun and second-dispatch gate

Both workflow jobs have the same fail-closed job condition including:

`github.run_attempt == 1`

The persist job's durable claim step occurs before dependency installation, validation, and benchmark execution.

The durable claim commits an empty claim commit then pushes it with:

`--force-with-lease="refs/heads/$RESULT_BRANCH:$GITHUB_SHA"`

A second dispatch or rerun from the same dispatch SHA therefore sees a moved result ref and cannot satisfy the explicit expected-old-tip lease.

R302 corrected replay records PASS for the corresponding rerun/second-dispatch lease rejection checks.

**Reviewer CAS replay:** **NOT RUN**.

### 5. CAS move/delete/race rejection

Claim stage uses explicit expected old tip `$GITHUB_SHA`.

Final persistence uses explicit expected old tip `$claim_sha`:

`--force-with-lease="refs/heads/$RESULT_BRANCH:$claim_sha"`

Direct workflow inspection also requires the remote result ref to equal the expected tip immediately before the final push.

The corrected R302 replay records PASS for:

- claim CAS success
- rerun/second-dispatch stale lease rejection
- deleted result branch not recreated
- moved result branch rejected
- deleted branch before final persist not recreated
- moved branch before final persist rejected
- final CAS success
- stale final lease rejected

**Reviewer CAS replay:** **NOT RUN**.

### 6. Result branch absent behavior

GitHub branch search during this review found no current branch named `research/r293-v25-capture-result`.

The workflow does not create the branch. Preflight and claim both require a non-empty remote SHA and exact equality with the dispatch SHA; an absent branch therefore fails closed before benchmark work. R302 also records the explicit expected-old-tip lease as rejecting branch recreation after deletion.

### 7. Action SHA pins

Direct first-party GitHub tag-ref inspection confirmed:

- `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683` is the object of `refs/tags/v4.2.2`
- `actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065` is the object of `refs/tags/v5.6.0`

The final workflow uses only these full action commit SHAs; no mutable `@v4` / `@v5` action references are present.

### 8. Token non-persistence

Direct workflow inspection shows:

- both checkout steps set `persist-credentials: false`
- `GITHUB_TOKEN` is explicitly scoped only to the durable-claim push and final-result push steps
- push authentication is supplied via process-scoped `GIT_CONFIG_COUNT/GIT_CONFIG_KEY_0/GIT_CONFIG_VALUE_0`
- token is not embedded in the remote URL
- no `git remote set-url` is used

R302 corrected replay records PASS for process-scoped helper visibility/non-persistence and token absence from persistent Git config.

**Reviewer credential replay:** **NOT RUN**.

### 9. Exact four-file output allowlist

The protocol output allowlist and result persistence allowlist are identical and contain exactly:

1. `research/captures/r293/SHA256SUMS`
2. `research/captures/r293/manifest.json`
3. `research/captures/r293/run-receipt.json`
4. `research/captures/r293/vectors.f32le`

Before commit, the workflow compares all working-tree changes against this exact sorted allowlist. After staging, it separately compares the staged file list against the same allowlist.

No fifth persisted output path is admitted by the workflow logic.

### 10. Forbidden paths / resources

Direct static review found no workflow path for:

- `actions/upload-artifact` or other Actions artifact persistence
- Git LFS
- PAT
- Actions cache
- secret-based credentials
- PR-triggered execution
- holdout/private-full evaluation
- submission
- leaderboard mutation
- merge

The benchmark path is pinned to the public `aicrowd/arc-whestbench-public-2026@v2-phase2` mini split, 100 MLPs, and remains unauthorized by the protocol until a separate dispatch authorization.

No Actions run, benchmark, estimator run, dependency/data download, paid resource, merge, PR comment/review, result-branch creation, holdout access, or submission was performed by this R297 review.

## Reviewer execution boundary

The following checks were **directly inspected by this reviewer** on exact PR head `f6fb9018504632edffa1fb80d14ce8a68f442602`:

- PR head/state
- exact Git blob identities
- historical R291 preservation
- active R294 patch identity
- workflow/protocol/preflight/self-check identity alignment
- job rerun guards
- claim-before-benchmark ordering
- explicit expected-tip leases
- exact four-file allowlist
- action full-SHA use and first-party tag mapping
- token handling text
- current absence of the result branch
- absence of forbidden workflow paths listed above

The following execution claims are **receipt-backed, reviewer NOT RUN**:

- R294 exact `git apply --check` / `git apply`
- R302 corrected 21/21 checker execution
- CAS adversarial replay
- process-scoped credential non-persistence replay
- independent SHA-256 recomputation of all committed blobs

## Final disposition

**PASS.** No blocking inconsistency was found at the exact reviewed PR head. The original R296 checker execution defect is explicitly superseded by R302's corrected checker and exact replay; this review relies on R302 for those runtime/static-selfcheck execution claims and does not misattribute them to an independent R297 replay.

PR #36 must remain open/draft/unmerged until separately authorized. This review does not authorize Actions, benchmark execution, result-branch creation, merge, holdout access, submission, or paid resources.
