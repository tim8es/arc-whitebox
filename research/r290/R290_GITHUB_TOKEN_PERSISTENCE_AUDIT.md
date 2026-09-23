# R290 — GITHUB_TOKEN persistence audit for the R288 capture

Status: **COMPLETE — DIRECT GIT PERSISTENCE PATH CONFIRMED**

Job: R290  
Owner: `gha-result-persistence-audit-r291-session`  
Run: `R290-gha-result-persistence-audit-20260923`

## Verdict

**Yes.** The future R288 capture can be preserved without GitHub Actions artifact
storage by committing the sealed ~1.36 MB capture as ordinary Git repository content
to an unprotected research branch from the authorized GitHub Actions job, using only:

```yaml
permissions:
  contents: write
```

at the persistence job/workflow scope.

This removes the account-specific Actions-artifact / GitHub-Packages storage uncertainty
that left R287 in `WAITING_INPUT`. It does not use `actions/upload-artifact`, GitHub
Packages, Git LFS, cache storage, or another metered storage product.

The path is fully proven for a **pre-existing unprotected research branch**. If the
coordinator requires a brand-new result-only branch name, the safe preflight is to
create that empty branch before the authorized run and verify its branch API reports
`protected:false`; this avoids relying on an unqueryable hypothetical legacy
branch-protection pattern for a branch that does not yet exist.

No capture/result commit was attempted in R290. The only repository writes made by this
audit are the required control claim/start/finish records and append-only R290
report/receipt.

## R288 payload being persisted

R288 receipt SHA256:
`b3c6795d03996b79ffd1bc7d2766bec337e034b1f9a57eecc744de8b762b8f10`.

Frozen capture content:

- `vectors.f32le`: exactly 1,228,800 bytes;
- `manifest.json`: at most 131,072 bytes;
- `SHA256SUMS`: at most 4,096 bytes;
- total protocol upper bound: **1,363,968 bytes** (~1.301 MiB).

This audit changes none of those bytes or semantics.

## Current repository facts

Read from the live public repository during R290:

- repository: `tim8es/arc-whitebox`;
- visibility: **public**;
- owner type: personal GitHub user `tim8es`, not an organization;
- default branch: `main`;
- repository API size: `20053` KiB before any future capture;
- repository rulesets endpoint: **empty list**;
- `main`: `protected:false`;
- `research/control-v2`: `protected:false`;
- `research/r291-v25-capture-harness`: `protected:false`;
- `research/r288-v25-residual-capture-protocol`: `protected:false`.

Repository API:
https://api.github.com/repos/tim8es/arc-whitebox

Rulesets API:
https://api.github.com/repos/tim8es/arc-whitebox/rulesets

The connector cannot read the administration-only legacy branch-protection configuration
endpoint, but the branch metadata above directly reports protection disabled for the
existing branches checked. Therefore the strongest no-unknown path is to push only to
an already-created branch whose own branch API was verified immediately before the run.

## Exact current workflow permissions and triggers

At live control head, exactly four workflow files exist.

| Workflow | Blob SHA1 | Declared token permission | Push trigger |
|---|---|---|---|
| `r233-v25-onehot-wick-fixture.yml` | `876e16aca6a8325b767b004c57016871fb7d6e1d` | job `contents: read` | `research/control-v2`, only `research/r233/R233_EXECUTE_TRIGGER.txt` |
| `r238-rsrf.yml` | `adae8a650a0f2c9c05c0b4354258e55f6e90a7db` | job `contents: read` | `research/control-v2`, only `research/r238/R238_EXECUTE_TRIGGER.txt` |
| `r252-cfsp4-one-shot.yml` | `608ea92fd571a8eac4d6ae5aa38e806c112f2cba` | workflow `contents: read` | `research/control-v2`, only `research/r252/R252_EXECUTE_TRIGGER.txt` |
| `research-control.yml` | `b44a640c8d3cd3b6ba21f452237d9ba631c92621` | workflow `contents: read` | `main`, selected control/history/result paths |

Thus **none of the current workflows can push repository contents as written**. A future
authorized capture workflow/job must explicitly use `contents: write`; no broader
permission is needed for the Git persistence step.

GitHub's workflow syntax states that a job/workflow `permissions` key can add or remove
the permissions granted to `GITHUB_TOKEN`; when any scopes are explicitly listed,
unspecified scopes are set to `none`. The repository is personal rather than
organization-owned, so the documented organization-level write restriction is not an
applicable policy layer here.

Primary docs:
https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

Repository Actions settings documentation:
https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository

## Is a GITHUB_TOKEN Git push supported?

Yes.

