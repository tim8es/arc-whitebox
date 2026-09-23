# R264 — Forensic delta of the current public Phase-2 leader method

Status: COMPLETE (read-only public-primary-source audit)
Job: R264 / PUBLIC-LEADER-METHOD-DELTA-20260923
Owner: leader-method-forensics
Run ID: R264-leader-method-forensics-20260923
Control start revision: 299
Frozen source/code commit: f70cd8e08269b29c6bd1c2c7a4e2c5396f1a2009
Checked at: 2026-09-23T12:06:51Z

## Verdict

**NO_CHANGE_PUBLIC_METHOD_EVIDENCE.**

The strongest visible Phase-2 row is still J2W. Its displayed winning entry remains the same public score telemetry recorded by R230/R241: adjusted score `2.1e-9`, final-layer MSE `1.64e-8`, compute utilisation `0.1306572576`, zero failed MLPs, and displayed last submission `2026-09-19 00:05 UTC`. The current leaderboard also labels the row “No change”.

The only visible row-level metadata delta relative to R241 is `Entries: 310 -> 312`. That is submission-count/telemetry metadata, not algorithm or source disclosure. It does not establish that the currently displayed best submission changed, and it cannot identify a method.

The exact submission route for `#331539` still renders only the generic anonymous `Loading`/share shell. No method description, source-code link, artifact/download link, system description, or implementation text was exposed in the inspected public page. The J2W team page still identifies `joe_wanza` as the sole visible organizer and exposes no method.

Accordingly, R264 finds no new verifiable method/code fact to add to R230 and admits no leader-derived estimator hypothesis.

## Delta from R230 / R241

| Field | R230 / R241 evidence | Current public primary artifact | Delta | Method significance |
|---|---|---|---|---|
| strongest visible participant | J2W | J2W | none | none |
| submission | #331539 | #331539 View route from rank-1 row | none | none |
| adjusted score | 2.1e-9 | 0.0000000021 | none | telemetry only |
| final-layer MSE | 1.64e-8 | 0.0000000164 | none | telemetry only |
| compute utilisation | 0.1306572576 | 0.1306572576 | none | telemetry only |
| failed MLPs | 0 | 0 | none | telemetry only |
| last submission shown | 2026-09-19 00:05 UTC | 2026-09-19 00:05 UTC | none | no visible replacement of best row |
| Entries | 310 in R241 | 312 | +2 | not method evidence |
| public method text for #331539 | none observed | none exposed in anonymous page | none | method remains UNKNOWN |
| public source/artifact for #331539 | none observed | none exposed | none | implementation remains UNKNOWN |

## Fact / inference firewall

### Observed implementation facts for J2W

None. No J2W implementation was publicly exposed in the inspected primary artifacts. Therefore R264 does **not** attribute K3, K4, D21 feedback, shared-basis compression, sampling, Strassen, calibration, or any other estimator mechanism to J2W.

### Permitted inference

The leaderboard demonstrates only an accuracy/compute point. The unchanged score/MSE/utilisation/last-submission fields are consistent with the same strongest displayed entry remaining visible. The `Entries` increase is consistent with additional recorded entries, but it does not show what code they used or whether any changed code produced the rank-1 displayed metric.

No stronger inference is supported.

## Pinned V25 source comparison

The normalized R209 record pins V25 to source commit:

`dff3dd65e9d2210e02418cca99e05556f6bf2c75`

At that commit, the relevant public source is:

`methods/public_504aldo/estimator_v25.py`
Git blob SHA-1: `195373a110215256b759d7c172ba8c923c62e5cc`

Verifiable V25 code facts:

