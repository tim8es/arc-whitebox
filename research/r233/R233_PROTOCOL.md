# R233 — Output-preserving V25 counted-FLOP reduction protocol

Frozen before executing any fixture.

## Pinned inputs

- Upstream repository: `504aldo/whest-p2-cumulant-k3`
- Upstream commit: `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- V25 path: `estimators/estimator_v25.py`
- V25 git blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- R209 V25 normalized input SHA256:
  `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`
- R209 V25 counted FLOPs per mini-100 row:
  `806303721965`
- Phase-2 shape/budget: width 1024, depth 16, `B=2**41`.

R231 established that compute-only improvement at fixed raw MSE bottoms out at
`2.228303490170447e-9`; therefore tiny pricing-only improvements are not a frontier
solution.

## One frozen source-level optimization

V25 builds `SL2`, `SR2`, and `SL1` in `_term_prog` so every row has exactly one
nonzero coefficient:

- `SL2[t, wl] = coef`
- `SR2[t, wr] = 1`
- `SL1[t, wl] = coef`

Yet every prediction layer evaluates:

```
WL2 = SL2 @ WT
WR2 = SR2 @ WT
WL1 = SL1 @ WT
```

Frozen candidate **ONEHOT-WICK-ROW-SELECT** replaces only those three transforms with
row selection from `WT` and, for SL rows, multiplication by the single coefficient:

```
WL2 = take(WT, wl2_idx, axis=0) * sl2_coef[:, None]
WR2 = take(WT, wr2_idx, axis=0)
WL1 = take(WT, wl1_idx, axis=0) * sl1_coef[:, None]
```

No estimator arithmetic, term ordering, term products, cumulant state, source ranks,
lambda law, or output formula changes.

## Algebraic identity

For a row `s` with one nonzero `s[j]=c`,

`s @ WT = c * WT[j,:]`.

For `SR2`, `c=1`. This is an exact finite-dimensional identity. The fixture must
also show bitwise equality on deterministic finite float32 inputs under flopscope.

## Frozen micro-fixture

The fixture statically parses only constants from the pinned V25 source, reconstructs
`_term_prog` for suite-relevant modes 0 and 1, and never imports or executes the
estimator.

Fixture width: `n=8`; deterministic finite float32 `WT`.

It must verify:

1. exact V25 git blob;
2. term counts: mode0 d2=6, d1=4; mode1 d2=52, d1=14;
3. every `SL2/SR2/SL1` row has exactly one nonzero;
4. baseline dense transforms and candidate transforms are bitwise equal;
5. flopscope 0.12.1 counted FLOPs match the frozen analytic formulas.

## Counted-FLOP model

Official flopscope pricing for float32 matrix multiply is
`M*N*(2*K-1)`; `take`/fancy gather is `4*N`; elementwise multiply is `N`.

With `K=21` Wick pairs:

- dense SL transform: `41*T*n`
- row-select SL transform: `5*T*n`
- dense SR transform: `41*T*n`
- row-select SR transform: `4*T*n`

Therefore savings are:

- d2 pair (`WL2+WR2`): `73*T*n`
- d1 (`WL1`): `36*T*n`

Suite schedule:
- layer 0: mode0, d2+d1;
- layers 1..14: mode1, d2+d1;
- layer 15: trimmed mode1, d1 only.

Frozen projected production saving:
`62,756,864` counted FLOPs per V25 MLP, before any execution.

## Gates

**Identity GO:** all fixture outputs bitwise equal for modes 0 and 1.

**Count GO:** measured candidate FLOPs are strictly lower and fixture deltas equal the
analytic model exactly.

**Meaningful GO:** projected production counted-FLOP reduction must be at least
`0.1%` of the pinned V25 count (`>=806,303,722` FLOPs/MLP), with no estimator-output
change. This is deliberately a modest materiality threshold; it is far below the compute
reduction needed to approach the R231 floor.

A bounded public mini-100 is authorized only if **all three** gates pass. Otherwise R233
ends terminal PRE-MINI NO-GO. No rescue optimization is substituted after seeing the
fixture.

## Prohibitions

No canonical estimator edits, no full estimator execution before gates, no paid compute,
no private/holdout data, no submission, no parameter tuning, no R232 estimator-family
work, and at most one public mini-100 only after the frozen gates.
