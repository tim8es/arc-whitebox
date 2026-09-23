# R258 terminal report — full-history checkout successor

Status: **INFRA_ERROR before parent/candidate science; no retry**

## Frozen control

- run ID: `R258-BPK2K-ONE-SHOT-20260923-A1`
- protocol commit: `f123a7f6b0f1b0e12314e6a4c9c21980fd3a6a33`
- workflow commit: `47d8ff5eef1cc70a60e7c9cb9ad10c3cec1a0cc2`
- arm commit: `1d4998148c7a3e374002c00fdebddcf713e95daa`
- branch: `research/r258-bpk2k-full-history-one-shot-20260923`
- immutable R257 terminal base: `c4b46ecacba1876613a6e11b678399d0b1fd83ba`
- R257 receipt SHA256:
  `4b28cfb1f912afc9cae0b98484b711ee8dde5145e5d0753b2977eadd21093cc1`

R258 retained the R257 scientific protocol/gates/source hashes. The only intended
execution change was full-history checkout with `fetch-depth: 0`.

## Sole Actions execution

- run: `35840156117`
- job: `107113033506`
- attempt: `1`
- head: `1d4998148c7a3e374002c00fdebddcf713e95daa`
- standard GitHub-hosted runner: `ubuntu-24.04`
- workflow conclusion: **failure**
- artifact: `10740674582` (`r258-one-shot-evidence`)
- artifact ZIP SHA256:
  `4109b2e0c6cd5e7380bf60dcf1a5efe621af9df9bbe5dee6d142410efdb6ec9f`

Exactly one R258 workflow/attempt exists. No rerun or second workflow was dispatched.

## Full-history repair result

The R257 failure is repaired: checkout, frozen ancestry, changed-path guard, Git-blob
checks and SHA256 source checks all passed.

Runtime pins also passed exactly:
- Python 3.11.16
- NumPy 2.4.6
- FlopScope 0.12.1
- WhestBench 0.16.1

All three wheel digests matched the frozen manifest.

The pinned V25 parent download/hash verification passed:
SHA256 `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`.

## Exact R258 infrastructure failure

Fixture generation itself succeeded and persisted:

`r258_artifacts/fixture/R254_FIXTURE_RUNTIME_MANIFEST.json`

with exact frozen:
- seed 254001
- weights SHA256
  `199e5fd8c669ec927717a12f0a3bbcee83e37db8db6e61e8c50eb791f457b3f0`
- truth SHA256
  `58354221cedab39e900d78040a8383df45672425389f3865b731eea7b0063f1d`
- all 16 layer hashes equal
- `replay_equal=true`

The workflow then attempted to read the different filename:

`r258_artifacts/fixture/R254_RUNTIME_FIXTURE_MANIFEST.json`

and failed with:

`FileNotFoundError: [Errno 2] No such file or directory:
'r258_artifacts/fixture/R254_RUNTIME_FIXTURE_MANIFEST.json'`

The fixture step therefore exited 1. This filename mismatch was already latent in the
frozen R257 workflow but R257 never reached it because of its earlier shallow-checkout
failure. R258 made no scientific/gate change and exposed this next infrastructure
boundary.

## Execution accounting

Completed:
- full-history checkout;
- ancestry and frozen source/hash verification;
- Python setup;
- pinned wheel digest/runtime verification;
- pinned V25 source download/hash verification;
- deterministic fixture construction and replay.

Not executed:
- V25 parent estimator execution;
- BPK2K construction;
- BPK2K execution;
- target-free MSE/FLOP/residual gates;
- candidate validation;
- exact live R209 identity access;
- public mini-100;
- public gates.

Counts:
- parent executions: 0
- candidate constructions: 0
- candidate executions: 0
- target-free measurements: 0
- public measurements: 0

The workflow receipt decision is
`INFRA_ERROR_BEFORE_TARGET_FREE_RESULT`; target-free/public fields are null.

Scientific status is **UNEVALUATED**. No BPK2K numeric accuracy, FLOP, timing, public
score, paired-gain, improved-row or rank claim is made.

## Artifact integrity

The downloaded ZIP independently hashes to the GitHub-reported digest.
It contains 14 files. `R258_ARTIFACT_HASHES.json` contains 13 mapped files and all 13
recompute with zero mismatches.

Key artifact hashes:
- workflow receipt:
  `c80b9da36450243ba7706bfd23c9b6bb9448f29ac99f308259110f895ede64c0`
- runtime versions:
  `e9f9d943b5aa2ac563ce1c62fa685a99c482c1dc406e380709eb9fe8d835eda7`
- runtime fixture manifest:
  `4c14e8b3907907c73d061a9d46575d0847971aa8fda3ef642826c7118b33e105`
- pinned V25 source:
  `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`

## Terminal disposition

R258 is terminal **INFRA_ERROR** under the frozen exactly-one-workflow/no-rerun rule.
The workflow conclusion is **failure**; the research status is **INFRA_ERROR**; the
scientific status is **UNEVALUATED**.

No tuning, paid/private/holdout/full run, R223/R244 artifact access, submission,
leaderboard/canonical edit, or R254/R257 history rewrite occurred.
