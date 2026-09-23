# R277 - independent static review of PR #35

Status: COMPLETE static review with FINDINGS; not PASS.
Owner: preflight-independent-review
Run ID: R277-pr35-static-independent-review-20260923
Reviewed PR: https://github.com/tim8es/arc-whitebox/pull/35
Exact PR head: e054a32d7d3bdac98408392b09f467e174c2565b
Current main/base: b5b988f8ec49a5ec473d59fcbfdfaf8c4350c850
Control claim/start: revisions 355 / 359.

## Scope and method

This review is read-only with respect to PR #35 and production code. R277 did not
edit the PR, post a review/comment, merge it, trigger Actions, execute fixtures,
run estimators/science, or access competition data.

The review inspected the exact committed bytes of the analyzer, the consolidated
10-case regression file, the CLI documentation, R275 evidence, and the exact
historical R257-R259 workflow failure sites. R277 did not re-run the unit test
command; the independent evidence here is source-level review plus verification
that the R275 receipt refers to the exact PR blobs.

PR state at review:
- open, not merged;
- head e054a32d7d3bdac98408392b09f467e174c2565b;
- current main b5b988f8ec49a5ec473d59fcbfdfaf8c4350c850;
- ahead 2 / behind 0;
- GitHub mergeable=true, mergeable_state=clean;
- five added files, with no workflow file changed.

## Exact PR implementation evidence

Production analyzer:
- scripts/arc_workflow_preflight.py
- Git blob SHA-1 a654fa1e15bfa8f9c2bfaa39073ecdf044a74a12
- SHA-256 8d002d9f98ce717d2f84757bb2efea9f5b2c4660fb097b230bcc199d6c310cdf

Regression tests:
- tests/test_arc_workflow_preflight.py
- Git blob SHA-1 a5c4cc5801d30af3ffcdcb9b53c0d5cc932593fb
- SHA-256 041102f9622deb96eb2fd886aca771de0dd0553ad6efbf626ea6d39a3449a5e8

CLI/docs:
- docs/workflow-preflight.md
- Git blob SHA-1 81d37a3759c0fc67b6bc8705e05a74e01877d4bd
- SHA-256 1b1118309f616c7e0d977d2c0da3e6073b99de2fc16459f7d338cef1d9c2a3ba

R275 recorded the exact same blobs and a local/offline 10/10 PASS for:
  python -m unittest tests/test_arc_workflow_preflight.py -v
with verbose-output SHA-256
49d62a48aa3753688382c26f6b51a6b55f7e70d5e0e5853f5d8c49a778f92f98.
R277 does not substitute that prior execution for the independent static analysis below.

## Historical failure contract: PASS

The test suite does directly represent the three verified R257-R259 infrastructure
failures and the R274 hardening cases.

### R257: shallow checkout before ancestry guard

Historical source:
- .github/workflows/r257-one-shot.yml
- commit 187bc8f9ca459a96af1f7cf0d014bc906b278a2a
- Git blob 96e47b51cac6b7ecf39f02a47dd2cb63d1771578
- line 25: actions/checkout@v4 with no fetch-depth input
- line 40: git merge-base --is-ancestor ...

R257 receipt: 4b28cfb1f912afc9cae0b98484b711ee8dde5145e5d0753b2977eadd21093cc1.
The run failed exactly at the ancestry guard because the protocol ancestor was absent.

Regression mapping:
- tests/test_arc_workflow_preflight.py lines 95-98
  test_shallow_history_is_rejected.

### R258: runtime-manifest filename mismatch

Historical source:
- .github/workflows/r258-one-shot.yml
- commit 47d8ff5eef1cc70a60e7c9cb9ad10c3cec1a0cc2
- Git blob d6ac9965c19bbbaeb5c6a6598b5e01d08929805f
- lines 25-27: full-history checkout is present
- line 117: workflow reads R254_RUNTIME_FIXTURE_MANIFEST.json

Generator source:
- research/r254/r254_fixture.py
- Git blob 141466b6c4aae6cc61fe086860dc0766a08d6968
- line 102: emits R254_FIXTURE_RUNTIME_MANIFEST.json

R258 receipt: 60e0ed2e62a400c5738a1da63c88b59c47352c5e872ec8f1e7935f60091472ef.

Regression mapping:
- tests/test_arc_workflow_preflight.py lines 99-104
  test_manifest_name_mismatch_is_rejected.

### R259: nonexistent nested replay field

Historical source:
- .github/workflows/r259-one-shot.yml
- commit 65394e2679bebd7005e7fba13de3166a2c5800d2
- Git blob 9d8099c4ba68904b2b6b38f07b4f878dc2053efa
- line 122: corrected R254_FIXTURE_RUNTIME_MANIFEST.json
- line 127: asserts independent_replay.all_layer_hashes_equal

Actual generator:
- research/r254/r254_fixture.py lines 61-80: independent_replay contains
  layer_sha256, weights_concat_sha256, truth_sha256 only;
- line 94: build_manifest returns independent_replay plus replay_equal;
- line 102: serializes that manifest.
There is no all_layer_hashes_equal key.

R259 receipt: dd1c5c0d9941941cb00153e076c09cb51743966f0486579de85ac70f97af1fe1.

Regression mapping:
- tests/test_arc_workflow_preflight.py lines 106-108
  test_nonexistent_schema_field_is_rejected.

### Remaining seven tests

- lines 110-114: known repaired contract positive control;
- 116-125: unrelated generator dict cannot legalize a key;
- 127-138: serialized-object/nested-helper positive schema trace;
- 140-155: full-history checkout in another job cannot satisfy ancestry job;
- 157-162: unnamed run step is analyzed;
- 164-174: manifest read with no extracted key fails closed;
- 176-184: delegated unknown helper fails closed.

