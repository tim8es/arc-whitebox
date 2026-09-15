# E043 protocol — terminal-adjoint K3 replay

Status: **PREREGISTERED / NOT YET RUN**

## Provenance and firewall

- Branch: `research/e043-terminal-adjoint-k3-20260915`.
- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Algebra reference only: public `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, `estimators/estimator_v25.py`, git blob `195373a110215256b759d7c172ba8c923c62e5cc`.
- E019–E042 are occupied and immutable. No code, parameter, representation, branch ancestry, or result-conditioned mechanism is inherited from them. In particular this experiment does not use source pruning/reservoirs, backward leverage, signed/angular response fits, half-space mixtures, Hutchinson source sketches, old-tier confinement, or source-column cubature.
- No canonical, ledger, merge, holdout, full split, official scorer, parameter sweep, rescue, rerun, or post-result tuning.
- Public Phase-2 mini index 0 is permitted exactly once after focused tests are GREEN.

## New method class

V25 pays to propagate every inherited K3 source through every later layer and feeds those inherited cumulants back into each intermediate nonlinear closure. E043 tests a different hybrid estimator: **forward local closure + terminal adjoint replay**.

The forward pass contains no inherited K3 carrier. It follows the pinned V25 Gaussian/K4 local closure and creates the same per-layer K3 birth objects, but stores each birth locally instead of transporting it. Old-source K3 D3/D21 terms are set to zero at all nonterminal layers. K4 regeneration and same-layer birth algebra remain pinned; no source is selected, ranked, weighted, or discarded.

At the final preactivation only, every stored K3 birth is replayed exactly through the already-fixed sequence of linearized transport matrices from its birth layer to the final layer. The terminal replay then evaluates the pinned dense V25 `_dslices` contraction for D3. Because the final layer is mean-only in V25, E043 computes no terminal D21: D21 cannot influence a later layer and is excluded by preregistration.

This is an adjoint/recompute representation: source state is not carried forward layer by layer. Cost is exchanged from repeated persistent carrier transport/contraction at every layer for one terminal replay after the forward trajectory has been fixed.

## Fixed-before-evaluation replay contract

For layer index `b`, store the exact birth tuple needed to reconstruct the inherited K3 source immediately after birth: dense `a_b`, right/metadata factors (`s_b`, `e_b`, `c1_b`, `c2_b`, `y_b`, `w2_b`) and the thin residual/feed factors used by the pinned `_dslices` algebra. Store each subsequent dense linearized transport matrix `WDb_t` produced by the forward closure.

For source `b`, define the terminal transport recursively, with no approximation and no rank truncation:

- `A <- a_b`, `P <- I` at the birth boundary;
- for every later transport `t=b+1,...,L-1`, apply the same pinned V25 source update `A <- WDb_t @ A`, `P <- WDb_t @ P`;
- replay all thin residual/feed legs through the same sequence required by the pinned source algebra;
- evaluate the terminal D3 contribution with the pinned dense source contraction;
- sum all stored birth contributions exactly once.

The replay order is chronological and fixed. There is no network-dependent source ordering, no stopping rule, no stochastic sketch, no coefficient fitting, and no result-dependent branch.

The forward nonlinear trajectory is frozen before terminal replay. Terminal D3 is inserted only into the final nonlinear mean calculation; it is not fed backward or used to recompute earlier means/covariances. This missing intermediate inherited-K3 feedback is the sole intended approximation under test.

## Frozen implementation contract

Implementation must verify the pinned V25 git blob before patching. It may modify only source-carrier lifetime/evaluation and the final-layer D3 injection needed for terminal replay. Pinned coefficient tables, lambda adaptation, Gaussian covariance propagation, memoryless K4 formulas, K4->K3 birth algebra, feedback rank/formulas at birth, Wick/nonlinear term programs, and mean formulas remain semantically unchanged.

Native V21/V24 old-source confinement is disabled because E043 has no persistent inherited source carrier to confine. No E042 cubature constants or logic may appear in this branch.

The patch must expose a deterministic pure helper that replays a synthetic source through an arbitrary list of transport matrices. On a linear synthetic chain, terminal replay must equal ordinary sequential forward source transport to floating-point tolerance.

## Focused tests before public data

Without loading public data, tests must establish:

1. branch protocol pins canonical parent, upstream commit/path/blob, and terminal-only replay;
2. replay of dense A/P and thin legs equals ordinary sequential forward transport on deterministic synthetic chains;
3. replay is invariant to whether the suffix product is formed explicitly or applied matrix-by-matrix;
4. with an empty transport suffix, replay is identity;
5. the patched pinned V25 source verifies exact patch target counts and compiles;
6. a synthetic rectangular-width estimator runtime completes, returns finite `(depth,width)`, and records nonzero FLOPs;
7. source-carrier propagation/contraction is absent from nonterminal layers in the patched code, while the terminal replay consumes every stored birth exactly once;
8. the patched source contains no target access, public-data access, experiment-result branching, sweep, rescue, source selection, signed/angular fit, leverage rule, or cubature logic.

RED is committed first and must fail only because the E043 implementation module is absent.

## Single frozen public diagnostic

After focused GREEN, execute exactly one direct diagnostic on `aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`, index `0`, under `flopscope.BudgetContext(2**41)`. Do not call the official scorer or `whest run`.

Record final-layer raw MSE, billed FLOPs/utilization, adjusted proxy `raw_mse * max(0.1, utilization)`, finite/failure status, wall time, pinned-blob identity, patch target counts, number of stored births, number replayed, and terminal-only invariants.

No baseline rerun and no determinism rerun are authorized.

## Frozen local GO gates

Every gate must pass:

- raw final-layer MSE `<= 1.89e-08`;
- utilization `<= 0.14`;
- adjusted proxy `< 2.5e-09`;
- failures `== 0`;
- output finite;
- pinned blob identity exact;
- all patch target counts exact;
- every stored birth is replayed exactly once at the terminal layer and zero times earlier.

Any failed or unevaluable gate => **NO-GO / DROP E043**.

## Kill rule

No E043 rescue or rerun: no intermediate replay window, no second terminal pass, no rank truncation, no source subset, no alternate ordering, no coefficient fit, no restored D21, no feedback/lambda/K4 change, no holdout, no second mini index, and no official scorer. Any material mutation requires E044+ directly from canonical.