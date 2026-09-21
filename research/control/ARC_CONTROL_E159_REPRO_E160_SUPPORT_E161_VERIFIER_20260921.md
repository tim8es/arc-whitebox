# ARC control update — E159 clean-room angular-radial reproduction / E160 support / E161 verifier

Recorded: 2026-09-21

Control key: `ARC-CONTROL-E159-ANGULAR-RADIAL-REPRO-E161-20260921`

Prior control receipt:

`control/arc-deep-error-frontier-20260919@76b2eb21b3f3efeecfaa17e8f049d0118c07e7ed`

Status: **ACTIVE OWNER ALLOCATION / APPEND-ONLY CONTROL / FAIL-CLOSED**.

This receipt closes E157 and allocates E159/E160/E161. It does not rewrite prior evidence and does not authorize public/public-mini targets, scorer/holdout/full, sweeps, rescue, reruns, canonical mutation, ledger mutation, merge, or status-only promotion.

## Immutable closed state

The following remain closed:

- **E147** — terminal scientific NO-GO;
- **E148** — terminal scientific NO-GO;
- **E150** — terminal theory NO-GO;
- **E152** — terminal theory NO-GO;
- **E151** — sealed FAIL-CLOSED before science; no import-path repair/rerun/rescue;
- **E154** — terminal scientific NO-GO; no ARK4/recurrent-K4 rescue;
- **E157** — terminal scientific NO-GO; no AIK4-1 rescue/rerun.

## E157 — TERMINAL NO-GO / CLOSE AIK4-1

Authoritative branch:

`research/e157-owner-aik4-onebirth-20260921@2c23f27f17560829111ac51a30e0b70d592b790f`

Frozen physical tuple:

- owner protocol blob: `4fdaff001faedca323d464cf8ae218611efc32e4`;
- parent commit/blob: `cf1c86edf4f1a35f887bd464f78d5454eefcc68b / cf233297780b509da35edd149e3c83d1a3a06087`;
- candidate commit/blob: `3641d4a03e9a6cb2be4abc3100d933b4c10f2cc6 / ec8789e0681ffa29d07b66dff804abd07f95bd6c`;
- launch/executed head: `f5720c423ac8b82111b8d75d1ee13594495e4010`;
- run/job/attempt: `35600676928 / 106335760826 / 1`;
- artifact: `10639360054`, `e157-aik4-onebirth`;
- artifact SHA256: `b188a603b49053d1476dd48c52bc956af29a22730062c4a13ec9a7ed8d07f3db`;
- terminal decision: `E157_TERMINAL_NO_GO_AIK4_1`.

Decisive target-free scientific failure on exact2d:

- parent MSE: `0.014810821567308377`;
- AIK4-1 MSE: `0.01891592042211022`;
- candidate/parent ratio: `1.2771688819655316`;
- frozen gate: `<=0.98`;
- relative worsening: `27.716888196553157%`.

Identity, no-recurrence, deterministic replay, firewall and cost gates passed; the exact-small scientific gate failed.

Therefore **E157 is immutable terminal NO-GO**. No parent substitution, overlay repair, seed/threshold change, extra fixture, second run, renamed AIK4-1 continuation, or public-target validation.

The E158 reservation branch
`review/e158-e157-verifier-reservation-20260921@ff8311af166867dc924d2144ec7444a69f796db7`
is **CLOSED UNUSED** because E157 did not survive its owner scientific gate. E158 must not verify, repair, or reinterpret E157.

## Namespace checkpoint at intake

Fresh branch search:

- E159: no branch observed;
- E160: no branch observed;
- E161: no branch observed.

Fresh Actions search:

- no E159 run;
- no E160 run;
- no E161 run.

All three identities are collision-free at allocation time.

## E159 — sole active scientific owner

Allocate:

**E159 — clean-room public angular-radial reproduction.**

E159 is the only active scientific owner under this receipt.

“Public” in this experiment name means reproduction of a publicly described angular-radial **method/mechanism/source formulation**, not permission to read or evaluate public benchmark targets.

### Hard public-target distinction

E159 may use:

- publicly available source code, papers, equations, documentation, or method descriptions as frozen provenance for the mechanism being reproduced;
- clean-room reimplementation of the pinned angular-radial method;
- deterministic synthetic/analytic target-free fixtures and references.

E159 may **not** use:

- ARC public target outputs/labels/reference answers;
- public-mini targets;
- public benchmark error/score as a scientific gate;
- scorer, holdout, full suite or submission;
- target-derived fitting, selection, tuning or coefficients.

Any public target read or benchmark-target evaluation fails closed.

### Clean-room requirement

E159 must be a reproduction, not an E154/E157 rescue.

