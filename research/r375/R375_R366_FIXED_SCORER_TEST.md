# R375 — R366 fixed-Phase-2-scorer rescue/closure

**Status:** COMPLETE  
**Verdict:** **NO_MEASUREMENT / R366_REMAINS_CLOSED**  
**Reason:** a rigorous fixed-Mini scorer gate can be written without the unknown population-target term `eta_i`, but this checkout/evidence set contains neither the exact Mini target tensors nor a valid R366 white-box flattening construction `T_m(W)`. No candidate score was measured.

**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `research/r375-r366-fixed-scorer-test-20260924`  
**R366 source:** `review/r366-uncovered-estimator-frontier-scout-20260924@02305335c80161311e13839de3268be97a43e504`  
**R373 source:** `review/r373-r366-shallow-ridge-independent-redteam-20260924@99a7e683ce4d0f0a603ecf601d9a2faf7d0b49cf`

R375 does not repeat the R373 algebra/literature red-team. It addresses only the fixed-scorer rescue question and whether the already-retained evidence is sufficient for a real same-panel test.

## 1. Correct fixed Mini scorer GO gate: eta is unnecessary for direct evaluation

R373 correctly showed that a target-free Gaussian-L2 certificate against the mathematical population mean does not by itself upper-bound error against the fixed baked Mini target.

That does **not** prevent a valid local Mini development comparison once the candidate estimator is frozen.

For public Mini row `i`, let:

- `W_i`: public MLP weights;
- `y_i`: fixed baked public Mini target, final layer float32[1024];
- `p_i = E[g_{A_i,B_i}(X)]`: R366 analytic shallow-ridge prediction, where `(A_i,B_i)=T_m(W_i)`;
- `F_i`: FlopScope-counted estimator FLOPs;
- `B=2^41=2,199,023,255,552`.

For a valid Phase-2 row,

`mse_i = mean_j (p_ij-y_ij)^2`

and

`score_i = mse_i * max(0.1, F_i/B)`.

The exact same-panel suite gate is therefore

`S_R366 = (1/100) sum_i score_i < 8.170397440117225e-9 = S_R209`,

with all 100 rows valid under the Phase-2 FLOP, wall-time, residual-time, shape/finiteness and memory constraints.

This gate contains no `eta_i` because it evaluates against the **actual fixed scorer labels** rather than trying to upper-bound them through the exact population mean.

### Target-free estimator versus target-bearing evaluation

The separation required for an honest R366 test is:

1. **Estimator construction:** `T_m(W_i)`, width `m`, all choices, stopping rules and analytic readout must depend only on allowed network information and preregistered constants. No `y_i`, target hashes, R209 residuals, or scorer error may enter candidate construction.
2. **Evaluation only:** after the candidate implementation/configuration is frozen, WhestBench may compare its prediction to the public Mini `y_i` and report the development score.
3. **No post-label rescue:** a failed Mini result cannot be converted into a target-free claim by retuning `T_m`, `m`, or per-network parameters against those same labels without explicitly classifying the work as development tuning.

This is a valid public-development test, not a fresh holdout and not an analytic theorem.

Official first-party documentation confirms that the public `mini` split has 100 MLPs and contains both `weights float32[16,1024,1024]` and `all_layer_means float32[16,1024]`; the baked means use `N=1,000,000,000` samples. The official scorer defines the suite score as mean `final_layer_mse * max(0.1,C_m/B)`, with Phase-2 `C_m=F_m`.

Primary sources:
- https://huggingface.co/datasets/aicrowd/arc-whestbench-public-2026/blob/v2-phase2/README.md
- https://github.com/AIcrowd/whest-starterkit/blob/main/docs/reference/score-report-fields.md

## 2. Existing-artifact availability audit

### 2.1 R224: exact identities/hashes exist; target bytes do not

R224 retained:

- `research/r224/R224_MINI100_FINGERPRINTS.json`
- blob `9ecde34282c3fbef51ff3b11d4ec439012b3c52d`
- 100 exact `mlp_seed/network_id` values;
- 100 exact SHA-256 fingerprints of C-contiguous float32 `all_layer_means[16,1024]`;
- target dtype/shape and dataset metadata SHA.

The extraction script

- `scripts/r224_extract_public_mini100.py`
- blob `1302dc583c8351d1d10bc8d3d4201239c5b6d7a7`

did read `all_layer_means` during the historical authorized extraction, but persisted only fingerprints/metadata. It did **not** persist target arrays.

### 2.2 R291: expected panel manifest has no numeric target arrays

`research/r291/R291_EXPECTED_PUBLIC_MINI100.json`

- blob `caf813cd5eab771108f105fe050fd6631b298733`;
- 100 records;
- no long numeric arrays;
- stores identity/fingerprint metadata, not `weights` or `all_layer_means` tensors.

### 2.3 R209 normalized result has metrics, not prediction/target tensors

`research/results/R209-v25-mini100.json`

- blob `0183d0570f7c9965e00e8553ffc003c313865232`;
- 100 rows, 0 failures;
- `raw_prediction_tensors_archived=false`;
- per-row final MSE, FLOPs, wall/residual time and target hashes are retained;
- no final prediction bytes and no target bytes.

Independent R282 artifact recovery already established:

- branch `research/r282-r209-artifact-recovery-20260923`;
- head `4575900a2f963904fe24c70427b0d1182b97163a`;
- receipt blob `48a29e486405693a993fcc429a3fd9c80d28da5e`;
- verdict `NO_RECOVERABLE_RAW_V25_RESIDUAL_VECTORS_IN_EXISTING_EVIDENCE`;
- R224 target hashes present, target bytes absent;
- exact gap includes the 100 public Mini final target vectors (or full all-layer target tensors).

### 2.4 R293 capture result is still absent

