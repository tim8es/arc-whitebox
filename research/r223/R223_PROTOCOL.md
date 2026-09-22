# R223 — isolated V25 local-feed lambda development test

Date: 2026-09-22
Idempotency: `ARC-R223-V25-LOCAL-FEED-LAMBDA-20260922`
Branch: `research/r223-v25-isolated-improvement-20260922`
Central queue start: revision 87, run id `R223-v25-isolated-improvement-20260922`.

## 0. Goal and one frozen change

R223 tests exactly one algorithm-level delta from the strongest clean reproducible V25
method baseline:

> **V25-LF: normalized per-neuron K4->K3 feed lambda, with V25's scalar lambda transport,
> K4 use-side, source state, ranks, age gates and all other arithmetic unchanged.**

This is an accuracy-directed estimator change, not a runtime/affinity experiment and not
a cost-only optimization. The incremental arithmetic is O(n) per layer, so any adjusted
score gain must come from raw-MSE improvement rather than crossing or exploiting the 0.1B
score floor.

Forbidden:

- R218 affinity/runtime work;
- R219 dependence-carrier work;
- Strassen/V26-V29 cost engineering;
- rank/age/source sweeps;
- CountSketch H137 rescue;
- E142/E145 response-action integration;
- target fitting, per-network fitting, leaderboard fitting;
- canonical estimator edits;
- holdout/full/scorer/submission;
- paid or larger GitHub runners;
- rerun/rescue after the single panel result.

## 1. Frozen parent

Pinned public method source:

- upstream repository: `504aldo/whest-p2-cumulant-k3`;
- upstream commit: `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`;
- V25 git blob: `195373a110215256b759d7c172ba8c923c62e5cc`.

Immutable local evidence is R209's audited E136 V25 artifact:

- Actions run: `35544406064`;
- V25 job: `106167659234`;
- artifact id: `10617855153`;
- artifact ZIP SHA256:
  `820bf9368beac10ea537fc018c3c2185bbd310b9542603cbfa8309519c8e3e08`;
- report SHA256:
  `68683f9f2e8eca89a85fd18826998f5937d4770c2ce33bf6e6738fb236c8e5a3`;
- full canonical 100-row hash:
  `85472c4808bff7a83a9ca853688ad9068895b073bb1592fd0f364d82c112b13e`;
- index/metric runtime hash:
  `f5605b03d55808ac4afd7ff2de42c317b96ae20483551a2f7ddddb9d89cd680b`.

Exact parent panel/config:

- dataset: `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`;
- dataset SHA256:
  `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`;
- split: `mini`;
- streaming: true;
- first/all `100` mini MLPs in the archived order;
- names-order SHA256:
  `18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce`;
- width/depth: `1024 x 16`;
- flop budget: `2^41`;
- wall cap: `120 s`;
- residual cap: `0.4 s`;
- max threads: `1`.

Parent metrics:

- failures: `0/100`;
- mean raw final MSE: `2.228303490170447e-8`;
- mean adjusted score: `8.170397440117225e-9`;
- mean effective compute: `806303721965`;
- mean C/B: `0.36666448157347986`;
- max residual: `0.19043814401743475 s`.

The R223 workflow must download this exact parent artifact and verify both ZIP and report
hashes before the candidate panel run is accepted.

## 2. Immutable-history novelty screen

Public V25/V29 and project history already close:

- scalar lambda table/global-scale scans;
- V25 scalar per-MLP adaptive lambda;
- larger residual and D21-feedback ranks;
- lower shared/nested old-source ranks;
- CountSketch old-tier contraction H137 under its frozen identity;
- response-only old-D21 integration E142/E145;
- V29 Strassen/buffer repricing.

Search of project branches/code and the pinned public repository found no implemented
**per-neuron feed-local lambda** or `lambda vector` mechanism.

Primary V25 evidence is especially relevant:

- F68: removing the K4->K3 feed degrades raw MSE by roughly 4x; the feed carries the
  regeneration gain;
- regenerating the K4 diagonal is catastrophic, so the exact per-neuron diagonal must stay;
- F75/V25: a scalar lambda is adapted from the target-free online statistic
  `mean(dG)/mean(var)`;
- public sensitivity says lambda-table polishing is small, so R223 does not change the
  scalar transport coefficient. It uses already-computed per-neuron heterogeneity only at
  the accuracy-critical feed.

## 3. Frozen V25-LF rule

At a suite-shape layer where V25 has computed its pre-update diagonal

[
dG_0=t_g+lambda t_v
]

and the scalar online ratio

[
r=rac{operatorname{mean}(dG_0)}{operatorname{mean}(var)},
]

V25-LF keeps the existing scalar adaptation unchanged:

[
lambda'=lambda,operatorname{clip}(r/REF_R,0.5,2)^{BETA},
]

and keeps the exact same scalar-updated `dG`, `wk431`, and all other state.

