# R319 — grader-public-50 ↔ R209 Mini-100 exact join audit

**Verdict: NOT_JOINABLE.**

R319 closes only the identity-bridge gap left by R314. It does not repeat the general score-comparability audit.

Using only already committed project artifacts and direct machine identity keys, the 50 grader-public MLP rows cannot be joined exactly to the 100 R209 V25 Mini-100 rows. The blocker is one-sided: R209/R224 has complete canonical `network_id` and target fingerprints for all 100 rows, while the committed grader-public-50 evidence exposes **0/50** `network_id` values.

Display-name equality, row order, rank, score, MSE, or similar values are not used as identity evidence.

## 1. Prior-audit stop check

R305, R311, and R314 were checked first.

- **R305**: verdict `NOT_COMPARABLE`; its committed branch contains only its report and receipt. Contrary to the premise that R305 already contains a public-50 name→network-ID map, the R305 receipt explicitly records public fields only `mlp_index` and `mlp_name`, with `network_id_exposed=false` and `target_sha256_exposed=false`.
- **R311**: `same_panel_proven=false`; missing field explicitly includes an immutable public-50 identity/join key.
- **R314**: `exact_public50_to_r209_join_proven=false` and `exact_panel_identity_proven=false`.

Therefore the requested exact-join question was **not already closed positively**, and R319 proceeds only to the direct-key inventory.

## 2. Immutable evidence used

### R305

Branch head:
`d6124d78714e9882f7d7384b6ad6482af22f7301`

Artifacts:
- `research/r305/R305_VISIBLE50_MANIFEST_AUDIT.md`
  - Git blob SHA-1: `d45093692dea0338acd65e612743ea5ed32e74ed`
- `research/r305/R305_RECEIPT.json`
  - Git blob SHA-1: `6dca6965c3ef27263d1d1cd2aea12d303a485d9d`

R305 records:
- grader-public rows: 50;
- public fields: `mlp_index`, `mlp_name`;
- `network_id_exposed=false`;
- `target_sha256_exposed=false`;
- prior name overlap reported as 0/50, but R319 does **not** use display/name equality as an identity bridge.

### R271 grader-public identity audit

`research/r271/R271_IDENTITY_AUDIT.json`
- Git blob SHA-1: `dae9e30f803918f642710e50e0191568f9939578`
- recorded SHA-256: `c1d329541d544f396e02b18ddb2c78c02bf73da911ff7a97f3bd0b1827ac1260`

Its 50 public rows contain:
- 50/50 `mlp_index`;
- 50/50 distinct `mlp_name`;
- **0/50 `public_network_id`**;
- every row: `network_id_exposed_by_official_page=false`.

R271 also explicitly records:
- `exact_visible50_network_ids_available=false`;
- `exact_id_match_test_possible=false`;
- `row_order_used_for_identity=false`;
- `exact_same_panel_proven=false`.

### R224 / R209 Mini-100 identity evidence

R224 normalization commit:
`8fb0afb77ae834d88bae29557a41356d4d98401f`

`research/r224/R224_MINI100_FINGERPRINTS.json`
- Git blob SHA-1: `9ecde34282c3fbef51ff3b11d4ec439012b3c52d`
- receipt-recorded JSON SHA-256: `ae0b3659568cc1297aeac89f6babf9f2df2b2752d0216e638141ec6411f629a4`
- dataset metadata SHA-256: `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`
- network-ID rule: **decimal exact int64 `mlp_seed`**
- target-fingerprint rule: SHA-256 of C-contiguous raw float32 `all_layer_means` bytes
- records: 100
- network IDs present: 100/100
- unique network IDs: 100
- network-ID collisions: 0
- target SHA-256 present: 100/100
- unique target hashes: 100
- target-hash collisions: 0

`research/results/R209-v25-mini100.json`
- Git blob SHA-1: `0183d0570f7c9965e00e8553ffc003c313865232`
- receipt-recorded normalized-result SHA-256: `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`
- original R209 V25 artifact ID: `10617855153`
- original artifact ZIP SHA-256: `820bf9368beac10ea537fc018c3c2185bbd310b9542603cbfa8309519c8e3e08`

The normalized R209 result has 100 `per_network` rows, each with:
- `network_id`;
- `target_sha256`;
- per-MLP metric fields.

Observed exact-key integrity:
- network IDs present: **100/100**
- unique network IDs: **100**
- network-ID collisions: **0**
- target SHA-256 present: **100/100**
- unique target hashes: **100**
- target-hash collisions: **0**

Panel:
- dataset: `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`
- split: `mini:all-100`
- count: 100
- stage: `development`
- dataset metadata SHA-256: `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`

## 3. Exact join accounting

Only a shared direct machine identity key is admissible.

| Join property | Grader-public 50 | R209 V25 Mini-100 |
|---|---:|---:|
| Rows | 50 | 100 |
| Canonical `network_id` present | **0/50** | **100/100** |
| Unique canonical `network_id` | not observable | **100/100** |
| `network_id` collisions | not assessable because IDs absent | **0** |
| `target_sha256` present | **0/50** | **100/100** |
| Unique target fingerprints | not observable | **100/100** |
| Direct-key joinable rows | **0/50 proven** | N/A |
| Full 50-row join proven | **NO** | **NO** |

The `0/50 proven` figure means there are zero public rows carrying an admissible direct key with which an R209 row can be matched. It does **not** mean that zero underlying networks overlap.

The 50 public `mlp_name` values and R209 names are not used for joining, even though prior audits recorded their overlap, because the task requires direct identity keys and forbids inference from display names.

Row position is likewise not used.

## 4. Split/panel conclusion

The two committed objects remain different until an exact bridge is supplied:

- leaderboard/grader public split: **50 scored public MLPs**;
- R209 V25: **100-row `v2-phase2 mini:all-100` development panel**.

Existing evidence does not establish that the grader-public 50 are a particular 50-row subset of R209 Mini-100.

Accordingly:
- exact public50 → R209 row mapping: **NOT PROVEN**;
- coverage of a direct-key mapping: **0/50 available**;
- full join: **NOT_JOINABLE**;
- exact public-50 V25 subset recomputation from existing R209 rows: **not justified**.

## 5. Minimal missing artifact

The minimal missing artifact for the **identity join itself** is:

> an immutable official grader-public 50-row manifest that maps each public `mlp_index` to the canonical machine `network_id`, with an explicit statement that this `network_id` uses the same identity semantics as R224's decimal exact int64 `mlp_seed`.

That artifact alone would make an exact ID-membership join test possible against the already committed 100 unique R209/R224 IDs.

`target_sha256` would strengthen identity and detect target mismatches, but is not the minimum field required if the official `network_id` semantics are explicitly identical.

If the resulting 50 IDs are not all present in R209, then a second artifact would be required for score reconstruction: immutable V25 per-MLP results for the missing exact grader-public networks. R319 does not assume that outcome.

## 6. Final verdict

**NOT_JOINABLE.**

The exact bridge is absent from committed evidence. In particular, the committed R305 artifacts do **not** contain the presumed name→network-ID mapping; they document that the official public surface did not expose one.

No data/dependency download, code execution, benchmark, Actions, private/holdout/full access, submission, main edit, PR edit, or control edit was performed.
