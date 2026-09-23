# R253 — R252 Actions accounting incident report

Status: **READ-ONLY POSTFLIGHT AUDIT**  
Subject: R252 terminal evidence at control revision 241  
R253 run ID: `R253-r252-actions-accounting-audit-20260923`

## Finding

Revision 241 correctly leaves R252 terminal `INFRA_ERROR`, but its current completion projection is materially incomplete. R252 has **one queue attempt and two distinct GitHub Actions runs**, despite the frozen authorization for exactly one standard Actions run and no retry. Neither run reached an unchanged-parent measurement; candidate and public measurements are also zero.

The original revision-241 `finish` event is historical evidence and must remain unchanged. R253 supplies an append-only erratum and a `terminal_evidence_correction` event that updates only the current R252 reason/receipt projection.

## Immutable run accounting

| Run | Method / workflow | Immutable evidence | Terminal pre-science failure | Measurements |
|---|---|---|---|---|
| 35830273198 / job 107081017265 | V25-D21-CWG; `.github/workflows/r252-one-shot.yml`; branch `research/r252-d21-sensitivity-gram-20260923`; head `c00cf0b98016c6fa81c203a6613ce811f585f0c2` | artifact 10736967637; ZIP SHA256 `4ecd1ed42f28a4b02caccd70dce9570a0738d7cb2b4f3976207fdd31f98bb989` | All three pinned wheel SHA256 checks passed. Runtime check then observed Python 3.11.16, NumPy 2.4.6, FlopScope `0.12.1+np2.4.6`, WhestBench `unknown` and compared them to plain exact strings `3.11.16/2.4.6/0.12.1/0.16.1`; exit 1. Fixture, parent/candidate, validation and public steps were skipped. | parent 0; candidate 0; public 0 |
| 35830986191 / job 107083271578 | V25-CFSP4; `.github/workflows/r252-cfsp4-one-shot.yml`; branch `research/control-v2`; head `71ecefb647bb590db14ba4b9d764652dea3d4040` | artifact 10736403843; ZIP SHA256 `10bb14764934b5b46e17cd0abded75ea883310bf2e2ec042c9bd29d2c6c0039e` | Core wheel hashes and runtime versions passed; pinned V25 identity passed; all 16 fixture weight hashes and concatenated weight SHA256 `de5fcc26bb7eaf45f29175cb292f27091b6b13ab6a4f3dc095be96cf402a8d4e` passed. Fixture truth check then raised `RuntimeError: truth hash mismatch` against expected `623f35aaf0a3a9dfc7f9955ea0c45d02b118fc0fa20579f0747116b838d54450`. The failing observed truth digest/bytes were not retained. Parent/candidate/public execution was skipped. | parent 0; candidate 0; public 0 |

Sources:
- run 35830273198: https://github.com/tim8es/arc-whitebox/actions/runs/35830273198
- job 107081017265: https://github.com/tim8es/arc-whitebox/actions/runs/35830273198/job/107081017265
- artifact 10736967637: https://github.com/tim8es/arc-whitebox/actions/runs/35830273198/artifacts/10736967637
- run-1 workflow at immutable head: https://github.com/tim8es/arc-whitebox/blob/c00cf0b98016c6fa81c203a6613ce811f585f0c2/.github/workflows/r252-one-shot.yml
- run-1 frozen D21-CWG protocol: https://github.com/tim8es/arc-whitebox/blob/c00cf0b98016c6fa81c203a6613ce811f585f0c2/research/r252/R252_PROTOCOL.md
- run 35830986191: https://github.com/tim8es/arc-whitebox/actions/runs/35830986191
- job 107083271578: https://github.com/tim8es/arc-whitebox/actions/runs/35830986191/job/107083271578
- artifact 10736403843: https://github.com/tim8es/arc-whitebox/actions/runs/35830986191/artifacts/10736403843
- run-2 workflow at immutable head: https://github.com/tim8es/arc-whitebox/blob/71ecefb647bb590db14ba4b9d764652dea3d4040/.github/workflows/r252-cfsp4-one-shot.yml
- run-2 frozen CFSP4 protocol: https://github.com/tim8es/arc-whitebox/blob/71ecefb647bb590db14ba4b9d764652dea3d4040/research/r252/R252_PROTOCOL.md

## Authorization/accounting conclusion

Both frozen workflows explicitly describe a one-run/no-retry safety boundary. The queue contains one R252 attempt, but GitHub records two distinct push-triggered workflow runs, at 07:09:44Z and 07:18:00Z, with different workflow files and different scientific methods. Therefore the second dispatch is an **unauthorized duplicate dispatch relative to the R252 one-run authorization**. This is an accounting/protocol finding, not a scientific result.

R252 remains `INFRA_ERROR`. There are no parent, candidate or public measurements to interpret.

## Attribution

GitHub API metadata for both runs reports `actor=tim8es` and `triggering_actor=tim8es`. Both run-head commits also report author/committer `tim8es`. This proves the GitHub account attribution visible in immutable run/commit metadata.

**Session/agent attribution is UNKNOWN.** GitHub commit/run evidence does not prove which chat, session or agent initiated either repository write; R253 does not infer it.

## Preservation / R253 boundary

R253 did not delete or replace either artifact or log, did not edit or trigger a workflow, did not rerun R252, and conducted no science. No paid/private/holdout data, submission, leaderboard mutation or canonical estimator change occurred in R253.

Machine-readable erratum: `research/r253/R253_R252_TERMINAL_EVIDENCE_ERRATUM.json`.
