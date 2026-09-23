# R252 terminal report — pre-parent infrastructure failure

Status: **INFRA_ERROR**  
Run ID: `R252-one-shot-actions-global-accuracy-20260923`  
GitHub Actions run: `35830986191`, job `107083271578`, attempt `1`

## Frozen research question

R252 selected exactly one new candidate after full-history deduplication:
**V25-CFSP4**, a final-layer Cornish-Fisher sigma-point response that leaves the pinned
V25 cross-neuron K3/K4 state and layers 0-14 unchanged. The protocol, novelty audit,
fixture construction, byte hashes, source/cost gates and conditional R209 gates were
committed before the workflow existed. R251 GFNP was excluded and treated only as an
infrastructure terminal record.

## One-shot environment evidence

The repository was confirmed public and exactly one standard GitHub-hosted
`ubuntu-24.04` workflow run was triggered. There was no retry.

The run successfully verified:
- Python `3.11.16`;
- NumPy `2.4.6`;
- FlopScope `0.12.1+np2.4.6`;
- WhestBench `0.16.1`;
- NumPy wheel SHA256
  `89cd468399cfd2504718f0ba50e410dca55a170b61a02ad92bb18c8a65186e93`;
- FlopScope wheel SHA256
  `cd08df7e0eb468117b9a48b82d076130a9a9858ec20fdc0d015e2bd477519582`;
- WhestBench wheel SHA256
  `1a8e2620880221eb357056b0fdd65425b026dab222657f54ee202bd75dab987e`;
- pinned V25 Git blob
  `195373a110215256b759d7c172ba8c923c62e5cc`;
- pinned V25 SHA256
  `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`.

## Exact failure

The workflow failed at **Reconstruct and retain exact frozen fixture bytes**, before
parent execution.

The frozen generator first verifies all 16 individual weight-matrix hashes and then the
concatenated weight-byte hash. It reached the later truth check, so those weight-byte
checks passed. The concatenated expected/verified weight SHA256 is:

`de5fcc26bb7eaf45f29175cb292f27091b6b13ab6a4f3dc095be96cf402a8d4e`.

It then raised exactly:

`RuntimeError: truth hash mismatch`

against frozen expected truth SHA256:

`623f35aaf0a3a9dfc7f9955ea0c45d02b118fc0fa20579f0747116b838d54450`.

The generator did not include the computed observed digest in the exception and failed
before writing `fixture-replay.json` or retained truth bytes. Therefore the observed
truth SHA256 is **UNKNOWN**. It would be improper to manufacture it or run again.

The generator's later-layer exact-truth construction uses dense float64 matrix-vector
reductions, so backend-dependent reduction order is a plausible explanation for a
byte-level discrepancy. That is only an inference; the sole retained run does not prove
the numerical cause.

## Stop-rule result

Because the exact frozen target-free fixture/truth identity failed before the mandatory
parent gate:

- parent executions: **0**;
- parent per-layer finite/max-abs/symmetry checkpoints: **0**;
- candidate constructed: **false**;
- candidate executions: **0**;
- target-free scientific comparison: **none**;
- public R209 data access: **none**;
- public mini-100 executions: **0**;
- submissions/leaderboard mutations: **0**;
- retry/rerun: **0**.

This is not evidence for or against CFSP4 and is not a V25 parent failure. The correct
classification is **INFRA_ERROR / no scientific result**.

## Durable Actions artifact

- artifact ID: `10736403843`
- name: `r252-cfsp4-one-shot`
- ZIP SHA256:
  `10bb14764934b5b46e17cd0abded75ea883310bf2e2ec042c9bd29d2c6c0039e`
- size: `46,746` bytes
- run head: `71ecefb647bb590db14ba4b9d764652dea3d4040`

The artifact retains runtime/package identities, V25 source, frozen protocol/novelty/
fixture manifest/scripts, trigger, disposition and an evidence SHA256 manifest. It does
not contain candidate source or public reports because those stages were never reached.

## Governance

R252 is terminal under the user's one-run/no-retry rule. Do not repair or retry this task.
A future new task would require a new preregistration and a fixture truth serialization
whose bytes are defined independently of backend-dependent reduction order.

No paid/private/holdout data, R223/R244 candidate outputs/artifacts, submission,
leaderboard mutation, canonical V25 edit, second method or gate relaxation occurred.
