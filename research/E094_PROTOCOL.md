# E094 Protocol — source-axis joint compression across young + old K3 families

## Provenance

- Canonical parent: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.
- Branch: `research/e094-source-axis-joint-compression-20260917`.
- E091 is not a production candidate: its production-base screen found no measured base below the required utilization ceiling.
- E092 and E093 are occupied by independent lanes and are not modified or reused as experiment state.
- No public, scorer, holdout, full-suite, canonical, or ledger mutation is authorized in E094 Stage A.

## Motivation from measured V29 cost

Pinned upstream V29 family ledger on width=1024, depth=16, steady state:

- total: 260.1 dense-matmul units = 0.2540 x `2**41`;
- young transport: 60.71 units;
- young hub: 54.90 units;
- old shared-basis family: 106.83 units;
- thin/elementwise: 24.78 units;
- covariance: 7.10 units;
- birth/closure: 5.71 units.

The target utilization `<=0.135` is `<=138.24` units. Even deleting the entire old family would leave about 153.27 units, and deleting the entire young family would leave about 144.49 units. Therefore any single-family prune is analytically insufficient on the measured ledger. A viable representation must reduce both source-heavy families or create an equivalent cross-family fusion.

## Single hypothesis

The expensive K3 state has a small **source-axis numerical rank**, distinct from the spatial column rank already explored by V21-V24/E052-E053 and from capped spatial hub atoms (F76).

For source matrices `A_s, P_s` (and their left/hub partners), stack source index first. If a joint source-axis factorization exists

`A_s = sum_a C[s,a] Ahat_a`, `P_s = sum_a C[s,a] Phat_a`

with source rank `rho << S`, then the common transport is linear:

`W A_s = sum_a C[s,a] (W Ahat_a)`, `W P_s = sum_a C[s,a] (W Phat_a)`.

Thus transport requires `2*rho` dense products instead of `2*S` before reconstruction in source space.

For a bilinear hub sum of the generic form

`H = sum_s gamma_s L_s R_s^T`,

with `L_s=sum_a C_L[s,a] Lhat_a` and `R_s=sum_b C_R[s,b] Rhat_b`, define

`M = C_L^T diag(gamma) C_R`.

Factor `M = U diag(sigma) V^T`. Then

`H = sum_t sigma_t (sum_a U[a,t] Lhat_a) (sum_b V[b,t] Rhat_b)^T`.

Therefore the number of dense hub contractions is `rank(M) <= min(rho_L,rho_R,S)`, not `S` or `rho_L*rho_R`. The same source-metric factorization is applicable to old shared-basis source sums, so this is a cross-family representation rather than an old-tier prune.

## Stage A research questions

Stage A is synthetic/local only and answers three falsifiable questions:

1. **Algebra gate:** does the source-metric factorization reproduce direct transport and direct bilinear source sums to float64 tolerance when the source stack is exactly low-rank?
2. **Stability/error gate:** for a deterministic near-low-rank source stack, does truncation error track the discarded source-axis singular energy without numerical pathologies?
3. **Cost-necessity gate:** using the measured V29 ledger, what joint compression fractions of young and old source-heavy families are mathematically necessary to cross 0.135 utilization after leaving all non-source families unchanged?

Stage A does not claim that real V29 states have the required source-axis rank. It establishes whether the representation is algebraically sound and what compression ratio a later state-spectrum probe must demonstrate before production integration is worth coding.

## Frozen synthetic falsifier

- NumPy PCG64 seed: `94094`.
- dtype: float64.
- matrix width: `n=48`.
- source count: `S=12` (large enough to test both young-like and old-like source stacks).
- exact latent source rank: `rho=3`.
- left/right latent basis matrices: independent deterministic Gaussian matrices scaled by `1/sqrt(n)`.
- source coefficient matrices: deterministic Gaussian, shape `(S,rho)`.
- source weights `gamma`: deterministic signed values in `[0.5,1.5]` with alternating sign, to prevent a positivity-only shortcut.
- near-low-rank perturbation levels: `eps in {1e-6, 1e-4, 1e-2}` relative RMS.
- no benchmark/public data, targets, fitted constants, or estimator outputs.

## Frozen gates

### Algebra gates

All must pass:

- exact-rank transport reconstruction max abs error `<=1e-11`;
- exact-rank bilinear hub reconstruction max abs error `<=1e-10`;
- exact-rank bilinear relative Frobenius error `<=1e-11`;
- signed source weights are actually mixed (`min(gamma)<0<max(gamma)` after alternating sign construction);
- all arrays finite.

### Truncation gates

For each frozen perturbation level, compute the optimal joint source-axis SVD of the concatenated flattened source legs and truncate to `rho=3`.

- measured joint-stack relative Frobenius error must be no larger than `1.05 *` the Eckart-Young discarded-energy prediction (numerical tolerance only);
- direct-vs-compressed transport relative error must be `<= 4 *` joint-stack relative error;
- direct-vs-compressed bilinear hub relative error must be `<= 12 *` joint-stack relative error;
- errors must be monotone nondecreasing with perturbation level.

These are representation/stability gates only, not competition accuracy gates.

### Cost-necessity gates

Use the measured V29 units frozen above. Let `fy` and `fo` be remaining fractions of young and old source-heavy cost after source-axis compression. Conservative projected units:

`C = 37.59 + 115.61*fy + 106.83*fo`.

- report the symmetric required fraction `f*` where `fy=fo=f*` and `C=138.24`;
- report required young fraction if old is compressed to `fo=0.5`;
- report required old fraction if young is compressed to `fy=0.5`;
- Stage A is worth a real-state spectrum probe only if the symmetric requirement is `f* >= 0.40` (i.e. the method need not achieve an implausible >60% reduction in both families merely to reach the cost gate).

## Decision

- `STAGE_A_GO`: algebra + truncation + cost-necessity gates all pass. Next action is one **synthetic official-shape V29 state-spectrum probe** that instruments source-axis Gram spectra without changing predictions. Public remains forbidden.
- `STAGE_A_NO_GO`: close E094 immediately. No rescue, altered rank, seed, tolerance, public diagnostic, tuning, or sweep.

No official scorer, public-mini, holdout, full suite, canonical mutation, ledger mutation, or merge is allowed in E094 Stage A.