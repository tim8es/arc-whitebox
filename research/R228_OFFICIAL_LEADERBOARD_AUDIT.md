# R228 Official Leaderboard and Rankability Audit

Status: COMPLETE (read-only audit)
Job: R228 / OFFICIAL-LEADERBOARD-RANKABILITY-AUDIT
Run ID: R228-official-leaderboard-audit-20260923
Frozen protocol commit: e47da3c92416e374435fba8313ed7606b5a72227
Queue start commit: 127ed05f8776d8435df8ddec0665544f0d2ed851
Access window: 2026-09-23T01:29:56+03:00 to 2026-09-23T01:33:14+03:00 (2026-09-22T22:29:56Z to 22:33:14Z)

## Scope and source policy

This audit uses primary official sources only for competition facts: the AIcrowd challenge and leaderboard, an official AIcrowd Phase-2 submission detail page, and the official AIcrowd whest-starterkit repository pinned to commit 5eb9aa1455fcb3216af55994bdf25dc242b95797. The R209 records are used only as the internal comparator whose rankability is being tested.

No estimator was run. No paid compute, competition submission, external mutation, canonical-result edit, private split access, or leaderboard mutation was performed.

## Finding

R209 mini-100 is NOT_RANKABLE against the current Phase-2 competition leaderboard.

The local R209 V25 score is a valid score for its published development panel, but it is not an official public-leaderboard score and cannot be converted into a competition place. There are independent exact-comparability failures:

1. Panel mismatch. The published local Phase-2 dataset has a 100-MLP mini split for day-to-day iteration [S6]. A graded Phase-2 submission is currently scored on a distinct 50-MLP public grader split, while another 50 MLPs are sealed private; the final score is the full 100 grader MLPs [S3].
2. Final-rank data are incomplete by design. The private 50 are sealed until results release and are described as the holdout split that determines final rank [S3]. Therefore a final competition place is not observable now from public data alone.
3. Evaluator/meter mismatch. The integrated R209 records report whestbench 0.16.1 and flopscope 0.12.1, while the official starter-kit explicitly states that the grader is on whestbench 0.16.0 and flopscope server/client 0.12.0 [S7]. No claim is made that this patch difference changes R209 V25's score, but exact evaluator equivalence is absent.
4. No exact grader submission exists for the R209 V25 result being compared. The official leaderboard rows are results of submitted artifacts on the grader panel [S2,S3]; R209 is a local archived mini-100 evaluation.

Accordingly, this audit does not state a rank for R209 V25 or V29.

## Official Phase-2 scoring contract

The official current round is v2-phase2: width 1024, depth 16, per-MLP budget B = 2**41 = 2,199,023,255,552 FLOPs, predict wall cap 120 s, residual wall cap 0.4 s, setup cap 5 s, and effective compute C_m = F_m [S5].

For a valid MLP m:

    adjusted_m = final_layer_mse_m * max(0.1, C_m / B_m)

The leaderboard metric is the suite mean of adjusted_m; lower is better [S4]. If a per-MLP cap is blown, predictions for that MLP are zeroed and the compute multiplier is forced to 1.0 [S4]. A setup timeout fails the run rather than one MLP [S4].

The official challenge page states that submissions are scored on MSE against a high-budget Monte Carlo reference and directs current scoring/contract details to the starter kit [S1].

## Current visible public leaderboard snapshot

At the access window above, the official AIcrowd leaderboard rendered 50 participant rows. The displayed Adjusted Score range on that page was 2.1e-9 through 5.4e-9; ties produce displayed rank numbers 01 through 43 [S2]. These are current PUBLIC leaderboard positions, not a completed final 100-MLP ranking, because the private half is still sealed [S3].

Top visible rows and their current View targets:

| Display rank | Participant | Adjusted score | Final-layer MSE | Compute util. | Failed | Entries | View submission |
|---:|---|---:|---:|---:|---:|---:|---:|
| 01 | J2W | 2.1e-9 | 1.64e-8 | 0.1306572576 | 0 | 310 | 331539 |
| 02 | marius_binner | 2.4e-9 | 1.68e-8 | 0.1459323523 | 0 | 152 | 331308 |
| 02 | suliman_tadros | 2.4e-9 | 1.83e-8 | 0.1320802423 | 0 | 39 | 331854 |
| 04 | a_s6 | 2.5e-9 | 2.00e-8 | 0.1258033415 | 0 | 106 | 331756 |
| 05 | Puffi | 2.8e-9 | 1.94e-8 | 0.1456939183 | 0 | 78 | 330322 |
| 05 | reds | 2.8e-9 | 1.73e-8 | 0.1623309082 | 0 | 59 | 331730 |
| 07 | oqaris | 3.1e-9 | 2.15e-8 | 0.1459882369 | 0 | 93 | 330951 |
| 07 | ben3 | 3.1e-9 | 1.68e-8 | 0.1838821710 | 0 | 23 | 331882 |
| 09 | Camaro | 3.3e-9 | 1.90e-8 | 0.1754820884 | 0 | 67 | 331734 |
| 10 | mliston | 3.5e-9 | 1.91e-8 | 0.1837895810 | 0 | 35 | 331760 |

