# R398 — R385 decision memo

**Date:** 2026-09-30  
**Decision:** **CONTINUE — one bounded implementation/synthetic gate only**  
**Scope:** synthesis of completed R395/R396/R397 plus current first-party Phase-2 rules. No benchmark/data download, install, run, submission, leaderboard claim, or control-plane edit.

## 1. Current Phase-2 state

Current first-party starter-kit heads checked for this memo:

- `AIcrowd/whest-starterkit@5eb9aa1455fcb3216af55994bdf25dc242b95797`
- `AIcrowd/whestbench@4794ce8673c1221bdb245b19e933ae0afd7ffa3c`

Official scoring source:

- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/concepts/scoring-model.md
- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/rounds.md

For a valid MLP row,

[
s_m=mathrm{MSE}_{mathrm{final},m}max!left(0.1,rac{C_m}{B}ight),
qquad C_m=F_m,
]

and the leaderboard metric is the mean of (s_m) over the evaluated MLPs. The Phase-2 budget is

[
B=2^{41}=2{,}199{,}023{,}255{,}552.
]

The 10% compute-discount floor is reached at (C/Ble0.1). Phase 2 also has a 120 s per-`predict()` wall cap, a hard 0.4 s residual cap, a 5 s setup cap, and an 8 GB solution-process memory cap.

Official Phase-2 launch / current dates:

- https://discourse.aicrowd.com/t/phase-2-of-the-arc-white-box-estimation-challenge-is-live/18197

The organizer's current key dates are:

- **registration deadline:** 2 October 2026, 23:59 UTC;
- **team-freeze deadline:** 2 October 2026, 23:59 UTC;
- **Phase-2 submission deadline:** 17 October 2026, 23:59 UTC;
- algorithmic-contribution write-up deadline: 24 October 2026, 23:59 UTC.

The same official post states width 1024, depth 16, (2^{41}) FLOPs/MLP, 120 s wall, 0.4 s residual, 8 GB memory, 10 submissions/team/day, and that Phase-2 numerical computation must run through FlopScope.

## 2. What R395/R396/R397 actually establish

### R395 — execution blocked, not scientific NO-GO

Artifact:

- https://github.com/tim8es/arc-whitebox/blob/bd3782c73c23b8f5b6847bfd2bed702ca575a63f/research/r395/R395_R385_MULTISHELL_SCREEN.md
- head `bd3782c73c23b8f5b6847bfd2bed702ca575a63f`
- blob `621cb5245a655a65a98366b6affead9728d5c5d2`

R395 produced **no metric measurement**. Its execution environment lacked:

- a local ARC checkout;
- R385/R383/R376/R388 source files;
- frozen V25/R223 baseline code;
- `whest` / `whestbench`;
- `flopscope`;
- inspectable existing sound affine-bound code.

Therefore R395's STOP was an **environment/toolchain-access blocker**, not evidence that R385 is inaccurate or infeasible.

This distinction matters: the next gate still needs **no Mini/public/private/holdout benchmark-data download**. It does, however, require a pre-provisioned local checkout and already-available WhestBench/FlopScope/baseline/affine-bound code. "No benchmark-data download" does not mean "no code/toolchain is needed."

R395 also records the handoff: it superseded unstarted R394; no duplicate R394 implementation should resume.

### R396 — all-in Fast-Lin cost is plausible, but not at the 10% floor

Artifact:

- https://github.com/tim8es/arc-whitebox/blob/22e63b7f3abd8e5252bd18724e263b7e5550eb7f/research/r396/R396_R385_AFFINE_PAIR_COST_AUDIT.md
- head `22e63b7f3abd8e5252bd18724e263b7e5550eb7f`
- blob `9a32fa70b2b5f327a6ce88c402fae893033878a1`

R396 corrects the earlier R385/R376 affine-cost premise. A full all-output Fast-Lin construction requires 120 dense 1024×1024 GEMMs across all target layers. Its literal all-in (K=64) schedule is

[
C_{mathrm{R396}}=258{,}427{,}298{,}702
]

FLOPs, giving

[
u=rac{C}{2^{41}}
=0.11751912948147947.
]

This is comfortably below the hard budget and has no source-based memory NO-GO, but it is **above** the 0.1 score floor.

Exact break-even implication:

[
rac{u}{0.1}=1.1751912948147947.
]

So the compute multiplier is **17.51912948147947% larger** than the floor multiplier. To tie an otherwise comparable method that is already at the 0.1 floor, R385 at this utilization must have raw final-layer MSE no more than

[
rac{0.1}{u}
=0.8509252956622657
]

times that method's raw MSE — i.e. it needs at least **14.90747043377343% lower raw MSE** to offset the multiplier penalty.

That is a score-mechanics break-even calculation, not a measured R385 accuracy result.

R396's remaining unknowns are measured wall/residual behavior and machine-level numerical soundness.

Primary method sources used by R396:

- Fast-Lin: https://proceedings.mlr.press/v80/weng18a.html
- CROWN: https://proceedings.neurips.cc/paper/2018/hash/d04863f100d59b3eb688a11f95b0ae60-Abstract.html

### R397 — shell certificate survives, with numerical corrections

Artifact:

- https://github.com/tim8es/arc-whitebox/blob/12ff1cfbded8e82dd0f76bd517d35d3007fb7627/research/r397/R397_R385_MULTISHELL_CERTIFICATE_AUDIT.md
- head `12ff1cfbded8e82dd0f76bd517d35d3007fb7627`
- blob `1e82a8a017c5fd2ffd9730b63c97e246455edaa5`

