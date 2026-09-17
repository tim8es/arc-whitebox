# E104 Result — local scientific GO

Idempotency key: `ARC-E104-HAAR-RADIAL-RAOBLACKWELL-20260918`

## Provenance

- Branch: `research/e104-haar-radial-raoblackwell-20260918`.
- Direct canonical parent: `29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Protocol/proof commit: `f85ce2487ae953f20b611b327d2269f1c54548fc`.
- Frozen Stage-A implementation commit:
  `12f355b8d905007ceb2abc139440468ffb47ac8f`.
- Sole workflow commit:
  `d21ee2567124fe73f124218c3033ff0a2a6123b5`.

## Exact mechanism

For every bias-free ReLU MLP layer output `H`, positive homogeneity gives
`H(rq)=rH(q)`. With Gaussian polar decomposition `X=RQ`,
`R~chi_n` independent of the spherical direction `Q`.

For fixed Haar directions, replacing each independent random radius `R_i`
by the analytic `E[R]` is the conditional expectation of the E100 estimator
given those directions. E104 is therefore an exact Rao–Blackwellization of the
random-radius E100 estimator for every fixed zero-bias network: it preserves
expectation and cannot increase coordinatewise estimator variance in exact
arithmetic.

## Frozen Stage-A evidence

- run: `35287541033`
- job: `105423103388`
- conclusion: success
- artifact: `e104-stage-a`
- artifact ID: `10524219347`
- artifact ZIP SHA256:
  `37fc50e20a084aa1e59a59443da9ce7022a2dbee13a88e7d643970d291af4301`
- artifact size: `1358` bytes.

Frozen corpus:

- width/depth: `32/6`
- network seeds: `104000..104007`
- reference: `65536` iid-antithetic trajectories
- E100 comparator / E104 candidate: `2048` trajectories
- common Haar direction seeds: `204000..204007`
- comparator random-radius seeds: `304000..304007`
- no benchmark/public/scorer/holdout/full data.

Measurements:

- E100 same-direction random-radius pooled MSE:
  `2.964601925006463e-05`
- E104 analytic-radius pooled MSE:
  `2.4711999064194e-05`
- pooled E104/E100 ratio:
  `0.8335688800492203`
- relative MSE reduction:
  `16.64311199507797%`
- E104 wins: `6/8`
- worst per-network E104/E100 ratio:
  `1.170455041103274`
- positive-homogeneity max relative error:
  `2.2608089923871456e-07`
- deterministic scalar-signature replay max abs:
  `0.0`
- exact antithetic pair max abs:
  `0.0`
- all outputs finite: true
- analytic mean chi radius at width 32:
  `5.612839389220763`.

Per-network E104/E100 ratios:

- 104000: `0.9130575138930157`
- 104001: `1.0704461164540224`
- 104002: `0.8930809341423782`
- 104003: `0.3711565046663753`
- 104004: `0.5476962691290366`
- 104005: `0.8868803866330074`
- 104006: `0.6148973990231094`
- 104007: `1.170455041103274`.

All preregistered gates passed.

The inherited conservative production-utilization upper bound from measured
E103 is `0.0677789313122048 <= 0.12`; E104 removes random chi-radius work and
adds only a scalar analytic radius constant.

## Decision

**E104 = LOCAL SCIENTIFIC GO FOR HAAR RADIAL RAO–BLACKWELLIZATION.**

This is stronger than a tuning observation: the estimator change is backed by
a fixed-network conditional-expectation theorem and the frozen synthetic
experiment confirms a material additional variance reduction over E100 at the
same directions/trajectory count.

It does not establish competition raw final-layer MSE `<=1.89e-8`.
No public/public-mini, official scorer, holdout/full, tuning sweep, rescue,
canonical mutation, ledger mutation, or merge occurred.
