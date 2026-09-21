# ARC control update — E165 verified E164 / E166 terminal / E167 stable-reference owner / E168 verifier

Recorded: 2026-09-21

Control key: `ARC-CONTROL-E167-STABLE-REFERENCE-E168-20260921`

Prior control receipt:

`control/arc-deep-error-frontier-20260919@231f58c5d76c094d388668bf0d6810f7ad044b4e`

Status: **VERIFIED TARGET-FREE GO FROZEN / E166 TERMINAL / E167 SOLE OWNER / E168 SOLE VERIFIER / APPEND-ONLY CONTROL**.

This receipt freezes E164/E165 as verified target-free AGO evidence, closes E166 without rerun, and allocates E167/E168. Public/public-mini targets, holdout, scorer, full-suite and submission remain blocked. No rescue, sweep, rerun, canonical mutation, ledger mutation, or merge is authorized.

## E164/E165 — verified target-free AGO GO

E164 owner evidence remains frozen:

- owner branch/head: `research/e164-cleanroom-ago-20260921@342f2ab03ad5251971b17f8d8d43c1861774cbb6`;
- protocol: `b40957707e51f6d2fc142b913d9a500795d1bfe7`;
- candidate: `5709a167535b488d54974db9b4559afc16696fd8`;
- candidate blob: `ea9078eccc2e2bf2a2bea499ef10a4daf80ea0d4`;
- candidate runtime SHA256: `533149d0a1c05be12097b997b8762270b299c574cf6c32324de7d17ec285169c`;
- executed head: `ee9bafc24206cdf32e9c8d5f8085783b8fb6e421`;
- run/job/attempt: `35604133996 / 106347007723 / 1`;
- artifact: `10641735549`, `e164-ago`;
- artifact SHA256: `9397f519215a8a4b07b1c7b517032b4d6d4575de121c562b04ae5844e6669bea`;
- pooled AGO/parent MSE ratio: `0.6661376209420509`;
- all three frozen fixtures improved;
- all-in production upper: `112131571712 FLOPs = 0.05099153518676758 B`.

Independent verifier:

`review/e165-e164-independent-verifier-20260921@c5e3e011a7ee6f420435c8b307034efb17720b8a`

Receipt:

`research/E165_E164_INDEPENDENT_VERIFIER_RECEIPT.json`

Decision:

`E165_INDEPENDENT_VERIFIER_GO_E164_CLEANROOM_AGO`.

E165 independently verified:

- frozen owner provenance and artifact digest;
- AGO K1/K2 identities and radial readout;
- exact2d analytic identity;
- all fixture MSEs and pooled ratio `0.6661376209420509`;
- reference stability;
- deterministic replay;
- target/public firewall;
- clean-room ancestry;
- all-in cost `112131571712 FLOPs`.

E165 created no competing candidate or scientific rerun and did not modify E164/canonical/ledger.

**E164/E165 is therefore frozen verified target-free AGO GO.**

This still does not authorize public-target execution under this receipt.

## E166 — terminal production-shaped one-shot

Authoritative branch:

`research/e166-production-shaped-ago-20260921@6acb17f836806226f5f9d3ab996a9198927f2532`

Frozen provenance:

- protocol commit/blob: `e8895594e2280d7f0c5037d5aba5151253aa9b13 / d3271ce7e6da160c8152be877ec63c5adb1d18f1`;
- falsifier commit/blob: `7276bb670b7fe969e79bbfaa4867ef410d809110 / ea7a22698089f9d98ed13248aa72bcc915ff4b3b`;
- workflow commit/blob: `cfeaf5db4603ceb77dbea255b68c5f4367bc778d / 96f5443d40592f9530592178fba93260f0628a56`;
- arm/executed head: `40c9177a3f32d38d915b9f5da7c40431284859d1`;
- run/job/attempt: `35606863697 / 106355965383 / 1`;
- artifact: `10642051274`, `e166-production-shaped-ago`;
- artifact SHA256: `98c21ee635ceb8a224bd693177c7a1214cfd161b47d12bc14f254929009f9994`;
- terminal decision: `E166_TERMINAL_NO_GO`.

Production-shaped fixture:

- width `1024`;
- depth `16`;
- network seed `1661024`;
- reference samples `8192`;
- reference seed `1668192`;
- eight reference batches.

