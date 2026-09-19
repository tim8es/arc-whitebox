# E128 OWNER/INTEGRATOR protocol

Idempotency key: ARC-E128-OWNER-INTEGRATOR-20260919

Role: administrative/scientific integration controller for experiment IDs E121-E127.

Canonical base at freeze:
- branch: research/bootstrap
- head: 29bee3f8d23fc620b77aaed414b1b7a928af4b83
- ledger: research/ledger.csv

## Non-negotiable admission rules

An E121-E127 result is not eligible for the canonical ledger unless all of the following exist and agree:
1. exactly one authoritative mechanism identity for that experiment ID;
2. a protocol frozen before the scientific run;
3. an immutable result receipt bound to protocol/implementation/run;
4. a concrete workflow run and job (or another repository-verifiable executable run record);
5. target-access scope explicitly states no benchmark/public/scorer/holdout/full target leakage unless that access was specifically authorized by the frozen protocol;
6. claimed metrics are present in the run artifact/log or are deterministic arithmetic derived from recorded metrics;
7. branch ancestry is compatible with the declared parent.

A branch name, prose result, commit message, or receipt without a run is not a scientific PASS/NO-GO.

## Collision policy

IDs E121-E127 are single-owner slots. If two non-identical mechanism branches claim the same ID:
- neither is integrated automatically;
- mark the ID COLLISION_QUARANTINE;
- compare protocol freeze time/ancestry and mechanism identity;
- preserve the earliest valid frozen owner as authoritative only when provenance is unambiguous;
- re-key every independent later mechanism before execution/integration;
- never combine metrics from colliding branches.

Same-ID pollution includes reusing one ID for a materially different mechanism, corpus, target, or acceptance gate after results are known.

## Target-leakage policy

Target-free means candidate construction, feature/state selection, tuning, rank/grid/threshold choice, stopping, rescue, and coefficient choice are independent of benchmark/public/scorer/holdout/full targets.

Exact references may be used only where the frozen protocol explicitly designates them as verification truth. A candidate that consumes the exact reference or target-derived boundary/state information is not target-free.

## PASS handling

For an authoritative PASS, E128 must write an exact independent-verifier action before any production/promotion run. The action must name:
- immutable owner head and receipt;
- independent reference or invariant;
- target-leakage checks;
- deterministic replay check;
- all-in FLOP categories;
- exact numerical admission thresholds;
- forbidden public/scorer/holdout/full/production actions.

PASS does not itself authorize production.

## NO-GO handling

For an authoritative NO-GO:
- integrate the measured blocker and reusable lesson;
- close the mechanism fingerprint against renaming/recycling;
- assign the next free ID to one genuinely non-overlapping hypothesis;
- freeze its mechanism-class distinction before code;
- do not rescue/tune/rerun the failed lane.

## Canonical ledger policy

research/ledger.csv is append/update-only through a dedicated integration commit/PR from this owner branch. E128 will not add speculative rows for unexecuted E121-E127 IDs.

At this freeze, live GitHub branch search found no branches claiming E121-E127. Therefore those IDs are reserved/unclaimed, not PASS, NO-GO, or DONE. No E121-E127 canonical ledger rows are added by this freeze.

## Current exact action

Wait for the first concrete E121-E127 owner branch. On detection:
1. freeze its head;
2. inspect protocol, implementation, receipt and Actions run;
3. collision-check all branches for that ID;
4. apply leakage/run-evidence gates;
5. integrate only if evidence-complete;
6. emit verifier action for PASS or reusable lesson + next non-overlapping hypothesis for NO-GO.
