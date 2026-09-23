# R279 — official Phase-2 visible-50 local-path audit

**Verdict: NO compliant metadata/docs-only path is currently published for reproducing the exact online Phase-2 visible-50 panel locally.** The grader/meter version pair is public and can be pinned; the missing piece is the panel identity/data mapping.

## Primary-source findings

| Surface | Endpoint / artifact | Permission | What it proves |
|---|---|---|---|
| AIcrowd public grading page | https://assets.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/329251 | Public web read | Phase 2 exposes **50 public scored + 50 private sealed**. The public ledger exposes `mlp_index`, `mlp_name`, scores/FLOPs/timing. It does not expose `mlp_seed`, `network_id`, weights, ground-truth tensors, or target fingerprints. |
| AIcrowd REST client contract | `AIcrowd/whestbench@v0.16.0:src/whestbench/aicrowd_client.py`, blob `000750d57a7720c336e751f89efc7bc05ae78fa5` | `Authorization: Token <api_key>`; submission status authorized to caller's own submission | Documented endpoints are identity, eligibility, upload presign, create submission, and own-submission status. No test-panel/dataset download endpoint is exposed by the first-party client contract. |
| HF public dataset | https://huggingface.co/datasets/aicrowd/arc-whestbench-public-2026/tree/v2-phase2 | Public repo, CC-BY-4.0 | The published Phase-2 release has only `mini=100` and `full=1000` splits. `metadata.json` likewise lists only prepared `mini` and `full`; no `visible50` split/config/manifest is published. |
| HF schema/reproducibility | https://huggingface.co/datasets/aicrowd/arc-whestbench-public-2026/blob/v2-phase2/README.md | Public metadata/docs | Published rows contain `mlp_seed`, weights and baked `all_layer_means`; `mlp_name` is derived from `mlp_seed` and carries no additional identity information. Seeds can reproduce published-dataset weights, but the online visible-50 seeds are not exposed by AIcrowd. |
| Current starter kit | `AIcrowd/whest-starterkit@5eb9aa1455fcb3216af55994bdf25dc242b95797:pyproject.toml`, blob `2c1d562a2073046d6912868184b52c8c593d23c5` | Public source | Current kit installs `whestbench>=0.16.1,<0.17.0` and `flopscope>=0.12.1,<0.13.0`, while its own source states the **grader** is `whestbench v0.16.0` with `flopscope[server]==0.12.0`. |
| Exact grader releases | `AIcrowd/whestbench@v0.16.0` pyproject blob `f1c4c3af8b355c9a4249f6db959cdaff083394c4`; `AIcrowd/flopscope@v0.12.0` pyproject blob `abffcea12208ada091bceaca2e4c945b6b9d54a0` | Public releases/source | The exact grader version pair is publicly identifiable. `flopscope 0.12.0` publishes the `server` extra pinned to `flopscope-server==0.12.0`. Version reproduction is therefore not the remaining blocker. |

## Reconciliation with R271

R271 found 0/50 exact `mlp_name` overlap with immutable R209 mini-100, no public online `network_id`/target fingerprint, and an evaluator-version mismatch. This audit independently confirms the structural reason: the HF public release and the AIcrowd online test set are different published surfaces. HF metadata offers no `visible50` selector, while AIcrowd exposes only a score ledger for those 50.

The public HF `full` split is **1,000 public MLPs**, not the online "full test set" of 100 MLPs (50 public + 50 sealed). No benchmark data was downloaded, so no row-level search inside the 1,000-MLP split was attempted or inferred.

## Minimum missing artifact

The minimum remaining public artifact is an **official immutable visible-50 manifest** that maps every online `mlp_index` / `mlp_name` to a machine-stable identity usable against a public dataset revision — preferably `mlp_seed` or an explicit public dataset row ID — plus `target_sha256` (or equivalent target fingerprint).

If those 50 rows are not already present in an existing public HF revision, then a public immutable `visible50` dataset artifact containing the exact weights and baked ground truth is additionally required. The grader/meter versions are already known: `whestbench 0.16.0` + `flopscope[server] 0.12.0`.

**Bottom line:** without submission, sealed/private/full-test access, or guessing from names/order, there is currently no first-party documented route to obtain the exact online visible-50 panel locally.

## Constraints observed

Metadata/docs only. No benchmark-data download, estimator/benchmark execution, Actions, submission, paid resource, sealed/private/full-test access, leaderboard mutation, or canonical/model edit.
