# R295 — independent security/persistence audit of draft PR #36

**Decision: SECURITY_NO_GO_BEFORE_ACTIONS.**

Scope was restricted to the security/persistence control plane of draft PR #36. The R291 patch format/content was not audited; R292/R294 own that lane. No Actions run, benchmark, download, PR comment/review, code change to PR #36, result-branch creation, paid resource, or submission occurred.

## Exact audited snapshot

- Repository: tim8es/arc-whitebox
- PR: #36, draft/open
- PR head branch: research/r293-v25-capture-workflow-prep
- PR head commit: 114e08d49943c309fe09830af0a5e24095af9246
- Workflow: .github/workflows/r293-v25-residual-capture.yml
- Workflow git blob SHA-1: a7130bb2248fba3ad04bdd6c55348496aa8cdd9d
- Static preflight blob: 24cc8d120d7d8c3e72f45016bc83f8b391ed92f1
- Protocol blob: ae42019fed2ae34faaa02d8c8cf423c49750ed0d
- Initial known head supplied by coordinator matched the current head throughout the audit.
- Live repository rulesets endpoint returned [].
- Exact result ref refs/heads/research/r293-v25-capture-result did not exist at audit time. The prepared workflow therefore fails closed today.

## Findings

### PASS — manual trigger and main-ref confirmation

The workflow declares only workflow_dispatch, with a required confirmation string. Both preflight and persist independently require github.ref == refs/heads/main and the exact RUN_R293_V25_CAPTURE_ONCE confirmation input.

There is no push, pull_request, pull_request_target, schedule, repository_dispatch, or workflow_call trigger. GitHub documents that a workflow_dispatch workflow must exist on the default branch to be triggered and that callers may select a ref; the explicit per-job main-ref guard is therefore necessary and present.

Primary source:
https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow

### BLOCKER F1 — concurrency is serialized, but no-retry / exactly-once execution is not enforced

The fixed concurrency group plus cancel-in-progress: false prevents two runs in that group from executing concurrently. It does not make the benchmark one-attempt-only.

GitHub explicitly permits a workflow/job to be re-run and re-runs retain the original GITHUB_SHA and GITHUB_REF. github.run_attempt increments on every re-run. The current workflow never checks github.run_attempt == 1.

Consequences:
1. if persist reaches or completes the benchmark but fails before the result branch advances, a manual re-run can execute the benchmark again;
2. the result-branch precondition still passes because the branch can remain at the original dispatch SHA with no persisted manifest;
3. separate later manual dispatches are also possible after a failed attempt, because the branch one-shot marker is created only after successful persistence.

The concurrency group is therefore a mutual-exclusion control, not a no-retry control. GitHub also documents that, by default, only one pending item is retained in a concurrency group and a newer pending run replaces the prior pending run.

Primary sources:
https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs
https://docs.github.com/en/actions/reference/workflows-and-actions/contexts
https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency

Required remediation before authorization: fail closed when github.run_attempt != 1, and define the intended policy for a second independent dispatch after any failed first attempt.

### PASS / HARDENING GAP F2 — job-level token permissions are narrow, but mutable action tags execute in the write-token job

Top-level permissions: {} disables default scopes. preflight grants only contents: read; persist is the sole job granting contents: write. GitHub documents that when permissions are explicitly specified, unspecified permissions become none.

However, the write-token persist job executes actions/checkout@v4 and actions/setup-python@v5 by mutable major-version tags. GitHub's secure-use guidance says a full-length commit SHA is the only immutable action reference and recommends SHA pinning, especially where a compromised action could use GITHUB_TOKEN. GitHub also documents that actions can access github.token even if the workflow does not explicitly pass it.

This is a security hardening gap in the persistence control plane and is independent of R291 patch content.

Primary sources:
https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
https://docs.github.com/en/actions/tutorials/authenticate-with-github_token
https://docs.github.com/en/actions/reference/security/secure-use

### PASS / CREDENTIAL-HANDLING CONCERN F3 — checkout credentials are not persisted, but the final push step reintroduces the token into git config

Both checkouts set persist-credentials: false, correctly opting out of checkout's credential persistence.

The final persistence step then runs git remote set-url origin with https://x-access-token:$GITHUB_TOKEN@github.com/$GITHUB_REPOSITORY.git, followed by git push origin HEAD:refs/heads/$RESULT_BRANCH.

That explicitly stores the built-in token in the local remote URL until runner teardown. It occurs only in the final step after benchmark and staging checks, so exposure is bounded, but the workflow cannot literally claim that credentials remain absent from git config for the whole job. The command is not run under set -x, and no repository secret/PAT is used.