At R375 inspection time, branch `research/r293-v25-capture-result` does not exist.

R353 had already documented that PR #36 is a prepared but not authorized/executed capture path. R375 did not dispatch it.

### 2.5 Local runtime/cache inspection

Read-only local inspection found:

- no mounted repository under `/mnt/data`, `/home/oai/share`, `/workspace`, `/workspaces`, or `/repo`;
- no files under `/mnt/data`;
- no existing Hugging Face cache under the checked `/home/oai/.cache/huggingface`, `/root/.cache/huggingface`, `/tmp/huggingface`, `/data`, or `/datasets` paths.

No network dataset fetch was attempted.

### Availability conclusion

The official public dataset **publishes** exact Mini weights and targets, and R224 preserves enough seeds/hashes to identify the panel. But the exact tensor bytes needed for an offline scorer run are **not already present in the repository artifacts or local runtime available to R375**.

The published seed protocol can reproduce the weights from the public per-MLP seeds, but R375 did not regenerate them; more importantly, exact baked target bytes cannot be reconstructed from the retained hashes. The dataset README notes that bit-for-bit rebaking of means additionally depends on bake accumulation details. Hashes are not scorer labels.

Therefore the requested no-download/no-install constraint blocks a real fixed-Mini scorer execution in this task.

## 3. Independent protocol blocker: R366 still has no candidate T_m

Even if the target tensors had already been cached, R366 does not contain an implementation-ready deterministic flattening algorithm.

Its mechanism is specified only as the required map

`T_m(W_1,...,W_L) -> (A,B)`

with `g(x)=A ReLU(Bx)`.

R366 explicitly stopped because no constructive target-free white-box theorem/algorithm was found that simultaneously supplies:

- a concrete deterministic `T_m`;
- a width `m`;
- a Gaussian-L2 certificate;
- bounded `C_Tm`;
- all-in FLOP/time/memory feasibility.

Inventing a sampled regression/distillation fit would leave the R366 mechanism family and violate its novelty condition. Choosing an arbitrary unproved flattening heuristic would not satisfy the R366 re-entry protocol.

Thus there are **two independent reasons** no R375 benchmark is run:

1. exact public Mini target tensors/weights are not retained locally/repository-side under the no-download constraint;
2. no admissible R366 `T_m` candidate exists to run.

The second blocker means merely materializing the public Mini data would not by itself rescue R366.

## 4. R209 baseline re-verification

From the retained normalized R209 record:

- rows: **100**
- failures: **0**
- mean raw final-layer MSE: **2.228303490170447e-8**
- mean adjusted score: **8.170397440117225e-9**
- measured FLOPs per row: **806,303,721,965**
- mean score multiplier: **0.36666448157347986**
- mean wall time: **29.562124561340013 s**
- max wall time: **30.145106520000354 s**
- mean residual time: **0.17882064507017958 s**
- max residual time: **0.19043814401743475 s**

R375 candidate metrics:

- candidate rows executed: **0**
- candidate final-layer MSE: **NOT_MEASURED**
- candidate adjusted score: **NOT_MEASURED**
- candidate FLOPs/time/memory: **NOT_MEASURED**
- improvement versus R209 `8.170397440117225e-9`: **NOT_ESTABLISHED**

R375 therefore does **not** call R366 an improvement.

## 5. Minimal next step

The cheapest scientific next step is **not** a benchmark run.

First, a separate theory/implementation task must supply one concrete deterministic, target-free `T_m(W)` with frozen `m`, exact estimator code path, and static all-in FLOP/memory accounting. Without that, there is no R366 candidate to evaluate.

Only after such a candidate exists, a separately authorized public-development data-materialization/evaluation step may make the exact `v2-phase2 mini:all-100` rows available and run the frozen candidate through the pinned WhestBench/FlopScope scorer. That future step must verify the retained R224 identities/target SHA-256 values before scoring and must keep target tensors outside estimator construction.

Under the current R375 instruction, no dataset download/materialization is permitted, so this step was not attempted.

## 6. Reproducibility / commands

### Executed read-only local checks

```bash
find /mnt/data -maxdepth 2 -type f
find /home/oai/share /workspace /workspaces /repo /mnt/data -maxdepth 3 -type d -name .git
find /home/oai/.cache/huggingface /root/.cache/huggingface /tmp/huggingface /data /datasets -maxdepth 4 -type f
```

The GitHub evidence was read by immutable ref/blob through the repository API. Key refs/blobs are listed above and in the receipt.

### Benchmark/estimator commands executed

**None.**

No `whest run`, no FlopScope estimator execution, no Actions dispatch, and no dataset loader was invoked.

## 7. Final disposition

**R366 is not rescued by the scorer correction alone.**

R373's unknown-`eta_i` objection can be bypassed for a real public-development comparison by evaluating a frozen target-free candidate directly against the fixed Mini labels. That gives a clean scorer GO gate.

But R375 cannot execute that gate because the retained evidence has hashes/metrics rather than exact target tensors, the runtime has no existing dataset cache, downloads are forbidden, and R366 still lacks a concrete admissible `T_m`.

**Final R375 classification: `NO_MEASUREMENT / R366_REMAINS_CLOSED`.**

## 8. Execution accounting

- R366 edits: **0**
- R320 edits: **0**
- main edits: **0**
- PR edits: **0**
- control/queue edits: **0**
- candidate code committed: **0**
- estimator runs: **0**
- benchmark runs: **0**
- Whest/FlopScope scorer runs: **0**
- Actions runs: **0**
- dataset downloads: **0**
- dependency installs: **0**
- private/holdout/full access: **0**
- submissions: **0**
- paid resources: **0**
- local operations: read-only filesystem/cache inspection plus scalar arithmetic only
