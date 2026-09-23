# R271 - Exact visible-50 identity reconciliation against R209 V25

Status: COMPLETE desk audit; **NOT_COMPARABLE**
Job: R271 / VISIBLE50-IDENTITY-RECONCILIATION-20260923
Owner: leader-method-forensics
Run ID: R271-visible50-identity-reconciliation-20260923
Control claim/start: revisions 326 / 328
Source/code commit recorded at start: 244e77592048e545282628ef16dfca65b95aeb2b
Isolated branch: research/r271-visible50-reconciliation-20260923

## Decision

The exact same-panel R209 V25 score **cannot be computed from the existing R209 record**.

This is stronger than the earlier generic 100-vs-50 split caveat:

1. The official Phase-2 submission ledger exposes the visible public panel as 50 rows with `mlp_index` and `mlp_name`, but it does **not** expose a machine-stable `network_id` or target fingerprint.
2. Official starter-kit documentation defines `mlp_name` as a deterministic human-readable slug and stable label. The 50 published visible-panel labels have **0/50 exact label overlap** with the 100 immutable R209 labels.
3. R209 is recorded under `whestbench 0.16.1` and `flopscope 0.12.1+np2.4.6`. The current official starter-kit source explicitly states that the grader is on `whestbench v0.16.0` with `flopscope[server]==0.12.0`. Thus exact evaluator/meter version identity also fails.
4. Because exact visible-50 network IDs are not public and no 50 rows can be selected from R209 by proven identity, **no 50-row score was recomputed**. In particular, the first 50 R209 rows were not used.

Verdict: **NOT_COMPARABLE**. No official gap or rank is claimed.

## Official visible Phase-2 50

Official primary source:
https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329251

That page states that every displayed public-split number is graded on 50 public MLPs, recomputed each submission, with 50 additional MLPs sealed for final release. Its ledger publishes `#` and `name`; the documented report schema calls those `mlp_index` and `mlp_name`.

The table below is keyed by the **published mlp_index**, not by the score-sorted display order.

| mlp_index | official mlp_name | official network_id | exact mlp_name present in R209 |
|---:|---|---|---|
| 00 | natasha-heath | NOT PUBLIC | no |
| 01 | caitlin-kemp | NOT PUBLIC | no |
| 02 | jennifer-jordan | NOT PUBLIC | no |
| 03 | brandon-chen | NOT PUBLIC | no |
| 04 | nicholas-gonzalez | NOT PUBLIC | no |
| 05 | thomas-anderson | NOT PUBLIC | no |
| 06 | jill-gardner | NOT PUBLIC | no |
| 07 | amanda-richmond | NOT PUBLIC | no |
| 08 | tina-garcia | NOT PUBLIC | no |
| 09 | alicia-levy | NOT PUBLIC | no |
| 10 | jennifer-miller | NOT PUBLIC | no |
| 11 | richard-contreras | NOT PUBLIC | no |
| 12 | david-webb | NOT PUBLIC | no |
| 13 | bradley-king | NOT PUBLIC | no |
| 14 | jodi-morales | NOT PUBLIC | no |
| 15 | travis-ward | NOT PUBLIC | no |
| 16 | tanya-bennett | NOT PUBLIC | no |
| 17 | joseph-vega | NOT PUBLIC | no |
| 18 | amy-young | NOT PUBLIC | no |
| 19 | april-rogers | NOT PUBLIC | no |
| 20 | william-white | NOT PUBLIC | no |
| 21 | evan-jennings | NOT PUBLIC | no |
| 22 | julie-grant | NOT PUBLIC | no |
| 23 | chad-cortez | NOT PUBLIC | no |
| 24 | diana-summers | NOT PUBLIC | no |
| 25 | lauren-nelson | NOT PUBLIC | no |
| 26 | stephen-kelly | NOT PUBLIC | no |
| 27 | brandy-johnston | NOT PUBLIC | no |
| 28 | joshua-reed | NOT PUBLIC | no |
| 29 | william-saunders | NOT PUBLIC | no |
| 30 | john-fischer | NOT PUBLIC | no |
| 31 | stacey-cunningham | NOT PUBLIC | no |
| 32 | jeffery-bailey | NOT PUBLIC | no |
| 33 | sandra-fernandez | NOT PUBLIC | no |
| 34 | patricia-douglas | NOT PUBLIC | no |
| 35 | donald-nguyen | NOT PUBLIC | no |
| 36 | ian-lara | NOT PUBLIC | no |
| 37 | margaret-miller | NOT PUBLIC | no |
| 38 | gabriel-baird | NOT PUBLIC | no |
| 39 | jason-davies | NOT PUBLIC | no |
| 40 | jerry-kerr | NOT PUBLIC | no |
| 41 | travis-fox | NOT PUBLIC | no |
| 42 | tim-richardson | NOT PUBLIC | no |
| 43 | seth-griffin | NOT PUBLIC | no |
| 44 | stephanie-garcia | NOT PUBLIC | no |
| 45 | daniel-martinez | NOT PUBLIC | no |
| 46 | jared-parker | NOT PUBLIC | no |
| 47 | ronnie-carpenter | NOT PUBLIC | no |
| 48 | leah-fields | NOT PUBLIC | no |
| 49 | tyler-espinoza | NOT PUBLIC | no |

