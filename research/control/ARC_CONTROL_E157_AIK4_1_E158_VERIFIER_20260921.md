# ARC control update — E157 AIK4-1 sole owner / E158 sole verifier

Recorded: 2026-09-21

Control key: `ARC-CONTROL-E157-AIK4-1-E158-20260921`

Prior control receipt:

`control/arc-deep-error-frontier-20260919@e385865c967ffb09222ada6eacf64b324268247b`

Status: **ACTIVE OWNER ALLOCATION / APPEND-ONLY CONTROL / FAIL-CLOSED**.

This receipt closes E154 and allocates E157/E158. It does not rewrite prior evidence and does not authorize public/public-mini targets, scorer/holdout/full, sweeps, rescue, reruns, recurrent K4, canonical mutation, ledger mutation, merge, or status-only promotion.

## Closed state

The following remain closed:

- **E147** — terminal scientific NO-GO;
- **E148** — terminal scientific NO-GO;
- **E150** — terminal theory NO-GO;
- **E152** — terminal theory NO-GO;
- **E151** — sealed FAIL-CLOSED before science after import-path failure; no repair/rerun/rescue;
- **E154** — terminal scientific NO-GO.

## E154 — TERMINAL NO-GO / CLOSE ARK4

Authoritative branch:

`research/e154-clean-angular-radial-k4-20260921@c599aa6deb7fc7630951be88bac9e0ce1afbe949`

Frozen provenance:

- protocol commit: `b4d3f6d034269d664c05c2fb4003160168b1fbd7`;
- candidate commit: `03d5def9703cb9fa4c6f7ccbf4ffdd0589a4974e`;
- reference commit: `8d4e14ee9d37283290bc34800617a5228618ba9c`;
- tests: `e321e8dcaf7c0e6938cf0a0fc040c700a4f65fec`;
- falsifier: `96530f912c463b85e91b235f0810f9392e58e3dc`;
- workflow: `fd6a0af515a205132ae076840eaeea7579d3b390`;
- executed arm/head: `fb1bc55f54b13a9c2dfa2a980b785c4b4f82072f`;
- run/job: `35595066151 / 106317878198`;
- artifact: `10636273829`, `e154-angular-radial-k4`;
- artifact SHA256: `35237eeffaabcd7fe723e13f1ba2cae503d7731f62e41f2fd199d4b97a7c8c96`;
- terminal decision: `E154_TERMINAL_NO_GO_CLOSE_ARK4`.

Decisive scientific failure:

- dense32 baseline final-mean relative RMS: `0.06996621447064387`;
- dense32 ARK4: `0.06735395868606409`;
- ratio: `0.9626640400035388`, missing frozen <=0.95 gate;
- adversarial16 baseline: `0.07163670989919448`;
- adversarial16 ARK4: `0.0740661768122803`;
- adversarial ratio: `1.0339137143024089` — correction worsened the adversarial fixture;
- deep K4 diagonal relative RMS: `1.280279689303633` (32D) and `1.3018672466300862` (16D), failing the frozen <=0.35 gate.

Production cost passed (`111981625344` FLOPs, `0.05092334747314453 B` utilization), so cost is not the blocker.

**E154 is immutable terminal NO-GO.** No closure modification, empirical-gate repair, metric repair, recurrent-K4 variant, rescue, rerun, or public validation.

E155 remains historical support-only evidence. Its support protocol may be cited as hypothesis design input but is not owner evidence and authorizes no execution.

E156 is closed unused as the obsolete E154 verifier reservation. It must not be reused.

## Namespace checkpoint

Fresh branch search at intake:

- E157: no branch observed;
- E158: no branch observed.

Fresh Actions search at intake:

- no E157 run;
- no E158 run.

Both identities are collision-free at allocation time.

## E157 — sole active scientific owner

Allocate:

**E157 — AIK4-1, exact one-birth angular-input K4 correction.**

E157 is the only active scientific owner under this receipt.

The allowed mechanism is narrowly defined:

1. retain the exact angular-input K4 through the first linear step;
2. use it only for the first nonlinear K1/K2/K3 birth / frozen selected Wick contributions;
3. destroy/drop the K4 carrier immediately after that first nonlinear conversion;
4. perform **no recurrent K4 state, scalar c4, K4 transport, or K4-derived later-layer arithmetic**.

This is specifically not E154 recurrent/memoryless K4 rescue.

