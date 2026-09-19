# E112 Result — terminal NO-GO

Decision: **TERMINAL NO-GO / DROP E112**

## Mechanism

Deterministic fourth-order Edgeworth correction of the scalar pre-ReLU marginal using exact first four moments.

This is not a sampler/control variant and does not reopen E104-E111.

## Frozen exact gate

- input: N(0,I_2)
- width: 8
- depth: 4
- zero bias
- weight seed: 112112
- exact piecewise angular integration
- exact Rayleigh radial moments through order 4
- no Monte Carlo
- no numerical quadrature
- no benchmark/public targets

Protocol commit: `06d87a2e76d6ac0c99e34dfbcdd9c50f66c446d4`

Implementation/verifier lineage:
- implementation `dd4036dcb1bfabe8633d2c8555237b6abab44795`
- verifier `33ae15ae616c864f75a053cfda56114e351fa3c8`
- sole scientific arm `7b5d814a0407a41ded91d2a2b558ab56b72bd981`

Execution:
- run `35455219121`
- job `105929179847`
- conclusion `success`
- artifact `e112-exact-gate`
- artifact ID `10588046582`
- artifact ZIP SHA256 `406132e2cd2ec7a50b103b67866e62269795329333370caf4c93920df6909a1b`
- extracted JSON SHA256 `619009f2eee0f228af9db1c9f10ec1992d9da0e2d119c15c94c4d01ad07b5a7d`

## Exact bias result

Layerwise E112 Edgeworth-4 mean-bias MSE:

- layer 1: `2.4074124304840448e-33`
- layer 2: `5.3614554238036615e-05`
- layer 3: `5.530464877850174e-04`
- layer 4/final: `3.0035784800557875e-04`

Plain Gaussian final bias MSE:
`4.3282315571962346e-03`

Final E112/Gaussian ratio:
`0.06939505061973768`

Thus Edgeworth-4 removes about 93.06% of the frozen Gaussian plug-in bias, but absolute final bias remains

`3.0035784800557875e-04 = 15,891.9496 x 1.89e-8`.

Pooled all-layer E112 bias MSE:
`2.267547225071582e-04`.

Deterministic replay max abs:
`0.0`.

## Cost admission

Inherited all-in upper:
`149,220,512,434` FLOPs.

Frozen E112 increment upper:
`500,000,000` FLOPs.

All-in upper:
`149,720,512,434` FLOPs.

Utilization:
`0.06808500640272541 <= 0.13`.

Compute passes; scientific absolute bias fails.

## Verdict

E112 is a strong relative correction but has no credible path to the raw target under the frozen mechanism. It is terminal and may not be rescued by damping, clipping, term deletion, alternate expansion order, extra cumulants, or retuning under E112.

No production gate is authorized by E112.
