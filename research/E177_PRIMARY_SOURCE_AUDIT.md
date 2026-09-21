# E177 — primary-source audit: Phase-2 accuracy/cost frontier and AGO compatibility

Date: 2026-09-21  
Branch: `research/e177-primary-source-audit-20260921`  
Mode: **research-only; no estimator code, no benchmark run, no baseline mutation**

## Question

Audit the official ARC cumulant-propagation reference and the strongest inspectable
public Phase-2 implementations. Identify which mechanisms are actually evidenced
to buy accuracy or compute, which are compatible with AGO, and freeze exactly one
next experiment.

Project constraints for this audit:

- raw final-layer MSE target: `< 2.0e-8` (project stretch target remains `1.89e-8`);
- compute cap: `C/B <= 0.135`;
- Phase-2 budget: `B = 2^41 = 2,199,023,255,552` FLOPs;
- therefore `0.135 B = 296,868,139,499.52` FLOPs.

## Pinned sources

### ARC primary

1. Wu, Lecomte, Winer, Robinson, Hilton, Christiano,
   *Estimating the expected output of wide random MLPs more efficiently than sampling*,
   arXiv:2605.05179:
   https://arxiv.org/abs/2605.05179

2. Official ARC reference implementation:
   https://github.com/alignment-research-center/mlp_cumulant_propagation/tree/93d091a4c26c042bfffa28f2e76a81bc0aba94bb

   Audited blobs:
   - `README.md`: `0665357e37164f1896392fbbd4431a5a4e692871`
   - `src/mlp_kprop/factor_k3.py`: `ed7cddd91fcf3a744a02aacfba6f24f9f743c82a`
   - `src/mlp_kprop/wick.py`: `2947a40c33fac64441dbc5b180bfe6a865cca452`

3. ARC overview:
   https://www.alignment.org/blog/mechanistic-estimation-for-wide-random-mlps/

### Official Phase-2 harness / starter

Pinned starter kit:
https://github.com/AIcrowd/whest-starterkit/tree/5eb9aa1455fcb3216af55994bdf25dc242b95797

Audited:
- `examples/03_covariance_propagation.py` blob
  `675b3dd8f032f342112a99f431115b35f8481620`;
- Stage-3 public-mini documentation:
  `v2-phase2`, width 1024, depth 16, budget `2^41`, 100 Mini MLPs,
  baked `N=1e9` reference means.

The official example records:
- raw Mini final-layer MSE about `4.050e-6`;
- measured estimator FLOPs `51,709,240,799`;
- `C/B = 0.02351464027`.

### Strongest fully inspectable public Phase-2 K3 implementation

504aldo, pinned MIT release:
https://github.com/504aldo/whest-p2-cumulant-k3/tree/18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45

Forum write-up:
https://discourse.aicrowd.com/t/everything-we-tried-a-factorized-k-3-cumulant-propagation-estimator-at-0-25-x-b-where-its-flops-go-and-25-measured-dead-ends-team-504aldo-rank-10/18218

Audited public estimator:
- V29 blob `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`.

Independent local reproduction already recorded in E136:
- upstream V25/V29 blob identity preserved;
- same first-three public Mini MLPs: both raw `2.33e-8` to report precision;
- V25 mean `C/B ~= 0.36683`;
- V29 three-MLP mean `C/B ~= 0.25769`, consistent with the author's
  `0.2526` steady-state figure after first-predict warm-up.

### Current public frontier, but not an inspectable implementation

The 504aldo write-up records the then-current #1 as raw `1.71e-8` at
`C/B = 0.158`, and other leaders around `0.149-0.164 B`. This is useful
frontier evidence, **not source-code evidence**: the leader mechanism is not
publicly specified there.

At `0.158 B`, reaching this project's `0.135 B` cap still requires a
`14.56%` compute reduction even if raw accuracy is preserved.

## Audit result: there is no publicly verifiable joint winner at <2e-8 and <=0.135B

As of this audit, no inspectable public Phase-2 implementation verifies both
constraints simultaneously.

