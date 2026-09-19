# E104 Target-Free Transfer Protocol

Idempotency key: `ARC-E104-TARGET-FREE-TRANSFER-20260919`

Status: **PREREGISTERED / ONE-SHOT TARGET-FREE PRODUCTION-SHAPE FALSIFIER**.

## Provenance

- Parent E104 branch head: `4c90b7d7b1f798f5706f368d80f23f8b98fa66b2`.
- Source mechanism: Haar-direction radial Rao–Blackwellization frozen by `research/E104_PROTOCOL.md`.
- Stage-A implementation commit: `12f355b8d905007ceb2abc139440468ffb47ac8f`.
- Stage-A local GO run/job/artifact: `35287541033 / 105423103388 / 10524219347`.
- Independent production-shape verification run/job/artifact: `35446062235 / 105905067035 / 10584569066`.
- This branch changes no estimator law, sample count, rank, precision, QR convention, radius rule, or competition-facing interface.

## Question

Does the frozen E104 Rao–Blackwell mechanism remove a **material final-layer error component at production shape** on a disjoint synthetic network, without reading benchmark/public/scorer/holdout/full targets?

This test does **not** estimate competition raw MSE. It only tests whether the exact radial variance component removed by E104 remains at least one competition-target MSE unit in a production-shaped target-free synthetic instance.

## Frozen production-shaped transfer instance

Exactly one instance:

- width: `1024`;
- depth: `16`;
- total antithetic trajectories: `4096`;
- positive Haar directions: `2048` = two QR blocks of size 1024;
- weights: iid `N(0,2/1024)`, float32, zero bias;
- weight seed: `104204`;
- Haar direction seed: `104205`;
- QR: float64, column signs canonicalized by `sign(diag(R))`, zero -> +1;
- E104 radius: analytic `mu = E[chi_1024]`;
- propagation: float32 matrix multiply + ReLU, float64 layer means;
- budget: `2**41`.

The seeds are disjoint from Stage A and the prior production verification.

## Exact target-free transfer statistic

For positive directions `q_i`, define

`A_i = 0.5 * (H(q_i) + H(-q_i))`.

The frozen E104 production path propagates `±mu q_i`; by positive homogeneity its paired final-layer activation is

`S_i = 0.5 * (H(mu q_i) + H(-mu q_i)) = mu A_i`.

For the E100 random-radius comparator on the same directions,

`M_random - M_RB = (1/m) sum_i (R_i/mu - 1) S_i`,

with `R_i ~ chi_1024` independent. Therefore the exact conditional pooled final-layer MSE removed by E104 is

`V_radial = Var(R/mu) / (m^2 * width) * sum_i ||S_i||_2^2`.

No target/reference prediction is needed.

## One-shot gates

All must pass:

1. finite production-shaped prediction and final trajectory activations;
2. prediction shape exactly `(16,1024)`;
3. exact antithetic input pairing;
4. Haar block orthogonality max abs error `<=1e-10`;
5. homogeneity relative error `<=2e-6`;
6. measured frozen E104 estimator utilization `<=0.12`;
7. exact conditional radial MSE removed is finite and strictly positive;
8. **target-scale materiality:** `V_radial >= 1.89e-8`;
9. no public/scorer/holdout/full/benchmark targets are read.

If any gate fails: **TARGET_FREE_TRANSFER_NO_GO**. No rerun, seed change, extra network, threshold change, rescue, sweep, tuning, or public/full evaluation under this receipt.

If all gates pass: **TARGET_FREE_TRANSFER_PASS** for the E104 mechanism only. This does not establish competition raw MSE `<=1.89e-8`; `scientific_go=false` and competition raw MSE remains unexecuted.

## Evidence policy

- Focused synthetic tests precede the sole production-shaped transfer run.
- The workflow uploads its JSON result even on a scientific gate failure.
- A final immutable receipt records exact implementation SHA, run/job/artifact identity, measured FLOPs/utilization, transfer statistic, gate outcomes, and VERIFIED/UNEXECUTED classification.
- No canonical or ledger mutation.
