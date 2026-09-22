# R227 — V25 second-regeneration-mode feasibility screen

Date: 2026-09-23
Idempotency: `ARC-R227-V25-SRM2-20260923`
Branch: `research/r227-v25-second-regen-feasibility-20260923`
Queue owner: `v25-optimization`

## 0. One frozen hypothesis

R227 considers exactly one upstream-untried V25 accuracy lever:

> **V25-SRM2:** add one deployable second memoryless K4 regeneration mode beyond
> V25's scalar `G_pre_off = lambda*C_pre_off`, while leaving parent V25 ranks,
> age gates, D21 feedback, scalar lambda rule and all other arithmetic unchanged.

This is the only raw-accuracy item that the pinned upstream F88 history itself
still calls untested. R227 does not reopen R223 feed-local lambda, R219
factor-copula, QPASS/rank/lambda/f64 ladders, future-aware/oversampled basis
variants, CountSketch, response-aligned D21, or Strassen families.

## 1. Frozen parent / panel

Pinned method:
- `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- `estimators/estimator_v25.py` git blob
  `195373a110215256b759d7c172ba8c923c62e5cc`.

R224-normalized R209 mini-100 parent:
- record `research/results/R209-v25-mini100.json`
- record SHA256 `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`
- panel names/order SHA256
  `18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce`
- dataset metadata SHA256
  `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`
- failures `0/100`
- mean raw final MSE `2.228303490170447e-8`
- mean adjusted score `8.170397440117226e-9`
- mean measured FLOPs `806303721965`
- mean C/B `0.36666448157347986`.

No parent rerun is authorized.

## 2. Source novelty / deployability gate

Pinned upstream evidence:
- `lean/g_regen_probe.py` blob
  `2a443055a58e577700585d5664902d0541ec2d2c`;
- `docs/findings_log.md` blob
  `09cf41e8826052ceb83109115cae688c03baaaca`;
- `docs/claims_evidence.md` blob
  `087aaa2404a046afd06bd954a1cc0bf09ffdf05c`.

The published 9-mode probe constructs additional live modes such as
`C*C`, `Sym(diag(mu)K21^T)`, `var var^T`, `K22`, etc. Its coefficients
are obtained by `torch.linalg.lstsq(X,y)` with `y=G_off` from the dense
augmented-K3 chain. The cross-dump `xregen` path likewise first fits every
dump against dense `G_off`, then replays the mean coefficients of the other
dumps.

F88 records only the aggregate oracle result: adding eight modes changes
2.230e-8 -> 2.205e-8 on dumps 0/1 (~1.1%), and says a fitted table captures
less. It does not publish a frozen transferable multi-mode coefficient table,
a target-free online coefficient identity analogous to V25's scalar
`mean(dG)/mean(var)` law, or a factorized production feed formula for a
specific second mode.

### Required feasibility gate

Before any mini-100 execution, all must be true:

1. one specific second mode is identified from immutable evidence;
2. its coefficient is fully specified from quantities already available in
   V25 at inference, or by an immutable published frozen table;
3. candidate construction does not require the removed dense `G_off` oracle;
4. the mode has an explicit production factorization through the K4->K3 feed,
   with complete all-in cost;
5. no benchmark target/final mean or R224 per-network score selects the mode or
   coefficient.

If any item fails, R227 is **TERMINAL PRE-SCIENCE NO-GO** and the mini-100 run
is forbidden.

## 3. Cost falsifier

The special V25 covariance mode is cheap because its K4->K3 feed is
algebraically folded into existing A/P legs. The published generic extra-mode
oracle has no corresponding factorization.

For the literal dense extra-mode feed, one additional dense `n x n` product
per feed-bearing layer is an optimistic lower bound:
- `n=1024`;
- 14 feed-bearing layers;
- `2*n^3` FLOPs per dense product;
- extra lower bound `30,064,771,072` FLOPs
  = `0.013671875 B`.

Even granting the full published oracle raw gain of 1.1%, the optimistic
adjusted-score ratio versus the R224 parent is

`0.989 * (0.36666448157347986 + 0.013671875) / 0.36666448157347986
 = 1.025876995330922`.

Thus a literal dense-mode implementation is score-worse before any mode
formation, coefficient work, or extra term-table cost. A panel run can be
authorized only if the source feasibility gate supplies a non-dense
factorization.

## 4. Frozen source falsifier

`scripts/r227_srm2_feasibility.py` receives exact pinned copies of:
- V25 source;
- `g_regen_probe.py`;
- `findings_log.md`;
- `claims_evidence.md`.

It verifies:
- exact git blob identities;
- the oracle probe contains `torch.linalg.lstsq(X, y[:, None])`;
- `y` is sourced from `Goff`;
- `xregen` fits every dump before replay;
- F88 marks second regeneration mode as the only untested Track-2 item;
- no deployable multi-mode table marker exists in V25;
- the frozen dense-mode lower-bound arithmetic above.

This is a source/feasibility falsifier, not a benchmark run.

## 5. Science authorization

Only if the feasibility falsifier finds a fully specified deployable second
mode and factorization may R227 create candidate estimator source and authorize
one same-panel mini-100 run on verified-free standard public GitHub Actions.

If feasibility fails: no candidate panel, no paid compute, no holdout, no
submission, no rescue under R227.
