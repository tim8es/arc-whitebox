# R255 independent postflight — R254 terminal infrastructure evidence

Status: **COMPLETE — R254 independently confirmed INFRA_ERROR; scientific result UNEVALUATED**

R255 is read-only postflight. It did not edit R254/R256, trigger or rerun Actions,
execute science, access private/holdout data, submit, alter leaderboard state, or edit
canonical estimator/result files.

## Queue provenance

- assignment control revision: 252
- assigned owner: r254-independent-verifier
- dependencies checked COMPLETE: R249, R253
- claim revision/commit: 253 / b5887ca4a6a363513c2f4283f81502fb2b3cdd65
- start revision/commit: 254 / 401e24e5d9e8704a4c58c08a51c59497b4a884e9
- R255 run id: R255-r254-independent-postflight-20260923

## Immutable R254 subject

- branch: research/r254-balanced-rider-reduction-20260923
- terminal receipt commit: 9a97e04bf0563e593c7fa9d6437410227d30dc1c
- terminal receipt blob: 7a5fc131fa8221bf642225208a5a49ad972b4663
- terminal report commit/blob: 1930a284ace35fd14c8351aa21d4a15abaaa8191 / 24f4f0e9f68b137006383f5141e0e680ec492d0a
- Actions run/job/attempt: 35834163527 / 107093511576 / 1
- workflow head: ff40219e132ce208428b7acfb1a03a79cd535be7
- workflow path/blob: .github/workflows/r254-one-shot.yml / 649e7b9184e0d8521636fd1af23fb9e4359b3a64
- artifact: 10737609819 (r254-one-shot-evidence)
- artifact ZIP SHA256: 9512985e1af5a98afa9d4ca4e87f6935d8e15ac9c73a28a3a7f0c3ddc5db05e7

GitHub metadata independently shows exactly one R254 branch Actions run and attempt 1.
The run and job both have GitHub conclusion success.

## Workflow success versus research status

The green Actions conclusion does not mean a completed scientific result. Workflow step
8 launches research/r254/r254_one_shot.py with set +e, records its real exit code and
sets go=false on failure, then deliberately exits 0 so the always-run receipt/hash and
artifact-upload steps can preserve evidence. Downstream validation/public steps require
targetfree go=true and are skipped otherwise.

Independent ZIP inspection verified:

- ZIP SHA256 equals the pinned digest above;
- target_free.exit is 1;
- R254_TARGET_FREE_RESULT.json is absent;
- R254_WORKFLOW_RECEIPT.json decision is INFRA_ERROR_BEFORE_TARGET_FREE_RESULT;
- target_free.stdout is empty;
- validation/public identity/public report/public gate files are absent;
- R254_ARTIFACT_HASHES.json contains 15 entries and every listed SHA256 recomputes.

Therefore GitHub workflow success and research INFRA_ERROR are simultaneous,
non-conflicting facts.

## Exact BudgetContext.summary() mismatch

Frozen harness source research/r254/r254_one_shot.py has Git blob
52f1885fcb4fc3cfb99a0ad2fc6b8517187605d9.

Its relevant frozen logic is:

- line 76: enter flops.BudgetContext(...) as ctx;
- line 78: summary = ctx.summary();
- the returned value is stored as budget_summary;
- line 148: p.get("budget_summary", {}).get("residual_wall_time_s", 0.0).

Immutable target_free.stderr terminates at line 148 with the exact exception:

AttributeError: 'str' object has no attribute 'get'

stderr SHA256:
f0cdc771a5aee2138284e809fbbc5c2e769698bd31ddda1907bafc0b50b2a386

The official FlopScope 0.12.1 release commit
b599f015b0bc005b1edb6d7a1b10e0814675e693 confirms the API contract in
flopscope-client/src/flopscope/_budget.py, Git blob
93349b139b3a08bdd67a7bc37b1b446c681c835c:

- summary_dict(...) returns dict;
- summary(...) is annotated -> str and formats summary_dict(...).

So R254's failure is exactly a harness telemetry/type-boundary defect: code treated the
string from BudgetContext.summary() as a mapping. It is not scientific evidence for or
against BPK2K.

## Frozen source and fixture hashes

Repository identities at executed head:

