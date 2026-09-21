# E147 protocol — Response-Aligned Projected K3 estimator

Idempotency key: `ARC-E147-RESPONSE-PROJECTED-K3-ESTIMATOR-20260921`.

Status at freeze:

**PROTOCOL ONLY / PRE-CODE ARCHITECTURE ADMITTED / NO IMPLEMENTATION OR PHYSICAL RUN YET.**

Branch:
`research/e147-response-projected-k3-estimator-20260921`.

Parent:
`research/e145-v25-v29-response-integration-20260921@3e378fa7ff775e357d4098de70600c415e141633`.

## Why E147 exists

E145 closed the simple integration route.

Pinned V29 has a non-old arithmetic floor of about

`0.1496 B > 0.135 B`

even if the entire old tier is deleted for free.

Therefore E147 does **not** patch E142 into V29.

It replaces the estimator-level K3 representation so that:

- no V29 young dense K3 source stack is transported;
- no V22/V24 old shared/nested source stack is transported;
- no exact full D21 matrix is ever required as estimator state;
- downstream K3 information is represented only through target-free
  response-aligned projected actions.

This is a new estimator architecture, not E145 rescue.

## Public/reference provenance used only for algebra and cost comparison

Pinned public repository:

`504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.

Relevant pinned blobs:

- V25:
  `195373a110215256b759d7c172ba8c923c62e5cc`;
- V29:
  `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`;
- V29 namespace audit:
  `a689ef69fd64bed7765cb93ce4910c3fedcbd04a`.

E142 final receipt:

`research/E142_RECEIPT.json`
at
`c8418babd468a8c2c6e214512dfed5ebd3a34ee2`.

No public fitted final errors or benchmark targets are used to construct E147.

## Frozen estimator name

**RAP-K3 — Response-Aligned Projected K3.**

The state is a projected trilinear K3 action core, not a source stack.

For layer `l`, let:

- `U_l in R^(n x q)` have orthonormal columns;
- `V_l in R^(n x r)` have orthonormal columns;
- `K_l` denote the conceptual full symmetric K3 tensor.

E147 stores only

`G_l[a,b,c]
 = <K_l, U_l[:,a] (x) U_l[:,b] (x) V_l[:,c]>`

with shape

`q x q x r`.

The first two indices are symmetrized.

Production ranks are frozen:

- row/action basis `q=96`;
- response basis `r=48`.

Rank schedules for exact-small homologues:

`q(n) = min(n, max(8, ceil(3n/32)))`

`r(n) = min(q(n), max(4, ceil(3n/64)))`.

Therefore:

- 32-D: `q=8, r=4`;
- 16-D: `q=8, r=4`;
- 1024-D: `q=96, r=48`.

No rank sweep is allowed.

## Two-pass architecture

RAP-K3 uses two target-free passes.

### Pass A — K2 scaffold and backward response bases

First compute only the low-order state needed by the public-style closure:

- mean;
- covariance;
- variance;
- ReLU/Wick scalar coefficients;
- memoryless K4 diagonal quantities.

No K3 source stack is constructed.

From those low-order states define the same coordinatewise K3 linear/Wick map
used by factorized K3 propagation:

`T_l = W_l D(w1_l)`

with the exact orientation convention fixed by the implementation/reference
harness.

Final response bases are deterministic Gaussian/Rademacher blocks generated
from experiment seeds only.

Then pull bases backward:

`T_l^T U_{l+1} = U_l R^U_l`

`T_l^T V_{l+1} = V_l R^V_l`

using thin QR with canonicalized signs.

This is the defining response alignment.

For every retained response direction at the next layer, its pullback is
exactly in the previous retained subspace in exact arithmetic.

### Pass B — projected K3 forward propagation

The projected K3 core is transported by the small matrices from Pass A:

`G_pre,l+1
 = G_l x_1 (R^U_l)^T
       x_2 (R^U_l)^T
       x_3 (R^V_l)^T`.

No `n^3` tensor and no V29 K3 source stack is transported.

At each ReLU layer, the new K3 birth implied by the frozen low-order
nonlinear closure is **immediately projected** into

`U_l (x) U_l (x) V_l`

using the factorized/hub algebra before any dense K3 tensor is materialized.

The birth is added directly to `G_l`.

No source is appended for future dense transport.

## D21 sufficient action

For response column `c`, define

`C_c = G_l[:,:,c]`.

The projected D21 action is

`Y_l[i,c]
 = sum_(a,b) U_l[i,a] U_l[i,b] C_c[a,b]`.

Thus

`Y_l ~= D21_l V_l`.

Whenever the low-order nonlinear program requires a full D21-like matrix,
E147 uses the frozen rank-r surrogate

`Dhat_l = Y_l V_l^T`

with its diagonal explicitly zeroed.

The same `Dhat_l` is used consistently in:

- Wick D21 scaling;
- D21-dependent nonlinear closure terms;
- D21 feedback terms;
- regenerated-K4 feed terms that depend on D21.

There is no separate exact/full D21 state.

This removes the V29 operation classes whose purpose is to transport,
reconstruct and contract young/old K3 sources into full D21.

## What E147 retains from the public low-order chain

E147 keeps the algebraic role of:

- full covariance;
- ReLU mean/covariance update;
- D3 vector;
- memoryless K4 diagonal regeneration;
- final-layer mean-only trim;
- scalar/elementwise nonlinear closure.

It does **not** retain the V29 K3 source representation, source-age bases,
old-tier range finders, source transports or full-D21 contraction path.

The public code is a reference for the low-order formula family only, not a
runtime dependency.

## Explicit target-free error certificate

The estimator carries a deterministic certificate for the K3 projection error.

Let the conceptual exact K3 state be

`K_l = Khat_l + E_l`

where `Khat_l` is the RAP-K3 projected tensor represented by `G_l`.

Maintain a scalar upper bound

`rho_l >= ||E_l||_F`.

Because D21 is a repeated-index slice of K3,

`||D21(K_l) - D21(Khat_l)||_F <= rho_l`.

The surrogate additionally right-projects onto `V_l`.

Define the full surrogate error certificate

`B_D21,l
 = rho_l + B_V,l`

where `B_V,l` is a sourcewise/factorwise upper bound on the third-mode
off-response birth content.

For every factorized birth atom
`a (x) b (x) c`, the third-mode off-response term is bounded by

`||a|| ||b|| ||(I - V_l V_l^T)c||`.

For the first two projected modes, the omitted response-relevant birth error is
bounded by the corresponding expansion using

`||(I-UU^T)a||`,
`||(I-UU^T)b||`,
`||U^T a||`,
`||U^T b||`,
`||V^T c||`.

For symmetrized atoms, E147 sums the three permutation bounds before summing
atoms.

All atom factors come from the candidate low-order birth algebra; no target or
exact K3 tensor is required.

### Why linear transport does not create an unobserved retained-subspace leak

Because the bases are defined by exact pullback QR,

`U_{l+1}^T T_l (I-U_l U_l^T) = 0`

and

`V_{l+1}^T T_l (I-V_l V_l^T) = 0`

in exact arithmetic.

Therefore omitted components cannot enter the next retained projected core
through the linear/Wick transport step.

The projected core transport is algebraically closed.

### Nonlinear recurrence

The only propagation of state error into future projected births is through
the nonlinear low-order closure.

For each layer compute a target-free local Frobenius Lipschitz bound

`L_l`

for the projected birth map with respect to D21.

`L_l` is obtained by summing absolute coefficients of every D21-containing
term in the frozen polynomial/nonlinear program multiplied by the current
candidate magnitudes of the other factors.

No fitted target error enters `L_l`.

The certificate recurrence is

`rho_(l+1)
 <= B_birth,l+1
  + L_l B_D21,l
  + B_fp,l`

after the exactly closed projected transport.

`B_birth` is the sourcewise projection bound above.

`B_fp` is a standard floating-point accumulation envelope

`gamma_m * S_l`

with operation count `m`, unit roundoff `2^-52`, and a computable
sourcewise magnitude sum `S_l`.

### Certified relative D21 error

If

`||Dhat_l||_F > B_D21,l`,

then triangle inequality gives

`||D21_l||_F
 >= ||Dhat_l||_F - B_D21,l`.

Hence the target-free computable relative-error certificate is

`eps_cert,l
 = B_D21,l /
   (||Dhat_l||_F - B_D21,l)`.

If the denominator is non-positive, the certificate is infinite and the gate
fails.

This is a deterministic certificate, not a fitted D21-error predictor.

## Protocol-only proof of production cost

Competition budget:

`B = 2^41 = 2,199,023,255,552 FLOPs`.

Project cap:

`floor(0.135 B) = 296,868,139,499 FLOPs`.

Production shape:

- `n=1024`;
- depth `16`;
- 15 non-final K3 update layers plus final mean-only trim;
- `q=96`;
- `r=48`.

One unit below is

`2 n^3 = 2,147,483,648 FLOPs`.

### A. Conservatively retained low-order/public-style work

Pinned V29 grouped families not assigned to young/old K3 source machinery are:

- K3 thin / elementwise: 24.78 units;
- covariance: 7.10 units;
- birth / closure: 5.71 units;
- other / untagged: 0.03 units.

Their displayed sum is 37.62 units.

E147 freezes a larger all-in allowance of

`38.00 units
 = 81,604,378,624 FLOPs`

to cover source-log rounding and retain every one of those operation classes
even where RAP-K3 may later make some thin work unnecessary.

### B. Backward response-basis dense multiplications

For both bases:

`2 n^2 (q+r)`

per non-final transition.

Across 15 transitions:

`C_B = 4,529,848,320 FLOPs`.

### C. Thin QR / sign canonicalization for response bases

Conservative charge:

`8 n (q^2+r^2)`

per transition.

`C_C = 1,415,577,600 FLOPs`.

### D. Projected K3 core transport

Conservative per layer:

`4 r q^3 + 2 r^2 q^2`.

Across 15:

`C_D = 3,185,049,600 FLOPs`.

This bills third-mode mixing and two q-mode core sandwiches.

### E. D21 response extraction and rank-r surrogate construction

Conservative per layer:

`2 n q^2 r + 2 n^2 r`.

Across 15:

`C_E = 15,099,494,400 FLOPs`.

### F. Direct projected nonlinear K3 birth

Conservative upper per layer:

`8 n q^2 r
 + 8 n q r^2
 + 16 n^2 r`.

This covers all factorized birth projections, D3/K4/D21 feed projections,
temporary response actions and reductions.

Across 15:

`C_F = 93,616,865,280 FLOPs`.

No `n^3` birth tensor is allowed.

### G. Error certificate

Conservative upper per layer:

`8 n q^2 r + 8 n^2 r`.

This covers:

- projected/off-subspace factor norms;
- sourcewise atom residual accumulation;
- local closure Lipschitz reductions;
- D21 certificate norms;
- floating-point envelopes.

Across 15:

`C_G = 60,397,977,600 FLOPs`.

### H. General helper / accounting reserve

`10.00 units
 = 21,474,836,480 FLOPs`.

This reserve covers:

- basis initialization;
- finite checks;
- zero-diagonal enforcement;
- deterministic seed generation;
- array clears/copies;
- final reductions;
- metadata-independent helpers;
- any implementation operation class not explicitly named above.

An unlisted class exceeding this reserve is an accounting failure.

### Complete all-in upper

`C_total =
  81,604,378,624
