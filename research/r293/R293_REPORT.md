# R293 — safe one-shot V25 residual-capture workflow preparation

Status: **COMPLETE — REVIEW PR PREPARED, NOT MERGED, NOT RUN**

Job: R293  
Owner: `v25-capture-workflow-prep-r268`  
Run: `R293-v25-capture-workflow-prep-20260924`

## Outcome

A review-only draft PR has been prepared from a clean branch based on current `main`.

- preparation branch: `research/r293-v25-capture-workflow-prep`
- base `main`: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- draft PR: **#36**
- PR URL: https://github.com/tim8es/arc-whitebox/pull/36
- PR state at audit time: open, draft, not merged
- result branch frozen by protocol: `research/r293-v25-capture-result`
- result branch current state: **does not exist** (GitHub branch API returned 404)
- Actions triggered by R293 preparation/PR: **0**

This task prepares infrastructure only. It does **not** authorize or complete the
R278 scientific residual-correction diagnostic.

## Frozen dependencies inherited

R293 depends on and preserves:

- R288 receipt SHA256
  `b3c6795d03996b79ffd1bc7d2766bec337e034b1f9a57eecc744de8b762b8f10`
- R290 receipt SHA256
  `61fb8cd816e91416dd80f6b31ef87f8687310776ed74ce5dc1a069cf062eee00`
- R291 receipt SHA256
  `c534f45b6928cf42a3674625d3e548c7fe38da9cc3d233ccbe6f863c7f34d8b4`

R291 artifacts are copied into the PR byte-for-byte; no estimator or evaluator
algorithm was rewritten.

| Artifact | Git blob SHA1 | SHA256 |
|---|---|---|
| `research/r291/r291_capture_harness.py` | `3e438c0f6b87ab2fa90c1fc71bbf3cfea1e9052d` | `28526a56505beaa94183ea590810949a3a856639d3f6fa63d8869ddad419ad3e` |
| `research/r291/R291_WHESTBENCH_0_16_1_INTEGRATION.patch` | `a3d909540fc079908fcca9987c5cdb0252a1da8c` | `20ff649b9c5eec3711b223496ee3eaef0d657cc4252de8690a20dc21557e464e` |
| `research/r291/R291_EXPECTED_PUBLIC_MINI100.json` | `caf813cd5eab771108f105fe050fd6631b298733` | `ebeb221b71cf3842e807d5cf28b8c38493e53032c8e1fa897b7f5bef6b1be720` |

## New R293 files

Before this report/receipt commit, the prepared executable/static files were:

| Path | Git blob SHA1 | SHA256 |
|---|---|---|
| `.github/workflows/r293-v25-residual-capture.yml` | `a7130bb2248fba3ad04bdd6c55348496aa8cdd9d` | `9e5c4f93b2a06522ecda68d7d817de69dad9363d0b5156354e84947ff70d9c0b` |
| `research/r293/R293_PROTOCOL.json` | `ae42019fed2ae34faaa02d8c8cf423c49750ed0d` | `ed88671c7e2341cddf6cdf718a33ec87541dc2c5962ae9f1128734920b9b9764` |
| `scripts/r293_capture_workflow_preflight.py` | `24cc8d120d7d8c3e72f45016bc83f8b391ed92f1` | `1328b06e73dc3f38e610952993163cf0037e09fef1e93ed82635f3ec3d1e26b4` |

The workflow is intentionally inactive until a separately authorized merge to `main`.

## Workflow security boundary

The workflow has only:

```yaml
on:
  workflow_dispatch:
```

There are no `pull_request`, `pull_request_target`, `push`, `schedule`,
`repository_dispatch`, or `workflow_call` triggers.

Both jobs additionally require:

`github.ref == 'refs/heads/main'`

and the manual confirmation input exactly:

`RUN_R293_V25_CAPTURE_ONCE`.

A manual dispatch against another ref could still create a GitHub workflow-run record,
but both R293 jobs would be skipped; benchmark/persistence work can execute only when
the dispatch ref is `main`.

