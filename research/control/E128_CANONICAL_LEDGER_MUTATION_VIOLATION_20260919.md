# E128 canonical-ledger mutation control violation — 2026-09-19

Status: **CONTROL VIOLATION / FAIL CLOSED**

Authoritative control predecessor: `7a584d49a251d1455d0c8339fcd0ca74d302f25b`.

## Live evidence

A new durable successor identity exists after the prior E121 blocker: branches `research/e128-owner-integrator-20260919` (tip `0e3be575ab59f03c436875e16e98f99c8f6278d8`) and `research/e128-integrate-e121-20260919`.

On the integration branch, Actions run `35464820658`, attempt 1, job `105955125768`, head `bffda2a7f7ebc80edee842dd64d64582fbab1405`, concluded `success`. The job explicitly ran `python scripts/e128_append_e121_ledger.py` and then step `Commit canonical ledger candidate`. No artifact was emitted by that run.

The resulting bot commit is `6f0b294134bee4b1818bdf0739ece0b99865895a`, message `research(E128): append verified E121 terminal NO-GO to ledger`. Its only reported changed file is `research/ledger.csv`, adding an E121 row. Therefore a workflow performed a canonical/ledger mutation while this control regime explicitly prohibits canonical/ledger mutation.

A subsequent CI run `35464838652` on head `6f0b294134bee4b1818bdf0739ece0b99865895a` completed with conclusion `failure`; that does not undo the durable ledger mutation on the integration branch.

This note does **not** reinterpret E121 science. E121 remains terminal NO-GO under the previously recorded evidence gate. E119 remains terminally closed and its sole authoritative scientific execution remains run `35458020001`, job `105936659806`, artifact `10589345345`, ZIP SHA256 `7485a4380bca0175197afeb327aed9abeb2f5d14ca335cdff6571ad0c7ed78e3`.

## Classification

`E128_CANONICAL_LEDGER_MUTATION = CONTROL_VIOLATION`

No GO, successor reservation, or scientific authorization is inferred from the E128 integration workflow or ledger row. In particular, a successful governance/integration workflow cannot satisfy the protocol-first scientific gate for any E121+ candidate.

## Exactly one bounded correction

**Correction C-E128-1:** disable/remove the E128 automatic ledger-write path from successor intake and keep all E121+ evidence integration append-only on `control/arc-deep-error-frontier-20260919`; do not mutate `research/ledger.csv` again unless a later explicit control decision lifts the canonical/ledger freeze.

Until that correction is evidenced, successor science remains fail-closed under the standing protocol-first gate; this monitor does not dispatch, rerun, cancel, merge, or mutate scientific branches.
