# R212 — protocol-first falsifier for Alternative-Basis Strassen

Date: 2026-09-22  
Idempotency: `ARC-R212-ABS-20260922`  
Branch: `research/r212-alternative-basis-strassen-20260922`  
Parent: R211 terminal receipt `9a24c88baf2dad6ade40f500922958c5f59a626f`.

## 0. Scope

R212 selects exactly one not-yet-closed algorithmic family:

> **Karstadt–Schwartz Alternative-Basis Strassen (ABS), stationary 2x2 rank-7 recursion with a frozen uniform recursion depth and classical leaves.**

R212 changes the linear/basis phase of the existing rank-7 Strassen leaf kernel. It does
not change estimator semantics, K3/D21 state, source ranks, or contraction DAG.

Explicit exclusions:

- E011 Hopcroft–Kerr rectangular bilinear kernel;
- R202 fixed TA32/LITA scheme;
- R206 TA/LITA rank sweep;
- R211 contraction-DAG CSE/reassociation;
- alternative bilinear ranks/base sizes;
- nonuniform recursion schedules;
- decomposed-recursive higher-dimensional basis methods;
- rank/source/seed sweeps;
- holdout, paid resources, scorer, submission, leaderboard/canonical mutation.

Repository branch/commit search before protocol freeze found no prior
`alternative basis`, `ABMM`, or `winograd variant` branch/commit in this project.

## 1. Primary sources

### Karstadt & Schwartz

Elaye Karstadt and Oded Schwartz,
*Matrix Multiplication, a Little Faster*, JACM 67(1), 2020,
DOI `10.1145/3364504` (conference precursor SPAA 2017,
DOI `10.1145/3087556.3087579`).

Primary claim used: changing basis permits a 2x2 rank-7 Strassen-like algorithm whose
leading arithmetic coefficient is reduced from 6 to 5.

### Schwartz & Vaknin

Oded Schwartz and Noa Vaknin,
*Pebbling Game and Alternative Basis for High Performance Matrix Multiplication*,
SIAM J. Sci. Comput.,
DOI `10.1137/22M1502719`.

Normative details used by R212 are explicit in that paper:

- exact alternative-basis matrices `phi_opt`, `nu_opt^{-1}`;
- rank 7;
- bilinear phase: 7 multiplications and 12 additions/subtractions;
- each input basis transform: 2 additions/subtractions;
- inverse output basis transform: 2 additions/subtractions;
- exact ring identity for the resulting matrix product.

### 2026 stability source

O. Schwartz, S. Toledo, N. Vaknin, et al.,
*Alternative Basis matrix multiplication is fast and stable*,
Numerische Mathematik 158 (2026),
DOI `10.1007/s00211-026-01531-9`.

This source establishes that alternative-basis algorithms are not intrinsically excluded
by numerical stability. R212 does **not** assume the float32 gate from that theorem; it
retains an empirical <=1.05 gate if cost feasibility survives.

## 2. Pinned ARC/V29 production source

`504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`

- `estimators/estimator_v29.py` blob
  `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`;
- `docs/audit_v29_ns_d0.log` blob
  `a689ef69fd64bed7765cb93ce4910c3fedcbd04a`.

Pinned V29 already uses the ordinary 2x2 rank-7 Strassen schedule with 18 additions at
recursive nodes. R212 tests only whether the exact alternative-basis linear phase can
cross the inherited H185/R206 mechanism gate.

## 3. Frozen exact-small identity

Use the primary-source basis maps.

For a 2x2 input matrix A:

[
phi(A) =
egin{bmatrix}
A_{11} & A_{12}\
A_{21} & A_{12}-A_{21}+A_{22}
end{bmatrix}.
]

Use the same map for B.

On transformed inputs, define:

[
t_1=A_{21}+A_{22},quad
t_2=A_{22}-A_{12},quad
t_3=A_{22}-A_{11},
]

[
t_4=B_{22}-B_{11},quad
t_5=B_{21}+B_{22},quad
t_6=B_{22}-B_{12}.
]

Seven products:

[
m_1=A_{11}B_{11},;
m_2=A_{12}B_{21},;
m_3=A_{21}t_4,;
m_4=A_{22}B_{22},
]

