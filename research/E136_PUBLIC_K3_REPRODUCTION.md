# E136 — public K3 baseline reproduction

Status: **PUBLIC BASELINE REPRODUCTION / NOT A WIN CLAIM**

This lane reproduces the published Phase-2 K=3 estimator from team 504aldo as a
working, inspectable base for later research. It is not a claim that the public
baseline is optimal or that it wins the challenge.

## Pinned primary sources

- Upstream MIT repository, pinned commit:
  https://github.com/504aldo/whest-p2-cumulant-k3/tree/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45
- Published forum write-up:
  https://discourse.aicrowd.com/t/everything-we-tried-a-factorized-k-3-cumulant-propagation-estimator-at-0-25-x-b-where-its-flops-go-and-25-measured-dead-ends-team-504aldo-rank-10/18218
- Official challenge rules:
  https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/challenge_rules
- Official starter-kit reproduction path:
  https://github.com/AIcrowd/whest-starterkit
- Official WhestBench public dataset revision:
  `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`

Upstream commit at intake: `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.

Vendored upstream Git blob identities:

- `estimators/estimator_v25.py`: `195373a110215256b759d7c172ba8c923c62e5cc`
- `estimators/estimator_v29.py`: `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`
- `LICENSE`: `2c843327a87b547245b566f02391295ba71ad26a`

The vendored copies live under `methods/public_504aldo/` and retain the upstream
MIT license.

## Published targets to reproduce

The upstream write-up reports:

| path | raw final-layer MSE | C/B | role |
| --- | ---: | ---: | --- |
| V25 | about `2.13e-8` leaderboard; `2.23e-8` 100-MLP public mini | `0.3667` | same estimator arithmetic without Strassen |
| V29 | about `2.13e-8` leaderboard; `2.275e-8` on the author's 8 local dumps | `0.2526` steady-state public path | cost-engineered path |

The write-up states that V26-V29 do not change the estimator arithmetic and that
their gains are cost engineering. Therefore the important reproduction checks
are:

1. V25 and V29 both validate and execute at Phase-2 shape.
2. Their predictions/raw error agree closely on the same public MLPs.
3. V25 has no Strassen implementation.
4. V29 contains the published Strassen-Winograd + pooled-buffer cost path and
   approaches the published `C/B ~= 0.2526` on steady-state suite-shaped runs.
5. Non-suite validation shapes use the generic fallback rather than assuming
   `1024 x 16`.

The forum post originally described Strassen as awaiting sponsor clarification.
A later author update records that the sponsor confirmed on 2026-09-11 that
Strassen-Winograd expressed as flopscope operations is permitted with no
recursion-level limit. E136 nevertheless keeps V25 as the non-Strassen
reference so later work does not depend on that cost-engineering choice.

## Phase-2 restriction audit

The official Phase-2 environment requires participant computation to go through
flopscope, with Python stdlib allowed for control/bookkeeping. The public
write-up additionally records the practical limits used by this estimator:
suite shape `1024 x 16`, per-MLP budget `2^41`, 5 s setup, 0.4 s residual
cap, 8 GB solution-process memory, and a non-suite smoke shape.

E136 statically checks the vendored files for forbidden direct imports such as
NumPy/SciPy/Torch and dynamically runs `whest validate`. The validator's
small non-suite MLP is also the shape-fallback test.

No holdout, private scorer, submission, or full split is used by this lane.

## Reproduction run

The E136 Actions workflow performs, in order:

1. exact vendored-blob and license audit;
2. `whest validate` for V25 and V29;
3. a streaming local run on the first three MLPs of the official public
   `v2-phase2/mini` split for V25;
4. the same three public MLPs for V29;
5. artifact upload of validation/run logs and a machine-readable static receipt.

The streaming path is intentional: the official mini split is about 7 GB, while
WhestBench supports `--streaming --n-mlps K` specifically for constrained CI.

A three-MLP raw MSE is a **reproduction smoke sample**, not an estimate precise
enough to replace the published 100-MLP/leaderboard values. The strong parity
check is V25-vs-V29 on the identical three MLPs plus V29 metered cost. If CI
memory or the public HF transport prevents the mini slice from completing, the
receipt must report that exact technical blocker; validation/static results
remain admissible but raw/cost parity stays unverified.

## Legal provenance

The upstream repository contains an MIT License, copyright 2026 504aldo. MIT
permits use, copying, modification and redistribution subject to preserving the
copyright and permission notice. E136 vendors the original license alongside
the copied estimator files. No upstream code is represented as original
arc-whitebox work.

## Exit condition

E136 is successful when it produces a reproducible, legally attributed public
baseline with code identity, validation evidence, Phase-2 restriction audit,
shape-fallback evidence, and measured public-mini smoke results.

Success does **not** mean the baseline wins, reaches the private leaderboard, or
is suitable for direct submission without further independent review.


## Recorded result

Authoritative Actions run: `35540584740`, job `106157369520`, head
`830bb11a27cc3a3d9c1e42fb4c6f6fa2004fffe4`.

- Static provenance/license/rules audit: PASS.
- V25 non-suite `whest validate`: PASS.
- V29 non-suite `whest validate`: PASS.
- Public `v2-phase2/mini`, streaming first 3 MLPs, V25: PASS,
  raw final-layer MSE `2.33e-8`.
- Same three public MLPs, V29: PASS, raw final-layer MSE `2.33e-8`.
- V25 plain report recorded aggregate estimator FLOPs `2.42e12` over three
  MLPs, implying mean `C/B ~= 0.36683` from the rounded report, versus the
  published `0.3667`.
- V29 plain report recorded aggregate estimator FLOPs `1.70e12` over three
  MLPs, implying mean `C/B ~= 0.25769`. This is about 2% above the published
  `0.2526` steady-state path; the upstream write-up explicitly says the first
  predict uses a shallower, higher-cost Strassen level, so a three-MLP mean is
  expected to sit above steady state.

The three-MLP raw value is 2.4% above the author's published V29 eight-dump raw
`2.275e-8`, 4.5% above the published V25 100-MLP mini raw `2.23e-8`, and
9.4% above the public-LB `~2.13e-8`. Those are compatible smoke results, not a
claim of exact suite parity. The stronger local reproduction fact is that V25
and V29 give the same raw result on the identical three public MLPs while the
metered cost falls along the published V25 -> V29 path.

Immutable receipt: `research/E136_REPRODUCTION_RECEIPT.json`.

Evidence artifact: Actions artifact `10614453799`,
SHA256 `103b5d4b97fb6584a45805877414545ea05705693f573f816d1ef76b8ce7b658`.
