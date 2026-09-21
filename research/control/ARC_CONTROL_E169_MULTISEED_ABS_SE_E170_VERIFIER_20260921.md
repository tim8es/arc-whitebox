# ARC control update — E169 preregistered multi-seed absolute-SE AGO / E170 verifier

Recorded: 2026-09-21

Control key: `ARC-CONTROL-E169-MULTISEED-ABS-SE-E170-20260921`

Prior control receipt:

`control/arc-deep-error-frontier-20260919@a28995ec9ab87da327be3302a561316dc6e0c1e5`

Status: **VERIFIED E164/E165 GO FROZEN / E166-E167 CLOSED / E169 SOLE OWNER / E170 SOLE VERIFIER / APPEND-ONLY CONTROL**.

This receipt preserves E164/E165 as verified target-free AGO GO, closes E166/E167 without rerun, and allocates E169/E170. It does not authorize public/public-mini targets, holdout, scorer, full suite, submission, post-hoc gate changes, sweeps, canonical mutation, ledger mutation, merge, or status-only promotion.

## E164/E165 — verified target-free AGO GO remains frozen

Owner:

`research/e164-cleanroom-ago-20260921@342f2ab03ad5251971b17f8d8d43c1861774cbb6`

Independent verifier:

`review/e165-e164-independent-verifier-20260921@c5e3e011a7ee6f420435c8b307034efb17720b8a`

Verifier decision:

`E165_INDEPENDENT_VERIFIER_GO_E164_CLEANROOM_AGO`

Frozen result:

- pooled AGO/parent MSE ratio: `0.6661376209420509`;
- all three frozen E164 fixtures improved;
- production all-in upper: `112131571712 FLOPs = 0.05099153518676758 B`;
- target/public firewall: PASS;
- deterministic replay: PASS;
- clean-room ancestry: PASS.

No E164/E165 rerun, rescue, retune, post-result repair, or ledger promotion.

## E166 — terminal, positive production-shaped AGO signal but uncertified reference

Authoritative branch:

`research/e166-production-shaped-ago-20260921@6acb17f836806226f5f9d3ab996a9198927f2532`

Execution:

- run/job/attempt: `35606863697 / 106355965383 / 1`;
- executed head: `40c9177a3f32d38d915b9f5da7c40431284859d1`;
- artifact: `10642051274`, `e166-production-shaped-ago`;
- artifact SHA256: `98c21ee635ceb8a224bd693177c7a1214cfd161b47d12bc14f254929009f9994`.

Frozen signal:

- parent MSE: `1.8811649099480322e-5`;
- AGO MSE: `1.7538238290386996e-5`;
- AGO/parent ratio: `0.9323073271057079`;
- improvement: `6.769267289429215%`;
- improved `6/8` batch references;
- batch delta mean / SE: `2.620904337760046`.

Terminal blocker:

- reference SE RMS: `0.0030812641362217745`;
- allowed frozen SE: `0.000837573597730659`;
- ratio: `3.678797664878309`.

E166 remains terminal. No rerun, reference enlargement, threshold change, rescue, or reinterpretation.

## E167 — terminal reference-precertification failure before AGO execution

Authoritative branch:

`research/e167-precertified-reference-ago-20260921@8a0fab382bb5d2f13528f965bb2a83dc373b62e2`

Frozen provenance:

- protocol commit/blob: `431685e6dcf80a2f1841e7f0229234bf5110eabf / d542c0a4a4c2367fa310669d5f8fef94b858bccf`;
- reference commit/blob: `aa8b26f86d72fbff6922c7159934f9d6cf76ff67 / f8fdb5f4855dbf175d9d67638b15c49471004c9a`;
- tests commit/blob: `e1202f23219bae852f6f151466ba6d09daae006f / d9691c812682b8c6eec63c476e36db5a650940cd`;
- falsifier commit/blob: `5a18296b5780b5dfd17b085defb9c3f4b32e3a96 / ddf801086d65d459120d42842d7e405e0fca4fe5`;
- workflow commit/blob: `3a73270a620faa48649c6ba3577fe3a95b1eeaad / e674d6f98df642d526108e7ed0bb815981c15d3d`;
- arm/executed head: `458ef70f8e47b8ae092b257409f1c7e9b0a5980a`;
- run/job/attempt: `35607925972 / 106359504079 / 1`;
- artifact: `10642563726`, `e167-precertified-ago`;
- artifact SHA256: `41e1bd0867180c7ac7dbd9abe03f5936e88321183b1fbe7fc8b70b4a7c5371bd`;
- decision: `E167_TERMINAL_NO_GO_REFERENCE_PRECERTIFICATION`.

