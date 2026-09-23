# R252 frozen protocol — V25 D21-sensitivity weighted confinement Gram

Status: **FROZEN BEFORE THE SOLE ACTIONS WORKFLOW**  
Run ID: `R252-one-shot-actions-global-accuracy-20260923`

## 1. Evidence boundary and novelty

R252 is accuracy-first, motivated by R231's exact R209 mini-100 audit: V25 raw error is diffuse rather than tail-dominated, so a global accuracy mechanism is required. Full immutable history was deduplicated from `research/history.json` (194 experiment IDs; blob `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`) and the legacy ledger, plus R231/R232/R238/R239/R245/R249/R250/R251 evidence. R230 is used only for the negative fact that leading methods are undisclosed; no leader method is inferred.

Excluded families remain excluded: R251 GFNP; R232 DRRE descendants; R238 RSRF descendants; R247 2:4 young-D21 sparsity; R248 rank-1 Kronecker transport; R250 LEG2-R1; R244 MP-R16; R223 V25-LF; historical source dropping/windowing, hub-column/CP caps, source cubature, mixture/activation-pattern closure, response-aligned/adjoint lanes, Walsh/FWHT/serializer lanes, precision changes, rank/range-finder ladders, and other closed/rejected families. R223/R244 candidate outputs/artifacts are not read.

Exactly one candidate is frozen:

**V25-D21-SWG — D21-sensitivity weighted confinement Gram.**

The pinned V25 shared old-source basis (F72/F73) chooses its range from a weighted leg Gram. At source birth the parent stores
`dA = 9 + w2^2 + 9 e^2`, `dP = 1 + s^2`, a hub-leg-energy heuristic. But the dominant downstream accuracy channel is the D21 contraction. Its leading right-factor groups are

`D21 ~= LA A^T + LP P^T + thin`,
`LA = 2(AP)w2 + (PP)e`,
`LP = (AA)w2 + (PP)s/3 + 2(MP)/3`.

R252 changes only the static column weights used when a source later enters the shared basis, keeping all ranks, age gates, transports, contractions, K4 regeneration, lambda adaptation, D21 feedback, final-layer trim and coefficient tables unchanged:

- `dA_parent = 9 + w2*w2 + 9*e*e`
- `dP_parent = 1 + s*s`
- `dA_R252 = 4*w2*w2 + e*e`
- `dP_R252 = w2*w2 + 0.1111111111111111*s*s`

The coefficients are the squared leading D21 sensitivities (2,1,1/3), not fitted parameters. The method is network-agnostic, target-free, deterministic, has no seed choice, no per-network rule and no parameter sweep. It is distinct from changing rank, sketch, source count or transport representation.

## 2. Pinned parent and source patch

Parent: `methods/public_504aldo/estimator_v25.py` at R209 code commit `dff3dd65e9d2210e02418cca99e05556f6bf2c75`, Git blob `195373a110215256b759d7c172ba8c923c62e5cc`, SHA256 `c0ae6f12d27d851ddd104dd749ac1f2a6400a6b18a0b4104c389150b93bd4b20`.

Candidate construction is forbidden until the unchanged-parent gate passes. The workflow freezes an exact two-anchor textual patch and asserts each anchor occurs exactly once. It then writes a temporary candidate source only after parent GO. No canonical V25 file is edited.

The scientific delta introduces only arithmetic whose array operand is already an `fnp.ndarray`: multiplication/addition by literal constants. It adds no `math.*`, Python scalar division, scalar reduction/materialization, numerical stdlib call, new numerical library, FFI or concurrency. The literal `0.1111111111111111` is shipped data, not runtime scalar division. Before any public panel the workflow must statically verify these exact patch anchors and fail closed if the integrated delta contains a new output-affecting Python numerical path.

R249 remains binding. R252 does not generalize the narrow `fnp.sqrt(2.0 / width)` example into permission for arbitrary scalar arithmetic.

## 3. New deterministic exact-truth fixture

Exactly one new target-free fixture, ID/seed `R252-BLOCK2-252001`:

- width 1024, depth 16, float32 dense weights;
- 512 independent 2x2 blocks per layer, no cross-block weights;
- each block is selected deterministically from six frozen dyadic 2x2 matrices by
  `index = (252001 + 17*layer + 29*block + 7*layer*block) mod 6`;
- no competition network, target, name or seed is used;
- exact construction and exact-truth algorithm are in `research/r252/r252_fixture.py`;
- expected dense concatenated weight SHA256: `1ed998cad7f2ba4c8259f70a241913359ac49b7b0252d91a0c578539893ddfb0`;
- expected exact all-layer mean truth SHA256 (little-endian float64 C-order, shape 16x1024): `0803ca4d381ad13ab0842fcd4775a3e4b1ad2f1409f517d196ac89073c479946`.

