# E189 ARC control update — H180 terminal provenance closure / H185 hardening gate

Recorded: 2026-09-22

Control key: `ARC-CONTROL-E189-H185-HARDENING-E187-E188-20260922`

Prior control head at intake:

`control/arc-deep-error-frontier-20260919@2137c7213bdaaff20f701dcdf52ae8ac1bb3d175`

Status: **E181/H180 TERMINAL NO-GO WITH DUPLICATE-OWNER PROVENANCE / E182 FORBIDDEN / E185 H185 PROTOCOL-ONLY / E186 LAUNCH REJECTED / E187 HARDENING ONLY / E188 INDEPENDENT REVIEW ONLY / H185 SCIENTIFIC OWNER-RUN BLOCKED**.

This is append-only control. It does not mutate `research/ledger.csv`, `research/bootstrap`, canonical history, scorer/submission/holdout/full state, or leaderboard state.

## E181 / H180 — terminal NO-GO; duplicate-owner provenance frozen

H180: aggregate symmetric-CP inherited-K3 carrier.

Two E181 owner branches and two physical owner executions exist. That violates the one-owner provenance rule. The second owner execution is not an admissible independent confirmation or rescue.

### First E181 owner

Branch current head:

`research/e181-h180-symmetric-cp-carrier-20260921@7832255730af2be573a342bdb7b44320f9e18531`

Frozen run head:

`147cb201a162d98c0a683a4e58b2d30209da6b0f`

Run/job/artifact:

- run `35641709985`;
- job `106472337192`;
- artifact `10659065918`, `e181-h180-symmetric-cp-carrier`;
- artifact SHA256 `757dd08001d4799728141ebc4387ac886839622687b2409f31f44108570b3999`.

Terminal receipt:

`research/E181_TERMINAL_RECEIPT.json@a07b6f679f67a9b982522b28123e0c22ad99a0e5`.

Scientific first failing gate:

- max D21 relative RMS `0.08845639298080632`;
- frozen threshold `0.015`;
- accuracy stage suppressed;
- terminal NO-GO.

The workflow wrapper later failed its manifest verification race, but the falsifier completed and the immutable artifact exists. No rerun was authorized.

### Duplicate clean-room E181 owner

Branch current head:

`research/e181-h180-symmetric-cp-carrier-cleanroom-20260921@42a85188ebf23f0d0626f81f52b39449150c22d2`

Frozen execution head:

`e28cc9bf3cbddc675be667ebbac6a1d98cb0dc0e`

Run/job/artifact:

- run `35642430938`;
- job `106474721114`;
- artifact `10658383129`, `e181-h180-target-free-run`;
- artifact SHA256 `8871c4fa0077dc73ffb7c442ae736e43c6958e9e1bd0d183f4c241291a87bc68`.

Committed duplicate-owner receipt:

`research/e181_artifacts/E181_RECEIPT.json@4fa4df934c6a255bfbafd1f8aa16b393ecbc7a6e`.

It also reports scientific NO-GO before accuracy:

- stage0 D21 RMS ratio `0.2626435881468867`;
- stage1 D21 RMS ratio `0.4169990347589253`;
- frozen D21 gate `0.015`;
- stage1 D3 RMS ratio `0.4488406625479034`;
- accuracy `NOT_RUN_BY_FROZEN_GATE`;
- terminal reason `G2_D21_RMS_GATE_FAILURE`.

The second execution is retained as provenance evidence of a duplicate-owner control violation, not as a second admissible owner run.

### H180 closure

H180 is terminal NO-GO.

Forbidden:

- any E181 rerun;
- any H180 rescue, rank/seed/projection/source-age variant or renamed continuation;
- using the duplicate clean-room run to legitimize a second owner;
- treating either run as a basis for E182 verification.

## E182 — do not create

E182 is **FORBIDDEN / CLOSED UNUSED**.

Do not create:

- an E182 branch;
- an E182 verifier receipt;
- an E182 workflow/run;
- an E182 candidate or hypothesis.

A verifier cannot repair duplicate-owner provenance by choosing one E181 execution.