Top-level token permissions are empty. The two jobs are:

1. `preflight`: `contents: read`
2. `persist`: `contents: write`

`contents: write` therefore occurs exactly once and only on the job that ultimately
persists the result. Both checkout steps use `persist-credentials: false`; the built-in
`github.token` is materialized for the final push step only as `GITHUB_TOKEN`.
No PAT, repository secret, deploy key, Git LFS, Actions artifact, cache, release asset,
or Packages persistence path is present.

Both jobs use only standard `ubuntu-24.04` GitHub-hosted runner labels.

## Result-branch one-shot gate

The result destination is not a dispatch input. It is frozen as:

`research/r293-v25-capture-result`.

R293 does not create that branch.

Before any benchmark setup, the future workflow requires the branch to:

- already exist;
- report `protected:false` through the GitHub branch API;
- point exactly to the `workflow_dispatch` `GITHUB_SHA` on main;
- contain no existing
  `research/captures/r293/manifest.json`.

The persistence job repeats the branch SHA/protection gate before the benchmark and
checks the remote SHA a final time before commit/push.

The result commit is required to have parent exactly `GITHUB_SHA`. After the first
successful result push, the branch no longer equals `GITHUB_SHA`; therefore the
same workflow invocation cannot be used for a second capture without an explicit
external branch reset/recreation, which is not authorized by this workflow.

A rejected push fails closed. There is no fallback to PAT, artifact storage, LFS,
Packages, cache, or paid storage.

## Frozen runtime and source identities

Future execution is pinned to:

