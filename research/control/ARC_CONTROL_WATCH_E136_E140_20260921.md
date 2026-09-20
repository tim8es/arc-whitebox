# ARC control update — watch E136/E137/E138/E139/E140

Recorded: 2026-09-21 02:38 +03

Control key: `ARC-CONTROL-WATCH-E136-E140-20260921`

Status: **FAIL-CLOSED / APPEND-ONLY CONTROL**.

This receipt supersedes the prior E133–E135 watch. It does not rewrite earlier receipts and does not authorize canonical/ledger mutation, rescue, rerun, tuning, public/public-mini/scorer/holdout/full access, merge, or status-only scientific promotion.

## Closed lanes

The following identities are closed and must not be rescued, rerun, renamed, reinterpreted, or used for speculative ledger/status promotion:

- E122;
- E124;
- E127;
- E132;
- E134.

Any new mechanism that materially repairs one of these closed lanes must be re-keyed only if a later explicit control decision permits it; this receipt does not.

## E136 — FAIL CLOSED under current control admission

Observed branch:

`research/e136-public-k3-reproduction`

Observed authoritative completed reproduction evidence:

- head: `830bb11a27cc3a3d9c1e42fb4c6f6fa2004fffe4`;
- run/job: `35540584740 / 106157369520`;
- artifact: `10614453799`;
- artifact SHA256: `103b5d4b97fb6584a45805877414545ea05705693f573f816d1ef76b8ce7b658`.

Its immutable receipt explicitly classifies the lane as `PUBLIC_BASELINE_REPRODUCED_SMOKE` and records access to the official public `v2-phase2/mini` split. It is therefore **not target-free evidence** under this control regime.

The branch also has multiple workflow executions and a newer follow-up workflow at head `dff3dd65e9d2210e02418cca99e05556f6bf2c75`, run `35544406064`, observed in progress at this checkpoint. The lane does not satisfy the new admission rule of one target-free scientific receipt with protocol-first owner ancestry.

Control disposition:

**E136 FAIL CLOSED FOR SCIENTIFIC PROMOTION.**

The public reproduction may remain historical provenance/baseline evidence, but it cannot produce an admissible scientific GO, ledger row, or verifier handoff under this watch. Do not dispatch a verifier for E136. Do not authorize further E136 follow-up, rescue, rerun, or status promotion. Completion of already-running `35544406064` does not cure the admission failure.

## E137 — TERMINAL FAIL CLOSED; no rerun

Observed branch:

`research/e137-mit-v25-v29-improvement-scout-20260921`

The target-free H137 Stage-A protocol was frozen before its implementation run:

- scout protocol: `77c13ded84bb8b5e6bd4a092cd2021b3732a21fe`;
- Stage-A protocol: `ce5a217eca58e8608d824c7f5ef82dab6097e98a`;
- executed workflow head: `eb21ee6bb5838255293d1b8a7ae48b1aa7b20569`;
- run/job: `35544178486 / 106167052999`;
- run conclusion: failure;
- scientific falsifier started: false;
- failure: `ModuleNotFoundError: No module named 'methods'`;
- artifact: none.

The frozen protocol says any failed or unevaluable gate is terminal NO-GO with no rerun/rescue. Because the falsifier never imported, certificate/scientific metrics and full candidate cost result are unevaluated.

Control disposition:

**E137 TERMINAL NO-GO / FAIL CLOSED.**

No rerun, import-path repair, alternate sketch, rescue, second Stage-A, scientific promotion, ledger row, or verifier is authorized. A verifier cannot validate missing physical scientific evidence.

## New namespaces E138/E139/E140

Live branch search at this checkpoint:

- E138: no branch observed;
- E139: no branch observed;
- E140: no branch observed.

These are the only clean new owner namespaces admitted by this receipt.

## Mandatory admission contract

A new E138/E139/E140 scientific lane is admissible only if all conditions are frozen **before implementation/workflow execution**:

1. **protocol-first ancestry** — first scientific owner commit is protocol-only and descends from the declared parent;
2. collision-free experiment identity;
3. exact mechanism and provenance;
4. deterministic synthetic/target-free corpus and seeds;
5. independent exact-small falsification gate where an exact-small reference is available/required by the claim;
6. **target-free residual/error certificate** that is computable from frozen evidence, with a numerical pass/fail threshold;
7. **complete all-in cost** including estimator operations, diagnostics, helper transforms, RNG, normalization/materialization, certificate computation, setup and any other protocol-charged work;
8. target/oracle/public/scorer/holdout/full firewall;
9. exactly one authorized physical owner scientific run, no tuning/no rescue/no post-result threshold or mechanism changes;
10. immutable target-free result receipt and terminal kill rule.

Public/public-mini measurements, leaderboard values, final targets, scorer/holdout/full access, status prose, branch reservations, protocol-only commits, workflow definitions, issues/PRs/comments, or accepted commands are not admissible scientific result evidence.

## One-verifier rule

For the first qualifying physical owner run on each admissible E138/E139/E140 lane:

1. freeze owner ID/branch, protocol SHA, executed head, run/job, artifact ID/name/digest and immutable owner receipt SHA;
2. verify protocol-first ancestry, target-free receipt, certificate completeness and full-cost completeness;
3. if any required element is missing/incomplete, append **FAIL-CLOSED** control receipt and stop — no repair/rescue/verifier;
4. otherwise designate **exactly one** fresh collision-free independent review-only verifier;
5. verifier may inspect/recompute only the frozen owner evidence and must not modify, regenerate, rerun, tune, rescue or substitute the candidate;
6. append one owner→verifier handoff receipt;
7. no second/nested verifier.

## Ledger/status firewall

No canonical or `research/ledger.csv` mutation is authorized by this receipt.

No speculative ledger row or scientific status may be derived from:

- branch existence;
- protocol text;
- accepted command;
- issue/PR/comment;
- workflow creation;
- in-progress run;
- public reproduction;
- incomplete/failed execution;
- owner prose without physical target-free receipt;
- verifier reservation without physical verifier evidence.

## Single next gate

Watch E136/E137 for control drift only; both are fail-closed under the current evidence.

For new science, wait for the first collision-free, protocol-first, target-free physical owner run on **E138/E139/E140** with a computable residual certificate and complete all-in cost. Then apply the one-verifier rule above.
