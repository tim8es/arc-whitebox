# R230 Public Leader Method Audit

Status: COMPLETE (read-only, evidence-limited)
Job: R230 / PUBLIC-LEADER-METHODS-TRANSFER-AUDIT
Run ID: R230-public-leader-method-audit-20260923
Frozen protocol commit: f55de5498921bd57b68e88f7ed179e6c13c15ce7
Queue start commit: f471601a79f43f3eada4f19144050615b486d3bd
Access window: 2026-09-23T01:44:36+03:00 to 2026-09-23T01:46:44+03:00
UTC window: 2026-09-22T22:44:36Z to 2026-09-22T22:46:44Z

## Decision

NO_PUBLIC_METHOD_EVIDENCE_FOR_TARGET_SUBMISSIONS.

The official AIcrowd leaderboard publicly links submission IDs 331539 (J2W) and 331308
(marius_binner), and exposes their public score telemetry. However, in this audit the
public submission detail URLs did not expose a readable method description, source-code
link, downloadable artifact link, or system-description field. The anonymous HTML view for
both target URLs returned only the client-side "Loading" shell, while the direct static
assets endpoint was not readable through the audit web interface.

Therefore this audit does not attribute any algorithm, representation, cumulant order,
matrix-multiplication scheme, calibration rule, sampling method, or source lineage to
either target submission.

No competitor code or archive was downloaded or executed.

## Access and permission gate

The target IDs are legitimate public navigation targets: the current official leaderboard
has a public "View" link for each target row [S1].

That does not imply that all submission internals are public. AIcrowd staff explicitly
confirmed on the official challenge forum that error details on submission detail pages
are protected by RBAC and only visible to the submitting team; a separate global-message
leak was acknowledged and targeted for repair [S5]. This audit treated any non-public
detail field as out of scope and did not attempt an access-control bypass.

The public target pages themselves were requested via their official AIcrowd URLs [S2,S3].
The readable anonymous body was only the generic page shell and did not contain method,
source, artifact, download, or description material.

## Public facts for the two target submissions

Snapshot source is the official leaderboard at audit time [S1].

| Submission | Public participant/team | Public adjusted score | Public final-layer MSE | Compute utilization | Public method/source evidence |
|---|---|---:|---:|---:|---|
| 331539 | J2W | 2.1e-9 | 1.64e-8 | 0.1306572576 | NONE OBSERVED |
| 331308 | marius_binner | 2.4e-9 | 1.68e-8 | 0.1459323523 | NONE OBSERVED |

The public J2W team page identifies joe_wanza as its sole team organizer [S4]. This is an
identity fact, not a method fact.

No analogous method disclosure tied specifically to submission 331308 was found in the
official public material inspected here.

## Explicit exclusion of unsupported inference

The official AIcrowd forum contains a detailed public V25/V29 write-up by team 504aldo
[S6]. That author compares the disclosed K3+memoryless-K4 family with leaderboard leaders
and speculates about what top methods may carry. The post explicitly labels its explanation
of the top method as a "best guess" and "not validated".

R230 therefore does not use that speculation as evidence about 331539 or 331308.

Likewise, public score/utilization pairs cannot identify an algorithm. Many materially
different estimators can occupy similar points in the accuracy/compute plane.

## Comparison with experiment history

The internal history shows that our already-explored family is broad:

- E007 reproduced the public V25 factorized K3 + memoryless K4 frontier at mini-100 raw
  MSE about 2.23e-8, adjusted score about 8.17e-9, utilization about 0.3667, 0/100 failures.
- E010/E014 and later work investigated V29/Strassen/batching cost paths and residual-time
  failure modes.
- E017/E052/E094 and related lanes covered old-source/shared-basis or source-axis
  compression variants.
- E019/E154 and related lanes covered higher-order/fourth-cumulant closure variants;
  E154 ended terminal NO-GO for its frozen angular-radial memoryless-K4 closure.
- E137 explicitly documented the V25/V29 baseline lineage and selected a CountSketch
  old-tier contraction hypothesis rather than claiming to explain leaderboard leaders.
- E151 was a prior "leader forensics" source audit; importantly, it explicitly stated
  that its angular-radial/Strassen hypothesis was NOT a claim about J2W, marius_binner,
  or other leaders.

R209 normalized evidence on the shared mini-100 panel:

| Record | Panel | Adjusted score | Raw final MSE | Failures | Known mechanism status |
|---|---|---:|---:|---:|---|
| R209 V25 | v2-phase2 mini:all-100 | 8.170397440117225e-9 | 2.228303490170447e-8 | 0/100 | Public V25 factorized-K3 lineage, internally reproduced |
| R209 V29 | same mini-100 | 0.5270942878803214 | dominated by failed rows | 57/100 | Same arithmetic family with V29 cost engineering; residual failures dominate this archived local run |

