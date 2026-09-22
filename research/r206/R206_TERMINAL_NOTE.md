# R206 terminal note — frozen TA rank sweep

Executed once on GitHub Actions run `35750632262`, attempt 1, at
`c74bf80beea36e5b0dba087a3030f34a8aad8c5f`.

No duplicate run is authorized after this receipt.

## Frozen sweep result

Synthetic fixture: float32 `1024x1024 @ 1024x1024`, seed 206, one BLAS
thread.  Reference is the same float32 input promoted to float64.

| tensor | rank | exact scaled integer residual | leaf FLOPs | leaf/classical | full arithmetic FLOPs | full/classical | runtime s | relative-F32 error | candidate/parent relative error |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 26^3 | 8052 | 0 | 1,030,656,000 | 0.479936600 | 13,504,019,200 | 6.288298965 | 0.692035 | 0.02541547 | 85,806.50 |
| 28^3 | 9847 | 0 | 997,560,182 | 0.464525159 | 15,226,343,822 | 7.090318865 | 0.922293 | 0.03289849 | 111,070.32 |
| 30^3 | 11890 | 0 | 1,019,567,500 | 0.474773115 | 17,669,351,000 | 8.227932733 | 1.088782 | 0.04070967 | 137,442.04 |
| 32^3 | 14197 | 0 | 930,414,592 | 0.433258057 | 18,826,027,008 | 8.766551971 | 0.998631 | 0.05231684 | 176,629.63 |

Ordinary float32 parent relative error:
`2.9619515982982244e-07`.

Frozen gates:
- mechanism/full arithmetic ratio <= `0.42`;
- candidate/ordinary-float32 error ratio <= `1.05`;
- exact identity must hold.

All exact identities pass.  All four leaf-only lower bounds already exceed 0.42,
so transform/reconstruction optimization cannot rescue these four ranks under
the frozen arithmetic convention.  Complete arithmetic ratios are 6.29--8.77.
All stability ratios miss 1.05 by five orders of magnitude.

Decision:
`TERMINAL_NO_GO_NO_PARETO_POINT_MEETS_COST_AND_STABILITY`.

No compiler was built.  No benchmark target, holdout, scorer, paid run, or
submission was used.  The canonical research ledger was not modified.

## Successor method (not executed here)

Do **not** continue the LITA square-rank sweep and do not tune the four schemes.

The next non-repeating falsifier should move above the isolated matmul kernel:
**exact contraction-DAG common-subexpression elimination with contraction-order
reassociation for H185**.

Rationale: R206 proves a per-product leaf lower bound above the mechanism gate
for the tested TA family.  A successor therefore has to eliminate dense
products, not merely make their U/V/W transforms cheaper.  The H185 graph
should be represented symbolically, with exact index identities, and a
target-free optimizer should search only legal reassociations and reusable
intermediates.  This is a graph-level exact arithmetic class, not another
bilinear-rank kernel.

Minimal successor falsifier:
1. freeze one synthetic H185 contraction DAG and its tensor shapes;
2. canonicalize index expressions and identify reusable exact intermediates
   before measuring any cost;
3. prove output equality on a small integer fixture;
4. compare complete arithmetic FLOPs of the original and optimized DAG,
   including materialization/reduction additions;
5. require optimized/original FLOPs <= 0.42 before any float32 production-shape
   probe;
6. then require float32 error ratio <= 1.05 against the same float64 reference;
7. terminal NO-GO on either gate; no compiler, benchmark, holdout, or submission.

This successor is only a recommendation recorded by R206; it is not executed
or authorized by this commit.
