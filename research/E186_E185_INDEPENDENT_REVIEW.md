# E186 INDEPENDENT REVIEW — E185 exact trilinear-aggregation frontier

Date: 2026-09-22  
Branch: `review/e186-e185-independent-review-20260922`  
Reviewed E185 head: `10f5f0ab41da70b0661f44596f23f9e7f182ec11`  
Reviewed E185 artifact blob: `4d608cd5f292b04dff9c719e4990628b38d55872`  
Mode: **READ-ONLY PROCESS REVIEW — NO SCIENTIFIC RUN, NO BASELINE/LEDGER MUTATION**

## 0. Review decision

**Decision: REJECT the E185 owner-run as currently specified.**

This is **not a rejection of H185 as a research hypothesis**. The hypothesis remains
admissible and distinct from H180. The rejection is procedural: E185 does not yet freeze
enough implementation, coverage, production-dtype, evidence and verifier detail to make
one irreversible owner-run independently auditable.

A successor may be authorized only after the missing gates in Section 6 are frozen in a
pre-run protocol commit. No scientific/target-bearing run is authorized by E186.

## 1. Independence from H180 / rescue check

### 1.1 Git ancestry

E185 head `10f5f0ab...` has direct parent:

`e1536d36a5e2d641ab3596892847e2fcf41e83ab` = E177 audit.

It does **not** descend from:

- E180 `research/e180-cost-wall-cp-20260921`;
- E181 H180 owner branch;
- E183 H180 implementation/cost review.

The E185 commit adds only
`research/E185_TRILINEAR_AGGREGATION_PROTOCOL.md`; no H180 implementation/result is
carried into the branch.

### 1.2 Mechanism distinction

H180:

- changes the inherited K3 **representation**;
- replaces per-source history by a fixed rank-`3n` symmetric CP carrier;
- uses an approximate post-ReLU reprojection;
- accepts structural D21 approximation up to a frozen error threshold.

H185:

- keeps the V29 estimator state, young/old A/P history, D3/D21, K4 regeneration and
  closure equations;
- changes only the algebraic schedule for exact matrix products;
- forbids rank/source projection, CP/Tucker/TT replacement and source dropping.

Therefore E185 is not an H180 rescue, rerun, rank variant or renamed CP carrier.

**Gate result: PASS — distinct hypothesis class.**

## 2. Primary-source audit

### 2.1 Pan 1980

Victor Y. Pan, *New Fast Algorithms for Matrix Operations*,
SIAM Journal on Computing 9(2), 1980, DOI `10.1137/0209027`.

The primary abstract explicitly introduces trilinear aggregation, uniting and canceling
for fast linear noncommutative matrix-multiplication algorithms and states an improvement
over Strassen.

Primary source:
https://epubs.siam.org/doi/10.1137/0209027

**E185 use: supported.**

### 2.2 Pan 1982

Victor Y. Pan, *Trilinear aggregating with implicit canceling for a new acceleration of
matrix multiplication*, Computers & Mathematics with Applications 8(1), 1982,
DOI `10.1016/0898-1221(82)90037-2`.

The primary abstract states an **Exact Computing** algorithm for arbitrary even `n`
using:

`M_even(n) = (n+2) * [1.75(n+2) + (n^2 + 4n + 3)/3]`

essential multiplication steps.

At `n=1024`, E185's value

`M_even(1024) = 361,857,033`

is arithmetically consistent with that formula.

Primary source:
https://www.sciencedirect.com/science/article/pii/0898122182900372

Important limitation: this is a count of essential multiplications, **not** an all-in
flopscope cost. It does not include the additions, linear combinations, coefficient
multiplications, copies, temporary formation or residual-time cost that decide H185.

**E185 use: supported with the limitation already acknowledged by E185.**

### 2.3 Schwartz–Zwecher 2025

Oded Schwartz and Eyal Zwecher,
*Towards Faster Feasible Matrix Multiplication by Trilinear Aggregation*,
arXiv:2508.01748.

The primary abstract confirms that trilinear aggregation remains a live finite-base
matrix-multiplication class for feasible input sizes and explicitly identifies additive
complexity / leading coefficient reduction as a practical obstacle.

Primary source:
https://arxiv.org/abs/2508.01748

**E185 use: supported.**

### 2.4 Demmel–Dumitriu–Holtz–Kleinberg

*Fast matrix multiplication is stable*, arXiv:math/0603207.

The paper proves normwise stability for a broad class of recursive fast multiplication
algorithms. It does not certify the specific future Pan/TA compiler, coefficient set,
blocking scheme or V29 float32 path.

Primary source:
https://arxiv.org/abs/math/0603207

**E185 use: supported only as class-level evidence; a production numerical gate remains
mandatory.**

## 3. Cost lower bound review

Pinned F86 grouped ledger:

- young K3 = `115.6u`;
- old K3 = `106.8u`;
- thin/elementwise = `24.8u`;
- covariance = `7.1u`;
- closure/birth = `5.7u`.

Dense K3 transformable model:

`C_dense = 115.6 + 106.8 = 222.4u`.

Conservative unchanged remainder:

`C_fixed = 24.8 + 7.1 + 5.7 = 37.6u`.

Hard cap:

`C_cap = 138.24u = 0.135B`.

Therefore the maximum transformed dense bill is:

`C_dense,max = 138.24 - 37.6 = 100.64u`.

Necessary transformed-cost ratio:

`r_required <= 100.64 / 222.4 = 0.4525179856`.

E185's stricter mechanism gate:

`r_bundle <= 0.42`

would imply:

`C_dense,TA <= 93.408u`

and leave:

`100.64 - 93.408 = 7.232u`

of modeled integration headroom.

**Cost arithmetic verdict: PASS as a planning bound.**

### 3.1 Rounding issue that must be fixed pre-run

F86's headline total is `260.1u`, while the published grouped terms sum to `260.0u`.
Therefore the E185 statement

`260.1 - 138.24 = 121.86u`

is a headline-scale planning value, not an exact lower bound.

The production protocol must freeze one machine-readable parent ledger/hash and derive
all cost gates from that single source. It must not mix the rounded `260.1u` headline
with the `222.4u + 37.6u = 260.0u` grouped model.

## 4. Closed-dead-end audit

### F67 symmetric-contraction dead end

F67 closed Solomonik/Demmel-style savings for contracting a **dense symmetric order-3
tensor** because V29's dominant work is non-symmetric matrix multiplication
(`W A`, `W P`, and asymmetric D21 contractions).

H185 attacks exactly those ordinary matrix products with a different bilinear algorithm.
It does not rely on a symmetric order-3 contraction.

**Not the same dead end.**

### F86 ordinary engineering headroom

F86 measured the remaining ordinary Strassen/pricing lever at only about `7-10u`,
with residual-time cost making it non-shippable. That result concerns deeper pricing of
the existing multiplication scheme.

H185 requires a new exact bilinear/trilinear decomposition and a much larger
`<=0.42` bundle ratio. If it cannot achieve that all-in, it dies immediately.

**F86 raises the bar but does not logically close H185.**

### F88 representation-compression closures

F88 closes Tucker/shared-basis/multiplicatively-closed-basis/hub-merge/adjoint variants
of the K3 representation. H185 does not compress or replace the state.

**Not the same dead end.**

### Dead-end conclusion

No reviewed project result already proves H185 impossible. The hypothesis remains a
high-risk exact-algorithm lane whose likely failure mode is additive/copy/runtime
overhead, not a previously closed statistical representation failure.

## 5. Can the current protocol be one owner-run with independent verification?

### What E185 already gets right

The intended falsifier is target-free and production-shaped. It freezes:

- one hypothesis class;
- one seed;
- no base-case or coefficient sweep after results;
- parent/candidate product comparison;
- D3/D21 comparison;
- all-in namespace FLOP accounting;
- replay hashes;
- no automatic target-bearing follow-up.

That is compatible in principle with one owner-run.

### Why it is not yet independently verifiable

The current protocol says the future implementation *must later freeze* exact coefficient
tables, base cases, recursion/blocking, shape coverage and fallback. Those are not yet
present in E185 itself.

More importantly, the saved-output list is insufficient for a verifier to recompute the
claim without trusting owner summaries. It does not require immutable raw input matrices,
a manifest for every input/output, an exact operation-coverage map, coefficient-table
hashes, or a frozen production-dtype comparison.

Therefore the current protocol is **one-run-shaped but not yet one-run-ready**.

## 6. Missing mandatory gates before authorization

All items below must be frozen before the single owner run. These are blocking gates,
not optional polish.

### G0 — exact implementation identity

Commit and hash:

- the exact Pan/TA or generated bilinear decomposition;
- every coefficient table;
- base-case dimensions;
- recursion/blocking rules;
- rectangular adaptation rules;
- padding rules;
- fallback rules.

No algorithm selection may remain dynamic or result-dependent.

### G1 — complete F86 coverage map

Before execution, enumerate every production hot-path operation that contributes to the
modeled `222.4u` dense K3 bill.

For each namespace/event, record one of:

- transformed by the frozen TA compiler;
- unchanged parent operation;
- fixed fallback.

The sum of mapped parent costs must reconcile to the exact machine-readable parent ledger.
The current phrase "products selected from" is insufficient.

**Failure to cover the bill used in the `0.42` projection is pre-run REJECT.**

### G2 — exact parent ledger / rounding freeze

Commit the exact F86-compatible parent operation ledger used for projection, including:

- raw flopscope count;
- namespace totals;
- call semantics (including warm/steady-state convention);
- SHA-256.

Derive `r_required`, projected all-in cost and headroom from this ledger only.

### G3 — immutable input evidence

The owner receipt must preserve, for every bundle case:

- input matrices consumed by parent and candidate;
- dtype and shape;
- raw-array SHA-256;
- file SHA-256;
- nbytes;
- seed/provenance;
- parent output;
- candidate output.

