# R296 — harden draft PR #36 against workflow re-runs, ref races, mutable actions and token persistence

Status: **COMPLETE — SECURITY HARDENING PREPARED / STATIC-OFFLINE VERIFIED / NO ACTIONS RUN**

Job: R296  
Owner: `r293-workflow-security-fix-r268`  
Run ID: `R296-pr36-workflow-security-hardening-20260924`

## Scope

R296 modifies only the existing draft PR #36 security/persistence control plane. It
does not change the frozen V25 estimator, the R291 capture harness, the R294 evaluator
patch semantics, the public-mini panel, score computation, FLOP accounting, or the
four-file capture output contract.

Input audit: R295 receipt SHA256
`4e118c1d992bc042b02e0855e570b8b47db94de29d377037d6429fdc681911e6`.

R296 started from PR #36 head
`4cb350b2ccf280fe26de069b83120764229c002b`.

Pre-report hardened PR head:
`e854147327889c4d240e705034dd5c238479fe94`.

PR #36 remains open, draft, and unmerged. The frozen result branch
`research/r293-v25-capture-result` remains absent.

## R295 F1 — workflow re-runs and separate duplicate dispatches

Both workflow jobs now require:

`github.run_attempt == 1`

in addition to the existing main-ref and manual confirmation gates. The benchmark-capable
`persist` job therefore cannot execute on a GitHub re-run attempt.

A second independent dispatch is blocked before dependency installation / validation /
benchmark by a durable **empty claim commit** on the pre-created result branch. The claim
commit is created locally with parent exactly `GITHUB_SHA`, then published with:

`--force-with-lease="refs/heads/$RESULT_BRANCH:$GITHUB_SHA"`

The explicit expected old SHA turns the ref update into a compare-and-swap. If another
dispatch already claimed the ref, the branch tip no longer equals `GITHUB_SHA` and the
lease fails before any benchmark-capable work.

The empty claim changes no repository file, so it does not widen the frozen output
file allowlist.

## R295 F4 — atomic pre-created-only branch updates

The previous check-then-ordinary-push sequence is removed.

Two server-side expected-old-tip leases are now required:

1. **claim:** expected old tip = exact dispatch `GITHUB_SHA`;
2. **final result:** expected old tip = exact durable claim SHA.

The workflow never uses a blind `--force`. It uses only explicit
`--force-with-lease=<ref>:<expected-old-sha>` CAS updates.

This property was tested offline against a local bare Git remote. Final PASS matrix:

- claim CAS from exact pre-created tip succeeds;
- stale second dispatch / same-tip claim is rejected;
- branch deleted before claim is **not recreated**;
- branch moved before claim is rejected;
- branch deleted after durable claim and before final result is **not recreated**;
- branch moved after durable claim and before final result is rejected;
- final result CAS from exact claim SHA succeeds;
- stale final lease after the result lands is rejected.

Result: **8/8 PASS**.

The branch `protected:false` API gate is retained before claim and rechecked immediately
before final persistence. Any protection/ruleset change that causes the server update to
reject remains fail-closed.

## R295 F2 — immutable action pins

GitHub tag refs were read from the official action repositories and resolved to:

- `actions/checkout@v4.2.2` ->
  `11bd71901bbe5b1630ceea73d27597364c9af683`
- `actions/setup-python@v5.6.0` ->
  `a26af69be951a213d495a4c3e4e4022e16d87065`

All checkout uses in PR #36 now reference the full checkout commit SHA. The single
setup-python use references the full setup-python commit SHA. Mutable
`actions/checkout@v4` and `actions/setup-python@v5` references are absent.

Official tag-ref endpoints used for verification:

- https://api.github.com/repos/actions/checkout/git/ref/tags/v4.2.2
- https://api.github.com/repos/actions/setup-python/git/ref/tags/v5.6.0

## R295 F3 — token non-persistence

Both checkout steps still set `persist-credentials: false`.

The previous:

`git remote set-url origin https://x-access-token:...`

path is removed. The token is never inserted into `origin`, another remote URL, or
persistent repository Git config.

The built-in token is explicitly exposed only in the two minimal CAS push steps:
durable claim and final result persistence. Those steps use a process-scoped
`GIT_CONFIG_COUNT/GIT_CONFIG_KEY_0/GIT_CONFIG_VALUE_0` credential helper. The helper
contains only the literal environment-variable reference; the token itself is not
written into Git config.

Offline process-scope test with a dummy token:

- helper is visible to the configured Git process;
- local repository config has no credential helper afterward;
- dummy token is absent from `.git/config`.

Result: **3/3 PASS**.

Static committed-byte checks also confirm:

- exactly two explicit `GITHUB_TOKEN: ${{ github.token }}` step environments;
- no `GH_TOKEN` environment alias;
- no `Authorization` header in workflow source;
- no token-bearing remote URL;
- no `git remote set-url`;
- exactly two process-scoped credential-helper configurations.

## Existing R293/R294 gates preserved

The workflow still has only `workflow_dispatch`, fixed main-ref confirmation, standard
`ubuntu-24.04`, empty top-level permissions, `contents: read` on preflight, and the
only `contents: write` grant on `persist`.

The exact four persisted files remain:

- `research/captures/r293/vectors.f32le`
- `research/captures/r293/manifest.json`
- `research/captures/r293/SHA256SUMS`
- `research/captures/r293/run-receipt.json`

No broad `git add .` or `git add -A` is introduced.

The corrected R294 evaluator patch is unchanged and remains active:

- patch blob:
  `65abb2e2040e44a7965f5123acd17bb838891532`
- SHA256:
  `bab98621f510520a0fe8539c41bb2d59dd4680eaa8237a63a81d082897934cf3`
- expected patched scorer blob:
  `8493b7ff28110fb13f467400b6895c56bd7550bb`.

The R294 real apply checker and explicit `git apply --check` path remain in the future
workflow.

## R296 checker artifacts

Exact pre-report file identities:

| Path | Git blob SHA1 | SHA256 | Bytes |
|---|---|---|---:|
| `.github/workflows/r293-v25-residual-capture.yml` | `19f6f95ceb2cacef5497eafd5e31e20e86cfad8c` | `23cb8b2a4db23b6dd030b6148cfaa8d6d2cb45e31ff264195c970117fd69f863` | 22,374 |
| `research/r293/R293_PROTOCOL.json` | `cc51198550b0d35b7fb0e34e8b072d74a456476c` | `e0e36f5107676326529359f238b678b03d5faf25fae913d102387dc6ba1f3a74` | 6,682 |
| `scripts/r293_capture_workflow_preflight.py` | `ba27e0a6f6e13e24344b3cec6b60a5717e45b51f` | `be910a30efe4ddb0c77826bd92d5c58f058a1db673f314cd3b61667d2d795e1f` | 12,591 |
| `scripts/r296_workflow_security_selfcheck.py` | `dc09a5c4a06136370344c27723c5c430588b0fa2` | `55ea4d7300d1e8e1913a07031b626bd1475e4d46f9590033a8fb38c5e4865d82` | 10,698 |

The hardened R293 preflight is now a superset of the previous gates and additionally
requires run-attempt guards, exact action SHAs, exact two-stage leases, durable-claim
ordering, two minimal token steps, process-scoped credential configuration, and the
new protocol security fields.

The new R296 adversarial checker is also invoked by the future workflow preflight.

## Test notes

The first local adversarial self-check attempt stopped before exercising lease behavior
because its synthetic bare remote had not yet received the base Git object; local
`update-ref` correctly rejected a nonexistent object. This was a **test fixture bug**,
not a workflow failure. The checker was repaired to seed/move the synthetic remote via
local Git pushes. Final lease tests then passed.

Exact current workflow/protocol static assertions all pass, including:

- manual trigger only;
- two main-ref guards;
- two run-attempt guards;
- exact full-SHA action counts;
- no mutable action tags;
- one `contents: write`;
- both checkout credentials disabled;
- exactly two explicit token steps;
- no token remote/config/header persistence;
- two explicit leases with exact expected old tips;
- durable claim before install/benchmark-capable work;
- exact four-file allowlist;
- no broad add;
- R294 patch identity/check path preserved;
- R296 protocol and race-test fields present.

## Remaining gates

R296 authorizes no execution.

Before any future run:

1. keep PR #36 under independent review;
2. separately authorize and merge the final reviewed PR to `main`;
3. externally create the frozen result branch at the exact merged-main SHA and verify
   `protected:false`;
4. separately authorize exactly one first-attempt `workflow_dispatch`;
5. treat a durable claim with no final result as terminal for that authorization unless
   the coordinator explicitly performs a new external reset/re-authorization;
6. verify final result branch SHA and four persisted file hashes before any scientific
   consumer task.

Any later workflow/protocol/preflight/security-checker byte change invalidates the file
hashes in this report and requires re-review.

## Accounting

- PR #36 merged: 0
- result branch created: 0
- Actions runs: 0
- benchmark / estimator runs: 0
- datasets accessed/downloaded: 0
- dependencies installed/downloaded: 0
- paid resources: 0
- private/holdout/full accesses: 0
- submissions: 0
- leaderboard/canonical edits: 0
- R294 evaluator patch semantic changes: 0
- R291 historical artifact changes: 0
