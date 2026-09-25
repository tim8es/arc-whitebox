# R388 — no-dataset generated-network screen protocol

**Status:** COMPLETE — protocol/research only  
**Verdict:** **USEFUL_AS_PAIRED_ENGINEERING_SCREEN_ONLY**  
**Not:** Mini-100 validation, public-50 validation, leaderboard evidence, or a substitute for a real submission  
**Branch:** `research/r388-no-dataset-screen-protocol-20260925`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Date:** 2026-09-25

## 1. Bottom line

Official no-dataset `whest run` is genuinely useful for ARC research **without downloading a contest dataset**, but only for a narrow purpose:

> **Run a frozen candidate and a frozen parent on exactly the same newly generated Phase-2-shaped networks and exactly the same locally sampled targets, then analyze paired candidate-minus-parent deltas.**

It is materially weaker as an **absolute-score** proxy for a strong estimator such as V25. The current no-dataset default uses only **200,000 Monte-Carlo input samples per MLP** to form its target means; the production Mini/public datasets use baked **N = 1,000,000,000** ground truth. At the current source's documented Phase-2 average final-layer variance (~0.0748), the local target's own mean-squared sampling floor is about `3.74e-7`, whereas R209/V25's Mini-100 raw final-layer MSE is `2.228303490170447e-8`. Thus an absolute no-dataset V25 MSE is not a faithful estimate of its competition-quality error.

The useful signal is the **paired difference**, because both estimators can be scored against the identical generated network and identical sampled target under the same root seed. The common target-noise square cancels algebraically in the difference of squared errors; only a cross-term proportional to the candidate-parent prediction difference remains.

R388 therefore preregisters a low-cost screen of **8 distinct root seeds × 3 generated MLPs = 24 generated networks**, with V25 and the next frozen estimator evaluated on every one. The eight root-seed suites are the uncertainty units because one root seed also supplies the run-level `ctx.seed`, so treating all 24 MLPs as fully independent replicates would overstate precision if setup-time randomness/state matters.

A pass means only:

**ENGINEERING_SCREEN_GO_TO_HIGHER_FIDELITY_VALIDATION.**

It does **not** mean “beats V25 on Mini-100,” “beats V25 on public-50,” or “will improve leaderboard rank.”

---

## 2. Exact first-party source snapshot

### WhestBench

Audited repository/commit:

`AIcrowd/whestbench@4794ce8673c1221bdb245b19e933ae0afd7ffa3c`

| Item | Path | Git blob SHA-1 |
|---|---|---|
| run CLI and no-dataset defaults | `src/whestbench/cli.py` | `f214a0e210aa2cd10d0d0a68b14a2b1341b4091f` |
| generation/scoring/seeding | `src/whestbench/scoring.py` | `9cf7653a0267c4d048617c9045ac8be127f3c8bf` |
| random MLP generation | `src/whestbench/generation.py` | `38397fae458acfd46b5642866481672c7fce6f2d` |
| Monte-Carlo target generation | `src/whestbench/simulation.py` | `a6fc58c2b71d197478eae62b54c66882332f30d6` |
| JSON-output option | `src/whestbench/presentation/output.py` | `2ddddb9c7ae3844ab8fd26dc301e02f2b98fc2f8` |
| CLI reference | `docs/reference/cli-reference.md` | `aac3684596084492614cfd1f9958fbd877357375` |
| score/per-MLP schema | `docs/reference/score-report-fields.md` | `3b66b33a0775f01eecbda2a148495d471f2eff65` |
| seed behavior regression tests | `tests/test_mlp_seed_plumbing.py` | `1f7cbd9aec2eee6d186a691858decb7807937368` |

Primary links:

- https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/cli.py
- https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/scoring.py
- https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/generation.py
- https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/simulation.py
- https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/docs/reference/score-report-fields.md

### Starter kit

Audited repository/commit:

`AIcrowd/whest-starterkit@5eb9aa1455fcb3216af55994bdf25dc242b95797`

