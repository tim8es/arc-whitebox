# E117 protocol — rigorous Lipschitz–Schur low-rank remainder certificate

Idempotency key: ARC-E117-LIPSCHITZ-SCHUR-CERTIFIED-TAIL-20260919

Status: PREREGISTERED / PROOF-ONLY / NO HEURISTIC ACCURACY CLAIM.

## Identity / occupancy

The requested E114 identity is already occupied and sealed by
research/e114-activation-boundary-flux-20260919. E115 and E116 are also occupied.
This proof-only, non-duplicative lane therefore uses E117.

Branch:
research/e117-lipschitz-schur-certified-tail-20260919

Parent:
E113 terminal receipt commit d69dd21677dfa4f82eaaca45a5611c32804ee9a0.

No public/public-mini, benchmark targets, scorer, holdout/full, tuning, sweep,
rescue, rerun, canonical/ledger mutation, or merge.

## Candidate class

Output-specific low-rank / Schur compression with a rigorous deterministic
remainder certificate.

At a hidden layer let h have mean m and centered second moment

    Sigma = E[(h-m)(h-m)^T].

Choose any rank-r orthogonal projector P and preserve the mean exactly:

    h_hat = m + P(h-m).

Let f_j be one scalar final output coordinate of the downstream suffix.
If f_j is L_j-Lipschitz in Euclidean norm, then

    |E f_j(h) - E f_j(h_hat)|^2
      <= E |f_j(h)-f_j(h_hat)|^2
      <= L_j^2 E ||(I-P)(h-m)||_2^2
      =  L_j^2 tr((I-P) Sigma).

For fixed rank r, Ky Fan's theorem gives the optimal orthogonal projector:

    min_rank(P)=r tr((I-P) Sigma)
      = sum_{k=r+1}^n lambda_k(Sigma),

with eigenvalues ordered descending.

Thus the best certificate available to this family is

    C_{j,r} = L_j^2 sum_{k=r+1}^n lambda_k(Sigma).

For vector output mean MSE, averaging the coordinate certificates gives

    C_r = (1/n) sum_j C_{j,r}.

A rank-r candidate can be admitted only if C_r <= 1.89e-8.

This is a rigorous sufficient-error certificate. Failure means the frozen
certificate family cannot certify the requested accuracy; it does not claim
that every possible uncertified approximation has large true error.

## Frozen analytic fixture

Depth 4, width 8, zero bias.

Input:
    X ~ N(0,I_8).

Layer 1:
    W1 = I_8,
    h = ReLU(X).

Therefore coordinates of h are independent half-rectified standard normals,

    E[h_i] = 1/sqrt(2*pi),
    Var(h_i) = v = 1/2 - 1/(2*pi),

and hence exactly

    Sigma = v I_8.

Suffix layers 2..4 use the normalized Sylvester Hadamard matrix

    H8 / sqrt(8)

for every weight matrix, followed by ReLU.

Each suffix weight has exact spectral norm 1 and ReLU is 1-Lipschitz, so every
final scalar coordinate has the rigorous global bound

    L_j <= 1.

The frozen certificate intentionally uses L_j=1. No data-dependent tightening,
activation-mask specialization, or observed-gradient fitting is permitted.

Because Sigma is isotropic,

    C_r = v (8-r)

for every rank-r orthogonal projector, including any output-specific choice.

The strongest nontrivial compression is r=7, for which

    C_7 = v = 1/2 - 1/(2*pi).

This is an exact symbolic expression.

## Frozen gates

The executable must verify:

1. normalized Hadamard orthogonality to <=1e-15 in float64;
2. suffix spectral norms equal 1 to <=1e-15;
3. exact scalar v = 1/2 - 1/(2*pi) is finite and positive;
4. certificates C_r = v(8-r) are strictly decreasing for r=0..8;
5. C_8 = 0;
6. min_{r<=7} C_r = C_7;
7. deterministic replay max_abs = 0;
8. no external/target access.

Admission gate:

    min_{r<=7} C_r <= 1.89e-8.

If false, record:

    TERMINAL CERTIFICATE NO-GO

for rank-reducing Lipschitz–Schur compression under this frozen rigorous
remainder bound.

No rank-dependent empirical calibration, alternative norm, learned metric,
mask-conditioned Lipschitz constant, signed cancellation assumption, seed
change, suffix change, or rescue under E117.

## Production interpretation

If the only certifiable rank is r=n, there is no low-rank compression.
A full-rank projection adds work and cannot be the intended production
compression mechanism.

No production-shaped prototype is authorized after a terminal certificate
NO-GO.
