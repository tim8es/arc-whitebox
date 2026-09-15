# E040 protocol — exact late-source K3 window on pinned V25

Idempotency key: `ARC-E037-RESEARCH-20260915-E040`

Status: **PREREGISTERED / NOT YET RUN**

## Provenance and firewall

- Branch: `research/e040-late-source-exact-window-20260915`.
- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Upstream estimator is pinned exactly to `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, file `estimators/estimator_v25.py`, blob `195373a110215256b759d7c172ba8c923c62e5cc`.
- E019–E039 are immutable/occupied and are not inherited. E038 is terminal DROP; E039 is independently occupied.
- Public Phase-2 mini index **0 only** for exactly one frozen scientific diagnostic.
- No holdout/full split, scorer, second mini index, tuning, sweep, birth-count search, cutoff search, coefficient fit, canonical mutation, or ledger mutation.

## Disjoint hypothesis

V25 spends approximately 95% of its cost in K3 source machinery. Its old sources are not exact: after fixed ages they enter shared low-rank old-source tiers. E040 tests a different representation: **delete all early long-lived sources at birth and retain only a short late window, but retain those selected sources exactly as dense K3 legs for their whole remaining lifetime.**

This is neither old-source rank compression nor a global K3/K4 response carrier. It trades breadth in source birth time for exactness of the sources closest to the final output.

The frozen scientific hypothesis is that the final-layer non-Gaussian correction is dominated by the most recent births and that long-lived approximate old tiers contribute more cost/bias than useful final signal. If true, exact late sources can simultaneously lower compute and improve raw error relative to the pinned V25 trajectory.

## Frozen source window

The network has depth 16. K3 births occur after layers 0..14 and are inserted into the source stacks at the next layer.

Freeze exactly:

- keep birth layers **7,8,9,10,11,12,13,14**;
- equivalently, keep a newborn source iff its insertion layer satisfies `li >= 8`;
- births 0..6 are never inserted into any source stack and leave no source metadata;
- retained births are transported as exact dense V25 source legs;
- old-source confinement is disabled exactly (`V21_NO_CONFINE=1`) so no retained source enters V21/V24 rank tiers;
- all other V25 equations, V18 feedback rank, residual rank, K4 regeneration, lambda rule, final-layer trim and mean program are unchanged.

No reweighting of retained sources is allowed. No scaling compensates for deleted sources. The source window is a literal structural truncation.

## Quantitative cost path

With all 15 births, source-layer lifetimes form `1+...+15 = 120` source-layer pairs before final use. Keeping birth layers 7..14 gives remaining lifetimes `8+7+...+1 = 36` source-layer pairs, exactly 30% of the full count.

Using the upstream F86 finding that approximately 95% of V29/V25-family cost is source machinery, the preregistered first-order utilization projection from V25's `0.36666448` is

`0.36666448 * (0.05 + 0.95 * 36/120) = 0.1223153204`,

which is below the hard `0.14` gate without choosing the cutoff from measured accuracy.

The accuracy target is intentionally stronger than V25: raw final MSE must be `<=1.89e-08`. At utilization below 0.14 this also provides a direct route to adjusted `<2.5e-09`.

## Focused tests before public data

Tests must establish before any mini-data access:

1. exact pinned upstream commit/file/blob identity;
2. patch target occurs exactly once and changes only the newborn insertion predicate from `if newborn is not None and not skip_src:` to the frozen `... and li >= 8:` predicate;
3. `V21_NO_CONFINE=1` is set before executing the pinned estimator source;
4. a synthetic insertion schedule produces exactly insertion layers 8..15 / birth layers 7..14;
5. exactly 8 births are retained and exactly 36 retained source-layer pairs result;
6. projected utilization arithmetic equals `0.1223153204` within `1e-12` and is `<0.14`;
7. patched source remains deterministic and no coefficient/window search logic exists.

RED must be committed before the E040 wrapper module exists and fail only because that module is absent. Public mini data must not be accessed during RED/GREEN iteration.

## Single frozen public diagnostic

After focused GREEN, run exactly once on public Phase-2 mini index 0. The pinned V25 source is fetched by immutable commit and its blob SHA is verified before execution. The frozen one-line birth predicate patch is then applied, `V21_NO_CONFINE=1` is frozen before module execution, and the resulting estimator is evaluated under normal `flopscope.BudgetContext`.

Record:

- final-layer raw MSE;
- billed FLOPs and utilization;
- adjusted proxy `raw_mse * max(0.1, utilization)`;
- residual and wall time;
- failures count;
- deterministic repeat max absolute difference;
- finite status;
- upstream SHA/blob verification;
- exact patch target count;
- retained birth/insertion schedule and source-pair count;
- scope check proving no other upstream source mutation.

## Frozen GO gates

Every gate is mandatory:

- raw final-layer MSE `<=1.89e-08`;
- utilization `<=0.14`;
- adjusted proxy `<2.5e-09`;
- failures `==0`;
- residual wall time `<0.400 s`;
- finite output;
- deterministic repeat max abs difference `==0.0`;
- upstream commit/blob identity exact;
- patch target count exactly `1` and only frozen insertion predicate changed;
- retained births exactly `7..14`, insertion layers exactly `8..15`, source-pair count exactly `36`;
- old-source confinement disabled exactly, with no other V25 environment mutation.

## Kill rule

Any failed or unevaluable structural or quantitative gate => **NO-GO / DROP E040**.

After terminal NO-GO there is no rescue under E040: no alternate cutoff, window length, birth weighting, nonuniform birth selection, source scaling, partial confinement, rank change, K3/K4 add-back/change, lambda change, second index, rerun, scorer, holdout, tuning, or sweep. Any materially different source selection/transport mechanism requires E041+ directly from canonical.