- Python `3.11.16`
- NumPy `2.4.6`
- FlopScope `0.12.1`
- WhestBench `0.16.1`
- datasets `4.1.1`
- standard `ubuntu-24.04`
- V25 upstream repository `504aldo/whest-p2-cumulant-k3`
- V25 upstream commit
  `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- V25 blob
  `195373a110215256b759d7c172ba8c923c62e5cc`
- V25 SHA256
  `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`
- inherited R288/R209 control commit
  `dff3dd65e9d2210e02418cca99e05556f6bf2c75`
- WhestBench source commit
  `4d08668b485c8a7d25a105c3c00d2f4fc2538f18`
- original `scoring.py` blob
  `9cf7653a0267c4d048617c9045ac8be127f3c8bf`.

The workflow verifies V25 blob + SHA256 and verifies the installed WhestBench
`scoring.py` blob before applying the exact frozen R291 patch.

The direct runtime package versions are exact. The Python package resolver can still
select transitive dependency versions allowed by those packages; the future run
therefore records the complete resolved `pip freeze --all` into the persisted
run receipt. This is a remaining reproducibility risk, not an unpinned direct
V25/evaluator/meter version.

## Frozen public panel and capture semantics

The workflow uses only:

- dataset `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`
- split `mini`
- streaming
- exactly 100 networks
- local runner
- FLOP budget `2199023255552`
- wall limit `120s`
- residual wall limit `0.4s`
- one thread.

R278 remains frozen:

- sort decimal `network_id` strings lexicographically;
- first 50 FIT, last 50 EVAL;
- residual = `final_target - final_pred`;
- future fit rule = `d = mean_FIT(residual)`;
- evaluation rule = `pred + d` on EVAL;
- no per-network tuning.

The R293 run itself performs **capture only**. It does not fit or evaluate the residual
correction.

R291 capture sealing must produce exactly 100 rows, `<f4[1024]` vectors, a
1,228,800-byte raw vector payload, 50 FIT / 50 EVAL identities, matching R224 target
fingerprints, vector/manifest hashes, and the R288 <=1,363,968-byte protocol cap.

## Persistence allowlist

Exactly four paths may be committed:

- `research/captures/r293/vectors.f32le`
- `research/captures/r293/manifest.json`
- `research/captures/r293/SHA256SUMS`
- `research/captures/r293/run-receipt.json`

Before commit, the workflow compares both the full working-tree change set and staged
file set against this exact list. Broad `git add .`, `git add -A`, and directory-wide
`git add` are rejected by the static gate.

## Offline/static safety check

`scripts/r293_capture_workflow_preflight.py` is standard-library only. It verifies:

- workflow_dispatch-only surface;
- banned trigger/storage/secret surfaces absent;
- top-level permissions empty;
- exactly one `contents: write`;
- only the two expected jobs;
- standard runner labels;
- both checkout credentials disabled;
- main-ref and confirmation gates;
- fixed non-input result branch;
- branch-protection/SHA/one-shot checks present;
- direct version/source pins present;
- exact output allowlist;
- all R293 authorization fields remain false;
- exact Git blob and SHA256 identities of all three R291 carried artifacts.

A static inspection of the committed workflow/protocol returned **PASS** for those
conditions. One checker-only overly broad file-allowlist predicate was found during
preparation and narrowed before the PR was opened; the workflow itself did not change
to satisfy that checker repair.

## PR-trigger audit

Current `main` has one workflow, `.github/workflows/research-control.yml`, whose
`pull_request.paths` filter covers only:

- `scripts/arc_*.py`
- `tests/test_arc_*.py`
- `research/results/**`
- `research/control/**`
- `research/history.json`
- `.github/workflows/research-control.yml`.

The R293 PR changes none of those paths. The new R293 workflow has no PR trigger.
After opening draft PR #36, the repository Actions run list contained no R293 run and
no new PR run; the latest run remained the earlier main push run
`35902504659` created at `2026-09-23T18:26:44Z`.

## Remaining risks

1. **R291 live-integration risk.** R291 proved the evaluator patch synthetically and
   statically, not in a real WhestBench public-mini run. A runtime mismatch must fail
   the future run; it must not be repaired ad hoc inside the authorized one-shot.
2. **Transitive Python resolution.** Direct competition/runtime versions are exact, but
   transitive packages are resolved at execution time. The full resolved freeze is
   persisted for audit. If a fully hash-locked environment becomes a prerequisite,
   that lock must be prepared/reviewed before authorizing the run.
3. **Result branch state is intentionally missing now.** The branch must be created
   externally after the PR is merged, from the exact merged-main SHA, and independently
   verified unprotected.
4. **Repository policy can change.** A later ruleset/token-policy change can reject the
   push. The workflow fails closed and does not select another credential/storage path.
5. **Git file recommendation.** The 1,228,800-byte vector file exceeds GitHub's
   recommended 1 MB individual-file size but is far below the enforced 100 MB limit,
   as established by R290.
6. **Scientific conclusion is separate.** Even a successful capture run does not itself
   authorize fitting/evaluating R278 correction or changing canonical/leaderboard state.

## Next gates

No next gate is authorized by R293 itself. A coordinator/owner must separately:

1. review draft PR #36 and verify exact branch/file hashes;
2. authorize and merge the PR to `main`;
3. record the resulting exact main SHA;
4. externally create `research/r293-v25-capture-result` at exactly that SHA;
5. verify that branch reports `protected:false` and no new ruleset/policy blocks the
   narrow `GITHUB_TOKEN contents:write` push;
6. separately authorize exactly one `workflow_dispatch` on that main SHA with
   confirmation `RUN_R293_V25_CAPTURE_ONCE`;
7. after execution, verify the result-branch commit and all persisted hashes;
8. only then open a separate scientific task to consume the frozen R278/R288 capture.

## Accounting

- PR created: 1 draft review PR (#36)
- PR merged: 0
- result branch created: 0
- Actions triggered: 0
- benchmark/estimator runs: 0
- dependency installs/downloads: 0
- dataset downloads/accesses: 0
- capture result commits: 0
- upload-artifact/LFS/PAT/cache/Packages use: 0
- paid resources: 0
- private/holdout/full accesses: 0
- submissions: 0
- estimator semantic changes: 0
- scorer semantic changes beyond the frozen R291 patch: 0
- PR #35 modifications: 0
- leaderboard/canonical edits: 0
