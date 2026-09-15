# E023 — exact F68 zero-structure elision

Idempotency key: `ARC-E023-SEARCH-20250915`

Status: **PREREGISTERED / one bounded local diagnostic only**

Base: canonical `29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

Pinned scientific ancestor: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, `estimators/estimator_v25.py` blob `195373a110215256b759d7c172ba8c923c62e5cc`.

Comparator anchor (E007/V25): raw final-layer MSE `2.23e-08`, utilization `0.36666448`, adjusted `8.17e-09` displayed (`2.23e-08 * 0.36666448 = 8.176617904e-09` arithmetically).

No E019/E020/E021/E022 branch is a base or implementation dependency. No official scorer, holdout, tuning, sweep, estimator redesign, rank change, lambda change, source-age change, or canonical mutation is permitted.

## Exact structural observation

V25 F68 stores the residual carrier as

`Rr_full = [3*Bm.T | u_b | y_b]`

with static right factors

`Lr_full = [Q | w1sq | 0]`.

The final transported `y_b` column therefore has an **identically zero right factor for every source**. It is required later only as the separate F68 transported row-vector carrier `Yk = Z_st[:,:,rres+1]`; it is mathematically absent from the generic residual products

`MP = einsum('kiq,kjq->kij', Z_st, L_st)`

and

`PPL = einsum('kij,kjq->kiq', PP, L_st)` followed by contraction with `Z_st`.

Separately, source 0 is born while `mode == 0`. The F68 feed birth branch is inactive there, so V25 explicitly sets

`y_b = u_b = c1_b = dgw = w1sq = 0`.

Thus source-0 F68 `u/y` transport and every downstream F68 feed contraction for source 0 are exact zeros. This is not E021: E021 concerns the distinct V18 feedback stack `Zf_st` / `R1T_st` / `R2T_st`; E023 concerns the F68 feed columns embedded in `Z_st` and the `c1/c2/Yk` feed algebra.

## Frozen candidate

Only these exact-zero eliminations are allowed:

1. In generic residual contractions, use only `Z_st[:,:,:rres+1]` and `L_st[:,:,:rres+1]`; the globally zero-`L` transported `y` column is excluded from `MP` and `PPL`.
2. In `Z_st` transport, keep the first `rres` residual columns unchanged; transport the `u` and `y` columns for sources `1:` only and preserve source 0 as exact zero. Output layout remains bit-compatible with V25.
3. In the F68 feed block, evaluate `R`, the D3 feed, LP feed update, the `(1/3) R Yk^T` D21 term, and related elementwise work on sources `1:` only. Source 0 contributes exact zero and remains represented as zero where layout requires it.
4. No arithmetic for sources `1+`, K3/K4 closure, shared-basis logic, V18 feedback, lambda, final-layer trim, or source birth is otherwise changed.

No approximation is introduced. Candidate and V25 are expected to be numerically identical up to ordinary reassociation-free slicing of terms that are mathematically zero.

## Quantitative path

Target adjusted `<8.17e-09` at unchanged raw requires utilization below

`8.17e-09 / 2.23e-08 = 0.3663677130`,

so the required compute saving versus the E007 anchor is

`(0.36666448 - 0.3663677130) * 2**41 = 6.52597525e8 FLOPs/MLP`.

Conservative static dead-work accounting at width `n=1024`, depth 16:

- remove one globally zero-`L` q-column from `MP` for source counts `k=1..15`: about `2*n^2*sum(k)=2*1024^2*120 = 2.5166e8` FLOPs;
- same q-column from `PPL` on non-final layers `k=1..14`: about `2*n^2*105 = 2.2020e8`;
- source-0 two dead F68 columns from 15 dense transports: about `4*n^2*15 = 6.2915e7`;
- source-0 `R = AP*c1 + PP*c2` on 15 layers: about `4*n^2*15 = 6.2915e7`;
- source-0 D21 feed elementwise path on layers 1..14: at least `5*n^2*14 = 7.3400e7`;
- source-0 `R Yk^T` D21 outer term on layers 1..14: about `2*n^2*14 = 2.9360e7`.

Static projected removal is therefore about `7.00e8 FLOPs/MLP` before small vector-stack savings, implying

- projected utilization `~0.36634616`;
- projected adjusted at unchanged E007 raw `~8.16952e-09`.

The margin is intentionally narrow; measured flopscope billing decides the experiment.

## One frozen local diagnostic

Dataset: public `aicrowd/arc-whestbench-public-2026@v2-phase2`, mini index **0 only**. This is a compute/equivalence diagnostic, not a raw-MSE fitting experiment.

Procedure:

1. Fetch and hash-check the exact pinned V25 blob.
2. Build an in-memory E023 source patch containing only the three zero-elision transformations above.
3. Run exact V25 and E023 once each on mini index 0 under identical deterministic setup and `2**41` estimator budget, with a generous diagnostic BudgetContext ceiling so measurement itself does not truncate.
4. Report full-output max absolute error, relative Frobenius error, final-layer MSE ratio, billed FLOPs, utilization delta, residual wall time, finite flag, and repeat E023 once unmetered for determinism.
5. Focused synthetic tests must prove source-0 preservation and exact equivalence of the sliced algebra before the scientific diagnostic.

## Frozen GO gates

All must pass:

1. Full estimator max absolute output error `<=1e-7` versus pinned V25.
2. Full estimator relative Frobenius error `<=1e-7`.
3. Index-0 final-layer MSE ratio within `[0.999999, 1.000001]`.
4. Measured billed saving `>=6.60e8 FLOPs/MLP`.
5. Projected utilization from E007 anchor `0.36666448 - saving/2**41 <=0.3663677`.
6. Projected adjusted `2.23e-08 * projected_util <8.17e-09`.
7. E023 measured residual wall time must not exceed exact V25 by more than `0.005 s` in the same diagnostic process.
8. Finite and deterministic; repeated E023 output max absolute difference `0`.
9. No new persistent `n x n` state; layouts may be sliced/repacked only for the frozen zero lanes.
10. Pinned upstream blob identity must match exactly.

## Kill rule

Any failed gate => **NO-GO / DROP E023**.

No rescue under E023 by changing the source subset, combining with E021, changing ranks, changing the final-layer algorithm, introducing approximations, using a second mini index, tuning implementation choices to observed billing, or running the official scorer. Any such change requires a new experiment ID.

## Primary-source basis

- Exact V25 source at the pinned commit: the birth code explicitly defines `Lr_full` with the final zero column and sets all F68 feed quantities to zero when the feed branch is inactive; `_dslices` separately reads the transported last `Z_st` column as `Yk` after generic `Z/L` residual contractions.
- Wu et al., arXiv:2605.05179, is the primary cumulant/Hermite estimator paper underlying this family; E023 changes no statistical approximation, only removes algebraic operations multiplying exact structural zeros.
