# R309 — grader/toolchain delta audit (source-only)

Date: 2026-09-24  
Repository base: `tim8es/arc-whitebox@4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
Report-only branch: `review/r309-toolchain-delta-audit-20260924`

## Scope and method

This audit compares only immutable official GitHub tags/commits and source diffs for the Phase-2 version gap:

- grader pair reported by the official starter kit: `whestbench==0.16.0`, `flopscope[server]==0.12.0`;
- local pair used by the starter kit and recorded by R209: `whestbench==0.16.1`, `flopscope==0.12.1+np2.4.6`.

No package/data download, install, import, execution, benchmark, GitHub Actions, holdout/full data, submission, scorer run, or PR/main/control mutation was performed. R305's manifest search was not repeated. The method was: dereference annotated tags to commits; compare tag-to-tag source; compare exact Git blob identities for evaluator-critical modules; inspect only the changed source; statically scan the frozen R209 V25 and R223 candidate source for affected FlopScope APIs.

## Immutable pins

### Official starter-kit statement

- Starter-kit commit: https://github.com/AIcrowd/whest-starterkit/commit/5eb9aa1455fcb3216af55994bdf25dc242b95797
- `pyproject.toml` blob: `2c1d562a2073046d6912868184b52c8c593d23c5`
- Immutable file: https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/pyproject.toml

That file pins the local floors to `whestbench>=0.16.1,<0.17.0` and `flopscope>=0.12.1,<0.13.0`, and explicitly states that the grader is on `whestbench v0.16.0` with `flopscope[server]==0.12.0`.

### whestbench tags

| tag | annotated-tag object | commit |
|---|---|---|
| `v0.16.0` | `714bedbdd306b6d4eaf15d1e9ec550fe810b9a39` | `8f0cb19a92eae7f88139e2f3810a392cf7a5b95e` |
| `v0.16.1` | `66526b4c80d9aea6af981c7a0f92e9ec76c57238` | `4d08668b485c8a7d25a105c3c00d2f4fc2538f18` |

Commits:
- https://github.com/AIcrowd/whestbench/commit/8f0cb19a92eae7f88139e2f3810a392cf7a5b95e
- https://github.com/AIcrowd/whestbench/commit/4d08668b485c8a7d25a105c3c00d2f4fc2538f18

The `v0.16.0...v0.16.1` diff changes only `CHANGELOG.md`, `docs/reference/rounds.md`, `pyproject.toml`, `src/whestbench/budget.py`, `tests/test_sampling_cost.py`, and `uv.lock`. The release adds a published Monte-Carlo-per-sample reference helper and raises the FlopScope floor; it does not alter the direct estimator score/evaluator modules.

Exact evaluator-critical blob equality:

| behavior | path | 0.16.0 blob | 0.16.1 blob | status |
|---|---|---|---|---|
| scoring | `src/whestbench/scoring.py` | `9cf7653a0267c4d048617c9045ac8be127f3c8bf` | same | COMPATIBLE |
| seed derivation | `src/whestbench/seeds.py` | `d04431aca4643a45831d22751a4f6d49d6467435` | same | COMPATIBLE |
| runner | `src/whestbench/runner.py` | `75636c28fa3eabc6047e1c981f34b6a0501ba8f3` | same | COMPATIBLE |
| subprocess evaluator | `src/whestbench/subprocess_worker.py` | `33f9d48793e67dd95180aadbcdd024720019348e` | same | COMPATIBLE |
| reporting | `src/whestbench/reporting.py` | `343bc9af5b6c1e942e5c469fac8cf909b6406cc2` | same | COMPATIBLE |
| protocol | `src/whestbench/protocol.py` | `fd03c7a79d8fa797fb910394de811edb4f02203b` | same | COMPATIBLE |

Immutable examples:
- scoring: https://github.com/AIcrowd/whestbench/blob/8f0cb19a92eae7f88139e2f3810a392cf7a5b95e/src/whestbench/scoring.py
- seeds: https://github.com/AIcrowd/whestbench/blob/8f0cb19a92eae7f88139e2f3810a392cf7a5b95e/src/whestbench/seeds.py
- runner: https://github.com/AIcrowd/whestbench/blob/8f0cb19a92eae7f88139e2f3810a392cf7a5b95e/src/whestbench/runner.py

The only evaluator-adjacent source blob that changes is `budget.py`:
- 0.16.0: `73c25ce6c4a49ee90095710c213465c9579e4441`
- 0.16.1: `6586f12d178e0136420cb282535663f1faad5abc`
- additive implementation commit: https://github.com/AIcrowd/whestbench/commit/5f2b2a3ba6b0549e13e9b625dfa74d53c2c344b8

That commit adds `dtype_aware_billing` metadata and `mc_flops_per_sample()/mc_samples_at_budget()/mc_at_bm()` reference helpers. The pre-existing Phase-2 round constants and direct score path remain: `B=2**41`, `lambda=0`, residual cap `0.4 s`, predict cap `120 s`, gated residual mode. Therefore the MC-reference addition is **COMPATIBLE** for R209/R223 direct scoring; it changes a published baseline/reference helper, not the estimator score formula.

### flopscope tags

| tag | annotated-tag object | commit |
|---|---|---|
| `v0.12.0` | `5c8bf6a8d2449a1d9e5f676eec72576485b5300d` | `2b8682e354379c50bc24145675356b8bb87fe6b3` |
| `v0.12.1` | `e683fd35c74bde24240c1b8c3fb3d8b1e8e7e10e` | `b599f015b0bc005b1edb6d7a1b10e0814675e693` |

Commits:
- https://github.com/AIcrowd/flopscope/commit/2b8682e354379c50bc24145675356b8bb87fe6b3
- https://github.com/AIcrowd/flopscope/commit/b599f015b0bc005b1edb6d7a1b10e0814675e693
- implementation change: https://github.com/AIcrowd/flopscope/commit/260a1289b3847ebbccc37f3e12659eadd8a10366

Relevant before/after blobs:

| path | 0.12.0 blob | 0.12.1 blob |
|---|---|---|
| `src/flopscope/_array_ops.py` | `51e27ecfebe5c05e3be7b70a4cd127c570a0e0df` | `d112b1e96e50cfdf0674c3230d291b622191b86d` |
| `src/flopscope/_symmetric.py` | `ed9cfcfd47fd7340e4d11f36b913103d8ca82269` | `73c796835c586fcdb5c763bc30dd7ce4cb7277a4` |
| `src/flopscope/_symmetry_utils.py` | `8d63f4883152cb8f8516d079c052d9859ccda693` | `6d9a489e868bfb06bf049429acee4cab6a2cfaf6` |
| `src/flopscope/numpy/random/__init__.py` | `b2b892ffe678f3e67a480b38d7b90e544a5d4166` | `629b1131c581ae33f56055b2c8c4ee7c98967618` |
| `src/flopscope/_registry.py` | `af61edaa3f6b1438b72fb730096f6110c040cd52` | `de7388e5649224360ca3fa8e5f62b4ad5ebcc596` |

## Behavior classification

| behavior | status | source-backed effect |
|---|---|---|
| whestbench score formula / aggregation | **COMPATIBLE** | Exact same `scoring.py` blob. Valid rows use final-layer MSE times `max(0.1,C/B)`; failures force multiplier 1; aggregate remains arithmetic mean. |
| whestbench estimator seed derivation | **COMPATIBLE** | Exact same `seeds.py` blob. Protocol-3 uses the third child of `SeedSequence(input_seed).spawn(3)`; protocol-4 keyed derivation is also unchanged. |
| FlopScope `default_rng(seed)` wrapper used by V25 | **COMPATIBLE** | The `default_rng` source excerpt is byte-identical between 0.12.0 and 0.12.1. R209 V25 stores `default_rng(ctx.seed)` in setup but never reads that field afterward, so this path cannot change its predictions or FLOPs. |
| whestbench runner/evaluator/failure handling | **COMPATIBLE** | `runner.py`, `subprocess_worker.py`, `protocol.py`, and `scoring.py` blobs are identical. |
| Phase-2 residual-cap rule | **COMPATIBLE** | The same evaluator logic zeros output and flags failure when measured residual time exceeds 0.4 s; Phase-2 `lambda=0`, so residual time is gated, not priced. |
| exact residual pass/fail outcome on another runtime | **UNKNOWN** | The cap logic is identical, but measured wall time is runtime/environment dependent. Source diff alone cannot reproduce R209's exact residual times or V29's exact 57/100 failure count. |
| generic 0.12.0→0.12.1 FLOP accounting | **NOT_COMPATIBLE** | One real price-affecting path exists: `full/full_like` with non-scalar `fill_value` no longer receives shape-inferred symmetry in 0.12.1, so downstream ops can bill more densely. The official release explicitly identifies this as the only price-moving change. |
| `as_symmetric` charge | **COMPATIBLE** | Official implementation commit states its charge is unchanged. |
| `as_symmetric` value semantics on tolerance-only symmetric input | **NOT_COMPATIBLE** | 0.12.1 canonicalizes accepted data before attaching the symmetry tag; 0.12.0 can retain the small within-tolerance asymmetry. Predictions can therefore differ for code relying on that edge case, even when billed FLOPs do not. |
| default Reynolds `symmetrize` on enumerable groups | **COMPATIBLE** | Release explicitly says Reynolds default/result pricing is unchanged. |
| oversized Reynolds failure accounting / new `canonical-copy` mode | **NOT_COMPATIBLE** | 0.12.1 refuses an unenumerable Reynolds projection before charging and adds `canonical-copy`; 0.12.0 lacks those semantics/API. |
| `fnp.random.symmetric` ordinary default mode | **COMPATIBLE** | Existing default remains Reynolds; generic RNG methods are not changed. New mode/oversized-group behavior is the incompatible exception above. |

## R209 / R223 applicability

### R209 V25

Immutable prior evidence:
- R209 audit blob: `7fec90369227839a9902c7cceb9f3519acb66cb8`
- https://github.com/tim8es/arc-whitebox/blob/research/r209-e136-archive-evidence/research/R209_E136_ARCHIVE_EVIDENCE_AUDIT.json
- frozen V25 source blob: `195373a110215256b759d7c172ba8c923c62e5cc` in `504aldo/whest-p2-cumulant-k3`
- recorded local toolchain: Python 3.11.16, whestbench 0.16.1, flopscope 0.12.1+np2.4.6.
- recorded V25: 0/100 failures, adjusted score `8.170397440117225e-9`, mean effective compute `806303721965`, maximum residual `0.19043814401743475 s`.

Static scan of frozen V25:
- no `full(` / `full_like(` calls;
- no `symmetrize` or `fnp.random.symmetric`;
- two `flops.as_symmetric` calls:
  1. `fnp.eye(...)`, exactly symmetric by construction;
  2. `fnp.diagflat(K2v) + (K11 + K11.T) * 0.5`, explicitly symmetrized by construction.
- one `fnp.random.default_rng(ctx.seed)` assignment in setup; the stored field is never read later.

**R209 V25 source-semantic score portability: COMPATIBLE.** The whestbench scoring/evaluator/residual logic is byte-identical, the only 0.12.1 price-changing path is absent, and the V25 symmetry calls use inputs that are symmetric by construction while `as_symmetric` billing itself is unchanged.

**R209 V25 exact numeric replay under the grader runtime: UNKNOWN.** Source equivalence does not prove bit-identical floating output or wall-clock residual measurements on the grader because R209 records NumPy 2.4.6 locally while this audit does not have an immutable grader-side NumPy/build/runtime receipt. This is a verification gap, not evidence of a score-changing 0.16.0/0.12.0 patch.

### R209 V29 residual failures

The mechanism is **COMPATIBLE** (same 0.4-s gate and same evaluator source), but the exact failed-row set/count is **UNKNOWN** across runtimes because residual wall time is measured. R209's recorded 57/100 V29 residual failures must not be asserted to reproduce from source inspection alone.

### R223

The earlier R309 statement that R223 had no scientific panel result was stale. Current immutable control/evidence supersedes the attempt-1 terminal receipt used there:

- live `research/control-v2` state checked at revision **479**;
- R223 finish event revision **193** records attempt 6 as `SCIENTIFIC_REJECT`;
- attempt 6 queue run: `R223-v25-local-feed-attempt6-20260923`;
- GitHub Actions run/job recorded by independent R240 postflight: `35810427656` / `107020553482`, run attempt 1, completed/success;
- immutable R240 receipt: https://github.com/tim8es/arc-whitebox/blob/3b99fcaea2ef29b050612610ff04a8fc7a6886cd/research/r240/R240_RECEIPT.json, blob `f9f19b6313a5b302e2f1d6a40014a5d55ef5494a`, SHA-256 `e75ec5e2641df59887cf38520e9d9f3a449731fa5fcac481398433c4c4ac8bbd`;
- R242 integration receipt: https://github.com/tim8es/arc-whitebox/blob/b55b9ab2e3dd7ff58ea405704e8f63e86112d48d/research/r242/R242_INTEGRATION_RECEIPT.json, blob `ba7fb51a5b82009514797da85c3d517c2c3185fe`;
- normalized result: `research/results/R223-v25-local-feed-mini100.json`, blob `c8b617c43ff1145977c38e7e1cca6d23985ec392`, parent `R209-v25-mini100`.

Attempts 1–5 remained pre-panel infrastructure failures. **Attempt 6 executed exactly one public Phase-2 `mini:all-100` development panel**; R240 independently bound the immutable artifact, verified all 100 paired rows and failure semantics, and confirmed that this was the only candidate panel invocation.

Observed same-panel development result:

| metric | R209 V25 parent | R223 V25-LF candidate |
|---|---:|---:|
| rows | 100 | 100 |
| failures | 0 | 0 |
| mean raw MSE | `2.228303490170447e-8` | `2.2284993050902814e-8` |
| mean adjusted score | `8.170397440117226e-9` | `8.171116513490029e-9` |
| mean effective/measured compute | `806303721965` | `806303829485` |
| max residual | `0.19043814401743475 s` | `0.19380312699274782 s` |

The candidate is slightly worse on adjusted score: parent-minus-candidate mean adjusted delta is `-7.190733728024271e-13`. It improves exactly 50/100 networks; paired delta mean / SE is `-0.48188156603559223`.

Frozen R223 gates: **1, 2, 3, 8, 9, 10, 11 PASS; 4, 5, 6, 7 FAIL**. Specifically, candidate failures are zero and identity/provenance/cost/residual/one-run gates pass, while candidate mean raw MSE is not below parent, adjusted score is not <= 0.995× parent, fewer than 55/100 rows improve, and paired parent-minus-candidate mean is not >2SE. Verdict: **same-exposed-panel DEVELOPMENT NO-GO / SCIENTIFIC_REJECT; drop V25-LF under the frozen protocol**.

This observed score must not be conflated with competition evidence:

- **public Mini-100 development result: OBSERVED / COMPARABLE to the authenticated R209 parent on the same panel**;
- **R223 candidate source-level evaluator/FLOP semantics across 0.16.1/0.12.1 → 0.16.0/0.12.0: COMPATIBLE** for the affected APIs identified by this source audit;
- **exact numeric/timing replay under the grader pair/environment: UNKNOWN** — no exact grader-pair replay was executed here, and runtime/NumPy/timing differences remain unmeasured;
- **leaderboard rank / leaderboard score equivalence: NOT_COMPARABLE** from this Mini-100 development result;
- **final-100 or hidden/private split performance: NOT_COMPARABLE / UNKNOWN** because no such R223 evaluation is evidenced;
- **submission/competition outcome: NOT_COMPARABLE**; no submission claim follows from R223 attempt 6.

The attempt-6 frozen candidate blob recorded by R240 is `eb95d4ae46a031be5131eef8dd0909f2061b8749`; the comparator blob is `fd1ce8711f92bb123f69d7bcddb37bb0fec3b8b0`. Its affected-API scan remains the same relevant pattern as V25: no non-scalar `full/full_like`, no `symmetrize`/random-symmetric path, and the same two `as_symmetric` call shapes.

## Practical conclusion

The 0.16.1/0.12.1 local pair is not universally equivalent to grader 0.16.0/0.12.0: FlopScope 0.12.1 has real, narrowly scoped symmetry/value/accounting changes. However, the frozen R209 V25 and R223 candidate do not use the one documented price-moving `full/full_like(non-scalar)` path or the new canonical-copy/oversized-Reynolds paths. Their direct whestbench score, seed, evaluator, and residual-cap logic is unchanged at exact blob level, and their `as_symmetric` charge is unchanged.

Accordingly, there is **no source-level evidence that the patch-version gap materially changes R209 V25's adjusted score or the source-level accounting semantics applicable to the observed R223 V25-LF candidate**. The remaining portability uncertainty is runtime-level: exact floating behavior (including the grader's NumPy build/version) and measured residual wall time.

## Minimum future verification

To close the remaining UNKNOWN without expanding scope:

1. Obtain one immutable grader-environment receipt that records the exact NumPy version/build (or the full `flopscope.__version__` suffix and server environment) alongside the already stated whestbench/flopscope pair.
2. If exact score portability must be proven, perform one explicitly authorized offline/public Mini-100 replay of the frozen R209 V25 under the exact grader pair/environment, comparing per-MLP name/order, prediction/metric hashes where available, FLOPs, residual-failure flags, and adjusted scores against R209. No holdout/full/submission is needed.
3. R223 already has one authenticated public Mini-100 development result from attempt 6. If exact grader-pair portability of that observed result must be proven, perform only a separately authorized exact-pair replay; do not infer leaderboard, final-100, hidden/private, or submission performance from the existing development panel.

## Audit limits

This report makes no claim that all 0.12.0 and 0.12.1 programs are equivalent. It also does not turn source-level compatibility into a measured grader reproduction. No runtime package behavior was executed in R309.
