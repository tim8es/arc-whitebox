# ARC control update — E169 owner GO / E170 unevaluated / E171 evidence-complete AGO / E172 verifier

Recorded: 2026-09-21

Control key: `ARC-CONTROL-E171-EVIDENCE-COMPLETE-AGO-E172-20260921`

Prior control receipt:

`control/arc-deep-error-frontier-20260919@6a86f94f42ea069897b7d86293db4a8f0607c6e5`

Status: **E169 OWNER GO SIGNAL FROZEN / E170 UNEVALUATED / E171 SOLE OWNER / E172 SOLE VERIFIER / APPEND-ONLY CONTROL**.

This receipt preserves E164/E165 as verified target-free AGO GO, freezes E169 as owner-only multi-seed production-shaped GO evidence, records E170 as UNEVALUATED because immutable numeric vectors were not retained, and allocates E171/E172. It does not authorize public/public-mini targets, holdout, scorer, full suite, submission, E169 rerun, post-hoc gate changes, sweeps, canonical mutation, ledger mutation, merge, or status-only promotion.

## E164/E165 — verified target-free AGO GO remains frozen

E164 owner:

`research/e164-cleanroom-ago-20260921@342f2ab03ad5251971b17f8d8d43c1861774cbb6`

E165 verifier:

`review/e165-e164-independent-verifier-20260921@c5e3e011a7ee6f420435c8b307034efb17720b8a`

Frozen pooled AGO/parent MSE ratio:

`0.6661376209420509`.

No E164/E165 rerun, rescue, post-result mutation, or ledger promotion.

## E169 — owner GO signal frozen, not independently numerically certified

Authoritative owner branch:

`research/e169-multiseed-ago-20260921@3eb9c506ef96a1ff3bba7e604832e851a84fe12b`

Frozen provenance:

- protocol commit/blob: `bc2469e0ca5dbd6c8d5c8b8cc54d04014ab5fdd4 / 127fe7a2ced0fab545904c79654f1f2ee956ccea`;
- reference commit/blob: `1e52373bcb8181205031eac0ddf391697bbab53a / bed83baec6eea86b880cbacb7ea1b300e9782165`;
- tests commit/blob: `1a9ae4d53f87ca5bbf85471bc943759c0a702983 / fe09b62ce7a5e9cc1f6b3f0088aec689b141abd6`;
- owner script commit/blob: `4327a4c7f20e13fcf03b0686fe2a933bd004bd7e / b43df48e322976ddc0e9d4a344e927a76b2db887`;
- workflow commit/blob: `6b6601bca3f1b94e583eb71ded71c38c01c581b5 / f8aeb46beb10073711d13befa45cc674b79b0102`;
- arm/executed head: `eb9fcb39a4f74e53dd4146b623e52625b53903c9`;
- run/job/attempt: `35610324934 / 106367522989 / 1`;
- artifact: `10644057088`, `e169-multiseed-ago`;
- artifact ZIP SHA256: `339167cb44e46d346629175c11d95a889a79df0ad35de608cc4e7bbfc203d209`;
- owner decision: `E169_SYNTHETIC_MULTISEED_PRODUCTION_SHAPED_OWNER_GO_AGO`.

Frozen owner signal across three preregistered 1024x16 seeds:

- seed `1691024`: AGO/parent `0.8423674288902979`;
- seed `1692024`: AGO/parent `0.8625794411723062`;
- seed `1693024`: AGO/parent `0.8356350912978462`;
- pooled parent MSE: `4.695225767320242e-6`;
- pooled AGO MSE: `3.97834400692741e-6`;
- pooled ratio: **`0.8473168712391894`**;
- pooled improvement: **`15.268312876081058%`**;
- positive paired batch deltas: `136/144`;
- batch delta mean / SE: `17.486418865901825`;
- all three absolute reference SE values passed the frozen `7e-4` gate;
- production all-in upper: `112131571712 FLOPs = 0.05099153518676758 B`.

E169 remains a frozen owner GO signal only. No E169 rerun, replay-as-new-science, artifact regeneration, reference regeneration, vector reconstruction by execution, gate change, rescue, or public validation.

## E170 — sole verifier consumed as UNEVALUATED

Verifier branch:

`review/e170-e169-independent-verifier-20260921@e3482ec16abce507387d5cc306bf3dd06808e826`

Receipt:

`research/E170_E169_INDEPENDENT_VERIFIER_RECEIPT.json`

Decision:

`E170_INDEPENDENT_VERIFIER_UNEVALUATED_E169_NUMERIC_RECOMPUTATION_EVIDENCE_INCOMPLETE`.

E170 verified from immutable evidence:

