# E038 result — conditional-Gaussian full-covariance ReLU kernel

Status: **DONE / NO-GO / DROP**

Idempotency key: `ARC-E037-RESEARCH-20260915-E038`

## Provenance

- Branch: `research/e038-conditional-gaussian-cov-20260915`
- Canonical base: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`
- Protocol-only first commit: `37e1eb6cb45c7b77cf228f2e43ee6531de0f13a6`
- Implementation commit: `a5b3e2ec49a1faa003a91aea38e1aa50ae6d99a7`
- Final pre-science focused/backend-preflight commit: `d517f1d02b23a20cf3f0b4bfd47af70265cd78cf`
- Frozen harness commit: `6ddfa03488dabdc81208b40ba64af3a48f4e90ed`
- Frozen scientific commit: `8c871d767b692f991505ff714169c95dc9755137`
- Public Phase-2 mini index: `0` only
- Scientific workflow run: `35011453895`
- Job: `104524156199`
- Artifact: `10414011684`
- Artifact zip SHA256: `61ef8698c90a5d8d862ff493f13df19a06c8c650a9178cf01fc33cc4daefb2c4`

## Focused TDD

- RED: run `35010906122`, job `104522320045`; expected `ModuleNotFoundError` before implementation.
- Initial implementation run `35011081213`, job `104522889909`: 4/5 tests passed; the only failure was a test assertion requiring pre-clipping correlation to equal exactly 1.0, while floating roundoff was `1.0000000000000002`. The protocol explicitly records correlation before mathematical clipping, so the assertion alone was relaxed to `<=1e-12`; estimator code was unchanged.
- Focused GREEN: run `35011191613`, job `104523269300`: success.
- Backend-preflight GREEN: run `35011303146`, job `104523647847`: success; no public data accessed.
- Frozen scientific run repeated focused tests: `6 passed, 3 warnings in 2.28s`.

No public-mini scientific metric was observed before focused GREEN and backend preflight.

## Frozen local diagnostic

Single allowed public-mini index-0 measurement:

- final-layer MSE: `1.1938567981733376e-05`
- billed FLOPs: `174310368260`
- utilization: `0.079267178198279`
- adjusted proxy: `1.1938567981733376e-06`
- residual wall time: `0.3520044520000738 s`
- measured wall time: `18.617897315000008 s`
- deterministic repeat max abs difference: `0.0`
- covariance diagonal max abs error: `0.0`
- maximum absolute correlation before mathematical clipping: `1.0000001192092896`
- finite: `true`
- failures: `0`
- frozen scope check: `true`

## Gates

PASS:

- utilization `<=0.14`
- failures `==0`
- residual `<0.400 s`
- finite
- deterministic repeat
- covariance diagonal error `<=1e-12`
- frozen 16-node conditional-kernel scope

FAIL:

- raw final MSE `<=1.89e-08`: observed `1.1938567981733376e-05`
- adjusted proxy `<2.5e-09`: observed `1.1938567981733376e-06`

The raw miss is about `631.67x` the required ceiling. Relative to E035 (`4.920249745871731e-05`), the full nonlinear conditional-Gaussian covariance transform improves raw error by roughly `4.12x`, but pairwise Gaussian state remains far from sufficient. The missing information is therefore higher-order/non-Gaussian cross-neuron source structure, not merely a better Gaussian covariance nonlinearity.

## Decision

**NO-GO / DROP E038.**

No alternate quadrature order, epsilon, dtype cast, PSD repair, symmetrization change, K3/K4 add-back, source add-back, rerun, second mini index, scorer, holdout, tuning, or sweep is allowed under E038. Any new mechanism must use E039+ from canonical.

Canonical and `research/ledger.csv` were not changed. No scorer or holdout was used.
