# E118 protocol — output-specific angular-cell boundary-flux sketch

Idempotency key: `ARC-E118-OUTPUT-SPECIFIC-FLUX-SKETCH-20260919`

Status at freeze: **ONE TARGET-FREE IMPLEMENTATION / EXACT-REFERENCE RUN AUTHORIZED**.

## Provenance and non-overlap

- Branch: `research/e118-output-specific-flux-sketch-20260919`.
- Direct parent: verified E114 exact-reference head
  `b02f1f7c00528fa494376ebf167be50737ff6460`.
- E114 established the exact activation-boundary flux identity and reusable
  exact angular reference.
- E117 established exact scalar-observable local flux factorization.
- E116 closed exact fixed linear input transport.
- E118 does **not** enumerate the full mask/region set, use a Gaussian plug-in,
  fit any target, use benchmark/public labels, or construct a projector from
  the exact reference.

## Frozen scalar final observable

For width `n`, use the deterministic dense observable

`c_j = (j+1) / sqrt(sum_{r=1}^n r^2)`.

Thus `||c||_2=1`. It is fixed from output coordinate indices only and is
independent of weights, exact reference, or targets.

The scalar network observable is

`F_c(x)=c^T h_L(x)`.

## Output-specific compressed representation

In two input dimensions, write `q(theta)=(cos theta,sin theta)` and define

`s(theta) = [F_c(q(theta)), dF_c(q(theta))/dtheta]^T`.

Between activation boundaries, positive homogeneity and linearity imply the
exact harmonic state transport

`s(theta+h) = R(h) s(theta)`

with

`R(h)=[[cos h, sin h],[-sin h, cos h]]`.

A derivative jump `Delta` at an activation boundary `tau` inside a cell
ending at `b` contributes

`Delta * u(b-tau)`, where `u(r)=[sin r, cos r]^T`,

to the endpoint state defect

`d = s(b)-R(h)s(a)`.

E118 uses a fixed angular grid of exactly

`M = 1024`

cells and stores **one scalar flux atom per cell**, located at the cell
midpoint in the local jump coordinate. For each cell:

`Delta_hat_m = u(h/2)^T d_m`.

The compressed boundary-flux representation is therefore the length-1024
signed vector `Delta_hat`; no activation mask table, region list, boundary
root list, or per-boundary downstream state is stored.

The reconstructed scalar Gaussian mean is

`mu_hat = E[R]/(2*pi) * sum_m Delta_hat_m`,

with `E[R]=sqrt(pi/2)`.

This is directly derived from E114. It is not angular output quadrature:
candidate mean reconstruction uses only the **state defects from the exact
boundary-flux ODE**, not a sum of sampled output values.

## Candidate execution without boundary enumeration

At the 1024 fixed grid angles, the candidate performs:

1. one batched forward pass to obtain `F_c(q_m)`;
2. one scalar-observable reverse pass to obtain each input gradient
   `grad_x F_c(q_m)`;
3. angular derivative
   `F'_c(q_m)=grad_x F_c(q_m) dot (-sin theta_m, cos theta_m)`;
4. fixed harmonic state transport and one scalar midpoint projection per cell.

The forward/reverse execution uses ordinary realized ReLU gates at the sampled
angles only. It never discovers or enumerates the full activation partition.

The angle/tangent stencil and constants
`sin(h/2), cos(h/2), E[R]/(2*pi)` are static representation constants. They
are generated once outside the online flopscope region and are not data- or
weight-dependent.

## Exact E114 reference bias

On the frozen exact 2-D corpus, E114 supplies every true final boundary angle
`tau_k` and vector derivative jump `j_k` only for **reference measurement**.

For scalar jump `Delta_k=c^T j_k`, if its cell ends at `b_k`, the exact
E118 midpoint-sketch flux is

`sum_k Delta_k cos((b_k-tau_k)-h/2)`.

Therefore the exact representation bias is available without numerical
quadrature or Monte Carlo:

`bias_exact = E[R]/(2*pi) *
  [sum_k Delta_k cos((b_k-tau_k)-h/2) - sum_k Delta_k]`.

The exact reference also groups each cell's true 2-vector state defect and
records the orthogonal one-atom remainder

`r_m = d_m - u(h/2) Delta_hat_m`.

This measures the geometry lost by the one-scalar-per-cell compression.

The deployable candidate never receives boundary angles or jumps.

## Frozen corpus

Reuse the verified E114 exact-reference corpus unchanged:

- input dimension: `2`;
- output/hidden width: `8`;
- ReLU depth: `4`;
- zero bias;
- iid He-normal float64 weights;
- seeds: `114200, 114201, 114202, 114203`.

No seed/width/depth/grid sweep is permitted.

## FLOP accounting

Actual candidate arithmetic must run inside `flopscope.BudgetContext`.
Bill:

- all four batched forward dense maps and ReLUs;
- scalar-observable output reduction;
- all four reverse dense maps / gate products;
- angular derivative products and reductions;
- harmonic state prediction, defects, midpoint projections, final reduction.

Static angle/tangent stencil generation is excluded as a fixed compile-time
representation constant and explicitly reported as such.

For production shape only as an admission bound:

- `n=1024`, `L=16`, `M=1024`;
- forward + scalar reverse dense core:
  `4*M*L*n^2 = 68,719,476,736 FLOPs`;
- reserve `5,000,000,000` FLOPs for ReLUs, gate products, observable
  reduction, angular derivatives and sketch helpers;
- all-in upper:
  `73,719,476,736 FLOPs`;
- utilization:
  `0.03352373675443232 <= 0.13`.

This bound is preregistered before execution. Production scientific execution
is not authorized by E118.

## Frozen gates

Integrity:

1. candidate finite on all four networks;
2. candidate output shape is scalar per network and representation length
   exactly 1024;
3. flopscope reconciliation exact;
4. measured candidate FLOPs deterministic across exact replay;
5. exact E114 reference finite and flux identity discrepancy `<=1e-10`;
6. candidate flux sum agrees with the independent boundary-jump formula to
   absolute tolerance `<=1e-10`;
7. candidate deterministic replay max abs `==0`;
8. no benchmark/public/scorer/holdout/full/target access.

Cost:

9. preregistered production utilization upper `<=0.13`.

Scientific accuracy:

10. every frozen network scalar mean squared bias
    `(mu_hat-mu_exact)^2 <= 1.89e-8`;
11. pooled scalar mean squared bias across the four networks `<=1.89e-8`.

If all gates pass:

**E118 OUTPUT-SPECIFIC COMPRESSED FLUX REPRESENTATION GO**.

If either scientific bias gate or cost gate fails:

**TERMINAL NO-GO / CLOSE E118**.

No grid-size change, offset change, observable change, correction factor,
boundary-aware refinement, clipping, target fit, rescue, rerun, or production
scientific run is allowed after execution.
