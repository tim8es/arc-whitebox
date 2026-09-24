# R356 — proof-grade static recovery attempt for H185 dense-parent FLOP denominator

**Status:** COMPLETE  
**Decision:** **NO_GO — PROOF_GRADE_STATIC_RECONSTRUCTION_NOT_CLOSED**  
**Authorization:** **NONE — R356 cannot authorize H185, HARDENING_READY, or any execution**  
**Mode:** immutable-source / static billing audit only; no estimator, test, benchmark, rerun, or Actions execution  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `review/r356-h185-static-dense-flops-reconstruction-20260924`

## 1. Result

R356 does **not** recover proof-grade exact integer FLOP totals for all eleven H185 dense namespaces or for the fixed remainder of F86 dump0/call-2.

The source is sufficiently explicit that exact namespace costs are statically derivable **for a fully pinned process configuration and predecessor state**. However, the persisted F86 evidence does not immutably pin all runtime inputs that select the operation schedule and final FlopScope billing configuration.

Because the task requires stopping on any runtime-dependent or attribution ambiguity, R356 stops at that point rather than presenting default-configuration calculations as the actual F86 ledger.

The exact whole-parent total recovered by E190 remains valid persisted evidence for this audit:

[
C_{mathrm{parent,total}}=558{,}473{,}140{,}719.
]

It does not determine the exact dense/fixed split.

## 2. Live immutable lineage

### E187

Branch: `research/e187-h185-protocol-hardening-20260922`  
Live head: `06fbb08fb9ece3b5b3d8da7b60fee331030a044f`

Relevant artifacts:

- `research/E187_H185_PROTOCOL_REVISION.md` — blob `d623a9348518c0afe2869fc89f44a746960e81f5`
- `research/e187/E187_H185_PROTOCOL_LOCK.json` — blob `215187db7fb4a3ba391a1229e48ce6a482bebd97`
- `research/e187/E187_PARENT_LEDGER.json` — blob `33699fbfa47e23ffef99b6a99e064aa130100671`

E187 freezes eleven dense namespaces:

`young_transport, hub, shared, old_legs, j_rf, j_rot, j_proj, j_tier2, j_qc, j_core, qc_transport`.

The published grouped rows are only:

- dense: `222.44u`
- fixed/remainder: `37.62u`
- total: `260.06u`

and E187 explicitly forbids recovering the exact denominator by reversing those rounded values.

### E190

Branch: `research/e190-cost-evidence-recovery-20260922`  
Live head: `7145df65c84970eeab5dbfb48d1045eaee8be7ca`

Artifacts:

- `research/E190_COST_EVIDENCE_RECOVERY.md` — blob `976ebe39a06092bbc5838ea3f249cc5348bc87a5`
- `research/e190/E190_RECOVERED_PARENT_LEDGER.json` — blob `4ba395635e08f9fafd592edd8978207341d7d42a`

E190 recovers the exact whole total from immutable E136 evidence:

`558473140719` FLOPs.

E190 explicitly records:

- exact dense raw FLOPs recovered: **false**
- exact fixed/remainder raw FLOPs recovered: **false**
- exact per-namespace raw FLOPs recovered: **false**

### E191

Branch: `review/e191-e190-independent-review-20260922`  
Live head: `37488d6e9abd52c625cde9506f541dcd85c70701`

Artifact:

- `research/E191_E190_INDEPENDENT_REVIEW.md` — blob `04a7407a0b93580b9868ffcc28d461ee91c4f89a`

E191 requires the exact dense subtotal, exact fixed subtotal, and same-ledger reconciliation to the exact total. A lone exact whole total is insufficient.

R351 later re-audited this state and reached the same conclusion.

## 3. Exact pinned F86 source

Repository: `504aldo/whest-p2-cumulant-k3`  
Commit: `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`

Immutable files inspected:

- namespaced estimator `estimators/estimator_v29_ns.py`
  - blob `f91df783b83cb5fae0af57a16799c5df81891bd2`
- plain V29 `estimators/estimator_v29.py`
  - blob `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`
- audit harness `harness/audit_v29_ns.py`
  - blob `279d8e0308360fde7616d56f8e8cc2705b529898`
- committed audit log `docs/audit_v29_ns_d0.log`
  - blob `a689ef69fd64bed7765cb93ce4910c3fedcbd04a`