- lines 1-15: file declares the K3-simple factored cumulant lineage, memoryless kappa4 regeneration, D21 feedback, old-source tiers, and V25 adaptive per-MLP lambda; V25 defines `lam_l = LAM[l] * ((mean(dG)/mean(var))/REF_R[l])^BETA`;
- lines 17-34: V24/V21 old sources are confined to shared low-rank bases, including a nested second tier;
- lines 54-67: V18 adds rank-limited D21-feedback thin legs;
- lines 71-82: V17 regenerates the kappa4 core without per-source kappa4 memory;
- lines 101-110: the base is explicitly the reference `k_max=3` SIMPLE factored algorithm plus accuracy riders, including an offline-fitted online mean correction;
- lines 269-272: the mean-correction coefficient table is documented as ridge-fitted on five public v2-phase2 MLP trajectories;
- lines 294-299 and 314-322: the regenerated-kappa4 lambda table and V25 adaptive ratio references are public-fitted constants/rules;
- lines 403-410 and 425-436: the shipped estimator fixes old-tier and feedback ranks and gates suite-specific riders to width 1024/depth 16;
- lines 676-697: the adaptive lambda is actually applied online from `mean(dG0)/mean(var)` and used in regenerated K4 terms.

Exact source:
https://github.com/tim8es/arc-whitebox/blob/dff3dd65e9d2210e02418cca99e05556f6bf2c75/methods/public_504aldo/estimator_v25.py

Because J2W exposes no corresponding implementation, there is no evidence-backed code intersection or difference to compute against V25. A lower public score/utilisation pair is not proof that J2W removed, replaced, compressed, or retained any V25 component.

## Primary public artifacts inspected

1. Official Phase-2 leaderboard:
   https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards
   Current rank-1 row exposes J2W/#331539 telemetry and a public View route.
2. Official submission route #331539:
   https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331539
   Anonymous public render remains a generic Loading/share shell.
3. Official J2W team page:
   https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/teams/J2W
   Identifies joe_wanza as team organizer; no method text.
4. Official AIcrowd challenge forum search was checked for an exact J2W/joe_wanza/#331539 disclosure. No submission-specific primary method disclosure was found in the inspected results. This is a bounded audit statement, not proof that no disclosure exists anywhere.

The public 504aldo forum write-up remains excluded as evidence about J2W because its leader explanation is explicitly speculation rather than a J2W submission disclosure.

## Internal provenance used only for comparison

- R230 report: `research/R230_PUBLIC_LEADER_METHOD_AUDIT.md`
  - report commit `e87c71cab3449d99b09907b128d7ff698dcd1410`
  - Git blob SHA-1 `98a33dddf9cc56db090a7b66fcc7577949727e96`
  - SHA-256 `19db5374f6906d15792934dd2f88c601d8d2ef1866e213a220c2610bb30e73a2`
- R230 receipt: `research/R230_PUBLIC_LEADER_METHOD_AUDIT_RECEIPT.json`
  - receipt evidence commit `12d5e6260b99ba822ad86644b74932844f43d903`
  - Git blob SHA-1 `6e4a2a64152fa0ea9efbe2011e4e03accfa2d96d`
- R241 report: `research/r241/R241_LEADERBOARD_REFRESH.md`
  - report commit `f7a2d3f2c855d639250e459e7b8b80c2f9b13d71`
  - Git blob SHA-1 `73feb8fa6316feea935837a28ccdc694e1e0301a`
  - SHA-256 `62bc2866abca422fdad2eff0b414b4ab89c32bc0534e5098e9b943c24c34baee`
- R241 receipt: `research/r241/R241_RECEIPT.json`
  - Git blob SHA-1 `4c208c9f1d85b3528632723739c7e8a56c456c36`
- R209 normalized V25 record: `research/results/R209-v25-mini100.json`
  - Git blob SHA-1 `0183d0570f7c9965e00e8553ffc003c313865232`
  - pinned `code_commit` `dff3dd65e9d2210e02418cca99e05556f6bf2c75`

## Constraints

No estimator run. No benchmark run. No GitHub Actions run. No competitor code download or execution. No private/holdout/full data access. No paid compute. No submission. No leaderboard or canonical-result edit. No method was inferred from telemetry.
