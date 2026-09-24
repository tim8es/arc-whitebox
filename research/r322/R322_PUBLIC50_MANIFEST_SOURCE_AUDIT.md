# R322 — Phase-2 grader-public-50 manifest source audit

**Verdict: EXISTS_BUT_NOT_PUBLICLY_EXPOSED (category b).**

R322 follows only the exact blocker from R319: whether an official public immutable artifact exposes the Phase-2 grader-public 50-row mapping from `mlp_index` to the canonical seed identity used by R224 (`network_id = decimal exact int64 mlp_seed`).

No such public 50-row manifest was found.

However, first-party sources do establish that the underlying identity-bearing mapping exists inside the evaluation dataset construction: official WhestBench documentation defines evaluation `public` and `holdout` splits as datasets baked from explicit per-MLP seed files, stores `mlp_id` + `mlp_seed` in every dataset row under seed protocol 3.0, and shows the combined evaluation dataset being uploaded as **private**. The live Phase-2 submission surface independently confirms a 50-public / 50-holdout grader partition.

Accordingly this is **(b) exists but is not publicly exposed**, with an important precision: the sources prove the identity-bearing evaluator dataset/map exists; they do **not** prove that AIcrowd maintains a separately named standalone “manifest” file.

## Scope

- exact repo base: `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`
- branch: `review/r322-public50-manifest-source-audit-20260924`
- prior blocker: R319 `NOT_JOINABLE`
- searched only:
  - official public AIcrowd challenge/submission surfaces,
  - official AIcrowd/WhestBench documentation,
  - official public dataset viewer metadata already exposed on Hugging Face under the `aicrowd` organization.
- no authentication
- no dataset/dependency download
- no inference from display names or row order
- no benchmark, score calculation, Actions, paid/private/holdout/full access, submission, or main/PR/control edit

## 1. R319 blocker carried forward exactly

R319 established:

- grader-public rows: 50
- public canonical network IDs: **0/50**
- public target hashes: **0/50**
- R209/R224 Mini-100 canonical network IDs: **100/100**, unique, zero collisions
- admissible join key: canonical `network_id`
- direct-key coverage: **0/50**
- exact join: **NOT_JOINABLE**

R319 minimum missing artifact:

> immutable official grader-public 50-row mapping from public `mlp_index` to canonical `network_id`, with the same identity semantics as R224's decimal exact int64 `mlp_seed`.

R319 receipt:
- path: `research/r319/R319_PUBLIC50_R209_JOIN_AUDIT_RECEIPT.json`
- Git blob SHA-1: `517c4ea88041432c6929c561b18b42a01be94761`

## 2. Actual Phase-2 public surface

Official AIcrowd submission #329251 exposes the live Phase-2 partition contract:

https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329251

Publicly visible facts include:

- `50/50 public scored`
- public split: 50 MLPs
- private/holdout split: 50 MLPs, sealed
- full test set: 100 MLPs
- per-MLP ledger exposes row numbers / names and grading metrics

The visible ledger does **not** publish `mlp_seed`, `network_id`, target fingerprint, evaluator dataset revision, or a public 50-row identity-manifest URL.

Therefore the public submission surface itself does not unblock the join.

## 3. Official WhestBench dataset identity semantics

Official repository:
`AIcrowd/whestbench`

Pinned main commit inspected:
`4794ce8673c1221bdb245b19e933ae0afd7ffa3c`

### Dataset schema

File:
`docs/reference/dataset-format.md`

Git blob SHA-1:
`aeadf7c1246fe7383dfdb6187a6e2826556a72e8`

Pinned URL:
https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/docs/reference/dataset-format.md

The schema specifies one row per MLP and includes:

- `mlp_id: int32` — 0-based index in the logical dataset
- `mlp_seed: int64` — canonical input seed stored in the parquet under seed protocols 3.0/4.0

Under seed protocol 3.0, `mlp_seed` is explicitly the input seed stored in the dataset row. This is the same seed identity class used by R224's canonicalization rule:

`network_id = decimal exact int64 mlp_seed`.

Thus an evaluator dataset using schema/seed-protocol 3.0 inherently contains the direct key R319 needs.

## 4. First-party evidence that evaluator public/holdout identity data exists privately

Official file:
`docs/how-to/parallel-bake.md`

Git blob SHA-1:
`32af5ceb79870dc9546299bed7ca9bc5bcfdbdeb`

Pinned URL:
https://github.com/AIcrowd/whestbench/blob/4794ce8673c1221bdb245b19e933ae0afd7ffa3c/docs/how-to/parallel-bake.md