Observed target-free signal:

- parent MSE: `1.8811649099480322e-5`;
- AGO MSE: `1.7538238290386996e-5`;
- AGO/parent: `0.9323073271057079`;
- improvement: **`6.769267289429215%`**;
- improved `6/8` batch references;
- batch improvement mean / SE: `2.620904337760046`;
- all-in production cost remained `112131571712 FLOPs = 0.05099153518676758 B`.

Terminal blocker:

- reference SE RMS: `0.0030812641362217745`;
- allowed frozen reference SE: `0.000837573597730659`;
- SE / allowed: **`3.678797664878309`**.

Therefore the positive transfer signal is not certified by E166's preregistered reference-precision gate. E166 is terminal. It does not falsify AGO, but it cannot be promoted to production-shaped GO.

### Preserved control-order defect

The prior receipt required E165 PASS before E166 scientific advance.

Git history shows:

- E166 protocol commit `e8895594...`: `2026-09-21T13:36:30Z`;
- E166 arm commit `40c9177a...`: `2026-09-21T13:37:58Z`;
- E166 run created: `2026-09-21T13:38:01Z`;
- E165 verifier receipt commit `c5e3e011...`: `2026-09-21T13:38:26Z`.

Thus E166 advanced before the durable E165 PASS receipt. This historical ordering defect remains part of the control record and is not erased by the present update.

The present control accepts E166 only as a **terminal, hypothesis-generating target-free signal** and explicitly authorizes a fresh E167 identity. It does not retroactively convert E166 into clean gate-ordered GO evidence.

**No E166 rerun, reference-sample increase, threshold change, workflow repair, rescue, or reinterpretation.**

## Namespace checkpoint

Fresh intake search:

- E167: no branch observed;
- E168: no branch observed;
- no E167/E168 Actions run observed.

Both identities are collision-free at allocation.

## E167 — sole active scientific owner

Allocate:

**E167 — production-shaped synthetic AGO with preregistered stable reference.**

E167 is the only active scientific owner.

E167 is a new experiment identity, not an E166 rerun or rescue. It may use:

- verified E164/E165 AGO mechanism/provenance;
- E166 only as hypothesis-generating evidence that reference precision, not the observed AGO direction, was the terminal blocker.

E167 must not reuse E166's observed reference mean, batch means, MSE values, or post-result statistics as its scientific reference or as evidence satisfying an E167 gate.

### Frozen scientific mechanism

The candidate must remain the verified E164 AGO mechanism with no scientific-mechanism change:

1. frozen full-covariance K2 parent;
2. one exact K1/K2 Gaussian-to-angular gauge after the first activation;
3. identical parent closure thereafter;
4. exact final radial `a1(n)` mean readout.

No K4/D4/D22/c4, no recurrent K4, no target fitting, no candidate-specific parent refit.

Production-shaped synthetic target remains:

- width `1024`;
- depth `16`;
- zero bias.

### Preregistered stable-reference requirement

Before any E167 implementation/workflow/run, the first owner protocol commit must freeze one reference design completely.

It must specify, before observing E167 candidate/reference results:

1. exact deterministic reference construction;
2. exact sample count or deterministic quadrature/design size;
3. exact reference seed(s) or deterministic point set identity;
4. exact batching/replication plan;
5. exact reference precision/stability estimator;
6. exact numerical stability threshold;
7. an a-priori precision justification showing why the fixed design is intended to resolve the frozen AGO-vs-parent effect without adaptive sampling;
8. exact rule for reference failure;
9. no sample-count increase, seed replacement, batch addition, stopping-rule adaptation, or alternate reference after execution.

E166's observed SE may be used once as design/planning context for choosing a single E167 reference design before freeze. It may not be used to fit the AGO candidate, select among multiple E167 reference outcomes, or relax the E167 gate after execution.

There is no separate adaptive reference sweep. The reference design and the candidate evaluation must be contained within the one frozen E167 owner protocol and one physical owner execution.

### Mandatory protocol-first freeze

Before implementation/workflow, E167 must freeze:

