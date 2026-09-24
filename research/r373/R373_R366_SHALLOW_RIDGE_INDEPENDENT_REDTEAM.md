# R373 — independent mathematical red-team of R366 shallow-ridge scout

**Status:** COMPLETE  
**Verdict:** **FAIL — MATERIAL CONTEST-SCORER CERTIFICATE ERROR**  
**Mode:** independent read-only mathematical/source audit; no estimator, synthetic, or benchmark execution  
**Exact base:** `4619801e0cc5e7e340cd0406eb44e0633d8aa5e5`  
**Branch:** `review/r373-r366-shallow-ridge-independent-redteam-20260924`

## 1. Audited R366 evidence

R366 source was re-read at the exact requested immutable state:

- branch: `review/r366-uncovered-estimator-frontier-scout-20260924`
- head: `02305335c80161311e13839de3268be97a43e504`
- report: `research/r366/R366_UNCOVERED_ESTIMATOR_FRONTIER_SCOUT.md`
- report blob: `f2c512a04c1eb9b0d179cd04a5563e34a6f109aa`
- receipt: `research/r366/R366_RECEIPT.json`
- receipt blob: `1929547b16f922470cb81071446b3a43d3dea95c`

R373 does not edit R366 or R320.

## 2. Algebra audit

### 2.1 Gaussian ReLU moment — PASS

For `X ~ N(0,I_n)` and fixed `b in R^n`,

`Z=b^T X ~ N(0, ||b||_2^2)`.

Writing `Z=||b||_2 G` with `G~N(0,1)`,

`E ReLU(Z) = ||b||_2 E[G 1{G>0}] = ||b||_2 / sqrt(2*pi)`.

The formula also holds for `b=0`. R366's identity is correct. Tallis (1961) is a valid primary-source truncated-normal reference, although the scalar identity follows directly from the one-dimensional Gaussian integral.

Primary source:
- G. M. Tallis (1961), *The Moment Generating Function of the Truncated Multi-Normal Distribution*, JRSS B 23(1), 223–229.
- DOI: https://doi.org/10.1111/j.2517-6161.1961.tb00408.x

### 2.2 Vector readout for the stated surrogate — PASS

For

`g(x)=A rho(Bx)`, `A in R^(n x m)`, `B in R^(m x n)`,

let `b_j^T` be row `j` of `B`. Linearity of expectation gives

`E[g(X)] = A E[rho(BX)]`.

No independence between the `m` preactivations is needed because expectation is componentwise. Therefore

`E[g(X)] = (1/sqrt(2*pi)) A [||b_1||_2,...,||b_m||_2]^T`.

This is exact for the surrogate `g`. It is not generally exact/unbiased for the original deep network `f`.

### 2.3 Jensen conversion to exact-mean error — PASS

Let `h(X)=f(X)-g(X)` and

`delta^2 = E ||h(X)||_2^2`.

Since squared Euclidean norm is convex,

`||E h(X)||_2^2 <= E ||h(X)||_2^2 = delta^2`.

Thus for the exact population mean `mu=E f(X)` and surrogate mean `mu_hat=E g(X)`,

`(1/n)||mu_hat-mu||_2^2 <= delta^2/n`.

R366 is correct **for error to the exact population mean**.

## 3. Contest scorer normalization — MATERIAL FAIL

R366 then treats `delta^2/n` as an upper bound on the benchmark/scorer `final_layer_mse`. That implication is not valid for the published Phase-2 Mini targets.

The official public Phase-2 dataset states that `final_means` are empirical means baked from `N=1,000,000,000` independent Gaussian samples. The scorer compares the estimator prediction against those fixed baked target vectors, not against the inaccessible mathematical population mean.

Let:

- `mu = E f(X)` be the exact population mean;
- `y` be the fixed baked Mini target vector;
- `mu_hat = E g(X)`;
- `eta = ||mu-y||_2^2/n`.

R366 proves only

`||mu_hat-mu||_2/sqrt(n) <= sqrt(delta^2/n)`.

The scorer uses

`MSE_score = ||mu_hat-y||_2^2/n`.

By triangle inequality,

`MSE_score <= (sqrt(delta^2/n) + sqrt(eta))^2`.

A looser valid bound is

`MSE_score <= 2 delta^2/n + 2 eta`.

Without a certified bound on `eta` (or an exact relation to the fixed baked target), `MSE_score <= delta^2/n` does **not** follow. The cross term may increase or decrease the fixed-target MSE.

