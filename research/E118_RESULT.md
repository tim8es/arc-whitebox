# E118 Result — terminal NO-GO / physical boundary-flux compression

Idempotency key: `ARC-E118-BOUNDARY-FLUX-PHYSICAL-COMPRESSION-20260919`

Decision: **TERMINAL NO-GO / DROP E118**

## Identity

Branch:

`research/e118-boundary-flux-physical-compression-20260919`

Parent:

`research/e114-activation-boundary-flux-20260919@b9f64030f65da9b32fc7718d04fb108ee1a73dab`

E118 does not dispute the verified E114 activation-boundary-flux identity. It tests whether that identity can be turned into an actual output-specific physical compression algorithm under the requested incremental compute and RMS constraints.

No exact final boundary contribution was used for candidate state selection. The exact E114-style full refinement is reference/verifier only.

## Frozen scalar observable

For width `n`:

`s(x)=sum_j h_L,j(x)/sqrt(n)`.

The candidate stores physical angular region states

`(layer, theta_lo, theta_hi, A)`

with

`h_layer(q(theta))=A q(theta)`.

Expansion physically computes the next dense linear map, finds every ReLU zero in the current angular interval, splits the cell, zeroes inactive rows, and materializes every child coefficient matrix.

## Candidate compression law

Unresolved state `I` uses the rigorous target-free envelope

`U(I)=E[R]/(2*pi)*(theta_hi-theta_lo)*||A||_F*prod_remaining ||W_l||_F`.

This follows from ReLU 1-Lipschitzness and `||A||_2<=||A||_F`.

The algorithm always expands the unresolved physical state with largest `U(I)`.

Resolved final cells are integrated analytically. Unresolved cells contribute zero to the point estimate, and

`sum_I U(I)`

is the explicit absolute remainder certificate.

No benchmark target, exact final mean, exact final flux contribution, mask oracle, fitted coefficient, sampler, or control variate enters the queue ordering.

## Protocol-first provenance

- protocol commit:
  `154d3ad5d030257acd9cf65a81bff74ab46b9d36`
- implementation commit:
  `422c7f8c77819ae8ddaeb88f3e6dc2776ea5537f`
- exact tests commit:
  `b26cec959712a4712021ebf674dcba00f1447d83`
- frozen executable commit:
  `2bfcbb247c78650e8896c9bd81bedb61930c91ff`
- sole scientific arm/workflow commit:
  `69b28aff1569c0fac9534a539f4b445691ba83ba`

## Sole frozen run

- run: `35457354702`
- job: `105934894435`
- run attempt: `1`
- workflow head: `69b28aff1569c0fac9534a539f4b445691ba83ba`
- exact tests: `3 passed in 0.09s`
- scientific computation step: success
- artifact upload: success
- terminal workflow conclusion: failure only because frozen scientific exit code was `2`
- rerun: none

Artifact:

- name: `e118-boundary-flux-physical`
- ID: `10588344207`
- size: `3250` bytes
- GitHub ZIP SHA256:
  `3b99993d9021b990f786b5803e9b5300f19dc925ff329b9f63e85434de9b5c42`
- independently downloaded ZIP SHA256: identical
- extracted JSON SHA256:
  `3849098edb1da9273b800b3102d0b17020ff9a8065a8c519426a8e3df244b245`
- log SHA256:
  `9c57487faf521e20f32a39dfb8b650ea56ad440be5056960f5d5b4ec1d07d57c`
- exit file SHA256:
  `53c234e5e8472b6ac51c1ae1cab3fe06fad053beb8ebfd8977b010655bfdd3c3`

## Frozen exact instance

- input dimension: `2`
- width: `8`
- depth: `4`
- weight seed: `118118`
- zero bias
- candidate expansion cap: `62`
- scalar RMS/absolute error limit:
  `1.37477270849e-4`
- numerical quadrature: none
- Monte Carlo truth: none

## Exact E114-style reference

Full physical angular refinement:

- layer state counts:
  `[1, 17, 31, 50, 62]`
- final intervals: `62`
- child states materialized: `160`
- root checks: `792`
- roots materialized: `61`
- coefficient bytes materialized: `20,512`

