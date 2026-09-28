# R393 — independent audit of the R388 no-download paired `whest run` screen

**Status:** COMPLETE — independent source/protocol audit only  
**Verdict:** **FAIL_AS_WRITTEN__SEED_PAIRING_PASS__GO_GATE_REQUIRES_CORRECTION**  
**Execution:** no estimator run, no generated-network run, no install, no download, no dataset access, no submission  
**Branch:** `research/r393-paired-screen-audit-20260928`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Date:** 2026-09-28

## 1. Bottom line

R388 is **correct about the central seed mechanism**:

> With no `--dataset`, two separate `whest run` invocations using the same explicit root `--seed`, the same `--n-mlps`, the same explicit `--n-samples`, and the same WhestBench/FlopScope numerical environment regenerate the same weight RNG streams, the same ground-truth-input RNG streams, the same per-MLP estimator seeds, and the same setup seed.

The current source constructs all generated contest data **before** estimator setup, so the candidate cannot influence the generated networks or sampled targets.

However, the **R388 GO gate is not valid as written for R385/V25**. Two material protocol defects must be corrected before a GO can be treated as confirmatory engineering evidence:

1. **Adjusted-score target noise does not cancel when candidate and control have different compute multipliers.** R388 correctly derives cancellation for raw squared-error differences, but then also requires `U95_adj < 0`. For R385 versus V25 the multipliers are expected to differ substantially, so the common (arepsilon^2) target-noise term survives in the adjusted-score difference and is biased in favor of the cheaper estimator.
2. **R388 requires zero candidate failures but does not equivalently prohibit parent/control failures.** A failed V25 row is scored against zero predictions with multiplier 1.0 and can make the candidate look artificially favorable. Any failure in either arm must block GO.

A smaller auditability defect also needs correction:

3. Current JSON `run_config` records `seed`, shape, budget and timing limits, but **does not record `n_samples`**. Therefore exact command lines/flags must be retained externally; JSON equality alone cannot prove both runs used `--n-samples 200000`.

With the corrections in §10, the no-download screen is useful as a **raw-MSE paired engineering falsifier only**. A clean GO permits higher-fidelity validation; it does not establish Mini-100/public-50/leaderboard improvement or an official adjusted-score improvement.

---

## 2. Exact audited artifacts and primary sources

### R388

- branch: `research/r388-no-dataset-screen-protocol-20260925`
- head: `e00498ffbab0ef5e5e5c1a58d5874ec4af5627e6`
- report: `research/r388/R388_NO_DATASET_SCREEN_PROTOCOL.md`
- report blob: `ec4a6126d29b2475c9459bb2bf435eecea8bb0b3`
- link: https://github.com/tim8es/arc-whitebox/blob/e00498ffbab0ef5e5e5c1a58d5874ec4af5627e6/research/r388/R388_NO_DATASET_SCREEN_PROTOCOL.md

R388 itself is protocol-only and reports zero measurements.

### Current official WhestBench source

Current `AIcrowd/whestbench` main audited at:

`4794ce8673c1221bdb245b19e933ae0afd7ffa3c`

| Source | Git blob SHA-1 | Primary link |
|---|---|---|
| CLI / `whest run` | `f214a0e210aa2cd10d0d0a68b14a2b1341b4091f` | https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/cli.py |
| contest generation + scoring | `9cf7653a0267c4d048617c9045ac8be127f3c8bf` | https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/scoring.py |
| random MLP generation | `38397fae458acfd46b5642866481672c7fce6f2d` | https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/generation.py |
| MC target generation | `a6fc58c2b71d197478eae62b54c66882332f30d6` | https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/simulation.py |
| runner lifecycle | `75636c28fa3eabc6047e1c981f34b6a0501ba8f3` | https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/runner.py |
| estimator contract | `3472b746b07f412729090f6a83bc828c35d26f80` | https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/docs/reference/estimator-contract.md |
| score report fields | `3b66b33a0775f01eecbda2a148495d471f2eff65` | https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/docs/reference/score-report-fields.md |
| MLP seed regression tests | `1f7cbd9aec2eee6d186a691858decb7807937368` | https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/tests/test_mlp_seed_plumbing.py |
| setup-seed regression tests | `ceb04c32f36238a2090d3fff1c7d2086793222d9` | https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/tests/test_setup_context_seed.py |

