# E104 post-production process instructions — owner handoff

Instruction key: `ARC-OWNER-E104-PROCESS-INSTRUCTIONS-20260919`

Owner branch: `research/owner-frontier-e094-e104-20260919`

This commit is a process-only correction. It changes no experiment result, mechanism, metric, scientific verdict, competition verdict, canonical state, or ledger state.

## Evidence that must be consumed

Authoritative E104 identity:

- branch: `research/e104-haar-radial-raoblackwell-20260918`
- local scientific result commit: `785be77d27eb6770b251a87182184281fb571949`
- independent production verifier run head: `95c353cc9cc6ca15837fc3da5d2cdd22d2ee2323`
- production-shaped run: `35446062235`
- job: `105905067035`
- artifact: `e104-production-independent-verify`
- artifact ID: `10584569066`
- artifact ZIP SHA256: `3a22b369883b141be19528acec69df9165be627976152ad845e35c5f90320237`
- production verification receipt commit: `4c90b7d7b1f798f5706f368d80f23f8b98fa66b2`
- owner production-gate reconciliation commit: `419cabc034ca06938ee57ce909ed97d60a1ec0c2`

Verified production-shaped facts:

- workflow conclusion: success
- width/depth/trajectories: `1024 / 16 / 4096`
- prediction shape: `[16,1024]`
- finite: true
- prediction bitwise replay: true
- prediction repeat max abs: `0.0`
- antithetic pair max abs: `0.0`
- exact FLOP reconciliation: true
- reconciled/flopscope total: `149047442096`
- utilization: `0.06777892944955966`
- utilization <= 0.12: PASS
- utilization <= 0.135: PASS
- public/scorer/holdout/full targets read: false
- raw competition MSE evaluated: false

## Required owner behavior

1. Treat E104 production-shaped verification as **complete and sealed**. Do not rerun it for confirmation or tuning.
2. Preserve the classification exactly:
   - local scientific GO: preserved;
   - production-shaped verification: PASS/VERIFIED;
   - competition/raw-MSE GO: **not established**;
   - `scientific_go=false` at competition level remains unchanged.
3. Do not relabel synthetic production-shape verification as public/competition accuracy evidence.
4. Do not mix evidence from the same-ID collision `research/e104-orthogonal-antithetic-complete-billing-20260918` into the authoritative Haar/Rao-Blackwell E104 identity.
5. Do not mutate canonical `research/bootstrap`, the canonical ledger, or E104 experiment history as part of this handoff.
6. The already-recorded successor assignment remains **E105 only**, as frozen in owner addendum commit `eec00f043be542248680ffa8606e435fcb9b6b4c`.
7. E105 must be protocol-first, target-free, synthetic production-shape only, with frozen seeds, deterministic replay, complete flopscope accounting, immutable run/job/artifact/digest receipt, and no public/public-mini/scorer/holdout/full access.
8. Any later promotion claim must cite the E104 production run and receipt above and must keep the unresolved absolute competition-distribution/raw final-layer MSE explicit until separately measured under an authorized protocol.

## Stop conditions

Stop and record a correction instead of proceeding if any proposed owner action:

- reruns or tunes E104;
- changes E104 mechanism/shape/seeds after the frozen receipt;
- treats utilization success as accuracy success;
- mixes same-ID collision evidence;
- accesses public/scorer/holdout/full without a separately authorized protocol;
- changes the successor identity away from the already-assigned E105 without an append-only owner reconciliation.

This instruction artifact exists solely to make the post-E104 owner handoff independently auditable.
