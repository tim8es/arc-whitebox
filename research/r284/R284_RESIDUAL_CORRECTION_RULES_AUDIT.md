# R284 — rule audit for one fixed global residual correction

**Verdict: CONFIRMED_ALLOWED_WITH_CONDITIONS via the documented shipped-data path.**

Question audited: whether an estimator may use one fixed network-agnostic output-space residual direction `d` and coefficient `alpha`, fitted offline only from the published Phase-2 public-development `mini` networks, then apply that frozen correction to unseen networks.

No estimator was implemented or run. No dataset was downloaded. No Actions, paid resources, private/holdout/full access, submission, leaderboard or canonical edit occurred.

## Required context

R276 proposed a global residual-structure diagnostic after a full-history NO-GO and explicitly suggested one fixed network-agnostic output-space correction direction. R278 froze a concrete FIT/EVAL rule `d = mean_FIT(y-p)` but did not execute it; it stopped on missing retained raw vectors / pinned local runtime. This R284 result is only a rules/source audit, not scientific evidence for the correction.

- R276 report blob: `4970614c1ac789b008260d726a2bbd5272116434`; receipt blob: `56f40cc6b109d769e521c9ba0cf363c7683ef5ab`.
- R278 report blob: `84a1186a70770b0480064f6d26703807b05b2f32`; receipt blob: `1568273d596bd2510c8a3c3520db6da18d2918b0`.

## Classification

| Boundary | Classification | Basis |
| --- | --- | --- |
| Fit `d` / `alpha` offline using only published public-development Mini networks and their public baked targets | **ALLOWED** | The official starterkit calls public `mini` the 100-MLP dataset for "Day-to-day iteration" and exposes identical baked ground truth for fair estimator comparisons. AIcrowd's first-party townhall also states that offline training on external/public Monte-Carlo data is within the rules and offline compute is untracked. |
| Freeze the fitted result before evaluating unseen networks | **ALLOWED** | This is ordinary offline precomputation. The official shipped-weights guide explicitly names a "calibration scalar" and a "learned projection matrix" as examples of offline precomputation that may be shipped. |
| Ship the fixed vector/scalar as numeric data (`.npz`, `flopscope.Module`, lookup/calibration artifact) | **ALLOWED** | Phase-2 allowed-code docs explicitly permit trained weights, lookup tables, calibration constants and other precomputed artifacts. |
| Encode a large learned vector directly as Python source literals rather than shipped data | **UNKNOWN / unnecessary** | The current primary docs explicitly bless numeric **data files** and distinguish data from execution, but do not separately rule on source-literal embedding of a learned 1024-vector. Use the documented `.npz` / Module path instead of relying on this ambiguity. |
| Read or adapt to target values of the new evaluation network | **NOT ALLOWED / not part of the estimator contract** | The estimator contract calls `predict(mlp, budget)`; the only MLP inputs are shape, weights and grader seed. In WhestBench v0.16.1 the scorer calls `predict` inside the budget window, then only after prediction materializes `final_target = data.final_targets[i]` for MSE. Targets are evaluator-side, not estimator inputs. |
| Use the frozen public-development constants on a fresh private/final rerun | **ALLOWED as the same frozen estimator** | AIcrowd states the private rerun uses a completely fresh set of MLPs and no public-split score carries over. Nothing in the cited primary sources prohibits an estimator whose fixed shipped parameters were trained offline on public data. |
| Compute `alpha*d` numerically inside `setup()` to avoid metering | **NOT WITHIN THE DOCUMENTED PATH** | `setup()` is off-budget, but the official contract says it is for **loading precomputed work, not doing it**: compute offline, ship the artifact, read it in setup. |
| Apply the correction numerically inside `predict()` through `fnp` | **REQUIRED / METERED** | All numerical computation must use FlopScope primitives. Current starterkit cost table bills `fnp.multiply` and `fnp.add` at 1 FLOP per element in float32. |

## Development-data use

Current official starterkit `docs/how-to/use-evaluation-datasets.md` at commit
`5eb9aa1455fcb3216af55994bdf25dc242b95797` (blob `53af1ead77023bb2c4c27fa2a64b494a4f46aa26`) says:

- § "Use evaluation datasets", lines 199-205: pre-baked datasets exist for fast iteration and fair comparisons against the same ground-truth means.
- lines 208-214: public `mini` = 100 MLPs, explicitly "Day-to-day iteration"; `full` is a separate final lock-in check.
- lines 226-240: iterate against `mini`; `mini` and `full` are different MLPs.

Primary URL:
https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/how-to/use-evaluation-datasets.md

AIcrowd's own townhall summary (posted by `aicrowd_team`) states at lines 19 and 35 that offline training on external/public Monte-Carlo data is within the rules and the offline compute is not counted; lines 20 and 36 state final/private re-evaluation uses fresh MLPs.

Primary URL:
https://discourse.aicrowd.com/t/townhall-summary-recording/18078

The current official Challenge Rules page remains the source of truth; the starterkit's allowed-code page explicitly says so:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/challenge_rules

## Package-time constants