- protocol blob: ad7a12dea1895d703af53dcef2828370bb4448da
- candidate spec blob: 6bffbdfd113bba80cc72cd375cdc44138f9c0845
- fixture manifest blob: 5a6eb7bbfc07bf9e6609ee6cfbb2b2ea9e17ebf8
- novelty/formula audit blob: 16220bd884bc27a44f8e9fa3fc25a37d43d12312
- fixture generator blob: 141466b6c4aae6cc61fe086860dc0766a08d6968
- one-shot harness blob: 52f1885fcb4fc3cfb99a0ad2fc6b8517187605d9
- workflow blob: 649e7b9184e0d8521636fd1af23fb9e4359b3a64

Pinned unchanged V25 parent:

- upstream Git blob: 195373a110215256b759d7c172ba8c923c62e5cc
- persisted source SHA256: c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20

Generated candidate persisted source SHA256:
55cc395d69309dcb13c38ae3b91032dd4b8d0d6b6caf5eb09f0dad03328723e0

Frozen fixture:

- id/seed: R254-MONOMIAL-PATH-254001 / 254001
- concatenated-weight SHA256: 199e5fd8c669ec927717a12f0a3bbcee83e37db8db6e61e8c50eb791f457b3f0
- truth SHA256: 58354221cedab39e900d78040a8383df45672425389f3865b731eea7b0063f1d
- runtime fixture manifest SHA256: 4c14e8b3907907c73d061a9d46575d0847971aa8fda3ef642826c7118b33e105

The runtime manifest records replay equality for concatenated weights, truth, and all
16 per-layer hashes against the frozen manifest.

## Execution and persisted-measurement accounting

Frozen source control flow and retained stderr establish:

- unchanged parent executions: 1
- candidate constructions: 1
- candidate executions: 1

The persisted artifact establishes:

- persisted parent scientific measurements: 0
- persisted candidate scientific measurements: 0
- persisted public measurements: 0
- persisted parent/candidate MSE ratio: unavailable
- persisted parent/candidate FLOP ratio: unavailable
- persisted target-free candidate-gate verdict: unavailable

R255 does not reconstruct, infer, quote, or promote numerical scientific values that
existed only in process memory.

## No validation/public/mini-100

GitHub marks steps 9–12 skipped:

- candidate validation
- exact R209 public row/network/target identity
- exact public R209 mini-100 candidate run
- frozen public gates

Corresponding artifact and exit files are absent. The workflow receipt stores null for
validate_exit, public_identity_exit, public_exit, public_gate_exit and public payloads.
Thus public/mini-100 scientific measurements are zero.

## Independent conclusion

**R254 remains terminal INFRA_ERROR.**

The workflow infrastructure completed successfully enough to preserve failure evidence,
but the research harness failed before serializing a target-free scientific result.
BPK2K accuracy and cost gates are UNEVALUATED. Evidence supports neither scientific GO
nor scientific rejection and supports no numeric MSE/FLOP claim.

## Source links

- https://github.com/tim8es/arc-whitebox/actions/runs/35834163527
- https://github.com/tim8es/arc-whitebox/actions/runs/35834163527/job/107093511576
- https://github.com/tim8es/arc-whitebox/actions/runs/35834163527/artifacts/10737609819
- https://github.com/tim8es/arc-whitebox/blob/ff40219e132ce208428b7acfb1a03a79cd535be7/.github/workflows/r254-one-shot.yml
- https://github.com/tim8es/arc-whitebox/blob/ff40219e132ce208428b7acfb1a03a79cd535be7/research/r254/r254_one_shot.py
- https://github.com/tim8es/arc-whitebox/blob/ff40219e132ce208428b7acfb1a03a79cd535be7/research/r254/R254_FIXTURE_MANIFEST.json
- https://github.com/tim8es/arc-whitebox/blob/9a97e04bf0563e593c7fa9d6437410227d30dc1c/research/r254/R254_RECEIPT.json
- https://github.com/AIcrowd/flopscope/commit/b599f015b0bc005b1edb6d7a1b10e0814675e693
- https://github.com/AIcrowd/flopscope/blob/b599f015b0bc005b1edb6d7a1b10e0814675e693/flopscope-client/src/flopscope/_budget.py