These ten tests are coherent regressions for the historical failures and the three
R274 hardening boundaries. The finding below is not that those tests are wrong; it
is that they do not exhaust the broader fail-closed contract stated by code/docs.

## Finding F1 - HIGH: fetch-depth is not proven to be an actions/checkout input

Claimed contract:
- scripts/arc_workflow_preflight.py lines 4-9;
- docs/workflow-preflight.md lines 14-20;
- specifically docs lines 16-17 require a preceding actions/checkout with
  fetch-depth: 0 in the same job.

Implementation:
- analyzer lines 264-276 collect the entire textual checkout step;
- lines 307-314 accept any line in that step matching
  ^\s*fetch-depth:\s*0, without proving that it is nested under the checkout
  step's with: mapping.

Therefore a syntactically valid action step such as:

  - uses: actions/checkout@v4
    env:
      fetch-depth: 0

satisfies the analyzer's regex, while it does not set the actions/checkout
fetch-depth input. Checkout therefore retains its normal shallow behavior. If the
same job later runs git merge-base --is-ancestor, this is a false PASS for exactly
the class of contract that failed R257.

The same issue can arise if a matching fetch-depth line appears in another nested
mapping or textual payload inside the checkout step. Test lines 140-155 verify
same-job scoping but do not verify with:-input scoping.

Required disposition for PASS: structurally prove that fetch-depth: 0 belongs to
the relevant checkout step's with: mapping, or reject when that relation cannot be
proved; add a regression for a misleading non-with fetch-depth line.

## Finding F2 - HIGH: destructive/unknown manifest mutations are silently ignored

Claimed contract:
- analyzer lines 4-9 say unsupported static contracts fail closed;
- docs lines 19-20 say workflow key paths must exist in the object statically
  traced to the generator's json.dumps(...) write.

Implementation:
- _process, lines 118-133, only models Assign, AnnAssign, Return, and expression
  calls routed through _apply_update;
- _apply_update, lines 98-116, silently returns for every expression call that is
  not a recognized name.update(one_dict);
- other statements/mutations are also skipped rather than rejected.

Concrete static counterexample:

  m = {"seed": 254001}
  m.clear()
  (out_dir/"R254_FIXTURE_RUNTIME_MANIFEST.json").write_text(json.dumps(m))

The resolver records seed from the assignment, silently ignores m.clear(), and can
therefore approve a workflow read d["seed"]. At runtime the serialized object is
empty and that read fails.

The same unsound class includes pop/popitem, mutating helper calls, deletion through
unsupported statements, and destructive mutation of a nested dict. This is a
fail-open boundary, not merely a conservative false rejection.

Tests lines 116-138 correctly close the unrelated-dict scope bug but do not cover
mutation after schema construction.

Required disposition for PASS: reject any unmodeled operation that can affect an
object on the manifest dataflow, or model it soundly; add a destructive-mutation
regression.

## Finding F3 - HIGH: workflow manifest reads/key accesses are only partially traced

Claimed contract:
- docs lines 19-20 cover manifest key paths read by workflow steps;
- R274 hardening described a statically traceable json.loads binding tied to the
  manifest.

Implementation has two gaps:

1. Lines 368-377 accept json.loads(argument) as tied to a manifest path variable
   merely when the argument text mentions that variable. They do not prove that
   the argument is the file contents. For example json.loads(str(p)) can be
   accepted as a manifest binding if p was assigned from the manifest path.

2. Lines 394-403 extract only bracket chains such as d["a"]["b"]. Lines 404-407
   fail closed only when no bracket path at all was found. Thus unsupported key
   access can hide beside one supported access. Example:

     d = json.loads(p.read_text())
     assert d["seed"] == 254001
     assert d.get("ghost") is True

   Only seed is checked against the generator schema. The ghost read is invisible,
   block_paths is non-empty, and the analyzer can return PASS although runtime
   fails because ghost is absent.

Tests lines 164-184 prove fail-closed behavior when extraction/binding is wholly
absent, but they do not cover mixed supported and unsupported access or a false
json.loads data dependency.

Required disposition for PASS: either reject unsupported manifest-variable uses/key
accesses in a manifest-reading step, or statically cover them; prove the json.loads
payload derives from a recognized file-content read rather than mere textual
reference. Add mixed-access and false-binding regressions.

## CLI/docs review

Accurate:
- analyzer imports only standard-library modules (lines 16-22);
- CLI arguments in docs match implementation:
  --workflow and --fixture-generator, lines 443-447;
- files are read as text and statically analyzed, lines 448-452;
- exceptions are converted to nonzero return code 2 with
  WORKFLOW_PREFLIGHT_FAIL, lines 453-455;
- success prints JSON and returns 0, lines 456-457;
- the analyzer does not execute the workflow or fixture generator.

Not accurate enough for the current implementation:
- docs lines 14-20 and analyzer docstring lines 4-9 state a general fail-closed
  guarantee for the supported contracts, but F1-F3 show concrete false-PASS paths.
- the documentation does not state the actual narrow syntax assumptions that would
  be needed to make the current implementation safe to use as a proof gate.

## Verdict

**FINDINGS - NOT PASS.**

PR #35 correctly packages the R272/R274 analyzer on a clean current-main base and
the 10 tests faithfully cover the known R257-R259 incidents plus the R274 regressions.
However, the production analyzer is not yet fail-closed for the contract advertised
by the PR/docs. F1-F3 are concrete source-level false-PASS classes.

No merge recommendation is encoded as a PR action; R277 made no PR comment/review
and performed no merge or Actions operation.
