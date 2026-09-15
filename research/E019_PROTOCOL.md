# E019 — pooled multi-mode memoryless K4 residual closure

Status: **preregistered development diagnostic**

Idempotency key: `ARC-E019-MULTIMODE-K4-20250915`

Base: canonical `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

## Frozen comparator

E007/V25 remains the fixed score comparator:

- raw final-layer MSE: `2.23e-08`
- adjusted final-layer score: `8.17e-09`
- mean utilization: `0.36666448`
- failures: `0/100`

Scientific source is the public K3/K4 repository `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`; the dense teacher is `lean/lean_k3_aug.py` blob `8fdaa96fd68f30ce9020e6534626e97ebf71d291`.

## Novel mechanism

Keep the shipped V25 adaptive `lambda_l * C_off` closure frozen. E019 does **not** refit lambda and does not use the E016 rank-1 `q q^T` mode.

For layers 8..14 only, model the remaining dense-teacher off-diagonal K4 residual

`R_l = G_off - lambda_l C_off`

with exactly eight already-live deterministic matrix modes from the upstream F68 regeneration probe:

1. `cc = offdiag(C * C)`
2. `k21 = offdiag(Sym(mu[:,None] * K21.T))`
3. `t = offdiag(Sym(K3v[:,None] * mu[None,:]))`
4. `vv = offdiag(var[:,None] * var[None,:])`
5. `k31 = offdiag(Sym(K31))`
6. `k22 = offdiag(K22)`
7. `mc = offdiag(Sym(mu[:,None] * C))`
8. `mm = offdiag(mu[:,None] * mu[None,:])`

Candidate closure:

`G_off^E019 = lambda_l C_off + sum_m gamma[l,m] B_m`.

There is one pooled 8-vector `gamma[l]` per layer, fitted once on public fit dumps 0..3 by deterministic float64 Frobenius least squares using accumulated 8x8 normal equations. No per-MLP coefficients, no ridge, no subset selection and no mode sweep are allowed. The K4 diagonal remains exact.

## Quantitative path

Upstream F68 reports on the dense augmented-K4 oracle that `C_off` alone gives about `2.230e-08`, while the nine-mode basis (`C_off` plus these eight live modes) gives about `2.205e-08`, roughly 1.1% oracle raw headroom. Upstream F88 explicitly leaves this as the only untested raw item and bounds it at about <=1% after frozen-table transfer.

The cost path is still real even if only a small fraction transfers. Using the conservative E016-class extra-work proxy `58,713,088` FLOPs gives projected utilization `0.3666911796212304`. At that utilization, beating E007 adjusted `8.17e-09` requires raw MSE below `2.2280328663588557e-08`, only `0.0882123%` better than E007 raw.

Therefore E019 can be score-positive without approaching the full oracle ceiling.

## Frozen development split

- public Phase-2 mini only;
- fit indices exactly `0,1,2,3`;
- frozen validation indices exactly `4,5,6,7`;
- scored layers exactly `8..14`;
- fit coefficients once on the dense teacher trajectory from fit dumps;
- freeze all coefficients before validation;
- structural validation against the dense teacher;
- one memoryless end-to-end replay on validation using the same frozen V25 lambda law;
- no official scorer and no holdout.

## GO gates

All must pass:

1. Mean validation K4-core relative-RMS error improves by at least `0.5%` versus frozen `lambda*C_off`.
2. Worst validation layer/dump structural error ratio is `<=1.01` versus baseline.
3. Validation end-to-end final-layer MSE improves by at least `0.20%` versus the identical C-only memoryless replay.
4. No individual validation dump final-layer MSE regresses by more than `1.0%`.
5. Projected adjusted score from the measured raw ratio and measured/proxied extra compute is strictly `<8.17e-09`.
6. Projected total utilization is `<=0.3670`.
7. K4 diagonal is unchanged; all outputs and coefficients are finite and deterministic.
8. Candidate construction uses only the eight frozen modes and one pooled coefficient vector per layer; V25 lambda is unchanged and no per-MLP fit occurs.
9. Production-oriented mode accumulation is streamed through at most one additional `n x n` scratch matrix; no eight-matrix persistent bank.
10. Focused residual proxy median for the added closure work is `<=0.005 s` per MLP-equivalent.

## Kill rule

Any failed gate is `NO-GO / DROP E019`. There is no rescue under E019 by changing the mode set, adding/removing modes, ridge regularization, coefficient clipping, changing fit/validation indices, fitting per MLP, changing lambda, tuning layers, running a sweep, accessing holdout, or running the official scorer.

If the pooled normal equations are non-finite or numerically singular enough that deterministic least squares cannot produce finite coefficients, that is also an immediate NO-GO; do not regularize.

## Primary-source basis

- Hanin, *Random Fully Connected Neural Networks as Perturbatively Solvable Hierarchies*, arXiv:2204.01058. Finite-width cumulants form a layerwise hierarchy in powers of inverse width: https://arxiv.org/abs/2204.01058
- Yaida, *Non-Gaussian processes and neural networks at finite widths*, arXiv:1910.00019. Develops finite-width non-Gaussian corrections propagated through network layers: https://arxiv.org/abs/1910.00019
- Antognini, *Finite size corrections for neural network Gaussian processes*, arXiv:1908.10030. Shows the leading symmetric finite-width correction is fourth-Hermite / fourth-cumulant order: https://arxiv.org/abs/1908.10030
- Upstream primary implementation/evidence: `lean/g_regen_probe.py` and `docs/findings_log.md` at commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.

The literature supports fourth-cumulant finite-width corrections generally; the specific eight-mode residual ansatz is an empirical white-box hypothesis and is gated only by the frozen development measurement above.