Frozen reference design:

- production shape: `1024 x 16`;
- network seed: `1671024`;
- antithetic reference samples: `196608`;
- reference seed: `167196608`;
- batches: `48`;
- batch size: `4096`.

Observed reference result:

- reference SE RMS: `0.0005905340995593883`;
- frozen absolute SE limit: `0.0007` -> **PASS**;
- parent RMSE: `0.0019511739426750251`;
- frozen parent-relative 20% limit: `0.000390234788535005` -> **FAIL**;
- SE / parent-relative limit: `1.513283096008744`;
- precision gain versus E166 reference: `5.21775804650947x`.

The E167 protocol correctly stopped before AGO execution. Therefore:

- E167 AGO MSE: **NOT EVALUATED**;
- E167 AGO/parent ratio: **NOT EVALUATED**;
- no E167 AGO effect claim is admissible.

Durable evidence supports: E166 showed a positive AGO production-shaped signal; E167 showed that a much larger preregistered reference can pass the frozen absolute-SE gate, but its separate parent-relative gate failed before candidate execution.

E167 is terminal. No rerun, seed change, reference increase, gate weakening, candidate execution, rescue, or reinterpretation.

E168 is closed unused because E167 did not produce an admissible owner result for verification.

## Namespace checkpoint

Fresh intake:

- `research/e169-multiseed-ago-20260921` exists at `342f2ab03ad5251971b17f8d8d43c1861774cbb6`;
- it contains no E169 delta relative to that E164 receipt head and is treated only as an empty namespace reservation;
- no E169 Actions run observed;
- no E170 branch observed;
- no E170 Actions run observed.

E169/E170 are collision-free for the new allocation.

## E169 — sole active scientific owner

Allocate:

**E169 — preregistered multi-seed production-shaped AGO with absolute-SE reference certification.**

E169 is the only active scientific owner.

E169 is a new experiment identity. It is not an E166 or E167 rerun/rescue.

### Scientific mechanism

Carry forward the verified E164/E165 AGO mechanism without scientific-mechanism change:

1. full-covariance K2 parent;
2. one exact Gaussian-to-angular K1/K2 gauge after the first activation;
3. identical K2 parent closure for later layers;
4. exact final radial `a1(n)` mean readout.

No K4/D4/D22/c4, recurrent higher-order state, target fitting, candidate-specific parent refit, or post-hoc correction.

Production-shaped synthetic networks remain width `1024`, depth `16`, zero bias.

### Multi-seed requirement

E169 must preregister a fixed multi-network design before any E169 scientific execution.

The owner protocol must freeze:

1. exact number of synthetic network seeds, with at least two distinct seeds;
2. exact ordered seed list;
3. deterministic weight generator and per-seed weight-hash procedure;
4. one identical AGO/parent mechanism across every seed;
5. exact per-seed reference design;
6. exact aggregate-across-seeds scientific statistic;
7. exact per-seed and aggregate pass/fail rules;
8. exact handling of a failed/unevaluable seed.

No seed may be added, removed, replaced, reordered, or selectively excluded after execution begins.

No seed search.

### Absolute-SE reference certification

E169 intentionally tests a **new preregistered absolute-SE certification class**. This does not modify E166/E167 gates; those lanes remain terminal under their original protocols.

Before any E169 run, freeze:

1. one absolute reference SE metric;
2. one numerical absolute-SE threshold;
3. exact sample/design size per seed;
4. exact reference RNG seed or deterministic point-set identity per network seed;
5. exact batching/replication plan;
6. exact precision estimator;
7. exact pre-candidate or leakage-proof reference-certification ordering;
8. a-priori justification for the fixed absolute-SE threshold and reference budget that does not depend on any E169 observed candidate result;
9. exact failure rule.

The threshold must be fixed in the protocol before E169 reference or AGO results exist.

Forbidden after execution begins:

- changing the absolute-SE threshold;
- adding samples;
- changing reference seeds;
- changing batch count/size;
- substituting a relative-SE gate;
- dropping a difficult seed;
- using an observed E169 effect size to relax precision;
- selecting among multiple reference designs.

E166/E167 historical evidence may be cited only as pre-experiment design motivation. It cannot satisfy an E169 gate.

### Mandatory protocol-first freeze

Before implementation/workflow execution, E169 must freeze:

