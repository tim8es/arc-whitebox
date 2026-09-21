# E193 ARC control update — H185 raw-FLOP recovery gate / E190-E191 / E192 orthogonal research

Recorded: 2026-09-22

Control key: `ARC-CONTROL-E193-H185-RAW-FLOP-RECOVERY-E190-E191-20260922`

Prior control receipt:

`control/arc-deep-error-frontier-20260919@62def574d87394887a5f7e943374202a2ac2dbde`

Status: **E185 H185 PROTOCOL-ONLY / E187 PROTOCOL NO-GO / E188 REJECT / E190 RECOVERY EVIDENCE / E191 RESERVED INDEPENDENT REVIEW / E192 ORTHOGONAL RESEARCH / H185 OWNER-RUN BLOCKED / APPEND-ONLY CONTROL**.

This receipt is append-only. It does not rewrite E185/E187/E188, does not rehabilitate H180/E181, does not create E182, and does not mutate `research/ledger.csv`, `research/bootstrap`, canonical history, submission/scorer/holdout/full state, or leaderboard state.

## E185 / H185 — remains protocol-only

Branch:

`research/e185-trilinear-aggregation-frontier-20260922@10f5f0ab41da70b0661f44596f23f9e7f182ec11`

Protocol:

`research/E185_TRILINEAR_AGGREGATION_PROTOCOL.md@4d608cd5f292b04dff9c719e4990628b38d55872`

H185 remains unchanged:

**preserve the full V29 estimator state and D21/K3 arithmetic; replace only dense bilinear matrix-product schedules by an exact trilinear-aggregation algorithm.**

Status remains **PROTOCOL-ONLY**.

No H185 mechanism/scientific owner-run is authorized by E185 or this E193 receipt.

## E187 — protocol NO-GO on exact raw integer FLOP evidence

Branch:

`research/e187-h185-protocol-hardening-20260922@06fbb08fb9ece3b5b3d8da7b60fee331030a044f`

Protocol revision:

`research/E187_H185_PROTOCOL_REVISION.md@d623a9348518c0afe2869fc89f44a746960e81f5`

Machine-readable companions:

- `research/e187/E187_PARENT_LEDGER.json@33699fbfa47e23ffef99b6a99e064aa130100671`;
- `research/e187/E187_H185_PROTOCOL_LOCK.json@215187db7fb4a3ba391a1229e48ce6a482bebd97`.

E187 froze the implementation identity, coverage rules, float64/float32 gates, all-in accounting contract, runtime formula, replay, evidence manifest and verifier contract, but its own authoritative decision is:

**PROTOCOL NO-GO / OWNER RUN NOT AUTHORIZED.**

Blocking gate:

`G2_EXACT_RAW_PARENT_LEDGER`.

The pinned published F86 source exposes source-resolution grouped values:

- dense K3: `222.44u`;
- fixed: `37.62u`;
- grouped total: `260.06u`;
- headline: `260.1u`.

But it does **not** expose the exact raw integer flopscope count from which those unit values were rounded.

E187 explicitly records:

`exact_raw_flopscope_integer_available_in_published_log = false`

and

`exact_raw_parent_ledger_gate = FAIL`.

The rounded/source-resolution ledger is planning evidence only. It cannot be promoted into the exact raw-integer evidence required for an irreversible H185 owner run.

## E188 — REJECT owner-run; frozen review is not retroactively upgraded

Branch:

`review/e188-e187-independent-review-20260922@9fdaafb8254512ee5bc68b11529408cfeb4d8008`

Review:

`research/E188_E187_INDEPENDENT_REVIEW.md@20985b4c7144a14f0713037ca1827c3ad0e59e1f`

Decision:

**REJECT. DO NOT LAUNCH THE OWNER RUN.**

E188 could not independently establish the hardened E187 launch basis from the immutable evidence available to that review. Its review therefore fails closed.

The later-visible E187 branch/artifacts do not retroactively change the frozen E188 verdict. E188 is consumed and must not be edited/reused to authorize H185.

