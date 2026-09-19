# E104 — transfer / variance-decomposition gate

Idempotency key: `ARC-E104-TRANSFER-VARIANCE-DECOMP-20260919`

Status: **FROZEN TARGET-FREE TRANSFER GATE**.

## Provenance

- Branch: `research/e104-haar-radial-raoblackwell-20260918`.
- Frozen E104 Stage-A protocol commit: `f85ce2487ae953f20b611b327d2269f1c54548fc`.
- Frozen E104 Stage-A result: local scientific GO, pooled target-relative E104/E100 MSE ratio `0.8335688800492203` on width/depth `32/6`.
- Independent production-shape verification receipt exists and measures utilization `0.06777892944955966` at width/depth/trajectories `1024/16/4096`; it evaluates no accuracy target.
- This transfer gate changes no estimator mechanism and reads no benchmark/public target.

## Exact variance identity

For a fixed bias-free ReLU MLP final-layer map (F), positive homogeneity gives

[
F(rq)=rF(q), qquad rge0.
]

For one antithetic unit direction define

[
A(q)=rac{F(q)+F(-q)}{2}inmathbb R^p.
]

Let (q_1,dots,q_m) be the frozen Haar-row directions and let independent
(R_isimchi_n). The E100 random-radius estimator and E104 Rao–Blackwell
estimator are

[
M(Q,R)=rac1msum_{i=1}^m R_i A(q_i),
]

[
Z(Q)=rac{mu_R}{m}sum_{i=1}^m A(q_i),
qquad
mu_R=E[R].
]

Conditioned on the complete direction set (Q),

[
Z(Q)=E[M(Q,R)mid Q].
]

Since the radii are independent and (E[R^2]=n),

[
sigma_R^2=operatorname{Var}(R)=n-mu_R^2.
]

For mean squared Euclidean error per output coordinate, the exact conditional
radial variance removed by Rao–Blackwellization is

[
V_R(Q)
=
E_Rleft[rac{|M-Z|_2^2}{p}mid Qight]
=
rac{sigma_R^2}{m^2p}
sum_{i=1}^m|A(q_i)|_2^2.
]

No target appears in this identity.

Across random Haar direction sets, the law of total variance gives

[
operatorname{trVar}(M)/p
=
operatorname{trVar}_Q(Z)/p
+
E_Q[V_R(Q)].
]

Therefore the target-free variance ratio attributable to E104 is

[
ho
=
rac{operatorname{trVar}_Q(Z)/p}
{operatorname{trVar}_Q(Z)/p+E_Q[V_R(Q)]}.
]

The removable radial share is (1-ho). This is the exact next gate: Stage-A
already showed target-relative improvement on one shape, whereas this test asks
whether the mechanism still removes a material share of estimator variance on
a disjoint architecture without using any truth/reference means.

## Frozen transfer corpus

Synthetic only:

- width `64`;
- depth `8`;
- zero-bias He Gaussian float32 weights;
- network seeds `104800,104801,104802,104803`;
- per network, `16` independent Haar direction sets;
- direction-set seed for network index `a` and set index `j`:
  `604800 + 100*a + j`;
- positive directions per set: `256` = four complete `64x64` Haar-QR blocks;
- each block uses float64 iid Gaussian QR and positive-diagonal sign canonicalization;
- antithetic response uses both `q` and `-q`;
- float32 network propagation, float64 reductions;
- no random radius is needed for the primary variance decomposition.

All seeds and dimensions are disjoint from E104 Stage A.

## Finite-corpus estimator of the exact decomposition

For each network and direction set (j), compute (Z_j) and exact
(V_{R,j}) from the formula above.

Directional variance is estimated only from the frozen direction ensemble:

[
widehat V_Q
=
rac{1}{(J-1)p}
sum_j|Z_j-ar Z|_2^2.
]

The frozen network-level transfer statistic is

[
widehatho
=
rac{widehat V_Q}
{widehat V_Q+rac1Jsum_jV_{R,j}}.
]

Aggregate terms are formed by averaging (widehat V_Q) and the exact radial
terms across the four networks before taking the ratio.

This is a variance benchmark, not an accuracy estimator.

## Independent radial calibration check

On network `104800`, direction set `j=0` only, draw exactly `8192`
independent radius vectors using PCG64 seed `704800`.

For each replicate compute (M_k) from the already materialized (A(q_i));
do not rerun the network. Compare

[
rac1Ksum_krac{|M_k-Z|_2^2}{p}
]

with the analytic (V_R(Q)).

This check validates the executable implementation of the exact radial term.
It does not estimate network accuracy.

## Frozen gates

All integrity gates must pass:

1. all arrays/scalars finite;
2. exact antithetic input pairing;
3. per-QR-block direction orthogonality max abs error `<=1e-12`;
4. deterministic repeat scalar signature max abs `==0`;
5. (sigma_R^2>0);
6. every network has positive analytic radial variance;
7. 8192-replicate radial calibration relative error `<=0.05`.

Scientific transfer/variance GO requires:

8. aggregate (widehathole0.90), i.e. at least 10% of the estimated
   random-radius variance is the exactly removable radial component;
9. at least `3/4` networks have removable radial share `>=0.05`;
10. every network has (widehatho<1).

Failure of any scientific gate is a transfer NO-GO for claiming material E104
variance reduction beyond the original width/depth `32/6` synthetic corpus.

## Interpretation boundary

A pass means only: the frozen Haar/radial Rao–Blackwell mechanism transfers to
a disjoint synthetic architecture and removes a material, analytically
identified component of estimator variance.

It does **not** establish competition raw MSE, adjusted score, public-set
accuracy, or superiority to any non-E100 estimator. No public/public-mini,
official scorer, holdout/full benchmark target, tuning, sweep, canonical
mutation, or ledger mutation is authorized.