Set comparison: **0 / 50 visible stable labels occur in R209's 100 rows**.

This set comparison does not manufacture network IDs from the indices. The `#` column is only `mlp_index`; official docs do not define it as `network_id`.

Machine-readable preservation:
`research/r271/R271_IDENTITY_AUDIT.json`
- commit: `4869346674d3d2fd8b411e710fbfef2cdff62338`
- Git blob SHA-1: `dae9e30f803918f642710e50e0191568f9939578`
- SHA-256: `c1d329541d544f396e02b18ddb2c78c02bf73da911ff7a97f3bd0b1827ac1260`

## Immutable R209 evidence

Source:
`research/results/R209-v25-mini100.json`

Identity:
- Git blob SHA-1: `0183d0570f7c9965e00e8553ffc003c313865232`
- source commit: `dff3dd65e9d2210e02418cca99e05556f6bf2c75`
- dataset: `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`
- split: `mini:all-100`
- stage: `development`
- rows: 100
- evaluator: `whestbench 0.16.1`
- meter: `flopscope 0.12.1+np2.4.6`
- dataset metadata SHA-256: `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`

Every R209 row has a `network_id` and `target_sha256`, but none can be joined to the official visible 50 because the online page does not publish those machine IDs and the stable public labels do not overlap.

## Metric and evaluator versions

Official starter-kit source pinned for this audit:
- repository: `AIcrowd/whest-starterkit`
- main commit: `5eb9aa1455fcb3216af55994bdf25dc242b95797`

Metric sources:
- `docs/concepts/scoring-model.md`, blob `f65e3700ad1874e563f4ef9d91bd2e0a8aa0ae7e`
- `docs/reference/rounds.md`, blob `2aaf38a54b5d6ed83ce2604870dcac59e62cee59`

Current Phase-2 rule:
`adjusted_final_layer_score = mean_m(final_layer_mse_m * max(0.1, F_m / B))`,
with `B = 2**41`, `C_m = F_m`, failure multiplier 1.0, and lower better.

Schema source:
- `docs/reference/score-report-fields.md`, blob `4656a892bfeea52a233b900f6d698db8524936fc`
- line 53: `mlp_index` is the index in the evaluation set.
- line 54: `mlp_name` is a deterministic human-readable slug and stable label.
- there is no documented per-MLP `network_id` field.

Evaluator source:
- `pyproject.toml`, blob `2c1d562a2073046d6912868184b52c8c593d23c5`
- lines 12-13 pin starter-kit dependencies to flopscope >=0.12.1,<0.13.0 and whestbench >=0.16.1,<0.17.0.
- lines 24-28 explicitly state: grader = `whestbench v0.16.0`, `flopscope[server]==0.12.0`; the kit leads by one patch.

Therefore:
- scoring formula / round semantics: compatible at the documented rule level;
- exact evaluator version: **MISMATCH**;
- exact meter version: **MISMATCH**;
- exact panel identity: **NOT PROVEN and contradicted by 0/50 stable-label overlap**.

## R263 / R270 reconciliation

R263 correctly found:
- metric match;
- mean-over-MLP aggregation match;
- R209 public mini all-100 vs online 50-public + 50-sealed split mismatch;
- no official rank/gap.

R270 independently verified the R209 100-row arithmetic and preserved the same NOT_COMPARABLE decision.

R271 adds the missing identity-level check: the official visible ledger's 50 stable labels have zero overlap with R209, and no public network-ID field exists to support an exact-ID join.

## Why no 50-row recomputation appears

The task requires all 50 exact identities before selecting R209 rows. That gate fails.

A calculation using:
- the first 50 R209 rows,
- a guessed 50-row subset,
- score-sorted order,
- or matching only the rounded leaderboard score

would be evidence fabrication. None was performed.

The leader's displayed `2.1e-9` also remains a rounded UI value with unknown renderer mode, as R270 recorded. Since panel identity already fails, no rounding interval is used to manufacture a same-panel gap.

## Minimum missing public artifact

For a formal identity test, the minimum artifact is an **official immutable visible-50 manifest** that maps each public `mlp_index` / `mlp_name` to a machine-stable `network_id` (preferably also `target_sha256`) and states the grader evaluator/meter versions.

For an exact R209-derived score, those 50 IDs and fingerprints would additionally need to exist in the immutable R209 rows under compatible scoring/evaluator semantics. If they do not, existing R209 cannot answer the question; an immutable official/public **V25 per-MLP result artifact for those exact 50** would be required.

## Constraints

No estimator or benchmark run.
No dataset download.
No GitHub Actions run.
No paid resource.
No private/holdout/full data access.
No submission.
No leaderboard mutation.
No canonical/model edit.