Exact truth is analytic, not Monte Carlo. Each 2D block is positively homogeneous. On every angular interval its depth-l ReLU map is linear in `(cos theta, sin theta)`; the fixture algorithm splits intervals at every exact ReLU zero crossing and integrates each linear piece analytically over angle, multiplying by the exact 2D Gaussian radial mean. The frozen implementation has 5-9 angular regions per block/layer.

No alternate fixture, resize, rescale, reseed, truth approximation, Monte Carlo reference or retry is allowed.

## 4. One standard GitHub-hosted workflow only

Repository visibility is verified public before trigger. Official GitHub documentation states standard GitHub-hosted runners are free for public repositories; R252 uses exactly one standard `ubuntu-24.04` job, no larger/self-hosted runner and no paid/private resource.

The workflow pins and verifies before science:

- Python `3.11.16`;
- NumPy `2.4.6`, CPython-3.11 manylinux x86_64 wheel SHA256 `89cd468399cfd2504718f0ba50e410dca55a170b61a02ad92bb18c8a65186e93`;
- FlopScope `0.12.1` wheel SHA256 `cd08df7e0eb468117b9a48b82d076130a9a9858ec20fdc0d015e2bd477519582`;
- WhestBench `0.16.1` wheel SHA256 `1a8e2620880221eb357056b0fdd65425b026dab222657f54ee202bd75dab987e`.

Any runner/cost/version/hash mismatch stops before science. There is no retry or second workflow.

## 5. Mandatory unchanged-parent gate — first scientific measurement

The sole workflow reconstructs and hashes the frozen fixture/truth, verifies the pinned V25 bytes, constructs a WhestBench `MLP(width=1024, depth=16)`, and runs the **unchanged** parent first under FlopScope.

Without editing or monkeypatching FlopScope, the harness retains forensic checkpoints for every returned prediction layer and observes covariance state non-invasively from the unchanged Python frame for diagnostics only. Retained fields include:

- fixture/source/runtime hashes;
- prediction shape and byte hash;
- per-layer prediction finite + max-abs;
- per-layer covariance finite + max-abs + max `|C-C.T|` when the state is observable;
- parent FLOPs and timing summary;
- exact-truth per-layer MSE, all-layer MSE and final-layer MSE.

Parent GO requires: exact hashes; shape (16,1024); all predictions/checkpoints finite; every observed covariance symmetry residual `<=1e-5*max(1,max_abs)`; no exception/budget/time failure.

**Parent failure => terminal INCONCLUSIVE.** Candidate source is not constructed. No fixture/seed/scale change and no retry.

## 6. Single candidate falsifier — only after parent GO

After parent GO, construct exactly the frozen two-anchor candidate and run it once on the identical fixture/runtime.

All gates are mandatory:

- candidate source patch identity exact and no new prohibited/unresolved numerical path in the R252 delta;
- deterministic fixture/truth reconstruction hashes exact;
- finite candidate output, shape (16,1024), no exception/budget failure;
- candidate final-layer MSE `<=0.95 * parent final-layer MSE`;
- candidate all-layer MSE `<=0.98 * parent all-layer MSE`;
- at least 12/16 per-layer MSE values strictly improve;
- maximum per-layer degradation ratio `<=1.10`;
- candidate measured FLOPs `<= parent measured FLOPs`;
- candidate residual wall time `<=1.05 * parent residual wall time + 0.005 s`.

Any failure => terminal DEVELOPMENT NO-GO / SCIENTIFIC_REJECT. No public panel and no second method.

## 7. Conditional exact R209 public mini-100

Only if every runtime/parent/source/target-free/cost gate passes, the **same workflow** may continue once to:

`hf://aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`, exactly 100 rows, width 1024, depth 16, float32, metadata SHA256 `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`, R209 name/order SHA256 `18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce`.

Frozen development GO gates:

- exact R209 dataset/name/order identity and normalized-row identity;
- zero failures;
- mean adjusted score `<=0.95 * 8.170397440117225e-9 = 7.761877568111363e-9`;
- at least 55/100 rows have lower adjusted score than R209;
- paired parent-minus-candidate adjusted-score mean gain > 2 descriptive SE;
- mean measured FLOPs `<=806303721965`;
- max residual wall time <0.4 s.

This is development evidence only; no rank or exact leaderboard comparability inference is permitted.

## 8. Stop rules

No R251/GFNP execution; no second R252 attempt/workflow; no retry; no second method; no gate relaxation; no paid/private/holdout; no R223/R244 candidate output/artifact access; no submission/leaderboard mutation; no canonical V25 edit. Every terminal path writes a durable machine-readable artifact and the queue is finished from that evidence.
