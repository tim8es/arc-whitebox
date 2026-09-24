# R302 — repair and exact replay of the R296 workflow security self-check

Status: **COMPLETE — COMMITTED CHECKER FIXED / 21 OF 21 CHECKS PASS / NO ACTIONS RUN**

Job: R302  
Run ID: `R302-r296-selfcheck-repair-20260924-controlcenter`  
Owner: `Control Center 7.09`

## Finding and correction

Independent execution of the committed R296 checker at PR head `c3cb55870d9cc313e1323fd92fb5778b3e74b796` failed before reaching its CAS matrix. `git` is defined as `git(args, cwd, ...)`, but `set_remote` called `git(repo, args)`, producing `TypeError: Value after * must be an iterable, not WindowsPath` at line 172. This contradicted the PASS claim in the original R296 receipt.

R302 made only the argument-order correction in `scripts/r296_workflow_security_selfcheck.py`; the R296 report and receipt remain unchanged. Correction commit: `bf7a613652c669f350451196ea9fbb706ad05550`.

- corrected checker Git blob: `e6c975a72f8f4863b476bfe5b636984fe1169713`
- corrected checker SHA-256: `0392e2c88d7c9f6cb75813cc330cdd699217d9537957d428d3d183edd9673da0`
- workflow blob/SHA-256: `19f6f95ceb2cacef5497eafd5e31e20e86cfad8c` / `23cb8b2a4db23b6dd030b6148cfaa8d6d2cb45e31ff264195c970117fd69f863`
- protocol blob/SHA-256: `cc51198550b0d35b7fb0e34e8b072d74a456476c` / `e0e36f5107676326529359f238b678b03d5faf25fae913d102387dc6ba1f3a74`

## Exact replay

The corrected committed checker and exact workflow/protocol files were fetched by their pinned GitHub blob identities and executed from an isolated temporary directory (no repository clone). Environment: Python 3.13.13, Git 2.55.0.windows.3. Invocation: `python check.py --workflow workflow.yml --protocol protocol.json`.

Result: **PASS, 21/21 checks; failed=[]; exit code 0.** This includes action SHA pins, rerun and duplicate-dispatch gates, both atomic CAS success paths, rejection of stale/moved/deleted refs at claim and final persistence, process-only credential helper non-persistence, protocol gates, and token/remote checks.

Checks passing: `checkout_full_sha`, `claim_cas_success`, `claim_expected_dispatch_tip`, `deleted_before_final_not_recreated`, `deleted_branch_not_recreated`, `durable_claim_before_install`, `final_cas_success`, `moved_before_final_rejected`, `moved_branch_rejected`, `no_mutable_action_tags`, `process_scoped_helper_not_persisted`, `protocol_no_branch_creation`, `protocol_no_rerun_or_second_dispatch`, `rerun_gate_two_jobs`, `rerun_or_second_dispatch_lease_rejected`, `result_expected_claim_tip`, `setup_python_full_sha`, `stale_final_lease_rejected`, `token_not_in_remote`, `token_only_two_minimal_steps`, `two_atomic_leases`.

## Boundaries

PR #36 remains open/draft/unmerged. No Actions, benchmark, estimator, real capture vectors, dataset/dependency install or download, paid resource, result-branch creation, holdout, submission, leaderboard edit, or canonical-result edit occurred. This correction validates the workflow safety self-check only; it is not scientific score progress and does not authorize dispatch.
