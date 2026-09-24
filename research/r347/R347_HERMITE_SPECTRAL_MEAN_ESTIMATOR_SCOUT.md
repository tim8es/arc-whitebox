# R347 — Hermite / polynomial-chaos spectral mean-estimator scout

**Status:** COMPLETE  
**Verdict:** **ALREADY_COVERED**  
**Measurement classification:** **NO_NEW_ESTIMATOR_MEASUREMENT**  
**Branch:** `review/r347-hermite-spectral-mean-estimator-scout-20260924`  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`

## Stop-rule result

R347 stops at deduplication. The requested Hermite / polynomial-chaos spectral-propagation lane is already occupied by E115, which is an exact mechanism match at the family level:

- branch: `research/e115-hermite-chaos-certified-tail-20260919`
- current head: `85552f57c263be172fdceae25fffe278be065680`
- protocol: `research/E115_PROTOCOL.md`
- protocol blob SHA-1: `a63ac3cdedc6bf8a4948c22b8b907a1333f84f70`
- result receipt: `research/E115_RESULT_RECEIPT.json`
- result receipt blob SHA-1: `1f4c10bba845238bd07055c2f423a92c0cdb612a`
- mechanism recorded by E115: **dense total-degree Wiener/Hermite chaos transport with exact Parseval L2 remainder**
- terminal verdict: `TERMINAL_NO_GO_DENSE_TOTAL_DEGREE_HERMITE_CHAOS`

Because the user explicitly required **ALREADY_COVERED and stop** when this exact/equivalent spectral-truncation family is occupied, R347 performs no new literature derivation, analytic feasibility gate, implementation, or synthetic run.

## Exact mechanism overlap

E115 preregistered the same core representation R347 asks to investigate. For standard Gaussian latent (X\in\mathbb R^d), E115 represents each scalar activation by the multivariate probabilists' Hermite expansion

[
f(X)=\sum_{|\alpha|\ge0} c_\alpha He_\alpha(X).
]

Its degree-(p) projection (P_p f) carries the exact Parseval truncation certificate

[
\mathbb E[(f-P_p f)^2]
=
\sum_{|\alpha|>p}\alpha!\,c_\alpha^2.
]

The dense total-degree basis size is

[
B(d,p)=\binom{d+p}{p}.
]

That is precisely Hermite / polynomial-chaos spectral propagation with a rigorous truncation remainder under Gaussian latent input; changing the task label from “Hermite chaos” to “polynomial-chaos spectral propagation” does not create a new estimator family.

E115 also froze a production-shaped dense linear-transport lower bound for width (w=1024), latent dimension (d=1024), for only two late dense layers:

[
F_{\min}(p)=4w^2B(d,p),
]

before nonlinear reprojection, normalization, bookkeeping, or inherited estimator cost.

Its exact target-free falsifier found:

- degree 1 Parseval remainder MSE: `0.09084505690810465`;
- degree 2 Parseval remainder MSE: `0.011267585362156995`;
- degree-1 basis count: `1025`;
- degree-2 basis count: `525825`;
- degree-2 two-layer dense transport lower bound: `2205469900800` FLOPs;
- Phase-2 budget: `2199023255552 = 2^41` FLOPs;
- therefore degree 2 already exceeds the full (2^{41}) budget for only two late dense linear transports, before nonlinear projection/base-estimator cost.

E115's receipt classifies the lane terminal NO-GO for **dense total-degree Hermite chaos**.

## Current registry and broader dedupe

The current R320 traceability registry was checked:

- branch: `review/r320-sidecar-research-traceability-20260924`
- current head: `949361e498dd4339e75ddc2baf199782f7a9a5e5`
- report blob: `41b14238c0062081e1b3970e2961cb7c18ef88f9`
- receipt blob: `280516be04a2606a431f084e8cef9e678d290184`

R320 is a sidecar traceability registry rather than the historical E-series mechanism ledger; it does not supersede E115. Its current snapshot also preserves the corrected R335/R338 theory lineage and measurement separation.

The earlier accuracy/theory dedupe reports independently record the family as occupied:

- **R265**, branch `research/r265-method-theory-scout-20260923`, head `bc287eed95df49fb41d81d157b15471a5aa73a3d`, report blob `e9b5df06173bf70a587774f9374042962847d9e2`: explicitly lists `polynomial/TensorSketch, Hermite/chaos` among already represented mechanism families.
- **R276**, branch `research/r276-v25-accuracy-screen-20260923`, head `a646038b5aceb5428d6583b07525f394f4820c0d`, report blob `4970614c1ac789b008260d726a2bbd5272116434`: again lists `polynomial/TensorSketch, Hermite/chaos` as already represented.
- **R308**, branch `review/r308-theory-scout-20260924`, head `9c3ef5eefe014e7bdb1a11cc8941999048f6654b`, report blob `e07ddccdf3744c741a571556d7597ac15b460c4b`: full-history conclusion explicitly includes `polynomial/Hermite/TensorSketch`.

Other requested dedupe anchors were checked for current lineage and do not create a distinct Hermite-chaos opening:

- **R209** archive branch `research/r209-e136-archive-evidence` @ `e1f6dd6a6bc351b8253e255fef424b1931b37de3`; archive blob `7fec90369227839a9902c7cceb9f3519acb66cb8`; normalized V25 blob `0183d0570f7c9965e00e8553ffc003c313865232`.
- **R223** branch `research/r223-v25-isolated-improvement-20260922` @ `09efbb920313850a4727bd34db9088a46227ce5f`; protocol blob `1e88341a6320bf91c8f4eff0aa60d8b6a33cf484`; normalized result blob `c8b617c43ff1145977c38e7e1cca6d23985ec392`.
- **R317** branch `review/r317-truncated-normal-gate-estimator-20260924` @ `6ede298753b7ebc35765e18479775879769712ff`; report blob `b134ccb1c77c3d0e70fe70b64b651e6e5dd1f77c`; receipt blob `81f6adbc9cc64ab5ad3f4aaf230fe035fffa5ea5`.
- **R321** branch `review/r321-r317-compression-red-team-20260924` @ `774aac4105bfe1a171f40f7272fc4267aae6c2f8`; report blob `b0b71f4d74596c4744d0353d1654ac5726aeb2bb`; receipt blob `2c3d9f881d669ee924cecca106611c6c295a7243`.
- **R335/R338 corrected lineage** branch `review/r335-accuracy-side-estimator-scout-20260924` @ `1e233a439b81708353513998898e9f7cfd10caf2`; corrected report blob `32fcd8e7c43c712aa81b2c0e2f3487f3911d9c23`; corrected receipt blob `4e7d9523f1b08580358b9f2340f076977e611573`.

## Scope boundary

E115's own terminal scope is deliberately narrower than “all possible spectral methods”:

> dense total-degree Hermite chaos is ruled out; a separately preregistered low-rank/tensorized chaos mechanism is not ruled out.

R347 does **not** define a new tensorized/low-rank chaos state, rank-growth theorem, compression identity, or distinct experiment identity. Therefore the current R347 prompt is a duplicate of E115 rather than a new tensorized-chaos proposal. A future tensorized-chaos task would require an explicit distinct representation and rank-growth/error certificate before it could pass novelty dedupe.

## Required R347 items not re-derived

Because the dedupe stop rule fired, R347 intentionally does **not** perform the requested downstream steps:

1. no new primary-paper coefficient recurrence derivation;
2. no new Gaussian/ReLU assumption analysis;
3. no new final-layer mean truncation/propagation theorem;
4. no new width-1024/depth-16 cost model beyond citing the already committed E115 evidence;
5. no new falsifier design or execution.

This avoids repackaging an occupied method under a new name.

## Measurement classification

R347 produces **no scientific estimator measurement**.

- new estimator family: **NO**
- estimator implementation: **NO**
- synthetic width-8/depth-4 run: **NO**
- official/public benchmark run: **NO**
- leaderboard access/scraping: **NO**
- target/private/holdout/full access: **NO**
- new primary-literature scan: **NO — stopped at dedupe**
- E115 historical measurement reused as immutable prior evidence only: **YES**
- competitor-method inference from rank/score: **NO**

## Execution accounting

- code created or modified: **NO**
- benchmark/falsifier execution: **0**
- downloads/dependency installs: **0**
- GitHub Actions: **0**
- paid resources: **NO**
- submission: **NO**
- main edit: **NO**
- PR edit: **NO**
- control edit: **NO**
- queue edit: **NO**
