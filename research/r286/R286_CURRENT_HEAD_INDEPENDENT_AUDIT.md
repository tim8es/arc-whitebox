# R286 - independent current-head audit of PR #35

Status: COMPLETE with findings.
Owner: r281-independent-current-head-audit
Run ID: R286-pr35-current-head-adversarial-verify-20260923

## Pinned source

This audit independently checked the exact current PR #35 head requested by the
coordinator:

- PR #35 head: `05733f3bfa6730124c4601a918bcc6d401719e09`
- PR base/main at audit start: `b5b988f8ec49a5ec473d59fcbfdfaf8c4350c850`
- PR state at source pin: OPEN, unmerged, mergeable/clean
- production analyzer: `scripts/arc_workflow_preflight.py`
- analyzer Git blob SHA-1: `f9b01ba259cd57bd1692fbfc904585b05f561000`
- analyzer SHA-256: `1f73f557d943dc6b4fb4d42b2a5935f1d627082b292d8465f5018794dc8a38ce`
- tests Git blob SHA-1: `c94c6e7521a612d496f544eec19c863bc05bbb73`

R281 receipt:
- commit/head `05733f3bfa6730124c4601a918bcc6d401719e09`
- receipt blob `6e80b2b6f8b2e11a1eba7197403faa87396af8fc`
- receipt SHA-256 `6251bc55894ffec016f6e185c4017c757d6bd80b33cc7746673ee68fe7f35de6`

R283 receipt:
- commit `55ee4876459d338de136fa4be253e0c089c69697`
- receipt blob `be9a62eb0e3077407089db30969202ec548184ad`
- receipt SHA-256 `fb1002ca8e67d4d1cc791443a70559a4037ae0bba260d3121050746839952180`

## Method

Only small synthetic workflow/generator strings were passed to the current analyzer's
static `check_contract()` logic. No workflow, generator, fixture, estimator or benchmark
was executed. R286 did not edit PR #35 or its tests, post a PR comment/review, trigger
Actions, merge, or access benchmark data.

All exact reproduction strings, expected/observed outcomes and per-input SHA-256 hashes
are retained in:

- `research/r286/R286_REPRODUCTION_INPUTS.json`
- commit `8a5e2af57c86f97f5bda37b807974ba5586571a5`
- Git blob SHA-1 `4abcc3af49bb937337aabafaabeac6aeb9e49d54`
- SHA-256 `081550bac3585f3230a8d7f7bab4f058c254203dbfe89cd324710119e2f6e9ab`

## Exact four-case R283 matrix

| R283 case | Expected fail-closed | Current head observed | Result |
|---|---|---|---|
| N1 block-scalar/comment fake checkout text | REJECT | REJECT | CLOSED for exact R283 input |
| N2 double-space `git merge-base  --is-ancestor` | REJECT | PASS; `full_history_required=false` | STILL FALSE PASS |
| N3 comment bracket decoy + real `d.get("ghost")` | REJECT | REJECT | CLOSED for exact R283 input |
| N4 generator conditional manifest rebind | REJECT | PASS | STILL FALSE PASS |

### N1 - exact R283 input now rejects

Exact workflow SHA-256:
`980a5dc6ed9321f1ae3b39356f2554810d5f43723570203e8472c086b56fbecb`.

Observed error: the ancestry guard has no qualifying preceding checkout with
`with.fetch-depth: 0`.

R281's F1 change therefore closes the exact R283 N1 string. The relevant current
implementation is `_checkout_steps`, `_checkout_has_full_history`, and
`require_full_history_for_ancestry` in approximately
`scripts/arc_workflow_preflight.py:243-365`.

However, the underlying raw-text YAML issue is not fully closed; see E1 below.

### N2 - whitespace-equivalent ancestry guard still passes

Exact workflow SHA-256:
`c7ee2a6b32dde13575ed5ad981b3b964cb5095a0ef0b6d1dd1399dfff20ad894`.

The workflow contains:

`git merge-base  --is-ancestor "$P" HEAD`

with two spaces and no checkout.

Observed: **PASS** and `full_history_required=false`.

Cause remains exact raw substring checks for
`"git merge-base --is-ancestor"` in `require_full_history_for_ancestry` and in
the returned status flag. Relevant current range:
`scripts/arc_workflow_preflight.py:326-365`, plus the
`full_history_required` field in `check_contract` around `:484-510`.

Expected fail-closed behavior: recognize supported whitespace-equivalent ancestry
commands, or conservatively reject a merge-base/is-ancestor invocation whose semantics
cannot be proven.

### N3 - exact R283 input now rejects

Exact workflow SHA-256:
`551178ee909700810030efc0d86fcb4b1f620d66b4af94e68346e2e3cefdcf95`.

Observed: **REJECT**, `unsupported manifest access 'get' on 'd'`.

R281's direct unsupported-method guard therefore closes the exact R283 N3 input.
Relevant current range:
`scripts/arc_workflow_preflight.py:397-475`.

The broader manifest-variable provenance issue is not fully closed; see E2/E3.

### N4 - generator conditional dataflow still passes

Generator SHA-256:
`a724e374d274bd63af24de33517ecb6d3be7b3f114448b8e74829092581cb3ec`.

