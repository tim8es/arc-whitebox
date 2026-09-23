# R260 terminal report — BPK2K target-free scientific rejection

Status: **SCIENTIFIC_REJECT_TARGET_FREE / PUBLIC SKIPPED / NO RETRY**

## Frozen control

- run ID: `R260-BPK2K-ONE-SHOT-20260923-A1`
- protocol commit: `0b47b5ebeb965ebac01748133af57607f4dbc7b1`
- workflow commit: `47ab8c616665e6086e1b8c6f49acd937dab2d776`
- arm commit: `ed4ffbe1029d08cdc48648dc7a2877df308bba3d`
- branch: `research/r260-bpk2k-replay-schema-one-shot-20260923`
- immutable R259 terminal base: `be1f8e92dbf3a2adb4d5dcd75c2ff345454ac47b`
- R259 receipt SHA256:
  `dd1c5c0d9941941cb00153e076c09cb51743966f0486579de85ac70f97af1fe1`

Coordinator inspection passed before the sole arm commit. No other workflow/code change
occurred after the frozen workflow.

## Sole Actions execution

- GitHub Actions run: `35843525739`
- job: `107124034819`
- attempt: `1`
- head: `ed4ffbe1029d08cdc48648dc7a2877df308bba3d`
- runner: standard GitHub-hosted `ubuntu-24.04`
- workflow conclusion: **success**
- artifact: `10741778766` (`r260-one-shot-evidence`)
- artifact ZIP SHA256:
  `5f5522220664c028bef19906d66213826061bd85758ca63e01934f59aef9e22d`

Exactly one R260 Actions workflow/attempt exists. No retry or second workflow was
dispatched.

## Pre-science controls

All repaired infrastructure gates passed:
- full-history checkout;
- protocol ancestry and post-protocol changed-path guard;
- frozen source Git-blob/SHA256 checks;
- static replay-schema preflight on sealed R259 manifest;
- Python 3.11.16;
- pinned NumPy 2.4.6 / FlopScope 0.12.1 / WhestBench 0.16.1 wheel hashes;
- pinned V25 parent download/hash;
- exact fixture generation;
- fresh runtime replay-schema preflight before parent.

Fixture is exactly frozen:
- seed: 254001
- weights SHA256:
  `199e5fd8c669ec927717a12f0a3bbcee83e37db8db6e61e8c50eb791f457b3f0`
- truth SHA256:
  `58354221cedab39e900d78040a8383df45672425389f3865b731eea7b0063f1d`
- replay_equal=true
- 16 top-level layer hashes exactly equal 16 nested replay hashes
- top-level/nested weights and truth hashes agree.

## Parent execution

The unchanged pinned V25 parent executed first and passed:
- source SHA256:
  `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`
- shape: [16,1024]
- final-layer MSE: `0.06571899191579027`
- all-layer MSE: `0.032378284555651254`
- FLOPs: `806303721965`
- residual wall time: `0.32413096299903543` s
- finite on all 16 layers
- max symmetry residual: 0
- parent_go=true; parent_failures=[].

## BPK2K target-free result

The unchanged BPK2K candidate was constructed and executed exactly once:
- candidate source SHA256:
  `55cc395d69309dcb13c38ae3b91032dd4b8d0d6b6caf5eb09f0dad03328723e0`
- shape: [16,1024]
- final-layer MSE: `0.06574015420536944`
- all-layer MSE: `0.032379599124054775`
- FLOPs: `806303721965`
- residual wall time: `0.31171112699985315` s
- finite on all 16 layers
- max symmetry residual: 0.

Frozen gate reconciliation:

| Gate | Observed | Requirement | Result |
|---|---:|---:|---|
| final MSE ratio | 1.0003220117801912 | <= 0.95 | **FAIL** |
| all-layer MSE ratio | 1.0000406003104105 | <= 0.98 | **FAIL** |
| improved layers | 13 | >= 12 | PASS |
| max layer degradation ratio | 1.0003220117801912 | <= 1.10 | PASS |
| FLOP ratio | 1.0 | <= 1.0 | PASS |
| candidate residual | 0.31171112699985315 s | <= 0.3453375111489872 s | PASS |
| finite / shape / symmetry / source | valid | required | PASS |

Candidate failures are exactly:
- `final_mse_ratio`
- `all_layer_mse_ratio`.

For descriptive context only, candidate minus parent:
- final MSE delta: `2.1162289579171323e-05` (+0.0322011780%)
- all-layer MSE delta: `1.3145684035209548e-06` (+0.0040600310%).

The target-free result decision is
`SCIENTIFIC_REJECT_TARGET_FREE`; `target_free.exit=31`.

## Public-stage firewall

Because target-free candidate_go=false:
- candidate validation: skipped
- live exact R209 mini-100 identity check: skipped
- public mini-100 candidate run: skipped
- per-network public evidence: not produced
- public gates: skipped.

No public score or rank claim is made.

## Workflow versus research conclusion

These are intentionally distinct:
- GitHub workflow conclusion: **success** (the workflow preserved terminal evidence);
- research/scientific conclusion: **SCIENTIFIC_REJECT**;
- detailed decision: **SCIENTIFIC_REJECT_TARGET_FREE**.

This is not an infrastructure failure.

## Artifact integrity

The artifact contains 27 files. `R260_ARTIFACT_HASHES.json` maps 26 files and all 26
hashes independently recompute with zero mismatches.

- artifact ZIP SHA256:
  `5f5522220664c028bef19906d66213826061bd85758ca63e01934f59aef9e22d`
- workflow receipt SHA256:
  `fa26f3f1b8072929bdba07783b8a7054da9cdcd768b4446b95a047832ed7b79d`
- target-free result SHA256:
  `2125e0e0cef4830768353264fd5192c7d88128b3ee7e99ee457546e6abbdea52`
- artifact hash-map SHA256:
  `9e2d52f360cb03dcf4f7e80df932b225265d3310d5319cf01279baacecb57879`

The full workflow receipt and target-free payload remain in immutable artifact
`10741778766`; the complete 26-entry artifact hash index is committed alongside this
report.

## Terminal disposition

R260 is terminal **SCIENTIFIC_REJECT** under the one-shot/no-rerun protocol. BPK2K
failed the two frozen accuracy gates on the target-free fixture despite passing cost,
timing, improved-layer, degradation, finite, shape, symmetry and source gates.

No retry, tuning, paid/private/holdout/full execution, R223/R244 artifact access,
submission, leaderboard/canonical edit, or R254-R259 history rewrite occurred.
