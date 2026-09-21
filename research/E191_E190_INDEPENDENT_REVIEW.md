# E191 INDEPENDENT REVIEW — E190 raw-FLOP evidence for E187

Date: 2026-09-22  
Branch: `review/e191-e190-independent-review-20260922`  
Review base: E187 head `06fbb08fb9ece3b5b3d8da7b60fee331030a044f`  
Mode: **READ-ONLY EVIDENCE REVIEW — NO SCIENTIFIC RUN, NO REPOSITORY CODE EXECUTION, NO BASELINE/LEDGER MUTATION, NO SUBMISSION**

## 0. Decision

**KEEP E187 AT PROTOCOL NO-GO. DO NOT PROMOTE TO HARDENING_READY.**

The reason is narrow: the exact F86 raw FLOP ledger required by E186/E187 is still not
independently evidenced by an immutable artifact visible in the reviewed repository/source
lineage.

The pinned F86 Git objects are immutable, but the pinned public log contains only rounded
unit displays. The audit script obtains an exact `ctx.flops_used` value at runtime and
then prints rounded representations; it does not persist the exact integer.

No committed E190 branch/ref/artifact is visible in `tim8es/arc-whitebox` at review time.
Therefore any E190 claim of a newly found raw integer cannot be independently tied to an
immutable source object from this repository state.

## 1. Pinned F86 parent identity

E187 correctly pins the intended parent to:

- repository: `504aldo/whest-p2-cumulant-k3`;
- commit: `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`;
- estimator:
  `estimators/estimator_v29_ns.py`,
  Git blob `f91df783b83cb5fae0af57a16799c5df81891bd2`;
- audit harness:
  `harness/audit_v29_ns.py`,
  Git blob `279d8e0308360fde7616d56f8e8cc2705b529898`;
- published log:
  `docs/audit_v29_ns_d0.log`,
  Git blob `a689ef69fd64bed7765cb93ce4910c3fedcbd04a`;
- semantic event:
  **dump 0, call 2, steady-state ledger**, with call 1 excluded because it uses
  `STRASSEN_FIRST`.

This is the correct F86 parent lineage used by E177/E185/E187.

## 2. What the immutable public log actually contains

The immutable F86 log contains for call 2:

`C/B=0.2540 (260.1 units) ... ops=13121`

and then family/group rows printed at two decimal places, including:

- young K3: `115.61u`;
- old K3: `106.83u`;
- grouped display sum used by E187: `260.06u`;
- dense displayed sum: `222.44u`.

These values are immutable **as text in Git blob
`a689ef69fd64bed7765cb93ce4910c3fedcbd04a`**.

They are not exact raw FLOP integers.

## 3. Why rounded units cannot be substituted for a raw integer

The pinned audit source proves the distinction.

In `harness/audit_v29_ns.py`:

`C = float(ctx.flops_used)`

captures the raw runtime count.

But the script prints only:

- `C / B` with format `.4f`;
- total `C / UNIT` with format `.1f`;
- family/group `c / UNIT` with format `.2f`.

Therefore the exact integer `C` is discarded from the committed textual output.

Likewise, a value such as `260.06u` is a source-resolution sum of rounded display rows,
not an exact replacement for `ctx.flops_used`.

A claimed raw integer obtained by multiplying `260.06`, `260.1`, `222.44`, or any
other printed unit value by `2^31` is a reconstruction from rounded data and **does not
satisfy E186 G2 / E187 G2**.

## 4. Source-tree check

At pinned public commit
`18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, the recursive Git tree contains the
F86 audit evidence under the relevant audit naming only as:

1. `docs/audit_v29_ns_d0.log`
   blob `a689ef69fd64bed7765cb93ce4910c3fedcbd04a`;
2. `harness/audit_v29_ns.py`
   blob `279d8e0308360fde7616d56f8e8cc2705b529898`.

The committed tree does not contain a raw `op_log`, serialized
`ctx.flops_used`, or another exact-count receipt for that run.

Thus the pinned F86 Git commit itself cannot independently recover the exact raw integer.

## 5. E190 immutability / lineage finding

At review time, the `arc-whitebox` repository exposes E187 at:

`06fbb08fb9ece3b5b3d8da7b60fee331030a044f`

and does not expose a committed branch/ref/artifact matching E190.

Consequently E191 cannot verify:

- what exact integer E190 claims;
- what object contains that integer;
- whether that object predates or derives from rounded E187 numbers;
- whether it belongs to dump0/call2 rather than warm call1 or another V29 lineage;
- whether its exact dense-subtotal ledger can be recomputed.

**Result: E190 raw-integer claim is not independently immutable/verifiable in the
available repository state.**

## 6. Is one total raw integer sufficient for HARDENING_READY?

**No.**

Even if an exact total `ctx.flops_used` integer were supplied, H185 cost gating uses the
dense-parent denominator and coverage map, not only the whole-estimator total.

E187 requires independent verification of:

- exact total parent FLOPs;
- exact dense K3 parent FLOPs for the eleven mapped namespaces;
- exact fixed/remainder FLOPs;
- reconciliation of those exact values to the same `13121`-operation call-2 ledger.

The rounded `222.44u` dense value cannot serve as the exact denominator for the final
`C_TA_dense / C_parent_dense <= 0.42` receipt.

Therefore a lone exact total integer, without the immutable raw namespace ledger from the
same F86 run, is insufficient to promote E187.

## 7. Exactly missing evidence

There is **one** missing evidence object:

> **An immutable raw F86 call-2 flopscope receipt/op-log from the pinned
> `504aldo@18c17e2...` V29 namespace run that contains the exact integer
> `ctx.flops_used` and exact per-operation or per-namespace FLOP integers, so an
> independent verifier can recompute the exact dense-K3 subtotal, fixed subtotal and
> total, and can prove that the object is dump0 / second-predict / steady-state
> `ops=13121` under the pinned estimator and audit-harness blobs.**

Acceptable immutability requires a content-addressed/append-only identity (for example a
Git blob/commit or equivalent immutable artifact hash) for that raw receipt itself.

No derived integer reconstructed from `260.1u`, `260.06u`, `222.44u`, family rows,
or `C/B=0.2540` satisfies this evidence requirement.

## 8. Promotion rule

E187 may change from `PROTOCOL_NO_GO` to `HARDENING_READY` only when the single raw
evidence object above is committed/referenced and an independent review verifies all of:

1. it belongs to the pinned F86 lineage and dump0 call2;
2. exact total equals the sum of exact ledger entries;
3. exact dense subtotal equals the sum of the eleven E187 dense namespaces;
4. exact fixed subtotal plus exact dense subtotal equals the exact total;
5. formatting those exact values is consistent with the published F86 rounded displays.

This promotion would remove only G2. It would **not** constitute scientific GO or
automatically authorize a target-bearing run.

## 9. Final verdict

- Correct F86 lineage identified: **PASS**.
- Pinned public Git objects immutable: **PASS**.
- Published rounded units are exact raw integer evidence: **FAIL**.
- E190 claimed raw integer independently immutable/traceable: **UNVERIFIED**.
- Exact dense-parent denominator available: **FAIL**.
- Data sufficient for `HARDENING_READY`: **NO**.

**E187 remains PROTOCOL NO-GO.**

No scientific run, estimator execution, baseline/ledger mutation, submission or
leaderboard action was performed.
