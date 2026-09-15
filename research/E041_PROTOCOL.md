# E041 protocol — backward-leverage exact K3 source reservoir

Idempotency key: `ARC-E037-RESEARCH-20260915-E041`

Status: **PREREGISTERED / NOT YET RUN**

## Provenance and firewall

- Branch: `research/e041-backward-leverage-source-reservoir-20260915`.
- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Pinned upstream: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, `estimators/estimator_v25.py`, git blob `195373a110215256b759d7c172ba8c923c62e5cc`.
- E019–E040 are immutable/occupied and are not inherited. E040 is terminal unevaluable NO-GO.
- Public Phase-2 mini index **0 only** for exactly one frozen scientific diagnostic.
- No holdout/full split, scorer, second mini index, tuning, sweep, capacity search, probe-count search, gain search, coefficient fitting, canonical mutation, or ledger mutation.

## Disjoint hypothesis

E040 demonstrated that source birth filtering must be atomic over the complete V25 source record. E041 tests a different scientific mechanism: source retention is **network-aware rather than age-window based**. A fixed backward linear-response calculation, using only the MLP weights and no target/output truth, assigns each K3 birth a downstream leverage score. An exact integer knapsack then selects the source records that maximize frozen downstream leverage under a fixed source-transport cost budget. Selected sources are transported exactly as dense V25 source records with old-source confinement disabled; unselected births are atomically omitted from every dense, thin and metadata stack.

This differs from E018 importance-sampled D21: E041 uses no stochastic sampling and no D21 approximation. It selects complete K3 source records deterministically before V25 execution and then transports the selected records exactly.

## Frozen backward leverage

Use exactly four deterministic output probes equal to the first four Walsh/Sylvester-Hadamard sign vectors of length 1024. Probe construction is architecture-only and independent of MLP values.

Let `G_15` be the `1024 x 4` probe matrix at the final layer output. For birth layer `b=14..0`, propagate the probe matrix from layer `b+1` backward through all future linear maps using the frozen mean ReLU gain `1/2`:

`G_b = 0.5 * W_{b+1}^T_adjoint(G_{b+1})`.

In V25 storage the forward linear operator is `w.T`, so the adjoint update is exactly

`G_b = 0.5 * w_{b+1} @ G_{b+1}`.

The frozen birth score is

`score_b = mean_r sum_i G_b[i,r]^2`.

All MLP-dependent score arithmetic must execute under `flopscope` accounting. There is no ground-truth access, source-state access, K3 magnitude estimate, fitted factor or outcome feedback in the selector.

## Frozen cost budget and selection

A birth at layer `b` costs exactly `15-b` dense source-layer transports/uses through the final layer. Freeze integer capacity

`C = 41 source-layer pairs`.

This is the largest integer pair capacity whose first-order V25/F86 projection stays below the utilization gate:

`0.36666448 * (0.05 + 0.95 * 41/120) = 0.13734640313333332 < 0.14`,

while capacity 42 would project to `0.1402491636 > 0.14`.

Select births by exact deterministic 0/1 knapsack over the 15 `(score_b, cost_b)` items, maximizing total score subject to total cost `<=41`. Tie-breaks are frozen lexicographically in favor of the lower birth-index tuple. Because every score is nonnegative, the solver may choose any number of births so long as the exact optimum and tie-break rule are respected. The selected birth tuple is computed once from weights before source execution and is not revised from scientific outcomes.

## Atomic source-record filter

Patch pinned V25 so the selected birth set is read as a frozen module-level tuple supplied by the selector. For a birth `li`, either its complete source record is retained or no part of it is retained.

For unselected births all of the following are omitted consistently:

- `newborn` dense A/P/Z/L record;
- V18 feedback right factors `R1T_st/R2T_st`;
- `w2b_list`;
- `dA_list/dP_list`;
- `c1_list/c2_list/y_list`;
- consequent insertion-time `s_list/e_list` and `Zf_st` additions, because `newborn=None`.

Selected records use the unchanged pinned V25 formulas. Freeze `V21_NO_CONFINE=1` before module execution so selected sources remain exact dense records and never enter V21/V24 old-source low-rank tiers. No selected-source reweighting or compensation for omitted births is permitted.

## Quantitative hypothesis

The target is that a small set of network-important exact source histories captures the final non-Gaussian correction more efficiently than an age-defined window or global marginal/covariance closure.

Mandatory local GO gates:

- raw final-layer MSE `<=1.89e-08`;
- measured utilization `<=0.14`;
- adjusted proxy `raw_mse * max(0.1, utilization) <2.5e-09`;
- failures `==0`;
- residual wall time `<0.400 s`;
- finite output/state;
- deterministic repeat max abs difference `==0.0`.

## Focused tests before public data

Before any public-mini access tests must establish:

1. pinned commit/path/blob constants are exact;
2. four Walsh probes have shape `(n,4)`, entries exactly `{-1,+1}`, and deterministic orthogonality for synthetic power-of-two widths;
3. backward leverage on a hand diagonal two/three-layer network matches an explicit reference;
4. exact knapsack obeys capacity 41 and lexicographic tie-breaking on synthetic scores;
5. capacity arithmetic gives `0.13734640313333332` and capacity 42 exceeds `0.14`;
6. source patch target counts are exact and the patch atomically guards every complete source-record component listed above;
7. synthetic selected/unselected birth schedules keep all per-source stack cardinalities equal;
8. patched source sets `NO_CONFINE=True`, is deterministic, and contains no capacity/probe/gain search logic.

RED must be committed before the E041 module exists and must fail only because that module is absent. Public mini data must not be accessed during RED/GREEN iteration.

## Single frozen public diagnostic

After focused GREEN, run exactly once on public Phase-2 mini index 0. Under one `flopscope.BudgetContext`, first compute the four-probe backward leverage scores and exact capacity-41 selection from the MLP weights, then execute the patched pinned V25 candidate with that selected birth tuple. The selector FLOPs count toward utilization. An identical repeat is allowed solely for determinism and does not authorize alternate selection.

Record:

- 15 leverage scores;
- selected birth tuple and exact pair cost;
- selector FLOPs and total billed FLOPs/utilization;
- final-layer MSE and adjusted proxy;
- residual and wall time;
- deterministic repeat max abs difference;
- failures/finite status;
- pinned blob, patch target counts, NO_CONFINE and atomic-cardinality scope checks.

## Frozen gates

Every gate must pass:

- raw MSE `<=1.89e-08`;
- utilization `<=0.14`;
- adjusted `<2.5e-09`;
- failures `==0`;
- residual `<0.400 s`;
- finite;
- deterministic repeat diff `==0.0`;
- selected pair cost `<=41` and selection equals exact frozen knapsack result;
- selector MLP-dependent arithmetic was billed;
- pinned blob identity exact;
- all atomic patch target counts exact;
- all selected source stacks/metadata have equal cardinality;
- `NO_CONFINE=True` with no other V25 numerical environment mutation.

Any failed or unevaluable gate => **NO-GO / DROP E041**.

## Kill rule

No rescue under E041: no capacity 40/42, alternate probes, alternate ReLU gain, score normalization, greedy selector, source reweighting, partial record filtering, confinement/rank change, K3/K4/lambda modification, rerun, second index, scorer, holdout, tuning or sweep. Any material mutation requires E042+ directly from canonical.
