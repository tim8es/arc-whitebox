# E017 — data-dependent shared quadratic basis for old-tier Hadamard products

Status: **NO-GO at quantitative preflight; no implementation diagnostic**

Idempotency key: `ARC-E017-SEARCH-20250915`

Base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

## Frozen comparator

E007/V25 remains the fixed score comparator:

- adjusted final-layer score: `8.17e-09`
- raw final-layer MSE: `2.23e-08`
- mean utilization: `0.36666448`
- failures: `0/100`

At unchanged raw MSE, beating `8.17e-09` requires utilization `< 0.3663677130`, i.e. an absolute saving of only `0.000296767` from E007. The candidate therefore only needs a real billed-cost cut if it preserves accuracy.

## Mechanism

V21/V24/V29 old sources share a dense data-dependent basis `Qc`:

`A_s = Qc F_A,s`, `P_s = Qc F_P,s`.

The remaining old-tier wall is that D21 terms require elementwise products such as `A_s*P_s`, `A_s*A_s`, and `P_s*P_s`, forcing dense legs to be re-formed and then re-contracted.

E017 asks whether those elementwise products can instead be represented in one **shared quadratic basis**

`H(Qc) = span { q_a ⊙ q_b : 1 <= a <= b <= r }`,

then optionally compressed with a data-dependent leverage/subspace basis. This is distinct from E008: E008 used an oblivious TensorSketch collision map; E017 would use the actual `Qc` and its quadratic/Khatri–Rao feature space.

## Exact target

Remove a material fraction of the V29 old-tier `old_legs + shared` cost without changing the K3 source model, adaptive lambda, scheduling, Strassen/HK joiners, MZ/Prony history, or K4 response model.

Upstream V29 cost anatomy gives:

- total steady-state bill: about `260.1` units, where one unit is `2*n^3` FLOPs;
- K3 old tier: `106.8` units = `41.1%` of the bill;
- old dense re-form/re-contract work is roughly `0.7–0.8` unit per old source-layer, with total old-source cost about `1.1` unit/source-layer.

A useful E017 representation therefore has to be materially below `1.1` unit/source-layer while preserving the D21 fidelity requirement (`~2.2%` relative error from the upstream F71/F88 gate).

## Quantitative preflight

For width `n=1024`, the active old basis ranks in the current chain are in the `r=224..384` range. The symmetric quadratic feature count is

`M = r(r+1)/2`.

Thus:

| r | M = r(r+1)/2 | M / n |
|---:|---:|---:|
| 224 | 25,200 | 24.61 |
| 256 | 32,896 | 32.13 |
| 384 | 73,920 | 72.19 |

The quadratic feature count already exceeds the ambient neuron dimension once `r >= 45` (`45*46/2 = 1035 > 1024`). For a generic dense basis the Hadamard-square span therefore saturates the full ambient dimension `n`, rather than producing a small shared subspace. The current `Qc` is a data-dependent dense range-finder basis, not a Fourier/polynomial basis with multiplicative closure.

Even if one explicitly forms a compressed map from the `r^2` coefficient products into `s` shared quadratic coordinates, a dense data-dependent projection costs on the order of

`n * s * r^2`

multiply-add work per source/product family. In V29 units (`2*n^3`) this lower-level coefficient map alone is approximately

`s*r^2/(2*n^2)` units.

Examples:

| r | s | coefficient-map units |
|---:|---:|---:|
| 224 | 128 | 3.06 |
| 256 | 128 | 4.00 |
| 384 | 128 | 9.00 |
| 384 | 256 | 18.00 |
| 384 | 1024 | 72.00 |

Those costs exceed the entire current `~1.1` unit old-source-layer budget before reconstruction/contraction. Avoiding that dense coefficient map means evaluating

`(Qc F_A) ⊙ (Qc F_P)`

directly, which is precisely the current dense-leg re-formation path. In other words, exact data dependence does not create a cheaper transform; it algebraically returns to the existing `Qc @ F` operations.

A leverage-score or Khatri–Rao sketch does not repair the dimensional problem: the intrinsic quadratic span is generically ambient-dimensional here, so a high-fidelity subspace embedding must preserve a `k` close to `n`, not a small `k`. At the required `~2.2%` D21 fidelity, there is no source-supported route to `s << n`; E008 already showed that the cheap oblivious alternative has order-of-magnitude product error.

## Primary-source basis

1. Bocci, Carlini, Kileel, **Hadamard Products of Linear Spaces**, J. Algebra 448 (2016), arXiv:1504.04301. The paper develops the geometry/dimension behavior of Hadamard products of linear spaces and shows why coordinatewise products generically expand dimension rather than remain in the original linear space.
   - https://arxiv.org/abs/1504.04301
2. Bharadwaj, Malik, Murray, Grigori, Buluc, Demmel, **Fast Exact Leverage Score Sampling from Khatri-Rao Products with Applications to Tensor Decomposition**, arXiv:2301.12584. This is the relevant data-dependent alternative to oblivious TensorSketch; it accelerates sampling from Khatri–Rao products but does not remove the intrinsic subspace dimension that must be preserved.
   - https://arxiv.org/abs/2301.12584
3. Beretta, Musco, **A Tight Analysis of Khatri-Rao Oblivious Subspace Embeddings**, arXiv:2608.28094. For a `k`-dimensional subspace, Khatri–Rao embeddings still require sketch dimension scaling essentially with `k/eps^2` up to logarithmic factors; when the quadratic span has `k≈n=1024`, this is not a low-rank escape at `eps≈0.022`.
   - https://arxiv.org/abs/2608.28094

## Preregistered diagnostic gate (only if preflight passed)

Had the arithmetic admitted a strong path, the isolated diagnostic would have been frozen as follows:

- public mini dumps only; no holdout or official scorer;
- construct `Qc` from the frozen current old-tier trajectory;
- fit no per-MLP coefficients;
- one fixed data-dependent quadratic basis construction;
- validation requirement: old-tier D21 relative RMS `<= 2.2%` and projected old-source-layer cost `< 0.8` unit;
- projected total utilization must be `< 0.3663677130` at unchanged E007 raw, or otherwise projected adjusted score `< 8.17e-09` using the measured raw ratio;
- finite/deterministic and no residual/resource regression;
- no rank sweep, tuning, scorer, or holdout.

## Kill rule and decision

**Kill before code** if either:

1. the shared quadratic space is generically full ambient rank at the active `r`, or
2. applying a data-dependent compression map costs at least the current old-source-layer budget before the D21 contraction.

Both conditions hold numerically. Therefore E017 is **NO-GO** at preflight.

No tests, implementation code, development run, scorer, holdout, tuning, or sweep are justified under this hypothesis. Re-running E008 with a different sketch would violate the intended novelty constraint without a numerical cost/fidelity path.
