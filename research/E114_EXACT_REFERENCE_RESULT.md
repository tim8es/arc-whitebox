# E114 exact-reference result — final-observable output-compression support

Tracking key: `ARC-E114-EXACT-REFERENCE-OUTPUT-COMPRESSION-20260919`

Decision: **E114 EXACT REFERENCE HARNESS VERIFIED**

This work extends E114's exact activation-boundary-flux reference only. It does
not introduce or select a new deployable compression mechanism.

## Reusable instrument

Added:

- `methods/e114_exact_angular_reference.py`
- `scripts/e114_exact_reference_output_compression.py`
- `tests/test_e114_exact_angular_reference.py`

The reusable API enumerates the complete exact 2-D angular ReLU partition for
arbitrary zero-bias layer widths, then returns:

- exact Gaussian final mean;
- exact final second moment and covariance;
- exact final boundary angles and derivative-jump vectors;
- E114 flux sum and flux Gram matrix;
- exact bias/covariance/cross-covariance/remainder for any externally supplied
  orthonormal output-space basis;
- exact per-coordinate final-observable bias, residual variance and residual
  MSE.

The original scalar E114 depth-3 fixture is reproduced by the focused tests.

## Frozen corpus

Reference-only corpus:

- input dimension: `2`
- width/depth: `8 / 4`
- He-normal float64 zero-bias weights
- seeds: `114200, 114201, 114202, 114203`
- no Monte Carlo
- no numerical quadrature
- no benchmark/public targets

Final exact sector/boundary counts:

`[55, 61, 83, 55]`.

Exact final covariance off-diagonal RMS per network:

`[0.06030617653659119,
  0.08803619051900402,
  0.12364935826531466,
  0.015045803805632836]`.

These are true final-output dependence measurements, not a Gaussian plug-in.

## Instrument exactness

- focused tests: `3 passed in 0.14s`
- maximum E114 flux-mean vs independent sector-mean discrepancy:
  `3.3306690738754696e-16`
- covariance symmetry max abs: `0.0`
- minimum covariance eigenvalue over the corpus:
  `-1.3161352367288633e-32` (floating zero)
- identity-projector max remainder: `0.0`
- zero-projector second-moment reconstruction max abs:
  `1.1102230246251565e-16`
- maximum oracle projector symmetry error: `0.0`
- maximum oracle projector idempotence error:
  `1.5543122344752192e-15`
- deterministic replay max abs: `0.0`

All frozen instrument gates passed.

## Exact oracle capacity diagnostics

The ranks below use the top eigenvectors of the **exact flux Gram** only as an
oracle reference. They are not available to a deployable estimator and do not
define a candidate mechanism.

### Rank 1

- pooled relative flux-energy remainder:
  `0.5094115836158905`
- pooled relative final-output mean-square remainder:
  `0.69770168709665`
- worst network mean-bias MSE across outputs:
  `0.10092233962702041`
- worst absolute output mean bias:
  `0.6548876313528357`
- worst scalar-observable residual MSE:
  `1.2005837379354947`

### Rank 2

- pooled relative flux-energy remainder:
  `0.3175830428196701`
- pooled relative final-output mean-square remainder:
  `0.4447022467179565`
- worst network mean-bias MSE across outputs:
  `0.08313781262800225`
- worst absolute output mean bias:
  `0.6707864361193144`
- worst scalar-observable residual MSE:
  `1.2050250550173685`

### Rank 4

- pooled relative flux-energy remainder:
  `0.09830102553624856`
- pooled relative final-output mean-square remainder:
  `0.04581897107107757`
- worst network mean-bias MSE across outputs:
  `0.02192175245419047`
- worst absolute output mean bias:
  `0.36761843571682806`
- worst scalar-observable residual MSE:
  `0.21864797187719126`

The reference therefore exposes a concrete distinction needed by E114
compression work: low residual **flux energy** does not automatically imply
small bias or small per-observable remainder. The exact harness reports all
three separately.

## Execution provenance

Attempt 1 never reached the exact reference: the workflow lacked `pytest` and
failed with exit 127 before the scientific step. That blocker is sealed in
`research/E114_EXACT_REFERENCE_ATTEMPT1_BLOCKER_RECEIPT.json`.

The engineering-successor run verified byte-identical frozen scientific blobs
before execution and changed only test-runner availability.

Successful frozen run:

- arm head: `ce6dfdb09616500a3129d009cb4cc4fc3999430d`
- run/job: `35456370595 / 105932253496`
- run attempt: `1`
- workflow conclusion: `success`
- artifact: `e114-exact-reference-output-compression-v2`
- artifact ID: `10587574359`
- artifact ZIP SHA256:
  `1d9ce1add971b924732276e565c9c19abcf24a8635b5139f692edd0471a7fad3`

No public/public-mini, benchmark target, scorer, holdout/full, production run,
tuning, rank/seed sweep, canonical mutation or ledger mutation occurred.

## Scope conclusion

**The E114 exact-reference instrument is verified and reusable.**

This is reference infrastructure, not a compression GO. Any E114/E115
candidate must supply its projector/observable externally and be measured
against these exact bias, covariance and remainder quantities without using the
oracle basis to construct the candidate.
