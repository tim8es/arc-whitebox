# ARC control update — E151 one-shot consumed before science; E153 held unused

Recorded: 2026-09-21

Control key: `ARC-CONTROL-E151-ONE-SHOT-CONSUMED-20260921`

Status: **FAIL-CLOSED / APPEND-ONLY CONTROL**.

This receipt records the requested control state together with the physical repository state observed immediately after intake. It does not rewrite earlier receipts and does not authorize public/public-mini targets, scorer/holdout/full, sweeps, rescue, reruns, duplicate identities, canonical mutation, ledger mutation, merge, or status-only promotion.

## Closed predecessors

### E147 — TERMINAL SCIENTIFIC NO-GO

Branch:

`research/e147-response-projected-k3-estimator-20260921@da90720ae3ca971fd07cb8e2616eb6b5b95cb363`

Frozen physical evidence:

- protocol: `daf997a9b1204f7916e9f5b78eba3aa6ff113d49`;
- executed arm: `d9b962facec5500d230941df15d607b18b000bdc`;
- run/job: `35550965242 / 106185511147`;
- artifact: `10617789145`, `e147-rap-k3-exact-small`;
- artifact SHA256: `0b0afc633bdd2e5194b8fb943a5a25c0a8cae0226acac664b1c2e4740b31abff`;
- decision: `E147_TERMINAL_NO_GO_CLOSE_RAP_K3`.

No rescue, rank/basis/certificate sweep, seed replacement, public target read or rerun.

### E148 — TERMINAL SCIENTIFIC NO-GO

Branch:

`research/e148-global-seed-tt-k3-20260921@d79eb8e670fbb8ff007283d9ed1eab6dd53a8b35`

Frozen physical evidence:

- executed arm: `32f33320d555d2f74e52e4754012ba83357759db`;
- run/job: `35550915761 / 106185373716`;
- artifact: `10618351672`, `e148-gstt-k3`;
- artifact SHA256: `c371dd1baf5c876e423d26fc0ca3e85c402690dc4080922c9964a8aeca744159`;
- decision: `E148_TERMINAL_NO_GO_CLOSE_GSTT_K3`.

No rank/basis/seed sweep, closure repair, rescue, public target read or rerun.

### E150 — TERMINAL THEORY NO-GO

Branch:

`research/e150-observable-response-query-closure-20260921@86f736cda004b60bc6c9d7379efe71164cecdef5`

Frozen decision:

**TERMINAL PRE-CODE NO-GO — downstream weight-only response queries are not a closed sufficient statistic for the V25/V29 K3/D21 nonlinear closure.**

The low-rank query class has an invisible zero-diagonal D21 residual kernel; the information dimension needed to remove the explicit obstruction pushes the frozen production ledger above the `0.135 B` cap. No implementation/physical run is authorized.

### E152 — TERMINAL THEORY NO-GO

Branch:

`research/e152-final-observable-adjoint-theory-gate-20260921@49cdaa28bcd58da724c4027a0f0d1d9c55abfbe0`

Frozen evidence:

- theory note: `7e1d76f560f97655328cef57704a750960847717`;
- executed theory arm: `5819040464ab2f54ba872197af2b3dac0d7999c9`;
- run/job: `35592718850 / 106310472483`;
- artifact: `10634794792`, `e152-theory-gate`;
- artifact SHA256: `6f9b7a54c2648735de0f8e7813ef2816cc223711115ae3ec20e0a8e5ef6c572a`;
- decision: `E152_TERMINAL_NO_GO_EXACT_FINAL_OBSERVABLE_ACTION_ONLY`.

No larger query/adjoint sweep, approximate rescue under E152, or rerun.

E146/H143 is also already terminal under its frozen one-run policy after infrastructure failure; it is not active under this receipt.

## E151 ARSG — requested sole active owner, but one-shot has already been consumed

Owner branch:

`research/e151-leader-forensics-angular-strassen-20260921`

