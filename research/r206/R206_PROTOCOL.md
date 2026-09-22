# R206 — synthetic-only LITA/TA rank sweep protocol

Parent: `R202@df9cca77f9885644c6058dc4307acc187a2a2dcb`.

## Question

Before any H185 compiler work, measure whether nearby pinned LITA tensor-algorithm
schemes move toward both frozen gates:

- mechanism cost ratio <= **0.42**;
- float32 error ratio vs ordinary float32 matmul <= **1.05**.

This is a kernel-only falsifier. No benchmark targets, holdout, scorer, public
accuracy data, submission, compiler generation, or paid runner is authorized.

## Frozen sweep before execution

Exactly four public immutable schemes from
`khoruzhii/lita@c1dd9225df98676e385b53ae7517ff2ea0ec5779`:

| tensor | rank | Git blob SHA-1 |
|---|---:|---|
| 26x26x26 | 8052 | be5a2f9131ef77c3c3351dc1d218d21ec6845368 |
| 28x28x28 | 9847 | af512cdf847f49d02c97de7d328c8b611ac1a12f |
| 30x30x30 | 11890 | 0cd64a9423d228b0336b07449d65f26931c5bd35 |
| 32x32x32 | 14197 | 6f2dea4820245303dc2eb1fba13816436fabe54d |

The set is fixed before the run. No rank is added, removed, or selected using
observed errors.

## Fixture

For every point:

- deterministic seed 206;
- production-shaped synthetic multiplication 1024x1024 by 1024x1024;
- inputs drawn once as float32 and promoted to float64 for the reference;
- one BLAS thread;
- tensor dimension padding is explicit and billed through the padded block
  geometry;
- copies have zero FLOPs under the project convention but copied scalar counts
  are recorded;
- unsupported dtype/shape fallback is explicit and billed classically.

Exact integrity is checked separately on an integer `d x d` scalar-block
fixture using the rational scheme coefficients.  A common integer coefficient
grid is computed as the LCM of all denominators for that scheme; equality is
checked as an integer residual after multiplying by grid^3.

## Cost ledger

For padded block counts `bm,bk,bn` and rank R:

- leaf multiplications: `2 R bm bk bn`;
- every nonzero U/V/W coefficient multiply is billed;
- every U/V row reduction addition is billed;
- every W output-coordinate reconstruction addition is billed;
- padding/cropping scalar-copy counts are recorded separately;
- fallback FLOPs are recorded separately.

Report both leaf-only and complete arithmetic ratios against the same-shape
classical unpadded `2mnk` denominator.  Since the frozen V29 dense path is
classical-or-faster on its dominant families, failing 0.42 even against this
classical denominator is a conservative mechanism failure.

## Float32 gate

Record relative Frobenius and max-absolute error against the float64 reference.
For each metric report candidate/ordinary-float32 ratio.  Both must be <= 1.05.

## Decision / early stop

All four frozen points are cheap enough for one bounded run and are executed
once.  After the table is complete, stop R206 and do not build a compiler if no
point has both:

1. complete arithmetic ratio <= 0.42; and
2. both float32 error ratios <= 1.05.

Additionally, a leaf-only ratio >0.42 is a structural lower-bound failure even
before coefficient/reconstruction overhead.