The current official main is the same WhestBench commit R388 audited; there is no source-version drift between R388 and R393.

### R385 / R391 state boundary

R385's research report is committed at:
- branch `research/r385-multishell-clipped-gelr-20260925`
- head `2ba08cb916cc504f1c38673971c2aa811b2da48c`.

At R393 review time there is **no live repository branch/ref named R391**. This does not block the protocol audit, but it means R393 does not certify a repository-visible R391 candidate freeze/hash. The corrected gate below requires the actual executed candidate hash to be frozen before the first R388-root result is inspected.

---

## 3. `--seed` semantics — PASS

The current `whest run` parser states explicitly:

> Without `--dataset`, `--seed` seeds both MLP generation and estimator setup; with a dataset it controls setup only.

Source: current `cli.py`, run parser around lines 1371–1380.

For no-dataset generation, `make_contest()` executes:

[
operatorname{SeedSequence}(S).spawn(3n).
]

For MLP (i):

- child (3i): weight RNG;
- child (3i+1): ground-truth Gaussian-input RNG;
- child (3i+2): participant-facing `mlp.seed`.

Current source: `scoring.py`, `make_contest()`, around lines 114–150.

Separately, the CLI passes:

[
	exttt{SetupContext.seed}=S
]

to estimator `setup()`. Current source: `cli.py`, `_run_estimator_with_runner()`, around lines 2478–2496.

Therefore R388's three-stream split plus run-level setup seed description is correct.

### Estimator RNG nuance

Same root gives candidate and control the same **seed values**:
- same `ctx.seed=S`;
- same per-MLP `mlp.seed`.

It does **not** imply two different estimator implementations consume identical random variates. If candidate and control make different RNG calls, their estimator-internal streams diverge even when initialized from the same seed. The pairing guarantee is exact for the supplied seeds, not for arbitrary internal RNG draw sequences.

For deterministic R385/V25-style estimators this distinction is irrelevant. For stochastic descendants it must be stated explicitly.

---

## 4. Network and ground-truth MC pairing — PASS under frozen environment

### Weights

`sample_mlp()` receives child RNG (3i) and draws every (1024	imes1024) layer matrix from:

[
N(0,2/1024),
]

then stores float32 weights.

Source: `generation.py`, blob
`38397fae458acfd46b5642866481672c7fce6f2d`.

Thus same root, same MLP count and same source produce the same random weight streams.

### Ground-truth inputs

`sample_layer_statistics()` receives child RNG (3i+1), samples float32
(N(0,I_{1024})) inputs, propagates them in a fixed chunk order through all 16 ReLU layers, accumulates sums/squares in float64, and returns float32 means.

Source: `simulation.py`, blob
`a6fc58c2b71d197478eae62b54c66882332f30d6`.

With explicit `--n-samples 200000`, both arms consume the same number of draws from the same child stream.

### Candidate cannot affect generation

In current CLI control flow, `make_contest(spec)` finishes **before**:
- `SetupContext` construction,
- estimator loading/setup,
- any `predict()`.

Source: `cli.py`, `_run_estimator_with_runner()`:
contest construction around lines 2463–2476; runner setup starts at lines 2478–2496.

Therefore candidate/control code cannot perturb weight or ground-truth RNG state.

### Exact claim boundary

Under:
- the same exact WhestBench source/version,
- the same FlopScope numerical backend/version,
- the same root,
- the same `n_mlps`,
- the same explicit `n_samples`,
- the same numerical-thread/backend configuration,

