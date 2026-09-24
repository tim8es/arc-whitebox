# R351 — time-of-review re-audit of H185 launch gate after E190 recovery

**Status:** COMPLETE  
**Decision:** **GATE_REMAINS_BLOCKED_G2_EXACT_DENSE_DENOMINATOR_MISSING**  
**Authorization:** **NONE — this review does not authorize H185 or any run**

Exact R351 base:
`4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

R351 is a read-only independent gate review. It does not run an estimator/candidate, rerun E190/F86, download artifacts, trigger Actions, access targets/private/holdout/full data, submit, or edit R320/control/queue/PR/main.

## 1. Live lineage inspected

### E187 — frozen H185 protocol

Branch:
`research/e187-h185-protocol-hardening-20260922`

Live head:
`06fbb08fb9ece3b5b3d8da7b60fee331030a044f`

Relevant immutable artifacts:
- `research/E187_H185_PROTOCOL_REVISION.md` — blob `d623a9348518c0afe2869fc89f44a746960e81f5`
- `research/e187/E187_H185_PROTOCOL_LOCK.json` — blob `215187db7fb4a3ba391a1229e48ce6a482bebd97`
- `research/e187/E187_PARENT_LEDGER.json` — blob `33699fbfa47e23ffef99b6a99e064aa130100671`

Frozen E187 state:
- protocol status: `NO_GO`
- owner run authorized: **false**
- `current_authorized_owner_runs=0`
- dense K3 source-resolution display: `222.44u`
- fixed/remainder source-resolution display: `37.62u`
- whole grouped display: `260.06u`
- G2 blocker: exact raw parent ledger.

### E190 — later committed recovery

Branch:
`research/e190-cost-evidence-recovery-20260922`

Live head:
`7145df65c84970eeab5dbfb48d1045eaee8be7ca`

Parent:
E187 head `06fbb08fb9ece3b5b3d8da7b60fee331030a044f`

Relevant immutable artifacts:
- `research/E190_COST_EVIDENCE_RECOVERY.md` — blob `976ebe39a06092bbc5838ea3f249cc5348bc87a5`
- `research/e190/E190_RECOVERED_PARENT_LEDGER.json` — blob `4ba395635e08f9fafd592edd8978207341d7d42a`

E190 now supplies a machine-readable exact whole-parent total:

> **558,473,140,719 FLOPs**

The ledger binds that total to existing E136 evidence and bridges it to the F86 second-predict cost fingerprint through estimator identity and namespace-only wrapping semantics.

R351 independently recomputed the basic arithmetic from the integer:
- units: `558473140719 / 2^31 = 260.059321634005755186...u`
- budget ratio: `558473140719 / 2^41 = 0.253964181283208745...`
- formatted total: `260.1u`
- formatted grouped-scale total: `260.06u`
- formatted C/B: `0.2540`

Those are consistent with F86 displays.

E190 also explicitly records:
- `exact_dense_raw_flops_recovered: false`
- `exact_remainder_raw_flops_recovered: false`
- exact per-namespace raw FLOP integers are not recovered.

### E191 — independent review at earlier repository state

Branch:
`review/e191-e190-independent-review-20260922`

Live head:
`37488d6e9abd52c625cde9506f541dcd85c70701`

Parent:
E187 head `06fbb08fb9ece3b5b3d8da7b60fee331030a044f`

Artifact:
- `research/E191_E190_INDEPENDENT_REVIEW.md` — blob `04a7407a0b93580b9868ffcc28d461ee91c4f89a`

No separate E191 JSON receipt is present in the live E191 branch tree; the review report contains the gate criteria and verdict.

E191 correctly recorded that E190 was not visible in the repository state it reviewed. That time-of-review visibility problem is now resolved because E190 is committed and live.

However, the premise that E191 rejected **only** because E190 was invisible is incomplete. E191 §6 explicitly says:

> even if an exact total `ctx.flops_used` integer were supplied, H185 cost gating still needs the exact dense-parent denominator and coverage map.

E191 requires:
1. exact total parent FLOPs;
2. exact dense K3 parent FLOPs for the eleven mapped namespaces;
3. exact fixed/remainder FLOPs;
4. reconciliation of those exact values to the same `ops=13121` call-2 ledger.

Its promotion rule additionally requires an immutable raw evidence object from which an independent verifier can recompute exact total, dense subtotal, fixed subtotal, and formatting consistency.

### E193 — live-ref/receipt check

R351 found **no live E193 branch/ref** in the repository branch search, no E193 commit-search result, no default-branch E193 code/file search result, and no E193 entry in the current read-only `research/control/state.json` snapshot inspected.

Therefore:
- no E193 head can be cited;
- no E193 receipt can be consumed;
- no E193 evidence contributes to this gate decision.

This is an absence finding about the repository surfaces inspected, not a claim about any uncommitted/local coordinator work.

## 2. F86 source semantics verified

Pinned upstream F86 source:
- repository `504aldo/whest-p2-cumulant-k3`
- commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`