Primary official sources:
- AIcrowd public Phase-2 dataset README: https://huggingface.co/datasets/aicrowd/arc-whestbench-public-2026/blob/v2-phase2/README.md
- AIcrowd scoring model: https://github.com/AIcrowd/whest-starterkit/blob/main/docs/concepts/scoring-model.md
- AIcrowd score report fields: https://github.com/AIcrowd/whest-starterkit/blob/main/docs/reference/score-report-fields.md

The official scorer defines per-MLP final-layer MSE as the mean over the `n` final coordinates and ranks by the suite mean of

`final_layer_mse_i * max(0.1, C_i/B)`

for valid Phase-2 rows, with `B=2^41` and Phase-2 `C_i=F_i`.

### Exact correction to R366's Mini-100 gate

R366's displayed conditions

`mean_i[(delta_i^2/1024) q_i] < 8.170397440117225e-9`

and, at the 0.1 floor,

`mean_i[delta_i^2/1024] < 8.170397440117225e-8`

are **not sufficient conditions for the fixed Mini-100 contest score as written**.

A valid sufficient form requires a per-network bound `eta_i >= ||mu_i-y_i||_2^2/1024` and then, for example,

`mean_i[ (sqrt(delta_i^2/1024)+sqrt(eta_i))^2 q_i ] < S_R209`,

where `q_i=max(0.1,C_i/2^41)` and `S_R209` is the exact same-panel baseline score being compared.

At the score floor, the analogous sufficient condition is

`mean_i[(sqrt(delta_i^2/1024)+sqrt(eta_i))^2] < S_R209/0.1`.

R373 found no R366 artifact supplying the required `eta_i` certificate. The target SHA fingerprints in R209 establish target identity, not population-mean error.

Therefore R366's numeric `8.170397440117225e-8` residual threshold is arithmetically correct **only under the additional idealization `y_i=mu_i` (or `eta_i=0`)**. It is not a rigorous fixed-Mini scorer threshold without that assumption.

The arithmetic conversion `1024 * 8.170397440117225e-8 = 8.3664869786800384e-5` is correct under the same assumption.

## 4. Cost and storage audit — PASS WITH SCOPE CAVEAT

Dimensions are correct:

- `A`: `n x m`
- `B`: `m x n`
- total coefficients: `2nm`

Leading arithmetic once `A,B` already exist:

1. `m` row norms of `B`: approximately `2mn` scalar add/multiply work, plus `m` square roots;
2. dense `A v`: approximately `2mn` multiply/add work;
3. scaling/auxiliary work: `O(m+n)`.

Hence

`C_readout = 4mn + O(m+n)`

is a valid leading-order arithmetic estimate. At `n=1024`, this is approximately `4096m`.

For float32 coefficients only,

`4 bytes * (nm+mn) = 8nm = 8192m bytes`.

At `m=131072`, coefficient storage is exactly `1,073,741,824` bytes and leading `4096m = 536,870,912` arithmetic operations.

Caveat: this is not an all-in Phase-2 cost proof. Exact FlopScope billing depends on the eventual permitted implementation/primitives, and R366 correctly leaves `C_Tm` and auxiliary construction/certification costs unresolved.

The integer FLOP ceiling for the 0.1 floor is also correct:

`C <= floor(0.1 * 2^41) = 219,902,325,555`.

## 5. Novelty/dedupe audit — PASS WITH ONE REQUIRED CLARIFICATION

R373 re-read the exact-base `research/history.json` (blob `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`) and the R320 snapshot used by R366 (head `7336ffb2a88ab38ebb96177d4bc7d8bfd5dd53e1`, report blob `870c9131a4e4bc745ea6ad6510d6a45115dcc5a8`, receipt blob `3fa12a194b1fd33361465bef815afe1eedc81460`).

No prior artifact found in E100–E193/R320 implements the R366 mechanism

`deep known W -> deterministic target-free T_m(W) -> (A,B) -> g(x)=A ReLU(Bx) -> analytic Gaussian expectation`

as a whole-function shallow flattening.

However, R366's term-search presentation is incomplete because E113 contains the phrase/mechanism **"deterministic deep folded-ridge residual control"**:

- E113 branch: `research/e113-deep-folded-ridge-residual-20260919`
- terminal commit: `5be1a09857ba39edecd75a894d091505d7a2f0cc`
- protocol blob: `02d942d5b2d31ff291ba535a380d1b1b47384138`
- receipt blob: `197e26ea402a6cb21be52c1cb10b9ba1eb90ac23`

E113 is **not** the same class. It constructs a deterministic deep direction and an exactly centered folded spherical ridge **control variate** around an E104 radial/Haar estimator. It does not construct a shallow network `A ReLU(Bx)` approximating the whole deep function and does not analytically integrate such a surrogate.