| evidence | raw final MSE | C/B | what it proves |
|---|---:|---:|---|
| official starter K2 gain covariance | ~`4.05e-6` | `0.0235` | cheap K1/K2 propagation, far from raw target |
| E173 AGO on the current local K2 parent, first 5 official Mini MLPs | `3.5017e-6` | measured `0.03145` | AGO transfers to official Phase-2 shape and improves all 5, but K2 is far from frontier |
| public 504aldo V29 | ~`2.13e-8` | `0.2526` | near-target raw from K3 + memoryless K4; misses both strict raw <2e-8 and cost cap |
| leaderboard frontier reported by 504aldo | `1.71-2.0e-8` | ~`0.145-0.16` | existence evidence for better hidden mechanisms; still not a verified <=0.135B public implementation |

Therefore the statement “component X is publicly demonstrated to give
raw <2e-8 at <=0.135B” is currently unsupported. The joint intersection is
empty in the sources above.

## What actually buys the public K3 accuracy

The 504aldo version ladder is unusually useful because it separates accuracy
changes from later cost engineering.

1. **Factorized quenched K3 with full off-diagonal source memory.**
   V16b is the K3-simple chain with an exact algebraic collapse from roughly
   seven to four dense units per source-layer. It reaches raw `4.46e-8`.
   The important content is not marginal skew alone: D3 and D21 are the
   nonlinear interface, but old fully off-diagonal K3 content is needed to
   regenerate future D21.

2. **Memoryless K4 regeneration is the largest disclosed raw-accuracy jump.**
   V17 regenerates the off-diagonal K4 core approximately as
   `G_off = lambda_l C_off` while keeping the K4 diagonal exact.
   Reported raw moves `4.46e-8 -> 2.26e-8` at essentially unchanged compute.

3. **D21 feedback into nonlinear births closes most of the remaining disclosed
   K3-chain gap.**
   V18 uses rank-16 feedback and reports raw `2.08e-8`.
   Increasing the feedback rank is not the missing mechanism: the public
   ablation reports rank 32 as score-negative.

4. **Final-layer exact trimming is a cost-only identity.**
   At the last layer only the final mean is required, so full D21/full
   covariance work can be skipped there without changing the arithmetic
   needed for the answer.

5. **Age-shared old-source subspaces and Strassen-Winograd are cost mechanisms,
   not raw mechanisms.**
   V22/V24 compress old source legs into shared/nested bases; V26-V29 compute
   the same arithmetic with progressively cheaper matrix multiplication and
   buffer reuse. Raw remains around `2.1e-8`.

The decisive negative cost fact is F86: V29 without its entire old-source tier
is still about `153` units = `0.1496 B`, already above this project's
`0.135 B` cap. Consequently, “compress only V29 old sources” cannot meet the
cap even at zero old-tier cost.

The decisive negative accuracy fact is also public: the author estimates the
float64 ceiling of “K3 + memoryless K4” around `1.94e-8` on leaderboard scale,
while the reported leader is `1.71e-8`. The public evidence therefore points
to **non-memoryless fourth-order information plus persistent old-source
dependence** as the missing accuracy content. The representation carrying that
content at leader cost is not public.

## AGO compatibility audit

AGO evidence used here is local and immutable, not a claim about public leader
code:

- E164: exact K1/K2 Gaussian-to-angular gauge after first activation plus exact
  final radial readout; pooled synthetic AGO/parent MSE ratio
  `0.6661376209`; analytic all-in upper `0.0509915352 B`.
- E171/E172: production-shaped 1024x16 three-seed evidence, independently
  verified; pooled AGO/parent ratio `0.8469174380`.
- E173: first five official public Mini MLPs, AGO improves all five;
  mean parent `4.21111572e-6`, AGO `3.50171695e-6`, ratio
  `0.831541373`; measured mean compute `69,159,064,030` FLOPs
  = `0.0314499012 B`.

Compatibility classification:

| component | AGO compatibility | reason |
|---|---|---|
| zero-bias positive homogeneity / exact final radial factor | **exactly compatible** | this is the identity AGO exploits |
| K1/K2 mean + covariance propagation | **demonstrated** | E164/E171/E173 |
| float32, symmetry tags, Strassen/buffer cost engineering | **structurally compatible** | arithmetic implementation choice; does not define the probability gauge |
| exact last-layer trim | **structurally compatible** | output dependency identity, independent of gauge |
| full K3 source transport / D3 / D21 | **not yet demonstrated** | current AGO implementation has no K3 state; K3 must be transformed consistently, not left in the Gaussian gauge |
| memoryless K4 regeneration `G_off=lambda C_off` | **not safely portable as-is** | its fitted/empirical lambda law was measured in the original V29 state gauge; changing K1/K2 gauge without re-deriving K4 is not an exact transformation |
| rank-16 D21 birth feedback | **conditionally compatible** | only after a correct higher-order AGO transformation establishes D21 in the same gauge |
| V29 age-shared source bases | **conditionally compatible** | linear subspace machinery can transport a re-gauged K3 state, but no evidence says the same frozen ranks retain error after re-gauging |

