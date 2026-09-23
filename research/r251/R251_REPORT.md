# R251 — Global-accuracy method research

Status: **INCONCLUSIVE — parent preflight runtime unavailable before scientific measurement**

Attempt: `R251-global-accuracy-method-20260923`  
Owner: `global-accuracy-method-research`

## Scope and ancestry

R251 is accuracy-first and was opened only after R231/R239/R245/R249/R250 were terminal with receipts. The full `research/history.json` blob read for deduplication was `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`.

Required evidence read before freezing:

- R231 receipt commit `f36d8011fe1cf8eadf87e0751a18ca9555f9408f`: V25 error is globally signed/correlated and 61.87% of error energy is in layers 12–15.
- R232 terminal receipt commit `d7acd05ee8b8caa71e6463f0e8dab6eb17fb829b`: DRRE exact-small attempt closed after the frozen high-resolution parent hit a FlopScope symmetry failure; no DRRE accuracy measurement.
- R238 terminal receipt commit `a8bb06f23f416ea4a1c01c655756477849234c74`: RSRF parent control failed before candidate execution; RSRF is closed for this lineage.
- R239 receipt commit `6ba51144732eaadfe5ae8f5fb03d5f20b7561732`: `V25-LAMBDA-LOO-SHRINK` failed the target-free no-worse-all gate; no public panel.
- R245 report/receipt commits `265090b3b83adc2d854826df8d30a973453ffe8b` / `941db3239e675571ccf78138cc9cbc21baab1b45`: output-affecting `math.*` is not acceptable for a new candidate path; use billed `fnp`.
- R249 report/receipt commits `af688d4421f32ed7cc3bacdc8dc63733a4f4f6b2` / `2cc0a2971a32d09b72f86d7951d316619d779937`: array-valued `fnp` arithmetic is the safe path; nontrivial Python-scalar arithmetic remains an eligibility boundary to avoid.
- R250 report/receipt commits `627f0f7a16cf40ec84e8f2774f1b51d9847b245e` / `cc18c09a8ddf19e100a2d1757d4091d47fb33b5c`: `V25-LEG2-R1-TAIL-TRANSPORT` failed its frozen target-free error gate and is closed.

Also excluded by the task: R247 2:4 young-D21 sparsity, R248 rank-1 Kronecker transport, R244 MP-R16, R223 V25-LF, DRRE/RSRF descendants, and every history-closed/rejected family. No R223 or R244 candidate output/artifact was read. No undisclosed leaderboard method was inferred.

## Frozen hypothesis: V25-HK4-ROWLOCAL

The selected distinct hypothesis is a **heteroscedastic row-local K4 off-diagonal closure**.

V25 currently transports a diagonal K4 core and models the off-diagonal regenerated K4 coupling with one scalar coefficient. The frozen candidate keeps the table coefficient for the diagonal transport but deletes the V25 scalar online adaptation. At each layer:

`t_g = (W*W) @ g_prev`

`t_v = var - (W*W) @ var_prev`

`dG = t_g + t_v * lambda_table`

`q = fnp.divide(dG, fnp.maximum(var, 1e-10))`

and replaces the ordered (3,1) slice scaling

`wk431 = C_off * lambda_table`

with

`wk431 = fnp.multiply(C_off, fnp.reshape(q, (-1, 1)))`.

No new transport, rank approximation, source compression, sparsity, per-network fitting, or target-derived coefficient is introduced. The hypothesis is that deep-layer V25 bias partly reflects heteroscedastic fourth-cumulant/covariance coupling that a single scalar cannot represent.

The candidate was **specified but not implemented or executed**.

## Metering and static cost gate

The frozen candidate path introduces only `fnp.maximum`, `fnp.divide`, `fnp.reshape`, and `fnp.multiply`; no `math.*` and no new nontrivial Python-scalar arithmetic is permitted.

Static accounting is non-increasing relative to V25: the candidate removes two `fnp.mean` reductions, scalar ratio/clip/power adaptation, and the second `t_v * lambda + t_g` recomputation. It adds one vector maximum and one vector divide. The n-by-n `wk431` multiply remains one broadcast elementwise multiply. This was frozen as a source-level bound only; exact pinned-FlopScope verification was required before any public panel.

R209 mean measured FLOPs bound: **806,303,721,965**.

## Frozen target-free fixtures

`scripts/r251_fixture_replay.py` freezes two production-shape fixtures: width 1024, depth 16, seeds 251001 and 251002. They are zero-bias, one-latent Gaussian networks. The first layer depends only on latent coordinate 0; later weights are dense deterministic uint32-hash weights. Positive homogeneity makes every neuron exactly two-ray linear, so its exact mean is `(a_plus + a_minus) / sqrt(2*pi)` without Monte Carlo or target data.

Frozen aggregate hashes:

| seed | weights aggregate SHA256 | exact-truth tensor SHA256 |
|---|---|---|
| 251001 | `a8fe9b06bfb36ffd176a062d04855ac21f158ccfb2afb3f0f8786941343d4522` | `5238af31e84e8b58fc89323e31e30c5d73d8619c1dae4ec53466677abf2295e3` |
| 251002 | `4fe37ac2f49c04c8bc37769a99ab49f9a77a31ccc896fef5c15435e8d1be4add` | `5ee74eb505999e0c9068076317158e0fc044d9dc0aa9cc1d6c8d95feaacc3d92` |

The manifest is `research/r251/R251_FIXTURE_MANIFEST.json`. The frozen protocol is `research/r251/R251_PROTOCOL.json`.

## Parent-first gate and forensic stop

The protocol requires the **unchanged pinned V25 parent** to run first on those exact fixtures, with exact replay plus per-layer finite/max-abs/symmetry checkpoints. Candidate construction/execution is forbidden unless that parent gate passes.

The available execution runtime could not import the pinned Phase-2 packages:

`flopscope` → `ModuleNotFoundError`  
`whestbench` → `ModuleNotFoundError`

Environment observed: Python 3.13.5, NumPy 2.3.5, Linux x86_64.

A cache-only dependency check was attempted without network or paid compute:

`python -m pip install --no-index flopscope==0.12.1 whestbench==0.16.1 numpy==2.4.6`

It returned exit code 1: no local distribution for `flopscope==0.12.1`.

The task permits at most one verified-free standard Actions run **only after** all target-free/source/cost gates pass and reserves that run for exactly the public R209 mini-100 panel. Using Actions to repair or execute the target-free parent would violate that frozen sequencing. Therefore the unchanged parent was not executed, its mandatory checkpoints are unevaluable, and R251 stops **INCONCLUSIVE** before candidate implementation.

This is not a scientific rejection of V25-HK4-ROWLOCAL. No candidate accuracy result exists.

## Frozen public gate (not reached)

The exact R209 development panel was frozen as:

- `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`
- dataset metadata SHA256 `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`
- `mini:all-100`, 100 rows, shape `[16,1024]`, float32
- whestbench 0.16.1; FlopScope 0.12.1+np2.4.6
- name/order SHA256 `18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce`

If preflight had passed, the single-run gates would have been: zero failures; exact row/hash identity; mean adjusted score <= `7.761877568111363e-9` (=0.95×R209); >=55/100 improved; paired gain >2 descriptive SE; mean FLOPs <=806,303,721,965; max residual <0.4 s. No rank/comparability inference.

## Scope ledger

No estimator implementation, benchmark, Actions run, public mini-100 run, retry, second method, paid compute, private/holdout access, submission, leaderboard action, canonical V25 edit, or gate relaxation occurred. R223/R244 candidate outputs/artifacts were not read.