A manifest must cover every immutable vector/matrix. Saving outputs without inputs is not
enough for independent recomputation.

### G4 — exact-small algebra gate

For a small rational/integer fixture, independently verify the frozen decomposition as an
identity, not merely as a floating-point approximation.

The receipt must retain the exact fixture and equality result/hash.

### G5 — production float64 identity gate

Keep E185's float64 product, D3 and D21 comparison, but specify how zero/near-zero
denominators are handled in relative norms and also retain absolute norms.

Current `2e-12` threshold is acceptable only for this float64 mechanism check.

### G6 — production float32 gate

This is missing and blocking.

V29 production arithmetic is float32. Passing a float64 `2e-12` test does not establish
that a long cancellation-heavy TA decomposition is safe in the actual estimator dtype.

Before the run, freeze a float32 acceptance metric and numerical threshold for:

- every product family;
- D3;
- off-diagonal D21.

The threshold must be justified from a pinned parent numerical reference or error model;
it must not be chosen after seeing TA results.

### G7 — all-in flopscope legality/accounting gate

The candidate ledger must charge every arithmetic operation used to realize the algorithm,
including:

- additions/subtractions;
- coefficient multiplications;
- copies/temporary formation when billed;
- padding/unpadding;
- fallback products;
- all recursive/base-case calls.

No unmetered alternative numerical path may be used to create candidate values.

### G8 — hard runtime projection gate

Replace "retain a path to <=0.400 s" with a deterministic formula.

Freeze before execution:

- parent residual-time baseline source;
- bundle-to-production event-count scaling;
- allowed integration overhead;
- exact terminal threshold.

The verifier must be able to recompute PASS/FAIL from immutable timing/event evidence,
without qualitative judgment.

### G9 — deterministic replay

Replay the exact same owner bundle once inside the authorized workflow and require
bitwise-identical candidate outputs, ledgers and manifest hashes.

This replay is part of the one authorized workflow, not a second scientific hypothesis run.

### G10 — one-run arm and terminal semantics

Before execution commit an arm file containing:

- owner branch/head SHA;
- protocol SHA;
- implementation SHA;
- coefficient-table SHA;
- seed;
- `authorized_owner_runs = 1`;
- no rerun/rescue/sweep;
- exact terminal exit semantics.

A failed identity, coverage, cost, float32 or runtime gate must write a terminal receipt.
No changed base case or second seed is allowed under the same hypothesis run.

### G11 — independent verifier contract

Create/freeze a separate verifier protocol before the owner result exists.

The verifier may use only committed protocol plus immutable owner artifacts. It must
independently recompute:

- input/output hashes and manifest completeness;
- exact-small identity status;
- float64 and float32 product norms;
- D3/D21 norms;
- parent/candidate bundle FLOPs;
- coverage reconciliation to the exact parent ledger;
- `r_bundle`;
- projected all-in cost;
- runtime projection;
- deterministic replay/provenance.

The verifier must not modify the candidate, choose a new decomposition, run a new
hypothesis, or repair owner evidence.

Verifier receipt should separate:

- `mechanism_go`;
- `protocol_go`;
- `integration_readiness`.

### G12 — target firewall

Record a source/import/access audit proving that the mechanism run does not load:

- benchmark target means;
- scorer/holdout;
- public submission endpoint;
- leaderboard result data used for tuning.

## 7. Future one-run decision rule

After G0-G12 are frozen, the future owner mechanism run may be authorized with exactly
one candidate.

Mechanism GO requires all of:

1. exact-small algebra identity passes;
2. production float64 identity passes;
3. frozen production float32 gate passes;
4. immutable evidence + replay pass;
5. coverage reconciles to the exact parent ledger;
6. `C_TA_bundle / C_parent_bundle <= 0.42`;
7. projected all-in estimator cost `<=0.135B`;
8. hard runtime projection passes;
9. target firewall passes.

Any failure is terminal for that frozen implementation.

Passing these gates authorizes only a later **integration/scientific review**, not a
target-bearing accuracy run automatically.

## 8. E186 final verdict

### H180 separation

**PASS.** E185 is neither ancestry-rescue nor mechanism-variant of H180.

### Primary sources

**PASS with limitations.** The cited primary literature supports exact trilinear
aggregation as a real matrix-multiplication algorithm class and supports E185's warning
that additive complexity is decisive.

### Cost lower bound

**PASS as planning arithmetic, FAIL as final receipt basis until one exact parent ledger
replaces rounded F86 totals.**

### Existing dead end

**PASS.** No reviewed F67/F86/F88 result already closes this exact-algorithm class.

### One-run verifiability

**FAIL in current E185 form.** The protocol is conceptually one-run compatible but does
not yet freeze enough evidence, dtype, coverage and verifier detail for an irreversible
owner execution.

## Decision

**REJECT CURRENT FUTURE LAUNCH.**

Re-review after a pre-run amendment freezes G0-G12. If those gates are frozen without
changing the H185 hypothesis, a single target-free owner mechanism falsifier can be
independently verifiable without any scientific run or baseline/ledger mutation.
