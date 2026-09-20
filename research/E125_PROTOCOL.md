# E125 protocol — Clifford-8 rational tight-frame multi-source estimator

Idempotency key: `ARC-E125-CLIFFORD8-RATIONAL-TIGHTFRAME-20260920`

Status at freeze: **PROTOCOL ONLY / PREFLIGHT CERTIFICATE REQUIRED BEFORE ONE SCIENTIFIC RUN**.

Branch:
`research/e125-clifford8-rational-tightframe-20260920`.

Direct parent branch:
`research/bootstrap`.

This commit is protocol-only. No candidate code, tests, preflight output, workflow,
result, canonical ledger mutation, or scientific execution is permitted in this
commit.

## Non-rescue / non-duplication

E122 is terminal and remains terminal. E125 is **not** an E122 rescue.

E125 does not use E122 candidate code, simplex code, Haar-Stiefel frame generation,
modified Gram-Schmidt, E122 receipt values as candidate state, or post-result repair.

The only E122 fact used as scientific context is the already-established blocker:
a numerically generated Haar-8 frame can fail a strict orthogonality integrity gate
even when its small-width variance signal is favorable.

E125 replaces the entire frame/code construction with an algebraic signed-permutation
Clifford orbit generated from one independent spherical base direction per frame.

No canonical/ledger mutation or merge is authorized.

## New exact source construction

Define the exact integer 2x2 matrices

[
I=\begin{bmatrix}1&0\\0&1\end{bmatrix},quad
X=\begin{bmatrix}0&1\\1&0\end{bmatrix},quad
Z=\begin{bmatrix}1&0\\0&-1\end{bmatrix},quad
J=\begin{bmatrix}0&1\\-1&0\end{bmatrix}.
]

In dimension 8 define

[
A_0 = I\otimes I\otimes I
]

and the seven frozen signed-permutation matrices

[
egin{aligned}
A_1&=I\otimes I\otimes J,\\
A_2&=I\otimes J\otimes X,\\
A_3&=X\otimes J\otimes Z,\\
A_4&=Z\otimes J\otimes Z,\\
A_5&=J\otimes I\otimes Z,\\
A_6&=J\otimes X\otimes X,\\
A_7&=J\otimes Z\otimes X.
end{aligned}
]

Every entry is exactly in ({0,pm1}). The executable must verify with exact
integer arithmetic:

- (A_0=I_8);
- for (i>0), (A_i^T=-A_i);
- (A_i^T A_i=I_8);
- for distinct (i,j>0), (A_iA_j=-A_jA_i);
- every (A_i) is a signed permutation matrix.

For any production/stress dimension (d=8m), extend by

[
widetilde A_i = I_m\otimes A_i.
]

Then for every (q\in\mathbb R^d),

[
(widetilde A_iq)^T(widetilde A_jq)
=
|q|_2^2\delta_{ij}.
]

Therefore, for every unit (q), the eight vectors
(widetilde A_0q,ldots,widetilde A_7q) are an **exact orthonormal 8-frame**
in exact arithmetic. There is no QR, Householder, Gram-Schmidt, iterative
orthogonalization, or fitted correction.

The 16-source antipodal code for one frame is

[
C(q)=
{widetilde A_iq,-widetilde A_iq:i=0,ldots,7}.
]

This is an exact rational/integer operator construction; only the sampled base
direction (q) is floating/random.

## Exact unbiasedness identity

For each frame draw one independent

[
q_p = g_p/|g_p|_2,qquad g_p\sim N(0,I_d).
]

Thus (q_p) is uniform on (S^{d-1}).

Every (widetilde A_i) is fixed orthogonal. Hence each
(pmwidetilde A_iq_p) is also marginally uniform on the sphere.

For a fixed zero-bias degree-one homogeneous ReLU network (F), define

[
Y_p=
rac1{16}sum_{i=0}^7
left[
F(widetilde A_iq_p)+F(-widetilde A_iq_p)
ight].
]

Then exactly

[
E[Y_p]=E_Q[F(Q)].
]

With (mu_d=E[chi_d]),

[
widehatmu=
mu_drac1Psum_{p=1}^P Y_p
]

is unbiased in exact arithmetic for

[
E[F(X)],qquad X\sim N(0,I_d).
]

