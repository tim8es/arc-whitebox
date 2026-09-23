# R289 — final independent current-head audit of PR #35

Status: COMPLETE — all inherited false-PASS inputs reject on the current production analyzer.
Owner: `preflight-current-head-final-audit`
Run ID: `R289-pr35-current-head-final-audit-20260923`

## Control and source pin

At the first R289 read in this session, live control had already advanced beyond the
assignment snapshot and R289 was already owned by the assigned owner:

- R289 claim: revision 403
- R289 start: revision 404
- start source commit: `7a65d58a559dce27f709374a0fbaea6726aa3b43`
- start command: offline read-only synthetic replay of all R277/R283/R286 false-PASS inputs
- no duplicate claim/start was issued.

Fresh PR #35 source pin, checked before and after the replay:

- PR #35 state: OPEN, unmerged
- current head: `7a65d58a559dce27f709374a0fbaea6726aa3b43`
- production analyzer: `scripts/arc_workflow_preflight.py`
- analyzer Git blob SHA-1: `2c87bc09992228be915e117a6d3aac8a703f68ab`
- analyzer SHA-256: `946d7c79f988f0b739b8213b2423a315875a8c7c10699c21f1aa9b477a3551ac`
- current tests blob: `f1549f1c75f2566e8a347363e2807f87be31ee1f`
- current tests SHA-256: `75020df0dd484a2859c60ab20c65453d686e30ad2662f6ce0f25fc98e06d08bc`

The source pin differs from R286's obsolete `05733f3...` / analyzer blob
`f9b01ba...`. R285 is the intervening remediation.

## Prior immutable evidence read

- R277 receipt SHA-256:
  `97b2446a66bb00a38837f5cf0a5083ce2b61dcca668ca03969f0321743b86058`
- R283 receipt SHA-256:
  `fb1002ca8e67d4d1cc791443a70559a4037ae0bba260d3121050746839952180`
- R285 receipt SHA-256:
  `e4ddee4ffd75a0b94c4740bca4e39b6fd93b4ae531a8fc9ff9f1535827b0f109`
- R286 receipt SHA-256:
  `40bc27eb85e0f58e12bb94976661a2892ad399fdae673cc5dce110d0e0337fce`

R286 exact input strings were reused byte-for-byte where available. R277/R283 inputs
not retained in the R286 input bundle were reconstructed from their immutable report
snippets and frozen with their exact R289 SHA-256 values in the replay evidence.

## Method

The replay was synthetic and offline. Small workflow/generator strings were supplied
to the current production analyzer's static `check_contract()` logic extracted from
the exact pinned analyzer blob. The workflow and generator strings themselves were
not executed. No fixture, estimator, benchmark, Actions job, or competition data was
run or accessed.

Durable exact input/evidence bundle:

- `research/r289/R289_REPLAY_EVIDENCE.json`
- evidence commit: `6bb60df68457746acbe7367783ec699202264b2e`
- Git blob SHA-1: `3c1b835c20a2799ecf8db047c96260ad1d70e04c`
- SHA-256: `b9ed04a86b1f0bc892d44b0c76e701d1cdee9bed0c27ca99f64056171fe780bb`
- canonical 17-row matrix SHA-256:
  `2ac39bdcfaec15a7e6a80f12637d95cc75a54e940dda9a6c801b7551bd2f4ca6`

The evidence bundle contains every exact R289 workflow/generator string plus its
SHA-256, expected outcome, observed outcome, and rejection class.

## Exact replay matrix

| Input | Prior false-PASS class | Current head |
|---|---|---|
| R277 F1 | `env.fetch-depth: 0` masquerades as checkout input | **REJECT** |
| R277 F2 clear | destructive `m.clear()` ignored | **REJECT** |
| R277 F2 pop | destructive `m.pop(...)` ignored | **REJECT** |
| R277 F2 helper | helper mutation of manifest ignored | **REJECT** |
| R277 F3 get | valid bracket read masks `d.get(...)` | **REJECT** |
| R277 F3 wrong-load | path variable merely mentioned in `json.loads` | **REJECT** |
| R283 N1 | fake checkout text inside `run: |` | **REJECT** |
| R283 N2 | double-space ancestry guard bypass | **REJECT** |
| R283 N3 comment | comment manufactures bracket-key evidence | **REJECT** |
| R283 N3 string | string literal manufactures bracket-key evidence | **REJECT** |
| R283 N4 | conditional manifest rebind | **REJECT** |
| R286 E1 | fake checkout + nested `with:/fetch-depth` inside run block | **REJECT** |
| R286 E2 | manifest alias + unsupported access | **REJECT** |
| R286 E3 | dynamic manifest subscript | **REJECT** |
| R286 E4 | `del m["seed"]` | **REJECT** |
| R286 E5 | conditional early return / no manifest write | **REJECT** |
| R283 helper control flow | conditional return inside manifest-producing helper | **REJECT** |

Result: **17/17 inherited false-PASS inputs reject; 0/17 false PASS.**

A valid structural checkout with `with.fetch-depth: 0`, a supported ancestry guard,
an exact manifest read, and literal bracket access remains a **PASS** control.

## Rejection boundaries observed

The current analyzer now rejects the inherited cases at the intended narrow boundaries:

- structural checkout parsing prevents block-scalar/comment text and `env.fetch-depth`
  from supplying checkout proof;
- ancestry detection accepts supported shell whitespace, so the double-space command
  is recognized and then rejected for lacking checkout;
- generator processing rejects unsupported `If` and `Delete` statements and
  unsupported tracked-manifest mutations/helper mutation;
- workflow verifier analysis parses Python AST, proves the exact manifest read,
  rejects aliases and dynamic subscripts, and excludes comment/string decoys from
  key evidence.

No additional false-PASS was found within the requested R277/R283/R286 corpus.
This is a bounded corpus result, not a proof for arbitrary YAML/Python syntax.

## Verdict

**PASS_FOR_REQUESTED_R277_R283_R286_FALSE_PASS_CORPUS.**

The current PR #35 production analyzer on exact head `7a65d58...` rejects every
requested inherited false-PASS input while the valid control still passes. This
independently closes the specific R286 findings on the post-R285 current head.

## Safety

R289 made no change to PR #35, production code, tests, docs, workflows, fixtures,
estimators, or canonical results. It posted no PR comment/review, performed no merge,
triggered no Actions, and accessed no benchmark/competition data.