For **only the K4->K3 birth-feed column scaling**, define

[
q_i=rac{dG_{0,i}}{var_i},
]

[
s_i=operatorname{clip}(q_i/r,0.5,2),
qquad
ar s=operatorname{mean}_i s_i,
]

[
lambda^{feed}_i=lambda'rac{s_i}{ar s}.
]

Then replace only

[
c1_i=w1_ilambda'
]

by

[
c1_i=w1_ilambda^{feed}_i.
]

All other V25 arithmetic remains byte-for-byte source-equivalent.

The clamp `[0.5,2]` is not newly tuned; it is exactly V25's existing safety interval.

No target, per-network error, panel score, or post-result statistic enters the rule.

## 4. Exact/static falsifier before panel

The same workflow must pass these target-free checks before accessing the mini panel:

1. pinned parent source blob identity is exact;
2. only the preregistered feed-local patch is present;
3. for constant `q_i/r = 1`, `lambda_feed_i == lambda'` exactly in float64 test code;
4. `mean(lambda_feed) == lambda'` within `2e-15` on deterministic heterogeneous
   synthetic vectors;
5. every scale lies inside the normalized image of the frozen clamp and all values are
   finite;
6. off-suite validation remains valid;
7. no code path reads a target.

Failure before panel => terminal protocol/implementation NO-GO; do not patch or retry.

## 5. Conservative FLOP envelope

R223 adds only O(n) vector arithmetic on the 14 noninitial/nonfinal feed-bearing layers.

Conservative extra charge per layer:

- `dG0 / var`: `n`;
- division by scalar `r`: `n`;
- clip: `n`;
- mean: `n`;
- normalization divide: `n`;
- multiply by scalar lambda: `n`.

Add a 4n reserve per layer for temporaries/accounting.

Frozen upper:

[
C_{extra}le 10 ncdot14
=143{,}360	ext{ FLOPs}.
]

Against the measured V25 parent:

[
C_{extra}/806{,}303{,}721{,}965
<1.78	imes10^{-7}.
]

Thus the score multiplier is effectively unchanged; R223 is not a below-floor FLOP play.

The candidate must still report actual flopscope counts for every network.

## 6. Free/existing compute gate

The repository is publicly visible. R223 uses only the standard
`ubuntu-24.04` GitHub-hosted runner.

GitHub's current official billing documentation states standard GitHub-hosted runners are
free for public repositories. Larger runners are explicitly forbidden.

Before execution the workflow must verify the repository remains public and record the
standard runner label. If this cannot be verified, stop with `INFRA_ERROR_COMPUTE_NOT_PROVEN_FREE`.

## 7. Sole bounded development test

If all preflight gates pass, run exactly one candidate test with the exact R209 parent
panel/config:

`whest run --dataset hf://aicrowd/arc-whestbench-public-2026@v2-phase2 --split mini
--streaming --n-mlps 100 --runner local --flop-budget 2199023255552
--wall-time-limit 120 --residual-wall-time-limit 0.4 --max-threads 1`.

No parent rerun is permitted; compare against the immutable parent report artifact.

Retain:

- complete candidate `report.json` with all 100 per-network rows;
- exact parent report copied from the verified R209 artifact;
- per-network paired comparison JSON;
- environment/version files;
- source hashes;
- candidate estimator hash;
- artifact checksum manifest;
- aggregate MSE/FLOPs/runtime/failures/adjusted score.

## 8. Frozen scientific gates

Let parent values come only from the verified R209 artifact.

All gates must pass for DEVELOPMENT GO:

1. exact 100-name/order identity with parent;
2. dataset SHA identical;
3. candidate failures = 0;
4. candidate mean raw MSE < `2.228303490170447e-8`;
5. candidate mean adjusted score <=
   `0.995 * 8.170397440117225e-9 = 8.129545452916639e-9`
   (at least 0.5% adjusted improvement);
6. candidate improves adjusted score on at least 55/100 networks;
7. paired per-network adjusted-score delta
   `parent-candidate` has positive mean greater than `2 * SE(delta)`;
8. candidate mean C/B <= parent C/B + `1e-5`;
9. max residual < `0.4 s`;
10. exact candidate source/config/provenance gates pass;
11. only one candidate panel run exists.

Any failed gate => **R223 SCIENTIFIC_REJECT / DROP V25-LF**.

A GO would be a same-exposed-panel development result only. It does not authorize
canonical edits, leaderboard claims, holdout, scorer, or submission.

## 9. Run discipline

Immutable order:

1. central queue start — already published at revision 87;
2. this protocol;
3. pinned candidate source + focused static tests;
4. one arm commit;
5. exactly one public-mini-100 candidate run on verified-free standard Actions compute;
6. immutable result/receipt;
7. central queue finish.

No rerun, repair, alternate local scaling, clamp change, panel subset, or second seed.