The official multi-split evaluation example states:

- an evaluation dataset has `public` and `holdout` splits;
- each split has its own explicit per-MLP seed file;
- example seed files contain 50 independent int63 seeds:
  - `public-seeds.json`
  - `holdout-seeds.json`
- each split is baked with `--n-mlps 50`;
- the two splits are combined into one evaluation dataset;
- the example publication command targets
  `aicrowd/arc-whestbench-2026-evals`
  and uses `--private`.

This is direct first-party evidence that the evaluation-data workflow retains the exact row→seed identity information while keeping the combined evaluation artifact private.

It is **not** evidence that the literal example repo name/tag is the exact deployed Phase-2 grader artifact. R322 does not claim that.

## 5. Public dataset viewer is not the grader-public-50 bridge

Official public dataset:

https://huggingface.co/datasets/aicrowd/arc-whestbench-public-2026/tree/v2-phase2

Revision:
`v2-phase2`

Current verified commit observed for that revision:
`aa99830fdc09fad15407b10e8e3459d3e18bba0a`

Metadata:
https://huggingface.co/datasets/aicrowd/arc-whestbench-public-2026/blob/v2-phase2/metadata.json

The public metadata shows:

- seed protocol: `whestbench_explicit_per_mlp_seeds` v3.0
- width: 1024
- depth: 16
- exposed splits:
  - `mini`: 100 MLPs
  - `full`: 1,000 MLPs
- prepared splits: `mini`, `full`

The dataset card states that `mini` and `full` are independent and that `mlp_seed` is the row identity field.

No 50-row grader `public` split appears in this public dataset metadata.

Therefore `aicrowd/arc-whestbench-public-2026@v2-phase2` is **not** the missing grader-public-50 manifest.

## 6. Three-way existence classification

### (a) Manifest exists and is publicly accessible

**NO.**

No official public source found by R322 exposes all 50 current Phase-2 grader-public rows with `mlp_index/mlp_id → mlp_seed/network_id`, nor an immutable public evaluator artifact from which that mapping can be read without authentication/download.

### (b) Exists but is not publicly exposed

**YES — best-supported classification.**

Evidence chain:

1. the live Phase-2 grader has a concrete 50-row public partition;
2. the official evaluation-dataset workflow builds `public` and `holdout` splits from explicit per-row seed files;
3. official schema stores `mlp_id` and canonical int64 `mlp_seed` in each evaluation row;
4. official documentation explicitly illustrates publishing the combined evaluation dataset privately.

Therefore the direct row→seed identity data required by R319 exists in the evaluation-data workflow, but the exact deployed Phase-2 50-row mapping is not publicly exposed.

Caveat: R322 found no public evidence of a **separate standalone manifest file** distinct from the private evaluator dataset/seed files.

### (c) No evidence it exists

**NO.**

There is affirmative first-party evidence that the evaluation dataset construction contains the identity mapping.

## 7. What remains unknown

Public sources do not disclose:

- the exact deployed Phase-2 evaluator dataset repository identifier, if different from the documentation example;
- the exact deployed Phase-2 evaluator tag/revision/commit;
- an immutable hash of the private Phase-2 public-split parquet or seed list;
- the 50 Phase-2 public `mlp_seed` values;
- a public mapping from the submission ledger's `mlp_index` values to those seeds.

No such values are inferred from `mlp_name` or row order.

## 8. Minimal unblocker

The smallest user/platform-provided artifact that would unblock the exact R319 join is:

> an immutable official export for the current Phase-2 grader public split containing exactly 50 pairs `(mlp_index, mlp_seed)`, together with an immutable artifact identifier/hash and an explicit statement that `mlp_seed` uses WhestBench seed protocol 3.0 canonical input-seed semantics.

Because R224 defines:

`network_id = decimal exact int64 mlp_seed`

that export is sufficient to test all 50 IDs directly against the already committed R209/R224 100-row identity set.

Preferred strengthening, but not minimally required:

- `target_sha256` per row;
- evaluator dataset repo/revision/commit;
- parquet/blob SHA-256.

R322 stops here. No score is calculated.

## Safety / execution accounting

- code/estimator execution: **NO**
- benchmark: **NO**
- Actions: **NO**
- dataset/dependency download: **NO**
- login/authentication: **NO**
- private/holdout/full access: **NO**
- paid compute: **NO**
- competition submission: **NO**
- main changed: **NO**
- PR changed/opened: **NO**
- control changed: **NO**
- report-only branch: **YES**
