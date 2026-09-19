# E114 skeptical review protocol — adversarial output-boundary retention

Idempotency key: `ARC-E114-SKEPTICAL-OUTPUT-BOUNDARY-RETENTION-20260919`

Status: **PREREGISTERED / INDEPENDENT SMALL EXACT REVIEW**.

## Scope

This review does not rerun or modify E114. It asks two skeptical questions:

1. Does the 2-D activation-boundary flux identity survive a denser downstream-kink construction?
2. Does restricting to the final scalar observable, or observing low rank of boundary normals, by itself imply a compact boundary representation?

The review is target-free. No public, benchmark, scorer, holdout/full, tuning,
canonical mutation, or ledger mutation is authorized.

## Context from prior dead ends

- E111: late-layer Gaussian first-two-moment plug-in has large exact bias.
- E112: exact activation-mask state propagation is structurally exponential.
- E113: partial structural gate conditioning remains far above the target or is structurally brittle.
- E114: exact boundary-flux identity passed one depth-3 fixture, but production
  boundary compression was explicitly left unresolved.

The skeptical concern is that E114 may move the exact-state explosion from masks
to output-relevant interfaces rather than remove it.

## Frozen constructed network

Input dimension: 2. Zero bias. Maximum width: 4. Depth: 4.

Layer 1:
`
h = [ReLU(x), ReLU(-x), ReLU(y), ReLU(-y)].
`

Define positive asymmetric magnitudes
`
A = 1*h0 + 2*h1,
B = 3*h2 + 5*h3.
`

Layer 2:
`
p = ReLU(A-B),
n = ReLU(B-A),
s = ReLU(A+B).
`

Layer 3 with `c=2/5`:
`
q = ReLU(p+n-c*s),
r = ReLU(-p-n+c*s).
`

Layer 4 scalar output:
`
F = ReLU(q+r).
`

Since `q+r >= 0`,
`
F(x,y) = abs(abs(A-B) - (2/5)*(A+B)).
`

This is continuous, degree-one homogeneous, zero-bias, and piecewise linear.

## Frozen exact boundary prediction

Within each open quadrant, `A=a|x|`, `B=b|y|`, with
`(a,b)` equal to:

- quadrant I: `(1,3)`
- quadrant II: `(2,3)`
- quadrant III: `(2,5)`
- quadrant IV: `(1,5)`

Let `t=|y|/|x|`. Three internal kink families occur in every quadrant:

1. layer-3 outer gate, A-dominant:
   `B/A=(1-c)/(1+c)=3/7`;
2. layer-2 fold:
   `A=B`;
3. layer-3 outer gate, B-dominant:
   `B/A=(1+c)/(1-c)=7/3`.

Together with the four coordinate-axis layer-1 boundaries, this predicts exactly

- 4 layer-1 output kinks,
- 4 layer-2 output kinks,
- 8 layer-3 output kinks,
- 16 total final-output kink angles.

The final layer introduces no additional geometric kink because it receives the
nonnegative value `q+r`.

## Frozen reviewer gates

The sole deterministic executable must:

1. derive the 16 boundary angles analytically from the rational weights;
2. compute the exact linear coefficient vector of the final scalar output in
   every open angular sector by active-set propagation;
3. verify direct network evaluation against that sector coefficient;
4. compute every derivative jump across the 16 final-output kinks;
5. verify all 16 jump magnitudes are nonzero;
6. verify at least 12 of 16 jump values are distinct to `1e-12`;
7. verify the output retains all predicted layer-1/2/3 geometric boundaries
   (retention fraction `16/16=1`);
8. verify the 2-D matrix rank of all interface normals is exactly 2;
9. verify the E114 identity
   `sum derivative jumps = analytic sector integral`
   to `1e-12`;
10. verify deterministic replay is exact.

## Frozen interpretation

- If the flux identity fails, record **E114 exactness falsified**.
- If the identity passes but all 16 output-relevant boundaries survive while
  their normals have rank 2, record:

  **E114 EXACTNESS SURVIVES; NAIVE OUTPUT-THINNING / LOW-RANK-NORMAL
  COMPRESSION CLAIM FALSIFIED ON THE CONSTRUCTED NETWORK.**

This is deliberately scoped. It does not prove that every possible
output-specific compression is impossible. It disproves the inference that a
scalar final observable or low-rank boundary-normal span is sufficient evidence
for a compact exact representation.
