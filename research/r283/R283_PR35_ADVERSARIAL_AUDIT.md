# R283 - adversarial audit of PR #35 workflow preflight

Status: COMPLETE with confirmed and expanded fail-open findings.
Owner: preflight-adversarial-audit
Run ID: R283-pr35-adversarial-synthetic-audit-20260923
Control claim/start: revisions 369 / 370.

## Reviewed source and mid-audit PR movement

R283 started when PR #35 head was:
`e054a32d7d3bdac98408392b09f467e174c2565b`.

During the audit the PR advanced by one commit to:
`65634dfedfa3d46be785d2b07ba3997b292be16e`.

The only change between those heads is:
- `tests/test_arc_workflow_preflight.py`: +66 lines.

The production analyzer and docs are byte-identical across both heads:
- `scripts/arc_workflow_preflight.py`
  - Git blob SHA-1: `a654fa1e15bfa8f9c2bfaa39073ecdf044a74a12`
  - SHA-256: `8d002d9f98ce717d2f84757bb2efea9f5b2c4660fb097b230bcc199d6c310cdf`
- `docs/workflow-preflight.md`
  - Git blob SHA-1: `81d37a3759c0fc67b6bc8705e05a74e01877d4bd`
  - SHA-256: `1b1118309f616c7e0d977d2c0da3e6073b99de2fc16459f7d338cef1d9c2a3ba`

Current test file:
- Git blob SHA-1: `5cc0111b19905436207dbb86fd1d7e62ff208db2`
- SHA-256: `f790fc9ee2c914e2caed0b7d7dd46dcc931f94c2a7f257a7ea50a8f5c4264205`

PR remained open and unmerged at the closing source check.

R277 receipt reviewed:
- commit: `2ffac1885bdd2424b5e3dbf8519cd8159e23962e`
- Git blob SHA-1: `8ba3ad8d832684f4ec153bf276f9f84fc61af1cb`
- receipt SHA-256: `97b2446a66bb00a38837f5cf0a5083ce2b61dcca668ca03969f0321743b86058`

## Focused offline execution method

No fixture, workflow or estimator was executed. R283 used only small synthetic strings
and the current analyzer logic extracted from the exact reviewed analyzer blob above.
The focused harness exercised `check_contract()` and its current resolver/parsing
functions on minimal workflow/generator inputs.

Normalized execution evidence:
- 18 probes total in the main adversarial harness;
- 14 adversarial probes returned `PASS`;
- 4 controls included one valid PASS and three expected REJECTs;
- normalized result JSON SHA-256:
  `4ab1b3a9254a2ebfa6045730cb48106f5f99253b6bce162f06cc045fa7563fd5`.

A separate exact-body check of the six tests newly added at current PR head
`65634df...` found that all six current analyzer calls return `PASS` even though
those tests expect `PreflightError`.

## R277 F1-F3: executable reproduction

### F1 - checkout fetch-depth is not scoped to `with:`

Affected code:
- `scripts/arc_workflow_preflight.py:264-276` (`_checkout_steps`)
- `scripts/arc_workflow_preflight.py:280-316` (`require_full_history_for_ancestry`)

Minimal workflow fragment:

```yaml
- uses: actions/checkout@v4
  env:
    fetch-depth: 0
- run: |
    git merge-base --is-ancestor "$P" HEAD
```

Observed: **PASS**.

Expected fail-closed behavior: reject because `env.fetch-depth` is not the
`actions/checkout` input `with.fetch-depth`; checkout remains shallow.

Current PR now contains exactly this expected-rejection regression at test lines
187-202, but the analyzer blob is unchanged, so the counterexample still passes.

### F2 - destructive/unknown manifest mutations are ignored

Affected code:
- `scripts/arc_workflow_preflight.py:98-116` (`_apply_update`)
- `scripts/arc_workflow_preflight.py:118-133` (`_process`)
- `scripts/arc_workflow_preflight.py:190-199` (resolved serialization schema)

Minimal generator:

```python
def main():
    m = {"seed": 1}
    m.clear()
    (out_dir/"RTEST_RUNTIME_MANIFEST.json").write_text(json.dumps(m))
```