These records are useful baselines for deduplication. They do not reveal the target leader
methods and are not exact-panel leaderboard comparisons.

## Novelty / deduplication table

| Candidate public claim | 331539 evidence | 331308 evidence | History overlap | Novelty decision |
|---|---|---|---|---|
| Factorized K3 source propagation | not exposed | not exposed | E007/R209 V25, extensive descendants | UNKNOWN; do not attribute |
| Memoryless K4 regeneration | not exposed | not exposed | E007/R209 V25, E019/E154 variants | UNKNOWN; do not attribute |
| D21 feedback / old-source shared bases | not exposed | not exposed | V18/V22/V24 lineage, E017/E052/E137 | UNKNOWN; do not attribute |
| Strassen-Winograd / batched dense products | not exposed | not exposed | V29, E010/E014/E093/E151 | UNKNOWN; do not attribute |
| Angular-radial state gauge | not exposed | not exposed | E151 hypothesis, E154 tested NO-GO scope | UNKNOWN; do not attribute |
| CountSketch old-tier contraction | not exposed | not exposed | E137/H137 | UNKNOWN; do not attribute |
| Other fourth-order or old-memory mechanism | not exposed | not exposed | many higher-order lanes; exact target method unknown | UNKNOWN; no novelty claim |

Because the target method column is empty, there is no defensible intersection or set
difference from which to derive a leader-specific "new mechanism".

## Transferable hypotheses

Admitted leader-derived hypotheses: 0.

This is intentional. The R230 protocol requires public method evidence before a transferable
hypothesis can be attributed to either target. The target detail pages did not supply that
evidence, and the only official-forum explanation found for the leaders is explicitly
speculative [S6].

A future R230-successor may admit at most one leader-derived hypothesis only after one of
these evidence gates is met:

1. AIcrowd publicly exposes a method/system-description/source link tied to submission
   331539 or 331308; or
2. the submitting participant publishes an official AIcrowd forum post that explicitly
   ties a described mechanism to that exact submission ID.

Any admitted hypothesis should then pass both gates before execution:

- novelty/evidence gate: exact mechanism text must be compared against history before code;
  if it reduces to E007/V25, V29/Strassen, E137 CountSketch, E151/E154 angular-radial, or
  another recorded lane, it is not new;
- cost gate: pre-compute an all-in Phase-2 FLOP upper bound and require a plausible adjusted
  score improvement relative to R209 V25 on an identical development panel; do not treat
  savings below the 0.1 compute-multiplier floor as useful unless accuracy also improves.

No estimator run is authorized by this audit.

## Exact evidence gap

For each of 331539 and 331308, the missing item is not the score. The missing item is an
official public, submission-specific method/source disclosure.

Observed access result:

- official leaderboard row and View link: readable;
- official target detail URL: public route exists but anonymous audit body remained a
  JavaScript "Loading" shell;
- direct static assets route for these exact IDs: unavailable to the audit web reader;
- method/source/download/artifact/description field: not observed;
- protected/internal fields: not probed.

This is an access/evidence limitation, not evidence that no method description exists for
the submitting team or AIcrowd organizers.

## Sources

Primary official AIcrowd sources:

[S1] Current ARC White-Box Estimation Challenge leaderboard:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards

[S2] Official submission route 331539:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331539

[S3] Official submission route 331308:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/331308

[S4] Official J2W team page:
https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/teams/J2W

[S5] Official AIcrowd forum, "Errors are leaking information", staff RBAC clarification:
https://discourse.aicrowd.com/t/errors-are-leaking-information/18217

[S6] Official AIcrowd forum, 504aldo public V25/V29 write-up and explicitly unvalidated
leader speculation:
https://discourse.aicrowd.com/t/everything-we-tried-a-factorized-k-3-cumulant-propagation-estimator-at-0-25-x-b-where-its-flops-go-and-25-measured-dead-ends-team-504aldo-rank-10/18218

Internal comparison evidence:

[H1] research/history.json on research/control-v2.
[H2] E007 history record / research/E007_PROTOCOL.md.
[H3] research/E137_PRIMARY_SOURCE_NOTE.md at commit
01f4987c62d1a015236522ddc46e498383706f52.
[H4] research/E151_LEADER_FORENSICS.md at commit
25eec9d50561d7080b086b0579025fe2cd6646f5.
[H5] research/E154_TERMINAL_RECEIPT.json at commit
c599aa6deb7fc7630951be88bac9e0ce1afbe949.
[H6] research/results/R209-v25-mini100.json and R209-v29-mini100.json on
research/control-v2.

## Constraints confirmed

No estimator run. No paid compute. No submission. No private/holdout access. No competitor
code or artifact download. No competitor code execution. No access-control bypass. No
canonical result edit. No leaderboard-rank claim.
