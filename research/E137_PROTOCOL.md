# E137 protocol — MIT V25/V29 public-baseline improvement scout

Idempotency key: `ARC-E137-MIT-V25-V29-IMPROVEMENT-SCOUT-20260921`

Status at freeze: **PROTOCOL ONLY / RESEARCH-NOTE WORK AUTHORIZED; NO ESTIMATOR CODE OR SCIENTIFIC RUN AUTHORIZED**.

Branch:
`research/e137-mit-v25-v29-improvement-scout-20260921`.

Direct parent:
`research/bootstrap`.

## Goal

Produce a primary-source research note whose objective is a **clean improvement over a
verified public MIT-licensed baseline**, not another standalone estimator.

The baseline family is team 504aldo's public Phase-2 cumulant-propagation lineage:

- V16b
- V17
- V18
- V22
- V24
- V25
- V29

with V25 treated as the designated arithmetic/method baseline and V29 as the same arithmetic
after cost engineering.

The note must identify:

1. which exact mechanisms in the V16b/V17/V18/V22/V24/V25 lineage are already established;
2. which measured dead ends from the same primary-source release close obvious follow-ups;
3. which cost and accuracy gates remain genuinely open after V25/V29;
4. exactly one new non-overlapping improvement hypothesis.

## Primary-source policy

Evidence priority is frozen as:

1. public source code and documentation in
   `504aldo/whest-p2-cumulant-k3`;
2. the author's AIcrowd forum post tied from that repository;
3. ARC/reference implementation material named by the public baseline;
4. our own repository only for exclusion/overlap checks and local baseline-verification state.

Secondary summaries may be used only to locate a primary source, never as evidence.

Every quantitative statement in the final note must be tagged as one of:

- **PUBLIC VERIFIED** — directly stated/measured in the public baseline release;
- **LOCAL VERIFIED** — established in this repository by a frozen receipt/result;
- **INFERENCE** — derived from verified facts but not directly measured;
- **HYPOTHESIS** — proposed E137 improvement mechanism.

## No-code rule

This protocol commit precedes all E137 executable work.

Under this E137 scout:

- do not implement estimator code;
- do not create a workflow;
- do not run Actions;
- do not run public/public-mini/scorer/holdout/full;
- do not mutate canonical or ledger state.

The deliverable is a research note and immutable receipt for the note's source/provenance
audit only.

Any later implementation of the selected hypothesis requires a separate successor protocol
and experiment identity.

## Mandatory exclusions

The E137 hypothesis must not be a renamed or direct rescue of:

- E104-E121;
- E122/E124/E127;
- E132 layer-born D21 Hermite control;
- E134 source-age full K=3 direct closure;
- E135 residual/certificate lanes, including Parseval/orthogonal source residual,
  transport-residual certificates, or deterministic truncation-bound rescue;
- V25/V29 dead ends explicitly closed by the public release.

In particular, the hypothesis may not be:

- a new rank/rank-age schedule for the V22/V24 shared/nested bases;
- a larger residual or D21 feedback rank;
- a per-source K4 leg resurrection;
- a Tucker/CP/hub-column merge of the old K3 tier;
- a marginal Edgeworth/Gram-Charlier patch;
- an output correction/control variate;
- a QMC/sampling sidecar;
- a Strassen/pricing-only change;
- a source-window/drop-old-source variant;
- another source-age K3/D21 transport formulation.

## Baseline facts to verify from primary source

Before writing the hypothesis, confirm directly from the public release:

1. V16b exact 7-to-4 unit/source-layer algebraic restructure and its parity claim;
2. V17 memoryless K4 regeneration and what is exact vs fitted;
3. V18 rank-16 D21 feedback;
4. V19 exact last-layer trim, even though it is not the main requested lineage;
5. V22 shared old-source basis;
6. V24 nested second tier;
7. V25 adaptive per-MLP lambda;
8. V26-V29 arithmetic parity with V25 and cost-only engineering;
9. the published raw/cost ceiling of the V25/V29 closure;
10. the dead-end table, especially old-source dropping, slice-only memoryless closure,
    low-rank hub/Tucker variants, augmented K4 cost, output corrections, sampling hybrids,
    and the Khatri-Rao/Hadamard-product wall.

## Improvement-hypothesis admission rule

Exactly one hypothesis may be promoted into the note. It must satisfy all of:

1. **baseline-native:** starts from V25/V29 state and changes one identifiable mechanism;
2. **disjoint:** not in the exclusions above and not E132-E135;
3. **mechanistic:** names the missing information or avoidable computation;
4. **accuracy relevance:** addresses a residual that can plausibly move raw error below the
   V25/V29 closure floor rather than only reprice identical arithmetic;
5. **cost relevance:** has a credible path to lower than V29's old-source burden or to add
   accuracy while keeping total utilization competitive;
6. **falsifiable:** admits a small or local test with a binary GO/NO-GO;
7. **target-free construction:** no benchmark target or leaderboard fit may select the
   mechanism.

If no candidate satisfies all seven, the note must say **UNKNOWN / NO ADMISSIBLE HYPOTHESIS**
rather than relabel a closed lane.

## Required note structure

The final repository note must contain:

- baseline provenance and source hashes/paths where available;
- mechanism ladder V16b→V25;
- V29 cost-only delta;
- dead-end closure table;
- open accuracy gates;
- open cost gates;
- one admitted hypothesis or UNKNOWN;
- a minimal successor falsifier protocol sketch;
- explicit statement that no E137 code/run occurred.

## Close condition

After the note is committed, append a small JSON receipt containing:

- protocol commit;
- note commit;
- exact primary-source URLs/repository paths used;
- public baseline version identifiers;
- overlap audit against E132/E134 and E135 scope;
- selected hypothesis name or UNKNOWN;
- code_run=false;
- actions_run=false.
