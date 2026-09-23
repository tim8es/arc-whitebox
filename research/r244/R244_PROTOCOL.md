# R244 protocol — marginal-preserving Rres factorization (MP-R16)

Status: **FROZEN BEFORE EXECUTION**

## Provenance and scope

- Job: R244, owner `alternative-method-research`.
- Parent estimator: public V25 from `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.
- Exact parent estimator Git blob: `195373a110215256b759d7c172ba8c923c62e5cc`.
- Comparator: normalized `R209-v25-mini100`, SHA256 `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`.
- Exact development panel: `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`, all 100 rows, metadata SHA256 `264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1`, name-order SHA256 `18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce`.
- Toolchain: NumPy 2.4.6, whestbench 0.16.1, flopscope 0.12.1; budget `2**41`; wall 120 s; residual 0.4 s; one thread.
- Development-only. No private/holdout, submission, leaderboard/rank claim, paid compute, or canonical V25 edit.

R223 V25-LF/local-feed lambda and K4->K3 feed changes are explicitly excluded. The candidate does not change lambda, K4, K3 birth equations, D21 feedback rank, old-tier ranks/ages, correction tables, or term programs.

## Novelty check

The immutable history contains low-rank/range-finder work including E022 oversampling of the *tier-1 old-source shared basis*, E052/E053 old-tier rank/age changes, E094 source-axis compression, and response-aligned D21 work. None records the frozen construction below: an exact two-dimensional all-ones marginal subspace split of the **birth S21 residual `Rres`**, followed by the existing one-power range finder only on the doubly-centered remainder while keeping total `R_RES=16`.

External numerical-linear-algebra motivation:
- Tropp et al., *Practical Sketching Algorithms for Low-Rank Matrix Approximation*, SIAM J. Matrix Anal. Appl. 2017, DOI 10.1137/17M1111590: low-rank sketches can preserve structural properties while retaining fixed rank.
- A fixed-row/column-sum least-squares matrix approximation is a standard constrained approximation problem; see `https://doi.org/10.1016/j.egypro.2012.02.287`.

These sources motivate structure preservation only; they do not provide ARC outcome evidence.

## Frozen method

V25 uses `Rres = S21 - S_sep` and approximates it with a rank-16 one-power range finder `Rres ~= Q B`. R244 keeps total residual-leg rank exactly 16 but reserves two columns for the constant-vector marginals.

Let `u = 1/sqrt(n) * 1`, `a = Rres u`, `b = Rres^T u`, and `c = u^T a`.

Define the exact rank-at-most-2 marginal component

`M = u b^T + (a - c u) u^T`

and centered remainder

`E = Rres - M`.

Then exactly `E u = 0` and `E^T u = 0`, while `M u = Rres u` and `M^T u = Rres^T u`.

Apply the unchanged V25 one-power deterministic range finder to `E` at rank 14 using `w32[:, :14]`, obtaining `E ~= Q B`. Represent `Rres^T` in the existing thin-leg interface as

`Rres^T ~= B^T Q^T + b u^T + u (a-cu)^T`.

The three residual factor blocks are therefore:
- right/transported factors: `[B^T, b, u]` (16 columns total), multiplied by the existing factor 3;
- static left factors: `[Q, u, a-cu]`;
- the two pre-existing V17 feed columns are appended unchanged after these 16 columns.

No fallback, clipping, jitter, adaptive rank, target fitting, coefficient fitting, parameter sweep, or post-result change is allowed.

## Target-free exact-small falsifier

Before public data, run one deterministic standard-library/NumPy falsifier on matrices with `n=12`, total rank 6, bulk rank 4.

Fixture A is constructed exactly as `M + X Y^T` where the bulk factors are projected to both left/right complements of `u`. Gates:
1. `||E u||_inf <= 1e-12` and `||E^T u||_inf <= 1e-12`.
2. Exact-factor reconstruction max abs `<=1e-11` when the centered remainder rank is <=4.
3. Reconstructed row/column marginal errors max abs `<=1e-11`.
4. On a second fixed full-rank Gaussian fixture, constrained rank-6 approximation preserves both marginals to `<=1e-10` and is finite.
5. Candidate source static guard proves exactly one scientific replacement block and `R_RES==16`.

Any failure => desk/small-falsifier `SCIENTIFIC_REJECT`; do not invoke the mini-100 panel.

## Production cost bound

The parent Rres range finder uses rank 16. The candidate applies the same four dense matrix-by-thin products at rank 14 and adds two matrix-vector products plus O(n^2) centering/outer-product work. A conservative incremental allowance is `12*n^2` FLOPs per birth. Across at most 15 births at n=1024 this is `188,743,680` FLOPs = `8.5831e-5 * 2**41` per MLP. The two-rank reduction in the four thin products offsets approximately `251,658,240` FLOPs before elementwise details, so the static bound does not require a material cost increase.

Production gate: measured candidate mean FLOPs must be <= parent mean FLOPs + `0.001 * 2**41`; otherwise NO-GO regardless of MSE.

## Frozen mini-100 GO/NO-GO gates

The sole public candidate panel is allowed only if novelty, static source guard, exact-small falsifier, free-standard-compute gate, pinned toolchain, and `whest validate` all pass.

All of the following are required for scientific GO:
1. exact 100-name/order and target-hash identity with R209 parent;
2. candidate failures = 0;
3. candidate mean raw final MSE < parent mean raw MSE;
4. candidate mean official adjusted score <= `0.995 *` parent;
5. candidate improves official adjusted score on >=55/100 networks;
6. paired mean(parent score - candidate score) > 2 * descriptive SE across 100 networks;
7. measured mean FLOPs <= parent + `0.001 * 2**41`;
8. max residual wall time <0.4 s;
9. source/config/toolchain/panel provenance exact;
10. exactly one public mini-100 candidate panel invocation.

Expected measurable effect: preserving the two constant-vector marginals of every compressed Rres removes a systematic projection error without increasing residual-leg rank; the preregistered success threshold is at least 0.5% lower mean adjusted score.

Any failed scientific gate => same-panel **DEVELOPMENT NO-GO**. No gate relaxation, rescue, rerun, second workflow, or second panel.

## Execution budget

At most one GitHub Actions workflow/run on verified public standard `ubuntu-24.04` compute. It must perform, in order: free-compute/toolchain/source guards; exact-small falsifier; validation; exactly one candidate mini-100 panel; paired comparison; artifact hashing/upload. If infrastructure fails before the panel, finish R244 `INFRA_ERROR`; no retry.