So the R366 novelty conclusion survives, but the dedupe should explicitly distinguish E113 rather than relying on zero counts for selected terms such as "ridge function".

## 6. Literature audit — PASS FOR NARROW CLAIM, WITH HSU WORDING CORRECTION

### Bach 2017

Bach studies single-hidden-layer positively homogeneous networks, including ReLU, and explicitly states that the infinite-dimensional convex formulation still depends on a non-convex unit-addition subproblem; the paper does not obtain the needed provably polynomial-time algorithm preserving the desired bounds.

Primary source:
https://jmlr.org/papers/v18/14-546.html

This supports R366's narrow statement that Bach does not supply the required deterministic polynomial-time white-box flattening theorem for arbitrary known deep ARC networks.

### Hsu et al. 2021

The paper gives quantitative upper/lower width bounds for two-layer random-bottom-layer ReLU approximation. Its **main results** use L2 over the uniform cube, but Appendix E also treats Gaussian space. Therefore R366's broad wording that its "distribution/domain is not ARC" should be narrowed: Gaussian input measure is considered in the paper, but the results concern random shallow feature approximation of smooth function classes, not a deterministic white-box transformation of the ARC width-1024/depth-16 He-Gaussian deep-network ensemble with the required constants/cost certificate.

Primary source:
https://proceedings.mlr.press/v134/hsu21a.html

This is a wording correction, not an ARC impossibility result.

### Eldan & Shamir 2016

Their depth-separation theorem constructs a particular probability measure `mu` on `R^d`; the paper defines its density through the squared Fourier transform of a ball indicator. It is not the ARC standard Gaussian input law. Thus it cannot prove impossibility for the ARC ensemble.

Primary source:
https://proceedings.mlr.press/v49/eldan16.html

### Telgarsky 2016

Telgarsky proves exponential depth/width separations for semi-algebraic gates including ReLU. The theorem is an existence/depth-separation result, not a lower bound for the specific random ARC network ensemble.

Primary source:
https://proceedings.mlr.press/v49/telgarsky16.html

### Chen et al. 2022

The paper gives super-polynomial statistical-query lower bounds for learning certain two-hidden-layer ReLU networks under Gaussian inputs. This is a black-box/statistical learning hardness statement, not a white-box representation lower bound for known ARC weights.

Primary source:
https://proceedings.neurips.cc/paper_files/paper/2022/hash/45a7ca247462d9e465ee88c8a302ca70-Abstract-Conference.html

### Literature conclusion

The cited sources justify only the narrow conclusion:

> R366 did not find a constructive, target-free, white-box theorem that maps the actual ARC deep-network class to a sufficiently compact shallow ridge representation with certified Gaussian-L2 error and all-in Phase-2 cost.

They do **not** justify universal impossibility of shallow flattening for ARC. R366 itself mostly preserves this boundary.

## 7. Final red-team verdict

**FAIL — MATERIAL CONTEST-SCORER CERTIFICATE ERROR.**

What survives R373:
- Gaussian ReLU expectation formula: correct;
- vector analytic readout: correct;
- Jensen bound to the **exact population mean**: correct;
- leading readout dimensions/cost/storage: correct with the stated non-all-in caveat;
- distinctness of deterministic whole-function shallow flattening: survives dedupe, after explicitly separating E113;
- literature supports only the narrow missing-constructive-theorem claim, not universal impossibility;
- R366's conservative decision not to launch a numerical candidate remains scientifically defensible.

Material correction:
- the Gaussian-L2 surrogate certificate does **not by itself upper-bound the fixed Phase-2 Mini scorer MSE**, because the scorer target is a finite-`N=1e9` baked empirical mean rather than the exact population mean;
- therefore R366's same-panel residual thresholds are not rigorous sufficient scorer gates unless an additional target-vs-population error certificate is supplied.

R373 does not authorize implementation or a rerun. A corrected re-entry theorem would need both the original deterministic `T_m`/Gaussian-L2/cost certificate **and** a rigorous bridge from exact population mean error to the fixed scorer target (or a scorer gate explicitly formulated with a certified `eta_i` term).

## 8. Execution accounting

- R366 edits: **0**
- R320 edits: **0**
- code created/run: **0**
- estimator runs: **0**
- synthetic runs: **0**
- benchmark runs: **0**
- Actions runs: **0**
- downloads/installs: **0**
- paid resources: **0**
- private/holdout/full access: **0**
- submissions: **0**
- main/PR/control/queue edits: **0**
