# E181 PROTOCOL — H180 aggregate symmetric-CP carrier

Date: 2026-09-21  
Branch: `research/e181-h180-symmetric-cp-carrier-20260921`  
Clean base: E136 public V29 reproduction commit `dff3dd65e9d2210e02418cca99e05556f6bf2c75`  
Hypothesis source: E180 desk-research commit `805d11f8d59d9a502aab8b5bbf935d2f865fecea`, `research/E180_COST_WALL_CP_RESEARCH.md`.

## 0. Firewall

E181 is a new owner-run. E178 code, artifacts, vectors, receipts and implementation are forbidden inputs and are not scientific ancestry. No E178 rerun or repair is permitted.

Forbidden in E181: rank sweep, projection rescue, source-age hybrid, AGO, fitted coefficients, target-informed projection, public submission, scorer, leaderboard mutation, baseline/ledger mutation.

Exactly one H180 candidate and exactly one armed target-free falsifier run are allowed.

## 1. Official K3 representation and H180

Wu et al., *Estimating the expected output of wide random MLPs more efficiently than sampling*, arXiv:2605.05179, Eq. 15 / S.4.3, represents a symmetric third-order tensor by a symmetrized rank-O(n) factorization. The official ARC implementation commit pinned by E180 is
`alignment-research-center/mlp_cumulant_propagation@93d091a4c26c042bfffa28f2e76a81bc0aba94bb`, notably `src/mlp_kprop/factor_k3.py` and `FactoredTensor.contract_W/get_dslice/from_dstensor`.

H180 fixes one symmetric CP/Waring carrier:
[
T = \sum_{q=1}^{R} \lambda_q u_q^{\otimes 3},\qquad R=3n.
]

The required repeated-index slices are
[
D3_i=\sum_q\lambda_q u_{iq}^3,
\qquad
D21_{ic}=\sum_q\lambda_q u_{iq}^2u_{cq}.
]

A linear layer transports factors exactly by `u_q -> W u_q`.

## 2. One fixed projection rule

No fitting or reference-informed optimization is allowed. At each aggregate merge, candidate state contains the inherited CP components plus the deterministic newborn symmetric rank-1 components supplied by the synthetic falsifier.

If component count exceeds `R=3n`, compute only
[
s_q = |\lambda_q|\|u_q\|_2^3
]
from candidate state, retain the largest R components, and preserve their original `lambda,u` unchanged. Ties use original component index.

This fixed top-energy truncation is the sole reprojection rule. No alternate rank or rescue projection may be attempted after results are visible.

## 3. Exact-small identity gates

Before any D21 quality result is accepted:

1. **Carrier slice identity:** for deterministic small `n,r`, materialize dense `T` and require direct-CP D3 and D21 to equal dense `T[i,i,i]` and `T[i,i,c]`.
2. **Linear transport identity:** require dense `T x_1 W x_2 W x_3 W` to equal the CP tensor made from `WU`.
3. **Round-trip identity:** use an orthogonal W and require transport by W then `W.T` to reconstruct D3/D21.
4. All identity relative RMS errors must be finite and <= `1e-12`.

Any failure is terminal NO-GO; no target/reference MSE stage is run.

## 4. Single target-free structural falsifier

Pinned deterministic synthetic fixture:

- `n_small=24`, hence `R_small=72=3n`;
- depth 16;
- each layer contributes `n_small` newborn symmetric rank-1 K3 components;
- weights and births are generated only from committed integer seeds;
- the exact parent carries every component; the candidate applies the fixed top-energy truncation after each merge;
- identical linear transports are applied to parent and candidate;
- no benchmark targets, public labels, fitted constants or post-result parameter changes are inputs.

For each non-final layer, compare candidate and exact-parent D21. Freeze
[
e_{21}=\sqrt{\sum (D21_c-D21_p)^2/\sum D21_p^2}.
]

**D21 gate:** maximum non-final-layer `e21 <= 0.015`.

Also record D3 relative RMS, finite checks and SHA256 hashes of all saved parent/candidate structural vectors.

Failure is terminal and suppresses the MSE/SE reference stage by protocol.

## 5. Production all-in FLOP gate

Production shape is frozen to `n=1024`, `R=3072`, depth 16 and F86 unit
`u=2*n^3=2^31` FLOPs. Budget `B=2^41=1024u`.

Count:

- 15 CP linear transports: `15*3u = 45u`;
- 14 full D21 extractions: `14*3u = 42u`;
- frozen conservative V29 non-young remainder from E180: `37.6u`;
- projection bookkeeping for each merge: factor-norm scoring `2*n*(R+n)` FLOPs plus deterministic selection comparisons, all charged explicitly by the script.

Required simultaneously:

- `C_candidate/B <= 0.135`;
- `153.0u - C_candidate >= 14.76u`.

Any failure is terminal COST NO-GO.

## 6. Accuracy gate, only if structural and cost gates pass

Only after exact-small, D21 and cost gates pass may the one armed run expose a pinned local/public-mini reference and calculate paired parent/candidate final MSE and SE.

Required:
- `mean(MSE_candidate)/mean(MSE_parent) <= 1.02`;
- one-sided 95% upper confidence bound of paired relative degradation <= +2%.

If a prior fail-fast gate fails, MSE/SE fields in the terminal receipt must be explicit `not_run_due_to_<gate>`, not fabricated.

## 7. Evidence and immutability

The armed workflow must emit:

- exact-small metrics;
- D3/D21 per-layer metrics;
- production FLOP ledger;
- immutable `.npy` vectors for structural parent/candidate D3/D21;
- `manifest.json` with SHA256 for every evidence file;
- deterministic replay command and replay hash comparison;
- terminal receipt with GO/NO-GO and exact first failing gate.

The workflow is armed by exactly one committed `research/E181_RUN_ARM.json` file. No second arm is authorized.
