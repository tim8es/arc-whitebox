# R274 — workflow preflight false-PASS hardening

**Outcome:** COMPLETE. The R272 offline guard was hardened on a new isolated branch from the immutable R272 tip. No workflow, historical receipt/report/result, Actions run, estimator/science, competition dataset, submission, leaderboard, canonical file, or paid resource was touched.

## Reviewed inputs

- R272 immutable tip: `e4bdd87661ca0459675e1b4b9e8d22358be378d4`.
- R272 guard and tests from that tip.
- Actual R254 fixture generator on `research/r254-balanced-rider-reduction-20260923`, branch head `9a97e04bf0563e593c7fa9d6437410227d30dc1c`, fixture git blob `141466b6c4aae6cc61fe086860dc0766a08d6968`.
- Fresh ARC `AGENTS.md`, `research/RESEARCH_PROCESS.md`, STATUS and live control state before R274 claim/start.

The actual R254 generator statically has the required traceable dataflow: `main()` serializes `m` via `json.dumps(m)`; `m` is the third return value of `build_manifest()`, which expands `got`, nests `build_independent_hashes()` as `independent_replay`, adds `replay_equal`, and is then extended by `m.update(...)` before the runtime-manifest write.

## Three independent-review false-PASS boundaries closed

### 1. Unrelated dictionaries can no longer legalize manifest keys

R272 collected literal keys from every `ast.Dict` in the generator source. That could accept a workflow assertion merely because the same key appeared in an unrelated dictionary.

R274 replaces that union with a narrow static dataflow resolver tied to the object actually passed to the runtime manifest's `json.dumps(...)`. It traces literal dict construction, `**` expansion, zero-argument local helper returns, tuple unpacking, nested dict schema, and one statically resolvable `.update(...)`. Unsupported serialized-object shapes fail closed.

Regression: a `ghost_only_elsewhere` key placed in an unrelated dictionary is rejected when the workflow asserts it. A nested key actually supplied through `independent_replay` remains accepted.

### 2. Full-history checkout is now scoped to the ancestry job

R272 accepted `fetch-depth: 0` from any checkout step in the workflow. A separate job could therefore mask a shallow checkout in the job that actually ran `git merge-base --is-ancestor`.

R274 identifies workflow job blocks. For every ancestry guard, the latest preceding `actions/checkout` in that same job must contain `fetch-depth: 0`. A checkout in another job does not satisfy the contract. If the guard cannot be mapped to a job, the preflight rejects instead of guessing.

Regression: a `prep` job with full history plus a shallow `verify` job containing the ancestry guard is rejected.

### 3. Unnamed `- run:` steps and empty extraction now fail closed

R272 split candidate steps only at `- name:`. An unnamed `- run:` could read and assert the runtime manifest without being analyzed; an empty extracted-key set could then pass.

R274 enumerates every top-level list item under each job's `steps:` block, including unnamed `- run:` entries. For every step that references the runtime manifest it requires a statically traceable `json.loads(...)` binding tied to that manifest and at least one extracted bracket-key path. If either relation cannot be proven, the guard rejects with a specific error.

Regressions:
- unnamed `- run:` asserting nonexistent `ghost` is rejected;
- a manifest read followed only by `print(d)` is rejected because no verifiable key reference was extracted;
- delegation to an unknown helper with `--manifest ...` is rejected because this guard cannot prove the helper's key contract.

That last case is intentionally conservative: R274 does not pretend that an external helper is verified unless its contract is statically visible to this guard.

## Offline tests

Primary command recorded for R274:

`python -m unittest discover -s tests -p 'test_r274_workflow_preflight.py' -v`

Result: **6/6 PASS**.

Compatibility subcheck:

`python -m unittest discover -s tests -p 'test_r272_workflow_preflight.py' -v`

Result: **4/4 PASS** after the synthetic fixture in the R274 branch was minimally made explicit about the object it serializes (`json.dumps(m)`), matching the stricter contract. The original R272 branch and durable `research/r272/*` artifacts were not changed.

No fixture generator, estimator, workflow, Actions job, science, competition data, or network benchmark was executed by these tests; they operate only on synthetic source/workflow strings.

## Exact implementation evidence

Implementation commit before sealing report/receipt: `5faaf5116a38f4db202770eea70d1fb9355434a6`.

Committed/tested blobs and SHA256:

- `scripts/arc_workflow_preflight.py`
  - git blob: `a654fa1e15bfa8f9c2bfaa39073ecdf044a74a12`
  - SHA256: `8d002d9f98ce717d2f84757bb2efea9f5b2c4660fb097b230bcc199d6c310cdf`
- `tests/test_r272_workflow_preflight.py`
  - git blob: `c81b621b2535598ea198d1791fe2310f1d57cfa6`
  - SHA256: `52f5ae2813e1cf62eb50395ab5d8106ff20dbfc4cd16ef29b4eafda6a4e222f1`
- `tests/test_r274_workflow_preflight.py`
  - git blob: `73e864930eef77dfb377b6f38366675a7ecb0e45`
  - SHA256: `d842f085332e6d79ddbaa4d5827fc4106c13e70258791c62645bdb78acbd34a9`

Test-output SHA256:

- R274 focused 6-test output: `477f7108a2d417cb62dcf3f43452d2484d7b5704b11ef859fa05bccf00c591b4`
- R272 compatibility 4-test output: `02540d5712f2f59beee921c0efa31abfc245bfb494114ae123154ccceb3822e6`

The implementation diff from R272 tip contains no `.github/workflows/*`, history, `research/r272/*`, historical receipts/results, submission, leaderboard, or canonical changes.