R397 finds:

- shell probabilities/nesting: PASS in real arithmetic;
- positive-homogeneity scaling of one unit-box affine pair across shells: PASS;
- upper aggregation: PASS;
- exact cheap (J_k): not established;
- deterministic analytic lower bound on (J_k): PASS in real arithmetic;
- stable/cancellation-resistant lower path exists using (Phi(-t)), `log1p`, `expm1`, and a Mills-ratio lower construction;
- strict certificate-radius improvement over R376 is valid when
  [
  Delta U_{m shell}+L_{m MS}>0.
  ]

The shell readout is not the cost blocker. R397's safer (K=64) readout is only about 10.52M FLOPs. For all-in planning, however, **R396's audited affine-builder cost supersedes R397's conditional reuse of the old 138.5B affine envelope**.

## 3. Decision

### Recommendation: **CONTINUE**

Reason:

1. R395 supplied no negative metric result; it only exposed a missing execution environment.
2. R396 finds no FLOP or memory NO-GO: a source-derived Fast-Lin realization is about 11.75% of the hard budget.
3. R397 preserves the multi-shell certificate mathematically after specific stable-numerics corrections.
4. The remaining questions are precisely the ones a bounded implementation/synthetic screen can falsify.

This is **not** a recommendation to download benchmark data or submit.

## 4. One bounded falsifiable gate

**R398-G1 — generated-network implementation gate**

Run only in an environment where, **before execution**, all of the following are already present locally:

- exact ARC checkout with R385/R396/R397;
- frozen V25/R223 control source;
- current compatible `whestbench` and `flopscope`;
- an inspectable sound affine-bound implementation capable of forming R385 (ell,u);
- no need to clone/fetch/install anything.

Implement the R397-stable shell formulas and the R396-audited Fast-Lin-style affine path, then run exactly the existing no-dataset paired screen shape:

- 8 fixed root seeds;
- 3 generated 1024×16 MLPs/root;
- frozen R385 candidate and frozen V25 control on identical seeds/flags;
- no `--dataset`;
- explicit 200,000 local target samples;
- same runner/toolchain for both arms.

**PASS / continue to higher-fidelity validation only if every condition below holds:**

1. zero estimator/validation/budget/time/residual failures in **both** arms;
2. all candidate outputs and interval terms are finite and fail-closed checks satisfy (L_{m MS}le U_{m MS});
3. candidate measured utilization is **≤ 0.12** on every generated MLP (a preregistered engineering ceiling around R396's 0.117519 estimate, not a contest rule);
4. residual time is <0.4 s and wall time <120 s on every candidate MLP;
5. 8 GB compliance is actually enforced or measured; otherwise the gate is incomplete;
6. use **raw final-layer MSE paired deltas** as the accuracy endpoint: the one-sided root-level engineering upper bound is <0 and at least 7/8 root means are negative.

Do **not** use local adjusted-score improvement as the confirmatory endpoint: at different compute multipliers, finite-sample target noise does not cancel in the same way as raw paired MSE.

**Any failed condition => STOP R385 as the prioritized implementation path.**  
**All conditions pass => CONTINUE only to a separately authorized fixed-target/higher-fidelity validation.**

No leaderboard or contest-improvement claim follows from this gate.

## 5. Explicit unknowns

Still unknown after R395/R396/R397:

- **measured R385 score:** none;
- **measured raw MSE:** none;
- **0.4 s residual compliance:** unmeasured;
- **120 s wall compliance:** unmeasured;
- **8 GB runtime compliance:** unmeasured;
- **measured FlopScope all-in cost:** unmeasured; 11.7519% is static/source-derived;
- **finite-precision formal enclosure:** unvalidated — real-arithmetic soundness does not itself prove outward-rounded machine-level bounds;
- **quality/tightness of the realized affine bounds on generated/fixed networks:** unmeasured;
- **R393:** pending for decision-chain acceptance/integration in this memo; do not treat it as closing the above execution unknowns;
- **fixed Mini/public/private/holdout performance:** not measured and not required for R398-G1.

## 6. Source URLs

Current first-party ARC/Whest sources:

1. Phase-2 launch, limits and dates:  
   https://discourse.aicrowd.com/t/phase-2-of-the-arc-white-box-estimation-challenge-is-live/18197
2. Starter-kit scoring model:  
   https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/concepts/scoring-model.md
3. Current round parameters:  
   https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/rounds.md
4. Current estimator contract:  
   https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/estimator-contract.md
5. Phase-2 allowed-code rules:  
   https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/concepts/allowed-code.md

Internal evidence:

- R395: https://github.com/tim8es/arc-whitebox/blob/bd3782c73c23b8f5b6847bfd2bed702ca575a63f/research/r395/R395_R385_MULTISHELL_SCREEN.md
- R396: https://github.com/tim8es/arc-whitebox/blob/22e63b7f3abd8e5252bd18724e263b7e5550eb7f/research/r396/R396_R385_AFFINE_PAIR_COST_AUDIT.md
- R397: https://github.com/tim8es/arc-whitebox/blob/12ff1cfbded8e82dd0f76bd517d35d3007fb7627/research/r397/R397_R385_MULTISHELL_CERTIFICATE_AUDIT.md

## 7. No-action accounting

- benchmark/generated-network runs: 0;
- dataset downloads/access: 0;
- installs: 0;
- submissions/uploads: 0;
- Actions: 0;
- main/R320/PR/control/queue edits: 0;
- repository output: exactly this one research Markdown report.
