# R248 — distinct V25 efficiency method after R247

## Outcome

**DEVELOPMENT NO-GO before estimator/public measurement.** The frozen target-free structural falsifier failed decisively, so R248 stops before estimator implementation, validation, benchmark, public mini-100 access, or Actions.

## Ownership and evidence boundary

R248 is the transferred existing queue job, owned by `method-research-recovery`, run ID `R248-post-r247-distinct-method-research-20260923`.

Inputs read were the current process/history, immutable R209 V25 normalized baseline, R246 score diagnostic, R247 rejection report/spec/receipt, R245 static-compliance report, exact public V25 source blob `195373a110215256b759d7c172ba8c923c62e5cc`, and the upstream 504aldo findings log. No R223 or R244 candidate artifact/output was read.

The history inventory contains 194 experiments (blob `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`). The obvious cost families already covered/closed include source age/rank confinement, source dropping/windowing, source-axis compression, sketches/sampling, FWHT/structured projection, Strassen/deeper fast-matmul work, trilinear aggregation, precision changes, displacement structure, and the R247 2:4 young-D21 right-factor sparsifier. A literal history search found no Kronecker/Kron/tensor-product/HODLR/butterfly mechanism. The upstream findings log blob `09cf41e8826052ceb83109115cae688c03baaaca` uses “Kronecker” only in cited exchangeability/delta theory, not as a V25 transport-approximation experiment.

## Frozen candidate

Candidate: **V25-KRON1-YOUNG-TRANSPORT**.

Only the young dense A/P transport operator is changed. Parent V25 forms `WD = W * w1_prev` and applies dense `WD @ A` and `WD @ P` to young sources. R248 proposes a fixed rank-1 Kronecker surrogate `A_kron ⊗ B_kron` for `WD`, computed once per layer, and applies it by reshape plus two small batched matrix contractions. Young D21 right-factor contractions remain dense/exact; old tiers, Rres, lambda/feed logic, D3/D21 equations, K4 regeneration, covariance, mean correction and final trim remain unchanged.

Frozen candidate spec:
- path: `research/r248/R248_CANDIDATE_SPEC.json`
- Git blob: `3c8300af8386d9aa8e2e4aa434cc09d06874d233`
- SHA256: `0291e5599b2645d4f334d86f5b8384bdbb4e73655fac76e2396d93b9fab44d37`

This is distinct from R247 because it does not sparsify D21 contraction right factors; it approximates the shared transport operator itself. It is not MP-R16, V25-LF, a source-rank/age change, source removal, random contraction estimation, Strassen/trilinear aggregation, precision change, or displacement structure.

## R245 source-compliance gate

No candidate estimator was implemented because the target-free gate failed. The frozen production contract nevertheless requires:

- no output-affecting `math.*` in `predict()`;
- numerical normalization through metered `fnp.sum`, `fnp.sqrt`, `fnp.maximum`, and `fnp` array division;
- output-affecting linear algebra only through `fnp` reshape/transpose/matmul/einsum;
- fixed official shape constants `n=1024`, `d=32`;
- any newly required nontrivial output-affecting Python-scalar numerical arithmetic changes eligibility to **UNKNOWN** and stops R248 before public measurement.

The offline falsifier uses NumPy/SVD only as a target-free oracle upper bound; it is not estimator/submission code and no public dataset is opened.

## Static cost gate

R209 mean FLOPs are `806,303,721,965`, or `375.4644291312434` units of `2*n^3`.

The same F72/F73 anatomy used by R247 assigns 54 units to young A/P transports and 54 units to young D21 contractions. R248 touches only the 54 transport units.

For `n=d^2`, applying one Kronecker product to an `n x n` transported matrix costs a fraction `2/d` of one dense square product. At the frozen official `d=32`, this is `1/16`. Thus the 54 transport units become 3.375 units. After reserving a conservative 8 units for factor extraction, normalization, copies and integration overhead:

- conservative candidate units: `332.8394291312434`;
- conservative candidate FLOPs: `714,767,231,469`;
- candidate/parent ratio: `0.886473932833993`;
- frozen requirement: `<=0.9`.

The **static cost gate passes**. This is a planning bound, not a measured estimator result.

## Frozen target-free falsifier

Protocol:
- path: `research/r248/R248_PROTOCOL.json`
- Git blob: `be129968bd14578c43b74935d5a36d7d98692d2f`
- SHA256: `cde0830975bb0a140d837adaf423e98578f2911149d1333427aa99a0694332cb`

Falsifier:
- path: `scripts/r248_kron1_transport_falsifier.py`
- Git blob: `ed1609650a842660bf19f94a39adcf395db239e5`
- SHA256: `96ed06013c83cee9910d986cb61b2f1e8eb86df074256295eb7f0836bb7a865f`

The falsifier uses no ARC dataset or targets. It evaluates the **best possible Frobenius rank-1 Kronecker approximation** from an SVD of the rearranged transport operator. This oracle is more favorable than the frozen production one-power approximation, so oracle failure is sufficient to reject the production candidate.

Frozen cases: `n=256`, `d=16`, four fixed seeds × two synthetic transport families. An exact-Kronecker control validates the rearrangement.

GO requires:
- exact-Kronecker control RRMS `<=1e-12`;
- 8/8 realistic cases finite and deterministic;
- every operator/A/P transport RRMS `<=0.015`;
- mean A/P transport RRMS `<=0.012`.

## Falsifier result

Result:
- path: `research/r248/R248_FALSIFIER_RESULT.json`
- Git blob: `16d3df320232828f0254e5c8d48d375cc37edc9a`
- SHA256: `c4ab12de20ecd0bd0208d3519fb18563677fbc1bdb28633cd4b66a90a7588670`
- canonical result hash: `4a379199ec212c777c7418f177280281d97fbcd55c85a4db3623fa0a82fb2f31`

Checks:
- exact-Kronecker control RRMS: `4.812580056623063e-16` — PASS;
- deterministic replay: `8/8` — PASS;
- finite cases: `8/8` — PASS;
- maximum any realistic RRMS: `0.9913359558380901` — FAIL vs `0.015`;
- mean transported A/P RRMS: `0.9846514161220152` — FAIL vs `0.012`.

The best possible rank-1 Kronecker surrogate loses roughly 97–99% of transport fidelity on every realistic synthetic case. Because the oracle itself fails by about two orders of magnitude relative to the frozen structural gate, the cheaper one-power production approximation cannot pass this prerequisite.

## Decision

**R248 DEVELOPMENT NO-GO: V25-KRON1-YOUNG-TRANSPORT fails the frozen target-free structural-fidelity gate.**

Per the frozen protocol, no estimator source, `whest validate`, benchmark, public mini-100 candidate run, or Actions workflow is authorized. The public scientific score gates therefore remain unmeasured.

No retry, second mechanism, per-network tuning, R223/R244 candidate artifact/output read, paid/private/holdout access, submission, leaderboard mutation, canonical V25 edit, or gate relaxation occurred.
