# E033 — global diagram-sketch oracle ceiling

Idempotency key: `ARC-CONTINUE-RESEARCH-E033-20260915`

Status: preregistered; exactly one frozen public-mini index-0 diagnostic.

## Provenance / firewall

- Branch: `research/e033-source-hutchinson-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Dense teacher source: upstream `504aldo/whest-p2-cumulant-k3` commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, `lean/lean_k3_aug.py`, expected blob `8fdaa96fd68f30ce9020e6534626e97ebf71d291`.
- Public Phase-2 mini index 0 only.
- E023/E024/E026/E027 terminal and immutable. E028 reviewed local GO is not modified. E029/E032 are closed. E030/E031 are separate/occupied and are not reused.
- No scorer, holdout, second public index, fit, tuning, sweep, coefficient search, rank ladder, or rescue under E033.

## Method class

E033 tests a **global stochastic diagram representation**, not an input sampler and not a K3 micro-prune.

The production hypothesis has two parts:

1. **Persistent full-K4 carrier.** Instead of V25/V29's memoryless closure `G_off ~= lambda C_off`, keep the accumulated fourth-cumulant history in one global low-rank factor, frozen rank `R4=32`. A production implementation would transport the factor through each linear/ReLU response and rebuild it with one fixed range sketch. This targets the missing beyond-memoryless K4 history identified by F88.
2. **Source-axis Hutchinson compression for K3.** Instead of carrying every old K3 birth separately, use exactly `P3=4` fixed Rademacher source sketches. Quadratic self-source contractions are estimated by the identity `E_xi[(sum_s xi_s A_s)(sum_t xi_t P_t)] = sum_s A_s P_s`; cross-source terms cancel in expectation. This is a representation change of the diagram/source axis, not rank pruning of individual source matrices.

Both are intended to reduce state to O((R4+P3) n) transported vectors/factors and O((R4+P3) n^2) layer work.

## Why the first frozen diagnostic is an oracle ceiling

The required raw target, `<=1.89e-08`, is below the published V29/V25-style floor. Before implementing stochastic compression, E033 asks a strictly stronger question:

> If we give the method **exact dense K3 and exact dense persistent augmented-K4 history**, with no rank-32 or Hutchinson approximation at all, does the resulting index-0 output already reach `1.89e-08`?

This dense oracle contains at least as much K3/K4 information as the proposed compressed representation. If the oracle misses the raw gate, compression cannot make this representation class a credible route to the required target; E033 is killed immediately. A favorable numerical perturbation from compression is not a preregistered accuracy mechanism and may not be counted.

The same run records the rank-32 spectral capture of the dense pre-activation K4 core on layers 8..14. This is a secondary representation gate only if the raw oracle passes.

## Frozen diagnostic

1. Load the exact pinned `lean_k3_aug.py` and verify its git blob.
2. Load public Phase-2 mini index 0 only.
3. Run exactly one dense teacher trajectory with `k4_aug=True`, preserving exact K3 source history and exact dense K4 transport; attach a read-only pre-G hook on layers 8..14.
4. Record final-layer MSE against baked `final_means`.
5. In the hook, for each dense symmetric K4 pre-activation core `G`, compute eigenvalues of its off-diagonal residual after removing the shipped memoryless component `lambda_l C_off`; record the Frobenius energy captured by the best rank-32 symmetric approximation. No coefficient is fitted and the trajectory is not modified.
6. Separately meter a production-cost proxy consisting of 32 dense vector transports plus four source-sketch vector transports per active layer, all inside flopscope. Project total utilization using a frozen non-source base allowance of `0.095 B`; the complete projected utilization is `0.095 + measured_proxy/B`. The 0.095 allowance is deliberately conservative relative to covariance/Wick/non-source arithmetic and is fixed before the run.
7. Repeat only the scalar oracle prediction once unmetered to require bit-identical determinism. No alternate rank or P is evaluated.

## Frozen gates

All must pass for E033 GO:

1. **Oracle raw ceiling:** dense exact-K3 + dense persistent-K4 final MSE `<=1.89e-08`.
2. **K4 compressibility:** mean layers-8..14 best-rank-32 residual energy capture `>=0.95`, and worst layer `>=0.90`.
3. **Projected utilization:** `0.095 + proxy_flops / 2**41 <=0.14`.
4. **Joint adjusted path:** `oracle_raw * max(0.1, projected_util) <=2.646e-09`.
5. residual proxy `<0.400 s` and finite.
6. deterministic repeat max-abs difference `==0`.
7. exact pinned lean blob match.

Any failed or unevaluable gate => **NO-GO / DROP E033**. In particular, an oracle-raw failure cannot be rescued by changing R4, P3, lambda, source age, adding a fitted coefficient, or hoping compression changes floating-point error favorably. Any such idea requires E034+.

## Quantitative path

The hard target pair is unchanged:

- raw final MSE `<=1.89e-08`;
- utilization `<=0.14`.

At the boundary, adjusted `<=2.646e-09`.

The production proxy has 36 transported vectors. At n=1024 and 16 layers, one vector transport costs about `2 n^2`; even with several elementwise response operations, `36 * 16 * 2 n^2` is only about `1.21e9` FLOPs (`~0.00055 B`). Thus the projected compute gate is dominated by the fixed `0.095 B` non-source allowance and has substantial headroom. The scientific uncertainty is accuracy/representation, which is why the dense oracle ceiling is the primary gate.