## E185 / H185 — new exact trilinear-aggregation hypothesis, protocol-only

Branch:

`research/e185-trilinear-aggregation-frontier-20260922@10f5f0ab41da70b0661f44596f23f9e7f182ec11`

Protocol:

`research/E185_TRILINEAR_AGGREGATION_PROTOCOL.md@4d608cd5f292b04dff9c719e4990628b38d55872`

Mode remains:

**PROTOCOL / PRIMARY-SOURCE RESEARCH ONLY — NO CODE, NO SCIENTIFIC RUN.**

H185 is scientifically distinct from H180.

Frozen hypothesis class:

**keep the full V29 D21/K3 information and cross-source state unchanged, but replace the algebraic schedule of its dense matrix products with one exact trilinear-aggregation compiler whose all-in transformed dense-kernel bundle cost can satisfy the frozen cost gate.**

H185 does not authorize:

- CP/Tucker/TT/low-rank K3 replacement;
- source dropping;
- old-source-only compression;
- approximate matrix multiplication;
- target fitting;
- rank/base-case/coefficient sweep;
- scorer/submission/holdout/full/leaderboard access.

E185 remains protocol-only. No owner mechanism/scientific run is authorized by E185 itself.

## E186 — independent review rejects current launch

Branch:

`review/e186-e185-independent-review-20260922@89b514fff8c1e7e48a8bb3fc8e542984a84ba045`

Review:

`research/E186_E185_INDEPENDENT_REVIEW.md@6b5c16d0be80eea46357a8bfe12fad60d8f14bb2`

Decision:

**REJECT CURRENT FUTURE LAUNCH.**

This does not reject H185 as a hypothesis. It rejects the current protocol as one-run-ready.

E186 found H185 distinct from H180 and found its primary-source basis and planning cost arithmetic admissible, but blocked launch because the protocol does not yet freeze enough implementation, coverage, production-dtype, evidence and verifier detail.

The E186 hardening requirements G0-G12 are authoritative input to E187.

E186 is consumed as review evidence. It does not authorize a run.

## E187 — H185 hardening only; no scientific execution

Allocate:

**E187 — machine-readable H185 launch hardening.**

Recommended branch:

`research/e187-h185-launch-hardening-20260922`

E187 is a protocol/evidence-engineering lane, not a scientific owner run.

E187 must freeze, in machine-readable form where applicable, all E186 G0-G12 requirements without changing the H185 scientific hypothesis.

### Mandatory E187 deliverables

1. **Exact implementation identity**
   - exact TA/Pan decomposition or generated bilinear coefficient tables;
   - coefficient-table hashes;
   - base cases;
   - recursion/blocking;
   - rectangular adaptation;
   - padding;
   - fallback policy.

2. **Single machine-readable parent cost ledger**
   - raw flopscope count;
   - exact namespace totals;
   - event/call semantics;
   - warm/steady-state convention;
   - SHA256;
   - no mixing rounded `260.1u` headline with the `260.0u` grouped model.

3. **Full product/operation coverage map**
   - every production hot-path event contributing to the dense K3 bill;
   - each event labeled transformed / unchanged / fixed fallback;
   - mapped parent total must reconcile exactly to the machine-readable ledger;
   - no "selected products" subset may stand in for the full bill used in the projected cost claim.

4. **Immutable input/output evidence schema**
   - raw input matrices for every bundle case;
   - dtype/shape/nbytes/seed/provenance;
   - raw-array and file SHA256;
   - parent/candidate outputs;
   - complete manifest.

5. **Exact-small algebra gate**
   - rational/integer fixture;
   - exact decomposition identity;
   - retained equality evidence/hash.

6. **Production float64 stability gate**
   - product-family absolute and relative norms;
   - D3 and off-diagonal D21 norms;
   - explicit zero/near-zero denominator handling;
   - frozen numerical thresholds.

7. **Production float32 stability gate**
   - exact metric and thresholds for every transformed product family, D3 and off-diagonal D21;
   - thresholds justified before any owner result from pinned parent/error evidence;
   - no post-result tolerance selection.