Current official starterkit `docs/concepts/allowed-code.md` at commit
`5eb9aa1455fcb3216af55994bdf25dc242b95797` (blob `525276e8e5bc7f6a7dd54e876140ab0df514be32`):

- § TL;DR, lines 201-206: data files remain permitted; weights, lookup tables and precomputed artifacts are explicitly allowed.
- § "Data files remain permitted", lines 237-240: precomputation is legitimate; trained weights, lookup tables, calibration constants and any precomputed artifact may be shipped and loaded in `setup()`.

Primary URL:
https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/concepts/allowed-code.md

`docs/how-to/ship-weights.md` at the same commit (blob `1e8dc52cd52bb4858de0aea0e6ca07354e7b4055`):

- § "When to use this page", lines 197-203: explicitly gives a **calibration scalar**, a **learned projection matrix**, or lookup table as valid offline precomputation; shipping data is explicitly permitted.
- § "(b) Authoring weights offline", lines 227-241: offline compute is free, save numeric arrays as plain pickle-free `.npz`.
- § "(c) Loading in setup()", lines 245 onward: load shipped arrays from `submission_dir`.

Primary URL:
https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/how-to/ship-weights.md

Therefore a fixed residual direction vector plus scalar is squarely inside the documented **numeric precomputed artifact** category when shipped as data.

## Evaluation-target leakage boundary

Official starterkit `docs/reference/estimator-contract.md` at commit
`5eb9aa1455fcb3216af55994bdf25dc242b95797` (blob `43c1494420b46aad4bc1dbbab83528eca6b89668`):

- lines 216-239: required call is `predict(self, mlp, budget)`; `predict` runs inside a BudgetContext.
- lines 252-270: `setup()` loads precomputed work; MLP fields exposed to the estimator are width, depth, weights and seed.
- lines 282-288: all numerical estimator computation must use FlopScope; shipped precomputed data remains permitted.

Primary URL:
https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/estimator-contract.md

Independent source-level check against official WhestBench `v0.16.1`:
- annotated tag `66526b4c80d9aea6af981c7a0f92e9ec76c57238` -> commit `4d08668b485c8a7d25a105c3c00d2f4fc2538f18`;
- `src/whestbench/sdk.py` blob `7442366e445702d6c2fcc12baaa39c7a2d7af4da`: `BaseEstimator.predict(self, mlp, budget)`;
- `src/whestbench/scoring.py` blob `9cf7653a0267c4d048617c9045ac8be127f3c8bf`: scorer executes `estimator.predict(mlp, spec.flop_budget)`; only later does it bind `final_target = data.final_targets[i]` and compute MSE.

Primary URLs:
https://github.com/AIcrowd/whestbench/blob/v0.16.1/src/whestbench/sdk.py
https://github.com/AIcrowd/whestbench/blob/v0.16.1/src/whestbench/scoring.py

Thus a constant learned only from public-development targets is **not evaluation-target leakage by itself**. Leakage would begin if the fitted constant depended on the target of the network currently being evaluated, or were updated from sealed/private evaluation outcomes.

## Metered runtime operations

Current starterkit `docs/reference/code-patterns.md` at commit
`5eb9aa1455fcb3216af55994bdf25dc242b95797` (blob `2d1aa532af6f160fd0942da34f78595216a596de`), § "Operation costs", lines 243-266:

- `fnp.asarray(data)`: 0 FLOPs when no copy is needed;
- `fnp.multiply(a, b)`: 1 FLOP per element;
- `fnp.add(a, b)`: 1 FLOP per element.

Primary URL:
https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/code-patterns.md

For a Phase-2 **final-layer 1024-vector** correction:
- if `d` and `alpha` are shipped separately and `alpha*d` is computed in `predict()`, multiply + add is approximately **2,048 metered float32 FLOPs**;
- if `c = alpha*d` is precombined offline and shipped as the frozen correction vector, runtime application is one 1024-element `fnp.add`, approximately **1,024 metered FLOPs**.

Those counts are conditional on only those elementwise operations; any extra copies/stacking/materialization must be accounted separately.

A shape guard is still required for packaging/validation: the official contract warns that `whest validate` probes a tiny non-Phase-2 shape. A 1024-vector correction must therefore be applied only when the handed `mlp` has the compatible Phase-2 width/depth, without returning a hard-coded wrong-shaped output.

## Final answer

A fixed, network-agnostic residual direction and coefficient fitted **offline only on the published public-development Mini networks** may be carried into the estimator **as shipped numeric precomputed data** and applied to unseen networks. That use is supported by the first-party offline-training clarification and the starterkit's explicit calibration-scalar / learned-projection examples.

The compliant documented implementation boundary is:

1. fit and freeze `d` / `alpha` offline on public development data;
2. optionally precombine `alpha*d` offline;
3. ship the scalar/vector as pickle-free numeric data;
4. load only in `setup()`;
5. never read/update from an evaluation network's target;
6. apply the correction inside `predict()` using `fnp`, so its arithmetic is metered.

The only material ambiguity found is **literal source embedding of a learned 1024-vector**: current primary docs explicitly bless shipped numeric data but do not separately bless or prohibit representing the same learned vector as a Python literal. This ambiguity is avoidable; the explicit `.npz` / `flopscope.Module` path should be used.