The remaining exact-raw-ledger blocker is independently confirmed by E187 itself, so a new recovery/evidence cycle is required.

## E190 — recovery evidence only

Allocate:

**E190 — exact raw parent FLOP evidence recovery for the H185 launch gate.**

Recommended identity:

`ARC-E190-H185-EXACT-RAW-PARENT-FLOP-RECOVERY-20260922`

Recommended branch:

`research/e190-h185-raw-flop-recovery-20260922`

E190 is **not** an H185 scientific owner and must not execute the H185 candidate.

Its sole purpose is to recover and freeze the exact parent-side evidence missing from E187 G2 and make the complete E187 hardening tuple independently auditable.

### E190 permitted work

E190 may, in this order:

1. exhaust primary/source artifacts for an already-existing exact raw integer flopscope ledger;
2. if no exact raw integer artifact exists, perform at most one deterministic **parent-only, target-free cost-accounting reproduction** of the pinned V29/F86 accounting path solely to recover exact raw integer FLOP counts;
3. freeze all provenance needed to show that the recovered count has the same estimator/source/namespace/event semantics as the E187 parent ledger;
4. reconcile exact integers to the published `222.44u / 37.62u / 260.06u` source-resolution values;
5. produce one immutable machine-readable recovery ledger and one append-only receipt.

A parent-only cost reproduction under E190 is administrative/evidence recovery, not an H185 candidate run. It must not load benchmark target/reference means and must not execute TA/H185 candidate arithmetic.

### Mandatory E190 evidence

E190 must freeze:

- source repository/commit/path/blob identities;
- exact instrumentation/flopscope implementation identity;
- exact environment/dependency identity if reproduction is required;
- exact event/namespace semantics;
- exact warm/steady-state/call selection matching the pinned F86 interpretation;
- exact raw integer FLOP counts for total, dense K3, fixed remainder and every required namespace/event used by the H185 coverage map;
- integer-to-`u` conversion with `u = 2*1024^3`;
- deterministic reconciliation to the published rounded/source-resolution values;
- raw log file + SHA256;
- machine-readable ledger + SHA256;
- manifest + SHA256;
- evidence of zero H185 candidate execution;
- evidence of zero target/scorer/submission/holdout/full/leaderboard access.

If exact integer counts cannot be recovered or reproduced under identical accounting semantics, E190 returns terminal **RECOVERY_NO_GO**. Do not synthesize integers from rounded decimal values.

No rerun to obtain a more favorable ledger. If one reproduction is required, exactly one physical parent-only recovery workflow is permitted.

E190 does not authorize H185 even if recovery succeeds.

## E191 — sole independent review of E190 + E187

Allocate:

**E191 — independent read-only review of the recovered raw-FLOP evidence and the complete H185 hardening tuple.**

Recommended identity:

`ARC-E191-E190-H185-RECOVERY-INDEPENDENT-REVIEW-20260922`

Recommended branch:

`review/e191-e190-h185-recovery-20260922`

E191 is blocked until a complete immutable E190 recovery tuple exists.

E191 may inspect/recompute only. It must not run or repair H185 and must not regenerate missing owner evidence.

E191 must independently verify:

1. E185/H185 hypothesis identity is unchanged;
2. E187 protocol/lock/ledger identities are exact and immutable;
3. E190 source/instrumentation provenance matches the pinned parent accounting path;
4. recovered FLOP values are actual raw integers, not reverse-engineered rounded values;
5. raw log hashes and machine-readable ledger hashes match;
6. exact integer totals reconcile arithmetically to namespace/event subtotals;
7. integer-to-`u` conversion independently reproduces the published source-resolution values within their declared rounding semantics;
8. the full E187 product coverage map reconciles to the recovered exact dense parent denominator;
9. the E187 projected cost formulas are recomputed using exact raw integer evidence;
10. E187 float64/float32, runtime, exact-small, replay, immutable-manifest and one-run contracts remain frozen and internally coherent;
11. no H180/E181 rescue or E182 activity occurred;
12. no H185 candidate/scientific owner run occurred;
13. scorer/submission/holdout/full/leaderboard and target-data firewalls remained closed.

