# ARC research instructions — process v2

The user authorized an effective experimental research system on 2026-09-22.
For current work, this policy supersedes older manager-imposed blanket rules
(`one run ever`, `no repair`, `no code execution`, `no ledger update`, universal
`<=0.135B`, and blanket exclusion of approximate method families).
Preserve historical protocols and receipts as historical evidence. Never rewrite a
failed historical outcome as success. Official competition rules and user limits prevail.

Start with [research/RESEARCH_PROCESS.md](research/RESEARCH_PROCESS.md),
[STATUS](research/control/STATUS.md) and the live
[control state](https://github.com/tim8es/arc-whitebox/blob/research/control-v2/research/control/state.json).
Agents on old research branches must read these files from current `origin/main`.

## Before work

- Confirm an executable checkout and access to required artifacts. Use the available
  GitHub connector or a Git checkout; a missing checkout in one runtime is not a scientific rejection.
- Search `research/history.json` by mechanism, ID and prior assumptions. Its declared
  historical statuses are not automatically a current scientific verdict.
- Only the coordinator allocates a job and assigned owner. Publish the claim with
  `python scripts/arc_control.py claim R201 --owner baseline --publish` in the control
  checkout. Use YOUR assigned job and owner. Dry-run output is not ownership.
- A non-fast-forward rejection means another state change won: read the new state.
  Never force push, create a second owner lane or restart merely because a message repeated.
- Before actual execution publish `start` with run ID, code commit and command;
  after completion publish `finish` with a durable receipt. `active` chat status is
  not evidence of an experiment running.

## Science and evidence

- Optimize official per-network adjusted scores, averaged across the SAME panel.
  `0.135B` is not the official budget limit. Below `0.1B`, cheaper compute alone
  does not improve score. Preserve official failures and resource limits.
- Approximation is allowed; exact identities are mandatory only where the method
  claims an exact rewrite. Diagnostic D21 error is not the competition objective.
- Exploration permits debugging, profiling and bounded parameter search on development
  data. Log every attempt. Repair infrastructure errors with a new attempt under the
  same job; code/parameter changes require explicit versioning.
- Freeze a candidate before confirmation. Do not tune on confirmation outputs, hide
  failed runs, cherry-pick seeds, or label previously exposed networks as fresh holdout.
- Compare with immediate parent AND strongest reproducible candidate on identical
  data/versions. Report absolute score, measured FLOPs, uncertainty across networks,
  failures and tail regressions; never transfer an improvement percentage across methods.
- Missing inputs => WAITING_INPUT. Noisy result => INCONCLUSIVE. Infrastructure failure
  => INFRA_ERROR. A scientific rejection must specify the tested configuration and scope.
- Store inputs/outputs and reports durably with hashes. Seeds and run IDs are strings.
  Publish a normalized result in `research/results` with a pinned receipt URL, then
  regenerate the overview. Validation and historical receipt claims are separate.

## Limits and handoff

Research spending cap remains $100 TOTAL. Current remainder is unknown: do not start
new paid resources until reconciled. Reuse existing/free compute where verified.
Do not submit to the competition from a research worker. Prepare the package and
evidence; the coordinator handles the release decision under the user's authority.
Do not create competing schedules or guard tasks. This Control Center is the single
dispatcher. Reviewer jobs become claimable when their exact dependencies complete.
Finish with result/attempt ID, commit, receipt, measured conclusion and next useful task.
