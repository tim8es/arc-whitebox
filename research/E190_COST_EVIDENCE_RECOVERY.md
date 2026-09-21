# E190 COST-EVIDENCE RECOVERY — existing immutable evidence only

Date: 2026-09-22  
Branch: `research/e190-cost-evidence-recovery-20260922`  
Parent: E187 `06fbb08fb9ece3b5b3d8da7b60fee331030a044f`  
Mode: **READ-ONLY EVIDENCE RECOVERY — NO BENCHMARK, WORKFLOW, ESTIMATOR OR CANDIDATE RUN**  
Decision: **EXACT PARENT RAW TOTAL RECOVERED; NO TERMINAL GAP FOR THE TOTAL**

Normative machine-readable companion:

`research/e190/E190_RECOVERED_PARENT_LEDGER.json`

## 1. What E187 was missing

E187 correctly observed that the committed F86 namespace log prints only rounded
values. The audit script stores

`C = float(ctx.flops_used)`

but prints the call total as `C/B` to four decimals and `C/u` to one decimal, while
family/group values are printed to two decimal units.

Pinned F86 evidence:

- upstream commit:
  `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`;
- `docs/audit_v29_ns_d0.log` blob
  `a689ef69fd64bed7765cb93ce4910c3fedcbd04a`;
- `harness/audit_v29_ns.py` blob
  `279d8e0308360fde7616d56f8e8cc2705b529898`;
- plain V29 blob
  `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`;
- namespaced V29 blob
  `f91df783b83cb5fae0af57a16799c5df81891bd2`.

The source log renders:

- call 1: `0.2671 B = 273.5u`;
- call 2, designated by F86 as the ledger: `0.2540 B = 260.1u`;
- grouped display: `115.61 + 106.83 + 24.78 + 7.10 + 5.71 + 0.03 = 260.06u`.

The raw integer is not present in that text file.

## 2. Existing immutable artifact that recovers the integer

The already-completed E136 full-mini run contains an immutable JSON report with exact
per-MLP `flops_used`.

Provenance:

- Actions run: `35544406064`;
- V29 job: `106167659295`;
- run head: `dff3dd65e9d2210e02418cca99e05556f6bf2c75`;
- artifact ID: `10617318650`, name `e136-followup-v29`;
- artifact SHA-256:
  `32c29ac79c5c59b841c88c6c274ed378daf2778a61d4344c7aa0b58f1da11681`;
- `report.json` SHA-256:
  `76c496968b9a81dc1eae91e8204969c0dfe9d7f113dd46af0c0e7df82496a78b`;
- existing summary's per-MLP-index SHA-256:
  `36becb062d04f8b6fdf76d9d5d4e0407cb357e3b111d744be459ba83394e5b5a`;
- vendored estimator blob:
  `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`, byte-identical to upstream V29;
- environment records `flopscope 0.12.1+np2.4.6`, width 1024, depth 16, one BLAS thread.

The artifact ZIP was downloaded read-only and its SHA-256 was independently checked
against the GitHub artifact digest; they match exactly.

The existing `report.json` contains only three distinct raw FLOP counts:

| call position | exact `flops_used` | units | C/B |
|---|---:|---:|---:|
| MLP 0 | 587,262,754,287 | 273.465530149173 | 0.267056181786302 |
| MLP 1 | **558,473,140,719** | **260.059321634006** | **0.253964181283209** |
| MLP 2–99 | 555,383,704,047 | 258.620690576266 | 0.252559268140885 |

The first exact value renders as F86 call 1: `273.5u / 0.2671B`.
The second exact value renders as F86 call 2: `260.1u / 0.2540B`.

Therefore the missing exact raw count for the F86 call-2 parent ledger is:

> **558,473,140,719 FLOPs**

## 3. Why the E136 integer is valid evidence for F86

This is not an inference from one rounded number alone.

1. E136 executes a vendored V29 whose Git blob is exactly the pinned upstream plain-V29
   blob `17df1a...`.
2. Upstream `generators/make_v29_ns.py` blob
   `6c0e439eaeefcb2e06991cb86d9bda3b174fc30d` states and implements a pure textual
   namespace wrapping of that V29: asserted anchors, unchanged operation stream.
3. F86 explicitly defines the **second predict** as the namespace ledger.
4. The existing E136 raw first/second call pair reproduces both F86 rounded fingerprints,
   not merely the second one.
5. Both paths use the flopscope 0.12.1 family, width 1024 and depth 16.
6. F86 states that flopscope counts are shape-based, so one dump is the ledger.

The bridge therefore identifies the pre-rounding call-2 integer without executing a new
estimator.

## 4. Reconciliation with 222.44u + 37.62u

The exact recovered total is:

`
558,473,140,719 / 2^31
= 260.059321634005755... u
`

It rounds to:

- `260.06u` at two decimals;
- `260.1u` at one decimal;
- `0.2540B` at four decimals.

The F86 grouped display gives:

`
dense = 115.61 + 106.83 = 222.44u
remainder = 24.78 + 7.10 + 5.71 + 0.03 = 37.62u
dense + remainder = 260.06u
`

So the exact integer is fully consistent with the published decomposition.

Important precision boundary: **222.44u and 37.62u remain rounded group totals.**
The existing E136 artifact is plain V29 and contains no namespaced raw op-log; the
committed F86 log also does not retain exact group integers. E190 therefore does not
invent exact dense/remainder component FLOPs.

## 5. Search coverage

Read-only search covered:

- the complete recursive upstream Git tree;
- the F86 source log, cost-anatomy CSV, audit script, namespace generator and estimator
  identities;
- upstream GitHub Actions: zero runs/artifacts exist;
- E136 reproduction receipt and authoritative 3-MLP run;
- E136 full-100 run, V29 artifact, summary artifact/job and immutable hashes;
- E180, E185, E186 and E187 Actions: zero runs on each branch;
- repository text search for the recovered integer: absent, confirming that its storage
  location is the immutable E136 Actions `report.json`, not a committed prose value.

No benchmark, workflow, estimator, candidate or scientific run was started by E190.

## 6. Can the ledger be made machine-readable without execution?

**Yes, for the missing exact parent total.**

The companion JSON records:

- exact parent raw FLOPs: `558473140719`;
- exact artifact/run/job/head provenance;
- artifact and report hashes;
- source estimator and namespace-generator identities;
- exact call fingerprint;
- rounded F86 dense/remainder decomposition with its precision explicitly marked.

What cannot be recovered from existing evidence is an **exact raw integer split by F86
namespace/group**. Recovering that would require an existing raw namespaced op-log
(which the repository/artifacts search did not find) or a new execution.

## 7. E190 conclusion

**RAW PARENT TOTAL RECOVERED FROM EXISTING IMMUTABLE EVIDENCE.**

The condition for a terminal evidence gap stated in E190 is not met for the missing raw
parent total. The exact integer exists in an already-created immutable Actions artifact
and can be bound to F86 by code identity plus the two-call cost fingerprint.

E190 does not authorize an owner run and does not change H185/E187 launch status by
itself; a verifier/review may consume this recovered ledger and decide whether G2 is now
satisfied.

The exact component split remains unavailable, and E190 records that limitation rather
than fabricating precision.

No baseline, canonical ledger, scorer, submission or leaderboard state was changed.