Primary checkout source:
https://github.com/actions/checkout/blob/main/action.yml

### BLOCKER F4 — pre-created result-branch and tip==dispatch-SHA checks are not atomic with the push

Positive controls:
- result branch is a fixed env constant, not a dispatch input;
- preflight requires the branch to exist, report protected=false, and have tip GITHUB_SHA;
- persist repeats the protected/tip checks before benchmark setup;
- the final persistence step rechecks git ls-remote tip equals GITHUB_SHA;
- the local result commit is required to have parent exactly GITHUB_SHA;
- the push refspec is exactly HEAD:refs/heads/$RESULT_BRANCH;
- there is no force push.

Blocking race:
after the final ls-remote == GITHUB_SHA check and before the ordinary git push, another actor can delete the result branch. A normal push to an absent refs/heads result ref creates that branch. The workflow therefore does not strictly satisfy its own requirement that it refuses to create the result branch. A ref movement to a different state between check and push is likewise not protected by compare-and-swap/lease semantics.

The protected=false API check is also last performed before the long benchmark/setup portion, not immediately at persistence, so it is a stale precondition by push time.

Required remediation before authorization: make the push conditional on the remote ref still being exactly the dispatch SHA at the server-side update point, with semantics that fail if the ref is missing or moved, and recheck the protection/rules condition immediately before persistence.

Primary sources:
https://docs.github.com/en/rest/repos/rules
https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets

### PASS — exact output allowlist

The only intended persisted paths are:
- research/captures/r293/SHA256SUMS
- research/captures/r293/manifest.json
- research/captures/r293/run-receipt.json
- research/captures/r293/vectors.f32le

The workflow copies exactly those four files, derives the complete worktree change list, diffs it against the frozen allowlist, runs four exact git add commands, derives the staged filename list, and diffs it again against the same allowlist. It does not use git add . or git add -A.

### PASS WITH F4 CAVEAT — exact push target

RESULT_BRANCH is frozen to research/r293-v25-capture-result; inputs.result_branch does not exist; remote is reset to the same repository from GITHUB_REPOSITORY; and the refspec is exactly HEAD:refs/heads/$RESULT_BRANCH.

The target is exact, but branch-existence/tip state is subject to F4's race because the final push is not a compare-and-swap update.

### PASS — no artifact/LFS/PAT/cache/repository-secret persistence path and no recursive push trigger

No actions/upload-artifact, actions/download-artifact, actions/cache, Git LFS command, PAT, or secrets.* reference appears in the audited workflow. setup-python is not configured with a cache input. The only credential deliberately used is the built-in per-job GITHUB_TOKEN.

The persisted commit is pushed using GITHUB_TOKEN. GitHub documents that ordinary events caused by GITHUB_TOKEN do not create a new workflow run, except explicit workflow_dispatch / repository_dispatch events, so the result-branch push does not recursively trigger push workflows.

Primary source:
https://docs.github.com/en/actions/concepts/security/github_token

## What must be rechecked if R294 changes PR #36

R294 is RUNNING and owns the R291 patch-format repair. If it advances PR #36, this R295 result remains pinned only to head 114e08d49943c309fe09830af0a5e24095af9246 / workflow blob a7130bb2248fba3ad04bdd6c55348496aa8cdd9d.

If workflow bytes change, recheck at minimum:
1. exact PR head and workflow git blob;
2. top-level trigger set and both main-ref/confirmation guards;
3. concurrency group, cancel-in-progress, and explicit no-rerun/run_attempt gate;
4. top-level and per-job permissions;
5. every uses reference in the write-token job and whether it is full-SHA pinned;
6. checkout persist-credentials and any later token insertion into git config/env;
7. fixed result-branch name and absence of dispatch-controlled branch/ref inputs;
8. existence/protection/active-rules/tip checks and whether the final push uses atomic expected-old-tip semantics;
9. four-file worktree and staged allowlists;
10. exact remote/refspec and absence of force/branch-creation behavior;
11. absence of upload/download-artifact, LFS, PAT, cache, repository secrets, additional triggers, or dispatch events;
12. any new step between final branch verification and push, because it widens the TOCTOU window.

A change limited to the R294 patch artifact/hash can still require workflow-blob re-pinning and a fresh static control-plane review if any workflow bytes change.

## Accounting

- Actions runs: 0
- benchmarks / estimator runs: 0
- data/dependency downloads: 0
- paid resources: 0
- PR comments/reviews: 0
- PR code edits: 0
- result-branch creations: 0
- submissions: 0
- R291 patch-format/content audit: 0