the two invocations follow the same deterministic stream/arithmetic path and are source-semantically paired on networks and MC targets.

However, the standard JSON report contains no target hash and no raw `mlp.seed`; it exposes `mlp_name` and run seed. Thus **target-byte identity is not independently fingerprinted by the output artifact**. It is established from the frozen source semantics plus frozen environment/commands.

For auditability, preserve the exact command and environment record; do not claim that matching JSON alone proves target-byte identity.

---

## 5. `--n-samples 200000` — PASS only when explicit

Current executable source uses:
- no-dataset default `ground_truth_samples=200_000`;
- parser help also says default 200,000.

Source: `cli.py` around lines 125–146 and 1298–1308.

The human CLI reference still contains a stale sentence describing a different formula. R388 correctly avoids dependence on that documentation mismatch by specifying:

`--n-samples 200000`

explicitly.

### Auditability correction

Current JSON `run_config` records:
- `n_mlps`,
- width/depth,
- seed,
- FLOP budget,
- setup/wall/residual limits,
- lambda,

but **not `ground_truth_samples` / `n_samples`**.

Source: `cli.py`, report construction around lines 2518–2538.

Therefore every future paired-screen receipt must persist the exact command/argv (or an equivalent immutable protocol record) proving `--n-samples 200000` for both arms. Do not infer it from JSON.

---

## 6. Setup/reset/state semantics — PASS with one important cluster caveat

For `--runner local`:

1. `LocalRunner.start()` first calls `close()`;
2. it loads a fresh estimator object;
3. it calls `setup(context)` once;
4. the same estimator instance handles all three `predict()` calls in that root suite;
5. `runner.close()` is called in a `finally` block after scoring and invokes `teardown()`.

Sources:
- `runner.py`, `LocalRunner.start/close`;
- `cli.py`, `_run_estimator_with_runner()` around lines 2495–2511.

R388's command template launches separate shell `whest run` invocations. Therefore each candidate/control/root arm starts a fresh CLI process and a fresh estimator lifecycle.

The official setup-seed tests independently verify:
- two separate `whest run --seed 42` invocations give identical setup RNG draws for a correctly seeded estimator;
- local and subprocess runners give identical setup-seed draws.

Blob:
`ceb04c32f36238a2090d3fff1c7d2086793222d9`.

### Cluster caveat

Inside one root suite, estimator state is **not reset between the three MLPs**. A stateful estimator can let MLP 1 affect MLP 2/3. That is another reason the root suite, not the 24 individual rows, is the correct primary uncertainty unit.

Exact correction:
- each root × arm must be a fresh `whest run` process;
- do not implement the screen by reusing one long-lived estimator object across roots unless the harness reproduces the official fresh-run lifecycle.

---

## 7. Raw paired MSE algebra — PASS

For one neuron write sampled target:

[
Y=mu+arepsilon.
]

Let candidate/control predictions be (c,p). Then:

[
(c-Y)^2-(p-Y)^2
=
(c-mu)^2-(p-mu)^2
-2arepsilon(c-p).
]

The common (arepsilon^2) term cancels exactly.

Thus the raw paired delta removes the dominant standalone MC target-noise square. It is **not noise-free**: the cross term remains.

Because target inputs use a separate spawned child stream from `mlp.seed`, and the estimator has no target access, this is a defensible paired engineering statistic. Across root suites, the remaining MC cross term contributes to the observed root-to-root variation.

R388's raw-delta rationale is correct.

---

## 8. Adjusted-score pairing — FAIL for unequal compute multipliers

For valid MLP (m), current scorer uses:

[
s_m=q_m,mathrm{MSE}_m,qquad
q_m=max(0.1,C_m/B_m).
]

Source: `scoring.py`, around lines 656–679 and 960–985.

Let candidate/control multipliers be (q_c,q_p). The observed adjusted delta against noisy target (Y=mu+arepsilon) is:

[
egin{aligned}
D_{m adj}^{m obs}
={}&q_c,mathrm{MSE}(c,Y)-q_p,mathrm{MSE}(p,Y)\
={}&q_c,mathrm{MSE}(c,mu)-q_p,mathrm{MSE}(p,mu)\
&-2,overline{arepsilon,[q_c(c-mu)-q_p(p-mu)]}\
&+(q_c-q_p),overline{arepsilon^2}.
end{aligned}
]

Unlike the raw delta, the (arepsilon^2) term cancels **only if (q_c=q_p)**.

For R385 versus V25 that equality is not expected:
- R385's static certificate path was designed to sit at the 0.1 multiplier floor if its compute envelope holds;
- historical R209/V25 measured (C/Bapprox0.36666448).

Using R388's own development-scale variance estimate
(ar vapprox0.0748) and (N=200000),

[
E[overline{arepsilon^2}]approx 0.0748/200000=3.74	imes10^{-7}.
]

As a scale illustration, (q_c=0.1) and (q_p=0.36666448) imply a target-noise term around:

[
(0.1-0.36666448),3.74	imes10^{-7}
approx -9.97	imes10^{-8}.
]

That is about 12.2 times R209's stored adjusted Mini-100 mean
(8.17	imes10^{-9}). This is **not a predicted screen result**; it demonstrates that the bias can be large enough to dominate the adjusted endpoint.

Therefore R388 criterion:

`U95_adj < 0`

must **not** be used as confirmatory evidence for R385/V25 at (N=200000).

Exact correction:
- remove adjusted-score CI from the GO gate;
- report local adjusted scores only as descriptive diagnostics;
- do not infer a competition adjusted-score advantage from them;
- adjusted pairing could be reused only in the special case where the two arms have identical per-MLP score multipliers, or after an independently justified target-noise debiasing procedure.

---

## 9. FlopScope/scorer/failure semantics

### FlopScope/scorer

Ground-truth generation happens in its own large sampling budget context before participant execution. Its sampling cost is not the estimator's scored compute.

During scoring, participant `predict()` runs inside a per-MLP `BudgetContext`. With R388's explicit:

`--lambda-flops-per-second 0`

effective compute is (C_m=F_m).

For a valid run:
[
q_m=max(0.1,F_m/B_m).
]

This part of R388 is correct.

### Failure semantics

Current WhestBench zeroes predictions on:
- FLOP exhaustion,
- wall-time exhaustion,
- residual-time exhaustion,
- combined-budget exhaustion,
- estimator/prediction validation failures.

Failures are scored with multiplier **1.0**, i.e. no compute discount.

A parent failure can therefore make a candidate appear spuriously favorable.

R388 criterion 4 currently says only that **no candidate MLP** may fail. That is insufficient.

### Exact correction

A GO requires **zero failures in both arms**.

For every one of the 48 arm-MLP evaluations (24 candidate + 24 control), require:
- no `error`;
- no non-finite/shape validation failure;
- `budget_exhausted == false`;
- `time_exhausted == false`;
- `residual_wall_time_exhausted == false`;
- `combined_budget_exhausted == false`.

A failure in either arm invalidates that root pair for confirmatory comparison and blocks GO.

Do not silently drop one MLP and average the remaining two.

If there is a demonstrable infrastructure corruption unrelated to estimator behavior, rerun the **entire same root pair** under unchanged frozen sources/environment; never substitute a new root. Genuine estimator/resource failure is an operational FAIL, not a rerun opportunity.

Also note: the CLI may exit successfully despite budget/time exhaustion; per-MLP flags must be inspected rather than relying only on process return code.

### Local-run resource claim

R388 uses `--runner local`. Under the official contract, the 8 GB memory cap is advisory in local mode and enforced by `--runner subprocess`.

Therefore a local GO cannot claim grader memory compliance. FLOP and local timing evidence remain useful engineering diagnostics.