Workflow reads `d["seed"]`.

Observed: **PASS**, with asserted key `seed`.

Expected: reject unsupported mutation, or model it and then reject the missing key.
Equivalent probes with `m.pop("seed")` and `mutate_manifest(m)` also returned PASS.

The current PR added expected-rejection tests for `clear`, `pop`, and helper
mutation at test lines 204-229; the unchanged analyzer still passes their inputs.

### F3 - manifest binding/access tracing is lexical and partial

Affected code:
- `scripts/arc_workflow_preflight.py:359-378` (`_manifest_data_vars`)
- `scripts/arc_workflow_preflight.py:381-409` (`asserted_manifest_paths`)

Counterexample A:

```python
p = pathlib.Path("RTEST_RUNTIME_MANIFEST.json")
d = json.loads(p.read_text())
assert d["seed"] == 1
assert d.get("ghost") is True
```

Observed: **PASS**. Only `seed` is extracted; the unsupported `.get("ghost")`
read is invisible.

Counterexample B:

```python
p = pathlib.Path("RTEST_RUNTIME_MANIFEST.json")
d = json.loads('{"seed": 1}' + str(p)[:0])
assert d["seed"] == 1
```

Observed: **PASS**, although `json.loads` does not read manifest contents at all;
the argument merely mentions `p`.

Expected: prove an exact manifest-content load and reject every unmodeled access.

Current PR test lines 231-249 now encode expected rejection for wrong load source
and `.get`; the production analyzer remains unchanged and both inputs still PASS.

## Additional fail-open classes found by R283

### N1 - block-scalar/comment text can masquerade as a checkout action

Affected code:
- `_job_blocks`: lines 218-261
- `_checkout_steps`: lines 264-276

Minimal valid workflow shape:

```yaml
jobs:
  verify:
    steps:
      - run: |
          # uses: actions/checkout@v4
          fetch-depth: 0
          git merge-base --is-ancestor "$P" HEAD
```

There is **no checkout action at all**. The apparent `uses:` and `fetch-depth:`
are merely text inside a `run: |` block.

Observed: **PASS**.

Cause: `_checkout_steps` scans raw job lines and does not prove that a matching
`uses:` line is a top-level key of a workflow step.

Expected: structural step parsing; text inside YAML block scalars/comments must never
be interpreted as action metadata.

### N2 - semantically equivalent ancestry guard can bypass detection by whitespace

Affected code:
- lines 281, 287, 299: exact substring
  `"git merge-base --is-ancestor"`
- line 436: the same exact substring determines reported `full_history_required`.

Minimal command:

```sh
git merge-base  --is-ancestor "$P" HEAD
```

(two spaces between `merge-base` and `--is-ancestor`)

Workflow contains no checkout.

Observed: **PASS** and `full_history_required=false`.

Expected: normalize supported shell whitespace/line continuation, or reject any
merge-base/is-ancestor invocation whose ancestry semantics cannot be proven.

### N3 - comments and string literals can manufacture a "verified" bracket key

Affected code:
- lines 394-403: bracket-chain regex scans raw step text.

Minimal fragment:

```python
d = json.loads(p.read_text())
# d["seed"]
assert d.get("ghost") is True
```

Observed: **PASS**; the comment supplies extracted key `seed`, while the real
unsupported access is ignored.

A string literal containing `d["seed"]` produces the same PASS.

Expected: key extraction must operate on parsed executable Python, excluding comments
and string literal contents, and reject unsupported uses of the manifest data variable.

### N4 - generator control flow and write reachability are silently skipped

Affected code:
- `_process`: lines 118-133 only handles Assign, AnnAssign, expression calls and
  top-level Return; unhandled statement kinds are silently skipped.
- `contract`: lines 190-199 then trusts the stale environment.

Minimal examples that all returned **PASS**:

```python
m = {"seed": 1}
if True:
    m = {}
write(json.dumps(m))
```

```python
m = {"seed": 1}
if True:
    return
write(json.dumps(m))
```

