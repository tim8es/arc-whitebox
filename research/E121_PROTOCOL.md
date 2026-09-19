# E121 protocol — Haar-plane orbit source-memory estimator

Idempotency key: `ARC-E121-HAAR-PLANE-ORBIT-SOURCE-MEMORY-20260919`

Status at freeze: **ONE FROZEN TARGET-FREE FALSIFIER RUN AUTHORIZED**.

Branch:
`research/e121-haar-plane-orbit-source-memory-20260919`.

Parent:
`research/e119-generic-boundary-flux-certificate-20260919@a69e542fa8a53708dd581aac47739fc5d8e36955`.

E120/E121 branch occupancy was checked before branch creation; no E120/E121
research branch existed. This protocol deliberately does not reopen or rescue
E104-E119.

## New mechanism

E121 keeps a **shared low-dimensional source orbit** alive through every late
ReLU layer instead of replacing late-layer dependence by Gaussian moments and
instead of enumerating activation sign cones.

For input dimension `d`, draw a Haar-distributed orthonormal two-frame
`(u,v)`. For the frozen phase grid

`theta_m = 2*pi*m/M, m=0,...,M-1`,

construct

`q_m = u*cos(theta_m) + v*sin(theta_m)`.

Every `q_m` is propagated through the complete realized ReLU network with the
same weights. Thus the entire late-layer state remains a deterministic function
of the common source phase on one plane; no layer is re-Gaussianized and no
cross-layer covariance closure is inserted.

The frame contribution is the phase-orbit mean of final outputs. Average over
`P` independent frames.

For a zero-bias positively homogeneous ReLU network `F` and
`X~N(0,I_d)`, write `X=RQ`, with `R~chi_d` independent of uniform
`Q in S^(d-1)`. E121 uses the exact known radial factor

`mu_d=E[R]`

and estimates

`E[F(X)] = mu_d E[F(Q)]`.

The new mechanism is the **Haar two-plane cyclic orbit stratification**. The
analytic radial factor is an exact homogeneity identity, not a fitted
coefficient or the E121 variance-reduction mechanism.

## Exact unbiasedness identity

A Haar two-frame is invariant under every ambient orthogonal transformation.
For any fixed phase `theta_m`,

`u*cos(theta_m)+v*sin(theta_m)`

is therefore uniform on the unit sphere. Consequently each orbit node has the
correct spherical marginal and

`E_frame[(1/M) sum_m F(q_m)] = E_Q[F(Q)]`.

Hence E121 is unbiased in exact arithmetic for every `P>=1,M>=1`; it does
not require a Gaussian plug-in, target fit, sign-cone enumeration, boundary
enumeration, breakpoint search, or oracle region state.

The phase nodes are intentionally dependent. That dependence is the source
memory being tested: one two-dimensional source orbit is propagated intact
through all late ReLU gates.

## Non-duplication

E121 is not:

- E100/E103 orthogonal full-dimensional direction blocks;
- E104 radial Rao-Blackwellization of otherwise discrete Haar directions;
- E105 two-block risk certification;
- E106 fitted quartic control variate;
- E107 exact fourth-moment cubature;
- E108/E109 transported or Stein control variates;
- E110 Gaussian-line conditional expectation, which enumerated deep line
  breakpoints;
- E111 Gaussian late-layer plug-in;
- E112 cumulant/treewidth/message closure;
- E113 gate-conditioned/folded-ridge closure;
- E114-E119 activation-boundary flux, boundary materialization, fixed-grid flux
  sketch, or omitted-flux certificate.

E121 performs no root solve and has no activation-region object.

## Frozen candidate size

Production-shaped estimator constants are frozen before code:

- input/width `d=n=1024`;
- depth `L=16`;
- independent Haar two-frames `P=128`;
- cyclic phase nodes per frame `M=64`;
- total propagated directions `N=P*M=8192`;
- zero bias;
- float32 network propagation, float64 reduction;
- PCG64 frame generation;
- modified Gram-Schmidt two-frame construction;
- no antithetic add-on: the even cyclic orbit already contains
  `theta+pi`.

No `P/M` sweep or rescue is allowed.

## Frozen exact small-width falsifier

The falsifier is target-free and synthetic.

### Exact 2-D corpus