Verified immutable blobs:
- namespace log `docs/audit_v29_ns_d0.log` — `a689ef69fd64bed7765cb93ce4910c3fedcbd04a`
- audit harness `harness/audit_v29_ns.py` — `279d8e0308360fde7616d56f8e8cc2705b529898`
- plain V29 `estimators/estimator_v29.py` — `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`
- namespaced V29 `estimators/estimator_v29_ns.py` — `f91df783b83cb5fae0af57a16799c5df81891bd2`
- namespace generator `generators/make_v29_ns.py` — `6c0e439eaeefcb2e06991cb86d9bda3b174fc30d`

The harness semantics are explicit:
- call 1 is warm-up / `STRASSEN_FIRST`;
- **call 2 is the steady-state ledger**;
- raw total is captured as `C = float(ctx.flops_used)`;
- `ctx.op_log` is aggregated by namespace;
- an assertion checks `sum(fam.values()) == C` within tolerance;
- only formatted displays are persisted to the committed text log:
  - total to 0.1u;
  - family/group units to 0.01u;
  - C/B to four decimals.

The committed call-2 log reports:
- `ops=13121`
- total `260.1u / 0.2540B`
- grouped dense `222.44u`
- grouped remainder `37.62u`.

The 26 persisted family call counts sum exactly to **13,121**, matching call 2.

For the eleven E187 dense namespaces:
`young_transport, hub, shared, old_legs, j_rf, j_rot, j_proj, j_tier2, j_qc, j_core, qc_transport`

the persisted family call counts sum to **6,172**.

But call counts do not determine exact FLOPs because the namespaces contain heterogeneous shapes/operations.

A useful precision check is that the eleven **display-rounded** family unit rows sum to `222.45u`, while the grouped dense row is `222.44u`. This is expected because the grouped value is computed from unrounded internal `fam` costs and only then formatted. It proves that exact dense FLOPs must not be reconstructed by summing rounded family displays.

## 3. E191 criterion-by-criterion re-audit with E190 now visible

| Criterion | R351 result | Evidence |
|---|---|---|
| E190 immutable/live | **PASS** | branch/head/report/ledger now committed |
| exact whole-parent total | **PASS as persisted recovery evidence** | E190: `558473140719` |
| total formatting matches F86 call 2 | **PASS** | recomputed `260.1u`, `260.06u`, `0.2540B` |
| pinned estimator/source semantics | **PASS for lineage/bridge** | exact source blobs and namespace-only generator verified |
| exact raw F86 namespaced receipt/op-log | **FAIL / ABSENT** | neither F86 Git tree nor E190 contains it |
| exact dense K3 subtotal across 11 namespaces | **FAIL / MISSING** | E190 explicitly says not recovered |
| exact fixed/remainder subtotal | **FAIL / MISSING** | E190 explicitly says not recovered |
| exact dense + fixed = exact total from same ledger | **FAIL / NOT RECOMPUTABLE** | component integers absent |
| exact denominator for `C_TA_dense / C_parent_dense <= 0.42` | **FAIL / MISSING** | `222.44u` is rounded display only |
| exact same-ledger `ops=13121` reconciliation | **PARTIAL** | call count and total semantics known; exact per-entry FLOPs absent |
| data sufficient for `HARDENING_READY` | **NO** | E191 G2 package remains incomplete |