---

## 10. Corrected seed/execution protocol

The eight preregistered roots remain acceptable:

`388001, 388002, 388003, 388004, 388005, 388006, 388007, 388008`.

For **each root**, execute exactly two fresh CLI processes, one frozen control and one frozen candidate, with identical non-estimator flags:

- `--runner local` (or use subprocess for both arms if memory enforcement is part of the screen; never mix runner modes within a pair);
- `--n-mlps 3`;
- `--n-samples 200000`;
- `--seed <ROOT>`;
- `--flop-budget 2199023255552`;
- `--lambda-flops-per-second 0`;
- `--wall-time-limit 120`;
- `--setup-timeout 5`;
- `--residual-wall-time-limit 0.4`;
- `--format json`.

Freeze and record before result inspection:
1. control Git commit/path/blob and actual executed-file SHA if available;
2. candidate Git commit/path/blob and actual executed-file SHA;
3. exact WhestBench version/commit;
4. exact FlopScope version/backend;
5. Python/runtime/host identity sufficient to establish same numerical environment;
6. exact command argv for all 16 runs, because JSON does not record `n_samples`;
7. any explicit BLAS/thread-limit configuration; it must be the same within every pair.

Pairing integrity per root:
- same root seed;
- same three `mlp_index` values;
- same three `mlp_name` values;
- same width/depth;
- same exact commands except estimator path;
- same toolchain/backend/runtime controls;
- no failure in either arm.

A mismatch blocks that root and therefore blocks confirmatory GO unless the whole same-root pair is rerun for a demonstrated infrastructure reason.

---

## 11. Statistical gate: what passes and what does not

For root (r), retain the R388 primary raw endpoint:

[
D_r=rac13sum_{i=1}^{3}
igl(mathrm{MSE}_{c,r,i}-mathrm{MSE}_{p,r,i}igr).
]

The eight (D_r) values are the primary sample.

This choice is correct because:
- one root shares `ctx.seed`;
- one estimator instance/setup state spans its three MLPs;
- treating all 24 rows as independent would understate cluster dependence for stateful estimators.

### One-sided t upper bound

R388's formula is arithmetically correct:

[
U_{95}
=
ar D+t_{0.95,7}rac{s_D}{sqrt8}.
]

Use it only as an **engineering CI**. Exact Student-t coverage would require normal i.i.d. root-suite deltas; the eight deterministic pseudorandom roots do not supply a theorem that this model is exact.

The inferential statement must therefore remain:
“one-sided root-suite engineering summary under the generated-network seed model,”
not a contest-distribution confidence theorem.

### 7/8 sign guard

Requiring at least 7 of 8 root means negative remains a reasonable preregistered robustness condition.

Under independent roots with null negative-sign probability (1/2) and ties counted as non-wins:

[
P(Kge7)=rac{inom87+inom88}{2^8}=rac9{256}approx0.03516.
]

This is an engineering sign guard, not a leaderboard p-value.

### 24-row median

The median of the 24 raw per-network deltas may remain a descriptive robustness gate. Do not treat it as an independent 24-observation significance test because rows are clustered by root/setup state.

### Multiplicity

For **one preregistered frozen candidate**, requiring several conditions simultaneously
((U95_{m raw}<0), 7/8 raw root wins, raw 24-row median <0, zero failures)
is an intersection gate. It does not require a Bonferroni correction merely because all must pass; adding conjunctive conditions makes promotion stricter.

The real multiplicity risk is **candidate/configuration selection on the same roots**:
- if multiple candidates, shell counts, fallbacks, thresholds or code revisions are examined and the best is selected using these eight roots, the nominal t/sign summaries are no longer confirmatory;
- any candidate modified after any R388-root result burns this panel for confirmatory use;
- promotion then requires a fresh preregistered root panel.

R388's selection-bias firewall is substantively correct and should be enforced literally.

