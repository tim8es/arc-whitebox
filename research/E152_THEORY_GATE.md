# E152 theory gate — final-observable adjoint/source actions versus full intermediate D21

Idempotency key: `ARC-E152-FINAL-OBSERVABLE-ADJOINT-THEORY-GATE-20260921`.

Branch: `research/e152-final-observable-adjoint-theory-gate-20260921`.

Decision class: **THEORY / TARGET-FREE / NO BENCHMARK RUN**.

## Question

Can the full public V29 K3 chain be replaced by final-observable-only propagation that
uses adaptive downstream adjoints and source actions, while never reproducing the full
intermediate D21 object?

E152 is deliberately not:

- E142: old-tier queried residual actions at an existing D21 contraction interface;
- E147: a forward projected primal K3 core plus a rank-r D21 surrogate;
- E148: a global seed tensor-train K3 carrier.

E152 asks whether reverse/final-observable dualization itself removes the need for the
primal D21 information.

## Pinned primary sources

Public estimator repository:

`504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.

Pinned blobs:

- `lean/k3_tables2.py`: `9572ace30b98cd7803054b5222c48381ff72c5ae`;
- `estimators/estimator_v29.py`: `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`;
- `docs/audit_v29_ns_d0.log`: `a689ef69fd64bed7765cb93ce4910c3fedcbd04a`;
- `docs/community_post.md`: `aa06c6d24c0bf9f6cb9cfd326c4862d6a4ee3a73`;
- `docs/claims_evidence.md`: `087aaa2404a046afd06bd954a1cc0bf09ffdf05c`;
- `docs/findings_log.md`: `09cf41e8826052ceb83109115cae688c03baaaca`.

Official ARC source pin:

`alignment-research-center/mlp_cumulant_propagation@93d091a4c26c042bfffa28f2e76a81bc0aba94bb`.

Relevant local terminal evidence:

- E147 terminal receipt on
  `research/e147-response-projected-k3-estimator-20260921@da90720ae3ca971fd07cb8e2616eb6b5b95cb363`;
- E148 terminal receipt on
  `research/e148-global-seed-tt-k3-20260921@d79eb8e670fbb8ff007283d9ed1eab6dd53a8b35`.

## Primary dead-end constraints that matter here

The public evidence already rules out several ways of hiding the missing primal state:

1. **F65 / memoryless slice closure**: carrying only D3/D21 does not close the next
   layer. The public write-up reports that fully off-diagonal K3 omitted by the slice
   state contributes roughly 18–23% of next-layer D21 energy and is high-rank.
2. **F66/F72/F73 / source rigidity**: sources remain necessary; the shared old-source
   basis has an empirical accuracy cliff below approximately rank 384 at age 4 and rank
   224 at age 7.
3. **F69**: D21 feedback is one of the few K3 sub-blocks with material accuracy value.
4. **F71**: D21 can be omitted exactly only at the final mean-only layer. This is a
   last-layer identity, not a recurrence for layers 1–14.
5. **F76**: capped merged K3 atoms remain too high-rank; even 8n columns can be above
   the D21 precision requirement.
6. **F82**: a response/slice-series style memoryless closure lands on the same F65 floor.
7. **F88**: higher feedback/residual ranks and remaining same-chain representation knobs
   do not create a cheap escape.

These are empirical constraints, not the E152 proof. The proof below is algebraic.

## Frozen mechanism class being tested

Call the proposed class **AFO-SA**: adaptive final-observable source actions.

At every non-final nonlinear layer let `D` denote the zero-diagonal D21 matrix.
The candidate is forbidden to materialize or carry a full D21-equivalent matrix.
Its only D21 access is through adaptive linear source actions

[
D S_j,qquad D^T T_j,
]

where query blocks may depend on:

- network weights;
- low-order target-free state;
- downstream/final-observable adjoints;
- all previously returned source actions.

No target, exact reference, public score or post-result fitting may determine the queries.

Let `q_R` be the total number of right-query columns and `q_L` the total number of
left-query columns at a layer.

## Theorem 1 — adaptive action transcript is not an exact nonlinear sufficient statistic

Let

[
mathcal Z_n={Dinmathbb R^{n	imes n}:operatorname{diag}(D)=0}.
]

Then

[
dim mathcal Z_n=n(n-1).
]

For fixed right/left query matrices `S,T`, the transcript map

[
Phi(D)=(DS,D^TT)
]

has rank at most

[
n(q_R+q_L).
]

Therefore, whenever

[
q_R+q_L<n-1,
]

[
ker(Phi)cap mathcal Z_n
eq{0}.
]

### Adaptive queries do not evade the kernel

Run a deterministic adaptive algorithm on `D=0`. Every returned action is zero, so this
fixes the entire adaptive query sequence. After the last query choose any nonzero

[
Einker(Phi)capmathcal Z_n.
]

On `D=E`, every action is again zero. Therefore the adaptive branch and complete
transcript are identical for `D=0` and `D=E`.

This argument also applies to seeded randomized queries after conditioning on the frozen
seed.

## Theorem 2 — public ReLU K3 closure separates the indistinguishable states

The pinned public K3 term table contains, in the `(1,1)` power-cumulant program,

[
rac14,(mathrm{D21}^Todot mathrm{D21}^T)
]

with left/right Wick pairs `(2,1)` and `(4,1)`.

At zero mean and unit variance,

[
w(2,1)=phi(0),qquad
w(4,1)=-phi(0),
]

so the actual scalar multiplier of this component is

[
-rac{1}{8pi}
eq0.
]

Thus the exact nonlinear closure difference between `D=0` and any nonzero hidden
`D=E` contains

[
-rac{1}{8pi}(E^Todot E^T),
]

which is nonzero for every nonzero `E`.

Hence two D21 states with the same complete adaptive action transcript can have different
next nonlinear states.

The obstruction is already local; a future dense linear layer generically propagates the
nonzero difference into later covariance/K3 slices and therefore into a final mean
observable.

## Consequence

For an exact action-only representation to avoid the indistinguishability construction,
a necessary condition at every D21-consuming layer is

[
q_R+q_Lge n-1.
]

This is only a necessary condition, not a sufficiency claim.

At production width `n=1024` this means at least

[
1023
]

queried directions per layer.

The returned transcript itself then contains at least

[
n(n-1)=1,047,552
]

D21-response scalars per layer, versus `n^2=1,048,576` entries in the full matrix.
So exact AFO-SA has lost essentially all representation compression before any FLOP
accounting.

## Exact-small falsifier

A reusable exact witness is frozen in
`scripts/e152_final_observable_action_gate.py`.

Use:

- `n=8`;
- `q_R=q_L=3`, hence `q_R+q_L=6<n-1=7`;
- `S=T=[e_0,e_1,e_2]`;
- zero-diagonal hidden matrix `E` with exactly `E[3,4]=1`.

Then exactly, over integers,

[
ES=0,qquad E^TT=0,
]

so `D=0` and `D=E` have identical action transcripts, while

[
E^Todot E^T
eq0.
]

The script also verifies the production arithmetic below. It uses no network target or
benchmark data.

## Production lower bound for the requested source-action class

This is a class-conditional lower bound: it applies to AFO-SA when actions are evaluated
from the pinned V29 dense young-source identity

[
D_s=L_{A,s}A_s^T+L_{P,s}P_s^T
]

without first materializing `D_s`.

For a right block `S` of width `q`,

[
D_sS=L_A(A^TS)+L_P(P^TS).
]

That requires four dense-thin products. With the challenge FLOP convention, the cost is

[
8n^2q
]

per source. The left action has the same cost.

Therefore total right+left query width `q_R+q_L` costs at least

[
8n^2(q_R+q_L)
]

per dense young source-instance in this source-action circuit.

Pinned V29 `AGE_OLD=4` gives exactly 50 dense-young source/layer instances over
D21-consuming layers 1–14:

[
1+2+3+4+10cdot4=50.
]

Using the theorem's necessary `q_R+q_Lge1023`,

[
C_{	ext{young actions}}
ge
50cdot8cdot1024^2cdot1023
=
429,077,299,200	ext{ FLOPs}.
]

With

[
B=2^{41}=2,199,023,255,552,
]

this is

[
C_{	ext{young actions}}/B
=
0.19512176513671875.
]

Project cap:

[
0.135B=296,868,139,499.52.
]

So the young-source action path alone exceeds the cap by about
`132.21 billion FLOPs`, before:

- old-source actions;
- covariance;
- nonlinear closure/birth;
- D3/K4;
- feedback;
- certificates;
- helper work.

### Scope caveat

The arithmetic bound above is for the requested V29-factor/source-action circuit using
the legal dense-thin action identities. It is not claimed as a universal lower bound on
matrix multiplication complexity.

A custom fast-matrix-multiplication rewrite that abandons this action circuit would still
not fix Theorems 1–2: exactness requires an almost-full D21 transcript, violating the
defining requirement that the mechanism avoid reproducing full intermediate D21. Such a
rewrite is a different architecture, not an E152 rescue.

As a cross-check, the pinned steady V29 namespace ledger itself assigns 60.71 units to
young transport, 54.90 to the young D21 hub, 27.89 to old-leg formation, 27.91 to old
D21 contraction, 7.10 to covariance and 5.71 to closure/birth. E152 does not use their
sum as the theorem; it records them only to show the production obstruction is consistent
with the measured public cost anatomy.

## Why E147's small final-mean error does not reopen E152

E147 had final-mean relative errors around 1.0% and 0.55% on its two small fixtures while
its D21 relative errors were about 99% and 102%. That is evidence that one frozen small
trajectory can have weak final sensitivity to a bad D21 approximation.

It does not provide an exact sufficient statistic. E147's own certificate became
infinite, and Theorems 1–2 exhibit action-indistinguishable D21 perturbations that the
nonlinear closure can detect exactly.

E152 therefore does not convert E147's diagnostic into another rank/basis rescue.

## Why E148 does not overlap

E148 replaced the primal K3 carrier by one global TT state and failed its frozen small
accuracy gates. E152 carries no TT/core and proves a dual/action nonclosure result.

## Theory-gate decision

**TERMINAL NO-GO for exact final-observable-only adaptive adjoint/source-action
replacement of V29 that forbids a full or entrywise-equivalent intermediate D21.**

Dichotomy:

1. `q_R+q_L<n-1`: exact nonlinear closure is impossible by the adaptive kernel witness.
2. `q_R+q_L>=n-1`: the action transcript is essentially full D21; the requested
   representation goal is lost, and the pinned dense-young source-action implementation
   alone is `0.19512 B > 0.135 B`.

No physical run, public target, public-mini, scorer, holdout, full suite, rank sweep,
basis sweep, adjoint sweep, or final-MSE validation is authorized under E152.

An approximate deliberately non-exact dual compression would be a new experiment class.
It must not be called an E152 rescue and must confront F65/F76/F82 plus the E147/E148
terminal evidence.
