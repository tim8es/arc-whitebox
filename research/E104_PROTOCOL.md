# E104 Protocol — Haar-direction radial Rao–Blackwellization

Idempotency key: `ARC-E104-HAAR-RADIAL-RAOBLACKWELL-20260918`

Status: **PREREGISTERED / SYNTHETIC STAGE-A ONLY**.

## Provenance

- Direct canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Branch: `research/e104-haar-radial-raoblackwell-20260918`.
- Authoritative E100 orthogonal-Gaussian Stage-A:
  run `35286592051`, job `105420177508`, artifact `10525165155`;
  pooled orthogonal/iid MSE ratio `0.1883275202813626`, wins `8/8`.
- E100 independent marginal-law review:
  run `35286924532`, job `105421199103`, artifact `10524278137`; PASS.
- E103 production-shape package/cost validation:
  run `35287256818`, job `105422236549`, artifact `10525181002`;
  measured utilization `0.0677789313122048` at width/depth/N
  `1024/16/4096`.
- E003 radial marginalization is historical negative evidence, but it used an
  empirically whitened antithetic ensemble and paid extra whitening/norm cost,
  reducing its sample count. E104 has no whitening and changes only the random
  radii of E100 while holding its Haar directions and trajectory count fixed.

## Exact fixed-network theorem

For every bias-free ReLU MLP layer output `H_l` and every `r>=0`,

`H_l(r q) = r H_l(q)`

by positive homogeneity of linear maps and ReLU.

For `X~N(0,I_n)`, write `X=RQ`, where `Q` is uniform on the unit sphere,
`R~chi_n`, and `R` is independent of `Q`.

For one antithetic direction define

`A_l(q) = 0.5 * (H_l(q) + H_l(-q))`.

E100 with a Haar-row direction set `q_i` and independent Gaussian radii uses

`M_l = (1/m) sum_i R_i A_l(q_i)`.

Let

`mu_R = E[R] = sqrt(2) Gamma((n+1)/2) / Gamma(n/2)`.

E104 uses

`M_l^RB = (mu_R/m) sum_i A_l(q_i)`.

Conditioned on the complete Haar direction set,

`M_l^RB = E[M_l | q_1,...,q_m]`.

Therefore, for every fixed zero-bias network and every output coordinate,

- E104 is unbiased whenever E100 is unbiased;
- `Var(M_l^RB) <= Var(M_l)` by Rao–Blackwell;
- the difference is purely variance removal from the independent chi radii.

This proof is pre-code and does not use any target.

## Frozen Stage-A

Synthetic only:

- width `32`, depth `6`;
- He-Gaussian float32 weights;
- network seeds `104000..104007`;
- high-sample iid-antithetic reference: `65536` trajectories;
- reference seeds `404000..404007`;
- comparator/candidate trajectories: `2048`;
- common Haar direction seeds `204000..204007`;
- E100 random-radius comparator seeds `304000..304007`;
- E104 uses the exact analytic `mu_R`, no random radius;
- NumPy PCG64;
- float32 network propagation, float64 output reductions.

Within every network E100 comparator and E104 candidate use exactly the same
Haar directions. Only the radius rule differs.

## Required checks

Before MSE comparison, the script must verify:

1. positive homogeneity numerically on a deterministic fixed vector/radius with
   max relative error `<=2e-6`;
2. common E100/E104 directions are identical before radial scaling;
3. exact antithetic pairing;
4. all outputs finite;
5. deterministic full Stage-A repeat exactly at the scalar-signature level.

## Frozen scientific gates

All must pass:

1. finite outputs;
2. deterministic scalar-signature replay max abs `==0`;
3. homogeneity relative error `<=2e-6`;
4. aggregate `E104_MSE / E100_random_radius_MSE <=0.90`;
5. E104 beats E100 on at least `6/8` networks;
6. worst per-network E104/E100 ratio `<=1.25`;
7. conservative production utilization upper bound `<=0.12`.

For gate 7, E103's measured `0.0677789313122048` is a conservative inherited
upper bound because E104 keeps the same number of QR direction blocks and
network trajectories while removing per-direction chi-square draws and square
roots; it adds only one scalar analytic mean-radius constant.

Any failed gate => **TERMINAL NO-GO / DROP E104**. No seed/sample/rank change,
radius blending, partial marginalization, whitening, tuning, rerun, public
diagnostic, scorer, holdout/full, canonical mutation, or ledger mutation.

A pass is **LOCAL SCIENTIFIC GO FOR THE RADIAL RAO–BLACKWELL MECHANISM ONLY**.
It does not establish competition raw MSE `<=1.89e-8` and authorizes no public run.