- preregistered absolute-SE definition/threshold;
- ordered weight/reference seeds and sample/batch counts;
- paired batch improvement from retained batch MSE deltas;
- AGO identities;
- target/public firewall;
- complete FLOP accounting;
- deterministic replay claims and run count;
- clean ancestry and byte-identical E164 AGO mechanism.

E170 could not independently recompute two mandatory numerical claims without prohibited execution:

1. absolute reference SE values, because immutable evidence did not retain the `48 x 1024` batch final-mean vectors or coordinatewise SE vectors;
2. parent/AGO MSE values and pooled ratio, because immutable evidence retained final-mean hashes and derived scalars but not the parent/AGO/reference final-mean vectors or error vectors.

Therefore:

- E170 overall verdict: **UNEVALUATED**;
- E169 scientific GO independently certified: **false**;
- public validation authorized: **false**.

E170 is consumed. No second/nested E170 verifier and no E169 rerun to manufacture missing evidence.

## Namespace checkpoint

Fresh intake:

- E171: no branch observed;
- E172: no branch observed;
- no E171 Actions run observed;
- no E172 Actions run observed.

Both identities are collision-free at allocation.

## E171 — sole active scientific owner

Allocate:

**E171 — evidence-complete production-shaped AGO owner.**

E171 is the only active scientific owner.

E171 is a new experiment identity, not an E169 rerun or rescue. It may carry forward the verified E164/E165 AGO mechanism and use E169 only as prior target-free hypothesis evidence.

E171 must use a fresh preregistered synthetic panel. It must not reuse E169's exact ordered weight-seed/reference-seed panel as a new execution.

### Scientific mechanism

Carry forward the verified E164/E165 AGO mechanism without scientific-mechanism change:

1. full-covariance K2 parent;
2. one exact Gaussian-to-angular K1/K2 gauge after the first activation;
3. identical K2 parent closure thereafter;
4. exact final radial `a1(n)` mean readout.

No K4/D4/D22/c4, recurrent higher-order state, target fitting, candidate-specific parent refit, or post-hoc correction.

Production-shaped synthetic networks remain width `1024`, depth `16`, zero bias.

### Evidence-completeness requirement

E171 exists specifically to make every mandatory verifier computation possible from frozen immutable evidence without rerunning the candidate or reference.

Before execution, the protocol must define and the sole owner artifact must retain, at minimum, for every preregistered seed:

1. full parent final-mean vector, length 1024;
2. full AGO final-mean vector, length 1024;
3. full reference final-mean vector, length 1024;
4. all reference batch final-mean vectors used to compute reference SE, or an algebraically sufficient immutable representation from which the exact frozen SE metric can be recomputed;
5. coordinatewise reference SE vector if it is part of the frozen metric;
6. parent error vector `mu_parent - mu_ref`;
7. AGO error vector `mu_ago - mu_ref`;
8. all paired per-batch parent/AGO MSE values or deltas used by the scientific gate;
9. per-seed weight hash and reference-mean hash;
10. exact dtype, shape, byte order and serialization format for every retained numeric array;
11. SHA256 for each retained numeric file/array;
12. one manifest binding every array hash to experiment ID, seed, metric and source step.

The artifact must be sufficient for E172 to recompute, offline and without scientific execution:

- every per-seed absolute reference-SE value;
- every per-seed parent MSE;
- every per-seed AGO MSE;
- every per-seed AGO/parent ratio;
- pooled parent/AGO MSE and pooled ratio;
- paired batch positive counts, mean delta, SE(delta), and mean/SE;
- every scientific threshold comparison that determines GO/NO-GO.

Hashes plus derived scalars alone are not sufficient.

### Preregistered fresh panel and gates

Before implementation/workflow execution, E171 must freeze:

1. verified E164/E165 provenance;
2. explicit statement that E169 is not rerun and E170 is consumed UNEVALUATED;
3. unchanged AGO candidate identity/mechanism;
4. exact number of fresh synthetic network seeds, at least two;
5. exact ordered fresh weight-seed list, excluding the E169 panel `1691024,1692024,1693024`;
6. exact ordered fresh reference-seed list, excluding E169 reference seeds `169196608,169296608,169396608`;
7. deterministic weight generator and per-seed weight-hash procedure;
8. exact per-seed reference sample count, batch count and batch size;
9. exact absolute reference-SE metric and numerical threshold;
10. exact per-seed and aggregate AGO-vs-parent scientific metrics and thresholds;
11. exact cross-seed consistency rule;
12. exact paired-batch improvement rule;
13. complete evidence-retention schema above;
14. target-free residual/error certificate appropriate to the production-shaped claim;
15. complete deployed-estimator cost and independent reconciliation against `0.135 * 2^41`;
16. separate complete reference/test/evidence-materialization cost accounting;
17. memory/storage/runtime accounting for retaining immutable vectors;
18. deterministic replay;
19. target/oracle/public/public-mini/scorer/holdout/full/submission firewall;
20. terminal kill rule;
21. exactly one physical E171 owner workflow containing the complete fresh panel;
22. no sweep, tuning, rescue, rerun, retry, seed/reference/threshold/mechanism/evidence-schema substitution or post-result repair.