Thus E190 fixes E191's immutability/visibility objection for the **whole total**, but does not satisfy every E191 promotion criterion.

## 4. Why the exact total cannot substitute for the dense denominator

The H185 mechanism gate is on the dense transformed portion, not the entire estimator:

`C_TA_dense / C_parent_dense <= 0.42`.

Using `558,473,140,719` as the denominator would be semantically wrong because it includes all fixed/remainder work.

Using `222.44 * 2^31` would reverse-engineer an integer from a rounded display, which E191 explicitly forbids and R351 does not do.

Subtracting rounded `37.62u` from the exact total has the same defect: the remainder display is rounded and therefore cannot produce an exact dense integer.

The immutable source semantics explain how exact dense cost would have been available at runtime—sum the exact `r.flop_cost` values in the eleven namespaces from the call-2 `ctx.op_log`—but the raw op-log itself was not persisted.

## 5. Minimal missing exact artifact

The minimal missing evidence remains exactly the object identified by E191:

> **A content-addressed immutable raw F86 dump0/call-2 steady-state flopscope receipt or op-log, under the pinned V29 namespaced estimator/audit blobs, containing the exact total `ctx.flops_used` and exact per-operation or per-namespace integer FLOP costs for the same `ops=13121` ledger.**

It must permit an independent verifier to establish, without rounded-display inversion:

1. exact total = sum of exact ledger entries;
2. exact dense subtotal = sum of the eleven E187 dense namespaces;
3. exact fixed subtotal = sum of all remaining frozen namespaces;
4. exact dense + exact fixed = exact total;
5. exact values format consistently with the published F86 displays.

A proof-grade **static** exact-cost artifact could only substitute if it derives the same exact per-namespace integers from the pinned immutable source plus exact flopscope billing semantics, with no use of rounded displays as numerical inputs, and is independently reviewable. No such artifact is present in E187/E190/E191.

## 6. Is any one-time target-free recovery currently permitted?

Two cases must be separated.

### New execution-based recovery

**NO — not under the currently frozen E187 protocol.**

E187 states:
- `current_authorized_owner_runs=0`;
- owner run not authorized;
- producing the missing raw ledger by execution was forbidden in E187.

Its future one-owner/one-run semantics activate only **after** an append-only revision supplies the exact parent ledger and an independent review re-authorizes the mechanism. The candidate run cannot be used to create its own prerequisite.

E190 likewise does not authorize a run.

Therefore R351 does not authorize a one-time target-free re-execution to recover the ledger.

### Read-only/static recovery

**Permitted in principle, but not presently realized.**

A future independent evidence-recovery task could remain within the frozen scientific protocol if it does one of the following without estimator execution:
- discovers a pre-existing immutable raw F86 namespaced op-log/receipt; or
- produces a proof-grade exact static derivation from pinned immutable source and exact flopscope billing semantics, yielding exact per-namespace/subtotal integers without using rounded unit displays.

E190 reports that its repository/artifact search found no pre-existing raw namespaced op-log, and it did not supply such a static exact component derivation.

So there is no currently available permitted recovery artifact that closes G2.

## 7. Final decision

**KEEP H185/E187 AT PROTOCOL NO-GO. DO NOT MARK HARDENING_READY.**

What changed since E191:
- E190 is now a live immutable branch;
- exact whole-parent total `558,473,140,719` is now persisted with provenance;
- the whole-total visibility/immutability concern is resolved.

What did not change:
- exact dense-parent denominator is absent;
- exact fixed/remainder subtotal is absent;
- exact same-ledger component reconciliation is absent;
- no raw F86 namespaced op-log is persisted;
- no exact static component-cost proof is persisted;
- no runtime recovery is authorized.

This is a procedural/evidence decision only. It is not a scientific rejection of H185 and is not an H185 authorization.

## 8. Execution accounting

- estimator/candidate run: **0**
- rerun/recovery execution: **0**
- downloads: **0**
- GitHub Actions triggered: **0**
- paid compute: **NO**
- private/holdout/full access: **NO**
- submission: **NO**
- R320 edit: **NO**
- control/queue edit: **NO**
- PR/main edit: **NO**
- R351 branch artifacts: exactly report + JSON receipt
