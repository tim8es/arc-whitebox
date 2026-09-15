# E042 protocol — inherited K3 source-column cubature

Status: **PREREGISTERED / NOT YET RUN**

## Provenance and firewall

- Branch: `research/e042-source-column-cubature-20260915`.
- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Reference estimator only: public `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, `estimators/estimator_v25.py`, git blob `195373a110215256b759d7c172ba8c923c62e5cc`.
- E019–E041 are occupied, immutable, and not inherited or cherry-picked. In particular E039 half-space and E041 backward-leverage/source-selection mechanisms are excluded.
- No canonical, ledger, merge, holdout, full split, official scorer, parameter sweep, rescue, or post-result tuning.
- Public Phase-2 mini index 0 is permitted exactly once, only after focused tests are GREEN.

## Disjoint method class

V25 represents every inherited K3 source hub with dense `n x n` A/P column families (or later with a shared row-space basis). E042 changes the **internal integration representation**, not the set of source births: every source is retained, but the source hub's column-index sum is evaluated by a fixed deterministic cubature rule.

For suite width `n=1024`, freeze `q=320` column nodes. The nodes are architecture-only and fixed before any MLP or target is inspected. Let `bitrev10(k)` reverse the ten low bits of integer `k`. For a source born at layer `b`, use

`J_b[k] = (bitrev10(k) + 73*b) mod 1024`, for `k=0..319`.

All 320 nodes are unique. The cubature weight is the constant

`omega = 1024 / 320 = 3.2`.

The birth-dependent cyclic offset prevents the same omitted neuron coordinates from being reused by every source while remaining independent of network values and scientific outcomes.

## Hybrid exact/cubature boundary

The same-layer birth calculation is unchanged and exact: the V25 birth D3/D21, memoryless K4 regeneration, K4->K3 feed, and rank-16 D21 feedback are evaluated with the pinned formulas.

After birth, only the inherited K3 hub carrier is cubature-compressed:

- A/P source legs retain columns `J_b` only, shape `n x q` per source;
- source-column metadata (`w2`, `s`, `e`, K4-feed column scalars) is retained at the same `J_b` nodes;
- subsequent linear source transports act exactly on those retained columns;
- every inherited hub contraction over the source-column index is multiplied by `omega`;
- no birth/source is removed, no outcome-dependent source weighting is allowed, and no signed response fitting is used;
- native V21/V24 row-space confinement is disabled because it is a different representation axis and is shape-incompatible with the cubature carrier.

Thus E042 tests whether the 1024-column hub integral is sufficiently self-averaging that deterministic 320-node cubature preserves the K3/K4 accuracy field while reducing all inherited source transports and contractions from an `n` column axis to `q`.

## Frozen implementation contract

The patcher must verify the pinned V25 git blob before any change. It may modify only the source-carrier storage/transport, source-column metadata shapes, dense inherited `_dslices` contractions, and module-level E042 constants needed for the cubature representation. All V25 coefficient tables, nonlinear term specifications, lambda adaptation, K4 formulas, feedback rank, mean formulas, covariance formulas, and birth formulas remain byte-for-byte semantically unchanged.

For non-suite synthetic widths, the helper rule uses `q=min(320,n)` and the smallest power-of-two bit width covering `n`; if `q==n`, node order may permute columns but `omega=1` and the cubature contraction must equal the dense reference to floating-point tolerance.

## Focused tests before public data

Tests must establish, without loading the public dataset:

1. the branch protocol pins the canonical parent, upstream commit/path/blob, and `q=320`;
2. node generation is deterministic, unique, in range, birth-dependent, and gives exactly 320 nodes at width 1024;
3. `omega*n_nodes == n` exactly to floating tolerance;
4. a synthetic hub contraction implemented by cubature is exact when `q==n` and agrees with an explicit selected-column weighted reference when `q<n`;
5. a synthetic linear transport preserves the selected source-column identity and shape across two layers;
6. patch target counts on the real pinned V25 source are exact and the patched source compiles;
7. the patched source freezes native row-space confinement off and contains no experiment-ID-dependent fallback, sweep, target access, or result-dependent node choice.

RED is committed and must fail only because the E042 implementation module is absent. Public mini data is forbidden during RED/GREEN iteration.

## Single frozen public diagnostic

After focused GREEN, execute exactly one scientific diagnostic on public Phase-2 mini index 0. Under the normal `flopscope` estimator budget, run the patched E042 estimator once and record:

- final-layer raw MSE;
- billed FLOPs and utilization;
- adjusted proxy `raw_mse * max(0.1, utilization)`;
- failure/finite status;
- wall/residual time if exposed by the harness;
- pinned upstream blob and patch target counts;
- `q`, `omega`, and per-birth node-cardinality checks.

No baseline rerun is authorized; the canonical E007/V25 measurements are the comparison record. No determinism rerun is authorized because the node rule and estimator are deterministic by construction.

## Frozen local GO gates

Every gate must pass:

- raw final-layer MSE `<= 1.89e-08`;
- utilization `<= 0.14`;
- adjusted proxy `< 2.5e-09`;
- failures `== 0`;
- output finite;
- pinned blob identity exact;
- all patch target counts exact;
- every source keeps exactly `q=320` inherited hub columns at suite width.

Any failed or unevaluable gate => **NO-GO / DROP E042**.

## Kill rule

No E042 rescue or rerun: no alternate q, alternate nodes, random seed, network-aware reordering, signed weights, changed omega, source pruning, birth filtering, rank change, lambda change, feedback change, coefficient fit, holdout, second mini index, official scorer, or result-conditioned patch. Any material mutation requires E043+ directly from canonical.