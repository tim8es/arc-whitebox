# E029 — signed layer-1-exact network-aware angular cubature

Idempotency key: `ARC-WIN-RESEARCH-20260915`

Status: preregistered; no implementation or scientific measurement yet.

## Provenance

- Branch: `research/e029-signed-layer1-angular-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83` (`research/bootstrap` head at lane creation)
- Phase-2 public mini: `aicrowd/arc-whestbench-public-2026@v2-phase2`
- Shape: width `n=1024`, depth `L=16`
- Budget: `B=2**41=2,199,023,255,552` FLOPs/MLP
- Target adjusted score: `<2.5e-09`

E023–E027 are closed. E028 is a separate local-GO K3/Wick lane and is not used in E029. E029 is a direct angular-representation estimator, not a cumulant micro-patch.

## Primary-source motivation

For bias-free ReLU MLPs, positive homogeneity gives `M(r u)=r M(u)` for `r>=0`. With Gaussian input `X=R U`, radius and direction are independent, so

`E[M(X)] = E[R] E[M(U)]`.

Phase-1 public research established that fixed nonnegative angular rules are close to saturated at practical support and identified signed/network-adaptive angular rules as the main unresolved escape route (O6/O8). The same record reports that target-aware signed reweighting has multi-fold oracle headroom, while observable-based positive frame selection does not reliably transfer through later nonlinear layers.

E029 tests one fixed, lawful observable: exact first-layer response matching with signed weights over a network-specific angular support.

## Frozen mechanism

Use exactly `m=3n=3072` antipodal direction pairs (`6144` directional endpoints). The positive representatives are the concatenation of exactly three blocks, each row normalized to unit Euclidean norm:

1. coordinate frame `I_n`;
2. the `n` rows of `W_0`;
3. the `n` columns of `W_0`.

No random rotation, alternate frame family, frame count, support sweep, pruning, or adaptive support-count rule is permitted.

Let the pair weight vector be `w in R^m`. Start from uniform `w0=1/m`. For each first-layer neuron `i`, form the exact pair-averaged Gaussian-radial response of direction pair `j`:

`A[i,j] = E[R] * |<W_0[i], u_j>| / 2`.

The exact first-layer target is

`b[i] = ||W_0[i]|| / sqrt(2*pi)`.

Append the normalization row `1^T w = 1`. Compute the unique minimum-Euclidean-norm correction to uniform weights using the frozen dual projection

`w = w0 + C^T (C C^T)^(-1) (d - C w0)`,

where `C=[A; 1^T]` and `d=[b; 1]`.

No ridge, clipping, positivity projection, pseudoinverse cutoff, jitter, fallback, or alternate solve is allowed. A singular/nonfinite solve is an immediate NO-GO.

Propagate all `+u_j` and `-u_j` endpoints through the original MLP exactly. At every layer return

`mu_l = E[R] * sum_j w_j * (h_l(+u_j)+h_l(-u_j))/2`.

The first layer must match the analytic Gaussian mean to numerical tolerance by construction. The signed weights are frozen after the first-layer solve and reused unchanged through layers 1..15.

## Quantitative path to <2.5e-09

The official Phase-2 forward-pass cost is `33,554,432` FLOPs/sample. A naive 6144-endpoint pass would cost

`6144 * 33,554,432 = 206,158,430,208 = 0.09375 B`.

E029 reuses one `m x n` first-layer preactivation matrix for the antipodal pair, so its propagation carrier is slightly below that bound before the signed-weight solve. The dual Gram/solve is O(`n^2 m + n^3`) and is expected to keep measured utilization near the `0.1` score floor.

At multiplier `0.1`, adjusted `<2.5e-09` requires raw final-layer MSE `<2.5e-08`. The frozen local accuracy gate uses `<=2.45e-08` for margin. This is only about 10% above the canonical E007 raw anchor `2.23e-08`, so E029 can win by replacing expensive K3 source machinery with a near-floor signed angular carrier rather than by obtaining a 3x raw-MSE improvement.

## Frozen local diagnostic

Exactly one scientific diagnostic on public mini index `0`.

Record:
- final-layer raw MSE;
- billed FLOPs and utilization;
- adjusted proxy `MSE * max(0.1, FLOPs/B)`;
- residual wall time;
- first-layer max absolute and relative matching error versus analytic target;
- `sum(w)`, `sum(abs(w))`, min/max weight;
- finite status;
- deterministic repeat max absolute output difference.

One identical unmetered repeat is allowed only for determinism. No second MLP/index.

## Frozen GO gates

All must pass:

1. final-layer MSE `<= 2.45e-08`;
2. adjusted proxy `< 2.5e-09`;
3. measured FLOP utilization `<= 0.105`;
4. candidate residual wall time `< 0.400 s`;
5. first-layer max relative analytic-mean mismatch `<= 1e-5`;
6. `abs(sum(w)-1) <= 1e-5`;
7. signed-weight `L1=sum(abs(w)) <= 4.0`;
8. all outputs/weights finite;
9. deterministic repeat max absolute difference `== 0`;
10. support scope exactly three frozen `n`-row blocks and no forbidden stabilization/fallback.

Any failed or unevaluable gate => **NO-GO / DROP E029**. No rescue under E029.

## Execution budget

Protocol-only first commit, then focused RED/GREEN tests, then exactly one frozen local diagnostic. No official scorer, holdout, second mini index, tuning, coefficient/support sweep, rerun, or canonical mutation.