Reuse E114/E119 exact networks:

- input dimension 2;
- width 8;
- depth 4;
- He-normal float64;
- network seeds `114200,114201,114202,114203`.

For each network, `methods/e114_exact_angular_reference.py` supplies the
exact Gaussian final-output mean. It is verifier-only and is not available to
the E121 candidate.

Candidate frame seeds are
`121200,121201,121202,121203`.

### Exact 8-D source-memory stress

Build one block-diagonal width-8/depth-4 zero-bias network from four independent
2-D width-2/depth-4 E114 subnetworks with seeds
`121300,121301,121302,121303`.

The exact 8-D Gaussian final mean is the concatenation of the four exact 2-D
subnetwork means. The E121 candidate receives only the assembled 8-D weights,
not the block decomposition or exact means.

Run four independent frozen candidate seeds
`121400,121401,121402,121403`.

This fixture is intentionally exact-reference-friendly while still forcing the
candidate to propagate an 8-D shared source plane through four ReLU layers.

### Same-node iid spherical comparator

For falsification only, use `N=8192` independent normalized Gaussian
directions with the same exact radial factor and separate frozen seeds
`121500,121501,121502,121503`.

The comparator does not select or tune E121.

## Frozen scientific gates

All must pass:

1. all candidate outputs finite;
2. every generated two-frame has
   `max(|U^T U-I|)<=2e-12`;
3. deterministic replay is bitwise exact for predictions and exact for the
   accounting ledger;
4. exact 2-D pooled final-output MSE is strictly below the same-node iid
   comparator pooled MSE;
5. exact 8-D block-stress pooled final-output MSE is <=0.90 times the iid
   comparator pooled MSE;
6. no exact reference, target, benchmark label, public/public-mini, scorer,
   holdout or full-suite data is read by the candidate;
7. complete production all-in upper utilization is <=0.13.

The raw competition scale `1.89e-8` is recorded diagnostically but is not used
to tune `P`, `M`, seeds or weights. The falsifier also reports the measured
exact-reference MSE divided by `1.89e-8`.

If any scientific gate fails:

**E121 TERMINAL NO-GO / CLOSE HAAR-PLANE ORBIT SOURCE-MEMORY.**

No second scientific run and no parameter rescue.

If all pass:

**E121 LOCAL SCIENTIFIC GO — HAAR-PLANE ORBIT SOURCE-MEMORY.**

This would authorize only a separately frozen successor production-risk step,
not benchmark/public execution.

## Complete frozen FLOP budget

Production all-in upper bound uses conservative deterministic charges.

For `d=n=1024, L=16, P=128, M=64, N=8192`:

### Two-frame generation

Per frame upper charge:

`32*d + 64`.

This covers two Gaussian vectors, two norms, normalization, one projection,
orthogonalization, scalar square roots/divisions and bookkeeping with a
conservative scalar-equivalent charge.

Total:

`P*(32*d+64) = 4,202,496`.

### Phase/source materialization

Per propagated direction:

`64 + 3*d`

for sin/cos plus two scale operations and one add per coordinate.

Total:

`N*(64+3*d) = 25,690,112`.

### Full deep propagation

Use the physically established E103/E104 layer convention:

`2*n^2 + 2*n = 2,099,200` FLOPs per trajectory per square ReLU layer.

Total:

`N*L*(2*n^2+2*n) = 275,146,342,400`.

### Final reduction/materialization

Conservative:

`N*n + 5*n = 8,393,728`.

### All-in

`275,184,628,736` FLOPs.

Against `B=2^41=2,199,023,255,552`:

`util <= 0.12513948045670986`.

The `0.13B` cap is `285,873,023,221.76`, leaving at least
`10,688,394,485.76` FLOPs of frozen slack.

The executable must independently recompute this formula and record every
small-width candidate ledger component. Any omitted candidate operation class
is an accounting failure and terminal NO-GO.

## Run discipline

Order is immutable:

1. this protocol-only commit;
2. minimal implementation/tests/falsifier;
3. workflow arm;
4. exactly one GitHub Actions scientific run;
5. immutable JSON receipt commit with run/job/artifact/digest and GO/NO-GO.

No tuning, sweep, rescue, rerun, canonical mutation, ledger mutation or merge.
