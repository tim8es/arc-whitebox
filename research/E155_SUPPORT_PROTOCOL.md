# E155 SUPPORT PROTOCOL — AIK4-1 one-birth falsifier

Status: **SUPPORT PROTOCOL ONLY / OWNER NOT FROZEN / EXECUTION FORBIDDEN**  
Date: 2026-09-21  
Support id: `ARC-E155-AIK4-1-SUPPORT-20260921`

This file specifies the smallest admissible falsifier for the clean-room AIK4-1
hypothesis. It is not an execution arm. A separate owner must freeze the exact
parent commit, parent cost receipt, implementation blobs, fixture generator, and
owner protocol before any run exists.

## Hypothesis

AIK4-1 keeps the exact angular input K4 only through the first linear step and the
first nonlinear K1/K2/K3 birth, then drops K4 entirely.

The hypothesis is that this exact one-birth source can improve the error of a
budget-admissible deterministic parent without the unsupported recurrent scalar-K4
projection used by the public Phase-2 implementation.

## Hard firewall

Allowed:
- synthetic zero-bias ReLU MLP weights from the frozen owner seeds below;
- analytic Gaussian radial/angular identities;
- official ARC Wick coefficients/equations pinned in
  `E155_PRIMARY_SOURCE_SUPPORT.md`;
- dense K4 materialization **only in the small verifier fixtures**;
- deterministic analytic 2D activation-sector integration as an exact synthetic
  reference, implemented clean-room.

Forbidden:
- public Phase-2 targets or labels;
- public mini targets;
- scorer, holdout, full suite, submission;
- benchmark-target fitting or post-result fitting;
- sampling or sampling control variates;
- E151 code, workflow, artifacts, reruns, Strassen transfer, or rescue;
- recurrent scalar `c4` after the first nonlinearity;
- K3 rank/basis/TT/CountSketch/MUB repair;
- seed/rank/threshold sweep;
- rescue after a failed frozen run.

## Owner-freeze prerequisites

Before an execution arm may be committed, the owner must freeze all of:

1. one deterministic parent estimator commit and implementation blob hashes;
2. a target-free parent cost receipt;
3. proof that the parent already computes the first-layer
   (M=W_0W_0^T), so AIK4-1 adds no Gram GEMM;
4. parent all-in cost no larger than `0.1349904166907072 * 2^41` FLOPs,
   unless a tighter complete overlay accounting proves combined cost <=
   `0.135 * 2^41`;
5. exact AIK4-1 implementation blobs;
6. exact fixture-generation blobs and the one-shot run arm.

If any prerequisite is unavailable, status is
`E155_AUDIT_NO_GO_PENDING_OWNER_FREEZE`; do not execute.

## Frozen mathematical candidate

For input dimension (n):
[
kappa=-2/(n+2),qquad
a_1=sqrt{2/n},Gamma((n+1)/2)/Gamma(n/2).
]

At the first preactivation:
[
M=W_0W_0^T,
]
[
K4_{abcd}=kappa(M_{ab}M_{cd}+M_{ac}M_{bd}+M_{ad}M_{bc}),
]
[
D4_i=3kappa M_{ii}^2,
qquad
D22_{ij}=kappa(M_{ii}M_{jj}+2M_{ij}^2).
]

The exact ARC-style selected K4 power-moment terms are frozen as
[
Delta P_{p,i}=rac1{24}w_{4,p,i}D4_i,quad p=1,2,3,4,
]
[
Delta P_{11,ij}
=rac14,w_{2,1,i}w_{2,1,j}D22_{ij},
]
[
Delta P_{21,ij}
=rac14,w_{2,2,i}w_{2,1,j}D22_{ij}.
]

Here (w_{k,p}=E[partial^k operatorname{ReLU}(Z)^p]) is exactly the official
ARC `relu_wick_coef` convention evaluated at the parent's matching Gaussian
mean/variance.

The parent performs its ordinary moment-to-cumulant conversion and K1/K2/K3 birth
using these augmented first-layer power moments. Immediately after that conversion,
AIK4-1 destroys the K4 carrier. All later layers are byte-for-byte the owner-frozen
parent arithmetic except for the angular state already induced at layer 0.