The important firewall is therefore: **do not bolt E164 AGO onto V29 by changing
only mean/covariance and leaving K3/K4 untouched.** That mixes incompatible
moment gauges and would not be a valid test.

## Exactly one next hypothesis

### H177 — higher-order AGO gauge on the public K3-simple chain

Extend AGO from K1/K2 to a mathematically consistent angular gauge through the
third cumulant and the K4 quantities actually consumed by the K3-simple
nonlinearity, using exact radial moments from positive homogeneity. Then run
the **unchanged public K3-simple + memoryless-K4 closure** in that gauge and
convert only the recorded output means back with the exact radial factor.

No source dropping, new low-rank carrier, rank sweep, lambda refit, output
calibration, sampling correction, or new K4 model is part of H177.

Why this is the single highest-information next experiment:

- V29 is only `6.10%` above raw `2.0e-8` and `12.68%` above the project's
  `1.89e-8` target.
- AGO has repeatedly produced a much larger relative MSE reduction on K2:
  `15.3%` on the production-shaped three-seed panel and `16.85%` on the
  first-five official Mini panel.
- the test attacks the remaining **closure bias**, not V29's already-mapped
  matrix-multiplication engineering;
- it is orthogonal to Strassen/buffer optimization and therefore, if it works,
  can be carried into any future cost-admissible K3/K4 representation;
- it resolves the key compatibility uncertainty before spending another lane
  on a new high-order carrier.

This is a hypothesis, not an extrapolated score claim. K2 AGO gains need not
transfer to K3/K4.

## Protocol sketch for the successor experiment

No execution is authorized by E177.

1. **Protocol-only freeze.**
   Pin ARC reference commit
   `93d091a4c26c042bfffa28f2e76a81bc0aba94bb`, public 504aldo commit
   `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`, and the byte-identical E164
   AGO implementation. Freeze one H177 formula before any target-bearing run.

2. **Exact-small algebra gate, target-free.**
   On width <=8, depth <=4 synthetic zero-bias networks, materialize exact
   raw moments/cumulants through order 4 and verify the Gaussian<->angular
   radial transformation and inverse to <=`1e-12` float64. Verify D3/D21 and
   every K4 slice consumed by the closure after round-trip. Failure is terminal.

3. **One closure falsifier, still target-free.**
   Compare original K3-simple closure versus H177 on frozen synthetic networks
   against an exact angular/quadrature reference. No fitted lambda/rank change.
   Require deterministic replay and a predeclared pooled MSE improvement.

4. **Cost gate.**
   Charge all higher-order gauge work. The gauge itself must be
   `O(n^2)` per application and add <`0.002 B`; an `O(n^3)` gauge is
   terminal because it cannot be a reusable overlay.

5. **Only if exact-small GO, separately authorize a bounded public-mini
   parent-vs-H177 accuracy check.**
   Reuse identical MLPs and immutable target vectors; no tuning on the result.

6. **Interpretation.**
   H177 GO would establish a plausible raw-accuracy bridge to the leader class.
   It would **not** solve the `0.135 B` production problem: public V29 remains
   far too expensive. A later carrier experiment would still be required, but
   only after H177 shows that AGO survives the high-order closure.

## Decision

**E177 audit conclusion: NO PUBLICLY VERIFIED METHOD CURRENTLY SATISFIES BOTH
RAW <2e-8 AND C/B <=0.135.**

The strongest inspectable public accuracy mechanism is K3 source memory +
memoryless K4 regeneration + D21 feedback, but its V29 implementation costs
~`0.2526 B` and its disclosed closure sits around `2.1e-8` raw. The
leaderboard demonstrates that lower raw and lower cost are possible, but its
key representation is not publicly inspectable.

The one next experiment frozen by this audit is **H177 higher-order AGO gauge
on the unchanged public K3-simple closure**. Its purpose is to determine
whether AGO's measured K2 bias reduction survives the K3/K4 frontier before
any further representation work.

No code was run, no benchmark was executed, no baseline/canonical/ledger file
was changed, and no submission was made.