No seed may be added, removed, replaced, reordered, or selectively excluded after execution begins.

No post-hoc gate change.

### One-run authorization

After a valid protocol-first freeze, E171 may implement the minimum target-free evidence-complete owner harness and execute **exactly one** physical scientific workflow run.

Every preregistered seed, mandatory scientific gate, evidence-completeness gate and artifact hash/manifest gate must pass inside that one run.

Any failed, skipped, nonfinite or unevaluable mandatory gate — including missing immutable vectors, malformed artifact, storage/resource failure, replay failure, reference failure or scientific failure — consumes the authorization and closes E171 absent later explicit control.

No second run.

## E172 — sole independent verifier

E172 is reserved as exactly one independent review-only verifier for E171.

Do not create or execute E172 before a complete frozen E171 owner tuple and evidence-complete artifact exist.

After the sole E171 run, freeze:

- E171 branch/experiment identity;
- protocol SHA/blob;
- verified E164/E165 provenance;
- candidate identity;
- ordered fresh weight/reference seed lists and weight hashes;
- per-seed reference design;
- absolute-SE metric/threshold;
- implementation/reference/test/falsifier/workflow SHAs/blobs;
- executed head;
- run/job/attempt;
- artifact ID/name/ZIP SHA256;
- immutable owner receipt SHA/blob;
- evidence manifest SHA;
- hashes, shapes and dtypes for every retained numeric array;
- per-seed reference precision;
- per-seed parent/AGO metrics;
- aggregate metrics;
- paired-batch statistics;
- target-free certificate;
- estimator/reference/evidence-materialization costs;
- memory/storage/resource evidence;
- deterministic replay;
- firewall.

Only then may E172 execute exactly one independent verification.

E172 must recompute mandatory numerical science **from the retained immutable arrays**, not from owner-derived scalar claims:

1. reference SE for every seed;
2. parent and AGO MSE for every seed;
3. per-seed ratios;
4. pooled parent/AGO MSE and pooled ratio;
5. paired-batch positive counts, mean delta, SE(delta), and significance ratio;
6. every preregistered threshold comparison;
7. cross-seed consistency;
8. evidence manifest/hash integrity;
9. AGO mechanism identity and no closed-lane rescue;
10. complete estimator and separate research/evidence cost accounting;
11. deterministic replay evidence and resource accounting;
12. zero public/public-mini/scorer/holdout/full/submission access;
13. frozen provenance and no post-result mutation.

E172 may inspect/recompute frozen evidence only. It may not execute the scientific candidate/reference, regenerate missing vectors, modify, rerun, tune, rescue, substitute, repair, change gates, or publicly validate E171.

Exactly one verifier execution/receipt. No nested verifier.

If any mandatory vector/evidence is missing, E172 must fail/unevaluate rather than regenerate it.

## Public-target firewall

No public run is authorized.

Public/public-mini targets, holdout, official scorer, full suite and submission remain **BLOCKED** regardless of E169 owner GO.

E171 GO or E172 PASS also does not itself execute public work; a later explicit control allocation would still be required.

## Hard rejection rules

Reject and fail closed:

- E169 rerun/rescue/reference regeneration/vector reconstruction by execution;
- second/nested E170;
- E154/E157/K4 rescue;
- E164 owner rerun;
- reuse of E169 exact seed/reference panel as E171 execution;
- post-hoc E171 gate, seed, reference or evidence-schema changes;
- adaptive reference sizing;
- seed search/drop/replacement/selective reporting;
- E171 second run/retry;
- premature/repeated E172;
- verifier regeneration of missing evidence;
- public/public-mini/holdout/scorer/full/submission access;
- target fitting;
- scientific sweeps;
- duplicate/colliding IDs;
- speculative ledger/status promotion;
- mutation of `research/bootstrap`;
- mutation of `research/ledger.csv`;
- canonical merge/integration.

## Exact next action

Create one collision-free **protocol-first E171 evidence-complete AGO** owner freeze with a fresh preregistered multi-seed `1024 x 16` panel and immutable vector-retention schema sufficient for E172 to recompute every scientific gate without candidate/reference execution.

Then execute at most one target-free E171 physical workflow run.

Only after a complete frozen evidence artifact may E172 verify it.

Do not mutate canonical or ledger.