E191 verdict must be one of:

- `GO_H185_RECOVERY_EVIDENCE`;
- `NO_GO_H185_RECOVERY_EVIDENCE`;
- `UNEVALUATED_H185_RECOVERY_EVIDENCE`.

E191 is review-only. No nested verifier.

## H185 owner-run remains blocked after E190/E191

H185 scientific/mechanism owner-run is **forbidden now**.

It remains forbidden until all of the following exist durably:

1. complete E190 recovery evidence;
2. E191 verdict `GO_H185_RECOVERY_EVIDENCE`;
3. a **new explicit control GO** allocating exactly one H185 owner identity/run.

E190 success + E191 GO are necessary but not sufficient to launch.

No automatic owner-run arm, branch, workflow or execution after E191.

## E192 — separate orthogonal research

Allocate:

**E192 — orthogonal research lane, separate from H185 recovery and authorization.**

Recommended branch:

`research/e192-orthogonal-frontier-20260922`

E192 is research-only at this control stage.

Its purpose is to investigate a scientifically distinct frontier that does **not** depend on:

- H180/E181 CP-carrier rescue;
- E182;
- H185 trilinear-aggregation implementation;
- E190 raw-FLOP recovery succeeding;
- changing H185 thresholds/base cases/coefficient tables.

E192 must remain orthogonal to the E190/E191 authorization chain. Its output may be a primary-source research memo and a protocol-worthy hypothesis, but it cannot satisfy E190, replace E191, or authorize H185.

E192 may compare mechanism classes and derive algebraic/cost falsifiers from primary sources, but under this receipt it must not:

- execute a scientific candidate;
- run target-bearing public/public-mini benchmarks;
- access scorer/holdout/full;
- submit;
- mutate leaderboard;
- rescue H180/E181;
- create E182;
- mutate canonical/ledger.

If E192 identifies a promising new class, stop at a new-hypothesis/protocol recommendation. A separate control allocation is required before any scientific owner run.

## Duplicate/terminal firewall

Reject and alert on:

- any E182 branch/receipt/workflow/run;
- any new E181/H180 owner, rescue, rerun, rank/seed/projection/source-age variant or renamed continuation;
- any H185 owner/candidate workflow before a later explicit control GO;
- any E188 re-review used as authorization;
- E190 running the H185 candidate;
- more than one E190 parent-only recovery execution;
- E191 scientific execution or evidence repair;
- E192 being used to bypass E190/E191;
- scientific sweeps;
- scorer;
- submission;
- holdout/full;
- leaderboard mutation;
- canonical merge;
- `research/bootstrap` mutation;
- `research/ledger.csv` mutation.

## Evidence-driven trigger graph

H185 authorization path:

`E190 recovery evidence -> E191 independent review -> NEW CONTROL DECISION`.

No H185 owner run exists in this graph.

E192 proceeds separately as research:

`E192 orthogonal research memo -> separate future control decision if warranted`.

No progression by timer.

If E190 fails, H185 remains blocked.

If E191 is NO-GO or UNEVALUATED, H185 remains blocked.

If E191 is GO, report readiness for a new control decision only; do not launch H185.

## External firewall

Remain **CLOSED**:

- submission;
- official scorer;
- holdout/full;
- leaderboard mutation/update.

No E190/E191/E192 result opens these gates.

## Exact next actions

1. Create one E190 recovery-evidence lane for the missing exact raw integer parent FLOP evidence; prefer existing primary evidence, otherwise permit at most one parent-only target-free accounting reproduction.
2. After and only after immutable E190 completion, dispatch E191 exactly once as read-only independent review.
3. Permit E192 orthogonal research in parallel, research-only and separate from H185 authorization.
4. Do not create E182.
5. Do not repeat/rescue H180/E181.
6. Do not arm or execute H185 until E190/E191 are positive **and** a later explicit control GO exists.