The historical E155 support branch
`research/e155-cleanroom-angular-k4-support-20260921@3a6134914f930d1ef3624a76e25c5853ce6ffeff`
may be used as target-free support/design provenance only. E157 must still freeze its own owner protocol before implementation/workflow and may not execute E155.

### Mandatory protocol-first owner freeze

Before E157 implementation or workflow execution, the first scientific owner commit must freeze:

1. exact clean parent and provenance, including any E155 support material used;
2. exact AIK4-1 one-birth mechanism and explicit proof that recurrent K4 is absent after the first nonlinear conversion;
3. one deterministic parent estimator commit and implementation blob hashes;
4. deterministic synthetic fixtures/seeds;
5. target/oracle/public/public-mini/scorer/holdout/full/submission firewall;
6. exact-small/analytic K4 identity and selected-contraction falsification gates;
7. target-free scientific error gate against an exact/analytic synthetic reference;
8. a computable target-free residual/error certificate with numerical threshold appropriate to the scientific claim;
9. complete all-in production cost: parent plus every AIK4-1 operation, allocation-relevant arithmetic, Wick evaluation, moment-to-cumulant conversion, diagnostics/helpers/RNG/normalization/materialization/certificate/reference/setup and all charged bookkeeping;
10. combined production cost <= `0.135 * 2^41` FLOPs;
11. deterministic replay;
12. terminal kill rule;
13. exactly one physical target-free owner run;
14. no sweep, tuning, rescue, rerun, seed replacement, threshold change, parent substitution, mechanism substitution, or post-result repair.

If the chosen parent does not already compute a required first-layer Gram/state and adding it changes cost, that cost must be charged explicitly. No hidden inherited arithmetic.

### One-run authorization

After a valid protocol-first freeze, E157 may implement the minimum candidate/reference/tests/falsifier/workflow and execute **exactly one** target-free physical scientific run.

Any failed or unevaluable mandatory gate is terminal for E157.

Any infrastructure failure before science also consumes the one-run authorization and fails closed unless a later explicit control update says otherwise.

No second run.

## E158 — sole verifier

E158 is reserved as exactly one independent review-only verifier for E157.

Do not create or execute E158 before a complete admissible E157 owner tuple exists.

After the sole E157 physical run, freeze:

- E157 branch/experiment identity;
- protocol SHA;
- candidate/reference/test/falsifier/workflow SHAs as applicable;
- executed head;
- run/job/attempt;
- artifact ID/name/SHA256;
- immutable owner result/terminal receipt SHA;
- exact one-birth/no-recurrence evidence;
- exact-small/analytic falsifier metrics;
- target-free certificate metrics;
- complete all-in cost result;
- deterministic replay and firewall evidence.

Only if that tuple is complete may E158 execute one independent verification.

E158 must independently verify/recompute:

1. protocol-first ancestry and collision-free identity;
2. exact AIK4-1 one-birth K4 algebra;
3. explicit absence of recurrent K4 after first nonlinear conversion;
4. exact-small/analytic identity and selected Wick contraction parity;
5. target-free scientific/certificate arithmetic;
6. complete parent+overlay all-in cost;
7. deterministic replay;
8. target/public/scorer/holdout/full firewall;
9. frozen run/artifact provenance;
10. no sweep/rescue/rerun/post-result changes.

E158 may inspect/recompute frozen evidence only. It may not modify, regenerate, rerun, tune, rescue, substitute, repair, or publicly validate E157.

Exactly one verifier execution/receipt. No nested/second verifier.

If E158 appears before a complete E157 result, fail closed as premature verifier activity.

## Hard rejection rules

Reject and fail closed:

- recurrent K4 after first nonlinear conversion;
- any E154 rescue or renamed recurrent-ARK4 continuation;
- any E151 rescue/import repair;
- public/public-mini target scientific access;
- official scorer, holdout/full or submission access;
- target fitting;
- rank/order/seed/fixture/threshold/basis/certificate/mechanism sweeps;
- owner rerun/retry or post-result repair;
- duplicate/colliding experiment IDs;
- speculative status or ledger rows;
- mutation of `research/bootstrap`;
- mutation of `research/ledger.csv`;
- canonical merge/integration.

## Single next gate

Wait for one collision-free **protocol-first E157 AIK4-1** owner freeze.

After that, allow at most one target-free physical E157 falsifier. If and only if the complete frozen owner tuple is admissible, dispatch exactly one independent verifier under **E158**.
