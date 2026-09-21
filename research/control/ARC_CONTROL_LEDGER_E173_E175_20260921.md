# ARC control ledger — E173 local AGO mini-benchmark / E174 verifier / E175 result-driven research

Recorded: 2026-09-21

Control key: `ARC-CONTROL-LEDGER-E173-E175-20260921`

Prior control receipt:

`control/arc-deep-error-frontier-20260919@897e1b5beec0b9ddd61d1a723a68004c59faa0d6`

Status: **E171/E172 INDEPENDENT GO FROZEN / E173 ACTIVE OWNER / E174 RESERVED VERIFIER / E175 RESERVED RESEARCH / RESULT-DRIVEN TRIGGER / APPEND-ONLY CONTROL**.

This is the only active control-ledger allocation for E173-E175. It adds the missing post-E172 tasks without duplicating earlier E171/E172 control records. It does not mutate `research/ledger.csv`, `research/bootstrap`, canonical history, or leaderboard state.

## Verified prerequisite — E171/E172

E171 owner:

`research/e171-verifier-ready-ago-20260921@fea2747b04bd8027bdd98c9680ebce1dc1bb022c`

Owner execution:

- run/job/attempt: `35613064558 / 106376772199 / 1`;
- executed head: `7e94835606dd5c48eb5fc5a8244c75957ba9beb0`;
- artifact: `10645164045`, `e171-verifier-ready-ago`;
- artifact ZIP SHA256: `f8c25a1f962811f7addc91a66e79ef3a916e4c5961f3a8851c1d76c8550e7406`;
- owner receipt commit/blob: `fea2747b04bd8027bdd98c9680ebce1dc1bb022c / bdba803680a3a51f695b942298612719ed409f20`;
- evidence manifest SHA256: `e7dd9febd03f2cd338de082bc8610be3c882186c3014188adc42796203ad1cdd`.

Frozen E171 science:

- pooled parent MSE: `3.9298876324663385e-6`;
- pooled AGO MSE: `3.32829036514411e-6`;
- pooled AGO/parent ratio: `0.8469174379561903`;
- pooled improvement: `15.308256204380966%`;
- all three fresh 1024x16 seeds improved;
- absolute reference-SE gate passed for all seeds;
- paired batch positives: `131/144`;
- batch mean / SE: `15.549951719545932`;
- deployed estimator all-in: `112131571712 FLOPs = 0.05099153518676758 B`.

Independent verifier:

`review/e172-e171-independent-verifier-20260921@423edafe9e7a1c83b6e58ec1ea4862becafc2162`

Receipt:

`research/E172_E171_INDEPENDENT_VERIFIER_RECEIPT.json`

Decision:

`E172_INDEPENDENT_VERIFIER_GO_E171_VERIFIER_READY_AGO`.

E172 independently recomputed the mandatory reference-SE, per-seed MSE, pooled MSE ratio, paired-batch statistics and payload hashes from the immutable E171 vectors and returned overall `GO`.

E172 explicitly records:

- all requested numeric recomputations independently verified;
- provenance/cost/firewall/replay/ancestry verified;
- scientific scope limited to synthetic target-free production-shaped E171 AGO;
- public validation authorization: `false`;
- no candidate/reference scientific execution by verifier;
- no rerun/rescue/canonical-ledger mutation.

This satisfies the prerequisite for the next local integration stage.

## Control ledger — authoritative E173-E175 tasks

| ID | Role | Status | Dependency | Authorized scope | Completion trigger |
|---|---|---|---|---|---|
| **E173** | **owner** | **ACTIVE** | E172 independent GO | Branch-local AGO integration into the estimator/runtime plus one frozen local mini-benchmark | Complete immutable E173 owner tuple and benchmark receipt |
| **E174** | **verifier** | **RESERVED / BLOCKED ON E173** | Complete admissible E173 tuple | One independent review-only verification of E173 | E174 PASS/FAIL/UNEVALUATED receipt |
| **E175** | **research** | **RESERVED / BLOCKED ON E174** | Completed E174 receipt | Analyze E173+E174 evidence and recommend the next experiment/control allocation | Evidence-based next-experiment decision memo; no automatic scientific run |

No duplicate E173, E174 or E175 task is active elsewhere at this checkpoint. Fresh branch intake found no E173/E174/E175 branches and recent Actions intake found no E173/E174/E175 runs.

## E173 — sole active owner

Reserve identity:

`ARC-E173-LOCAL-AGO-MINI-BENCHMARK-20260921`

Recommended branch identity:

`research/e173-local-ago-mini-benchmark-20260921`

E173 is the only active owner.

### Authorized scope

E173 may:

1. integrate the E171/E172-verified AGO mechanism into a **branch-local** estimator/runtime path;
2. preserve a selectable frozen non-AGO baseline for exact comparison;
3. add focused integration tests and provenance guards;
4. run one preregistered **local mini-benchmark** after integration is frozen;
5. materialize an immutable evidence artifact sufficient for E174 verification.

The mini-benchmark authorization is narrow. E173 may use only the frozen local mini-benchmark inputs/harness declared in its protocol. If that harness uses the repository's public-mini inputs, access is permitted **only for this local mini-benchmark evaluation**.

This receipt does **not** authorize:

- external submission;
- official scorer submission;
- holdout;
- full benchmark/full suite;
- leaderboard write/update;
- publication of a score as an official leaderboard result;
- canonical merge;
- canonical or research-ledger mutation.

### Mechanism freeze

The integrated scientific mechanism must remain the independently verified AGO mechanism from E171/E172:

- E164 candidate blob: `ea9078eccc2e2bf2a2bea499ef10a4daf80ea0d4`;
- runtime source SHA256: `533149d0a1c05be12097b997b8762270b299c574cf6c32324de7d17ec285169c`;
- full-covariance K2 parent;
- one exact Gaussian-to-angular K1/K2 gauge after first activation;
- identical K2 closure thereafter;
- exact final radial `a1(n)` readout.

E173 may adapt integration interfaces/wrappers required by the local estimator, but any arithmetic change to the scientific AGO mechanism must be declared before benchmark execution and independently justified as equivalence. Hidden mechanism changes, target fitting, benchmark-conditioned tuning, or post-result patching are forbidden.

### Protocol-first E173 freeze

Before the mini-benchmark execution, E173 must freeze:

1. exact E171/E172 provenance;
2. exact integration branch point;
3. exact files/interfaces modified for local AGO integration;
4. exact AGO mechanism identity and equivalence guard;
5. exact baseline estimator identity;
6. exact local mini-benchmark dataset/input identity and hash;
7. exact benchmark harness/script identity;
8. exact metric definitions;
9. exact pass/fail or interpretation rules fixed before benchmark results;
10. exact run count: one frozen mini-benchmark evaluation;
11. immutable output/evidence schema retaining per-case results needed for E174 recomputation;
12. runtime/dependency/environment manifest;
13. deployed FLOP/cost accounting and any integration overhead;
14. deterministic replay where applicable;
15. explicit external-submission/holdout/full/leaderboard firewall;
16. terminal rule: no post-result threshold change, target-conditioned tuning, sweep, rescue or benchmark rerun under E173.

Implementation/unit/integration tests may run before the benchmark arm is frozen. They must not inspect mini-benchmark target outcomes for tuning.

After the benchmark arm is frozen, E173 gets exactly one benchmark evaluation.

Any benchmark infrastructure failure, incomplete evidence, forbidden access, or mandatory gate failure consumes E173's benchmark authorization and is reported as such. No automatic retry.

## E174 — sole verifier, event-gated after E173

Reserve identity:

`ARC-E174-E173-INDEPENDENT-VERIFIER-20260921`

Recommended branch identity:

`review/e174-e173-independent-verifier-20260921`

E174 must not be created/executed merely because time elapsed.

**Trigger E174 only when a complete immutable E173 owner tuple exists.**

Required E173 tuple:

- branch and experiment ID;
- protocol SHA/blob;
- integration branch point;
- integrated AGO source/interface SHAs/blobs;
- frozen baseline identity;
- mini-benchmark input/harness identities and hashes;
- executed head;
- run/job/attempt;
- artifact ID/name/ZIP SHA256;
- immutable owner receipt SHA/blob;
- per-case retained benchmark evidence;
- aggregate metrics;
- integration-equivalence evidence;
- FLOP/cost result;
- environment/dependency manifest;
- replay evidence;
- external-submission/holdout/full/leaderboard firewall evidence.

E174 may inspect/recompute frozen evidence only.

E174 must independently verify:

1. E171/E172 provenance;
2. AGO mechanism equivalence after local integration;
3. baseline identity;
4. benchmark preregistration and no result-conditioned tuning;
5. mini-benchmark input/harness identity;
6. per-case and aggregate benchmark arithmetic from retained evidence;
7. cost/integration overhead;
8. replay/provenance;
9. no external submission, holdout/full execution, scorer submission, or leaderboard mutation;
10. no post-result rerun/rescue/sweep.

Exactly one E174 verifier receipt. No nested verifier and no E173 scientific rerun to satisfy verifier gaps.

## E175 — research task, event-gated after E174

Reserve identity:

`ARC-E175-POST-E174-RESULT-DRIVEN-RESEARCH-20260921`

E175 is **research-only**, not a pre-authorized scientific experiment.

Do not activate E175 by timer.

**Trigger E175 only after E174 has emitted its immutable verifier receipt**, regardless of whether E174 returns PASS, FAIL, or UNEVALUATED.

E175 must:

1. read the frozen E173 owner result and E174 verifier result;
2. identify the dominant remaining blocker/opportunity from those actual results;
3. compare only scientifically distinct next-step classes relevant to that blocker;
4. reject reopening terminal/rescue lanes unless separately authorized;
5. produce one evidence-based next-experiment decision memo with:
   - proposed new experiment identity;
   - mechanism/hypothesis;
   - why it follows from E173/E174 evidence;
   - falsifier;
   - cost/compute envelope;
   - required evidence-retention schema;
   - exact kill rule;
   - whether any local/public/holdout/scorer access would be required;
6. stop at the decision memo.

E175 does **not** itself authorize or execute the proposed next experiment. A new explicit control allocation is required.

## Result-driven trigger graph

The control transition is strictly event-driven:

`E172 GO -> E173 owner result -> E174 verifier receipt -> E175 research decision -> explicit control decision on next experiment`.

There is **no timer-based promotion** between these stages.

Absence of a result means remain at the current gate. Do not create downstream work merely because an hour/day elapsed.

## External/leaderboard firewall

Until a separate explicit confirmation:

- no external submission;
- no official scorer submission;
- no holdout;
- no full benchmark/full suite;
- no leaderboard mutation/update;
- no claim that a local mini-benchmark result is an official leaderboard score.

E173 local mini-benchmark permission does not imply any of the above.

## Ledger/canonical firewall

Do not mutate:

- `research/ledger.csv`;
- `research/bootstrap`;
- canonical integration history.

This control-ledger receipt is append-only and is the authoritative allocation for E173-E175.

## Exact next trigger

**Now:** E173 owner only.

**When and only when E173 freezes a complete immutable owner tuple:** dispatch E174 exactly once.

**When and only when E174 freezes its verifier receipt:** dispatch E175 research to choose the next experiment from the observed evidence.

Do not advance by timer. Do not submit externally. Do not mutate leaderboard or canonical ledger.
