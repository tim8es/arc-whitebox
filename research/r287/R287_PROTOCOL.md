# R287 Protocol — zero-incremental-cost public runner audit

Job: R287  
Owner: `phase2-free-runner-audit`

## Question

Determine, without triggering Actions or installing/downloading anything, whether one future public-development V25 residual-capture job can be run on the repository's existing GitHub-hosted runner path at **zero incremental charge**, using:

- Python 3.11 pinned as in R209;
- WhestBench 0.16.1;
- FlopScope 0.12.1+np2.4.6;
- the public `v2-phase2 mini:all-100` dataset;
- the R278/R282 runner-side capture seam.

## Evidence split

Separate:

1. **documented public facts** — GitHub's official pricing/runner/timeout documentation and public repository metadata/workflow YAML;
2. **account-specific unknowns** — any billing-plan, spending-limit, Actions disablement, quota, policy, or storage state not visible from public repository metadata.

A zero-cost conclusion is allowed only if the actual target account/repository/runner path is proven not to incur incremental compute or storage charges and has sufficient execution eligibility. If any account-specific fact required for that conclusion is not provable from the allowed evidence, verdict = `WAITING_INPUT`.

## Repository/runtime facts to verify

- repository visibility;
- exact `runs-on` label used by the successful pinned R209/R223 public runs;
- Python setup version;
- pinned toolchain install command;
- dataset fetch path;
- job timeout and scorer wall/memory limits;
- whether the selected label is a standard GitHub-hosted runner rather than a larger runner or self-hosted runner.

## Constraints

No Actions trigger/rerun, no workflow edits, no package/data download/install, no paid/private/holdout/full access, no submission, no canonical/leaderboard edits.
