# ARC control update — E162 H160 Angular Gauge Only / E163 verifier

Recorded: 2026-09-21

Control key: `ARC-CONTROL-E162-H160-AGO-E163-20260921`

Prior control receipt:

`control/arc-deep-error-frontier-20260919@eff0d3a1fe959f2bdbbceead72ae318e7c059244`

Status: **ACTIVE OWNER ALLOCATION / APPEND-ONLY CONTROL / FAIL-CLOSED**.

This receipt records E160's supported H160 class, closes the superseded E159/E161 path, and allocates E162/E163. It does not reopen E154/E157 and does not authorize public/public-mini targets, scorer/holdout/full, sweeps, rescue, reruns, canonical mutation, ledger mutation, merge, or status-only promotion.

## Immutable closed state

The following remain closed:

- **E147** — terminal scientific NO-GO;
- **E148** — terminal scientific NO-GO;
- **E150** — terminal theory NO-GO;
- **E152** — terminal theory NO-GO;
- **E151** — sealed FAIL-CLOSED before science;
- **E154** — terminal K4 scientific NO-GO;
- **E157** — terminal AIK4-1 scientific NO-GO.

No E154/E157 K4 rescue, renamed continuation, recurrent K4, one-birth K4 repair, threshold/seed/parent substitution, or rerun is admissible.

## E159 — superseded terminal NO-GO

The prior E159 owner physically executed before this control update and is already terminal:

- branch: `research/e159-published-angular-gauge-20260921@c9637699f1faf9e04150168555d17562f6d916f3`;
- protocol commit/blob: `1551f71ca38f25d802da6dd3aed7ee0e49abb327 / 4d0c44607e72e34378346b02a3ccc4559d21a792`;
- implementation commit/blob: `72c8b3b01f9b5631663d3086d2c8f2ede5a74c8c / a8b00324c4c961ed0ab97d25425da98b094fad03`;
- launch/executed head: `dd8fc9df05bf27ca7e5cfc9d78bf0f58e1dfc089`;
- run/job/attempt: `35602168233 / 106340610062 / 1`;
- artifact: `10638919116`, `e159-published-angular`;
- artifact SHA256: `518b8ba466fda3f563a2315b4d40621d50e4197c072b6564d7e227de2f5cf167`;
- decision: `E159_TERMINAL_NO_GO_PUBLISHED_ANGULAR_GAUGE`.

The sole E159 run hit non-finite values in its reconstructed recurrent-K4 diagnostic path before mandatory immutable scientific metrics could be frozen. E159's one-run policy therefore closes it. No rerun/rescue.

This failure does **not** falsify H160, because H160 explicitly removes all K4 state/arithmetic and is supported independently by E160's source attribution.

E161 is closed unused as the obsolete E159 verifier reservation. Do not create or reuse E161.

## E160 — support-only source attribution

Support branch:

`research/e160-primary-source-angular-support-20260921@f425e18feab11ebcb3e8a908e713f36677f84e09`

Support artifact:

`research/E160_PRIMARY_SOURCE_SUPPORT.md`

Status:

**PRIMARY-SOURCE SUPPORT ONLY / NO OWNER PROTOCOL / NO EXECUTION AUTHORIZED.**

E160 identifies one distinct supported hypothesis class:

### H160 — AGO: Angular Gauge Only

The candidate delta is exactly the low-order angular/radial K1/K2 gauge:

[
m_A = m_G / a_1,
]

[
C_A = C_G - (a_1^{-2}-1)m_Gm_G^T,
]

followed by the same frozen parent closure and final radial mean readout:

[
m_G^{out}=a_1m_A^{out}.
]

H160 contains:

- **no K4 state**;
- no D4/D22 birth;
- no scalar `c4`;
- no recurrent K4;
- no K4-derived correction at any later layer;
- no refit/rerank of parent K3/D21 state.

E160's source audit records that the pinned public K2 ablation improved with scalar K4 completely disabled, while enabling recurrent scalar K4 on the angular K2 arm slightly worsened the published aggregate raw MSE. This is support for testing the gauge as a distinct mechanism, not permission to use benchmark targets in E162.

E160 remains support-only. It may be cited as provenance/derivation but cannot execute or promote H160.

## Namespace checkpoint

Fresh branch search at allocation:

- E162: no branch observed;
- E163: no branch observed.

Fresh Actions search at allocation:

- no E162 run;
- no E163 run.

Both identities are collision-free at allocation time.

## E162 — sole active scientific owner

Allocate:

**E162 — H160 Angular Gauge Only (AGO), clean-room, target-free, no K4.**

E162 is the only active scientific owner under this receipt.

### Mechanism boundary

E162 must test exactly one frozen gauge-only candidate against one frozen parent.

Candidate and parent must have identical non-K4 closure arithmetic. The only candidate delta may be:

1. at one owner-frozen first Gaussian activation state, convert K1/K2 by the exact angular gauge:
   - `m_A=m_G/a1`;
   - `C_A=C_G-(a1^-2-1)m_G m_G^T`;