+  4,529,848,320
+  1,415,577,600
+  3,185,049,600
+ 15,099,494,400
+ 93,616,865,280
+ 60,397,977,600
+ 21,474,836,480
= 281,324,027,904 FLOPs`.

Utilization:

`C_total / B
 = 0.1279313564300537`.

Slack to cap:

`296,868,139,499
 - 281,324,027,904
 = 15,544,111,595 FLOPs`.

Equivalent unit total:

`131.001708984375 units`

versus cap

`138.24 units`.

Pre-code cost gate:

**PASS**.

This ledger is estimator-level all-in, not a contraction-interface module
ledger.

## Exact-small falsifier — frozen before code

No public data.

### Fixture A — 32D dense

- input/width: 32;
- depth: 8 ReLU layers;
- zero bias;
- deterministic He-Gaussian weights;
- network seed: `147032`;
- candidate basis: `q=8, r=4`;
- final-basis seed: `147320`.

### Fixture B — 16D adversarial

- input/width: 16;
- depth: 8;
- zero bias;
- deterministic dense rotation + diagonal-gain construction;
- network seed: `147016`;
- candidate basis: `q=8, r=4`;
- final-basis seed: `147160`.

The adversarial fixture must rotate the neuron basis after every layer so a
coordinate-aligned low-rank closure cannot pass accidentally.

## Exact-small reference

Verifier-only reference:

- full dense symmetric K3 tensor;
- the same frozen K2/K3 nonlinear closure algebra;
- exact dense D3/D21 extraction;
- no low-rank/source truncation.

At 32D and 16D this is allowed only in the verifier.

Ordering is mandatory:

1. generate weights;
2. run RAP-K3 candidate;
3. freeze candidate state, predictions, certificates and ledger;
4. only then construct the full-K3 verifier trajectory;
5. score candidate-vs-reference.

The candidate module must not import the exact reference module.

## Frozen exact-small gates

All must pass.

### Integrity

1. finite candidate state and certificate;
2. bitwise deterministic replay;
3. backward basis pullback residual
   `<=1e-12`;
4. projected core linear-transport identity
   `<=1e-11`;
5. target/oracle firewall PASS;
6. no public/public-mini/scorer/holdout/full/submission access.

### K3/D21 scientific gates

7. pooled true D21 relative RMS error
   `<=0.022` on each fixture;
8. no layer true D21 relative RMS error
   `>0.030`;
9. D3 relative RMS error
   `<=0.022`;
10. final candidate mean relative RMS error versus the dense-K3 reference
    `<=0.022`.

These are algebraic-reference gates, not benchmark-target gates.

### Certificate gates

11. every exact layer D21 error is contained by `B_D21,l`;
12. every exact layer relative D21 error is contained by
    `eps_cert,l`;
13. `eps_cert,l <=0.030` at every layer;
14. pooled certified D21 relative error
    `<=0.022`;
15. final exact-small mean error is contained by the recursively accumulated
    target-free mean/closure certificate.

If the certificate is valid but too loose for gates 13/14, E147 is terminal
NO-GO even if realized error is good.

### Cost

16. executable operation-class ledger exactly reconciles to the frozen formula;
17. production upper
    `<=296,868,139,499 FLOPs`.

Any failed or unevaluable gate:

**E147 TERMINAL NO-GO / CLOSE RAP-K3.**

No q/r sweep, seed replacement, basis rescue, alternate certificate, public
target read or second run.

## Physical 1024x16 owner run — only after exact-small GO

This protocol authorizes **zero physical runs at protocol freeze**.

If and only if the exact-small frozen gates all GO, E147 may arm exactly one
physical owner run:

- synthetic 1024x16 zero-bias He-Gaussian network;
- seed `1471024`;
- one BLAS thread;
- no public/benchmark weights;
- no final target/reference mean;
- RAP-K3 estimator only;
- deterministic replay inside the same workflow execution;
- physical flopscope/all-in receipt;
- certificate values at all layers;
- residual wall-time measurement;
- no rank/sample/seed change after run;
- no rerun.

Physical-run GO gates:

- finite;
- deterministic replay;
- complete measured/accounted FLOPs <= project cap;
- no omitted operation class outside reserve;
- every production D21 certificate finite and <=0.030;
- no public target/scorer access.

A physical GO is still only an **owner GO**.

No public target, public-mini, official scorer, holdout, full suite or
submission may be used until a separate independent verifier explicitly gives
GO.

## Non-overlap / closed-lane firewall

E147 is not E145 rescue:

- E145 preserved V25/V29 source arithmetic;
- E147 deletes that source architecture.

E147 is not E142 replay:

- E142 starts from existing old-source contraction factors;
- E147 stores projected K3 action cores as the estimator state.

E147 is not H140:

- no rank-4 full symmetric response matrices;
- no SMV decomposition;
- no SVD recompression.

E147 is not H137:

- no CountSketch or randomized matrix-product patch.

E147 is not E132/E134:

- no source-age Hermite/Edgeworth estimator;
- no full source-age K3 stack.

E147 is not V22/V24 rank retuning:

- the basis is fixed by downstream response pullbacks, not by source-energy
  range finding;
- there is no old-source shared/nested tier.

## Freeze decision

At protocol stage:

- architecture is algebraically defined;
- target-free certificate is explicit;
- exact-small falsifier is fully frozen;
- complete production upper is
  `281,324,027,904 FLOPs = 0.12793 B`;
- cost gate passes;
- implementation is **not yet present**;
- exact-small scientific GO is therefore **UNEXECUTED**;
- physical 1024x16 run is **NOT YET AUTHORIZED**.

No canonical or ledger mutation.
