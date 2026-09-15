# E020 — terminal result

Status: **DONE / NO-GO / DROP before scientific validation**

Branch: `research/e020-quadratic-residual-rider-20260915`

Protocol commit: `6b5b07f7fe6a1598f6e391ad01d3fcc0e3d67fcd`.

Implementation commit: `0875c2285b480c04ed740bce3ba8af5c963e238a`.

## TDD evidence

RED:

- workflow run `34914032596`
- job `104207625666`
- expected failure: `ModuleNotFoundError: No module named 'methods.e020_quadratic_rider'`

GREEN:

- workflow run `34914093448`
- job `104207814163`
- `3 passed in 0.11s`

## Frozen-gate failure before measurement

The protocol freezes seven base observables on all 16 layers and requires the 36-column Hermite design to have full rank at **every fitted layer**. It also explicitly defines `D3` and `D21` features as zero where those source slices are unavailable.

On layer 0 the V25 source is in `mode == 0`: there are no prior K3 source stacks, so the correction block sets both `D3f` and `D21n` to identically zero vectors. Therefore two of the seven frozen E020 base features are constants with exactly zero variance.

With only five nonconstant base coordinates, the frozen second-order map can have at most

`1 + 5 + 5 + C(5,2) = 21`

independent columns, strictly below the required `DESIGN_WIDTH = 36`.

Thus the preregistered gate

`rank == 36 at every fitted layer`

is mathematically impossible before reading any fit or validation target. The paired scale gate also fails because the two frozen layer-0 features have standard deviation exactly zero.

This is a protocol-level structural kill, not a data-dependent numerical result. Running the public fit/validation after proving the frozen rank gate impossible would be a cosmetic run prohibited by the kill rule.

## Decision

**NO-GO / DROP E020.**

No frozen scientific validation, official scorer, holdout, tuning or sweep was run. Do not rescue E020 by removing the unavailable features, dropping layer 0, changing the feature map, changing normalization, or changing the rank gate; each is explicitly outside the frozen protocol and would constitute a different hypothesis.
