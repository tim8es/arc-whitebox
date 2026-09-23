# R267 — R257–R260 execution postmortem

**Outcome:** postmortem complete. Historical workflows, receipts, and scientific results were not changed. No new Actions run, estimator run, or dataset access occurred.

## Verified timeline

| Job | Verified failure/result | Parent / candidate executions | Public stage |
|---|---|---:|---|
| R257 | The first ancestry guard ran under the default shallow checkout. The pinned protocol ancestor was absent; git merge-base exited 128 with “Not a valid commit name”. | 0 / 0 | Not reached |
| R258 | Full-history checkout fixed R257. Runtime pins, source hashes, V25 source, and fixture replay passed. Workflow requested R254_RUNTIME_FIXTURE_MANIFEST.json while the fixture builder emitted R254_FIXTURE_RUNTIME_MANIFEST.json; FileNotFoundError. | 0 / 0 | Not reached |
| R259 | Filename preflight and fixture replay passed. Workflow then asserted independent_replay.all_layer_hashes_equal, a key absent from the manifest; the actual manifest has replay_equal and 16-element layer_sha256 arrays. KeyError. | 0 / 0 | Not reached |
| R260 | Repaired preflights passed; unchanged parent and candidate each ran once. Target-free accuracy failed: final-MSE ratio 1.0003220118 vs <=0.95; all-layer ratio 1.0000406003 vs <=0.98. Other frozen gates passed. | 1 / 1 | Skipped by the target-free gate |

Each job had exactly one Actions run/attempt; none was retried. R257–R259 produced zero parent/candidate executions and zero scientific measurements. R260 is the only measured experiment in the chain; it is a target-free scientific rejection, not an infrastructure failure. Public mini-100 was not reached in any job.

## Findings

The failures were sequential and independent: shallow history hid the pinned ancestor; after that was fixed, the workflow used the wrong emitted filename; after that was fixed, it still expected a schema field the generator did not emit. Those three failures say nothing about BPK2K accuracy. R260 shows the later infrastructure fixes let the frozen measurement run; it did not improve accuracy, and public evaluation correctly remained closed.

## Smallest useful prevention

Before arming a future workflow:
1. Require full Git history and verify the pinned protocol commit resolves locally.
2. Generate the exact fixture offline and validate the emitted filename and schema that the workflow will consume: replay_equal, exactly 16 layer hashes, and matching top-level/replay hashes.
3. Arm only after both checks pass; preserve the one-attempt rule.

No generic workflow linter was added: these checks belong beside the fixture builder and its specific workflow. The existing R259/R260 preflights are already narrowly scoped; this task was a postmortem.

## Primary evidence

- [R257 terminal report](https://github.com/tim8es/arc-whitebox/blob/c4b46ecacba1876613a6e11b678399d0b1fd83ba/research/r257/R257_TERMINAL_REPORT.md) · [receipt](https://github.com/tim8es/arc-whitebox/blob/c4b46ecacba1876613a6e11b678399d0b1fd83ba/research/r257/R257_RECEIPT.json)
- [R258 terminal report](https://github.com/tim8es/arc-whitebox/blob/d99a52d0d3cf0f1c946de78173588bc258e74b54/research/r258/R258_TERMINAL_REPORT.md) · [receipt](https://github.com/tim8es/arc-whitebox/blob/d99a52d0d3cf0f1c946de78173588bc258e74b54/research/r258/R258_RECEIPT.json)
- [R259 terminal report](https://github.com/tim8es/arc-whitebox/blob/be1f8e92dbf3a2adb4d5dcd75c2ff345454ac47b/research/r259/R259_TERMINAL_REPORT.md) · [receipt](https://github.com/tim8es/arc-whitebox/blob/be1f8e92dbf3a2adb4d5dcd75c2ff345454ac47b/research/r259/R259_RECEIPT.json)
- [R260 terminal report](https://github.com/tim8es/arc-whitebox/blob/5b2be00dc92ff4d0ced32bfaf67f6a691cadd967/research/r260/R260_TERMINAL_REPORT.md) · [receipt](https://github.com/tim8es/arc-whitebox/blob/5b2be00dc92ff4d0ced32bfaf67f6a691cadd967/research/r260/R260_RECEIPT.json)