Relevant official docs:

- Stage 3 Mini-100: `docs/getting-started/stage-3-run-local.md`, blob `2bc23fd23210f513a9bfab4917dde6f4ef18c125`  
  https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/getting-started/stage-3-run-local.md
- Evaluation datasets: `docs/how-to/use-evaluation-datasets.md`, blob `53af1ead77023bb2c4c27fa2a64b494a4f46aa26`  
  https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/how-to/use-evaluation-datasets.md

### Existing ARC baseline evidence

Frozen V25 source:

- branch: `research/r209-e136-archive-evidence`
- head: `e1f6dd6a6bc351b8253e255fef424b1931b37de3`
- path: `methods/public_504aldo/estimator_v25.py`
- blob: `195373a110215256b759d7c172ba8c923c62e5cc`

R209 normalized Mini-100 result:

- path: `research/results/R209-v25-mini100.json`
- integration commit: `20fafab5471e6ed227562c651179dd2ef331ea22`
- blob: `0183d0570f7c9965e00e8553ffc003c313865232`
- panel: `v2-phase2 mini:all-100`
- raw final-layer MSE: `2.228303490170447e-8`
- adjusted score: `8.170397440117225e-9`
- measured FLOPs/MLP: `806303721965`
- stage: development

R382 no-download route audit:

- head: `491df3e98adb4c60077350ad0481ec2cd3b601ab`
- report blob: `0f6da35d7dd2de222ecda49a79c1223d1f43451d`
- report: https://github.com/tim8es/arc-whitebox/blob/491df3e98adb4c60077350ad0481ec2cd3b601ab/research/r382/R382_NO_DOWNLOAD_EVALUATION_ROUTE.md

---

## 3. Exact no-dataset generation protocol

Current production source `_default_contest_spec()` in `src/whestbench/cli.py` returns:

- width = **1024**
- depth = **16**
- default MLP count = **10**
- per-MLP FLOP budget = current `DEFAULT_FLOP_BUDGET` = **2^41 = 2,199,023,255,552**
- default no-dataset ground-truth samples = **200,000**

The `whest run` parser can override:

- `--n-mlps`;
- `--n-samples`;
- `--seed`;
- `--flop-budget`;
- wall/setup/residual limits;
- runner and output format.

### 3.1 Network distribution

`sample_mlp()` generates each of the 16 weight matrices with shape `(1024,1024)` as:

`W_l[j,k] ~ N(0, 2/1024)`

then stores weights as float32.

This is He initialization for the bias-free ReLU MLP model used by WhestBench.

### 3.2 Target-input distribution

`sample_layer_statistics()` generates i.i.d. standard-Gaussian input vectors:

`x ~ N(0, I_1024)`

as float32. It propagates them through all 16 ReLU layers and accumulates per-neuron means in chunks, with float64 accumulation and float32 returned means.

At `--n-samples 200000`, each generated MLP therefore receives a Monte-Carlo approximation to its population activation means based on 200,000 independent Gaussian inputs.

### 3.3 Seed splitting

For a specified root `--seed S`, `make_contest()` executes:

`SeedSequence(S).spawn(3 * n_mlps)`.

For MLP index `i`, three separate spawned streams are assigned:

1. `3i`: weight-generation RNG;
2. `3i+1`: ground-truth Gaussian-input RNG;
3. `3i+2`: participant-facing estimator seed, exposed as `mlp.seed`.

The same root `--seed` also controls setup randomness through `ctx.seed` according to the official CLI/estimator contract.

The first-party regression tests verify that:

- per-MLP seeds are distinct inside a seeded generated suite;
- repeating the same root seed reproduces the per-MLP seed list;
- changing the root seed changes that list;
- `mlp.seed` survives subprocess transport.

Therefore a parent and candidate invoked with the same toolchain, root seed, `n_mlps`, and `n_samples` are designed to receive the same generated MLPs and the same target-sampling streams. This is the basis of the paired screen.

### 3.4 Important documentation mismatch

