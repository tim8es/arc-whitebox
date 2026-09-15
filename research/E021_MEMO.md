# E021 — exact final-layer old-tier D3 in shared factor coordinates

Status: **NO-GO at quantitative preflight; no implementation diagnostic**

Base: canonical `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

## Fixed comparator

E007/V25: raw `2.23e-08`, adjusted `8.17e-09`, utilization `0.36666448`, failures `0/100`.

At unchanged raw MSE, only about `0.304` V29 units of cost saving are needed to cross the displayed E007 adjusted score, so an exact final-layer cost cut would be useful if it were genuinely cheaper.

## Hypothesis

V19 already specializes the final layer to mean-only evaluation (`need_d21=False`), but old sources are still re-formed as dense A/P legs before computing D3. E021 asks whether the final D3 can instead be contracted **exactly** in the shared V21/V24 factor coordinates, avoiding final-layer dense old-leg re-formation.

For an old source, with `A = Q F_A` and `P = Q F_P`, the dominant final D3 terms include rowwise cubic contractions such as

`sum_j w2_j A_ij^2 P_ij`

and the analogous `M_ij P_ij^2` terms. Eliminating dense A/P formation exactly therefore requires evaluating a cubic polynomial in each row of Q. The corresponding coefficient object has three factor indices:

`T_abc = sum_j w2_j F_A[a,j] F_A[b,j] F_P[c,j]`

(and related tensors for the other terms), followed by

`D3_i = sum_abc Q[i,a] Q[i,b] Q[i,c] T_abc`.

This is the same cubic-core wall identified by the upstream F88 Tucker arithmetic, now applied to the final D3-only contraction.

## Quantitative preflight

Upstream F86 measures the final layer at only about `11.8` total units after V19/V29 trimming. Upstream F88 gives the cost of applying a shared cubic core over the whole old tier as

`n*r^3` FLOPs = `r^3/(2*n^2)` V29 units under the one-unit=`2*n^3` convention, with measured arithmetic:

- r=128: about `2.0` units
- r=224: about `10.7` units
- r=256: about `16` units
- r=384: about `54` units

The current nested old tier needs ranks in the r=224..384 range; r=128 is below the documented accuracy cliff. Therefore even the **smallest fidelity-compatible cubic-core application, r=224, costs about 10.7 units for the whole tier before building/updating the source-specific cubic coefficients and before the thin/feed pieces**.

That nearly equals the entire current final-layer bill (`11.8` units), not merely the old-leg portion that E021 aims to replace. At r=384 it is >4.5x the complete final-layer bill.

Constructing the coefficient tensor is not free: the exact source-specific `T_abc` itself requires contracting the n columns of the factors, also at cubic-rank scale. Avoiding explicit T construction by evaluating the factor products on demand algebraically returns to the current dense `Q @ F` legs and elementwise products.

## Accuracy necessity

The upstream V19 probe `V19_NO_SRC_LAST=1` sets final D3 source machinery to zero and saves roughly 30 pre-V29 units, but final MSE worsens from ~`2.16e-08` to ~`2.15e-07`, about 10x. Therefore simply removing or coarsely truncating final-layer source D3 is not an accuracy-preserving option; the proposed route must retain essentially the existing final D3 information.

## Frozen implementation gate (only if arithmetic passed)

A development implementation would have been allowed only if an exact factor-coordinate contraction had a proved projected cost below the current final old-leg path and projected total utilization below E007 at identical output. No approximation, sampling, TensorSketch, rank reduction, or holdout would be allowed under E021.

## Kill rule and decision

Kill before code if the exact cubic factor-coordinate contraction costs at least the existing final-layer work it is meant to replace.

That condition holds already at the minimum fidelity-compatible rank 224 (`~10.7` units before coefficient construction versus `11.8` units for the *entire* current final layer).

**E021 = NO-GO / DROP at preflight.**

No tests, code, development run, official scorer, holdout, tuning or sweep are justified. A stochastic or low-rank approximation of final D3 would be a different hypothesis, not an E021 rescue.
