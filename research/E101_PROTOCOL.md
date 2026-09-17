# E101 — multi-latent skew-rank lower bound

Idempotency key: `ARC-E101-MULTILATENT-SKEW-RANK-BOUND-20260918`

Status: **PREREGISTERED / ANALYTIC FALSIFIER ONLY**.

## Provenance and non-duplication

- Branch: `research/e101-multilatent-skew-rank-bound-20260918`.
- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- E099 is terminal structural NO-GO for one shared binary latent at `pi=0.1`; E101 does not alter or rerun E099.
- E100 is occupied by independent shrinkage/antithetic lanes and is not reused.
- E101 asks a strictly broader structural question: can replacing E099's single shared latent by a **small number m of independent standardized binary latent factors** remove the covariance PSD obstruction while keeping an exact finite Gaussian-mixture closure compact?
- No public/public-mini, scorer, benchmark holdout/full labels, tuning, sweep, canonical mutation, or ledger mutation.

## Frozen model class

At a hidden layer represent

[
X = mu + D S + arepsilon,
]

where:

- (Dinmathbb R^{n	imes m});
- (S=(S_1,ldots,S_m)) has independent identically distributed standardized two-point components;
- each component uses the E099 frozen weight (pi=0.1),
  (a_+=sqrt{(1-pi)/pi}=3),
  (a_-=-sqrt{pi/(1-pi)}=-1/3);
- therefore (E[S_a]=0), (E[S_a^2]=1), and (m_3=E[S_a^3]=8/3);
- (arepsilonsim N(0,Sigma_0)), independent of (S), with (Sigma_0succeq0).

This is the natural finite-rank independent-latent extension of E099. The latent law and (pi) are fixed; no fitted mixture weights, width-dependent weights, correlated latent law, or continuous latent distribution are allowed under E101.

## Exact first-layer target

Use only the analytic first-layer law

[
H_i=operatorname{ReLU}(Z_i),qquad Z_istackrel{iid}{sim}N(0,1).
]

Exact scalar moments:

[
mu_H=rac1{sqrt{2pi}},
]

[
v=operatorname{Var}(H_i)=rac12-mu_H^2,
]

[
kappa_3=
sqrt{rac2pi}-rac32mu_H+2mu_H^3.
]

Coordinates are independent, so the exact covariance is (vI_n), while every marginal has third cumulant (kappa_3>0).

For row (d_iinmathbb R^m) of (D), independence of the latent factors gives

[
kappa_3(H_i)=m_3sum_{a=1}^m d_{ia}^3.
]

Exact marginal skew matching therefore requires

[
sum_a d_{ia}^3=c,qquad c=kappa_3/m_3.
]

## Frozen lower bound

For every row,

[
c=left|sum_a d_{ia}^3ight|
lesum_a|d_{ia}|^3
=|d_i|_3^3
le|d_i|_2^3,
]

hence

[
|d_i|_2^2ge c^{2/3}.
]

Therefore

[
operatorname{tr}(DD^	op)=sum_i|d_i|_2^2
ge n c^{2/3}.
]

Exact covariance matching requires

[
Sigma_0=vI_n-DD^	opsucceq0,
]

so

[
lambda_{max}(DD^	op)le v.
]

Since (operatorname{rank}(DD^	op)le m),

[
operatorname{tr}(DD^	op)
le m,lambda_{max}(DD^	op)
le mv.
]

Combining both inequalities gives the necessary latent-rank bound

[
oxed{mge rac{n c^{2/3}}{v}}.
]

At the official width (n=1024), E101 freezes this exact calculation before execution.

## Explicit-mixture state implication

With (m) independent two-point factors, an exact component-wise Gaussian-mixture nonlinear update has (2^m) latent states. E101 does **not** claim that every conceivable approximation must enumerate these states. It tests the exact finite-mixture mechanism class only.

Thus two necessary compactness gates are frozen:

1. **low-rank gate:** exact first-layer moment matching must permit (mle64);
2. **explicit-state gate:** exact component enumeration must require at most (2^{64}) states.

Either gate failing is sufficient to close the proposed compact exact multi-latent mixture class. The generous threshold 64 is fixed before the calculation and is far above the 1–16 dimensional latent structures that would normally be considered compact.

## One local analytic falsifier

Run exactly one deterministic Python calculation at:

- width (n=1024);
- (pi=0.1);
- float64;
- no random inputs;
- no benchmark/public data.

It must record:

- (mu_H,v,kappa_3,m_3,c,c^{2/3});
- real-valued rank lower bound and integer ceiling;
- (2^{m_{min}}) as a symbolic decimal-log magnitude rather than materializing states;
- the E099 (m=1) minimum-eigenvalue as a cross-check;
- deterministic repeat equality;
- finite values.

## Frozen gates and terminal rule

All integrity gates must pass:

- analytic moments finite;
- latent mean/variance identities agree to (1e-15);
- E099 (m=1) cross-check agrees with (-252.126983267117) to (1e-9);
- deterministic repeat max abs (=0).

Scientific GO requires **both**:

- (m_{min}le64);
- explicit mixture state exponent (m_{min}le64).

If either scientific gate fails, E101 is **TERMINAL ANALYTIC NO-GO / DROP**. No changing (pi), correlated latent factors, nonbinary factors, approximation, rank threshold, width, rerun, rescue, or public diagnostic is allowed under E101. Such mechanisms require a new experiment ID.

## Interpretation boundary

A NO-GO here closes only the compact **exact independent binary multi-latent Gaussian-mixture** extension of E099. It does not rule out moment-only closures, continuous latent laws, correlated structured latents, or approximate quadrature mechanisms.