The estimator is a correlated multi-source estimator, but its unbiasedness does
not require the eight-frame distribution to be Haar-Stiefel.

## Frozen production shape

- (d=n=1024);
- depth (L=16);
- source-frame dimension (K=8);
- source codewords/frame (J=16);
- independent base directions/frames (P=252);
- propagated directions (N=PJ=4032);
- zero bias;
- network propagation float32;
- source construction / reductions float64 where required;
- PCG64 Gaussian base directions;
- no adaptive source count, rank, rotations, resampling, or tuning.

## Pre-run finite-sample output error certificate

This certificate must be computed from frozen weights **before any E125 source
direction is evaluated**.

Let final output width be (n). For every unit input (q), construct a
deterministic per-output nonnegative upper bound (b^{(ell)}) from weights only:

First layer:

[
b^{(1)}_j=|W_1[:,j]|_2.
]

For later layers:

[
b^{(ell)}
=
|W_ell|^T b^{(ell-1)}.
]

Because ReLU outputs are nonnegative and 1-Lipschitz,

[
0\le F_j(q)\le b_j:=b^{(L)}_j
]

for every unit (q). Therefore every frame average (Y_{p,j}) also lies in
([0,b_j]).

For (P) independent frames, Hoeffding plus a union bound gives, for one
estimator and confidence failure probability (delta),

[
t_j
=
b_jsqrt{rac{log(2n/delta)}{2P}}
]

and with probability at least (1-delta),

[
|widehatmu_j-mu_j|
\le
mu_d t_j
quad	ext{for all }j.
]

Hence the certified finite-sample output MSE bound is

[
oxed{
C_{m MSE}(W,delta,P)
=
mu_d^2
rac{log(2n/delta)}{2Pn}
|b|_2^2.
}
]

Frozen confidence discipline:

- total confidence failure budget across the eight scientific estimator
  realizations is (delta_{m total}=10^{-6});
- there are four 8-D and four 16-D candidate estimates;
- each estimate uses (delta=delta_{m total}/8=1.25\times10^{-7}).

The preflight must write immutable numerical (C_{m MSE}) values for the
frozen 8-D and 16-D stress networks **before** the scientific workflow is armed.
The certificate is a finite-sample stochastic error bound, not a competition
accuracy claim.

Preflight gates:

1. all (b_j) finite and nonnegative;
2. both 8-D/16-D certificates finite and positive;
3. independent recomputation of the formula is bitwise/deterministically equal;
4. production all-in cost proof below passes;
5. candidate/source code has not yet been executed.

A failed preflight closes E125 before scientific execution. No parameter change.

## Complete production operation ledger

Hard incremental cap:

[
C=136,758,472,261.
]

Frozen dimensions:

[
d=n=1024, L=16, K=8, J=16, P=252, N=4032.
]

All candidate operation classes are frozen before code.

### 1. Static Clifford construction and algebraic certification

Conservative one-time upper:

[
70,000.
]

This covers Kronecker construction of the eight 8x8 integer operators,
signed-permutation checks, all (A_i^TA_i) checks, and all pairwise
anti-commutation checks.

### 2. Base spherical direction generation

Per frame Gaussian generation:

[
16d.
]

All frames:

[
P(16d)=4,128,768.
]

### 3. Base-vector norm and normalization

Per frame:

[
3d+64,
]

covering square/sum, sqrt/division, scale and scalar bookkeeping.

All frames:

[
P(3d+64)=790,272.
]

### 4. Exact signed-permutation source materialization

The eight positive Clifford images and eight antipodes are signed
permutations/copies of (q). Conservatively charge one arithmetic-equivalent
sign/materialization operation per scalar:

[
16d
]

per frame, hence

[
P(16d)=4,128,768.
]

No dense (d\times K) orthogonalization exists.

### 5. Runtime norm/orthogonality certification

Even though orthogonality is algebraic, the frozen production candidate
physically computes the 8x8 Gram matrix of the eight positive source directions
for every frame and checks it against identity.

Per frame upper:

[
2dK^2+K^2.
]

All frames:

[
P(2dK^2+K^2)=33,046,272.
]

This explicitly bills the requested norm/orthogonality work.

### 6. Complete deep propagation

Frozen physical dense-layer convention:

[
2n^2+2n=2,099,200
]

per direction per square ReLU layer.

Thus:

[
NL(2n^2+2n)
=
135,423,590,400.
]

### 7. Final reduction and radial scaling

Conservative upper:

[
Nn+2N+5n
=
4,141,952.
]

### All-in production upper

[
70,000
+4,128,768
+790,272
+4,128,768
+33,046,272
+135,423,590,400
+4,141,952
=
oxed{135,469,896,432}.
]

Slack:

[
136,758,472,261-135,469,896,432
=
oxed{1,288,575,829}.
]

Protocol admission cost gate:

[
135,469,896,432\le136,758,472,261:
quad 	extbf{PASS}.
]

Any candidate operation class absent from this ledger is terminal accounting
failure. Verifier-only exact references and iid comparators are not candidate
production cost and must be reported separately.

## Frozen exact 8-D stress

Build four independent 2-D width-2/depth-4 zero-bias He-normal subnetworks with
seeds

[
125300,125301,125302,125303.
]

Assemble each layer block-diagonally into one 8-D width-8/depth-4 network.

Verifier-only exact Gaussian mean is the concatenation of four independent exact
2-D angular means. Candidate receives only the assembled dense weight matrices.

Candidate estimator seeds:

[
125400,125401,125402,125403.
]

Same-node iid spherical comparator seeds:

[
125500,125501,125502,125503.
]

Each estimate uses exactly (4032) propagated directions.

## Frozen exact 16-D stress

Build eight independent 2-D width-2/depth-4 zero-bias He-normal subnetworks with
seeds

[
125320,ldots,125327
]

and assemble one 16-D width-16/depth-4 block network.

Candidate seeds:

[
125600,125601,125602,125603.
]

Same-node iid comparator seeds:

[
125700,125701,125702,125703.
]

Again each estimate uses exactly (4032) propagated directions.

The 16-D stress ensures the algebraic 8-frame is a strict subspace frame rather
than a full ambient basis.

## Frozen scientific gates

After a successful immutable preflight, exactly one scientific workflow run is
authorized.

All gates must pass:

1. exact integer Clifford algebra and signed-permutation gates;
2. candidate outputs finite;
3. all sampled base-direction norm errors <= (2e-12);
4. all runtime 8-frame Gram errors <= (2e-12) in both 8-D and 16-D stresses;
5. deterministic replay is bitwise exact for predictions and exact for the
   operation ledger;
6. every realized candidate MSE is <= the corresponding pre-run
   (C_{m MSE}) certificate;
7. pooled 8-D candidate MSE / same-node iid pooled MSE <= (0.90);
8. pooled 16-D candidate MSE / same-node iid pooled MSE <= (0.90);
9. candidate source audit confirms no import/read/dependency on E122 candidate
   code or receipt, no simplex/Haar-Stiefel/Gram-Schmidt candidate path, no
   targets/reference access;
10. complete production all-in candidate upper equals the frozen ledger and is
    <= (136,758,472,261);
11. no public/public-mini/benchmark target/scorer/holdout/full access.

The raw (1.89e-8) competition scale may be reported diagnostically only and
cannot alter any frozen parameter or verdict.

Any failed gate gives:

**E125 TERMINAL NO-GO / CLOSE CLIFFORD-8 RATIONAL TIGHT-FRAME SOURCE CODE.**

If all gates pass:

**E125 LOCAL SCIENTIFIC GO — CERTIFIED CLIFFORD-8 MULTI-SOURCE ESTIMATOR.**

A local GO does not authorize production/benchmark execution or any claim of
competition accuracy.

## Immutable execution discipline

1. This protocol-only commit changes only `research/E125_PROTOCOL.md`.
2. Candidate implementation must be new E125 code; no E122 candidate import,
   copy, or wrapper.
3. Minimal tests and a preflight certificate executable may be committed only
   after this protocol commit.
4. Run the preflight only; it must not evaluate E125 source directions.
5. Commit the preflight certificate/ledger receipt before arming science.
6. Exactly one scientific GitHub Actions run after preflight PASS.
7. No rerun, seed change, operator change, source/frame count change, confidence
   budget change, ratio-gate change, precision change, fixture change, tuning,
   sweep, or rescue.
8. Seal one immutable result receipt with run/job/artifact/digest and explicit
   VERIFIED/UNEXECUTED classification.
9. No canonical/ledger mutation or merge.
