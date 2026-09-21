# E150 protocol — downstream-observable response-query K3 closure

Idempotency key: `ARC-E150-OBSERVABLE-RESPONSE-QUERY-CLOSURE-20260921`.

Status at freeze:

**PROTOCOL ONLY / MATHEMATICAL CLOSURE FALSIFIER COMPLETE / TERMINAL PRE-CODE NO-GO.**

Branch:

`research/e150-observable-response-query-closure-20260921`.

Parent:

`research/e148-global-seed-tt-k3-20260921@d79eb8e670fbb8ff007283d9ed1eab6dd53a8b35`.

No implementation, workflow, Actions run, public target, scorer, holdout/full
execution, canonical mutation or ledger mutation is authorized under E150.

## 1. Research question

E147 RAP-K3 and E148 GSTT-K3 both preserved their linear transport identities
but lost approximately 90--99% of exact-small D21/D3 signal.

E150 asks a different question:

> Can the estimator avoid any global low-rank K3 carrier and retain only
> adaptive downstream-response queries selected from the weight-only
> sensitivity of the final vector observable, updating only the ReLU K3 birth
> contractions actually needed by those queries?

This is not an E142/E147/E148 rescue.

- E142 retained exact old-source residual actions after the source state already
  existed.
- E147 stored a global projected K3 core.
- E148 stored a global open-core TT seed.
- E150 proposes **no global K3 carrier at all**.

The only K3 state would be response transcripts.

## 2. Pinned algebraic source

Public V25/V29 source:

`504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.

Pinned V25 blob:

`195373a110215256b759d7c172ba8c923c62e5cc`.

Pinned V29 blob:

`17df1a073a24f96c4705b04bcf61ef60fa06dd0c`.

The decisive public nonlinear terms are already explicit in V25
`TERM_SPECS`.

Examples include:

- `('d21T','d21T',...,0.25)`;
- `('d21T','d21',...,0.25)`;
- `('d3row','d21',...)`;
- `('c_off','d21T',...)`.

At runtime the corresponding operands are placed in `ABstack` and multiplied
entrywise before the nonlinear `PK2` contraction.

Therefore the K3/D21 state enters the next-layer closure both **linearly** and
**quadratically through Hadamard products**.

That distinction is the E150 closure test.

## 3. Frozen candidate query class

Call the proposed architecture:

**DORQ-K3 — Downstream Observable Response Queries for K3.**

At layer `l`, let the zero-diagonal D21 matrix be `D_l in R^(n x n)`.

E150 would retain only two response transcripts

`Y_l = D_l V_l in R^(n x k)`

and

`Z_l = D_l^T U_l in R^(n x k)`,

plus mean/covariance/D3 scalar-vector low-order state.

`U_l,V_l in R^(n x k)` are deterministic functions only of network weights,
layer index and the final vector observable.

No exact/reference/target value may enter their construction.

### 3.1 Weight-only final-observable seeds

The final observable is the complete width-`n` output mean vector.

Its raw linear sensitivities to the previous hidden layer are the columns of the
final dense weight matrix.

The compressed frozen E150 class selects `k` of those directions by:

1. sort final-weight columns by descending Euclidean norm;
2. break ties by column index;
3. retain the first `k`;
4. canonical thin QR;
5. propagate the retained response space backward using only weight matrices;
6. canonical QR after every pullback.

No activation target, D21 state or exact reference may alter this query basis.

Production query rank:

`k=64`.

Exact-small homologues:

- width 32: `k=8`;
- width 16: `k=4`.

No rank sweep is allowed.

### 3.2 Allowed adaptivity

Within the frozen response subspace, E150 may adapt scalar coefficients using
previous response values.

It may not add a new direction whose orientation depends on D21/K3 values.

This is the meaning of "chosen from weight-only final-observable sensitivity."

A stronger adaptive-query lower bound is proved below as well: even if later
query directions were allowed to depend on previous returned responses, the
zero-transcript adversary still defeats every class with too few directions.

## 4. Linear response closure would work

For a linear/Wick transport

`K' = K x_1 T x_2 T x_3 T`,

a requested trilinear response

`<K', a (x) b (x) c>`

equals

`<K, T^T a (x) T^T b (x) T^T c>`.

Therefore a response query can be pulled backward exactly through the linear
part.

Likewise, every factorized ReLU K3 birth atom can be contracted directly
against a fixed response tensor without materializing a global K3 tensor.

If the nonlinear closure were affine in D21, DORQ-K3 would be a plausible
closed sufficient-statistic class.

The falsifier is whether the actual closure is affine.

It is not.

## 5. Mathematical falsifier: quadratic D21 terms break query closure

### 5.1 Response transcript map

For fixed query matrices `U,V`, define

`L_(U,V)(D) = (D V, D^T U)`.

This is all D21 information retained by E150.

Suppose two zero-diagonal D21 matrices `D0,D1` satisfy

`L_(U,V)(D0)=L_(U,V)(D1)`.

Then E150 has identical K3 response state for both.

For E150 to be a sufficient statistic, every nonlinear quantity needed for the
future final observable must also agree.

### 5.2 A closure term that does not factor through the transcript

