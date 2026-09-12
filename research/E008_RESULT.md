# E008 — Polynomial-sketch old-source K3 contraction result

Status: DONE / DROP

## Hypothesis

Avoid dense old-source leg re-formation in the public K3 factorization by
representing the Hadamard reads (`A*P`, `A*A`, `P*P`) with low-dimensional
TensorSketch polynomial features.

## Frozen diagnostic

- upstream: `504aldo/whest-p2-cumulant-k3` (MIT)
- commit: `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`
- V25 blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- dataset: Phase-2 public `mini`
- MLP index: 0
- layer: 14
- old sources: 10 (7 nested tier-2)
- deterministic sketch sizes: `64, 128, 256, 512`
- run: `34708685523`
- job: `103593335381`
- artifact: `10302243595`

The diagnostic-only patch first verified that the stored factor representation
was being interpreted correctly. Re-forming the dense old legs from their exact
factors produced relative RMS errors only
`4.16e-07` for A and `3.65e-07` for P.

## Result

Aggregate relative RMS reconstruction errors of the degree-2 products:

| sketch m | A*P | A*A | P*P |
|---:|---:|---:|---:|
| 64 | 42.15 | 23.52 | 25.74 |
| 128 | 30.45 | 16.63 | 18.43 |
| 256 | 21.45 | 12.00 | 13.06 |
| 512 | 15.12 | 8.42 | 9.22 |

The preregistered mechanism required D21-scale fidelity near 2%. The necessary
quadratic products are instead wrong by factors of roughly 8–42 even at sketch
sizes that are already too large for the desired cost leverage. Implementing
degree-3 terms or the full D21 contraction cannot rescue this construction.

## Decision

DROP without an official scorer run and without holdout access.

Generic unbiased polynomial collision sketches preserve the wrong notion of
information for this problem. The accuracy-critical old-source remainder is too
structured/small relative to collision noise. Any successful compression needs
to be conditioned on downstream sensitivity or another problem-specific
observable rather than global polynomial-kernel fidelity.
