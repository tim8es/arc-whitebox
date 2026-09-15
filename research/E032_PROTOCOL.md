# E032 — backward-leverage homogeneous cubature

Idempotency key: `ARC-CONTINUE-RESEARCH-E032-20260915`

Status: preregistered single frozen local diagnostic.

## Provenance and firewall

- Branch: `research/e032-backward-leverage-cubature-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Dataset: public Phase-2 mini, index **0 only**.
- E023/E024/E026/E027 are terminal and immutable. E028 remains a reviewed local GO and is not modified. E029 is closed. E030/E031 are disjoint/occupied and are not used.
- No official scorer, holdout, second mini index, fitting, tuning, sweep, or post-result rescue is permitted under E032.

## Motivation

The Phase-2 frontier evidence says a winning representation must simultaneously escape the ~`1.94e-08` raw floor of the K3 + memoryless-K4 chain and the cost of its per-source old-K3 tier. E032 therefore abandons cumulant-source state entirely and represents the Gaussian integral directly by a fixed-size, network-oriented spherical cubature.

Because the MLP is bias-free and ReLU is positively homogeneous,

`f(r u) = r f(u)` for `r >= 0`,

so for `X ~ N(0,I_n)` the radial integral is exact:

`E[f(X)] = E[||X||] * E_{U~sphere}[f(U)]`.

Only the angular integral is approximated.

E029 matched first-layer marginals with signed weights and failed catastrophically at depth. E032 is mechanistically distinct: all cubature weights are equal and positive; the support is a union of full orthonormal bases; orientation is chosen from **backward whole-network linear-response probes**, not from `W0` or layer-1 constraints.

## Frozen representation

Width `n=1024`. The support has exactly **8192 endpoints** = 4096 base points plus their antipodes.

1. Build one normalized Sylvester-Walsh basis `H/sqrt(n)`.
2. Form exactly four orthonormal bases `H D_j / sqrt(n)`, `j=0..3`, where `D_j` are four fixed deterministic Rademacher diagonal masks generated from frozen integer seeds `(0x243F6A88, 0x85A308D3, 0x13198A2E, 0x03707344)` by the same xorshift32 recurrence. No MLP data enters these masks.
3. Construct eight frozen output probes from the first eight Walsh rows.
4. Back-propagate each probe through the **linear-response chain** `g <- 0.5 * W_l^T g` from layer 15 to layer 0. Normalize each nonzero input-space probe.
5. Apply exactly eight Householder reflections `x <- x - 2 g (g^T x)` to every base point. This produces one network-aware orthogonal rotation of the entire support and therefore preserves endpoint norms, antipodal symmetry, and the exact spherical second moment.
6. Append antipodes and propagate all 8192 endpoints through the real MLP with ordinary ReLU. At every layer return `E[||X||] * mean(endpoint activations)`.

No signed fitting, adaptive point count, learned coefficient, rank selection, source tensor, covariance closure, K3/K4 state, rejection, resampling, or output calibration is allowed.

## Static compute path

For `m=8192`, one dense layer propagation is approximately

`m * n * (2n-1) ~= 1.71696e10 FLOPs`.

Across 16 layers this is approximately `2.747e11`, or `~0.1249 B`. Eight backward probe chains and eight Householder applications are each O(`8 L n^2`) / O(`8 m n`) and together add well below `0.002 B`. The preregistered path therefore has headroom below the hard utilization gate `0.14` without relying on the score floor.

The target pair is intentionally much stronger than E028/E007:

- final-layer raw MSE `<= 1.89e-08`;
- utilization `<= 0.14`.

At the joint boundary the adjusted score is `1.89e-08 * 0.14 = 2.646e-09`.

## Tests before scientific data

Focused tests must establish:

1. exactly 4096 base points / 8192 endpoints at n=1024;
2. unit endpoint norms to numerical tolerance;
3. exact antipodal pairing;
4. empirical second moment of the unrotated support equals `I/n` to `<=1e-6` max error on a small synthetic power-of-two width;
5. Householder rotation preserves norms and second moment on a synthetic case;
6. backward probes are deterministic and depend on all supplied layers;
7. exact Gaussian radial mean agrees with an independent chi-mean formula on small widths.

Tests must be GREEN before the scientific harness is armed.

## Single frozen local diagnostic

Run E032 exactly once on public mini index 0 under `flopscope.BudgetContext`, with fixed thread/hash settings. Record:

- final-layer MSE against baked `final_means`;
- billed FLOPs and utilization;
- residual and wall time;
- finite status;
- support size;
- endpoint norm/antipode diagnostics;
- deterministic repeat max-abs difference (one unmetered repeat only).

## Frozen gates

All must pass:

1. final-layer raw MSE `<= 1.89e-08`;
2. utilization `<= 0.14`;
3. implied adjusted proxy `raw_mse * max(0.1, utilization) <= 2.646e-09`;
4. residual `< 0.400 s`;
5. finite output;
6. deterministic repeat max-abs difference `== 0`;
7. exactly 8192 endpoints and 4096 antipodal pairs;
8. no MLP-dependent arithmetic outside flopscope operations in the estimator path.

Any failed or unevaluable gate => **NO-GO / DROP E032**. There is no rescue, alternate mask, alternate point count, alternate number of probes, coefficient change, second index, or rerun under E032. A new idea requires E033+.
