# E188 INDEPENDENT REVIEW — E187 hardened H185 protocol

Date: 2026-09-22  
Branch: `review/e188-e187-independent-review-20260922`  
Review base: E186 commit `89b514fff8c1e7e48a8bb3fc8e542984a84ba045`  
Mode: **READ-ONLY AUDIT — NO SCIENTIFIC RUN, NO CODE EXECUTION, NO BASELINE/LEDGER MUTATION, NO SUBMISSION**

## 0. Executive decision

**Decision: REJECT the future owner-run at this time.**

Reason: the hardened E187 protocol is not present in any currently visible committed
branch/ref or artifact in `tim8es/arc-whitebox`. The repository still exposes:

- E185 head: `10f5f0ab41da70b0661f44596f23f9e7f182ec11`;
- E186 review head: `89b514fff8c1e7e48a8bb3fc8e542984a84ba045`;
- no branch matching `e187`;
- no branch matching `h185`;
- no `E187*` artifact visible from the reviewed ancestry.

Because E187 itself is not inspectable, E188 cannot independently verify that the
hardening requested by E186 was actually frozen before execution. This is a fail-closed
protocol rejection, not a scientific rejection of H185.

A future re-review may AUTHORIZE one owner-run only after E187 is available as an
immutable committed protocol and all checks below pass against that exact SHA.

## 1. Repository / ancestry visibility check

Full branch enumeration was inspected across all visible branch-list pages.

Visible relevant refs:

- `research/e177-primary-source-audit-20260921`
  -> `e1536d36a5e2d641ab3596892847e2fcf41e83ab`;
- `research/e178-h177-higher-order-ago-gauge-20260921`
  -> separate H177/AGO line;
- `research/e180-cost-wall-cp-20260921`
  -> H180 CP line;
- `research/e181-h180-symmetric-cp-carrier-20260921`;
- `research/e181-h180-symmetric-cp-carrier-cleanroom-20260921`;
- `research/e183-h180-implementation-cost-review-20260921`;
- `research/e185-trilinear-aggregation-frontier-20260922`
  -> `10f5f0ab41da70b0661f44596f23f9e7f182ec11`;
- `review/e186-e185-independent-review-20260922`
  -> `89b514fff8c1e7e48a8bb3fc8e542984a84ba045`.

No E187 ref/artifact is available for audit.

### Consequence

E188 may verify the inherited E185/E186 arithmetic and state what a hardened E187 must
contain, but it may not infer that E187 satisfies those requirements.

## 2. Parent / candidate cost arithmetic recomputation

Use the frozen F86 grouped model inherited by E185/E186:

- K3 young dense: `115.6u`;
- K3 old dense: `106.8u`;
- thin/elementwise: `24.8u`;
- covariance: `7.1u`;
- closure + birth: `5.7u`.

Therefore:

`C_dense_parent = 115.6 + 106.8 = 222.4u`.

`C_fixed = 24.8 + 7.1 + 5.7 = 37.6u`.

Grouped parent total:

`C_parent_grouped = 222.4 + 37.6 = 260.0u`.

F86 separately reports a rounded headline steady-state total of `260.1u`. These two
numbers must not be mixed in a final receipt.

Budget relation:

`B = 1024u`.

Hard cap:

`0.135B = 138.24u`.

Maximum admissible transformed dense bill:

`C_dense_candidate,max = 138.24 - 37.6 = 100.64u`.

Necessary aggregate transformed ratio:

`r_required <= 100.64 / 222.4 = 0.4525179856`.

E185 mechanism gate:

`r_TA <= 0.42`.

If, and only if, that `0.42` applies to the full `222.4u` dense parent bill:

`C_dense_candidate = 0.42 * 222.4 = 93.408u`.

Modeled all-in candidate:

`C_candidate_modeled = 37.6 + 93.408 = 131.008u`.

As a budget multiple:

`C_candidate_modeled / B = 131.008 / 1024 = 0.1279375B`.

Modeled cap headroom:

`138.24 - 131.008 = 7.232u`.

Modeled grouped-parent saving:

`260.0 - 131.008 = 128.992u`.

### Cost arithmetic verdict

**PASS for the inherited planning arithmetic.**

However this does not authorize execution. The candidate formula is valid only if the
production mapping proves that the `0.42` ratio covers the same full `222.4u` bill.