At the audited commit, the human CLI reference contains a stale/general sentence saying that no-dataset `--n-samples` defaults to `width*width*256`.

The **actual current run parser and `_default_contest_spec()` source both explicitly use 200,000** for no-dataset `whest run`.

R388 resolves this ambiguity in favor of executable source and preregisters `--n-samples 200000` explicitly rather than relying on a default.

This matters: a frozen protocol should not silently change if the documentation/default is corrected later.

---

## 4. Exact scoring protocol

For a valid MLP row, current WhestBench defines:

`s_m = final_layer_mse_m * max(0.1, C_m / B_m)`

and the suite `adjusted_final_layer_score` is the arithmetic mean of the per-MLP `s_m`.

Under current Phase-2 defaults:

`C_m = F_m`

because `lambda_flops_per_second = 0`.

A failed MLP is scored with the failure semantics documented by WhestBench; the score multiplier is forced to 1.0 rather than receiving the compute discount.

The JSON report exposes per-MLP:

- `mlp_index`;
- `mlp_name`;
- `final_layer_mse`;
- `adjusted_final_layer_score`;
- `flops_used`;
- `effective_compute`;
- wall/backend/overhead/residual timing;
- budget/time/residual failure flags;
- per-layer MSE;
- errors/tracebacks where applicable.

These exact per-MLP fields make no-dataset mode suitable for paired engineering diagnostics.

---

## 5. Why absolute no-dataset score is weak for V25-level estimators

The current WhestBench source itself documents the default 200k target as a development speed/fidelity trade.

Using its cited Phase-2 average final-layer variance of about `0.0748`, Monte-Carlo error in a sampled mean contributes an expected per-neuron squared target error of approximately:

`0.0748 / 200000 = 3.74e-7`.

R209/V25's raw Mini-100 final-layer MSE is only:

`2.228303490170447e-8`.

So the default local target-noise floor is roughly an order of magnitude larger than the V25 error being studied. This does **not** make no-dataset mode useless; it means the **absolute MSE level is the wrong statistic** for this research regime.

Increasing `--n-samples` would reduce target noise, but that directly increases ground-truth generation cost. R388's purpose is a low-cost no-download screen, so it keeps `N=200000` and exploits pairing instead.

---

## 6. Why paired differences retain useful signal

For one neuron, write the sampled target as:

`Y = μ + ε`

where `μ` is the true population mean and `ε` is Monte-Carlo target error. Let `c` and `p` be candidate and parent predictions.

The observed squared-error difference is:

`(c-Y)^2 - (p-Y)^2`

`= (c-μ)^2 - (p-μ)^2 - 2 ε (c-p)`.

The standalone `ε^2` target-noise term cancels **exactly**.

Consequences:

- comparing two absolute no-dataset MSEs is noisy;
- comparing **paired candidate-minus-parent MSE on the same generated target** is much cleaner;
- the remaining target-noise term is proportional to `c-p`, so cancellation is strongest when a proposed estimator is a refinement of V25 rather than a radically different predictor.

This is why the same root seed must be used for parent and candidate. Unpaired generated runs throw away the principal benefit of no-dataset mode.

This algebra does not prove that a paired local improvement transfers to Mini-100/public-50. It only explains why it can be a useful engineering screen.

---

## 7. Mini-100, public-50, and no-dataset are different evidence classes

| Property | no-dataset generated screen | development Mini-100 | live public-50 |
|---|---|---|---|
| Network set | freshly generated from current model distribution | fixed published 100 MLPs | fixed grader public 50 MLPs |
| Width/depth | 1024×16 | 1024×16 | 1024×16 |
| Weight model | He Gaussian via current generator | baked contest-development rows | grader evaluation rows |
| Ground truth | generated locally | baked | server-side baked |
| Ground-truth N | default 200,000; explicitly controllable | 1,000,000,000 | production grader reference |
| Dataset download | none | ~7.03 GB unless cached | none for participant submission path |
| Exact local `per_mlp` | yes | yes | participant raw export not documented; rendered public ledger exists |
| Same network panel as R209 | no | yes | no proven join |
| Submission slot | no | no | yes on the documented route |
| Primary use | engineering falsifier / paired screen | development validation | competition evidence |

