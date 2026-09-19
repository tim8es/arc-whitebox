# E104 transfer / variance-decomposition result — GO

Idempotency key: `ARC-E104-TRANSFER-VARIANCE-DECOMP-20260919`

## Provenance

- Branch: `research/e104-haar-radial-raoblackwell-20260918`.
- Frozen transfer gate commit: `a9c81b2ef8f6629f0d96abc392eb97c5b1822ece`.
- Implementation commit: `6db598dc5b5c6d57dd8e371b32c58b8bd7070194`.
- Workflow commit: `d189caf5e9d5329ad07cb3663cda9f59c964e929`.
- GitHub Actions run: `35446875709`.
- Job: `105907218691`.
- Conclusion: `success`.
- Artifact: `e104-transfer-variance`, ID `10585720511`.
- Artifact ZIP SHA256:
  `acbb2133897ed4dacef72e22d66b10be12c31a58736784815b511ab58d0082de`.
- Artifact size: `1387` bytes.

No public/public-mini, scorer, holdout/full benchmark target, reference target,
tuning, canonical mutation, or ledger mutation was used.

## Exact gate

For one fixed Haar direction set (Q=(q_i)_{i=1}^m), define the final-layer
antithetic response

[
A_i=A(q_i)=rac{F(q_i)+F(-q_i)}2.
]

The E100 random-radius estimator is

[
M(Q,R)=rac1msum_iR_iA_i,
]

while E104 is its conditional expectation over the independent chi radii,

[
Z(Q)=E[Mmid Q]
=rac{mu_R}{m}sum_iA_i.
]

Because (E[R^2]=n),

[
V_R(Q)
=
E_Rleft[rac{|M-Z|^2}{p}mid Qight]
=
rac{n-mu_R^2}{m^2p}sum_i|A_i|^2.
]

Thus, by total variance,

[
V_{m E100}=V_Q(Z)+E_QV_R(Q),
qquad
V_{m E104}=V_Q(Z).
]

The transfer statistic is therefore the target-free ratio

[
ho=
rac{V_Q(Z)}
{V_Q(Z)+E_QV_R(Q)}.
]

This is the exact variance component removed by radial Rao–Blackwellization;
it is not a competition-accuracy metric.

## Frozen transfer corpus

- width/depth: `64/8`;
- network seeds: `104800..104803`;
- 16 independent Haar direction sets per network;
- 256 positive directions per set = four complete `64x64` Haar-QR blocks;
- 512 antithetic trajectories per direction set;
- direction seed rule:
  `604800 + 100*network_index + set_index`;
- float32 network propagation and float64 reductions;
- disjoint from the original E104 Stage-A width/depth `32/6` corpus.

## Measured variance decomposition

Aggregate over the four transfer networks:

- directional E104 variance per coordinate:
  `1.1090400909817154e-4`;
- exact removable radial variance per coordinate:
  `3.208612882173001e-5`;
- predicted total E100 variance per coordinate:
  `1.4299013791990153e-4`;
- predicted E104/E100 variance ratio:
  `0.7756060013054634`;
- exactly removable radial share:
  `0.2243939986945367` = **22.4394%**.

Per-network predicted E104/E100 variance ratios:

- seed `104800`: `0.7617220248644164`
  (radial share `0.23827797513558363`);
- seed `104801`: `0.7181786792660733`
  (radial share `0.28182132073392663`);
- seed `104802`: `0.8038510554374702`
  (radial share `0.19614894456252993`);
- seed `104803`: `0.7898202474588977`
  (radial share `0.2101797525411022`).

All four networks exceed the frozen 5% removable-radial-share floor.

## Independent radial calibration

For network `104800`, first frozen direction set, the exact conditional
formula predicts

[
V_R=3.4925474464262145	imes10^{-5}.
]

With exactly 8192 independent radius vectors:

- empirical radial variance:
  `3.495219505079831e-5`;
- relative error vs exact formula:
  `0.0007650744033128221`.

Frozen calibration gate was `<=0.05`; PASS.

## Integrity

- deterministic repeat max abs: `0.0`;
- max Haar block orthogonality error:
  `1.1102230246251565e-15`;
- exact antithetic pair max abs: `0.0`;
- chi-radius variance:
  `0.4980317705252162 > 0`;
- all values finite;
- every network has positive exact radial variance.

## Frozen gate evaluation

PASS:

- aggregate predicted E104/E100 variance ratio `0.775606 <= 0.90`;
- 4/4 networks have removable radial share `>=0.05`;
- every network has predicted E104/E100 variance ratio `<1`;
- all integrity and calibration gates.

## Decision

**E104 TRANSFER_VARIANCE_GO.**

The Haar radial Rao–Blackwell mechanism transfers from the original
width/depth `32/6` Stage-A corpus to a disjoint `64/8` synthetic corpus and
removes a material variance component identified analytically, not through
target fitting.

The measured transfer benchmark supports a **variance-reduction claim only**.
It does not establish competition raw MSE `<=1.89e-8`, adjusted score,
public-set accuracy, or superiority to methods other than the frozen E100
random-radius estimator.
