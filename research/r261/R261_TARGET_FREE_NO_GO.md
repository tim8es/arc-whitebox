# R261 bounded target-free orthogonal-method result

Status: **EVIDENCE_BASED_NO_GO / NO EXECUTION / NO PUBLIC ACCESS**

## Scope

R261 was transferred as the same previously unstarted job to `orthogonal-method-research-e178-guard`.
This bounded pass used only committed source/protocol/receipts and the already-frozen target-free evidence.
It did not dispatch Actions, access R209/public/holdout/private/full data, use paid compute, submit anything,
or modify R260.

## Candidate considered: disable V25 online mean correction

The pinned V25 parent contains a natural orthogonal accuracy lever: the embedded online mean-correction
rider `CORR_BETA`, guarded by `V17_NO_CORR`. Disabling it would be structurally distinct from R260
BPK2K summation-order work: it changes the estimator correction term rather than floating-point
parenthesization.

However, this is not a defensible new target-free hypothesis.

The V25 source itself documents that `CORR_BETA` was ridge-fitted offline on public teacher-forced
trajectories. More importantly, the committed R254 protocol/history explicitly identifies prior
numerical-stability work and freezes BPK2K only after excluding previously explored families. A new
toggle/ablation of an existing public-fitted accuracy rider has no independent target-free evidence
predicting the mandatory >=5% final-MSE and >=2% all-layer-MSE gains on the frozen R254 fixture.

R260 establishes the relevant scale: parent final MSE `0.06571899191579027`, all-layer MSE
`0.032378284555651254`. Passing R261's inherited accuracy falsifier would require candidate final MSE
<= `0.06243304232000075` and all-layer MSE <= `0.03173071886453823`, plus >=12/16 improved layers.
The known BPK2K perturbation moved final MSE by only +0.0322% and all-layer MSE by +0.00406%.

There is no committed target-free evidence that removing the existing correction rider can plausibly
supply the required multi-percent improvement. Its provenance instead makes the direction scientifically
confounded: it was explicitly introduced as an accuracy correction fitted on public trajectories.
Testing its removal now would be an under-motivated ablation, not a bounded evidence-led orthogonal
successor.

## Result

**NO_GO before execution.** The falsifier is evidentiary: no orthogonal candidate available from the
committed V25 mechanisms has a target-free rationale strong enough to justify even one local production-shape
execution under the bounded R261 assignment. Executing a speculative toggle merely to obtain a number would
be method fishing.

No scientific measurement is claimed for an unexecuted candidate. No public stage is authorized.

## Safety accounting

- local estimator executions: 0
- Actions runs: 0
- public/R209 accesses: 0
- holdout/private/full accesses: 0
- paid compute: 0
- submissions: 0
- R260 edits: 0
- canonical estimator/result edits: 0
