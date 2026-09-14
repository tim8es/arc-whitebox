# E011 Hopcroft–Kerr Rectangular Leaf-Kernel Feasibility Protocol

Status: preregistered cost-only diagnostic.

## Objective

Determine whether an exact Hopcroft–Kerr rectangular bilinear leaf kernel can reduce the FLOP cost of the V29 old-source tier enough to justify a later integration experiment, without invoking the official scorer or changing estimator accuracy logic.

This experiment is preparation only. It does not score ARC examples and does not modify the canonical ledger.

## Isolation and provenance

- Branch: `research/e011-hk-rectangular-diagnostic`
- Base commit: `6d24bc7d1de7fd1144b7ec3fa187c5c61c1d701e`
- Canonical branch: `research/bootstrap` is read-only for E011.
- V29 old-source ranks motivating the target family: `R_OLD=384/224`.
- Hopcroft–Kerr source: `solven-eu/matmulcatalog` commit `f3a7f0f61b1005666c2cb03f98f2a16727604ea0`.
- Pinned scheme file: `2x16x16-r392-hk71-63c5683.json`.
- Required git blob: `82d1af82132941726bbe67d2e374f77f6e1031a6`.
- Required scheme properties: verified, rank 392, integer `+/-1` coefficients, not commutative-only.

No coefficient search, block-size sweep, rank-chunk sweep, scheme substitution, or other tuning is allowed inside E011.

## Frozen target geometry

The V29 old-tier terminal matrix-multiplication family is frozen as:

- `(128, 48, 128)` meaning `128x48 @ 48x128`;
- `(128, 128, 48)` meaning `128x128 @ 128x48`;
- `(256, 56, 256)` meaning `256x56 @ 56x256`;
- `(256, 256, 56)` meaning `256x256 @ 256x56`.

The single primary feasibility leaf is the smallest forming multiplication:

`128x48 @ 48x128 -> 128x128`.

The prototype must implement this leaf exactly using three `128x16 @ 16x128` contributions. Each contribution is block-lifted with block size 8 and the pinned rank-392 scheme cyclically oriented to `<16,2,16>`. The frozen rank chunk is 64.

The larger terminal shapes are recorded only to define the intended later integration surface. E011 does not benchmark them.

## Comparator

The comparator is exactly one dense `flopscope.numpy.matmul` on the same deterministic float32 inputs:

`fnp.matmul(A, B)` for `A.shape=(128,48)`, `B.shape=(48,128)`.

Both dense and HK paths are measured under `flopscope.BudgetContext` with identical process/runtime conditions after one warm-up of each exact operation signature.

## Deterministic inputs

- NumPy RNG: `np.random.default_rng(20260914)`.
- dtype: `float32`.
- No data-dependent tuning or repeated-seed selection.

## Metrics

Primary metric:

`cost_ratio = measured_HK_FLOPs / measured_dense_FLOPs`.

Supporting metrics:

- measured dense FLOPs;
- measured HK total FLOPs;
- HK rank-product FLOPs;
- measured encode/decode/accumulation FLOPs;
- direct-sparse scheduled non-product FLOPs;
- float32 relative Frobenius error versus dense;
- bitwise determinism across two identical HK executions;
- participant residual-wall-time overhead versus dense;
- projected production rank-buffer memory.

## Frozen arithmetic benefit gate

The dense comparator cost is fixed analytically and must match flopscope:

`128 * 128 * (2*48 - 1) = 1,556,480 FLOPs`.

E011 is a GO only if the exact HK prototype achieves at least a 15% measured FLOP reduction:

`cost_ratio <= 0.85`, equivalently `HK_total_FLOPs <= 1,323,008`.

The pinned rank products alone cost:

`3 * 392 * [8 * 8 * (2*8 - 1)] = 1,128,960 FLOPs`.

Therefore the entire encode + decode + inter-pair accumulation allowance is at most:

`1,323,008 - 1,128,960 = 194,048 FLOPs`.

Any measured total above 1,323,008 or measured non-product overhead above 194,048 is an immediate NO-GO.

## Numeric correctness gate

The exact bilinear construction must satisfy:

`||C_HK - C_dense||_F / ||C_dense||_F <= 2e-6`

on the frozen float32 diagnostic input.

Two identical HK executions must also be bit-identical. Failure of either condition is an immediate NO-GO.

## Residual-time limit

Participant residual-wall-time overhead is measured as:

`HK residual_wall_time_s - dense residual_wall_time_s`.

Gate: `<= 0.002 s` on the primary leaf.

A larger residual overhead is an immediate NO-GO, even if the FLOP gate passes, because this diagnostic is intended to screen out Python/scheduling overhead that would be unsafe to multiply across the old-source tier.

## Memory limit

For the intended production vectorisation projection, use the frozen conservative buffer model:

- `by <= 6`;
- `P = 343`;
- rank chunk `64`;
- block `8x8` float32;
- three simultaneous L/R/M buffers.

Projected bytes:

`6 * 343 * 64 * 8 * 8 * 4 * 3 = 101,154,816 bytes = 96.46875 MiB`.

Gate: `<= 128 MiB`.

Any larger required projection is an immediate NO-GO.

## Decision rule and kill rule

GO requires all five gates simultaneously:

1. relative Frobenius error `<= 2e-6`;
2. bitwise deterministic repeated execution;
3. measured `cost_ratio <= 0.85`;
4. residual overhead `<= 2 ms`;
5. projected rank-buffer memory `<= 128 MiB`.

If any gate fails, E011 stops as NO-GO. No alternative block size, rank chunk, bilinear scheme, coefficient representation, common-subexpression schedule, or matrix shape may be tried under E011. A materially different transform/scheduling strategy requires a new experiment ID.

## Explicit exclusions

E011 must not:

- run `whest` scoring;
- run the 100-MLP mini benchmark;
- open any holdout;
- tune any numerical or structural parameter;
- edit E010, E006, or E003 artifacts;
- edit `research/ledger.csv`;
- merge to `research/bootstrap`.

The only permitted execution is the focused synthetic kernel diagnostic plus its unit/lint checks.