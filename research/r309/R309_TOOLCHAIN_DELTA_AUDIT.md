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

Immutable terminal evidence:
- R223 terminal receipt blob: `a2ea83717b979b40e8ec13703c7465e0f50189ba`
- https://github.com/tim8es/arc-whitebox/blob/research/r223-v25-isolated-improvement-20260922/research/r223/R223_TERMINAL_RECEIPT.json
- frozen candidate blob: `a09ec139bc7399f169ace02cf587d55bc1c8771b`
- frozen comparator blob: `fd1ce8711f92bb123f69d7bcddb37bb0fec3b8b0`

R223 terminated at a pre-panel provenance guard; no candidate validation or scientific panel run started and no candidate score exists. Therefore **R223 actual score portability: UNKNOWN (no score exists to port)**.

The frozen candidate's affected-API scan matches V25: no non-scalar `full/full_like`, no `symmetrize`/random-symmetric path, and the same two `as_symmetric` call shapes. Thus **R223 candidate evaluator/FLOP semantics are COMPATIBLE at source level** between these patch pairs, but this is not a scientific result and does not convert R223's INFRA_ERROR into a score.

## Practical conclusion

The 0.16.1/0.12.1 local pair is not universally equivalent to grader 0.16.0/0.12.0: FlopScope 0.12.1 has real, narrowly scoped symmetry/value/accounting changes. However, the frozen R209 V25 and R223 candidate do not use the one documented price-moving `full/full_like(non-scalar)` path or the new canonical-copy/oversized-Reynolds paths. Their direct whestbench score, seed, evaluator, and residual-cap logic is unchanged at exact blob level, and their `as_symmetric` charge is unchanged.

Accordingly, there is **no source-level evidence that the patch-version gap materially changes R209 V25's adjusted score or the accounting that a future R223 run would receive**. The remaining portability uncertainty is runtime-level: exact floating behavior (including the grader's NumPy build/version) and measured residual wall time.

## Minimum future verification

To close the remaining UNKNOWN without expanding scope:

1. Obtain one immutable grader-environment receipt that records the exact NumPy version/build (or the full `flopscope.__version__` suffix and server environment) alongside the already stated whestbench/flopscope pair.
2. If exact score portability must be proven, perform one explicitly authorized offline/public Mini-100 replay of the frozen R209 V25 under the exact grader pair/environment, comparing per-MLP name/order, prediction/metric hashes where available, FLOPs, residual-failure flags, and adjusted scores against R209. No holdout/full/submission is needed.
3. R223 needs no "portability replay" until a scientific run is authorized, because there is no existing R223 candidate score. If such a run is later authorized, use the same exact grader pair/environment from the outset rather than translating a 0.16.1/0.12.1 result afterward.

## Audit limits

This report makes no claim that all 0.12.0 and 0.12.1 programs are equivalent. It also does not turn source-level compatibility into a measured grader reproduction. No runtime package behavior was executed in R309.
