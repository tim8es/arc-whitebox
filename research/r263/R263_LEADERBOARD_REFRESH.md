# R263 - Fresh official Phase-2 leaderboard/rules audit

Audit time:
- UTC: 2026-09-23T12:05:34Z
- Europe/Moscow: 2026-09-23T15:05:34+03:00
- Control claim/start: revisions 296/297
- Isolated branch: `research/r263-leaderboard-refresh-20260923`
- Frozen protocol commit: `fbb17a40760fc6630fda08f1d87533b298917324`
- Source snapshot commit: `d9d965d6bccb681658cade3e3d90f9e770152a29`

## Fresh official standings

Official AIcrowd leaderboard:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

Visible top rows at the audit time:

| Rank | Participant | Adjusted Score | Final Layer MSE | Compute utilisation | Failed | Entries | Last submission |
|---:|---|---:|---:|---:|---:|---:|---|
| 01 | J2W | 0.0000000021 | 0.0000000164 | 0.1306572576 | 0 | 312 | 2026-09-19 00:05 |
| 02 | suliman_tadros | 0.0000000022 | 0.0000000163 | 0.1375978303 | 0 | 45 | 2026-09-23 01:42 |
| 03 | marius_binner | 0.0000000023 | 0.0000000156 | 0.1474118618 | 0 | 158 | 2026-09-23 06:46 |
| 04 | a_s6 | 0.0000000025 | 0.0000000200 | 0.1258033415 | 0 | 106 | 2026-09-21 13:55 |
| 05 | Puffi | 0.0000000028 | 0.0000000194 | 0.1456939183 | 0 | 78 | 2026-09-08 14:09 |
| 05 | reds | 0.0000000028 | 0.0000000173 | 0.1623309082 | 0 | 59 | 2026-09-21 08:47 |
| 07 | oqaris | 0.0000000031 | 0.0000000215 | 0.1459882369 | 0 | 93 | 2026-09-14 05:56 |
| 07 | ben3 | 0.0000000031 | 0.0000000168 | 0.1838821710 | 0 | 23 | 2026-09-22 19:38 |
| 09 | mliston | 0.0000000032 | 0.0000000181 | 0.1756230281 | 0 | 39 | 2026-09-23 10:13 |
| 10 | Camaro | 0.0000000033 | 0.0000000190 | 0.1754820884 | 0 | 68 | 2026-09-21 09:26 |

The strongest displayed score is therefore **0.0000000021** for J2W. The leaderboard's View link resolves to submission #331539:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331539

Relative to R241 (2026-09-23T03:31:44Z), the top displayed participant and rounded score are unchanged; J2W's entry count increased from 310 to 312. No inference is made from entry count.

## Official Phase-2 metric and rules

Official scoring source:
https://github.com/AIcrowd/whest-starterkit/blob/main/docs/concepts/scoring-model.md

Current official definition:
`adjusted_final_layer_score = mean_m(final_layer_mse_m * max(0.1, C_m / B))`,
with `C_m = F_m` in Phase 2 and multiplier forced to 1.0 on a failed MLP. Lower is better. The per-MLP FLOP budget is `B = 2**41 = 2,199,023,255,552`.

Current-round source:
https://github.com/AIcrowd/whest-starterkit/blob/main/docs/reference/rounds.md

It identifies `v2-phase2` as current, width 1024, depth 16, 120 s predict cap, 0.4 s residual cap, and a 100-MLP graded suite.

Official Phase-2 launch/rules announcement:
https://discourse.aicrowd.com/t/phase-2-of-the-arc-white-box-estimation-challenge-is-live/18197

Submission deadline: **2026-10-17 23:59 UTC** = **2026-10-18 02:59 Europe/Moscow**.

## R209 V25 comparability

R209 normalized source:
https://github.com/tim8es/arc-whitebox/blob/research/control-v2/research/results/R209-v25-mini100.json

R209 V25 is:
- dataset `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`;
- split `mini:all-100`;
- stage `development`;
- 100 networks, 0 failures;
- recorded adjusted score `8.170397440117225e-9`.

The official public-Mini local instructions explicitly define that local development panel as 100 fixed public MLPs:
https://github.com/AIcrowd/whest-starterkit/blob/main/docs/getting-started/stage-3-run-local.md

A current official Phase-2 submission detail page, #329251, explicitly reports **50/50 public MLPs scored**, another **50 private MLPs sealed**, and states that the full 100-MLP test-set result is the final score:
https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329251

Therefore:
- metric formula: MATCH;
- aggregation rule (mean of per-MLP adjusted scores): MATCH;
- evaluated split/panel: **MISMATCH** (R209 public Mini development 100 vs current visible online public 50; the other 50 are sealed for final evaluation).

**Decision: NOT_COMPARABLE.** Per the R263 protocol, no numeric score gap, competition rank, or place is computed or claimed for R209 V25.

## Source hashes / provenance

- Normalized R263 source snapshot SHA256: `6cbb8ce69ad4330cc624e78209a49a1b333e3845daf8def1fd2a462d6ff49646`
- Source snapshot Git blob SHA1: `08b2453f8a3dc3b7e1d57fb939214143c6b5aa25`
- Official `scoring-model.md` Git blob SHA1: `f65e3700ad1874e563f4ef9d91bd2e0a8aa0ae7e`
- Official `rounds.md` Git blob SHA1: `2aaf38a54b5d6ed83ce2604870dcac59e62cee59`
- Official `stage-3-run-local.md` Git blob SHA1: `2bc23fd23210f513a9bfab4917dde6f4ef18c125`
- R209 normalized-result Git blob SHA1: `0183d0570f7c9965e00e8553ffc003c313865232`
- R209 receipt SHA256: `5c87e8868ce3221b01979f7360079960e8991629926a7623037662f3c4511740`
- R241 prior report SHA256: `62bc2866abca422fdad2eff0b414b4ab89c32bc0534e5098e9b943c24c34baee`
- R241 prior receipt SHA256: `7562d0846b9f7b342a9eb132e76c3fc633acb78204bb1d43ed43a51d61de3c04`

The dynamic AIcrowd leaderboard/announcement pages do not expose a stable origin byte digest through the read-only browser. Their audited fields are preserved in `R263_SOURCE_SNAPSHOT.json`; the SHA256 above binds exactly that normalized capture.

## Safety / execution record

No estimator or benchmark was run. No GitHub Actions workflow was started. No paid resource, private/holdout/full dataset, submission, leaderboard mutation, or canonical-result edit was used. This was a public-source and existing-evidence desk audit only.
