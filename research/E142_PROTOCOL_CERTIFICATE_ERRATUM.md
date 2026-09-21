# E142 pre-run certificate comparator erratum

Experiment:
`ARC-E142-RESPONSE-ALIGNED-OLD-D21-20260921`.

Status:
**PRE-CODE / PRE-RUN MATHEMATICAL CORRECTION ONLY.**

The frozen protocol commit
`620d3fb0cd72008443d44248a5c5c4489020f4a1`
correctly defines the response statistic and orientation-aware certificate, but
its diagnostic comparator

`B_norm = ||R||_F ||E||_F`

is the sharp full-residual norm bound. A sourcewise triangle certificate can
exceed that quantity because cancellation between sources reduces
`||R||_F`. Therefore the frozen gate
`B_orient <= B_norm` is not a theorem.

Before any E142 implementation or run, replace only that comparator gate by the
computable sourcewise norm-only comparator

`B_source_norm =
  sum_s [
    ||LA_s||_F ||FA_s||_F ||Qc^T E||_F
    + ||LP_s||_F ||FP_s||_F ||Qc^T E||_F
  ]
 + sum_s [
    ||LA2_s||_F ||FA2_s||_F ||U2^T Qc^T E||_F
    + ||LP2_s||_F ||FP2_s||_F ||U2^T Qc^T E||_F
  ]`.

For every source term,

`||F^T v||_F <= ||F||_F ||v||_F`,

so

`B_orient(E) <= B_source_norm(E)`

term by term.

The exact sharp quantity
`||R||_F ||E||_F` may still be materialized **after candidate execution** on
the small verifier as a diagnostic only; it is not a pass/fail comparator.

Updated frozen small gate 8:

> `B_orient <= B_source_norm + 1e-12*scale` on both fixtures.

No other mechanism, seed, dimension, response rank, cost term, certificate
formula, threshold or run rule changes.

No E142 executable code or Actions run existed before this erratum.
