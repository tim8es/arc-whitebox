# R269 multilevel-debiasing feasibility result

Status: **EVIDENCE_BASED_NO_GO_BEFORE_EXECUTION**

Job: R269  
Owner: `multilevel-debiasing-scout`  
Run: `R269-multilevel-theory-20260923`  
Claim commit: `a6aa4466426b1fb8e20a2e6c484192e400018881`  
Start control commit: `b24f69b9c74bf972c72f6e6621a511e88d4800f9`  
Frozen protocol commit: `8d93f50cab5b3c389e857e02667c2e400df43aae`

## Evidence read

R269 read the sealed R265 protocol/report/receipt and the complete current history. The history blob is unchanged from R265:

- `research/history.json` blob `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`
- 194 E-IDs
- 631 artifact records

Pinned V25 source:

- source commit `dff3dd65e9d2210e02418cca99e05556f6bf2c75`
- `methods/public_504aldo/estimator_v25.py` blob `195373a110215256b759d7c172ba8c923c62e5cc`
- 1132 lines

The full-history novelty check confirms that randomized multilevel/Rhee-Glynn terminology is absent, but randomized source/sample compression itself is already occupied by E033/E095. R223 owns feed-local lambda. Rank/basis/source-age/tensor/K3 transport/arithmetic hierarchies remain excluded. Direct lexical checks found no prior `multilevel`, `Rhee`, `Glynn`, `Russian roulette`, `Bernoulli`, `depth-prefix`, or `layer-prefix` mechanism.

Primary sources inherited from R265:

- Giles (2008), DOI `10.1287/opre.1070.0496`
- Rhee & Glynn (2015), DOI `10.1287/opre.2015.1404`

## Concrete V25 two-level telescope

The only concrete non-relabeling hierarchy that survives the exclusions is a depth-prefix telescope.

For deterministic V25 means `mu_1,...,mu_16`:

- `Y0 = mu_15`
- `Y1 = mu_16`
- `p = 1/2`
- `B ~ Bernoulli(1/2)`
- final-row estimator `Z = Y0 + (B/p)*(Y1-Y0)`

Rows 1..15 remain the exact V25 rows. The telescope is exactly unbiased over the Bernoulli randomization:

`E_B[Z] = Y1`.

For any unknown target vector `t`,

`E_B[||Z-t||^2/n] = ||Y1-t||^2/n + ((1-p)/p)*||Y1-Y0||^2/n`.

At `p=1/2`, the candidate adds exactly `||Y1-Y0||^2/n` expected raw-MSE variance. Thus it cannot beat deterministic V25 in expected raw MSE. Its only possible route to a lower adjusted score would be enough expected FLOP savings to compensate that added variance.

## Metered path and production cost

A compliant implementation would use only the existing V25 FlopScope NumPy path:

1. run exact V25 setup and layers 1..15;
2. take one Bernoulli decision from the existing `fnp.random.default_rng(ctx.seed)` setup RNG;
3. if selected, continue the exact V25 final layer, including its mean-only final path and source D3 machinery;
4. combine the final vector with metered `fnp` subtraction/multiplication/addition.

Let `C0` be exact prefix cost and `C16` the final-layer incremental cost. Then:

- parent: `C1 = C0 + C16`
- candidate worst case: `C1 + O(n)`
- candidate expectation at p=1/2: `C0 + 0.5*C16 + O(n)`

R265 records V25 mean measured cost `806303721965` FLOPs/network. The source docstring separately gives an older approximate, data-independent `~1.83e12` FLOP figure. Neither supplies a committed exact split into `C0` and `C16`, and the approximate docstring is not an upper-bound proof. Therefore R269 cannot honestly preregister the nontrivial expected production FLOP bound needed to evaluate the purported cost advantage.

## Frozen synthetic falsifier

A deterministic target-free falsifier was frozen but not executed:

`R269-DEPTH-TELESCOPE-W32-D6-v1`

- width 32, depth 6
- no external targets
- `W_l[i,j] = sqrt(2/32) * cos((l+1)*(i+1)*(j+1))`
- generated in float64, cast to float32 at estimator boundary
- standard Gaussian input assumption
- no seed/rank/probability sweep

Diagnostics:

- `D5 = mu_5-mu_4`
- `D6 = mu_6-mu_5`
- `rho_V = ||D6||^2 / max(||D5||^2,2^-100)`
- `rho_C = (C6-C5)/max(C5-C4,1)`
- p=1/2 correction variance `V6 = ||D6||^2/n`

Frozen gate would require exact replay, finite outputs, `rho_V < 1`, and `rho_V*max(rho_C,1) <= 0.5`, plus an already-valid static production cost bound.

## Why execution is forbidden

Two mandatory pre-execution gates fail.

**Target-free rationale fails.** `mu_15` and `mu_16` are means of different neuron layers under different weight matrices. Equal width does not give coordinate identity, and nothing in V25/history establishes that depth-prefix vectors form an L2-convergent approximation sequence to the fixed final-layer vector. The algebraic telescope is valid, but the correction-decay mechanism required by multilevel debiasing is unsupported. Running the fixture just to see whether this arbitrary difference is small would be method fishing.

**Full cost-bound gate fails.** The exact incremental split `C0/C16` required by the expected-cost claim is not committed. R269 is not allowed to execute merely to manufacture the missing bound once the theory gate has already failed.

## Decision

**NO_GO before prototype and before local synthetic execution.**

This is not a general rejection of Rhee-Glynn/MLMC. It is a bounded rejection of the only concrete non-relabeling V25 telescope available under R269's exclusions.

Accounting:

- prototypes created: `0`
- local synthetic falsifiers executed: `0`
- estimator/benchmark executions: `0`
- public/R209 accesses: `0`
- Actions/cloud runs: `0`
- paid compute: `0`
- private/holdout/full accesses: `0`
- tuning/per-network selection: `0`
- submissions: `0`
- canonical/leaderboard edits: `0`
