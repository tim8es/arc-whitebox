# E119 protocol — independent audit of generic E118 boundary implementation

Idempotency key: ARC-E119-INDEPENDENT-BOUNDARY-AUDIT-20260919

Status: PREREGISTERED / REVIEW-ONLY / NO PRODUCTION AUTHORIZATION.

## Reviewed candidate

Branch:
research/e118-boundary-flux-physical-compression-20260919

Reviewed head:
9e1ef4c27fb68e7371ee9d025bf055ab8e33527d

Implementation:
methods/e118_boundary_flux_physical.py
scripts/e118_boundary_flux_physical.py

E119 does not audit the separate E118 output-specific fixed-grid flux sketch because
that mechanism does not explicitly construct activation boundaries.

## Gate 1 — generic mechanism / source purity

PASS requires all:
- candidate API receives actual weight matrices;
- boundary/root construction is computed from supplied weights and state coefficients;
- no fixture-specific kink angle or region coefficient table is embedded in the candidate;
- exact reference is not used to select states or expansion order;
- production candidate does not consume benchmark/public targets.

Starting/ending angles 0 and 2*pi, numerical tolerances, and a fixed expansion cap are
algorithmic constants and are not considered fixture-specific oracle regions.

## Gate 2 — exact-corpus RMS certificate

Frozen owner corpus:
- seed 118118;
- input dimension 2;
- width 8;
- depth 4;
- zero bias;
- expansion cap 62;
- scalar observable normalized sum of final coordinates.

E119 constructs an independent exact angular reference directly from the frozen
weights, without using owner full_exact_reference.

Let mu_ref be independent exact mean and mu_cand the owner compressed candidate.
PASS requires BOTH:
- |mu_cand - mu_ref| <= 1.3747727085e-4;
- owner remainder_certificate <= 1.3747727085e-4.

The second condition is required because production authorization needs a certified
bound, not merely an observed exact-corpus error.

Also verify actual error <= owner certificate + 1e-12.

## Gate 3 — complete FLOP accounting

Competition incremental headroom when layered on the E104 base is frozen as
136758472261 FLOPs.

Owner production formula currently contains:
- 62 dense state transitions at 2*1024^3 FLOPs each;
- a fixed 3.6e9 helper/materialization/remainder reserve.

E119 must source-audit whether ALL production-relevant operations have either
physical flopscope accounting or a rigorous closed-form upper bound, including:
- root solving and root checks;
- sorting/deduplication of roots;
- trigonometric midpoint/direction work;
- mask tests;
- child coefficient materialization/copies;
- heap push/pop and priority calculations;
- Frobenius norms and suffix products;
- unresolved remainder-certificate accumulation;
- sector contribution/integration;
- state bookkeeping/materialization;
- certificate reduction.

PASS requires:
- every listed class is explicitly costed or physically billed;
- helper reserve is supported by a derivation or measurement proving it covers those
  classes at production shape;
- all-in increment <=136758472261 FLOPs.

A hand-written undifferentiated reserve with
high_dimensional_cone_helpers_proven_within_reserve=false is a Gate-3 failure.

## Authorization rule

Production authorization requires Gate 1 + Gate 2 + Gate 3 all PASS.

If Gate 1 passes but Gate 2 or Gate 3 fails:
INDEPENDENT NO-GO / PRODUCTION NOT AUTHORIZED.

No tuning, expansion-cap change, seed change, rescue, rerun, public/scorer/holdout/full,
canonical mutation, or ledger mutation.
