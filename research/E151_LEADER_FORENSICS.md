# E151 Leader Forensics — primary-source audit

Date: 2026-09-21
Branch: `research/e151-leader-forensics-angular-strassen-20260921`
Parent: E148 terminal head `d79eb8e670fbb8ff007283d9ed1eab6dd53a8b35`

## Scope

Find one target-free mechanism that can plausibly account for the Phase-2 frontier
`raw < 2.1e-8` with an all-in cost at or below `0.135 B`, while excluding:

- V29 old-tier compression / old-tier rescue;
- low-rank K3 / GSTT / response-projected K3;
- CountSketch;
- MUB128 repair or any spherical-design sampling estimator;
- sampling control variates.

No public target, public mini, scorer, holdout, full suite, or submission is run in E151.
This note is a source audit plus a frozen synthetic falsifier only.

## Primary-source findings

### 1. ARC's published algorithm leaves representation freedom outside "compress K3"

ARC's paper states that the same cumulant-propagation estimate can be represented
factorially to save a factor of width in the linear step, and that the augmented
algorithm is a separate accuracy/runtime trade. The current official repository is
even more explicit than the paper: factored AUGMENT deliberately drops
non-hypertree leading-order diagrams that it cannot afford, and the repository TODO
says cached FLOP/results need refresh after the truncation changes.

Pinned official ARC source:
- paper: https://arxiv.org/abs/2605.05179
- repo: https://github.com/alignment-research-center/mlp_cumulant_propagation
- audited commit: `93d091a4c26c042bfffa28f2e76a81bc0aba94bb`
- `src/mlp_kprop/kprop_harmonic.py` blob `7e901ce069baf40e2bdcbfb325a3c1b2e93b6007`
- `src/mlp_kprop/factor_k3.py` blob `ed7cddd91fcf3a744a02aacfba6f24f9f743c82a`
- `TODO.md` blob `d2a6f79bc5816f359994f156b322672c5bb5ca48`

This does **not** identify the leader algorithm. It does establish that a change of
representation/arithmetic can alter the cost frontier without being an old-tier
K3 compression scheme.

### 2. Exact radial/angular gauge is a deterministic state representation, not sampling

For a zero-bias ReLU MLP `f`, positive homogeneity gives, for
`X ~ N(0,I_n)`,

```
X = (R/sqrt(n)) Y,
Y uniform on S^{n-1}(sqrt(n)),
R independent of Y,
E[f(X)] = a1 E[f(Y)],
a1 = E[R]/sqrt(n).
```

The angular input has
`E[Y]=0`, `Cov(Y)=I`, `K3(Y)=0`, and

```
Cum4(Y_i,Y_j,Y_k,Y_l)
= -2/(n+2) * (delta_ij delta_kl + delta_ik delta_jl + delta_il delta_jk),
Cum4(Y_i,Y_i,Y_i,Y_i) = -6/(n+2).
```

This is an exact reparameterization of the target expectation. It changes the
truncation error of an approximate cumulant closure without adding sampling.

Open Phase-2 implementation/audit:
https://github.com/barnobarno666/ARC-White-Box-Estimation-2026
commit `1558651e49d68b40821930f0f9c9a059f33d3a52`.

Pinned artifacts:
- `phase8report.md` blob `3087457e972c0ea4692aeb9070c2a456cd1aed60`
- `candidates/estimator_p8_final.py` blob `fc743f80329c00cf2f0985333918496c006af2a2`

That report records, on its locked Phase-2 development panel, Gaussian -> angular
raw-MSE changes of:
- K2: `4.1257e-6 -> 3.4236e-6` (-17.02%);
- K2+scalar-K4: `4.0639e-6 -> 3.4303e-6` (-15.59%);
- its K3 architecture: `3.7859e-8 -> 3.4859e-8` (-7.92%, 8/8 wins).

Those are third-party measurements, not E151 measurements and not evidence that the
current leaders use the mechanism.

### 3. One-level Strassen is an exact arithmetic transform with a measured Phase-2 cost effect

The same open implementation replaces eligible dense matrix products by one level
of the seven-product Strassen identity. In exact arithmetic it changes no matrix
product. For an even `n x n` multiply, counting one multiply-add as 2 FLOPs and
18 half-size matrix additions,

```
C_classic = 2 n^3
C_strassen1 = 7 * 2 * (n/2)^3 + 18 * (n/2)^2
rho_1024 = C_strassen1 / C_classic = 0.877197265625.
```

The open Phase-2 report measures total estimator utilization
`0.786835 -> 0.695774`, ratio `0.884269`, with essentially unchanged raw MSE.
This is consistent with a matrix-product-dominated workload.

### 4. Frontier arithmetic

A public-board snapshot committed in the same open repository records:
- Puffi: raw `2.02e-8`, utilization `0.1478860181`;
- suliman_tadros: raw `1.97e-8`, utilization `0.1504215170`.

These rows are evidence about the frontier, not about their undisclosed algorithms.

If an otherwise identical matrix-dominated estimator received the **measured**
open-source total-cost ratio `0.8842692559`, the implied utilizations would be:

```
0.1478860181 * 0.8842692559 = 0.1307710592
0.1504215170 * 0.8842692559 = 0.1330131229
```

both below `0.135 B`.

This transfer is a hypothesis, not a fact: it requires the leader-grade arithmetic
to have enough eligible dense matrix products. Using the exact one-level ratio
`rho_1024=0.877197265625`, the required eligible fractions are 70.96% and 83.49%
respectively.

## Frozen E151 hypothesis

**ARSG: Angular-Radial State Gauge + exact one-level Strassen arithmetic.**

A leader-grade deterministic mechanistic closure can cross the
`raw < 2.1e-8, cost <= 0.135 B` frontier without V29 old-tier compression or a
new low-rank K3 approximation if:

1. the closure is evaluated in the exact angular gauge, so radial dispersion is
   removed before truncation and the known negative input K4 is injected;
2. at least the frozen required fraction of its billed work is eligible dense
   matrix multiplication;
3. those products are evaluated with one exact Strassen level.

This is one composite representation/arithmetic hypothesis. It is deliberately
not a claim that Puffi, suliman_tadros, J2W, or marius_binner use it.

## Why this survived the forensic filter

It is not a rename of E147 or E148: no K3 basis, rank, response projection, TT core,
or source-age compression is introduced. It is not CountSketch, MUB/spherical
sampling, or a control variate. Both parts have primary/open-source support and
have exact identities that can be falsified without benchmark targets.

The weak point is transferability: the angular gain and the Strassen total-cost
ratio were measured in one open K3 implementation, not in the undisclosed leader
implementations. E151 therefore freezes a falsifier and does **not** promote a
candidate or run a public target.