## 3. Dense-product mapping and fallback audit

E186 required a complete namespace/event map for every dense product included in the
`222.4u` denominator.

The correct production accounting identity is:

`C_candidate = C_fixed + sum_i(C_i * r_i) + sum_j(C_fallback_j)`

where:

- transformed operations `i` use the frozen TA implementation;
- fallback operations `j` are billed at their actual parent/fallback cost;
- the transformed + fallback parent-side costs reconcile exactly to the frozen dense
  parent ledger.

A bundle ratio computed from only a selected subset is not sufficient.

### What is currently inspectable

E185 says the synthetic bundle uses hot-path products "selected from":

- young transport;
- hub contraction;
- old-leg reconstruction/shared contraction;
- join projection/rotation where shape-compatible.

That language does **not** prove full production coverage.

E186 therefore required:

1. every dense production event/namespace enumerated;
2. each event labelled `TA`, `UNCHANGED`, or `FALLBACK`;
3. all fallback costs charged;
4. exact reconciliation to one machine-readable parent ledger.

### E188 result

Because E187 is not available, E188 cannot verify that:

- all dense product families are mapped;
- rectangular/non-square shapes have fixed TA rules;
- padding and unpadding are billed;
- unsupported shapes use an explicitly charged fallback;
- fallback events do not invalidate the `0.42` aggregate ratio;
- the map reconciles to exactly `222.4u` or to a newer exact parent ledger.

**Gate result: FAIL / UNVERIFIED.**

This alone blocks AUTHORIZE.

## 4. Exact-small gate audit

A valid hardened protocol must freeze:

- exact bilinear/trilinear coefficient tables or a deterministic generator;
- exact base cases;
- exact recursion/blocking rules;
- a rational/integer small fixture;
- an equality check proving the decomposition computes `AB` exactly;
- immutable fixture and expected/result hashes.

The exact-small gate must verify the actual frozen implementation, not merely the
literature formula or an abstract rank count.

E185 contains an exact-small symbolic/rational requirement, but E187 must specify the
actual decomposition used by the owner.

Because E187 is absent, the exact-small implementation identity cannot be checked.

**Gate result: FAIL / UNVERIFIED.**

## 5. Production float32 numerical gate audit

This was a blocking E186 requirement.

A float64 identity gate at `<=2e-12` is not sufficient for V29 because production
arithmetic is float32 and trilinear aggregation may use cancellation-heavy linear
combinations.

A hardened protocol must freeze before execution:

- product-family-specific float32 error metric;
- absolute and relative norms;
- zero / near-zero denominator handling;
- D3 error metric;
- off-diagonal D21 error metric;
- fixed threshold(s);
- the independent parent numerical reference used to justify those thresholds.

No threshold may be selected after observing TA output.

Because E187 is unavailable, E188 cannot verify the existence or adequacy of the
production float32 gate.

**Gate result: FAIL / UNVERIFIED.**

## 6. Runtime projection audit

E185's original wording — that the implementation should "retain a path" to
`<=0.400 s` residual — was correctly identified by E186 as too qualitative.

A hardened protocol must freeze a deterministic runtime rule containing:

1. parent residual-time baseline and source/hash;
2. bundle event counts;
3. production event-count scaling;
4. explicit integration/runtime overhead;
5. one numeric terminal threshold;
6. immutable timing evidence required in the owner receipt.

The verifier must be able to recompute runtime PASS/FAIL without owner judgment.

No inspectable E187 artifact exists, so this hardening cannot be verified.

**Gate result: FAIL / UNVERIFIED.**

## 7. Immutable evidence design audit

A single irreversible owner-run requires enough artifacts for verification without
re-running the hypothesis.

At minimum the hardened design must preserve:

### Inputs

For every case/product event:

- raw input matrices;
- shape;
- dtype;
- raw-array SHA-256;
- file SHA-256;
- byte count;
- seed/provenance;
- namespace/event identity.

### Frozen implementation identity

- owner protocol SHA;
- implementation SHA;
- coefficient-table SHA;
- generated-table source/hash if applicable;
- base-case / blocking / fallback config SHA.

### Outputs

- parent product outputs;
- candidate product outputs;
- D3 vectors;
- D21 vectors;
- float32 and float64 error metrics;
- cost namespace ledger;
- runtime evidence;
- replay hashes.

### Manifest

