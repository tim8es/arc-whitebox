# E007 — Public K3+K4 frontier reproduction

Status: RUNNING

## Objective

Reproduce a newly public Phase-2 frontier estimator before designing any new
mechanism on top of it. The scientific target is the factorized K=3 cumulant
chain with memoryless kappa4 regeneration and old-source compression published
by `504aldo/whest-p2-cumulant-k3`.

This is a reproduction experiment, not an authorship claim. Upstream is MIT
licensed, copyright 2026 504aldo.

## Upstream pin

- repository: `504aldo/whest-p2-cumulant-k3`
- license: MIT
- upstream commit: `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- estimator: `estimators/estimator_v25.py`
- expected Git blob SHA: `195373a110215256b759d7c172ba8c923c62e5cc`

The workflow downloads the raw file from the pinned commit and verifies exact
content with `git hash-object` before validation or scoring. No local code edits
to the estimator are allowed in E007-V25.

## Why V25 first

V25 is the same high-accuracy K3+kappa4 method family as the later V29 but does
not use Strassen-Winograd cost engineering. This separates the scientific
accuracy mechanism from a potentially contest-rule-sensitive FLOP optimization.

Public references disclosed by the author:

- V25: raw final-layer MSE about `2.13e-08`, compute `C/B≈0.3667`, adjusted
  score about `7.8e-09` on the public leaderboard; mini raw about `2.23e-08`.
- V29: raw about `2.13e-08`, compute `C/B≈0.2526`, adjusted about `5.40e-09`.

## Fixed environment

- dataset: `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`
- split: `mini`
- MLPs: 100
- width/depth: 1024 / 16
- FLOP budget per MLP: `2**41`
- runner: `local`
- project dependency pins: `whestbench>=0.16.1,<0.17.0`,
  `flopscope>=0.12.1,<0.13.0`
- no `full` split or private/gated data
- no parameter changes, seed sweep, or kill-switch changes

## Exact commands

```bash
curl -fsSL \
  https://raw.githubusercontent.com/504aldo/whest-p2-cumulant-k3/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/estimators/estimator_v25.py \
  -o /tmp/estimator_v25.py

test "$(git hash-object /tmp/estimator_v25.py)" = \
  "195373a110215256b759d7c172ba8c923c62e5cc"

whest validate --estimator /tmp/estimator_v25.py

whest run \
  --estimator /tmp/estimator_v25.py \
  --dataset hf://aicrowd/arc-whestbench-public-2026@v2-phase2 \
  --split mini \
  --runner local
```

## Reproduction gate

PASS only if all hold:

1. zero failed MLPs;
2. raw final-layer MSE is within 15% of the disclosed `~2.1e-08` to
   `~2.23e-08` reference scale;
3. mean compute utilization is within 10% relative of `0.3667`;
4. estimator validates unmodified against the current pinned grader stack.

Record adjusted score, raw final-layer MSE, all-layer MSE, total estimator FLOPs,
mean utilization, failures, scorer duration, wall clock and runtime versions.

## Stop / follow-up rule

If V25 fails reproduction, diagnose only compatibility/accounting differences;
do not retune the estimator and call it a reproduction.

If V25 reproduces, it replaces fixed blend as the project's serious frontier
reference. The next original experiment must address the disclosed structural
bottleneck: old third-cumulant source information costs much more than the young
source tier. Candidate ideas must change the representation or contraction
algebra, not merely compress the same dense legs by another small factor.
