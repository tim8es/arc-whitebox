# E100 independent-review handoff

Status: **HANDOFF ONLY — not an independent approval**

Source result commit: `8c503cf3bade5e3323f3e0a2e6b7d02c6c890696`

Sole frozen Stage-A: run `35286592051`, job `105420177508`, artifact `10525165155`.

## Core mathematical identity to verify

For a square iid Gaussian matrix G, QR with deterministic sign normalization of the diagonal of R yields a Haar-distributed orthogonal Q. Each row q_i is therefore marginally uniform on the unit sphere S^(n-1).

If r_i is independent with r_i^2 ~ chi-square(n), then x_i = r_i q_i has the standard Gaussian polar decomposition, hence each row is marginally exactly N(0,I_n).

E100 uses independent radii per row and appends -x_i. Therefore every individual trajectory has the same Gaussian input law as the iid-antithetic comparator. The within-block joint law is intentionally different: positive directions are orthogonal. The final sample mean remains unbiased because unbiasedness requires correct per-sample marginals, not independence.

## Frozen observed evidence

- aggregate iid-antithetic MSE: `1.1734719982468077e-04`
- aggregate orthogonal-antithetic MSE: `2.209970715494368e-05`
- ratio: `0.1883275202813626`
- wins: `8/8`
- worst network ratio: `0.4780911047150302`
- deterministic replay max abs: `0.0`
- conservative production cost: `140319042219` FLOPs
- utilization: `0.06380971272801617`
- static slack to the frozen `0.12 * 2^41` Stage-A cost gate: `123563748447.24` FLOPs.

## Required independent audit gates

1. **Marginal-law proof**: independently confirm the QR sign convention preserves Haar Q and that row-wise independent chi radii give exact Gaussian marginals.
2. **No hidden distribution change**: confirm only cross-trajectory dependence changed; network weights, trajectory count, reference law, and per-trajectory input marginal are identical in law.
3. **Reference independence**: confirm reference, iid comparator, and orthogonal candidate RNG seed families are disjoint and no target/reference information enters candidate sampling.
4. **Accounting**: independently reproduce the width-1024/depth-16/N=4096 cost expression. Explicitly decide how competition accounting treats QR, RNG, chi-square generation, ReLU operations, and reductions. The current margin is large, but omitted billable work must be recorded rather than assumed free.
5. **Determinism/portability**: check whether the QR sign normalization and NumPy QR are stable enough for the intended execution environment; this is an engineering portability question, not permission to rerun Stage-A.
6. **Protocol integrity**: verify there was exactly one scientific Stage-A run on E100 and no sample-count/block-size/seed sweep.
7. **Scope**: do not infer ARC/public raw MSE from the width-32 synthetic result. `scientific_go=false` remains authoritative.

## Allowed next action after independent PASS

Only a **new experiment ID** may implement the same frozen Haar-orthogonal antithetic law in the competition estimator/runtime and perform local production-shape cost/determinism checks before any public data.

No E100 rerun, rescue, tuning, alternate block construction, public/public-mini, scorer, holdout/full, canonical mutation, ledger mutation, or merge.