Official Mini-100 docs call it the real scorer against **100 fixed** `v2-phase2` MLPs with baked N=1e9 ground truth.

The official Phase-2 public submission surface states that the visible competition score is over **50 public MLPs**, with another 50 sealed MLPs for the full 100-MLP test.

Official example page:

https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329251

No-dataset mode matches the **model class and Phase-2 shape/rules**, not either fixed panel.

---

## 8. Preregistered low-cost R388 screen for the next frozen estimator

### 8.1 Purpose

Falsify weak candidate modifications cheaply before spending:

- a Mini-100 data transfer/run;
- a live submission slot;
- any public/private grader action.

This gate is deliberately classified as:

`ENGINEERING_SCREEN_NOT_LEADERBOARD_EVIDENCE`.

### 8.2 Frozen parent

Use exactly the historical V25 source blob:

`195373a110215256b759d7c172ba8c923c62e5cc`

from:

`research/r209-e136-archive-evidence@e1f6dd6a6bc351b8253e255fef424b1931b37de3:methods/public_504aldo/estimator_v25.py`.

R388 does **not** copy or execute that file. Before a future allocated screen, materialize/verify that exact blob into the run workspace and record its SHA.

### 8.3 Candidate freeze

Before the first R388-panel run, record:

- candidate Git commit;
- candidate file path;
- candidate Git blob SHA;
- SHA-256 of the actual executed file if the harness already records one;
- WhestBench and FlopScope versions;
- host/runtime record from the generated JSON report.

No candidate code/config change is allowed after seeing any R388 panel result.

### 8.4 Fixed panel

Preregistered root seeds:

`388001, 388002, 388003, 388004, 388005, 388006, 388007, 388008`.

For each root:

- `n_mlps = 3`;
- `n_samples = 200000`;
- total generated MLPs = **24**;
- both V25 and candidate use the identical root and flags.

Why 8×3 rather than one 24-MLP suite:

- total network count stays low;
- eight separate root seeds give eight run-level/setup clusters;
- uncertainty can be assessed at the root level instead of pretending three MLPs sharing one `ctx.seed` are independent setup replicates.

### 8.5 Verified command template

The following flags are present in the audited current CLI source. These commands are **protocol templates only; R388 did not execute them**.

Parent, for one preregistered root:

```bash
whest run \
  --estimator <EXACT_V25_BLOB_MATERIALIZED_FILE> \
  --runner local \
  --n-mlps 3 \
  --n-samples 200000 \
  --seed 388001 \
  --flop-budget 2199023255552 \
  --lambda-flops-per-second 0 \
  --wall-time-limit 120 \
  --setup-timeout 5 \
  --residual-wall-time-limit 0.4 \
  --format json
```

Candidate:

```bash
whest run \
  --estimator <FROZEN_CANDIDATE_FILE> \
  --runner local \
  --n-mlps 3 \
  --n-samples 200000 \
  --seed 388001 \
  --flop-budget 2199023255552 \
  --lambda-flops-per-second 0 \
  --wall-time-limit 120 \
  --setup-timeout 5 \
  --residual-wall-time-limit 0.4 \
  --format json
```

Repeat those two commands for the other seven preregistered roots, changing only `--seed`.

Do not add `--dataset`.

The exact local executable wrapper (`whest`, an already-provisioned `uv run whest`, etc.) is environment-specific. R388 does not authorize installation or synchronization of dependencies merely to obtain it.

### 8.6 Pairing integrity

For every root and MLP index, require:

- same `mlp_index`;
- same `mlp_name`;
- same run seed;
- same width/depth;
- same `n_samples`;
- same WhestBench/FlopScope versions;
- same scoring limits.

