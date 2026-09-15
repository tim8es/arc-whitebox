# E024 — final-layer V18 feedback rank-8 prefix

Idempotency key: `ARC-E024-SEARCH-20250915`

Status: **PREREGISTERED / one frozen local diagnostic**

Branch: `research/e024-final-feedback-r8-20250915`

Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

Pinned estimator source: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, `estimators/estimator_v25.py` blob `195373a110215256b759d7c172ba8c923c62e5cc`.

Comparator anchor: E007/V25 raw final-layer MSE `2.23e-08`, adjusted `8.17e-09`, utilization `0.36666448`, failures `0/100`.

## Independence / non-duplication

E024 does not rescue or modify E023. E023 changed the F68 K4->K3 feed carrier in generic `Z_st` and was killed by its exact-equivalence gate. E024 leaves that carrier untouched.

E024 is also distinct from E021: E021 removes one mathematically-zero source-0 block from the V18 feedback transport. E024 keeps every source and every rank-16 feedback state through layers 0..14 and makes one intentional approximation only at the already mean-only final layer: evaluate the V18 feedback contribution to final D3 using the first 8 of the existing 16 feedback coordinates.

No E012-E023 branch is used as ancestry or implementation source.

## Primary-source evidence

Upstream F69 in `docs/findings_log.md` at the pinned upstream commit reports that the V18 D21 feedback is very low-rank. On the port-faithful lean chain, dense feedback gives about `2.13e-08`, rank 32 `2.14e-08`, rank 16 `2.14e-08`, and rank 8 `2.17e-08` versus `2.36e-08` without feedback. The real V18 rank ladder on dumps 0/1 reports rank 8 `2.184e-08 @0.5013xB`, rank 16 `2.157e-08 @0.5093xB`, rank 32 `2.119e-08 @0.5473xB`; upstream shipped rank 16. Thus rank 8 preserves most of the feedback signal even when used through the whole chain.

V25/V19 already marks the last layer `trim=True`: only final D3 and the K4 diagonal are needed for the mean; D21 output and the two thin right-factor D21 feedback contractions are skipped. In that final layer the remaining V18 feedback work consists of transporting `Zf_st` and forming the dense `Xt` and `Yt` feedback legs used by D3.

## Frozen mechanism

For suite-shape V25 only (`n=1024`, depth 16, normal `R_FB=16`):

1. Layers 0..14 are byte-for-byte/source-identical V25 and retain rank 16 feedback state.
2. At layer 15 only, before the final `Zf_st` transport, take the prefix 8 coordinates of F1 and the prefix 8 coordinates of F2 from the existing rank-16 state.
3. Transport only those 16 total columns (`8 F1 + 8 F2`) through the unchanged `WDb` operation.
4. Pass the correspondingly sliced `R1T_st[..., :8]` and `R2T_st[..., :8]` to `_dslices` with `rfb=8` for final D3 evaluation.
5. No rank-8 basis is recomputed. No source is removed. No earlier layer changes. No changes to K4 regeneration, adaptive lambda, old-tier ranks, source ranks, term tables, or final nonlinear closure.

The prefix is fixed. There is no coordinate selection, singular-value ordering, refit, or alternate rank.

## Quantitative compute path

At the final layer there are `k=15` live sources, width `n=1024`, and baseline feedback rank `r=16`.

Two rank-linear families remain in the final mean-only path:

- feedback transport `Zf_st <- WDb @ Zf_st`, with `2r` columns;
- dense feedback leg formation `Xt=F1 R1^T` and `Yt=F2 R2^T`.

Using the standard dense multiply count, reducing `r=16 -> 8` saves approximately

`8 * k * n^2 * (16-8) = 1,006,632,960 FLOPs/MLP`.

Against the E007 anchor:

- projected utilization at this saving: `0.366206716328125`;
- projected adjusted at unchanged raw `2.23e-08`: `8.166409774117188e-09`;
- raw MSE can regress by only about `0.04396%` before losing the `<8.17e-09` target.

This is a narrow but real compute path. The diagnostic therefore tests whether keeping rank 16 through all earlier propagation makes the final-only rank-8 approximation materially smaller than the full-chain rank-8 penalty reported in F69.

## Frozen local diagnostic

Public dataset only: `aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`, index **0 only**.

Run exact pinned V25 and the frozen E024 candidate under identical deterministic setup and budget. Report:

- baseline and candidate final-layer MSE;
- MSE ratio;
- baseline and candidate billed FLOPs;
- billed saving;
- baseline and candidate residual wall time;
- output max absolute difference and relative Frobenius difference (diagnostic only, not an exact-equivalence gate because E024 is intentionally approximate);
- repeated-candidate determinism;
- projected utilization from the E007 anchor using measured saving;
- projected adjusted score using `2.23e-08 * measured_MSE_ratio * projected_utilization`.

No other mini index may be read. No fit split, validation split, holdout, scorer, or second diagnostic.

## Focused tests

Tests must be written and observed RED before implementation. They must verify:

1. final feedback slicing returns exactly F1 `[:8]` and F2 `[:8]` from a rank-16 concatenated carrier;
2. static right factors are sliced to the same prefix 8;
3. non-final layers retain all 16 coordinates;
4. input arrays are not mutated;
5. repeated slicing is deterministic.

## Frozen GO gates

All must pass:

1. Pinned upstream blob matches `195373a110215256b759d7c172ba8c923c62e5cc`.
2. Focused tests pass after an observed RED failure caused by missing E024 implementation.
3. Candidate is finite and deterministic; repeated candidate max absolute difference is `0`.
4. Measured final MSE ratio `candidate / baseline <= 1.0004`.
5. Measured billed saving `>= 9.0e8 FLOPs/MLP`.
6. Projected utilization `<= 0.3662552`.
7. Projected adjusted score, using measured MSE ratio and measured saving, is strictly `<8.17e-09`.
8. Candidate residual wall time is no more than baseline + `0.005 s` and is `<=0.350 s` on the local diagnostic.
9. Exact scope check: only final-layer V18 feedback rank changes from 16 to 8; all earlier-layer feedback and every non-feedback mechanism remain unchanged.
10. No official scorer, holdout, tuning, sweep, second rank, second mini index, or protocol mutation after measurement starts.

## Kill rule

Any failed gate => **NO-GO / DROP E024**.

No rescue under E024 by using rank 4/6/10/12, selecting non-prefix coordinates, recomputing a rank-8 basis, source-specific ranks, changing earlier layers, combining with E021/E023, accepting a larger raw regression because a different cost estimate looks favorable, or reading another mini index. Any such change requires a new experiment ID.
