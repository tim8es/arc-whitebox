# R235 - Material exact counted-FLOP second pass on pinned V25

Status: TERMINAL PRE-FIXTURE NO-GO
Run ID: R235-v25-material-exact-second-pass-20260923

## Objective

Continue the exact compute-efficiency lane after R233, exclude
ONEHOT-WICK-ROW-SELECT, and admit at most one distinct output-preserving
contraction/reuse rewrite only if the proved full-V25 saving can reach at least
1.0% of the pinned per-MLP counted FLOPs.

## Pinned source and records

Pinned V25:
- repository: 504aldo/whest-p2-cumulant-k3
- commit: 18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45
- file: estimators/estimator_v25.py
- git blob: 195373a110215256b759d7c172ba8c923c62e5cc
- SHA256 from R233 independent measurement:
  c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20

Operator-profile evidence:
- docs/findings_log.md at the same upstream commit
- git blob: 09cf41e8826052ceb83109115cae688c03baaaca
- F77 is the V25 flopscope op-log / exact-trim audit.
- F79 is the material Strassen audit.

Pinned R209 V25 record:
- SHA256:
  f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742
- counted FLOPs per MLP: 806303721965
- shape: [16,1024]
- failures: 0/100.

R233 terminal receipt SHA256:
a66e9e6699a7c036e4bdcacd202f365ca89310310e3ddea687df75b7c278fa62

## Dominant counted-FLOP profile

F77 records one unit u = 2*n^3 = 2^31 FLOPs for n=1024. The dominant V25
ledger is approximately:

| family | units | interpretation for exact reuse |
|---|---:|---|
| hub contractions | 100u | distinct nonsymmetric operands; no symmetry/alias discount |
| young transports | 80u | dense nonsymmetric WD@(A,P,Z) products; batching does not lower arithmetic count |
| shared-basis contractions | 30u | structurally required dense contractions |
| shared-basis formings | 33u | structurally required dense formings |
| W@Q / WD@Q | 27u | structurally required basis transport |
| C_pre sandwich | 22.5u | already billed at 0.75 symmetric rate |
| 16 dense n x n matmuls | 16u | 15 required newborn W@a_b transports plus final C@w32 |
| joins/moves/QR | about 20u | basis maintenance |
| term table | about 2.5u | small relative to total |

The 180u hub+young core alone dominates the ledger. Its operands are not same-object
symmetric products, so aliasing, symmetry tags, packing, or call fusion do not reduce
the scalar multiply-add count while preserving the same operation order.

## One screened direction: WEIGHTED-ALIAS-GRAM

The strongest remaining algebraically exact ledger rewrite is the weighted Gram
family used by the shared-basis join and tier-2 move:

    S = F @ (d * F.T)

With X = F.T, the same mathematical object is

    S = einsum("ia,i,ib->ab", X, d, X)

where the same X object appears twice. In principle this can receive flopscope's
same-object symmetric alias price.

This direction is distinct from R233.

### Exact source schedule

Pinned suite constants:
- n = 1024
- depth L = 16
- AGE_OLD = 4
- R_OLD = 384
- AGE_OLD2 = 7
- R_OLD2 = 224

The source gates imply:
- shared-basis joins at layers 5..14: 10 events;
- tier-2 moves at layers 8..14: 7 events;
- two weighted grams per event.

Therefore exactly 34 weighted Gram products are eligible.

One current dense (384,1024) @ (1024,384) matmul costs:

    384 * 384 * (2*1024 - 1)
    = 301842432 FLOPs

Current total at all eligible sites:

    34 * 301842432
    = 10262642688 FLOPs

Even granting an ideal exact half-price rewrite at every site, the maximum possible
saving is:

    5131321344 FLOPs/MLP

Relative to pinned V25:

    5131321344 / 806303721965
    = 0.0063640055282080665
    = 0.6364005528208066%

The R235 gate is 1.0%:

    0.01 * 806303721965
    = 8063037219.65 FLOPs/MLP

Thus the ideal candidate reaches only 63.64% of the required threshold and misses
it by a factor of 1.5713374156693627.

This is a strict optimistic upper bound. Upstream F77 also records that the
weighted same-object einsum can raise SymmetryError at representative operand
scale; that secondary implementation blocker is not needed for the R235 verdict.

## Other material-looking route excluded by exactness

Upstream F79 shows Strassen-Winograd can materially lower the two dominant
families, from roughly 0.3667xB to 0.3125xB in the reported ladder. However F79
explicitly records that for level > 0 the float32 summation order changes.

R235 requires exact output preservation. Therefore Strassen/reassociation is not
an eligible exact contraction/reuse optimization, even though its arithmetic
saving is material.

## Frozen fixture disposition

Before queue start, R235 committed:
- R235_PROTOCOL.md
- R235_COST_MODEL.json
- scripts/r235_weighted_alias_gram_fixture.py

The fixture would verify the exact source blob, reconstruct the 10-join/7-move
schedule, and compare the dense weighted Gram against the same-object alias form
under flopscope 0.12.1.

It was intentionally NOT executed. The frozen production cost gate already fails
under the ideal half-price upper bound, so a micro-fixture cannot make the
candidate eligible. The protocol explicitly forbids spending the one allowed
fixture run after this pre-cost failure.

No mini-100 is authorized.

## Decision

TERMINAL PRE-FIXTURE NO-GO.

No distinct exact output-preserving V25 contraction/reuse path survives the
>=1.0% production-savings gate.

The strongest exact ledger candidate has an optimistic upper bound of only
0.6364006%. The dominant nonsymmetric hub/transport core has no alias/symmetry
reuse that lowers counted FLOPs without changing arithmetic, and the known
material Strassen path changes float32 summation order.

No rescue candidate was substituted after the frozen decision.

## Sources

S1 - pinned V25 source:
https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/estimators/estimator_v25.py

S2 - upstream V25 ledger/exact-trim and Strassen findings:
https://github.com/504aldo/whest-p2-cumulant-k3/blob/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/docs/findings_log.md

S3 - official flopscope cost reference:
https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/flopscope-primer.md

S4 - R209 V25 normalized record:
https://github.com/tim8es/arc-whitebox/blob/20fafab5471e6ed227562c651179dd2ef331ea22/research/results/R209-v25-mini100.json

S5 - R233 terminal receipt:
https://github.com/tim8es/arc-whitebox/blob/027f0c517ec55a27fffc0878b043e3216c021344/research/r233/R233_TERMINAL_RECEIPT.json

## Scope confirmation

No canonical estimator edit. No canonical result edit. No estimator run. No
micro-fixture execution. No mini-100. No paid compute. No private/holdout data.
No submission. No retry. No R232 overlap.
