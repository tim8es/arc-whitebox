# E062 Protocol — Phase-2 structure-aware FWHT / antithetic carrier

## Status
Protocol-first. The first E062 commit (`51a84b7f66dfb3ac60bc04fd8bdba2c646ccab50`) contained only this file. No public/scorer/holdout/full evaluation is authorized by this protocol.

## Parent / isolation
- Canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Branch: `research/e062-structure-aware-fwht-20260916`.
- E049–E061 are immutable and must not be edited, rerun, rescued, or imported as implementation dependencies.
- Canonical and `research/ledger.csv` are read-only.

## Motivation and public provenance
E062 is a new structure-aware forward estimator family, not a V29 closure modification and not the E061 covariance/MC blend. It adapts the public Phase-1 submission 327651 mechanism class to the Phase-2 official shape (width 1024, depth 16): deterministic angular carrier, pilot-frozen dead/on/kink routing, antithetic continuation, exact FWHT first-layer evaluation, zero-skipping/compaction, and exact algebraic reuse where available.

The Phase-1 public result is used only as structural provenance; its width-256/depth-32 raw MSE is not treated as transferable evidence for Phase-2 accuracy.

## Frozen carrier / sample schedule
No post-hoc tuning is allowed.

- Official shape: `WIDTH=1024`, `DEPTH=16`.
- Budget: `B = 2**41`.
- Deterministic line representatives: `N_LINES=2048`.
- Propagated antipodal rows: `N_ROWS=4096`.
- Carrier blocks: exactly two complete Walsh bases of 1024 rows each.
- Block 0 diagonal sign vector: all `+1`.
- Block 1 diagonal sign vector: `(-1)**popcount(i)` for coordinate `i` (fixed, target-independent).
- Each line is paired with its antipode.
- Spherical radius: every direction has Euclidean norm `sqrt(1024)`; Gaussian radial ratio is frozen as `0.9997558892134077`.
- Pilot: first `PILOT_LINES=256` positive line representatives and their 256 antipodes, reused from the production carrier.
- Evaluation rows for safety diagnostics: all remaining 1792 positive representatives and their antipodes. Pilot and evaluation rows are disjoint.
- No stochastic production samples and no Phase-1 thresholds.

## Exact algebraic operations
1. **FWHT layer 0** — both 1024-row signed Walsh blocks use a 10-stage FWHT; every add/subtract is billed.
2. **Antithetic layer-1 fold** — use `ReLU(-z)=ReLU(z)-z`; helper products are billed.
3. **Support-exact zero-skipping** — columns exactly zero for every carrier row may be omitted in the next multiplication; detection/gathers are billed.
4. **Pilot dead/on/kink chassis** — only final three layers may use pilot-frozen classification. Dead output is zero, on output is the preactivation, kink output uses row-wise ReLU. Only pilot-dead columns may be physically removed from the next dense GEMM. `on` is not allowed to justify a GEMM removal.
5. FULL and CHASSIS use identical carrier points, radial scale, FWHT, antithetic identity and exact zero-skip machinery. Their only approximation difference is pilot dead/on/kink routing and consequent pilot-dead width compaction.
6. All MLP-dependent numerical work is through `flopscope` / `flopscope.numpy`.

## Package-safe preflight
Before a real MLP diagnostic:
1. root import after `pip install -e .`;
2. no module-path hacks;
3. synthetic official-shape construction;
4. FWHT identity relRMS <= `1e-6`;
5. antithetic identity maxabs <= `1e-6` on synthetic tests;
6. support-exact zero skip identity;
7. deterministic finite repeat.

The first E062 preflight passed on run `35111319158` (`4 passed`). The earlier single-item carrier-accuracy diagnostic is not the scout chassis falsifier and is not reused as evidence for the gates below.

## Frozen four-MLP FULL-vs-CHASSIS falsifier addendum
This addendum is authorized by the user clarification and precedes any public test.

Dataset is fixed to `aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`, indices exactly `[0,1,2,3]`. No other local MLP is inspected before verdict.

### Gate A — exact implementation aids
On index 0, full-width real weights:
- signed FWHT layer-0 products are checked against explicit Walsh matrix products;
- antithetic layer-1 folded preactivation is checked against explicit negative-carrier propagation.
Across the audit tensors require relRMS <= `1e-6` and maxabs <= `5e-6`.
Audit FLOPs are metered separately and reported; they are not credited as operational savings.

### Gate B — pilot sign safety
For each of the final-three-layer classifications, classification uses only the 512 frozen pilot rows. Violations are evaluated only on the disjoint 3584 evaluation rows.

For classified `dead`, a violation is `pre > 0`; for classified `on`, a violation is `pre < 0`. `kink` has no sign assertion.

Downstream mass for neuron j is frozen as `m_j = sum_k W_next[j,k]^2` when a next layer exists, otherwise `m_j = 1`. Weighted sign-violation mass is
`sum(|pre_ij| * m_j * violation_ij) / sum(|pre_ij| * m_j * classified_ij)`
over dead/on evaluation entries, pooled over all four MLPs and suffix layers. Gate: <= `1e-4`.

A neuron is `high-downstream-mass` iff `m_j >= 2 * mean(m)`. Gate: zero sign violations on any such classified neuron. This threshold is frozen before the diagnostic and is not tuned.

### Gate C — ground-truth parity
For each of the four MLPs compute final-layer raw MSE for FULL and CHASSIS against exposed `final_means` ground truth. Require:
- pooled CHASSIS raw MSE / pooled FULL raw MSE <= `1.01`;
- each per-MLP CHASSIS/FULL raw ratio <= `1.03`.

### Gate D — measured structural saving
Run FULL and CHASSIS separately under fresh `flops.BudgetContext` so all FWHT, antithetic, pilot, comparisons, gathers, compaction and GEMMs are billed.
Require pooled all-in prediction FLOPs ratio `CHASSIS/FULL <= 0.90`.

For each physically removed pilot-dead GEMM input column, report the exact dense-matmul FLOP saving implied by the actual matrix shapes. The sum of these removed-GEMM FLOPs must account for >=70% of measured `FULL_FLOPs - CHASSIS_FLOPs`. No savings are credited to FWHT or antithetic identities because they are common to both branches. Report residual wall time and ordinary wall time for both branches.

### Stop rule
Any failure of Gate A/B/C/D => terminal E062 NO-GO, no repair/tuning/rerun/public. If all four pass, stop for review before one bounded official-shape Stage-A. Public remains unauthorized until that later review.

## No hidden work
Prediction and structural diagnostic arithmetic that depends on MLP values or carrier values uses flopscope primitives. Python is used only for control flow, frozen constants/indices, serialization and shape-based FLOP bookkeeping. No NumPy/PyTorch/JAX prediction path is permitted.

## Forbidden
No scorer, holdout, full split, tuning, sweep, post-hoc pruning thresholds, V29 closure edits, canonical mutation or ledger mutation.