One immutable manifest must enumerate every input/output/config artifact and hash.

### Replay

The authorized workflow may replay the same frozen inputs once and require bitwise
identity of candidate outputs/ledgers/hashes. This is replay evidence, not a second
hypothesis run.

### Independent verifier

The verifier must be able to recompute every gate from committed protocol + immutable
owner artifacts only, without changing the candidate or selecting a new decomposition.

E185 originally required outputs but not a complete immutable input/config contract.
E186 explicitly hardened this requirement.

Since E187 is missing, E188 cannot confirm that the design was implemented.

**Gate result: FAIL / UNVERIFIED.**

## 8. Separation from E178 / H180 / E181

### What is established for E185

E185 head `10f5f0ab...` directly descends from E177
`e1536d36...`, not E178, E180 or E181.

Mechanistically:

- E178 is a higher-order AGO gauge lane;
- H180/E181 replace inherited K3 state with an approximate rank-`3n` symmetric CP
  carrier;
- H185 keeps the V29 state and cumulant representation unchanged and replaces only the
  exact matrix-multiplication algorithm.

Therefore the **E185 hypothesis class itself** is not a rescue of E178/H180/E181.

### What cannot be established for E187

Without the E187 commit, E188 cannot verify that the hardened successor:

- preserves the E185 exact-algorithm-only scope;
- does not import CP projection/rank compression;
- does not import AGO/higher-order-gauge logic;
- does not use E181 implementation/results as a rescue;
- does not change source ancestry.

A future E187 review must inspect its actual parent SHA and diff.

**Gate result for E185 class: PASS.**  
**Gate result for E187 concrete protocol: UNVERIFIED.**

## 9. One-run authorization requirements

A future single target-free owner-run can be authorized only if an immutable E187 commit
exists and E188-equivalent review verifies all of the following before execution:

1. E187 ancestry is E185/E186-compatible and does not descend from E178/H180/E181.
2. Exact TA decomposition/coefficient/base-case/blocking/fallback identity is frozen.
3. Exact-small rational/integer identity gate is executable from frozen artifacts.
4. One exact machine-readable parent ledger is frozen.
5. Every dense event contributing to the denominator is mapped.
6. Every fallback is explicit and billed.
7. Candidate cost is recomputed from the complete map, not a sampled bundle.
8. Full mapped parent denominator reconciles to the parent ledger.
9. Aggregate transformed cost and fallback cost imply all-in `<=0.135B`.
10. Production float64 numerical gate is frozen.
11. Production float32 product/D3/D21 gate is frozen with predeclared thresholds.
12. Hard runtime projection formula is frozen.
13. Immutable input/output/config manifest design is complete.
14. Deterministic replay is part of the one authorized workflow.
15. Separate independent-verifier protocol is frozen before owner results exist.
16. Target/scorer/submission/leaderboard access firewall is frozen.
17. One-run arm explicitly states `authorized_owner_runs = 1` and terminal no-rescue
    semantics.

Any missing item is pre-run REJECT.

## 10. Final E188 verdict

### Parent/candidate cost arithmetic

**PASS for inherited E185 planning arithmetic.**

At full `222.4u` coverage and ratio `0.42`, the modeled candidate is
`131.008u = 0.1279375B`, leaving `7.232u` below the `0.135B` cap.

### Dense mapping / fallback

**FAIL / UNVERIFIED.** No E187 artifact is available to prove full coverage and exact
fallback billing.

### Exact-small

**FAIL / UNVERIFIED.** No frozen E187 implementation identity is available.

### Float32 gate

**FAIL / UNVERIFIED.** This was mandatory after E186 and cannot be inferred from E185.

### Runtime projection

**FAIL / UNVERIFIED.** No hardened deterministic runtime formula is inspectable.

### Immutable evidence

**FAIL / UNVERIFIED.** No E187 manifest/input/config contract can be audited.

### Separation from old ideas

**PASS for H185/E185 as a class; UNVERIFIED for the missing E187 concrete successor.**

# Decision

**REJECT. DO NOT LAUNCH THE OWNER RUN.**

The rejection is procedural and evidence-based: the hardened protocol requested for E187
is not present in the accessible repository state, so independent authorization would
require assuming precisely the gates E186 said must be frozen.

No scientific run or repository code was executed. No baseline, canonical ledger,
submission, scorer or leaderboard state was changed.
