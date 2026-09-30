# R393 — independent audit of the no-download paired \`whest run\` screen

**Status:** COMPLETE  
**Overall verdict:** **FAIL AS WRITTEN; PASSABLE ONLY WITH THE CORRECTED GATE BELOW**  
**Execution:** source/protocol audit only; no estimator run, no install, no download, no dataset access, no submission  
**Exact base:** \`4619801e0cc5e7e340cd0406eb44e0633d8aa5e5\`  
**Branch:** \`research/r393-paired-screen-audit-20260928\`  
**Date:** 2026-09-30

## 1. Decision

R388's **pairing mechanism is valid**: with no \`--dataset\`, the same explicit root \`--seed\`, the same \`--n-mlps 3\`, the same explicit \`--n-samples 200000\`, and the same WhestBench/FlopScope environment regenerate the same weight streams, the same ground-truth Monte-Carlo input streams, the same per-MLP estimator seeds, and the same setup seed.

The original R388 GO gate is nevertheless **FAIL** for R385/R391 unless corrected.

The correct primary endpoint is the official Phase-2 quantity

\[
s_m=\mathrm{MSE}_m\max(0.1,C_m/B_m),
\]

not raw MSE alone. A FLOP reduction by itself is not a pass.

However, because R385 and V25 have different score multipliers, the common 200k-MC target noise does **not** cancel from the observed adjusted-score difference. Therefore the no-download screen needs a conservative **dual gate**:

1. **primary:** paired adjusted-score root-suite improvement against the frozen parent;
2. **anti-artifact guard:** paired raw-MSE root-suite improvement too.

A candidate passes only if **both** adjusted and raw root-suite gates pass, plus the failure/pairing/selection-bias conditions below. This preserves the official score objective while preventing a lower utilization number from being treated as victory by itself.

A GO remains only:

\`ENGINEERING_SCREEN_GO_TO_HIGHER_FIDELITY_VALIDATION\`

and does not establish Mini-100, public-50, sealed/full, leaderboard, or official submission improvement.

---

## 2. Exact audited evidence

### R388

- branch: \`research/r388-no-dataset-screen-protocol-20260925\`
- head: \`e00498ffbab0ef5e5e5c1a58d5874ec4af5627e6\`
- report blob: \`ec4a6126d29b2475c9459bb2bf435eecea8bb0b3\`
- report: https://github.com/tim8es/arc-whitebox/blob/e00498ffbab0ef5e5e5c1a58d5874ec4af5627e6/research/r388/R388_NO_DATASET_SCREEN_PROTOCOL.md

### R396 cost update

- branch: \`research/r396-r385-affine-pair-cost-audit-20260928\`
- head: \`22e63b7f3abd8e5252bd18724e263b7e5550eb7f\`
- report blob: \`9a32fa70b2b5f327a6ce88c402fae893033878a1\`
- report: https://github.com/tim8es/arc-whitebox/blob/22e63b7f3abd8e5252bd18724e263b7e5550eb7f/research/r396/R396_R385_AFFINE_PAIR_COST_AUDIT.md

R396's source-based Fast-Lin-style all-in estimate for R385 with K=64 is approximately

\[
2.585\times10^{11}\text{ FLOPs}\approx 11.75\%\times 2^{41}.
\]

That is above the 0.1 floor, so a representative candidate score multiplier would be about 0.1175 if the implementation realizes that ledger. R396 makes no score claim.

### Current official WhestBench source

Audited current main:

\`AIcrowd/whestbench@4794ce8673c1221bdb245b19e933ae0afd7ffa3c\`

Primary source files:

- CLI / run semantics, blob \`f214a0e210aa2cd10d0d0a68b14a2b1341b4091f\`:  
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/cli.py
- contest generation + scoring, blob \`9cf7653a0267c4d048617c9045ac8be127f3c8bf\`:  
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/scoring.py
- random MLP generation, blob \`38397fae458acfd46b5642866481672c7fce6f2d\`:  
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/generation.py
- target simulation, blob \`a6fc58c2b71d197478eae62b54c66882332f30d6\`:  
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/simulation.py
- runner lifecycle, blob \`75636c28fa3eabc6047e1c981f34b6a0501ba8f3\`:  
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/src/whestbench/runner.py
- estimator contract, blob \`3472b746b07f412729090f6a83bc828c35d26f80\`:  
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/docs/reference/estimator-contract.md
- score-report fields, blob \`3b66b33a0775f01eecbda2a148495d471f2eff65\`:  
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/docs/reference/score-report-fields.md
- MLP-seed tests, blob \`1f7cbd9aec2eee6d186a691858decb7807937368\`:  
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/tests/test_mlp_seed_plumbing.py
- setup-seed tests, blob \`ceb04c32f36238a2090d3fff1c7d2086793222d9\`:  
  https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/tests/test_setup_context_seed.py

No WhestBench source drift from the R388 commit was found.

---

## 3. Exact seed semantics — PASS

For no-dataset \`whest run --seed S\`, current \`make_contest()\` performs

\[
\mathrm{SeedSequence}(S).spawn(3n).
\]

For MLP index i:

- child 3i: weight-generation RNG;
- child 3i+1: ground-truth Gaussian-input RNG;
- child 3i+2: participant-facing \`mlp.seed\`.

Separately the CLI sends

\[
\texttt{SetupContext.seed}=S
\]

to \`setup()\`.

Therefore two separate runs with the same:
- root seed,
- \`n_mlps\`,
- \`n_samples\`,
- source/toolchain/backend,

are source-semantically paired on the generated networks and MC target streams.

Important nuance: same \`ctx.seed\`/\`mlp.seed\` means the same seed values are supplied. It does not force different estimator implementations to consume identical internal RNG draw sequences. For deterministic R385/V25-style code this is immaterial.

---

## 4. Weights and ground-truth pairing — PASS

\`sample_mlp()\` draws every dense layer from

\[
W_{jk}\sim N(0,2/1024)
\]

using the weight child stream and stores float32 weights.

\`sample_layer_statistics()\` uses the separate target child stream to draw float32

\[
x\sim N(0,I_{1024})
\]

and propagates exactly \`n_samples\` inputs through the 16-layer network.

The CLI constructs the full contest data **before** estimator loading/setup/predict. Candidate code therefore cannot perturb either generation stream.

With explicit \`--n-samples 200000\`, same root + same source/environment yields the same sampled-target construction path.

The standard JSON report does not carry a target hash or raw \`mlp.seed\`; pairing is established by frozen source semantics and exact commands, not by a target fingerprint in the report.

---

## 5. \`--n-samples=200000\` — PASS, but command capture is mandatory

Current executable source explicitly uses 200,000 as the no-dataset default, and the run parser documents the same number.

R388 correctly specifies it explicitly.

But current JSON \`run_config\` records seed/shape/budget/timing limits and **does not record \`n_samples\`**.

Therefore a confirmatory receipt must persist the exact argv for every arm/root. Matching JSON reports alone do not prove the same target sample count.

---

## 6. Reset/setup/state semantics — PASS with clustering consequence

For \`--runner local\`:

1. \`LocalRunner.start()\` calls \`close()\`;
2. a fresh estimator object is loaded;
3. \`setup(context)\` runs once;
4. the same estimator instance handles the three MLPs of that root suite;
5. \`runner.close()\` runs in a \`finally\` block and calls \`teardown()\`.

Each R388 command is a separate CLI process, so candidate/control/root arms get fresh estimator lifecycles.

Inside one root suite the three MLPs share setup state. Therefore the **root suite is the primary uncertainty unit**; the 24 MLP rows must not be treated as 24 independent setup replicates.

Official regression tests also verify repeatability of setup RNG draws across two runs with the same \`--seed\`.

---

## 7. Official Phase-2 scorer semantics

Current WhestBench defines for a valid row:

\[
s_m=\mathrm{MSE}_m q_m,\qquad
q_m=\max(0.1,C_m/B_m).
\]

With R388's explicit \`--lambda-flops-per-second 0\`,

\[
C_m=F_m.
\]

A failure forces multiplier 1.0 and zero predictions.

Therefore R393 accepts the coordinator correction:

> **Adjusted score is the primary research endpoint. Lower FLOPs are not a victory by themselves; they matter only through the official product of MSE and score multiplier.**

R396's ~11.75% candidate utilization is therefore relevant only as one factor of that product.

---

## 8. Why raw pairing cancels MC noise but adjusted pairing does not

Let

\[
Y=\mu+\varepsilon
\]

be the 200k-MC target, and c,p the candidate/parent predictions.

For raw MSE:

\[
(c-Y)^2-(p-Y)^2
=
(c-\mu)^2-(p-\mu)^2-2\varepsilon(c-p).
\]

The common \(\varepsilon^2\) term cancels exactly.

For adjusted score with multipliers \(q_c,q_p\):

\[
D_{\rm adj}^{obs}
=
q_c\mathrm{MSE}(c,Y)-q_p\mathrm{MSE}(p,Y).
\]

Expanding:

\[
D_{\rm adj}^{obs}
=
D_{\rm adj}^{true}
-2\overline{\varepsilon[q_c(c-\mu)-q_p(p-\mu)]}
+(q_c-q_p)\overline{\varepsilon^2}.
\]

The last term cancels only when \(q_c=q_p\).

R388 cites a Phase-2-scale average final-layer variance around 0.0748. At N=200,000:

\[
E[\overline{\varepsilon^2}]\approx 3.74\times10^{-7}.
\]

Using R396's illustrative R385 multiplier \(q_c\approx0.1175\) and historical V25 \(q_p\approx0.36666448\), the systematic term is on the scale

\[
(0.1175-0.36666448)(3.74\times10^{-7})
\approx -9.32\times10^{-8}.
\]

This is only a scale diagnostic, not a predicted screen result.

It proves that **observed adjusted-score improvement alone is unsafe at N=200k**: cheaper compute can amplify the target-noise floor in the candidate's favor.

Current standard \`whest run\` output does not expose the per-generated-MLP \`avg_variance\` needed for a clean rowwise noise correction. Therefore R393 does not invent a debiased adjusted statistic from unavailable fields.

---

## 9. Corrected endpoint hierarchy

The screen must keep the official adjusted score as **primary**, but it needs a raw-MSE corroboration guard.

For root r define:

\[
D^{adj}_r
=
\frac13\sum_{i=1}^3
(s_{c,r,i}-s_{p,r,i}),
\]

and

\[
D^{raw}_r
=
\frac13\sum_{i=1}^3
(\mathrm{MSE}_{c,r,i}-\mathrm{MSE}_{p,r,i}).
\]

Negative is better.

### Primary endpoint

\[
D^{adj}_r
\]

is the primary research endpoint because it matches the official Phase-2 objective.

### Mandatory anti-artifact endpoint

\[
D^{raw}_r
\]

must also pass its gate.

This makes the screen deliberately conservative: a candidate that wins only because its utilization is smaller, while raw prediction accuracy does not improve, is **not promoted by this no-download 200k screen**.

That conservative restriction is necessary because the standard report does not expose enough target-variance information to remove the unequal-multiplier MC bias.

It is not a statement that the official competition metric requires raw MSE improvement. It is a limitation of this low-fidelity local screen.

---

## 10. Statistical audit — 8 roots × 3 MLPs

The preregistered roots remain:

\`388001, 388002, 388003, 388004, 388005, 388006, 388007, 388008\`.

For each endpoint separately, use the eight root-suite means.

For \(D\in\{D^{adj},D^{raw}\}\):

\[
U95_D
=
\bar D+t_{0.95,7}\frac{s_D}{\sqrt8}.
\]

The arithmetic is correct.

Interpretation must be narrow:
- engineering one-sided root-suite summary;
- not exact contest-distribution coverage;
- not a leaderboard p-value.

The eight deterministic pseudorandom roots do not prove the exact normal-i.i.d. assumptions of a Student-t interval.

### 7/8 sign condition

R388's sign guard remains valid as a preregistered robustness filter:

\[
P(K\ge7\mid p=1/2)=9/256\approx0.03516.
\]

For the corrected gate, use **adjusted root signs** as the primary sign count and also require the raw endpoint to have at least 7/8 negative roots.

### 24-row medians

Report both adjusted and raw 24-row medians descriptively.

Do not treat the 24 rows as independent inferential replicates.

---

## 11. Multiplicity and selection bias

For one candidate/configuration frozen before any panel result, requiring multiple conditions **conjunctively** does not need Bonferroni correction merely because several gates must all pass.

The material multiplicity risk is adaptive selection:
- multiple R385 shell counts,
- fallback variants,
- code revisions,
- thresholds,
- multiple candidate families,
- choosing the best after seeing these roots.

If any candidate/config changes after viewing any of the eight root suites, the panel is burned for confirmatory use.

A descendant candidate needs a **fresh preregistered root panel** before promotion.

Do not stop early after favorable roots and do not replace a difficult root.

---

## 12. Failure handling — correction required

R388 explicitly prohibited candidate failures but did not symmetrically prohibit control failures.

That is insufficient.

A valid GO requires zero failures in **both arms** across all 48 arm-MLP evaluations.

Require for every row:
- no estimator/prediction error;
- no non-finite/shape error;
- \`budget_exhausted == false\`;
- \`time_exhausted == false\`;
- \`residual_wall_time_exhausted == false\`;
- \`combined_budget_exhausted == false\`.

A genuine failure in either arm blocks GO.

A demonstrated infrastructure corruption may justify rerunning the **same entire root pair** under the identical frozen sources/environment. Never substitute a new root.

Process exit code alone is insufficient because budget/time exhaustion can still yield a completed report.

---

## 13. Exact corrected execution protocol

For each of the 8 roots, run exactly two fresh processes, frozen control and frozen candidate, with identical non-estimator flags:

- \`--runner local\` or \`--runner subprocess\`, but the same runner in both arms;
- \`--n-mlps 3\`;
- \`--n-samples 200000\`;
- \`--seed <ROOT>\`;
- \`--flop-budget 2199023255552\`;
- \`--lambda-flops-per-second 0\`;
- \`--wall-time-limit 120\`;
- \`--setup-timeout 5\`;
- \`--residual-wall-time-limit 0.4\`;
- \`--format json\`.

Freeze before result inspection:
1. parent commit/path/blob + executed-file hash if available;
2. candidate commit/path/blob + executed-file hash;
3. WhestBench commit/version;
4. FlopScope version/backend;
5. Python/host/runtime fingerprint;
6. exact argv for all 16 runs;
7. explicit thread/BLAS configuration if any.

Pairing checks per root:
- same root;
- same 3 \`mlp_index\`;
- same 3 \`mlp_name\`;
- same width/depth;
- same toolchain/runtime controls;
- same exact non-estimator argv;
- zero failure flags in both arms.

Because \`run_config\` omits \`n_samples\`, the command record is mandatory.

---

## 14. Corrected GO / FAIL gate

A frozen R385/R391 candidate gets:

\`ENGINEERING_SCREEN_GO_TO_HIGHER_FIDELITY_VALIDATION\`

only if **all** conditions hold:

1. candidate and frozen parent hashes/config were fixed before any panel result;
2. all eight roots × three MLPs completed in both arms;
3. pairing integrity passes for every root;
4. no failures in either arm;
5. **primary adjusted endpoint:** \(U95_{adj}<0\);
6. at least 7/8 root-suite adjusted deltas are <0;
7. median of 24 adjusted per-network deltas is <0;
8. **mandatory raw guard:** \(U95_{raw}<0\);
9. at least 7/8 root-suite raw deltas are <0;
10. median of 24 raw per-network deltas is <0;
11. no candidate/configuration selection or tuning used these same roots.

This gate explicitly prevents "lower FLOPs alone" from qualifying as a pass.

### Classification on failure

- adjusted conditions fail: \`ENGINEERING_SCREEN_NO_GO_ADJUSTED\`;
- adjusted passes but raw guard fails: \`ENGINEERING_SCREEN_NO_GO_LOW_FLOP_ONLY_OR_MC_BIAS_RISK\`;
- candidate operational failure: \`ENGINEERING_SCREEN_FAIL_OPERATIONAL_CANDIDATE\`;
- parent operational failure: \`ENGINEERING_SCREEN_FAIL_OPERATIONAL_CONTROL\`;
- pairing mismatch: \`ENGINEERING_SCREEN_FAIL_PAIRING_INTEGRITY\`;
- adaptive reuse/tuning: \`ENGINEERING_SCREEN_EXPLORATORY_PANEL_BURNED\`.

---

## 15. What GO can legitimately claim

A clean corrected GO supports only:

- on the 24 preregistered generated 1024×16 networks, the frozen candidate had lower **observed budget-adjusted score** than the frozen parent according to the root-suite engineering gate;
- the same candidate also had lower **raw final-layer MSE** under the paired 200k target protocol, ruling out a promotion based solely on lower FLOPs;
- sampled runs had no local FLOP/wall/residual/validation failures;
- the candidate deserves higher-fidelity fixed-target validation.

It does **not** establish:
- an unbiased estimate of the production adjusted-score delta;
- R209 Mini-100 improvement;
- public-50 or sealed/full improvement;
- leaderboard score/rank/gap;
- exact grader timing;
- 8 GB compliance under \`--runner local\`;
- universal improvement over the contest distribution.

The adjusted endpoint remains contaminated by unequal-multiplier 200k target noise; the raw guard makes the screen conservative enough for promotion, not official enough for a score claim.

---

## 16. Final verdict

### Seed/network/target pairing

**PASS.**

Same explicit root + same \`n_mlps=3\` + same explicit \`n_samples=200000\` + same frozen toolchain/environment genuinely pairs generated networks and MC target streams.

### Original R388/R391 gate

**FAIL.**

Material corrections required:
- primary endpoint must be the official adjusted score, not raw MSE alone;
- adjusted-score target-noise bias must be acknowledged;
- raw-MSE improvement must remain a mandatory anti-artifact guard at N=200k;
- failures must be prohibited in both arms;
- exact argv must be retained because JSON omits \`n_samples\`;
- root suites, not 24 rows, are the primary uncertainty units;
- adaptive reuse burns the panel.

### Corrected R393 gate

**PASSABLE AS A NO-DOWNLOAD ENGINEERING SCREEN ONLY.**

No score or leaderboard claim follows.

---

## 17. Execution accounting

- estimator/generated-network/benchmark runs: **0**
- installs: **0**
- downloads: **0**
- dataset access: **0**
- Actions: **0**
- AIcrowd login/auth: **0**
- submission: **0**
- R320/main/PR/control/queue edits: **0**
- repository output: exactly this Markdown report.
