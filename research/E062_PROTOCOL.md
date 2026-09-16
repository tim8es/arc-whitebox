# E062 Protocol — Phase-2 structure-aware FWHT / antithetic carrier

## Status
Protocol-first. This commit must contain only this file. No public/scorer/holdout/full evaluation is authorized by this protocol.

## Parent / isolation
- Canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Branch: `research/e062-structure-aware-fwht-20260916`.
- E049–E061 are immutable and must not be edited, rerun, rescued, or imported as implementation dependencies.
- Canonical and `research/ledger.csv` are read-only.

## Motivation and public provenance
E062 is a new structure-aware forward estimator family, not a V29 closure modification and not the E061 covariance/MC blend. It adapts the public Phase-1 submission 327651 mechanism class to the Phase-2 official shape (width 1024, depth 16): deterministic angular carrier, pilot-frozen dead/on/kink routing, antithetic continuation, exact FWHT first-layer evaluation, zero-skipping/compaction, and exact algebraic reuse where available.

The Phase-1 public result is used only as structural provenance; its width-256/depth-32 raw MSE is not treated as transferable evidence for Phase-2 accuracy.

## Frozen hypothesis
At width 1024/depth 16, a deterministic two-block signed-Walsh angular carrier with exact Gaussian radial factor and support-exact structural compaction can achieve substantially lower integration error than ordinary MC at the same metered cost. Shorter depth and larger width may make the Phase-1 dead/on/kink execution chassis materially more accurate at a bounded 0.135 budget.

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
- Spherical radius: every direction has Euclidean norm `sqrt(1024)`; convert spherical mean to Gaussian mean using the exact scalar `E[||Z||]/sqrt(1024)` computed from log-gamma constants in billed flopscope-compatible arithmetic or a frozen precomputed float64 constant documented in code.
- Pilot: first `PILOT_LINES=256` line representatives and both antipodes (`512` rows), reused from the production carrier; no additional random/pilot samples.
- Common deterministic seed field: estimator does not draw stochastic production samples. Any test-only synthetic MLP generation uses frozen `PCG64` seed `62062` and is outside prediction work.

## Exact algebraic operations to test
1. **FWHT layer 0** — for each signed Walsh block, compute all 1024 first-layer line products by a 10-stage FWHT rather than an explicit 1024x1024-by-1024x1024 product. Every add/subtract is billed.
2. **Antithetic layer-1 fold** — use `ReLU(-z)=ReLU(z)-z` to obtain the antipodal layer-0 activations and the documented one-step identity for the next preactivation. All helper products are billed.
3. **Support-exact zero-skipping** — if a coordinate is exactly zero for every active carrier row at a layer, omit its column in the next multiplication. Boolean tests, gathers/scatters, and assembly are inside flopscope accounting.
4. **Dead/on/kink suffix** — only the final three layers may use pilot-frozen classification. For a neuron at a suffix layer:
   - `dead`: pilot maximum preactivation `<= 0`;
   - `on`: pilot minimum preactivation `>= 0`;
   - `kink`: otherwise.
   Dead outputs are set to zero on the carrier; on outputs bypass ReLU but still propagate exact carrier values; kink outputs evaluate ReLU row-wise. Classification itself and gathers are billed. This is an approximation only because the pilot classification is applied to production rows; the approximation error must be measured locally.
5. No unmetered NumPy/PyTorch/JAX work is allowed inside `predict`; all numerical prediction-time work must use `flopscope` / `flopscope.numpy`.

## Pre-code cost bound
A naive dense 4096-row forward through 16 width-1024 matrices is approximately `4096 * 16 * 2 * 1024^2 = 1.374e11` multiply/add FLOPs before ReLU/helper overhead, or about `0.0625 B`. Layer-0 FWHT replaces, rather than adds to, the first dense carrier product. Even charging a conservative second full-forward equivalent for pilot/helper/antithetic/compaction overhead gives < `0.125 B`, below the frozen `0.135` gate. Therefore implementation is authorized; measured all-in accounting controls promotion.

## Package-safe preflight gate
Before any real MLP diagnostic:
1. estimator imports from repository root after `pip install -e .`;
2. no module-path hacks;
3. all numerical `predict` work uses flopscope primitives;
4. synthetic width-1024/depth-16 object construction succeeds;
5. FWHT identity against explicit matrix multiplication on a small power-of-two test has relative RMS <= `1e-6`;
6. antithetic identity has max-abs error <= `1e-6` on a small synthetic case;
7. zero-skip route exactly matches dense support evaluation when the skipped columns are identically zero;
8. finite deterministic repeat on a small synthetic case has max-abs diff `0.0`.

Any preflight failure is terminal NO-GO for E062; no repair/rerun unless explicitly authorized by the user.

## Local ground-truth diagnostic
Run exactly one local bounded diagnostic on the smallest available Phase-2 mini/ground-truth item that is also suitable for comparison to E051, preferring `aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`, index `0` if ground truth is locally exposed by the harness.

Measure:
- raw final-layer MSE;
- all-layer MSE when available;
- all-in prediction FLOPs including FWHT, pilot reuse, classification, gathers, zero-skipping, antithetic helpers, radial scaling, output reductions, and metric work separately;
- utilization `all_in_flops / 2**41`;
- residual wall time and backend wall time when exposed;
- failures;
- finite status;
- deterministic repeat max-abs difference;
- counts of dead/on/kink coordinates and zero-skipped columns by layer.

Comparator receipt: E051 verified baseline `raw_final_mse=2.29004485946887e-08`, `utilization=0.2670561845802695`, `failures=0` on Phase-2 mini[0]. E051 is not rerun.

## Frozen local promotion gates
All must pass:
- `raw_final_mse <= 1.89e-8` (leader target noted separately: `1.68e-8`);
- measured all-in utilization `<= 0.135`;
- failures `== 0`;
- finite output and repeat;
- deterministic max-abs diff `== 0.0`;
- no hidden/unmetered prediction-time ndarray work;
- structural counters demonstrate the intended route is active.

Failure of any gate => terminal E062 NO-GO; **no public mini**.

## Bounded public mini authorization
Only after all local promotion gates pass, exactly one bounded Phase-2 public mini diagnostic is authorized, same frozen estimator and constants, with no tuning between local and public. No scorer, holdout, full split, sweep, or rerun.

## Stop conditions
- Local NO-GO: stop immediately, report receipts, no public.
- Local GO but public bounded diagnostic fails: terminal NO-GO, no rescue/rerun.
- Public bounded GO: stop for independent review; no scorer/holdout/full/canonical/ledger mutation.