Any mismatch invalidates that root pair. Do **not** replace it with a different seed.

---

## 9. Uncertainty analysis

### 9.1 Primary unit: root-seed suite

For root `r`, define the mean raw paired delta over its three generated MLPs:

`D_raw,r = mean_i(MSE_candidate,r,i - MSE_V25,r,i)`.

Likewise for the ranked metric:

`D_adj,r = mean_i(score_candidate,r,i - score_V25,r,i)`.

Negative is better.

The eight `D_r` values, not the 24 individual MLP rows, are the primary uncertainty sample. This is conservative with respect to any dependence induced by common run-level `ctx.seed`/setup state.

### 9.2 Reported uncertainty

For both raw and adjusted deltas report:

- the eight root-level values;
- arithmetic mean `D_bar`;
- sample standard deviation `s_D`;
- standard error `s_D / sqrt(8)`;
- one-sided 95% Student-t upper bound:

`U95 = D_bar + t_(0.95,7) * s_D/sqrt(8)`.

Also report:

- 24 per-network paired deltas;
- median per-network delta;
- count of negative per-network deltas;
- number of roots with negative `D_raw,r`;
- failures/resource flags.

The t interval is an engineering summary, not a theorem about the contest distribution. Eight root clusters are intentionally small; the purpose is early rejection, not precise effect estimation.

### 9.3 Robustness against one lucky root

As a distributional guard, require at least **7 of 8** root-level raw deltas to be negative.

Under a simple null in which positive/negative root signs are equiprobable, observing at least 7 negative signs has one-sided probability:

`(C(8,7) + C(8,8)) / 2^8 = 9/256 ≈ 0.035`.

This is not promoted to a contest p-value; it is a preregistered anti-outlier screen.

---

## 10. Exact GO / NO-GO gate

A future frozen candidate gets:

### `ENGINEERING_SCREEN_GO_TO_HIGHER_FIDELITY_VALIDATION`

only if **all** of the following hold:

1. candidate and V25 source hashes were frozen before the first panel result;
2. all eight preregistered roots were evaluated for both parent and candidate;
3. every parent/candidate root pair passes the pairing-integrity checks;
4. no candidate MLP has estimator error, non-finite output, FLOP exhaustion, wall timeout, residual timeout, or combined-budget exhaustion;
5. `U95_raw < 0`;
6. `U95_adj < 0`;
7. at least **7/8** root-level `D_raw,r < 0`;
8. median of the 24 raw per-network deltas is `< 0`.

If any accuracy condition 5–8 fails, classify:

`ENGINEERING_SCREEN_NO_GO_ACCURACY`.

If an operational/resource condition fails, classify:

`ENGINEERING_SCREEN_FAIL_OPERATIONAL`

and preserve the exact failure evidence. A local timing failure may be hardware-sensitive, so it is not automatically a theorem that the candidate fails on the grader; it is still a reason **not to promote** the candidate from this cheap screen.

There is deliberately **no absolute V25-score target** such as “must be below 8.17e-9 locally.” The no-dataset 200k target is too noisy for that interpretation.

There is also deliberately **no percentage ratio gate on absolute generated MSE**. The paired-delta confidence/sign gates are the statistic matched to this mode.

---

## 11. Selection-bias firewall

The R388 seed panel is useful only if it is treated as a preregistered test rather than a tuning set.

Rules:

1. Freeze candidate source/config before any R388 seed result is inspected.
2. Run all eight roots; do not stop after favorable roots.
3. Never drop or replace a difficult root.
4. If an infrastructure corruption makes a pair unusable, rerun **the same root pair** under the same frozen sources; do not substitute a new seed.
5. Do not tune thresholds, hyperparameters, branches, fallbacks, or estimator logic after seeing the panel and then reuse the same panel as confirmatory evidence.
6. If a descendant candidate is designed using these results, the eight R388 roots are **burned for confirmatory purposes**. Pre-register a fresh root panel.
7. If multiple candidates are tried and the best is selected on this same panel, nominal single-candidate uncertainty summaries no longer control selection bias. Treat all such results as exploratory and require a fresh panel before promotion.

