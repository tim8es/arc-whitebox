# E123 candidate-bearing verifier protocol — E122 @ c733af8

Verifier identity:
`ARC-E123-E122-C733AF8-ADVERSARIAL-12D-20260920`.

This file supersedes only the readiness state of the earlier E123 preflight.
It does not erase or reinterpret preflight run `35473330106`.

## Frozen E122 object

Authoritative object for this verifier run:

- branch:
  `research/e122-haar8-antipodal-simplex-source-code-20260920`;
- protocol commit:
  `fd2f2d93ed7be6124cd70485b561177c3b2787ad`;
- implementation commit:
  `3853efd5177f6931c7dcf884dd97f7342751ca03`;
- tested candidate head:
  `c733af8f3b179c9c9ef8314abc136b2ff6a7940b`;
- protocol blob:
  `fca1c0a0beb88f3bf2573cd4620a886b9dfaa0e7`;
- candidate blob:
  `bf03692f9c205805fbea4113ec9e17e9d1ce2811`;
- tests blob:
  `7b6f1e80def4b76a00526c04c90b20bb008cfa6f`.

No later E122 commit may affect this E123 run.

## Independent adversarial fixture

Use the E123 frozen 12-D, six-source, dense-input-mixed fixture:

- six independent 2-D width-2/depth-4 zero-bias He subnetworks;
- block seeds `123300..123305`;
- dense orthogonal input mixing seed `123390`;
- candidate receives only four 12x12 dense network weight matrices;
- no block decomposition, mixing matrix, source seeds or exact means are
  passed to E122.

Candidate seeds:
`123400,123401,123402,123403`.

Independent same-node iid spherical comparator seeds:
`123500,123501,123502,123503`.

Each estimate uses E122's frozen `P=224` frames and
`224*18=4032` propagated directions.

All candidate and iid estimates must execute before the exact reference is
materialized.

## Gates

### A. Determinism / algebra

1. E122 simplex algebraic gates pass at the protocol tolerances.
2. All candidate outputs finite.
3. Haar-8 orthogonality max abs <= `2e-12`.
4. Source-direction norm max abs <= `2e-12`.
5. For all four seeds, replay prediction is bitwise identical and candidate
   ledger is exactly identical.

### B. Adversarial multi-source error

After candidate/comparator execution, materialize the independent exact 12-D
mean as the concatenation of six independent exact 2-D angular references.

Require pooled candidate MSE / pooled same-node iid MSE <= `0.95`, matching
the stricter high-dimensional E122 16-D admission ratio rather than inventing
a looser gate.

Report raw candidate MSE and ratio to `1.89e-8` diagnostically only.

### C. Target/oracle firewall

Require all of:

- candidate source imports only standard-library/numpy dependencies;
- no E114/E123 reference import;
- no whestbench/dataset/scorer/public/holdout/full dependency;
- no filesystem/network read path in the candidate;
- candidate callable inputs are only weights, frames, seed;
- candidate executes before exact reference materialization.

### D. Error certificate

The user-requested certificate gate is strict.

A PASS requires the frozen E122 protocol and candidate, before this verifier
run, to define a computable finite-sample error certificate, including its norm
and the candidate output/state carrying that certificate.

Unbiasedness in expectation and post-hoc exact-reference MSE are not a
finite-sample error certificate.

If no such predeclared certificate exists, classify
`ERROR_CERTIFICATE_MISSING` and E123 scientific verdict is NO-GO even if the
empirical MSE ratio passes.

### E. Cost

Independently recompute the protocol ledger and compare every frozen term to
`production_cost_receipt()`.

Also audit actual candidate code for operation classes executed but absent from
the ledger.

At freeze, the verifier specifically checks:

- per-frame orthogonality diagnostic `U.T @ U`;
- per-frame source-direction `np.linalg.norm(q, axis=1)` diagnostic.

If these operations are absent from the frozen ledger's operation classes,
`ACCOUNTING_COMPLETE=false`.

For diagnosis, compute a corrected conservative upper adding those omitted
diagnostic operations. A corrected total below the hard cap does not repair the
protocol's explicit rule that an omitted candidate operation class is an
accounting failure.

## Decision

All A-E gates must pass for `E123_VERIFIED_E122_GO`.

Otherwise:
`E123_TERMINAL_NO_GO_FOR_FROZEN_E122_CANDIDATE`.

This verdict applies only to E122 head
`c733af8f3b179c9c9ef8314abc136b2ff6a7940b`.

No E122 rescue, code modification, parameter change, rerun, public/scorer
access, canonical ledger mutation or merge is authorized.