The public nonlinear program explicitly contains the entrywise quadratic term

`D^T (odot) D^T`

through `('d21T','d21T',...)`.

Define

`H(D) = D^T (odot) D^T`.

For `D=0`,

`H(0)=0`.

If a nonzero residual `E` is invisible to the response transcript,

`E V=0`,
`E^T U=0`,

then DORQ-K3 cannot distinguish `D=0` from `D=E`.

But

`H(E)=E^T (odot) E^T`

is nonzero for every nonzero real `E`.

Thus `H` does not factor through `L_(U,V)`.

The same obstruction also applies to the mixed public term
`D^T (odot) D`.

### 5.3 Existence of an invisible zero-diagonal residual

The vector space of zero-diagonal `n x n` matrices has dimension

`n(n-1)`.

The conditions

`E V=0`

and

`E^T U=0`

impose at most

`2nk`

linear constraints.

Therefore

`dim ker L_(U,V) >= n(n-1)-2nk`.

Whenever

`2k < n-1`,

the kernel contains a nonzero zero-diagonal matrix.

For E150's frozen ranks:

### 32-D mathematical fixture

`n=32,k=8`.

Lower bound:

`32*31 - 2*32*8 = 480 > 0`.

A nonzero invisible residual necessarily exists.

### 16-D mathematical fixture

`n=16,k=4`.

Lower bound:

`16*15 - 2*16*4 = 112 > 0`.

Again a nonzero invisible residual necessarily exists.

### Production

`n=1024,k=64`.

Lower bound:

`1024*1023 - 2*1024*64 = 916,480 > 0`.

The invisible residual space remains enormous.

Hence the frozen response query class is not sufficient even before any
numerical approximation issue.

## 6. Stronger adaptive-query adversary

The non-closure proof is not avoided by choosing later query directions from
previous response answers.

Consider any deterministic adaptive algorithm using at most `k` left and
`k` right directions.

Run it against `D=0`.

Every returned response is zero, so this determines the complete sequence of
queries on the zero transcript.

After all queries are fixed, choose a nonzero zero-diagonal

`E in ker L_(U,V)`

for the accumulated query spaces.

The same zero answers are then returned for `D=E`, so the algorithm follows
the identical adaptive transcript.

Yet

`E^T (odot) E^T != 0`.

Therefore **no deterministic adaptive query algorithm with an invisible
residual subspace can exactly propagate the public nonlinear D21 closure**.

The obstruction is information-theoretic, not a poor basis choice.

## 7. Final-observable rank obstruction

There is a second independent obstruction.

The final observable is an `n`-vector.

For a generic dense final weight matrix `W_L`, the `n` output sensitivity
columns have rank `n`.

Therefore the exact weight-only final-observable response span is already
full-dimensional with probability one under continuous He-Gaussian weights.

Selecting `k<n` directions is necessarily an approximation before any ReLU
closure is considered.

The final sensitivity structure therefore gives no exact low-rank observable
subspace to exploit.

## 8. Target-free residual certificate

Although the class is not closed, freeze the certificate that an approximate
query-only successor would have to carry.

Let

`D = Dhat + E`

with target-free bound

`rho >= ||E||_F`.

For a linear response matrix `Q`,

`|<E,Q>| <= rho ||Q||_F`.

For a mixed covariance/D21 Hadamard term,

`||(C (odot) D) - (C (odot) Dhat)||_F
 <= ||C||_infinity rho`.

For the quadratic D21 square,

`D (odot) D - Dhat (odot) Dhat
 = 2 Dhat (odot) E + E (odot) E`,

so

`||D (odot) D - Dhat (odot) Dhat||_F
 <= 2 ||Dhat||_infinity rho + rho^2`.

For the transpose-mixed term,

`D^T (odot) D`,

triangle/submultiplicative bounds give

`<= 2 ||Dhat||_infinity rho + rho^2`

under the same Frobenius residual certificate.

A target-free layer recurrence could therefore use

`rho_(l+1)
 <= B_birth,l
  + A_l rho_l
  + Q_l [2 ||Dhat_l||_infinity rho_l + rho_l^2]
  + B_fp,l`,

where:

- `B_birth,l` is the sourcewise ReLU-birth projection residual computed from
  factor norms;
- `A_l` is the sum of absolute coefficients of D21-linear closure terms;
- `Q_l` is the sum of absolute coefficients of D21-quadratic closure terms;
- `B_fp,l` is a standard floating-point accumulation envelope.

All quantities are candidate weights/state derived.

No benchmark target or exact D21 is needed.

This certificate is explicit and target-free.

It does **not** repair closure: it only bounds what the query state failed to
observe.

The E150 mathematical gate requires exact query closure before an approximate
certificate is allowed to justify implementation.

That gate fails analytically.

## 9. Frozen mathematical falsifier

No Actions run is required.

For each frozen symbolic fixture:

- 32D with `k=8`;
- 16D with `k=4`;

the falsifier consists of the dimension test

`n(n-1)-2nk > 0`

plus the public quadratic closure witness

`H(D)=D^T (odot) D^T`.

Pass criterion for query closure would be:

> every zero-diagonal `E` satisfying all stored response queries must leave
> every required nonlinear closure term unchanged.

Counterexample:

- choose any nonzero `E` in the transcript kernel;
- candidate transcript for `0` and `E` is identical;
- `H(0)=0`;
- `H(E)!=0`.

Therefore the closure criterion fails on both symbolic fixtures.

No numerical seed, rank tuning or exact-reference run can alter this theorem.

## 10. Complete production cost ledger for the frozen compressed class

The purpose of this ledger is to separate mathematical failure from cost.

If DORQ-K3 with `k=64` were closed, its complete estimator-level upper would
be:

Production:

- `n=1024`;
- depth `16`;
- `15` non-final transitions;
- query rank `k=64`.

One unit is `2n^3=2^31` FLOPs.

### A. Retained low-order/public-style allowance

`38 units = 81,604,378,624 FLOPs`.

This is the same conservative non-source allowance used by E147/E148.

### B. Backward weight-only response basis

`15 * 2 n^2 k
 = 2,013,265,920 FLOPs
 = 0.9375 units`.

### C. Direct ReLU-birth response updates

Conservative:

`15 * 8 n^2 k
 = 8,053,063,680 FLOPs
 = 3.75 units`.

### D. D21 left/right response actions

Conservative:

`15 * 8 n^2 k
 = 8,053,063,680 FLOPs
 = 3.75 units`.

### E. Query-space nonlinear closure, if it were closed

Conservative:

`15 * 16 n^2 k
 = 16,106,127,360 FLOPs
 = 7.5 units`.

### F. Residual certificate reserve

`12 units = 25,769,803,776 FLOPs`.

### G. Helper/accounting reserve

`10 units = 21,474,836,480 FLOPs`.

### Total hypothetical compressed class

`163,074,539,520 FLOPs`

`=75.9375 units`

`=0.07415771484375 B`.

Hard cap:

`296,868,139,499 FLOPs = 0.135 B`.

Slack:

`133,793,599,979 FLOPs`.

Thus **cost is not the reason the k=64 class is rejected**.

It is rejected because it is not a sufficient statistic.

## 11. Minimum information dimension required for exact quadratic closure

For the transcript map to be injective on arbitrary zero-diagonal D21 matrices,
a necessary information-count condition is

`2nk >= n(n-1)`.

Therefore

`k >= (n-1)/2`.

At `n=1024`, integer `k` must be at least

`512`.

This is only a necessary lower bound; the final-observable full-rank argument
can require the full `n` directions.

Insert `k=512` into the **same frozen complete ledger**:

- retained low-order allowance: `81,604,378,624`;
- backward queries: `16,106,127,360`;
- birth response updates: `64,424,509,440`;
- D21 response actions: `64,424,509,440`;
- nonlinear query closure: `128,849,018,880`;
- certificate reserve: `25,769,803,776`;
- helper reserve: `21,474,836,480`.

Total necessary-dimension lower-bound architecture:

`402,653,184,000 FLOPs`

`=187.5 units`

`=0.18310546875 B`.

This exceeds the project cap by

`105,785,044,501 FLOPs`.

For the exact full final-sensitivity span `k=n=1024`, the same ledger is

`676,457,349,120 FLOPs
 =315 units
 =0.3076171875 B`.

Therefore:

1. the budget-admissible low-rank response class is not closed;
2. the minimum information dimension that could remove the explicit kernel
   obstruction is already over budget.

## 12. Non-overlap firewall

E150 is not:

- E142: no preserved old-source factor state and no exact old residual action;
- E147: no `q x q x r` global K3 core;
- E148: no `r x n x r` global TT core;
- H140: no SMV rank-4 K3 carrier;
- H137: no CountSketch;
- V21/V24: no source-age shared/nested basis;
- E132/E134: no source-age full-K3 estimator or Hermite correction.

The terminal argument also forbids a disguised rescue:

- allowing D21-dependent query directions changes the frozen
  **weight-only final-observable sensitivity** class;
- storing enough residual structure to evaluate `D (odot) D` exactly becomes
  a global K3/D21 carrier again;
- adding a stochastic sketch of the quadratic term is a new estimator class,
  not E150.

## 13. Decision

The response query class does not close.

Two independent reasons are established before code:

1. **nonlinear closure obstruction**:
   public D21 Hadamard-square/product terms distinguish matrices that have
   identical low-rank response transcripts;

2. **information/cost obstruction**:
   eliminating the invisible zero-diagonal residual kernel requires at least
   `k=512` at production width by dimension counting, whose same complete
   all-in ledger is `0.1831 B >0.135 B`.

The exact final-observable sensitivity span is generically rank `1024`, even
stronger.

Therefore:

**E150 TERMINAL PRE-CODE NO-GO — DOWNSTREAM WEIGHT-ONLY RESPONSE QUERIES ARE
NOT A CLOSED SUFFICIENT STATISTIC FOR THE V25/V29 K3/D21 NONLINEAR CLOSURE.**

No implementation or physical run is scientifically authorized.

A successor would need a genuinely new representation for the **quadratic
D21 observable algebra**, not another low-rank K3 carrier or a larger E150
query rank.