---

## 12. Corrected GO / NO-GO gate

### GO

A frozen candidate may receive only:

`ENGINEERING_SCREEN_GO_TO_HIGHER_FIDELITY_VALIDATION`

if **all** hold:

1. control and candidate hashes/config were frozen before any root result was inspected;
2. all eight preregistered roots × three MLPs were completed for both arms;
3. source-semantic pairing checks and exact-command/environment records pass for every root;
4. **no failure/resource/validation flag occurs in either arm**;
5. root-suite raw-MSE one-sided engineering bound satisfies `U95_raw < 0`;
6. at least 7/8 root-level raw deltas are strictly negative;
7. median of all 24 raw per-network deltas is strictly negative;
8. the eight roots have not previously been used to choose/tune this candidate/configuration.

### Remove from GO

Delete R388 criterion:

`U95_adj < 0`

for R385/V25 at `n_samples=200000`.

Adjusted scores may be printed, but are descriptive local noisy-target quantities only.

### NO-GO / FAIL

- failure of conditions 5–7: `ENGINEERING_SCREEN_NO_GO_ACCURACY`;
- genuine failure in candidate arm: `ENGINEERING_SCREEN_FAIL_OPERATIONAL_CANDIDATE`;
- genuine failure in control arm: `ENGINEERING_SCREEN_FAIL_OPERATIONAL_CONTROL`;
- pairing/command/toolchain mismatch: `ENGINEERING_SCREEN_FAIL_PAIRING_INTEGRITY`;
- post-result code/config tuning or multi-candidate selection on the same roots: `ENGINEERING_SCREEN_EXPLORATORY_PANEL_BURNED`, requiring fresh roots for promotion.

---

## 13. What a corrected GO can legitimately claim

A corrected GO supports only:

- on these 24 preregistered freshly generated 1024×16 He-random ReLU networks,
  candidate raw final-layer MSE was consistently lower than frozen control under a shared 200k-MC target protocol, according to the stated root-cluster engineering gate;
- the candidate executed without sampled local FLOP/wall/residual/validation failures;
- measured local FlopScope compute on those generated rows can be reported descriptively;
- the method deserves a higher-fidelity fixed-target validation step.

A corrected GO does **not** support:

- official adjusted-score improvement;
- R209 Mini-100 improvement;
- public-50 improvement;
- sealed/full improvement;
- leaderboard score, gap or rank;
- exact grader runtime;
- 8 GB compliance under `--runner local`;
- universal improvement over the contest network distribution.

For R385 specifically, the no-dataset screen should be treated as a cheap implementation/accuracy falsifier before separately authorized fixed-target validation.

---

## 14. Final verdict

### Pairing semantics

**PASS.**

Same explicit root + same `n_mlps=3` + same explicit `n_samples=200000` + same toolchain/environment gives the same generated weight streams and same ground-truth input streams; setup receives the same `ctx.seed`, and each corresponding MLP receives the same `mlp.seed`.

### R388/R391 GO protocol as written

**FAIL.**

The raw endpoint is defensible, but the required adjusted-score CI is not target-noise-cancelled when score multipliers differ, and control-arm failures are not explicitly prohibited. JSON also cannot by itself prove `n_samples=200000`.

### Corrected protocol

**PASSABLE AS AN ENGINEERING SCREEN** after applying §§10–12.

It remains strictly a generated-network, no-download promotion gate to higher-fidelity validation and is not contest evidence.

---

## 15. R393 execution accounting

- code/estimator implementation: **NO**
- estimator/generated-network/benchmark runs: **0**
- package/validation runs: **0**
- installs: **0**
- dependency/data/artifact downloads: **0**
- Actions: **0**
- AIcrowd login/auth: **0**
- submission: **0**
- private/public/holdout/full dataset access: **0**
- R320/main/PR/control/queue edits: **0**
- repository output: exactly this one Markdown report.