Exact scalar mean from sector integration:

`1.913371359350446`

Exact boundary-flux mean:

`1.9133713593504451`

Boundary jump sum / angular sector integral:

- jump sum: `9.592221498433958`
- sector integral: `9.592221498433961`
- Gaussian flux-vs-sector discrepancy:
  `8.881784197001252e-16`

Thus the inherited E114 identity is independently preserved on the frozen random depth-4 network.

## Physical compressed candidate

At the frozen production-normalized 62-expansion cap:

- estimate:
  `1.7952053421963705`
- actual absolute scalar error:
  `0.11816601715407549`
- rigorous unresolved remainder:
  `1.7304891902620323`
- actual error is inside the certificate: PASS

Physical state ledger:

- expansions: `62`
- expansions by layer:
  `[1,16,24,21]`
- child states materialized: `116`
- materialized states by layer:
  `[1,17,30,43,26]`
- resolved final states: `26`
- unresolved states at stop: `29`
- max live priority queue: `47`
- root checks: `496`
- roots materialized: `54`
- coefficient bytes materialized: `14,880`
- live coefficient bytes at stop: `3,712`
- deterministic replay: exact

## Error failure

Requested limit:

`1.37477270849e-4`

Measured:

- actual error / limit:
  `859.5312986963839x`
- certificate / limit:
  `12,587.456672475979x`

Both decisive error gates fail by orders of magnitude.

This is not an oracle-selection issue: the candidate uses only state-derived Lipschitz/Frobenius envelopes, and the exact reference is read only after candidate construction for verification.

## All-in production-normalized incremental budget

Hard requested cap:

`136,758,472,261` FLOPs.

Minimum dense coefficient-state propagation for one production region:

`2*1024^3 = 2,147,483,648` FLOPs.

Frozen accounting:

- region transitions: `62`
- transition FLOPs:
  `133,143,986,176`
- helper/materialization/remainder reserve:
  `3,600,000,000`
- all-in frozen incremental ceiling:
  `136,743,986,176`
- margin:
  `14,486,085`

Thus the nominal arithmetic cap itself is respected.

However this already consumes essentially the complete incremental budget before proving that 1024-D polyhedral cone splitting, feasibility, facet storage and queue helpers fit the helper reserve.

The small exact gate fails first, so no production cone implementation is authorized.

## Physical production-state lower bound

One live production state must at minimum store one float32 dense
`1024x1024` coefficient map:

`4,194,304` bytes/state.

The observed small-width max live queue was `47`, corresponding to a production dense-map storage lower bound of

`197,132,288` bytes

before any cone facets, masks, boundary normals, queue metadata or helper buffers.

This memory figure is not the scientific kill; the remainder failure already kills the lane. It records the required physical representation rather than hiding it behind an oracle.

## Gates

PASS:

- exact E114 boundary-flux / sector identity
- candidate physical-state implementation
- explicit remainder certificate
- actual error within certificate
- exact deterministic replay
- finite outputs
- frozen nominal incremental FLOP ceiling <= requested cap

FAIL:

- actual scalar error <= `1.37477270849e-4`
- remainder certificate <= `1.37477270849e-4`
- physical representation closes the requested target before the production-normalized state-transition budget is exhausted

## Interpretation

E114's flux identity is exact, but the deployable compression problem is not solved by best-first physical region refinement with rigorous Lipschitz/Frobenius remainder bounds.

On width 8 / depth 4, a budget normalized to only 62 production dense region transitions leaves 29 unresolved physical states and an error certificate more than four orders of magnitude above the required tolerance.

The gap is too large to justify high-dimensional cone/facet engineering. That work would add cost rather than improve the frozen small-width certificate.

## Verdict

**E118 = TERMINAL NO-GO / DROP.**

Do not rescue by changing the state cap, bound, seed, width/depth, queue priority, observable, helper reserve or tolerance. Do not reopen E114 as an oracle boundary enumeration path.

No production execution, public/public-mini, official scorer, holdout/full, tuning, sweep, rescue, rerun, canonical mutation, ledger mutation or merge occurred.
