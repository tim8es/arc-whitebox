# R235 — second-pass exact V25 material counted-FLOP audit

Frozen before queue start and before any fixture execution.

## Scope

R235 continues the exact compute-efficiency lane after R233 and explicitly excludes
R233's ONEHOT-WICK-ROW-SELECT.

Goal: admit at most one *distinct* source-level contraction/reuse rewrite only if it can
preserve V25 outputs exactly and save at least 1.0% of the full pinned V25 per-MLP
counted FLOPs.

No estimator-family changes, approximations, changed ranks, changed fitted constants,
Strassen/reassociation with changed float32 summation order, canonical edits, paid
compute, private/holdout data, or submission.

## Pinned identities

V25:
- repository: `504aldo/whest-p2-cumulant-k3`
- commit: `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- path: `estimators/estimator_v25.py`
- git blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- SHA256 already independently measured in R233:
  `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`

Pinned V25 operator-profile evidence:
- `docs/findings_log.md` at the same upstream commit
- git blob: `09cf41e8826052ceb83109115cae688c03baaaca`
- F77 records the flopscope op-log ledger and exact-trim audit.
- F79 records that Strassen materially lowers arithmetic count but changes f32 summation
  order at any enabled level, so it is outside R235's exact-output contract.

R209 V25 record:
- path: `research/results/R209-v25-mini100.json`
- git blob: `0183d0570f7c9965e00e8553ffc003c313865232`
- SHA256:
  `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`
- counted FLOPs/MLP: `806303721965`
- shape: `[16,1024]`
- failures: 0.

R233 terminal receipt:
- git blob: `ba6e5a6df48007095ccf7ed1df522f347fe5d61e`
- SHA256:
  `a66e9e6699a7c036e4bdcacd202f365ca89310310e3ddea687df75b7c278fa62`.

Official flopscope cost reference:
- starter-kit commit: `5eb9aa1455fcb3216af55994bdf25dc242b95797`
- `docs/reference/flopscope-primer.md`
- git blob: `7c1478581347f362f691aa1b8023d8edcd44874d`
- float32 matmul price: `M*N*(2*K-1)`.

## Dominant ledger

F77's V25 dump-0 op log uses one unit `u = 2*n^3 = 2^31` FLOPs and records:

- non-symmetric hub contractions: ~100u;
- young dense transports: ~80u;
- shared-basis contractions: ~30u;
- shared-basis formings: ~33u;
- W@Q / WD@Q products: ~27u;
- C_pre sandwich: 22.5u, already billed at the 0.75 symmetric rate;
- 16 dense n×n matmuls: 16u, identified as 15 necessary newborn transports plus the
  required trimmed-final `C @ w32`;
- joins/moves/QR: ~20u;
- term-table contraction: ~2.5u.

The 180u hub+transport core has distinct, non-symmetric operands. Aliasing, symmetry
tags, batching, or mere fusion do not reduce its scalar multiply-add count.

Strassen/Winograd is excluded: upstream F79 shows a material saving but explicitly
records that at level > 0 the float32 summation order changes.

## Single screened direction: WEIGHTED-ALIAS-GRAM

The strongest remaining algebraically exact ledger rewrite is the weighted Gram family:

`S = F @ (d * F.T)`

at V25 source lines corresponding to:
- join update `Sj`: two grams (A and P) per shared-basis join;
- tier-2 move `S_s`: two grams (A and P) per nested move.

Algebraically, with `X = F.T`:

`F @ diag(d) @ F.T = einsum("ia,i,ib->ab", X, d, X)`.

Because the same `X` object appears on both sides, flopscope's alias pricing can, in
principle, bill the einsum at half of the dense symmetric Gram count.

This direction is distinct from R233 ONEHOT-WICK-ROW-SELECT.

## Exact production schedule and upper bound

Pinned suite constants:
- `n=1024`
- `L=16`
- `AGE_OLD=4`
- `R_OLD=384`
- `AGE_OLD2=7`
- `R_OLD2=224`.

From the source gates:
- shared-basis joins occur at layers 5..14 inclusive: 10 joins;
- nested tier-2 moves occur at layers 8..14 inclusive: 7 moves;
- each event evaluates two weighted grams.

Total eligible weighted grams: `2*(10+7)=34`.

One current `(384,1024) @ (1024,384)` float32 matmul costs:

`384*384*(2*1024-1) = 301842432` FLOPs.

Current cost of all 34 sites:

`34*301842432 = 10262642688` FLOPs.

Even granting an ideal, exact, failure-free 0.5× alias price at every site, the absolute
maximum saving is:

`5131321344` FLOPs/MLP.

Relative to pinned V25:

`5131321344 / 806303721965 = 0.0063640055282080665`
= **0.6364005528208066%**.

The R235 material gate is 1.0%:

`0.01 * 806303721965 = 8063037219.65` FLOPs/MLP.

Thus the ideal weighted-Gram rewrite reaches only 63.64% of the required saving and
misses the threshold by a factor of 1.5713374156693627.

This is an *upper bound*: actual flopscope weighted-alias execution can also fail its
symmetry validator at representative operand scale, as upstream F77 records. R235 does
not need that secondary blocker to reject the direction.

## Frozen minimal exact fixture

A reproducible fixture is frozen in
`scripts/r235_weighted_alias_gram_fixture.py`.

If execution were authorized, it would:
1. verify the exact V25 git blob;
2. verify the source constants and derive the 10-join/7-move schedule;
3. construct deterministic finite float32 `F,d`;
4. compare baseline `F @ (d * F.T)` to the same-object weighted alias einsum;
5. require bitwise equality and no `SymmetryError`;
6. compare measured flopscope 0.12.1 count to the analytic formulas.

## Gates, frozen before queue start

1. **Source gate:** exact pinned identities above.
2. **Exactness gate:** bitwise equal fixture output, no exception.
3. **Count gate:** measured candidate counted FLOPs strictly lower than baseline.
4. **Production materiality gate:** proved full V25 saving >=
   `8063037219.65` FLOPs/MLP (1.0%).

**Pre-fixture result:** materiality gate is impossible even under the ideal half-price
upper bound: `5131321344 < 8063037219.65`.

Therefore R235 is pre-registered **TERMINAL PRE-FIXTURE NO-GO**. The fixture is frozen
for reproducibility but MUST NOT be executed because execution cannot change the failed
production bound. Mini-100 is likewise forbidden.

No rescue direction may be substituted after this freeze.