2. continue the identical frozen parent closure from that angular K1/K2 state;
3. convert the final angular mean back by `m_G_out=a1*m_A_out`.

Forbidden inside E162:

- any K4 tensor/factor/state;
- D4 or D22;
- scalar `c4`;
- K4 recurrence;
- K4-derived Wick correction;
- E154/E157 candidate code/artifact reuse;
- parent K3/D21 refit, rerank, correction, or candidate-specific retuning;
- recurrent-K4 diagnostic path from E159.

### Mandatory protocol-first freeze

Before implementation/workflow, E162's first scientific owner commit must freeze:

1. exact clean parent commit/blob and complete parent mechanism;
2. exact E160 support commit used as source attribution;
3. exact location of the one-time K1/K2 gauge transform and final radial readout;
4. explicit static proof/audit that no K4/D4/D22/c4/recurrent-K4 arithmetic exists in parent or candidate path claimed by H160, or else exactly identify any parent fourth-order state and reject that parent before execution;
5. deterministic synthetic/analytic target-free fixtures and seeds;
6. independent exact-small/analytic reference capable of falsifying the gauge-only scientific claim;
7. exact gauge identity/parity gates with frozen numerical thresholds;
8. one frozen target-free scientific improvement/error gate against the exact/analytic reference;
9. a computable target-free residual/error certificate appropriate to the owner claim, with frozen numerical threshold;
10. complete all-in parent+gauge production cost including parent arithmetic, gauge outer product/state conversion, final radial readout, diagnostics/helpers/RNG/normalization/materialization, certificate/reference/setup and every charged operation class;
11. combined production cost `<=0.135 * 2^41` FLOPs;
12. deterministic replay;
13. target/oracle/public/public-mini/scorer/holdout/full/submission firewall;
14. terminal kill rule;
15. exactly one physical target-free owner run;
16. no sweep, tuning, rescue, rerun, retry, seed/fixture/threshold/parent/source/mechanism substitution or post-result repair.

The public benchmark numbers cited by E160 are hypothesis provenance only. They must not become E162 fitting data, thresholds, fixtures, reference outputs, or scientific evidence.

### One-run authorization

After a valid protocol-first freeze, E162 may implement the minimum clean-room parent/candidate/reference/tests/falsifier/workflow and execute **exactly one** target-free physical scientific run.

Any failed or unevaluable mandatory gate, including infrastructure failure before science, consumes the one-run authorization and closes E162 unless a later explicit control update says otherwise.

No second run.

## E163 — sole independent verifier

E163 is reserved as exactly one independent review-only verifier for E162.

Do not create or execute E163 before a complete admissible E162 owner tuple exists.

After the sole E162 physical run, freeze:

- E162 branch/experiment ID;
- protocol SHA/blob;
- E160 support provenance;
- parent commit/blob;
- candidate/reference/test/falsifier/workflow SHAs/blobs;
- executed head;
- run/job/attempt;
- artifact ID/name/SHA256;
- immutable owner result/terminal receipt SHA;
- no-K4 static/runtime evidence;
- gauge identity/parity metrics;
- target-free scientific/certificate metrics;
- complete all-in parent+gauge cost;
- deterministic replay;
- target/public firewall evidence.

Only if that tuple is complete and survives all owner gates may E163 execute one independent verification.

E163 must independently verify/recompute:

1. protocol-first ancestry and collision-free identity;
2. E160 source/support provenance without treating public benchmark targets as owner evidence;
3. exact H160 K1/K2 gauge algebra and final radial readout;
4. explicit absence of K4/D4/D22/c4/recurrent-K4 and E154/E157 rescue;
5. exact-small/analytic reference and scientific gate;
6. target-free residual/error certificate;
7. complete parent+gauge all-in cost;
8. deterministic replay;
9. zero public/public-mini target/scorer/holdout/full/submission access;
10. frozen run/artifact provenance and no post-result changes.

E163 may inspect/recompute frozen evidence only. It may not modify, regenerate, rerun, tune, rescue, substitute, repair, or publicly validate E162.

Exactly one verifier execution/receipt. No nested or second verifier.

Premature E163 activity fails closed.

## Hard rejection rules

Reject and fail closed:

- any E154/E157 rescue or renamed K4 continuation;
- any K4 state/correction inside H160/E162;
- E159 recurrent-K4 diagnostic reuse as a candidate path;
- public/public-mini benchmark target scientific access;
- benchmark-target scoring/evaluation as an owner gate;
- official scorer, holdout/full or submission access;
- target fitting;
- rank/order/seed/fixture/threshold/basis/certificate/parent/source/mechanism sweeps;
- owner rerun/retry or post-result repair;
- duplicate/colliding experiment IDs;
- speculative status or ledger rows;
- mutation of `research/bootstrap`;
- mutation of `research/ledger.csv`;
- canonical merge/integration.

## Single next gate

Wait for one collision-free **protocol-first E162 H160 Angular Gauge Only** owner freeze with an explicitly K4-free parent/candidate path.

E160 remains support-only.

After one complete admissible E162 target-free physical result, dispatch exactly one independent verifier under **E163**.