The first-party `actions/checkout` documentation states that checkout persists the
authentication token in local Git configuration by default so subsequent authenticated
Git commands work. Its official scenarios include **"Push a commit using the built-in
token"** with ordinary `git add`, `git commit`, and `git push`.

Primary source:
https://github.com/actions/checkout/blob/main/README.md

The current repository workflows use `actions/checkout@v4`; no separate PAT, GitHub App
token, deploy key, or secret is required for a same-repository push when the job's
`GITHUB_TOKEN` has `contents: write`.

## Downstream workflow effect

There are two independent protections against an accidental workflow cascade:

1. Current repository branch/path filters do not match a push to a separate R291/R290
   research branch: the three research execution workflows listen only to
   `research/control-v2` plus one exact trigger file each, while the control checker's
   push trigger listens only to `main`.
2. GitHub's first-party `GITHUB_TOKEN` documentation states that events generated by
   the repository's `GITHUB_TOKEN` do **not** create another workflow run, except for
   explicit `workflow_dispatch` and `repository_dispatch` events (and documented
   approval-state behavior for PR events). A plain `git push` therefore does not
   recursively launch push workflows.

Primary source:
https://docs.github.com/en/actions/concepts/security/github_token

No current workflow uses a downstream `repository_dispatch` or `workflow_dispatch`
call as a side effect of a push.

## Storage and cost

This path writes ordinary Git objects, not Actions artifacts.

GitHub documents standard GitHub-hosted runner usage as free for public repositories.
R287 already established that compute-side fact for this repository; its unresolved
cost issue was specifically durable **artifact storage**, which shares plan allowance
with GitHub Packages.

Primary billing source:
https://docs.github.com/en/billing/concepts/product-billing/github-actions

GitHub's repository docs state that GitHub Free supports unlimited public repositories.
The usage-based product billing documentation separately meters Actions artifacts,
Packages, Git LFS, Codespaces, etc.; ordinary Git repository content is instead governed
by repository/file limits.

Primary sources:
https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories
https://docs.github.com/en/billing/concepts/product-billing

Repository-size source:
https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits

Relevant limits:

- recommended repository on-disk maximum: 10 GB;
- recommended individual Git file size: 1 MB;
- enforced individual Git file limit: 100 MB.

The current repository is about 19.6 MiB by the repository API. Adding at most
1.301 MiB keeps it around 20.9 MiB, far below the repository recommendation.
The 1,228,800-byte `vectors.f32le` is slightly above GitHub's 1 MB *recommended*
individual-file size but far below the 100 MB enforced limit. This is a non-blocking
repository-health note, not a billing or push blocker.

Because the capture is stored as normal Git and does not use Git LFS, the separate Git
LFS storage/bandwidth billing model does not apply.

Git LFS billing source:
https://docs.github.com/en/billing/concepts/product-billing/git-lfs

## Minimal safe future persistence boundary

For the later separately authorized run:

1. use the already-proven public standard GitHub-hosted runner path;
2. keep the estimator/capture job permissions read-only except the smallest job that
   performs persistence, which gets exactly `contents: write`;
3. seal and verify the R288 capture before any Git operation;
4. use a pre-existing research branch verified `protected:false` immediately before
   authorization;
5. commit only the sealed `vectors.f32le`, `manifest.json`, `SHA256SUMS`, and a
   small run receipt/identity record;
6. push with the repository `GITHUB_TOKEN`;
7. do not call `actions/upload-artifact`, Packages, LFS, cache-save, release assets,
   `repository_dispatch`, or `workflow_dispatch` for persistence;
8. after the run, verify the branch commit SHA and file SHA256 values through the
   repository API.

A direct push should fail closed: if `git push` is rejected, do not fall back to a PAT,
artifact upload, LFS, or paid storage inside the same run.

## Remaining account-owner input

**No billing/usage-dashboard input is required for this persistence mechanism.** The
R287 missing input applied to Actions artifact/Packages shared storage; this design does
not consume that storage pool.

If a new result-only branch is required rather than an existing verified research
branch, the only remaining pre-run input is a repository-state fact, not a billing fact:
the owner/coordinator should pre-create that branch and confirm its branch API reports
`protected:false`. Safe fallback if that is not done: use an existing verified
unprotected research branch, or do not persist the capture; do not switch to
`upload-artifact`.

## Accounting

- Actions triggered: 0
- capture/result commits attempted: 0
- artifacts uploaded: 0
- packages/LFS/cache used: 0
- dependencies installed: 0
- datasets downloaded: 0
- paid resources: 0
- private/holdout/full accesses: 0
- submissions: 0
- PR #35 changes: 0
- leaderboard/canonical edits: 0

R290's own append-only report/receipt commits are audit records only and are not a test
of the future capture persistence path.