Frozen hypothesis:

**ARSG = exact angular/radial state gauge plus one exact level of Strassen for eligible dense matrix products.**

Frozen protocol:

`research/E151_PROTOCOL.md`

Frozen protocol blob:

`8b484ea0c5b8c8ea02b3f91575693e44a1e645a3`

Freeze receipt status before execution:

`HYPOTHESIS_AND_FALSIFIER_FROZEN_NOT_EXECUTED`

The user authorized exactly one target-free falsifier and explicitly prohibited reruns/rescue.

At the live checkpoint after that authorization, the physical one-shot already exists:

- arm/executed head: `a8e9adf1c13fe655e0c3051c3eb9a07a14d2f021`;
- run: `35593352619`;
- job: `106312487858`;
- attempt: `1`;
- workflow: `E151 ARSG target-free falsifier`;
- GitHub conclusion: `failure`;
- artifact: `10635776518`, `e151-arsg-falsifier`;
- artifact SHA256: `6743e76b9b09d309ec0ccda116bcf1020bc7d95cd779ff5a2130de0c973d8938`.

Frozen-arm verification, Python setup, dependency installation and syntax checks all passed.

The sole scientific step failed immediately at import:

`ModuleNotFoundError: No module named 'methods'`

from:

`scripts/e151_angular_strassen_falsifier.py`

before the ARSG identity/cost gates were evaluated.

The uploaded artifact contains the failure log and run arm; no complete scientific result JSON was produced.

## Control decision for E151

The one allowed physical E151 execution has been consumed.

Because:

1. the user explicitly authorized **one** target-free falsifier;
2. the frozen E151 protocol states any future execution must be exactly one synthetic run with **no sweep/rescue/rerun**;
3. the observed run failed before scientific gates became evaluable;

the admissible disposition is:

**E151 TERMINAL FAIL-CLOSED / NO SCIENTIFIC VERDICT ON ARSG.**

This is an infrastructure failure, not evidence that the ARSG mathematical hypothesis itself is false. It nevertheless exhausts the authorized E151 physical-run budget.

Forbidden:

- import-path repair followed by a second run;
- rerun/retry;
- workflow patch and re-arm;
- seed/threshold/fixture change;
- ARSG rescue under E151;
- public/public-mini target validation;
- status promotion from the failed run;
- speculative ledger row.

A future ARSG-related experiment would require a later explicit control decision and a fresh collision-free identity; this receipt does not authorize one.

## E153 — verifier reserved but not executable

Live branch search at this checkpoint shows no E153 branch.

E153 is the requested single verifier identity, but there is no complete E151 scientific result to verify.

Therefore:

- E153 remains **RESERVED / UNUSED**;
- do not create or execute E153 against the failed E151 run;
- do not use E153 to repair, rerun, regenerate, or substitute E151;
- do not infer missing ARSG metrics from logs/protocol prose;
- no verifier receipt is authorized from incomplete owner evidence.

A later explicit control decision is required before E153 can be reassigned.

The previously created E149 reservation remains control-invalid/collision-occupied and is not a substitute verifier.

## Hard rejection rules

Reject and fail closed:

- any public/public-mini target scientific run;
- scorer, holdout, full-suite or submission access;
- any rank/seed/fixture/threshold/mechanism sweep;
- any rescue or rerun of E147/E148/E150/E151/E152 or other closed lanes;
- duplicate experiment IDs or incompatible same-ID branches;
- speculative ledger rows;
- status-only scientific claims;
- mutation of `research/bootstrap`;
- mutation of `research/ledger.csv`;
- canonical merge/integration.

## Single next gate

There is **no active scientific owner after the observed E151 one-shot failure**.

Watch E151 for unauthorized rerun/rescue/public-target/status promotion and E153 for premature verifier execution. Do not execute science or mutate canonical/ledger until a later explicit control update allocates a fresh owner identity.
