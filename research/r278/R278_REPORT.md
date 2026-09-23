# R278 — global residual-direction diagnostic

Status: **BLOCKED BEFORE DIAGNOSTIC EXECUTION**

Job: R278  
Owner: `residual-structure-diagnostic`  
Run: `R278-global-residual-direction-20260923`  
Protocol commit: `9abb05944f7f37c60017a0a68e0a8e319c74ff26`

## Frozen question and split

R278 tests the specific R276 follow-up: whether one fixed network-agnostic final-output residual direction explains material V25 error across the central bulk.

Before inspecting any raw residual vectors, the protocol froze:

- sort immutable R209 `network_id` decimal strings lexicographically;
- first 50 = FIT;
- last 50 = EVAL;
- fit exactly one vector `d = mean_FIT(y_i - p_i)`;
- evaluate only `p_i + d` on EVAL;
- no per-network scalar, sign, selector, feature, normalization, or tuning.

Materiality requires >=2% mean EVAL raw-MSE improvement, >=30/50 networks improved, paired gain >2 descriptive SE, and median EVAL MSE improvement.

## Retained R209 evidence

The existing R209 workflow artifact was inspected locally without rerunning anything.

- artifact id: `10617318650`
- ZIP SHA256: `32c29ac79c5c59b841c88c6c274ed378daf2778a61d4344c7aa0b58f1da11681`
- `report.json` SHA256: `76c496968b9a81dc1eae91e8204969c0dfe9d7f113dd46af0c0e7df82496a78b`
- `environment.txt` SHA256: `13d60bf5de4ac31310c76a0d2526a7b8ac1e66f9e983f30057e693213529fbf2`
- `whest_version.json` SHA256: `c47add2684b095c56ea2a6f951f10098560476094435b1c8159a1fef45ccb29a`

It contains 100 per-MLP records, but those records contain metrics/FLOPs/failure/timing data only. No key containing prediction(s), target(s), truth, or vector is present. Therefore the residual direction cannot be reconstructed from the retained R209 artifact.

The retained run environment was Python 3.11.16, FlopScope 0.12.1+np2.4.6, WhestBench 0.16.1.

## Minimal faithful instrumentation

The exact WhestBench 0.16.1 source was inspected:

- tag `v0.16.1`, annotated tag SHA `66526b4c80d9aea6af981c7a0f92e9ec76c57238`
- tag target commit `4d08668b485c8a7d25a105c3c00d2f4fc2538f18`
- `src/whestbench/scoring.py` blob `9cf7653a0267c4d048617c9045ac8be127f3c8bf`
- `src/whestbench/runner.py` blob `75636c28fa3eabc6047e1c981f34b6a0501ba8f3`
- `src/whestbench/dataset.py` blob `eefa68a335f4031d82a931660be25aa44dc0bbe2`

The smallest faithful capture point is inside `evaluate_estimator()`, after all FLOP/wall/residual/combined-budget failure zeroing and immediately after:

`pred_np = fnp.asarray(predictions, dtype=fnp.float32)`

when the scorer defines:

`final_pred = pred_np[-1]`  
`final_target = data.final_targets[i]`

and before it computes `final_layer_mse`.

A diagnostic callback/file writer there can persist exactly the final vector that the scorer is about to score and its exact baked target, together with MLP name/index, failure flags, and FLOPs. The participant `predict()` BudgetContext has already closed, so runner-side serialization does not change estimator FLOP accounting. Any future run must additionally require exact 100-row `mlp_name` identity/order against immutable R209, then map each unique name to its frozen R209 `network_id`; mismatch must abort before fitting.

## Exact local blocker

The current existing local execution environment is not the pinned R209 environment:

- Python: 3.13.5; no `python3.11` executable;
- NumPy: 2.3.5;
- `whestbench`: not installed;
- `flopscope`: not installed;
- `datasets`: not installed;
- no local Hugging Face cache/copy of the public Phase-2 Mini data was found.

A local attempt to retrieve only the pinned packages,

`python -m pip download --no-deps whestbench==0.16.1 flopscope==0.12.1 -d /mnt/data/pkgs`,

failed before downloading anything after DNS retries with `Temporary failure in name resolution`.

The official prepared Mini split is 100 rows in 14 Arrow shards, approximately 6.72 GB of prepared data; those bytes are not present locally. The retained R209 artifact does not contain the weights, targets, or predictions needed to substitute for the dataset.

Therefore executing V25 here would require either an unpinned Python/package stack, regenerated/synthetic truth, or a new environment/data acquisition path. Any of those would violate the requested faithful pinned mini:all-100 diagnostic.

## Disposition

No residual diagnostic was executed. No MSE or score impact is inferred.

This is an **execution-environment/data-availability blocker**, not evidence for or against a common residual direction.

The frozen test remains executable without redesign if a local resource already containing:

1. Python 3.11.16,
2. WhestBench 0.16.1,
3. FlopScope 0.12.1+np2.4.6,
4. the exact public `mini:all-100` dataset cache,

is supplied. The instrumentation point and split/fit rule do not need to change.

Accounting:

- estimator/V25 executions: 0
- bounded residual diagnostics: 0
- Actions runs: 0
- paid compute: 0
- private/holdout/full access: 0
- submissions: 0
- leaderboard/canonical edits: 0