```python
m = {"seed": 1}
del m["seed"]
write(json.dumps(m))
```

A helper with an ignored conditional early return also passed.

Expected: unsupported control flow in the runtime-manifest-producing function or
a helper on its dataflow must fail closed unless the analyzer models every reachable
manifest state and write path.

The conditional-return case is especially important: current code can report PASS
even when the runtime path writes **no manifest at all**.

## Negative controls

The harness also verified that the analyzer does reject several unsupported cases:
- direct subscript assignment into the tracked manifest object;
- a manifest step using only `d.get("ghost")` with no bracket-chain decoy;
- a nested workflow read when the generator nested schema is dynamic/unresolved.

These controls show that the findings are specific silent-PASS boundaries rather than
a harness that simply turns all errors into PASS.

## Current-head test inconsistency

The current PR head adds six expected-rejection tests at lines 187-249:
1. checkout `env.fetch-depth`;
2. `m.clear()`;
3. `m.pop(...)`;
4. helper mutation;
5. non-manifest `json.loads` source;
6. `d.get(...)`.

Using those exact test inputs with the unchanged current analyzer, all six analyzer
calls returned `PASS`.

R283 did **not** trigger Actions and did not post a PR review/comment. This is an
offline source/input result only.

## Smallest safe fix scope

A safe follow-up should change only:

1. `scripts/arc_workflow_preflight.py`
2. `tests/test_arc_workflow_preflight.py`
3. `docs/workflow-preflight.md`
4. append-only evidence for the new repair task.

Do **not** change `.github/workflows/*`, historical R275/R277/R283 evidence,
fixtures, estimators, benchmark data, or canonical results.

### Analyzer changes

**YAML/checkout/guard scope (roughly lines 218-316):**
- derive checkout metadata only from actual top-level step mappings, not arbitrary raw
  lines in a job block;
- require `uses: actions/checkout@...` as a step key and `fetch-depth: 0` under
  that same step's `with:` mapping;
- block-scalar/comment text must be opaque;
- normalize supported ancestry command whitespace; if a step appears to invoke
  `merge-base`/`is-ancestor` but cannot be safely parsed, reject.

Because the tool is standard-library-only, a narrow strict structural parser is
preferable to pretending arbitrary YAML is supported. Ambiguous YAML constructs
should fail closed.

**Generator dataflow (roughly lines 39-199):**
- never silently skip statement types on the manifest-producing path;
- model or reject destructive dict operations (`clear`, `pop`, `popitem`),
  deletion, and calls that receive/operate on tracked manifest objects;
- reject unmodeled `if/for/while/try/with/match` control flow in manifest-producing
  functions/helpers unless all reachable states and write reachability are proven;
- conditional return/write reachability must be explicit.

**Workflow manifest dataflow (roughly lines 350-409):**
- prove `json.loads` receives contents of the exact runtime-manifest path, not an
  expression that merely mentions its variable;
- parse the relevant Python verifier body with stdlib AST/tokenize (or equivalently
  strict supported syntax) so comments/string literals cannot create key paths;
- account for every use of the manifest data variable; reject `.get`, aliasing,
  dynamic subscripts, helper passing or any unmodeled use instead of allowing one
  recognized bracket read to mask them.

### Regression additions

Keep the six current-head expected-rejection tests and add at least:
- fake/commented checkout text inside `run: |`;
- whitespace/line-continuation ancestry command;
- comment/string-literal bracket decoy plus real unsupported access;
- conditional manifest rebind;
- conditional early return before write;
- `del m["key"]`;
- helper control-flow early return.

## Verdict

**FAIL_CLOSED_CONTRACT_NOT_MET.**

R277 F1-F3 are executable and remain present in the current analyzer. R283 found
four additional silent-PASS classes (N1-N4). The current PR has started adding
regression tests, but at audit close its analyzer has not changed and the six newly
added expected-rejection inputs still return PASS.

No PR code was edited, no PR review/comment was posted, no merge or Actions occurred,
and no fixture, estimator, public benchmark data, private/holdout/full data or paid
resource was used.