1. verified E164/E165 provenance;
2. explicit statement that E166/E167 remain terminal and are not being rerun;
3. unchanged AGO candidate identity/mechanism;
4. fixed multi-seed network design;
5. complete absolute-SE reference design for every seed;
6. leakage-proof execution ordering;
7. frozen primary per-seed and aggregate AGO-vs-parent scientific metrics;
8. frozen numerical scientific thresholds and cross-seed consistency rule;
9. frozen absolute-SE certification threshold and failure rule;
10. target-free residual/error certificate appropriate to the multi-seed production-shaped claim;
11. complete deployed-estimator production cost and independent reconciliation against `0.135 * 2^41`;
12. separate complete reference/test cost accounting across all seeds;
13. memory/runtime/resource accounting;
14. deterministic replay for parent and AGO per seed;
15. target/oracle/public/public-mini/scorer/holdout/full/submission firewall;
16. terminal kill rule;
17. exactly one physical E169 owner run containing the entire preregistered multi-seed experiment;
18. no sweep, tuning, rescue, rerun, retry, seed/reference/threshold/mechanism substitution or post-result repair.

### One-run authorization

After a valid protocol-first freeze, E169 may implement the minimum target-free multi-seed owner harness and execute **exactly one** physical scientific workflow run.

Every preregistered seed and every mandatory gate must be evaluated inside that one run.

Any failed, skipped, nonfinite or unevaluable mandatory gate — including absolute-SE, infrastructure, resource, replay, firewall or cross-seed gate — consumes the authorization and closes E169 absent a later explicit control update.

No second run.

## E170 — sole independent verifier

E170 is reserved as exactly one independent review-only verifier for E169.

Do not create or execute E170 before a complete frozen E169 owner result exists.

After the sole E169 run, freeze:

- branch/experiment identity;
- protocol SHA/blob;
- verified E164/E165 provenance;
- candidate identity;
- exact ordered network seed list and per-seed weight hashes;
- per-seed reference design/seeds/sample counts/batches;
- absolute-SE metric and frozen threshold;
- implementation/reference/test/falsifier/workflow SHAs/blobs;
- executed head;
- run/job/attempt;
- artifact ID/name/SHA256;
- immutable owner receipt SHA;
- per-seed reference precision;
- per-seed parent/AGO metrics;
- aggregate cross-seed statistic;
- target-free certificate;
- estimator and total reference/test cost accounting;
- memory/resource evidence;
- deterministic replay;
- firewall.

Only then may E170 execute exactly one independent verification.

E170 must independently verify/recompute:

1. protocol-first identity and no E166/E167 rerun/rescue;
2. exact E164/E165 AGO mechanism carry-forward;
3. seed list and reference design were frozen before execution;
4. no seed selection/drop/replacement;
5. no post-hoc absolute-SE threshold or gate changes;
6. per-seed reference precision arithmetic;
7. per-seed and aggregate AGO-vs-parent metrics;
8. cross-seed scientific pass rule;
9. target-free certificate;
10. complete estimator and separate reference/test cost accounting;
11. deterministic replay and resource evidence;
12. zero public/public-mini/scorer/holdout/full/submission access;
13. frozen run/artifact provenance and no post-result mutation.

E170 may inspect/recompute frozen evidence only. It may not modify, regenerate, rerun, tune, rescue, substitute, repair, drop seeds, change gates, or publicly validate E169.

Exactly one verifier execution/receipt. No nested verifier.

Premature E170 activity fails closed.

## Public-target firewall

Public/public-mini targets, holdout, official scorer, full suite and submission remain **BLOCKED**.

E164/E165 verification does not implicitly authorize them. E169/E170 cannot unlock them without a later explicit control allocation.

## Hard rejection rules

Reject and fail closed:

- E166 or E167 rerun/rescue;
- E154/E157/K4 rescue;
- E164 owner rerun;
- any post-hoc E169 absolute-SE/scientific gate change;
- adaptive E169 sample/reference sizing;
- seed search, seed replacement, seed dropping or selective reporting;
- E169 second run/retry;
- premature/repeated E170;
- public/public-mini/holdout/scorer/full/submission access;
- target fitting;
- scientific sweeps;
- duplicate/colliding IDs;
- speculative ledger/status promotion;
- mutation of `research/bootstrap`;
- mutation of `research/ledger.csv`;
- canonical merge/integration.

## Exact next action

On the existing empty `research/e169-multiseed-ago-20260921` reservation, create one protocol-first E169 freeze that preregisters the entire multi-seed `1024 x 16` experiment and one absolute-SE reference certification rule before any scientific execution.

Then execute at most one target-free E169 physical workflow run.

Only after a complete frozen E169 result may E170 verify it.

Do not mutate canonical or ledger.