Before implementation/workflow, its first scientific owner commit must freeze:

1. exact public method/source provenance being reproduced, including immutable commit/blob/version/URL identifiers where available;
2. exact clean-room boundary: which behavior/equations are reproduced and which prior ARC experimental code/artifacts are forbidden;
3. explicit firewall excluding E154 and E157 candidate code, workflows and run artifacts from candidate construction;
4. deterministic synthetic/analytic target-free fixtures and seeds;
5. an independent exact-small or analytic reference capable of falsifying reproduction correctness;
6. exact reproduction/parity metrics and frozen numerical thresholds;
7. a target-free scientific error/certificate gate appropriate to the claimed angular-radial reproduction;
8. complete all-in production cost for the reproduced mechanism, including estimator arithmetic, transforms, radial/angular reconstruction, diagnostics/helpers/RNG/normalization/materialization, certificate/reference computation, setup and all charged bookkeeping;
9. combined production cost gate `<=0.135 * 2^41` FLOPs if the claim is production admissibility;
10. deterministic replay;
11. terminal kill rule;
12. exactly one target-free physical owner run;
13. no sweep, tuning, rescue, rerun, seed/fixture/threshold change, source substitution, mechanism substitution or post-result repair.

If exact public-source provenance cannot be frozen without using target outputs, fail closed before code.

### One-run authorization

After a valid protocol-first freeze, E159 may implement the minimum clean-room candidate/reference/tests/falsifier/workflow and execute **at most one** target-free physical scientific run.

Any failed or unevaluable mandatory gate, including infrastructure failure before science, consumes the one-run authorization and closes E159 unless a later explicit control update says otherwise.

No second run.

## E160 — support only

E160 is allocated as support-only for E159.

Allowed support:

- provenance audit of the pinned public method/source;
- equation-to-code mapping;
- independent derivation of angular/radial identities;
- exact-small reference derivation;
- target-free certificate analysis;
- production cost cross-check;
- adversarial review of clean-room separation and target firewall.

E160 is not a scientific owner and may not:

- execute a competing candidate;
- access public/public-mini target outputs;
- tune or alter E159 after freeze;
- trigger another E159 run;
- act as final verifier;
- promote E159;
- repair E154/E157.

Support artifacts must remain clearly labeled support-only and target-free.

## E161 — sole independent verifier

E161 is reserved as exactly one independent review-only verifier for E159.

Do not create or execute E161 before a complete admissible E159 owner tuple exists.

After the sole E159 physical run, control must freeze:

- E159 branch/experiment identity;
- protocol SHA;
- pinned public method/source provenance;
- clean-room candidate/reference/test/falsifier/workflow SHAs;
- executed head;
- run/job/attempt;
- artifact ID/name/SHA256;
- immutable owner result/terminal receipt SHA;
- reproduction/parity metrics;
- target-free scientific/certificate metrics;
- complete all-in cost result;
- deterministic replay;
- public-target firewall evidence.

Only if that tuple is complete and survives owner gates may E161 execute one independent verification.

E161 must independently verify/recompute:

1. protocol-first ancestry and collision-free identity;
2. exact public method/source provenance and clean-room separation;
3. no E154/E157 rescue or code/artifact reuse forbidden by the owner protocol;
4. angular-radial reproduction/parity arithmetic;
5. exact-small/analytic reference gates;
6. target-free scientific/certificate arithmetic;
7. complete all-in production cost;
8. deterministic replay;
9. absence of public/public-mini target/scorer/holdout/full/submission access;
10. frozen run/artifact provenance and no post-result changes.

E161 may inspect/recompute frozen evidence only. It may not modify, regenerate, rerun, tune, rescue, substitute, repair, or publicly validate E159.

Exactly one verifier execution/receipt. No nested/second verifier.

Premature E161 activity fails closed.

## Hard rejection rules

Reject and fail closed:

- any E154 rescue or recurrent-ARK4 continuation;
- any E157/AIK4-1 rescue or renamed continuation;
- public/public-mini target scientific access;
- benchmark-target scoring/evaluation as a scientific gate;
- official scorer, holdout/full or submission access;
- target fitting;
- rank/order/seed/fixture/threshold/basis/certificate/source/mechanism sweeps;
- owner rerun/retry or post-result repair;
- duplicate/colliding experiment IDs;
- speculative status or ledger rows;
- mutation of `research/bootstrap`;
- mutation of `research/ledger.csv`;
- canonical merge/integration.

## Single next gate

Wait for one collision-free **protocol-first E159 clean-room angular-radial reproduction** owner freeze with pinned public method/source provenance but **zero public benchmark target access**.

E160 may provide support only.

After one complete admissible E159 target-free physical result, dispatch exactly one independent verifier under **E161**.