- namespace generator `generators/make_v29_ns.py`
  - blob `6c0e439eaeefcb2e06991cb86d9bda3b174fc30d`
- rounded figure CSV `docs/figures/fig2_cost_anatomy_v29.csv`
  - blob `a70f696b5e525aaa70522eb0a02189e2c88dc5e9`

Harness semantics are explicit:

1. instantiate one estimator;
2. call `predict` once as warm-up;
3. call `predict` a second time on the same estimator;
4. call 2 is the steady-state ledger;
5. `C=float(ctx.flops_used)`;
6. exact runtime `ctx.op_log` is grouped by the last namespace segment;
7. only formatted text is committed.

The committed call-2 log records:

- `ops=13121`
- total display `260.1u / 0.2540B`
- grouped display `222.44u + 37.62u = 260.06u`
- all 26 family call counts
- eleven dense family call-count total: **6172**

The eleven displayed dense family rows sum to `222.45u`, not `222.44u`, confirming that family display rows are individually rounded and cannot be summed to recover the exact dense integer.

## 4. Exact FlopScope 0.12.1 billing semantics

Primary source:

Repository: `AIcrowd/flopscope`  
Commit: `b599f015b0bc005b1edb6d7a1b10e0814675e693`  
`pyproject.toml` blob `57ce0e5bedc56999104209c84c3b82de66e50058` identifies version `0.12.1`.

Relevant immutable source:

- `src/flopscope/_budget.py` — `f4d32d9d6a10b7292ba2e3c6fdbd8c68955248b8`
- `src/flopscope/_flops.py` — `d8103735c03f08ec915b7846bc877ad57d47fa03`
- `src/flopscope/_registry.py` — `de7388e5649224360ca3fa8e5f62b4ad5ebcc596`
- `src/flopscope/_weights.py` — `b221c25484a645e9ef9b54529c2ab69d2509e477`
- `src/flopscope/_dtype_billing.py` — `87c5789569320593a6054e0ca24d3d9e88df8b8b`
- `src/flopscope/_array_ops.py` — `d112b1e96e50cfdf0674c3230d291b622191b86d`
- `src/flopscope/_pointwise.py` — `5d8f9210ff23979ef9658897d8cd1a02127b33c4`
- `src/flopscope/numpy/linalg/_decompositions.py` — `4c10967cf0b2dc7fcad8a7626f403c75faa6eb39`
- packaged default weights `src/flopscope/data/default_weights.json`
  - blob `5f7074f76d56b92180c8a1553a3ebe3a4c1d43f5`

### Per-op integer

`BudgetContext._charge_op` computes:

[
	ext{adjusted cost}
=
operatorname{int}
(	ext{base flop cost}
	imes 	ext{dtype rate}
	imes 	ext{complex factor}
	imes 	ext{operation weight}).
]

The exact adjusted integer is stored in `OpRecord.flop_cost`, together with operation name, shapes, namespace and resolved dtype.

For ordinary real float32 operations under the packaged default table, the inspected relevant entries have rate/weight 1 for `matmul`, `add`, `subtract`, `multiply`, `copyto`, `sum`, `reshape`, and `linalg.qr`; `empty` has weight 0. Float32 dtype rate is 1.

For a 2-D matmul ((m,k)@(k,n)), FlopScope's exact base formula is:

[
2mkn-mn.
]

For reduced QR, its exact source formula is also integer-valued and shape-defined.

Thus, **given a completely fixed operation stream, shapes, dtypes and active billing table, the ledger is statically calculable exactly.**

## 5. Partial static consistency checks are possible, but are not the F86 proof

Several simple namespaces illustrate that the source/billing rules are sufficiently concrete.

Under the **source-default estimator configuration plus packaged default FlopScope billing**, the common shape

[
(1024,1024)@(1024,384)
]

or its transposed-output analogue costs:

[
2(1024)(1024)(384)-(1024)(384)
=
804{,}913{,}152.
]

Conditional source-default examples:

- `qc_transport`: one such matmul → candidate `804,913,152`
- `j_qc`: ten such matmuls → candidate `8,049,131,520`
- `j_proj`: twenty such matmuls → candidate `16,098,263,040`

For `j_core`, the default source path plus its exact F86 call count of 59 is consistent with ten join events:
- first join: 5 billed operations;
- next nine: 6 billed operations each;
- total: (5+9cdot6=59).