These controls matter more than increasing the raw MLP count while repeatedly reusing the same networks.

---

## 12. What conclusions can transfer

A clean GO supports only the following engineering claims:

- the candidate runs at the **Phase-2 1024×16 shape**;
- it fits the nominal Phase-2 analytical FLOP cap on the sampled generated networks;
- on the 24 preregistered generated He-random ReLU networks, paired against V25, the candidate shows a consistent negative raw-MSE and adjusted-score delta under the stated local target protocol;
- no sampled generated network exposed an obvious accuracy/resource catastrophe;
- the method is worth spending a higher-fidelity validation budget on.

The generated networks come from the same documented model family — bias-free dense ReLU layers with He-Gaussian weights and standard-Gaussian inputs — so this screen has more relevance than an arbitrary synthetic fixture.

---

## 13. What conclusions cannot transfer

A GO does **not** establish:

- an R209 Mini-100 score;
- improvement over R209/V25 on the fixed Mini-100;
- a score on the live public-50;
- a leaderboard rank or score gap;
- improvement on the sealed 50;
- exact participant/grader package compatibility;
- exact grader residual/wall timing;
- an 8 GB memory proof when using `--runner local` (local mode records but does not enforce the subprocess memory boundary);
- absence of panel-specific failures on Mini/public MLPs;
- statistical independence of contest MLPs from generated ones;
- a universal population improvement theorem.

If the candidate passes R388, the next evidence tier should remain separate: fixed higher-fidelity same-panel validation (for example Mini-100 if already authorized/available) or a separately authorized public submission route. R388 itself authorizes neither.

---

## 14. Why not use a single default 10-MLP run?

A single default run is useful as a smoke check, but weak research evidence:

- one root seed also fixes `ctx.seed`, so setup behavior is sampled once;
- ten per-MLP rows can look like ten replicates while sharing run-level state;
- there is no estimate of between-root sensitivity;
- one favorable generated suite is easy to overinterpret.

The preregistered 8×3 layout spends only 24 generated networks while obtaining eight independent root-seed clusters for uncertainty and selection-bias control.

---

## 15. Scope / measurement classification

### R388 classification

`PROTOCOL_ONLY / READ_ONLY_SOURCE_AUDIT / NO_MEASUREMENT`.

No R388 performance number is produced.

### Future R388-style screen classification

If executed later under separate authorization:

`GENERATED_NETWORK_ENGINEERING_SCREEN`.

It must **not** be entered into any leaderboard-comparability record as Mini-100, public-50, official-scorer, holdout, or submission evidence.

### R388 execution accounting

- estimator runs: **0**
- generated-network runs: **0**
- benchmark runs: **0**
- Actions: **0**
- installs: **0**
- dependency downloads: **0**
- contest dataset downloads: **0**
- AIcrowd login/auth: **0**
- package upload: **0**
- submissions: **0**
- public/private/holdout/full grader access: **0**
- R320 edits: **0**
- main edits: **0**
- PR edits: **0**
- control edits: **0**
- queue edits: **0**
- repository output: **exactly this one Markdown report**

---

## 16. Final verdict

**USEFUL_AS_PAIRED_ENGINEERING_SCREEN_ONLY.**

The official no-dataset `whest run` is valuable for cheaply testing whether a **frozen** estimator moves in the right direction relative to frozen V25 on fresh Phase-2-distribution networks, provided the comparison is paired on identical seeds/targets and uncertainty is assessed across multiple preregistered root seeds.

It is not a low-download substitute for Mini-100 or public-50, and its default 200k Monte-Carlo target is too noisy to interpret a V25-level **absolute** score.

The concrete next gate is frozen above: **8 roots × 3 MLPs, N=200k, paired V25/candidate, root-cluster uncertainty, GO only with both one-sided U95 bounds below zero plus 7/8 raw root wins and zero operational failures.**