1. verified E164/E165 provenance;
2. explicit statement that E167 is not E166 rerun/rescue;
3. exact unchanged AGO candidate blob/mechanism or a clean wrapper whose scientific arithmetic is proven identical;
4. deterministic synthetic `1024 x 16` weight construction and one frozen network seed;
5. the complete preregistered stable-reference design above;
6. candidate-before-reference or otherwise leakage-proof execution ordering;
7. frozen primary AGO-vs-parent scientific metric and numerical pass/fail threshold;
8. frozen reference-stability/certification gate;
9. target-free residual/error certificate appropriate to the production-shaped claim;
10. complete all-in estimator production cost and independent reconciliation against `0.135 * 2^41`;
11. explicit reference/test cost accounting separately from deployed estimator cost;
12. memory/resource accounting sufficient to distinguish resource failure from science;
13. deterministic replay;
14. target/oracle/public/public-mini/scorer/holdout/full/submission firewall;
15. terminal kill rule;
16. exactly one target-free physical owner run;
17. no sweep, tuning, rescue, rerun, retry, seed/reference/threshold/mechanism substitution or post-result repair.

### One-run authorization

After a valid protocol-first freeze, E167 may implement the minimum target-free production-shaped owner harness and execute **exactly one** physical scientific run.

Every mandatory gate must pass, including the preregistered reference-stability gate.

Any failed, skipped, nonfinite or unevaluable gate — including infrastructure/resource/reference failure — consumes the one-run authorization and closes E167 absent a later explicit control update.

No second run.

## E168 — sole independent verifier

E168 is reserved as exactly one independent review-only verifier for E167.

Do not create or execute E168 before a complete E167 owner result exists.

After E167's sole run, freeze:

- branch/experiment identity;
- protocol SHA/blob;
- verified E164/E165 parent provenance;
- candidate identity;
- synthetic 1024x16 weight seed/hash;
- complete preregistered reference design;
- implementation/reference/test/falsifier/workflow SHAs/blobs;
- executed head;
- run/job/attempt;
- artifact ID/name/SHA256;
- immutable owner receipt SHA;
- reference-stability evidence;
- parent/AGO scientific metrics;
- target-free certificate;
- estimator and reference/test cost accounting;
- memory/resource evidence;
- replay;
- firewall.

Only then may E168 execute exactly one independent verification.

E168 must independently verify/recompute:

1. protocol-first identity and no E166 rerun/rescue;
2. exact E164/E165 AGO mechanism carry-forward;
3. preregistration of the complete reference design before E167 execution;
4. no adaptive reference sample/seed/batch/threshold changes;
5. reference precision/stability arithmetic;
6. parent-vs-AGO production-shaped scientific metrics;
7. target-free certificate;
8. complete estimator cost and separate reference/test cost accounting;
9. replay and resource evidence;
10. zero public/public-mini/scorer/holdout/full/submission access;
11. frozen run/artifact provenance and no post-result mutation.

E168 may inspect/recompute frozen evidence only. It may not modify, regenerate, rerun, tune, rescue, substitute, repair, or publicly validate E167.

Exactly one verifier receipt/execution. No nested verifier.

Premature E168 activity fails closed.

## Public-target firewall

Despite E165 PASS, this control explicitly keeps:

- public/public-mini targets;
- holdout;
- official scorer;
- full suite;
- submission

**BLOCKED**.

Neither E164/E165 verification nor E167/E168 can implicitly unlock them. A later explicit control allocation is required.

## Hard rejection rules

Reject and fail closed:

- E166 rerun/rescue/reference enlargement under E166;
- E154/E157/K4 rescue;
- E164 owner rerun or post-result mutation;
- adaptive E167 reference sizing or reference sweep after execution begins;
- E167 second run/retry;
- premature or repeated E168;
- public/public-mini/holdout/scorer/full/submission access;
- target fitting;
- any scientific sweep;
- duplicate/colliding experiment IDs;
- speculative ledger/status promotion;
- mutation of `research/bootstrap`;
- mutation of `research/ledger.csv`;
- canonical merge/integration.

## Exact next action

Create one collision-free **protocol-first E167** owner freeze for the unchanged verified AGO mechanism on synthetic `1024 x 16`, with a single fully preregistered stable-reference design.

Then execute at most one E167 target-free physical run.

Only after a complete frozen E167 result may E168 verify it.

Do not mutate canonical or ledger.