[
m_5=t_1t_5,;
m_6=t_2t_6,;
m_7=t_3B_{12}.
]

Transformed output:

[
C'_{11}=m_1+m_2,
quad
C'_{12}=m_5-m_7,
]

[
C'_{21}=m_3+m_6,
quad
C'_{22}=m_5+m_6-m_2-m_4.
]

Inverse output basis:

[

u^{-1}(C') =
egin{bmatrix}
C'_{11} & C'_{12}-C'_{22}\
-C'_{21}+C'_{22} & C'_{22}
end{bmatrix}.
]

Frozen integer witness:

[
A=egin{bmatrix}1&2\3&4end{bmatrix},
qquad
B=egin{bmatrix}5&-1\2&3end{bmatrix}.
]

Direct product:

[
AB=egin{bmatrix}9&5\23&9end{bmatrix}.
]

The frozen ABS equations yield exactly the same integer matrix.

No floating-point tolerance is used for this identity.

## 4. Conservative production FLOP lower bound

Production screen: one square `1024x1024 @ 1024x1024` product, the dominant V29
young/hub geometry.

Inherited conservative mechanism gate:

[
C_{candidate}/C_{classical} le 0.42,
]

with the same project convention used by R202/R206:

[
C_{classical}=2n^3.
]

Let `L` be the uniform number of ABS recursive levels,
`0 <= L <= log2(1024)=10`.

At level `L`, there are `7^L` classical leaves of side `n/2^L`.

Mandatory leaf lower bound:

[
C_{leaf}(L)
=
2,7^Lleft(rac{n}{2^L}ight)^3.
]

The primary ABS bilinear phase requires 12 additions/subtractions per 2x2 recursive node.
Therefore mandatory bilinear-linear work is

[
C_{lin}(L)
=
sum_{j=0}^{L-1}
12,7^jleft(rac{n}{2^{j+1}}ight)^2.
]

Define the **optimistic lower bound**

[
C_{LB}(L)=C_{leaf}(L)+C_{lin}(L).
]

This deliberately charges **zero** for:

- both input basis transformations;
- inverse output basis transformation;
- materialization/copies;
- padding/cropping;
- buffer setup;
- integration overhead;
- runtime overhead.

So `C_LB` is strictly favorable to ABS.

For `n=1024`, exhaustive integer `L=0..10` gives the minimum at `L=7`:

[
C_{leaf}(7)=843,308,032,
]

[
C_{lin}(7)=206,632,704,
]

[
C_{LB}(7)=1,049,940,736.
]

Against

[
2n^3=2,147,483,648,
]

the best optimistic ratio is

[
r_{LB}
=
0.4889167547225952.
]

Frozen gate:

[
r_{LB} le 0.42.
]

It fails by

[
0.0689167547225952
]

absolute ratio, or about 16.41% relative to the gate.

Because basis transforms and all integration work were set to zero, no real implementation
of this frozen ABS family can improve the bound.

## 5. Frozen falsifier

Only if the lower-bound gate had passed, one synthetic check would be authorized:

- shape: `1024x1024 @ 1024x1024`;
- float32 deterministic inputs, seed `212`;
- frozen recursion depth = the analytically cheapest feasible `L`;
- byte-identical inputs for ordinary V29 Strassen comparator and ABS;
- float64 direct matmul reference;
- exact-small integer identity must pass first;
- complete arithmetic ledger including basis transforms;
- deterministic replay hashes.

Float32 gates:

1. relative-Frobenius error candidate/ordinary <= `1.05`;
2. max-absolute error candidate/ordinary <= `1.05`.

Cost gate remains complete candidate/classical <= `0.42`.

No alternate recursion depth, basis, schedule, seed, or second run would be allowed.

## 6. Decision rule

The production lower bound is evaluated before any synthetic execution.

Observed frozen lower bound:

[
0.4889167547225952 > 0.42.
]

Decision:

`TERMINAL_NO_GO_COST_LOWER_BOUND`.

Synthetic float32 execution is therefore forbidden by protocol.

This result closes only the stationary 2x2 rank-7 Karstadt–Schwartz
Alternative-Basis Strassen family under the R206/H185 0.42 mechanism gate. It does not
claim a universal lower bound against other base sizes, other ranks, or decomposed
recursive algorithms; those are different families.
