# R268 — independent audit of R261 control reconciliation

Audit scope: control-only, read-only with respect to R261 history/artifacts. No Actions, science, public/holdout/private data, paid resources, submission, leaderboard, or canonical estimator/result changes were used.

## Snapshot audited

- control branch: `research/control-v2`
- control head: `829887822daf04f5d88ed43c9568d24a4a5e3407`
- control revision: `300`
- `research/control/state.json`
  - git blob SHA-1: `2082543be6bcea905d073fff842b6e6a8f7b916a`
  - SHA-256: `582d85cba96d709abf3bcbcc39ad7b4ad70ce9ce0c60447cae976e7bf1f66fa0`
- `research/control/STATUS.md`
  - git blob SHA-1: `f9943b5d26ade36da636c94c80dd68460ee45978`
  - SHA-256: `9af6a4db93f40a458a081fe9131e185f650800bbb1f217f789544d68362051f2`

## Observations

### 1. Immutable queue events through R261 finish

The append-only queue history records:
- revision 287: R261 claimed by `orthogonal-method-research-e178-guard`;
- revision 288: R261 start with run id `R261-local-target-free-20260923` and the bounded target-free command, but **without `code_commit`**;
- revision 289: R261 finish with status `SCIENTIFIC_REJECT`, decision `EVIDENCE_BASED_NO_GO_BEFORE_EXECUTION`, and an original receipt URL/commit, but **without receipt SHA-256**.

The scientific terminal decision in revision 289 is therefore unambiguous, while the start/finish provenance payloads are incomplete relative to the current `arc_control.py` contract.

### 2. Original R261 report/receipt binding

Original report:
- commit: `933d259ec33c37c88f98df8c214935d02d8b60ca`
- path: `research/r261/R261_TARGET_FREE_NO_GO.md`
- actual git blob SHA-1: `835eee8021cfc8760c50c1b6978dcdabf2e52a2e`
- SHA-256: `34d49ef5f716863e20a752f76c8bebe6c820b4d4db83045511b995f981998509`

Original receipt:
- commit: `c7d0e98a413c0e4fc4e462d7aa65d8eeaae42f66`
- path: `research/r261/R261_RECEIPT.json`
- git blob SHA-1: `47b0d745cd31e8707256f0f7183d0d0212d9442e`
- SHA-256: `dabaa077c1eb70a4f5cf89355e8e262bf555e2ce1f23ac308de457b588885e8e`

The original receipt declares `report_blob = 84df1b3ecbc86c4564a0c29148e49cf57a9a4528`, which does **not** equal the actual report blob `835eee8021cfc8760c50c1b6978dcdabf2e52a2e`. The mismatch is real and preserved.

### 3. Coordinator reconciliation note

The append-only reconciliation artifact:
- commit: `9dfb89faeb33617da2f5ca91d32fa776426e228b`
- path: `research/r261/R261_COORDINATOR_RECONCILIATION.json`
- git blob SHA-1: `5cce867616e893cce4859e26c832fd94e826f153`
- SHA-256: `ceb4aa86da2ac1cd23ecea0bac0d6f4c68668d8d91c103ae39a39af8d155b5c2`

The note correctly records the report/blob mismatch, the missing start `code_commit`, the missing finish receipt SHA-256, and preserves the original report/receipt/event history rather than rewriting them.

### 4. Reconciled source commit provenance

The reconciliation identifies source commit `dff3dd65e9d2210e02418cca99e05556f6bf2c75`.

That commit exists. Independently, the normalized `research/results/R209-v25-mini100.json` record currently carries the same `code_commit` value. This supports the reconciliation's stated provenance basis for the pinned V25 source used by the desk review. No R261 candidate execution occurred, so this is provenance for the reviewed parent/source, not a candidate-run code commit.

### 5. Reconstructed attempt projection

Commit `dd9263eda28e97c15820da62bd4b03c613a29c18` directly repaired the R261 projection in `state.json`:
- restored one attempt with run id/command from revision 288;
- inserted `code_commit = dff3dd65...`;
- projected terminal `SCIENTIFIC_REJECT`;
- replaced the current durable receipt pointer with the reconciliation note and its SHA-256;
- annotated `source_event_revision = 288` and `finish_event_revision = 289`.

At that commit, however, `state.revision` remained `289` and the last entry in `events[]` remained the original revision-289 finish. No append-only `reconcile` event was added.

### 6. Current state/STATUS consistency

At audited revision 300:
- current `state.json` projects R261 as `SCIENTIFIC_REJECT`;
- current `STATUS.md` also displays R261 as `SCIENTIFIC_REJECT`;
- this terminal status agrees with immutable finish event revision 289.

R268 itself is still `QUEUED`, owner unset, assigned owner `r261-control-audit`, attempts empty; current `STATUS.md` agrees.

## Conclusions

1. **Report/blob mismatch handling: verified.** The mismatch is genuine, is explicitly documented by the reconciliation note, and the original artifacts were not rewritten.
2. **Source provenance: supported.** `dff3dd65...` exists and matches the normalized R209 V25 `code_commit`. It is appropriately interpreted as reviewed-parent/source provenance, not evidence of an R261 candidate execution.
3. **Scientific terminal status: consistent.** R261 = `SCIENTIFIC_REJECT` matches immutable finish revision 289 and current STATUS.
4. **Remaining R261 control discrepancy: projection is not event-replay-complete.** The repaired attempt/provenance/receipt projection was written directly into `state.json` by `dd9263e...` without an append-only reconciliation event or revision increment. Therefore the current R261 projection cannot be reconstructed from `events[]` alone; the reconciliation note + direct projection commit are additionally required.
5. **Remaining R268 queue error/blocker:** current `arc_control.py` permits `claim` only when every dependency has exact status `COMPLETE`. R268 depends on R261, whose exact terminal status is `SCIENTIFIC_REJECT`, not `COMPLETE`. Therefore a valid `claim/start/finish` for R268 cannot be published without either changing dependency semantics/job metadata or falsifying/re-writing R261 state/history. This audit does neither.

## Audit verdict

**R261 scientific outcome is preserved and current STATUS is accurate, but control provenance remains non-replayable from append-only events alone. R268 is additionally unclaimable under the current dependency gate because its dependency is terminal `SCIENTIFIC_REJECT` rather than exact `COMPLETE`.**

No R261 artifact, queue event, historical state, leaderboard, canonical result, workflow, or scientific code was modified by this audit.
