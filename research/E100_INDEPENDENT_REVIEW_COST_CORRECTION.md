# E100 independent-review cost correction

Status: **APPEND-ONLY FACTUAL CORRECTION / REVIEW PASS PRESERVED**

Source lane: `research/e100-orthogonal-gaussian-antithetic-20260918`

Source independent-review receipt commit:
`49ed8dc17de34463deea254da7d113f7fc828b97`

This note does not rerun E100, change its sampling law, or grant scientific GO. It corrects one accounting statement in the Stage-A result and first independent review.

## Factual issue

The E100 Stage-A/result accounting used two square QR blocks at

`2 * (4/3) * n^3`

for width `n=1024`.

That is not the bill for `fnp.linalg.qr(A)` when both Q and R are formed under the Phase-2 flopscope accounting model.

For a square `n x n` matrix, flopscope's reduced/complete QR cost model is

`2 * (2*m*n*k - 2*k^3/3)`, with `m=n=k`,

hence the base operation count is

`(8/3) * n^3`

**per QR**.

E100 constructs the Gaussian QR matrix in float64. Under flopscope's dtype pricing, float64 has rate 2 relative to the float32 billing unit. Therefore the billed QR charge is

`(16/3) * n^3`

per block, and with `2048` positive samples at width `1024` there are exactly two blocks:

`C_QR = (32/3) * 1024^3 = 11,453,246,122.666...`

before integer rounding.

The previously recorded QR line was `2,863,311,531`, so that line was low by a factor of approximately 4.

## Other omitted production work

A package-safe successor must also bill, rather than assume free:

- the float64 Gaussian draws used to form the two QR matrices;
- chi-square draws and square roots for the 2048 radii;
- QR sign normalization;
- radial scaling;
- float64 -> float32 casts;
- ReLU operations;
- reductions for **all** `depth x width` output means required by the estimator contract, not final-layer reduction only;
- any copies/selects/materialization that flopscope charges.

The benchmark target is the expectation under standard Gaussian inputs, so the intentional change is only the joint coupling among sampled trajectories. The exact marginal-law theorem remains valid in real arithmetic: sign-normalized Gaussian QR gives Haar Q; each row is uniform on the sphere; an independent chi radius gives a standard Gaussian marginal; antithetic negation preserves that marginal and unbiasedness.

The existing finite-precision caveat also remains: the implementation produces float32 rounding of a float64 polar construction, while the Stage-A iid comparator draws float32 normals directly. This is not a target/reference leak, but a production implementation must use flopscope primitives and preserve the intended marginal law as closely as the runtime permits.

## Corrected conservative envelope

Using the frozen production shape

- width `W=1024`
- depth `D=16`
- total trajectories `N=4096`
- budget `B=2^41`

the old forward term remains

`137,438,953,472` float32 billed FLOPs.

Replacing only the QR line by the correct float64 full-Q/R charge already raises the old total from

`140,319,042,219`

to at least

`148,908,976,811`

billed FLOPs before the additional RNG/all-layer-reduction corrections above.

For successor planning, freeze a conservative review envelope of

`151,000,000,000` billed FLOPs

until a package-safe flopscope implementation measures the exact total.

This envelope corresponds to

`151,000,000,000 / 2^41 = 0.06866684998385608`.

It remains below both:

- the E100 local Stage-A cost gate `0.12`;
- the project production utilization gate `0.135`.

Therefore the accounting error is **material as evidence hygiene but not mechanism-killing**.

## Review disposition

- Marginal-law proof: **PASS**.
- No target/reference leakage: **PASS**.
- Reference/comparator/candidate seed separation: **PASS**.
- QR sign convention: **PASS**.
- Existing low-order marginal structural review: **PASS**.
- Original static production cost number: **CORRECTED / DO NOT REUSE**.
- Corrected cost feasibility: **PASS WITH LARGE SLACK**.
- Competition/public accuracy: **UNEXECUTED**.
- `scientific_go`: **false**.

Because E100 has a same-ID collision with `research/e100-crossfit-two-subspace-shrinkage-20260918`, no new experiment should continue under the E100 ID. Any package-safe competition estimator implementation of the orthogonal-antithetic law must use a newly collision-checked experiment ID and must perform local production-shape flopscope accounting/determinism checks before any public data.
