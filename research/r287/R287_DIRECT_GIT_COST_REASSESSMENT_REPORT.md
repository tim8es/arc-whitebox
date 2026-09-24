# R287 reassessment — zero-cost gate after direct Git persistence

Status: **COMPLETE — PUBLIC STANDARD RUNNER COST VERIFIED / ARTIFACT QUOTA BLOCKER SUPERSEDED / NO RUN AUTHORIZED**

Job: R287  
Run ID: `R287-direct-git-cost-recheck-20260924-controlcenter`  
Owner: `Control Center 7.09`

## Previous blocker and change in plan

The first R287 attempt correctly ended `WAITING_INPUT` because the earlier persistence plan required 1 MiB of account-specific GitHub Actions artifact/GitHub Packages storage. R290 later verified direct Git persistence, and current PR #36 uses that design: capture files are pushed to a pre-created research branch with the built-in token; no Actions artifact, Git LFS, cache, PAT, or package storage is used. The old storage-quota input is therefore no longer needed for this workflow.

## Current exact workflow evidence

Reviewed PR #36 head `f6fb9018504632edffa1fb80d14ce8a68f442602` (still open/draft/unmerged), workflow blob `19f6f95ceb2cacef5497eafd5e31e20e86cfad8c`, and protocol blob `cc51198550b0d35b7fb0e34e8b072d74a456476c`.

- The repository is public (`private=false`); current GitHub metadata reports size 20,884 KB.
- Both jobs use standard `ubuntu-24.04` runners. GitHub documents standard hosted runner use as free and unlimited for public repositories: <https://docs.github.com/en/actions/reference/runners/github-hosted-runners>.
- GitHub separately bills included Actions artifact storage when used and shares that allowance with GitHub Packages: <https://docs.github.com/en/billing/concepts/product-billing/github-actions>. The current workflow has no artifact/package/cache/LFS path; it uses two direct Git pushes with exact expected-tip leases.
- The exact R293 offline preflight was run against files fetched at the reviewed PR head; result **PASS**, exit 0. It verified the runner label, direct persistence gates, R294 patch and frozen source artifacts, action SHA pins, and exact four-file allowlist. Runtime: Python 3.13.13. No Actions, dependencies, or data were downloaded or installed.
- The required result branch `research/r293-v25-capture-result` is still absent. The protocol explicitly forbids branch creation, merge, Actions run, and benchmark until separately authorized.

## Conclusion

The R287-specific billing blocker is resolved: standard GitHub-hosted compute for this public repository is documented as $0, and the workflow no longer consumes the Actions artifact-storage allowance. This is a cost/preflight determination, not authorization to run. No account-specific billing page was accessed, no external dataset/dependency fetch was performed, and no one-shot capture or benchmark was started.

Next required gate is explicit authorization to create the pre-existing result branch, merge PR #36, and dispatch the one-time public mini capture. No paid service, holdout, repeated run, or submission is included.