The generator builds `m={"seed":1}`, then executes a syntactic `if True: m={}`
before serializing `m`. The workflow reads `d["seed"]`.

Observed: **PASS**.

The current `_process` handles Assign, AnnAssign, expression Call and Return, but
silently ignores unsupported statement kinds such as `ast.If` and `ast.Delete`.
`contract()` then trusts the stale pre-write environment. Relevant ranges:
- `scripts/arc_workflow_preflight.py:99-158`
- `scripts/arc_workflow_preflight.py:202-226`

Expected fail-closed behavior: reject unsupported control flow on the
manifest-producing dataflow unless every reachable state/write path is modeled.

## Narrow current-head edge cases

### E1 - structural YAML false checkout remains

Workflow SHA-256:
`06abad97cc2bc1eff008a531cc04761132f1a53b3a37058ac79a763f7d57b684`.

A `run: |` block contains text shaped as:

```
# uses: actions/checkout@v4
  with:
    fetch-depth: 0
git merge-base --is-ancestor "$P" HEAD
```

There is no actual checkout action, yet the raw line scanner finds a fake checkout,
the nested raw-text `with:/fetch-depth` satisfies the F1 helper, and the analyzer
returns **PASS**.

This is a current-head continuation of the structural concern behind N1. Safe behavior:
block scalar contents must be opaque to workflow metadata parsing; only actual step
mapping keys may define `uses` and `with`.

### E2 - manifest alias escapes access validation

Workflow SHA-256:
`fe9bb81bc0de121217de04a5ec027a411c9cc3398e06153b38d3b16cd98f5a33`.

After a valid manifest load and `d["seed"]`, the workflow does:
`alias=d; alias.get("ghost")`.

Observed: **PASS**.

The current access check is tied to the original data variable name and does not
track aliases. Expected: either track manifest-derived aliases or reject aliasing /
unmodeled uses of a manifest value.

### E3 - dynamic subscript escapes access validation

Workflow SHA-256:
`07679b6f54c79ca2372ed19c9869163e632a22dbd900b08c9f883697aeddde13`.

After a valid `d["seed"]`, the workflow does:
`key="ghost"; assert d[key] is True`.

Observed: **PASS**.

The bracket-key extractor only recognizes literal string subscripts, while the
presence of one valid literal key prevents the block from failing closed. Expected:
reject dynamic subscripts or resolve them soundly.

### E4 - generator `del` silently passes

Generator SHA-256:
`846cec7aac0131da4ba8282cee7357a8de22d1f2dfdd8c8a32b3335b29a97742`.

The generator assigns `m={"seed":1}`, then executes `del m["seed"]`, then
serializes `m`; workflow reads `seed`.

Observed: **PASS**.

This confirms N4 is not limited to `if`: unsupported `ast.Delete` is silently
ignored.

### E5 - conditional early return can mean no manifest is written

Generator SHA-256:
`3950bfa081ebd63efdea54d4ac2f77413b91f550f26069f0df9634837c11b5d1`.

The generator has `if True: return` before the statically discovered write.

Observed: **PASS**.

At runtime this path writes no manifest at all. This is a write-reachability failure
and is stronger than a stale-key mismatch.

## Controls

The focused matrix also checked that R281's three direct fixes are real, rather than
a harness artifact:

- a valid checkout/manifest contract: PASS;
- `env.fetch-depth: 0` instead of checkout `with.fetch-depth`: REJECT;
- direct `m.clear()`: REJECT;
- direct `d.get("ghost")`: REJECT.

Thus the current failures are narrower residual boundaries around the repaired cases.

## Current-head conclusion

**FAIL_CLOSED_CONTRACT_NOT_MET_CURRENT_HEAD.**

On the exact requested production analyzer blob:
- 2/4 exact R283 additional cases are now rejected (N1, N3);
- 2/4 exact R283 additional cases still false-PASS (N2, N4);
- five narrow residual edge cases above also false-PASS.

R281's six focused fixes are therefore effective for their exact regression inputs,
but they do not establish the broader fail-closed guarantee advertised by the analyzer.

## Smallest safe follow-up diff scope

A follow-up repair can remain limited to:

1. `scripts/arc_workflow_preflight.py`
2. `tests/test_arc_workflow_preflight.py`
3. `docs/workflow-preflight.md`
4. append-only evidence for the follow-up task.

No workflow, historical R275/R277/R281/R283/R286 evidence, fixture, estimator, benchmark
or canonical-result edits are needed.

Required repair areas:
- replace exact ancestry-command substring detection with supported normalization /
  strict parsing and fail closed on ambiguous `merge-base ... is-ancestor` syntax;
- make YAML step metadata structural enough that block-scalar text cannot create
  checkout/`with.fetch-depth` evidence;
- reject or fully model unsupported generator control flow/mutation/write reachability
  on the runtime-manifest dataflow (`if/del/for/while/try/with/match`, aliases/helpers);
- track or reject manifest-value aliases, dynamic subscripts, helper passing and other
  unmodeled accesses instead of allowing one recognized literal subscript to mask them.

## Safety

R286 made no PR/code/test/docs modification, posted no PR review/comment, performed no
merge, triggered no Actions, executed no workflow/fixture/estimator/benchmark, and
accessed no benchmark data.
