# ARC control update — E127 closed, E130 forensic-only, watch E132/E133

Recorded: 2026-09-20 19:10 +03

Control key: `ARC-CONTROL-E127-E130-CLOSE-WATCH-E132-E133-20260920`

Status: **FAIL-CLOSED / APPEND-ONLY CONTROL**.

This receipt supersedes the previous E127/E130 watch state. It does not rewrite prior receipts and does not authorize canonical/ledger mutation, rescue, rerun, tuning, public/public-mini/scorer/holdout/full access, merge, or status-only scientific promotion.

Observed canonical remains `research/bootstrap@7a0034088ebbffbd74b441e1797c272e9d33cbff`; observed `research/ledger.csv` blob remains `040e52efe01efd7280180b7e2d72901b4c2f0532`. These are evidence only, not authorization to mutate either.

## E127 — CLOSED / TERMINAL NO-GO

Scientific branch:

`research/e127-sparse-hypergraph-certified-tail-20260920`

Physical evidence:

- protocol: `621bc2371d175e82d1d14e023e12e8f00aa76a5e`;
- executed head: `1afc34432d5213e31d0f3cc9a10ffab46f29a877`;
- run: `35509275149`;
- job: `106074241954`;
- artifact: `10604588862`;
- artifact SHA256: `379a34f9aed8f7d4440e720a88d70183002e47ee9a03205e7b6b13f81a813a85`;
- immutable terminal receipt head: `c48cb55794027f505fd1aa52ce957177684af0ac`.

Terminal blockers are preserved exactly:

- minimum certified full truncation order across the frozen corpus is adaptive order 6–8;
- minimum sparse certificate RMS is `1.8247726965068751`;
- raw RMS limit is `1.374772708486752e-4`;
- even the easiest certificate is `13273.268266399105x` over the RMS limit;
- sparse candidate pooled MSE is `0.00039423726348519186`, `20859.114470115972x` the raw MSE target;
- optimistic necessary retained non-singletons are 57–247 while the homologous production pair-cost cap is 47;
- production full-order costs fail catastrophically.

Verdict: **TERMINAL NO-GO / NO RESCUE**.

Prior control also recorded that this scientific E127 branch violated an earlier E127 verifier reservation. That identity violation remains immutable control evidence; it does not change the terminal scientific outcome and cannot be used to authorize a rerun, rename, verifier chain, or status promotion.

## E130 — FORENSIC SIGNAL ONLY / COMPLETE RECIPE UNKNOWN

Control classification supplied for E130:

- complete reproducible recipe: **UNKNOWN**;
- useful forensic finding: later/deeper layers create new sources rather than merely transporting a fixed early source basis;
- useful forensic finding: D21 / old-source dependence remains high-rank and materially structured.

At this checkpoint, live branch search and default-branch code search do not expose an E130 branch or run-backed E130 receipt that can be independently pinned to a protocol SHA / executed head / run / job / artifact tuple.

Therefore the E130 forensic findings are retained only as **hypothesis-generating control evidence**. They are not a complete estimator, not a scientific GO, not a ledger row, and not authorization to reconstruct or rescue E130.

No E130 rerun, completion attempt, recipe inference, or renamed E130 variant is authorized.

## Closed / inactive lanes

Explicitly inactive under this control state:

- E122 — TERMINAL NO-GO; no rescue;
- E124 — TERMINAL NO-GO / collision-quarantined; no rescue;
- E127 — TERMINAL NO-GO; no rescue;
- E130 — forensic-only UNKNOWN complete recipe; no continuation;
- E125/E126 and all other prior lanes are outside the active watch set unless a later explicit control receipt says otherwise.

## Active watch set: E132 / E133 only

Live branch search at this checkpoint:

- E132: no branch observed;
- E133: no branch observed.

A new E132 or E133 owner lane is admissible only if all are true **before implementation/workflow execution**:

1. live collision search shows one unambiguous scientific owner identity for the ID;
2. the first scientific owner commit is protocol-only;
3. protocol freezes mechanism, exact parent/provenance, deterministic corpus/seeds, comparator/reference, target/oracle firewall, numerical integrity gates, complete all-in FLOP accounting including diagnostics/helpers/RNG/materialization, and a computable finite error/certificate rule sufficient for the scientific claim;
4. protocol freezes one physical scientific run, no tuning, no rescue, no post-result threshold/mechanism changes, and a terminal kill rule;
5. the mechanism is not a disguised rescue/reconstruction of E122, E124, E127, or E130;
6. canonical and `research/ledger.csv` remain untouched;
7. branch reservation, protocol/status prose, workflow definition, issue/PR/comment, or accepted command alone is not scientific progress.

## One-verifier rule

For each admitted E132/E133 owner lane, the **first qualifying physical scientific run** triggers exactly one independent review-only verifier.

Control must first freeze:

- experiment ID and owner branch;
- protocol SHA;
- executed head;
- run and job IDs;
- artifact ID/name/digest;
- immutable owner result/receipt SHA when available.

Then:

- if a required finite certificate is absent/non-computable, append **FAIL-CLOSED** control receipt and do not dispatch rescue;
- if all-in cost accounting is absent/incomplete, append **FAIL-CLOSED** control receipt and do not dispatch rescue;
- if protocol-first ancestry/collision identity fails, append **FAIL-CLOSED** control receipt;
- otherwise designate exactly one collision-free verifier identity;
- verifier may inspect/recompute frozen evidence only and must not modify, rerun, rescue, tune, or substitute the owner candidate;
- no second verifier or nested verifier is admissible;
- append one owner→verifier handoff receipt on this control branch.

## Single next gate

**Wait for the first collision-free, protocol-first physical scientific run on E132 or E133.**

Until then: no scientific authorization, no status promotion, no ledger row, and no mutation outside append-only control evidence.
