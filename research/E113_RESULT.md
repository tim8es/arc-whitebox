# E113 Result — terminal NO-GO

Decision: **TERMINAL NO-GO / DROP E113**

## Mechanism

Deterministic top-4 **actual upstream gate-pattern conditioned** Gaussian-ReLU plug-in.

Each output conditions on the observed four-bit activation state of the four largest-|weight| parents. This is structural conditioning, not a fitted latent mixture and not a sampler/control variant.

## Frozen exact gate

- input: N(0,I_2)
- width: 8
- depth: 4
- zero bias
- weight seed: 113113
- exact piecewise angular integration
- exact actual upstream gate states
- no Monte Carlo
- no numerical quadrature
- no benchmark/public targets

Protocol commit: `f7a38cdbcbefc48af880a51f24aefb90fc5b9e0d`

Implementation/verifier lineage:
- implementation `eb7a82bb9006a41d92e7ef2a047e386600758cd0`
- verifier `277a71ce349879ad1ff024b4f8dd25d4f6c207f8`
- sole scientific arm `0570a76b07362c9d3df52c4190850391c2a4389a`

Execution:
- run `35455222505`
- job `105929188669`
- conclusion `success`
- artifact `e113-exact-gate`
- artifact ID `10587877752`
- artifact ZIP SHA256 `67b1f603eb680825aef96ff4e031ad04be9302e2fd11ed974250685f5a3b7a32`
- extracted JSON SHA256 `c576acd35e02c16c2e2856681327c13c617a77a69fa349ae0430efeb3ce5182d`

## Exact bias result

Layerwise E113 conditional mean-bias MSE:

- layer 1: `3.490748024201865e-33`
- layer 2: `3.732303736648083e-04`
- layer 3: `2.2719924228266947e-03`
- layer 4/final: `2.5704565401863883e-03`

Plain Gaussian final bias MSE:
`3.250972934646355e-02`

Final E113/Gaussian ratio:
`0.07906730052386626`

The structural gate conditioning removes about 92.09% of the frozen Gaussian bias, but final absolute bias remains

`2.5704565401863883e-03 = 136,002.9915 x 1.89e-8`.

Pooled all-layer E113 bias MSE:
`1.3039198341694728e-03`.

State-probability maximum absolute closure error:
`2.220446049250313e-16`.

Deterministic replay max abs:
`0.0`.

## Cost admission

Inherited all-in upper:
`149,220,512,434` FLOPs.

Frozen E113 increment upper:
`2,500,000,000` FLOPs.

All-in upper:
`151,720,512,434` FLOPs.

Utilization:
`0.06899450110449834 <= 0.13`.

Compute passes; scientific absolute bias fails.

## Verdict

E113 confirms that real hidden-gate conditioning captures important non-Gaussian structure, but four structural gate bits are nowhere near sufficient for competition-scale accuracy.

E113 is terminal. No parent-count change, selector change, state merge/split, conditional fit, rescue or rerun is allowed under E113.

No production gate is authorized by E113.
