# ARC control update — E154 owner / E155 support / E156 verifier

Recorded: 2026-09-21

Control key: `ARC-CONTROL-E154-ANGULAR-RADIAL-K4-20260921`

Prior control receipt:

`control/arc-deep-error-frontier-20260919@8d8c9c9f6fc89c2dc2af12a95a2444807b4cddde`

Status: **ACTIVE OWNER ALLOCATION / APPEND-ONLY CONTROL**.

This receipt supersedes the prior "no active scientific owner" gate only to allocate E154/E155/E156 as described below. It does not reopen any closed lane and does not authorize canonical or ledger mutation.

## Immutable closed state

The following remain terminal and may not be rescued, rerun, renamed into equivalent continuations, or promoted:

- **E147** — terminal scientific NO-GO;
- **E148** — terminal scientific NO-GO;
- **E150** — terminal theory NO-GO;
- **E152** — terminal theory NO-GO;
- **E151 ARSG** — sealed FAIL-CLOSED after its sole physical execution failed before scientific evaluation with `ModuleNotFoundError: No module named 'methods'`.

Frozen E151 physical tuple remains:

- branch: `research/e151-leader-forensics-angular-strassen-20260921`;
- executed head: `a8e9adf1c13fe655e0c3051c3eb9a07a14d2f021`;
- run/job: `35593352619 / 106312487858`;
- artifact: `10635776518`, `e151-arsg-falsifier`;
- artifact SHA256: `6743e76b9b09d309ec0ccda116bcf1020bc7d95cd779ff5a2130de0c973d8938`.

E151 remains **NO SCIENTIFIC VERDICT ON ARSG**. No import-path repair, workflow patch, retry, rerun, rescue, public-target validation, status promotion or ledger row is authorized.

## Namespace checkpoint at intake

Fresh branch search at this control checkpoint finds:

- E154: no branch;
- E155: no branch;
- E156: no branch.

Fresh Actions search finds no E154/E155/E156 workflow run.

Therefore all three identities are collision-free at allocation time.

## E154 — sole active scientific owner

Allocate:

**E154 — clean-room angular-radial K4 correction**

E154 is the only active scientific owner under this receipt.

The experiment must be clean-room relative to sealed E151:

- it may use general mathematical identities and independently pinned public mathematical/source material allowed by the project;
- it must not patch, import, execute, copy-forward, or silently repair the frozen E151 falsifier/workflow as an E151 continuation;
- it must not claim E151's failed execution as scientific evidence.

### Admission contract

E154 must be protocol-first.

Its first scientific commit must freeze, before implementation/workflow execution:

1. exact parent/provenance;
2. the angular-radial K4 correction mechanism and the scientific quantity it claims to improve or certify;
3. deterministic synthetic fixtures/seeds;
4. target/oracle firewall;
5. an independent exact-small or analytic falsification gate capable of rejecting the mechanism;
6. a computable target-free residual/error certificate appropriate to the claimed correction;
7. explicit numerical pass/fail thresholds;
8. complete all-in production cost accounting, including correction, diagnostics, helper transforms, RNG/normalization/materialization, certificate computation, and charged setup;
9. terminal kill rule;
10. no sweep/rescue/rerun rule.

After protocol freeze, E154 may implement and perform **at most one target-free physical scientific execution** of the frozen candidate.

No rank/order/seed/fixture/threshold/basis/certificate/mechanism sweep is authorized. No post-result repair or second execution is authorized.

If the sole physical run fails before science, E154 is fail-closed under the same one-run rule unless a later explicit control update says otherwise.

## E155 — support only

E155 is allocated as **support-only** for E154.

Allowed:

- independent theory derivations;
- cost-accounting cross-checks;
- exact-small reference derivations;
- target-free certificate analysis;
- source/provenance audits;
- adversarial review of the frozen E154 mechanism.

E155 is not a scientific owner and may not:

- create a competing estimator/candidate;
- change E154's frozen mechanism, thresholds, seeds, fixtures or certificate after execution;
- run public/public-mini targets, scorer, holdout/full or submissions;
- trigger a second E154 execution;
- act as the designated final verifier;
- promote E154.

Support evidence must remain clearly labeled support and target-free.

## E156 — verifier only

E156 is reserved as the **single independent verifier** for E154 and must not be created/executed before a complete admissible E154 owner result exists.

After E154's sole physical run completes, control must freeze the complete owner tuple before E156 verification:

- E154 branch and experiment ID;
- protocol SHA;
- candidate/implementation SHA(s);
- executed head;
- run ID;
- job ID;
- run attempt;
- artifact ID/name/digest;
- owner terminal/result receipt;
- exact-small/analytic falsifier evidence;
- target-free residual certificate evidence;
- complete all-in cost evidence.

E156 may inspect and independently recompute only the frozen evidence. It may not modify, regenerate, rerun, rescue, tune, substitute, or repair E154.

Exactly one verifier execution/receipt is allowed after a complete owner tuple is frozen. No nested or second verifier.

If E156 appears before that trigger, fail closed as premature verifier activity.

## Global firewall

Not authorized under E154/E155/E156:

- public or public-mini target scientific access;
- official scorer;
- holdout/full suite;
- submissions;
- target-fitted coefficients or oracle selection;
- sweeps of any kind;
- rescue or rerun of E151 or other closed lanes;
- E154 rerun or post-result repair;
- duplicate/colliding experiment identities;
- speculative scientific status;
- speculative ledger rows;
- mutation of `research/bootstrap`;
- mutation of `research/ledger.csv`;
- canonical merge/integration.

## Current next gate

Wait for a collision-free **protocol-first E154** allocation implementing the clean-room angular-radial K4 correction contract.

E155 may provide target-free support only.

E156 remains reserved and unused until a complete admissible E154 owner tuple is frozen after the sole target-free physical execution.