Final output is multiplied by the exact radial factor (a_1(n)).

No recurrent K4 state or scalar is permitted.

## Frozen target-free fixtures for the future owner run

One run contains all three fixtures and one deterministic replay inside the same
process.

### F0 — exact2d/depth8

- square width/input dimension: 2;
- depth: 8;
- zero bias;
- deterministic dense Gaussian weights;
- seed: `155002`;
- float64 verifier arithmetic.

The exact Gaussian final mean is computed by clean-room activation-sector
enumeration on the circle. On each sector the zero-bias ReLU network is linear in
((cos	heta,sin	heta)); integrate each sector analytically, then multiply the
unit-circle mean by (E[chi_2]).

This reference is synthetic and target-free.

### F1 — dense16/depth8

- width/input dimension: 16;
- depth: 8;
- zero bias;
- seed: `155016`;
- dense exact layer-0 K4 materialization is verifier-only.

### F2 — dense32/depth8

- width/input dimension: 32;
- depth: 8;
- zero bias;
- seed: `155032`;
- dense exact layer-0 K4 materialization is verifier-only.

F1/F2 are identity/cost fixtures, not benchmark-error fixtures.

## Mandatory gates

All gates must pass in the sole owner-frozen run.

1. **Source firewall** — no benchmark/public target/reference path is opened.
2. **Radial homogeneity** — for frozen nonzero probes,
   [
   f(x)=|x|/sqrt n; f(sqrt n,x/|x|)
   ]
   with max relative error <= `2e-12`.
3. **Angular K4 dense identity** — analytic K4 versus direct sphere fourth-moment
   formula, relative Frobenius error <= `2e-12` on F0/F1/F2.
4. **ARC factor-carrier identity** — dense K4 versus
   `Sym(M tensor 3*kappa*M)`, relative Frobenius error <= `2e-12`.
5. **D4 parity** — carrier readout versus dense K4 diagonal, max relative error
   <= `2e-12`.
6. **D22 parity** — carrier readout versus dense K4 `iijj` slice, max relative
   error <= `2e-12`.
7. **Selected Wick-term parity** — the frozen `Delta P_p`, `Delta P_11`,
   and `Delta P_21` formulas versus direct dense-K4 contractions, max relative
   error <= `2e-12`.
8. **No recurrence** — after the first nonlinear conversion there is no K4/c4
   state, K4 transport, or K4-derived later-layer arithmetic.
9. **Exact-small scientific gate** — on F0, final-mean MSE against the analytic
   Gaussian sector reference must satisfy
   [
   MSE_{m AIK4-1}le0.98,MSE_{m parent}.
   ]
   Parent and candidate must use identical frozen arithmetic except the AIK4-1
   overlay.
10. **Deterministic replay** — parent and candidate output arrays, gate metrics,
    and cost ledger are bitwise identical on the in-process replay.
11. **Complete production cost** — include parent plus every AIK4-1 operation,
    allocation-relevant billed arithmetic, Wick evaluation, conversion, and
    bookkeeping. Combined production cost must be <= `0.135 * 2^41` FLOPs.
12. **No sweep/rescue** — exactly one owner-frozen run.

The conservative pre-run overlay allowance is
[
20n^2+100n.
]
At production width 1024 this is `21,073,920` FLOPs, or
`9.583309292793274e-6 * 2^41`.

## Decision rule

- Any failed mandatory gate:
  `E155_TERMINAL_NO_GO_AIK4_1`.
- All gates pass:
  `E155_TARGET_FREE_SCIENTIFIC_GO_AIK4_1`.

A GO is still not permission for a public target, scorer, holdout, full suite, or
submission. It only authorizes verifier handoff under a separate instruction.

## Current state

[
oxed{	ext{SUPPORT PROTOCOL WRITTEN; OWNER NOT FROZEN; ZERO RUNS AUTHORIZED}}
]

Do not create an execution workflow or run arm from this support branch.
