# E125 append-only lesson — terminal preflight blocker and documented lead

Idempotency key: `ARC-E125-APPEND-ONLY-LESSON-20260920`

Status: **APPEND-ONLY LESSON / E125 REMAINS TERMINAL / NO RERUN / NO REPAIR**.

Branch:
`research/e125-clifford8-rational-tightframe-20260920`.

Terminal receipt:
`research/E125_TERMINAL_PREFLIGHT_RECEIPT.json`.

This file is append-only documentation. It does not modify the frozen E125
protocol, candidate, tests, preflight script, workflow, terminal receipt,
canonical ledger, or any prior result.

## Frozen terminal status

E125 remains:

**TERMINAL_PREFLIGHT_INSTRUMENT_NO_GO**.

No E125 rerun, helper-import repair, scientific stress, seed change, source-code
change, confidence change, or post-terminal rescue is authorized.

No E122 reopening is authorized.

## Exact blocker

The one E125 preflight execution was:

- run: `35503145305`;
- job: `106058362338`;
- workflow commit:
  `a9ca6129c2c602ef8700cd12ba119a2584fdd188`.

The static preflight test stage completed successfully:

`3 passed in 0.13s`.

The next preflight step terminated before numerical stress certificates were
materialized with:

```
ModuleNotFoundError:
No module named 'methods.e114_exact_angular_reference'
```

The failing import was in
`scripts/e125_preflight_certificate.py` and was used only to obtain a
synthetic He-weight helper for the frozen 8-D/16-D stress construction.

The direct cause was ancestry mismatch:

- E125 was intentionally created from `research/bootstrap`;
- that parent does not contain
  `methods.e114_exact_angular_reference`;
- the preflight script nevertheless imported
  `he_weights` from that module.

This failure occurred **before**:

- the 8-D numerical finite-sample certificate;
- the 16-D numerical finite-sample certificate;
- any E125 source-frame generation;
- any E125 network prediction;
- the 8-D exact stress;
- the 16-D exact stress;
- any iid comparator;
- any runtime frame-orthogonality stress.

Therefore the blocker is an instrumentation/ancestry dependency error, not
evidence that the Clifford identities, finite-sample formula, variance
reduction, or 8-D/16-D scientific gates fail.

The frozen protocol nevertheless declared any failed preflight terminal. That
rule controls the experiment, so E125 stays closed rather than being repaired
and rerun.

## What is verified

The following facts are retained as verified documentation only:

1. The protocol-only commit
   `fab8a6e6cb962862e617180ff59e1c72c142b0ec`
   changed only `research/E125_PROTOCOL.md`.
2. The independent E125 candidate commit is
   `e1220128a3967ed6bd951d72a209eb8bbcdca101`.
3. Static exact-integer Clifford tests passed before the blocker.
4. The frozen operation-ledger unit test passed before the blocker.
5. The generic weight-only certificate unit test passed before the blocker.
6. The protocol arithmetic ledger is:
   - all-in upper: `135469896432` FLOPs;
   - hard cap: `136758472261` FLOPs;
   - arithmetic slack: `1288575829` FLOPs.
7. No E122 candidate implementation is imported by the E125 candidate.
8. No canonical ledger was changed.

These verified facts do **not** convert E125 into a scientific GO.

## Clifford-8 rational frame — documented lead only

The retained mathematical lead is the signed-permutation Clifford construction.

For fixed integer operators
(A_0,ldots,A_7in{0,pm1}^{8	imes8}), extended blockwise to dimensions
divisible by eight, the intended exact identity is

[
(A_iq)^T(A_jq)=|q|_2^2delta_{ij}.
]

For unit (q), the eight positive source directions are therefore an exact
orthonormal frame in exact arithmetic without Gram-Schmidt, QR, or Householder
construction.

The antipodal 16-source orbit also has the marginal-invariance argument:
if (q) is uniform on the sphere and (A_i) is fixed orthogonal, then
(pm A_iq) is marginally uniform.

Because the frozen E125 preflight never reached the numerical certificate or
scientific stresses, this construction is preserved only as a **documented
lead**. It must not be cited as:

- a verified 8-D/16-D variance improvement;
- a verified finite-sample ARC certificate;
- a production-ready estimator;
- an E122 repair;
- an E125 result beyond the static facts listed above.

Any future experiment that uses the Clifford frame itself would be an E125
rescue/successor in the same mechanism class and is explicitly **not proposed
here**.

## Non-overlapping successor scan

Existing E126 already studies target-free finite-sample certificates for
multi-source algebraic-frame estimators. Therefore another frame/code/certificate
experiment would overlap E122/E125/E126 and is not admissible as the single
successor proposed by this lesson.

## Single proposed successor: E127 characteristic-function absolute-moment transport

Proposed new mechanism class:

**scalar characteristic-function transport for later-layer ReLU absolute
moments**.

This is not a source-code/frame estimator and does not use Clifford, Haar,
simplex, Gram-Schmidt, or E122/E125 samples.

The exact scalar identity is

[
E[operatorname{ReLU}(U)]
=
rac12 E[U]+rac12 E|U|,
]

and for any integrable real (U),

[
oxed{
E|U|
=
rac{2}{pi}
int_0^infty
rac{1-operatorname{Re}phi_U(t)}{t^2},dt,
qquad
phi_U(t)=E[e^{itU}].
}
]

Therefore a later-layer scalar ReLU mean can be recovered from the
characteristic function of its preactivation without assuming Gaussianity.

A legitimate E127 would have to be protocol-first and pass a pre-code gate:

1. identify an output-specific scalar preactivation/observable whose
   characteristic function can be transported from frozen network structure
   without target fitting;
2. provide a computable finite truncation-tail bound for the integral;
3. provide a deterministic quadrature/interpolation error bound;
4. prove the complete transport + certificate cost can fit the current
   utilization cap;
5. verify the identity on an exact small non-Gaussian fixture where Gaussian
   mean/variance closure gives the wrong ReLU expectation.

If any one of those five items cannot be obtained before production code, E127
must close analytically.

This is the only successor proposed here.

## Scope

- E125 rerun: false;
- E125 repair: false;
- E122 rescue: false;
- E126 duplication: false;
- canonical mutation: false;
- ledger mutation: false;
- public/public-mini/scorer/holdout/full: false;
- target fitting: false.
