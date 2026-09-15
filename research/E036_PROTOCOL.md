# E036 — centered output-Hessian diagonal heat-kernel estimator

Idempotency key: `ARC-E036-IMPLEMENT-20260915`

Status: **PREREGISTERED / AMENDED BEFORE CODE OR DATA**

## Provenance and firewall

- Branch: `research/e036-output-hessian-diagonal-20260915`
- Protocol-only root commit: `83f8c4b3cefe985cc79b6bf61392098ea210911b`
- Direct parent canonical: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- This amendment is protocol-only and occurs before tests, estimator implementation, or public-mini access.
- E031–E035 are not inherited. E023/E024/E026/E027/E029/E032/E033/E035 are terminal and immutable; E028 remains a separate reviewed local GO.
- Public Phase-2 mini index **0 only** is permitted for the single E036 scientific diagnostic.
- No official scorer, holdout/full split, second mini index, tuning, sweep, adaptive search, canonical mutation, or ledger mutation is authorized.

## Hypothesis

The final prediction error may be recoverable from an input-space second-order curvature correction without carrying covariance/K3/K4/source state through the network. For the bias-free network map `f(x)` around the standard-Gaussian input mean `mu=0`, E036 uses the centered heat-kernel approximation

`E[f(X)] ~= f(0) + 0.5 * tr(H_f(0))`,

where the trace is estimated by a frozen complete orthogonal Rademacher frame. The same construction is applied to every network prefix so the estimator returns one mean vector per layer.

This is a centered output-curvature estimator only. It is not a K3/K4/source-stack method and is not a rescue of E031–E035.

## Frozen probe set and correction

Suite shape is fixed to width `n=1024`, depth `L=16`.

1. Finite-difference scale is exactly `h=1.0` in standardized input coordinates.
2. The probe matrix is exactly the order-1024 **Sylvester Hadamard matrix** `H1024`, generated recursively from `H1=[1]` by `H2m=[[Hm,Hm],[Hm,-Hm]]` with no row/column permutation, sign randomization, subsampling, or data dependence.
3. All **1024 rows** are used. Every probe has entries in `{−1,+1}` and the frozen identity is `H1024.T @ H1024 / 1024 = I`.
4. For every probe row `v_r`, evaluate the complete network prefixes at `+v_r` and `−v_r`, and separately evaluate the baseline path at `0`.
5. At each layer/prefix `ell`, form

   `D2_r f_ell = f_ell(v_r) - 2 f_ell(0) + f_ell(-v_r)`

   because `h=1`.
6. The diagonal-Hessian trace proxy is exactly

   `trace_proxy_ell = mean_{r=1..1024} D2_r f_ell`.

   For any quadratic vector-valued function this equals the exact Hessian trace because the full Hadamard frame has exact second moment `I`.
7. The prediction is exactly one centered second-order correction:

   `pred_ell = f_ell(0) + 0.5 * trace_proxy_ell`.

No fitted coefficient, damping, clipping, alternate radial factor, learned calibration, adaptive `h`, probe reselection, K3/K4/covariance/D21/source term, or post-hoc sign choice is permitted.

## Static billed-cost preflight

The implementation may batch the `2*1024+1 = 2049` frozen paths, but batching must not alter the mathematical probe set or correction.

A dense forward envelope counts at most

`2 * L * n^2 * (2n+1)`

multiply/add FLOPs for the layer matrix products, i.e.

`2 * 16 * 1024^2 * 2049 = 68,753,784,832` FLOPs.

Relative to `B=2^41=2,199,023,255,552`, this is

`0.031265... * B`.

Elementwise ReLU, centering, and reductions are small relative to this envelope. The preregistered structural cost gate is therefore estimated utilization `<=0.105`. If the implemented path cannot satisfy that estimate before mini access, E036 is terminal NO-GO without a scientific diagnostic.

## Focused RED/GREEN tests before mini data

Tests are committed before the estimator module exists. RED must fail for the expected missing E036 module and must not access public mini data. After RED is verified, implementation is allowed.

Focused GREEN must establish:

1. exact Sylvester-Hadamard shape `(1024,1024)`, entries `±1`, deterministic generation, and orthogonality `H.T H / 1024 = I`;
2. centered finite differences and the full-frame trace proxy are exact on synthetic scalar/vector quadratic functions to numerical tolerance;
3. constant and affine functions produce zero correction;
4. correction uses exactly `h=1`, exactly all 1024 rows, and exactly coefficient `0.5`;
5. the network-prefix batched implementation matches an explicit small-width reference implementation;
6. repeated synthetic calls are deterministic and finite;
7. static cost envelope is `<=0.105 B`.

## Single frozen public diagnostic

If and only if GREEN and static cost preflight pass, run exactly once on public Phase-2 mini index `0` under `flopscope.BudgetContext`. One identical unmetered repeat is permitted solely for determinism.

Record:

- raw final-layer MSE;
- billed FLOPs and utilization;
- adjusted proxy `raw_mse * max(0.1, utilization)`;
- residual and total wall time;
- maximum absolute correction and maximum absolute output difference versus the baseline deterministic path;
- deterministic repeat maximum absolute difference;
- finite-status and failure count;
- exact `h`, probe-count, Hadamard-orthogonality, and scope checks.

## Frozen quantitative GO gates

Every gate is mandatory:

- raw final-layer MSE `<= 1.89e-08`;
- adjusted proxy `< 2.5e-09`;
- measured utilization `<= 0.105`;
- local failures `= 0`;
- residual wall time `< 0.400 s`;
- all outputs/intermediates finite;
- deterministic repeat maximum absolute difference `== 0`;
- `h == 1.0`;
- probe count exactly `1024`, exact unpermuted Sylvester-Hadamard frame, unchanged coefficient `0.5`;
- no scorer/holdout/tuning/sweep/second-index access.

A GO requires every gate to pass. Passing compute without accuracy, or accuracy without compute, is insufficient.

## Kill rule

Any failed or unevaluable structural preflight or quantitative gate is **NO-GO / DROP E036**.

After terminal NO-GO there is no rescue under E036: no alternate `h`, fewer/more probes, row permutations, random signs, radial scaling, fitted scalar, damping/clipping, K3/K4/covariance add-back, alternate finite-difference stencil, second mini index, rerun, scorer, holdout, or tuning. Any materially different mechanism requires a fresh experiment ID from canonical.

If E036 reaches GO, the only next step is review handoff. Official scorer remains separately controlled.