8. **All-in legality/accounting gate**
   - additions/subtractions;
   - coefficient multiplies;
   - copies/temporary formation where billed;
   - padding/unpadding;
   - fallback products;
   - recursive/base-case calls;
   - no unmetered alternative path.

9. **Hard runtime gate**
   - pinned parent residual-time baseline;
   - exact bundle-to-production scaling formula;
   - allowed integration overhead;
   - deterministic terminal threshold;
   - verifier-recomputable PASS/FAIL.

10. **Deterministic replay contract**
    - same bundle replay inside one future authorized workflow;
    - bitwise-identical candidate outputs, ledgers and manifest hashes.

11. **One-run arm and terminal semantics**
    - branch/head/protocol/implementation/coefficient-table identities;
    - frozen seed;
    - `authorized_owner_runs = 1`;
    - exact failure semantics;
    - no rerun/rescue/sweep/base-case or seed substitution.

12. **Independent verifier contract and target firewall**
    - verifier recomputation inputs and outputs;
    - mechanism/protocol/integration-readiness verdicts separated;
    - source/import/access audit;
    - no benchmark target means, scorer, holdout/full, submission endpoint, or leaderboard result data used for tuning.

### E187 status rule

E187 may return **HARDENING_READY** only if every mandatory item above is frozen and internally reconciled.

Any missing or ambiguous item yields **HARDENING_NOT_READY**.

E187 must not execute the H185 scientific/mechanism owner falsifier.

No target-bearing run and no public benchmark run.

## E188 — sole independent review of E187 hardening

Allocate:

**E188 — independent read-only review of E187 H185 launch hardening.**

Recommended branch:

`review/e188-e187-h185-hardening-20260922`

E188 is blocked until a complete immutable E187 hardening tuple exists.

E188 may inspect/recompute only. It must not implement or run H185.

E188 must independently verify:

1. H185 identity unchanged from E185;
2. no H180/E181 rescue or duplicate-owner continuation;
3. exact implementation/coefficient identity frozen;
4. machine-readable parent cost ledger internally reconciles;
5. full product map covers the bill used in the cost projection;
6. float64 gate is deterministic and verifier-recomputable;
7. float32/stability gate is frozen and justified pre-run;
8. all-in FLOP namespace accounting is complete;
9. runtime projection is a hard deterministic formula;
10. immutable input/output evidence schema is sufficient for independent recomputation;
11. exact-small algebra fixture is sufficient;
12. replay/one-run arm/terminal semantics are unambiguous;
13. target/scorer/submission/holdout/full/leaderboard firewall is complete.

E188 verdict must be one of:

- `GO_H185_LAUNCH_HARDENING`;
- `NO_GO_H185_LAUNCH_HARDENING`;
- `UNEVALUATED_H185_LAUNCH_HARDENING`.

No nested verifier.

## H185 scientific owner-run gate

**Scientific owner-run H185 is forbidden until both conditions exist durably:**

1. E187 = `HARDENING_READY`;
2. E188 = `GO_H185_LAUNCH_HARDENING`.

Until both are present:

- no H185 implementation owner workflow may be armed;
- no target-free H185 mechanism falsifier may run;
- no scientific owner branch may be launched from the protocol.

Even after both are positive, this E189 receipt does **not** itself execute or arm the scientific owner run. A subsequent explicit control allocation must bind the frozen E187/E188 tuple to exactly one owner identity/run.

No automatic promotion by timer.

## External and terminal firewalls

Remain forbidden:

- H180/E181 rescue or rerun;
- E182 creation;
- E175/E176 rescue;
- scorer;
- external submission;
- holdout/full;
- leaderboard mutation/update;
- target fitting;
- scientific sweeps;
- canonical merge;
- `research/bootstrap` mutation;
- `research/ledger.csv` mutation.

## Evidence-driven trigger

Current active control path:

`E187 hardening tuple -> E188 independent review -> control decision`.

If E187 is not ready, stop.

If E188 is NO-GO or UNEVALUATED, H185 remains blocked.

If E187 is HARDENING_READY and E188 is GO, report H185 launch readiness and wait for a separate explicit owner-run control allocation.

Do not advance by timer.