The leaderboard page is live and may change after this retrieval time. Submission IDs above are the targets of the official leaderboard's View links observed at retrieval time [S2].

An official Phase-2 submission detail page independently confirms the grading structure: 50/50 public MLPs are scored for the visible public result; the test set is 100 MLPs total; the other 50 are a different sealed private partition; the full 100-MLP score is described as the final score used for ranking [S3].

## Exact evaluation-panel audit

What is officially documented:

- Local public release: aicrowd/arc-whestbench-public-2026 at revision v2-phase2 [S6].
- Local mini split: 100 MLPs, intended for day-to-day iteration [S6].
- Local full split: 1,000 MLPs, intended as a final lock-in check before submission [S6].
- Grader test set: 100 MLPs total, partitioned 50 public + 50 private/sealed [S3].
- Current visible submission result: mean over the 50 public grader MLPs [S3].
- Final score: all 100 grader MLPs, after the private split is released/scored [S3].

What is not available as an exact locally reproducible official asset in the inspected primary sources:

- an immutable local manifest containing the exact 50 public grader MLP weights/targets/seeds;
- the 50 private grader MLP identities/targets, which are explicitly sealed;
- an official grader result for the R209 V25/V29 submitted artifact, because no submission was made by this audit.

The cardinalities alone show that local mini-100 and grader public-50 are not the same evaluation panel. As an additional identity check, nine MLP names visible on the official Phase-2 submission detail page (including jennifer-jordan, joshua-reed, william-white and amy-young) are absent from the 100 R209 V25 mini records. This internal cross-check is supportive, not a substitute for an official grader manifest.

## R209 comparator

The authoritative shared R209 V25 normalized record states:

- panel: hf://aicrowd/arc-whestbench-public-2026@v2-phase2, mini:all-100;
- stage: development;
- evaluator: whestbench 0.16.1;
- meter: flopscope 0.12.1+np2.4.6;
- 100 networks, 0 failures;
- mean official-formula adjusted score: 8.170397440117225e-9;
- mean final MSE: 2.228303490170447e-8;
- dataset metadata SHA256: 264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1.

The authoritative R209 V29 normalized record uses the same local mini-100 panel but has 57 residual_wall_time_exhausted failures and mean adjusted score 0.5270942878803214.

These are valid internal exact-panel development comparisons. They are not leaderboard placements.

The numerical magnitude of the V25 mini-100 score may be viewed descriptively next to the live public scores, but doing so is cross-panel and cannot establish a displayed or final place.

## Rankability gate

A defensible rank statement for an ARC estimator requires, at minimum:

- an official submission evaluated by the competition grader;
- the same Phase-2 metric and exact grader evaluator/meter semantics;
- the exact leaderboard evaluation panel relevant to the rank being claimed;
- for final competition rank, inclusion of the sealed private 50 after release.

R209 satisfies the formula/round family but fails the exact panel, grader-version, and official-submission gates. Final private-panel data are also unavailable.

Decision: NOT_RANKABLE_FROM_R209_MINI100.

## Specific evidence gap / permitted next evidence

The smallest evidence that would make a CURRENT PUBLIC leaderboard comparison exact is an official grader evaluation of the frozen estimator artifact on the official 50-public Phase-2 panel, or an organizer-published immutable public-50 panel artifact/manifest plus exact grader environment sufficient to reproduce it. This audit does not submit or request such a run.

A FINAL competition rank additionally requires the sealed private 50 and the official post-release full-100 grading. Those data are not currently public.

## Primary official sources

- [S1] AIcrowd challenge root (accessed 2026-09-23 local): https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026
- [S2] AIcrowd live leaderboard (accessed 2026-09-23 local): https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards
- [S3] AIcrowd official Phase-2 submission detail #329251: https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329251
- [S4] Official starter-kit scoring model, commit 5eb9aa1455fcb3216af55994bdf25dc242b95797, blob f65e3700ad1874e563f4ef9d91bd2e0a8aa0ae7e: https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/concepts/scoring-model.md
- [S5] Official starter-kit round rules, same commit, blob 2aaf38a54b5d6ed83ce2604870dcac59e62cee59: https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/reference/rounds.md
- [S6] Official starter-kit evaluation-dataset guide, same commit, blob 53af1ead77023bb2c4c27fa2a64b494a4f46aa26: https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/how-to/use-evaluation-datasets.md
- [S7] Official starter-kit dependency/grader note, same commit, blob 2c1d562a2073046d6912868184b52c8c593d23c5: https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/pyproject.toml
- [S8] Official starter-kit README (local Stage 3 public Mini 100 and submission path), same commit: https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/README.md

## Provenance and limits

Official-source repository revision: AIcrowd/whest-starterkit@5eb9aa1455fcb3216af55994bdf25dc242b95797 (latest main observed during this audit; commit timestamp 2026-09-16T05:53:44Z).

Live AIcrowd leaderboard and submission pages are dynamic; their values are timestamped above rather than treated as immutable. The exact private panel is intentionally unavailable. No raw private data were inferred or reconstructed.
