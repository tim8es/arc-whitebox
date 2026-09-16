# E095 — target-free output-subspace projected residual sampling

Idempotency key: `ARC-E095-OUTPUT-SUBSPACE-RESIDUAL-SAMPLING-20260917`

Status: **PREREGISTERED / PROTOCOL-ONLY**.

## Objective

Test whether the final-layer error of deterministic covariance propagation is sufficiently concentrated in a small, target-free output subspace that Monte-Carlo residual correction can estimate only that component and thereby reduce sampling variance per FLOP.

This lane is motivated by two public observations, used only as hypothesis provenance rather than benchmark evidence:

1. the Phase-1 technique census reports that much of a deterministic method's final error can concentrate in a low-dimensional (~6D) subspace computable from weights alone;
2. current Phase-2 public write-ups show a gap between covariance closure and stronger methods, while the V29 catalogue concludes that simply extending its per-source K3 family is not the missing representation.

No public benchmark target, scorer output, holdout/full target, E092 fitted coefficient, or E049-E053 V29 state is used by E095.

## Provenance / independence

- Branch: `research/e095-output-subspace-residual-sampling-20260917`.
- Direct base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Frozen deterministic base: `baselines/covariance_propagation.py` blob `f547b378faa56e299559bcefc89909fd401b8026`.
- Public motivation only:
  - AIcrowd forum topic `18157`, technique census / O10 low-dimensional error-subspace observation;
  - AIcrowd forum topic `18218`, V29 cost anatomy and representation-floor discussion.
- E095 is **not** a rescue/reparameterization of E092: there is no offline residual fit, ridge model, learned coefficient, calibration corpus, network classifier, shrinkage or gating of an E092 correction.
- E095 is **not** a V29/old-tier/K3/K4/harmonic/diagram/source-axis/FWHT/Strassen modification. It uses the canonical covariance baseline plus fresh within-MLP samples.

## Frozen estimator mechanism

For one MLP, first run covariance propagation and retain:

- deterministic mean prediction `b_l` for every layer;
- the final predicted post-ReLU covariance `C_L`.

Let `U in R^(W x k)` be the eigenvectors of `C_L` associated with the `k=6` largest eigenvalues, ordered descending with deterministic sign canonicalization (largest-magnitude entry in each eigenvector is non-negative). `k=6` is frozen before any Stage-A target is computed.

Draw a fixed antithetic sample set through the actual MLP and compute the final sample mean `m_N`. The E095 final-layer estimate is

`b_L + U U^T (m_N - b_L)`.

Intermediate layers remain the covariance-baseline means. The estimator therefore samples the actual network but retains only the sampled residual component inside a target-free six-dimensional output subspace. No target/reference quantity participates in construction of `U` or in inference.

For scientific comparison only, Stage-A also records the ordinary full sample mean `m_N` from the exact same trajectories. It is a comparator, not a second candidate.

## Frozen synthetic Stage-A corpus

No benchmark data is used.

- architecture: width `32`, depth `6`;
- weights: iid `N(0, 2/width)` in float64;
- MLP seeds: `95000..95007` (8 networks);
- independent high-sample reference seed: `2_000_000 + mlp_seed`;
- candidate sample seed: `3_000_000 + mlp_seed`;
- high-sample reference: `65536` total antithetic samples;
- candidate/full-sample comparator: `2048` total antithetic samples;
- subspace rank: exactly `6`.

All seeds, sample counts, architecture and gates are frozen before reference generation. There is no seed/rank/sample-count sweep.

## TDD stages

### RED

Before production implementation, commit focused tests importing an absent `methods.e095_output_subspace_sampling` module. A dedicated focused workflow must run once and fail for the missing module.

### GREEN

Implement only the frozen mechanism and make the same focused tests pass. Tests must cover deterministic synthetic MLP generation, covariance-state finiteness/symmetry, deterministic eigenvector sign canonicalization, exact rank-6 projection algebra and antithetic-sample determinism.

### Scientific Stage-A

After GREEN, create one path-isolated workflow whose creation triggers exactly one Stage-A run. It writes and uploads one JSON receipt. No scientific rerun is permitted.

## Frozen Stage-A measurements

For each of 8 MLPs record:

- covariance-baseline final-layer MSE versus high-sample reference;
- ordinary 2048-sample final-layer MSE using the frozen candidate sample stream;
- E095 projected-residual MSE using those exact same 2048 trajectories;
- projected/base MSE ratio;
- projected/full-sample MSE ratio;
- oracle subspace capture `||P delta||^2 / ||delta||^2`, where `delta = reference - b_L`, used only to evaluate the hypothesis after `U` is already fixed;
- finite/deterministic checks.

Aggregate the squared errors across all neurons/networks before forming aggregate ratios.

## Frozen GO gates

All must pass:

1. finite baseline, reference, sample and projected outputs;
2. deterministic repeat in the same environment (`max_abs_diff == 0` for subspace and projected estimate);
3. aggregate `projected_mse / baseline_mse <= 0.80`;
4. aggregate `projected_mse / full_sample_mse <= 0.75`;
5. projected estimator beats baseline on at least `6/8` MLPs;
6. projected estimator beats ordinary full-sample mean on at least `6/8` MLPs;
7. worst per-network projected/base MSE ratio `<= 1.50`;
8. mean oracle residual-energy capture by the frozen target-free subspace `>= 0.60`;
9. at least `6/8` networks have residual-energy capture `>= 0.50`;
10. conservative Phase-2 all-in utilization upper bound `<= 0.12` under `B=2**41`.

Any failed gate => terminal **NO-GO / DROP**. No rank change, alternative subspace, sample-count change, seed change, regularization, learned selector, gating, blending, rescue or scientific rerun is allowed in E095.

## Phase-2 FLOP upper bound

For a future width `W=1024`, depth `D=16`, candidate sample count `N=4096`, rank `k=6`, budget `B=2**41`:

- covariance propagation conservative upper: `5 D W^3`;
- symmetric eigendecomposition/sign handling conservative upper: `10 W^3 + 4 W^2`;
- antithetic forward samples through all layers: `2 N D W^2 + 2 N D W`;
- sample reduction plus rank-6 projection: `< 4 N W + 6 W k + 10 W`.

Numerically the declared conservative bound is below `0.12 B`; the Stage-A receipt must calculate the exact integer expression and fraction. This is an analytic feasibility gate only: a later Phase-2-shape implementation would still have to measure flopscope billing before any promotion.

## Promotion rule

Stage-A GO would establish only the mechanism: a target-free output subspace can convert sampling FLOPs into lower final-layer error than both covariance alone and an equal-trajectory full sample mean on the frozen synthetic corpus. It would authorize a **new** successor protocol for Phase-2-shape package-safe implementation and flopscope measurement, not public/scorer execution.

## Prohibited

No public/public-mini benchmark, scorer, holdout/full split, benchmark labels, E092 coefficient reuse, V29 reuse, fitting/tuning/sweep, rank/sample/seed search, rerun/rescue, canonical/ledger mutation, merge, or public promotion is authorized by E095.