Using the source matmul and pointwise formulas gives the conditional default-path `j_core` candidate:

[
6{,}047{,}514{,}624.
]

These values are consistent with the published two-decimal family displays.

**They are not promoted to actual F86 exact namespace integers.** Doing so would assume the runtime configuration that R356 is required to prove.

## 6. First proof-grade blocker: F86 estimator schedule is runtime-configurable and the executed values are not immutably recorded

The pinned namespaced V29 reads operation-count/shape-affecting environment variables at import/class-definition time, including:

- `V17_NO_FEED`
- `V17_NO_WK431`
- `V17_NO_REGEN`
- `V18_NO_FB`
- `V19_FULL_LAST`
- `V21_NO_CONFINE`
- `V21_QPASS`
- `V19_NO_SRC_LAST`
- `V26_STRASSEN`
- `V26_STRASSEN_HUB`
- `V29_CPRE_LEV`
- `V28_STRASSEN_SB`
- `V26_STRASSEN_MIN`
- `V28_STRASSEN_FIRST`
- `V28_STRASSEN_FUSE_P`
- `V21_AGE_OLD`
- `V21_R_OLD`
- `V24_AGE_OLD2`
- `V24_R_OLD2`
- `V24_QPASS2`.

These values alter one or more of:

- Strassen recursion depth and dense fallback;
- fused-leaf selection;
- matrix/rank shapes;
- range-finder/QR multiplicities;
- source confinement timing;
- nested-tier timing;
- last-layer source work;
- feedback/regen work.

The F86 audit harness does not set these variables. Its persisted invocation is only documented as:

`uv run python audit_v29_ns.py [dump_index]`.

No immutable F86 environment manifest recording the values/absence of the cost-affecting `V*` variables was found in E187/E190/E191 or the pinned upstream F86 artifacts.

The exact family call counts constrain the actual path, but R356 found no committed proof that those counts uniquely determine every possible environment setting and every source-level operation shape. Proving uniqueness by assuming source defaults would violate the requested proof standard.

## 7. Second proof-grade blocker: active FlopScope billing configuration is runtime-configurable and not recorded for F86

FlopScope 0.12.1 automatically loads packaged official weights, **unless runtime environment changes that behavior**.

Its source explicitly supports:

- `FLOPSCOPE_DISABLE_WEIGHTS`
- `FLOPSCOPE_WEIGHTS_FILE`.

A custom weights file can change operation weights and dtype rates while leaving the estimator source and operation count unchanged.

No immutable F86 process receipt was found that records:

- absence/value of `FLOPSCOPE_DISABLE_WEIGHTS`;
- absence/value and content hash of `FLOPSCOPE_WEIGHTS_FILE`;
- the effective active weight/dtype-rate table used by the F86 audit.

The packaged default table is immutable and known, but R356 cannot substitute “packaged defaults were probably active” for proof of the actual recorded F86 execution.

The E136 workflow used by E190 to recover the exact whole total contains no explicit `FLOPSCOPE_*` override and no estimator `V*` override in its workflow YAML. That supports the E190 whole-total bridge already accepted by R351, but it is a **different execution environment** from the local F86 namespace audit and does not create an exact F86 per-namespace receipt.

## 8. Call-2 is stateful with respect to call 1

The audit does not run call 2 on a fresh estimator.

Both `_Pool` and `_Strassen` scratch pools persist on the estimator across calls. Pool allocation/growth performs billed operations such as `copyto` and `reshape`; whether they occur in call 2 depends on what call 1 allocated.

The source explicitly selects a shallower first-call level:

[
s_{mathrm{lev}}
=
egin{cases}
min(	ext{STRASSEN_LEVELS},	ext{STRASSEN_FIRST}), & 	ext{call 1}\
	ext{STRASSEN_LEVELS}, & 	ext{call 2}.
end{cases}
]

Therefore a proof-grade call-2 reconstruction must statically reconstruct **both** calls in order and carry the exact pool state into call 2.

This is possible in principle once the runtime configuration is fully frozen. It is not possible proof-grade from the currently persisted F86 evidence because the schedule/billing configuration above is not immutably pinned.

## 9. Why the exact whole total and exact call counts do not solve the split

Known exact facts:

- whole total: `558,473,140,719`;
- call-2 operations: `13,121`;
- exact family call counts, including 6,172 calls across the eleven dense namespaces.

Missing exact facts:

- per-operation name/shape/dtype/cost from the actual call-2 log;
- exact per-namespace integer sums;
- exact dense subtotal;
- exact fixed subtotal.

One exact sum plus operation counts does not uniquely identify the component integer sums.

The rounded rows cannot supply the missing equations: they are intentionally many-to-one formatting outputs, and their independent rounding is already demonstrated by the `222.45u` family-row sum versus the `222.44u` grouped dense display.

R356 therefore performs **no rounded-value inversion**.

## 10. Reconciliation status

| Required proof item | R356 result |
|---|---|
| exact whole parent total | **PASS** — `558,473,140,719` from E190 |
| exact call-2 operation count | **PASS** — `13,121` |
| exact eleven dense family call counts | **PASS** — persisted F86 text; sum 6,172 |
| exact FlopScope formulas/API | **PASS** — 0.12.1 source inspected |
| exact F86 estimator/harness source | **PASS** |
| actual F86 runtime estimator knob state | **MISSING / AMBIGUOUS** |
| actual F86 active FlopScope weight configuration | **MISSING / AMBIGUOUS** |
| exact call-1-derived pool state for actual configuration | **NOT PROVABLE WITHOUT ABOVE** |
| all 13,121 actual op identities/shapes/dtypes | **NOT PERSISTED / NOT PROOF-GRADE RECONSTRUCTED** |
| exact 11 per-namespace integers | **FAIL — NOT RECOVERED** |
| exact dense subtotal | **FAIL — NOT RECOVERED** |
| exact fixed/remainder subtotal | **FAIL — NOT RECOVERED** |
| exact dense + fixed = whole total | **FAIL — COMPONENTS MISSING** |
| H185 exact dense denominator | **FAIL — STILL MISSING** |

## 11. Precise minimal missing fact for the static route

For a proof-grade **static** reconstruction, the minimum additional immutable runtime evidence is a content-addressed F86 invocation/billing manifest for the process that produced `docs/audit_v29_ns_d0.log`, recording:

1. exact values or explicit absence of every cost-affecting estimator environment variable listed in §6;
2. exact effective FlopScope billing configuration:
   - `FLOPSCOPE_DISABLE_WEIGHTS`;
   - `FLOPSCOPE_WEIGHTS_FILE`;
   - if custom, the file bytes/hash;
   - or an explicit effective-table hash proving packaged `default_weights.json` blob `5f7074...` was active;
3. exact FlopScope/NumPy runtime identity for that process.

Given those facts, the pinned harness defines the initial estimator state and the two-call ordering, so a future static proof could enumerate call 1, carry pool state forward, enumerate all call-2 operations, and reconcile exact namespace sums to the E190 whole integer.

An alternative sufficient artifact remains the object already identified by E191/R351: the immutable raw call-2 `ctx.op_log` containing each operation's name, shapes, namespace, dtype and exact `flop_cost`. No such artifact is present.

Neither missing artifact may be manufactured by a new run under R356.

## 12. Final decision

**NO_GO — exact H185 dense-parent denominator remains unproven.**

R356 found that source-level exact reconstruction is feasible in principle but **not proof-grade for the historical F86 dump0/call-2 execution from currently committed evidence**.

The blocker is not arithmetic precision. It is missing immutable runtime/billing state needed to prove which exact source path and billing table generated the historical namespace ledger.

Accordingly:

- do not set E187/H185 to `HARDENING_READY`;
- do not use conditional default-path namespace integers as the H185 denominator;
- do not infer exact dense or remainder counts from rounded displays;
- do not authorize an H185 owner/candidate run;
- no scientific conclusion about H185 is made.

## 13. Execution accounting

R356 performed only static repository/source inspection.

- estimator executions: **0**
- test executions: **0**
- benchmark executions: **0**
- reruns/recovery executions: **0**
- GitHub Actions: **0**
- dependency/data downloads or installs: **0**
- target reads: **0**
- private/holdout/full access: **0**
- paid resources: **NO**
- submissions: **0**
- E187/E190/E191/E193 edits: **0**
- R320 edits: **0**
- main/PR/control/queue edits: **0**
- H185 authorization: **NONE**
