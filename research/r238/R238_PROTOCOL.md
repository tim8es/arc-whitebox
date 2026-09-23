# R238 — RSRF-V25 recycled-start range finder

Date: 2026-09-23
Idempotency: ARC-R238-V25-RSRF-20260923
Queue owner: global-accuracy-research
Existing job only: R238 (no duplicate enqueue)

## 0. Frozen question

Test exactly one estimator family:

> **RSRF-V25** — at each V25 tier-1 old-source shared-basis rebuild after the first,
> preserve the canonical rank and single weighted-Gram application, but start the
> range finder from the sum of the fresh deterministic weight-slice sketch and the
> transported previous old-source basis:
>
> `Omega = W_slice + Qp`.

The first tier-1 join is unchanged because no previous old basis exists.

This is a deterministic **subspace-recycling / warm-start range-finder** method.
It is not DRRE/Richardson/rank extrapolation; not oversampling; not QPASS/power
iteration; not source-axis compression; not response alignment; not a K4 second mode;
not feed-local lambda; not copula/CountSketch/Walsh; not tail-only tuning.

No coefficient, rank, seed, age gate, or mixture weight is tuned. The recycling
coefficient is frozen to exactly 1 before any execution.

## 1. Governance and immutable evidence

Read before selection:
- `AGENTS.md` blob `6d9c61537a282a7d141af316dd8be438d1015a49`;
- `research/RESEARCH_PROCESS.md` blob `bf5a4676d8f36100e2dfdde32d544a39661eba8d`;
- `research/history.json` blob `8f94f371572fedbd8c1ebd9d19cc48ca837592fb`, 194 experiment IDs;
- `research/legacy-ledger.csv` blob `040e52efe01efd7280180b7e2d72901b4c2f0532`;
- R227 receipt blob `17f5b48580c7c6cf76b2966084b80024af04affe`;
- R231 receipt blob `a2cf807ce9617c464e0e60b12f0bbfc17e196cf4`;
- R232 terminal receipt blob `c6aa858bd083c86067160325015032d9d7208343`.

R231: V25 errors are weakly concentrated; global accuracy is primary.
R227: dense second-K4 regeneration is not deployable/score-positive.
R232: DRRE is closed and must not be retried or rescued.

The full history/legacy text was searched for subspace-recycling/warm-start/incremental
basis families and related terms; all frozen absent-term counts are zero in
`R238_NOVELTY_AUDIT.json`.

Adjacent work is not the same family:
- E022 widens the block to R_OLD+16 and eigentruncates; RSRF stays at R_OLD.
- QPASS changes the number of Gram applications; RSRF keeps exactly one.
- E094 compresses the source axis; RSRF changes only the spatial start block.
- response-aligned K3/D21 uses downstream response information; RSRF is response-free.

## 2. Pinned parent

Upstream:
`504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`

Pinned V25:
`estimators/estimator_v25.py`
git blob:
`195373a110215256b759d7c172ba8c923c62e5cc`.

Existing normalized mini-100 parent:
- 100/100 valid;
- failures 0;
- mean raw final MSE `2.228303490170447e-8`;
- measured FLOPs/network `806303721965`;
- adjusted score `8.170397440117225e-9`;
- normalized record SHA256
  `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`.

Canonical V25 is never modified.

## 3. Exact source patch

The candidate is generated only after the unmodified parent passes the frozen
base-executability gate.

Exactly one source occurrence must match:

```python
Om = fnp.copy(w32[:, :r_old])
Qp = (w1c * Qc) if ka > 0 else None
for _pass in range(QPASS):
```

and becomes:

```python
Om = fnp.copy(w32[:, :r_old])
Qp = (w1c * Qc) if ka > 0 else None
if ka > 0:
    Om = Om + Qp
for _pass in range(QPASS):
```

No other V25 line changes.

Interpretation: the current compressed old-source subspace is a useful prior for the
next join. Canonical V25 discards it from the start block and relies only on a fresh
weight slice. RSRF gives the same one-pass Gram action a start block containing both
the fresh sketch and the transported old subspace, without increasing rank.

## 4. Production cost bound

Competition budget:
`B=2**41=2199023255552`.

Parent:
`C_parent=806303721965`.

V25 has 10 tier-1 joins (layers 5..14); the first has no prior Qp, so RSRF adds work
on 9 joins. Production width/rank are n=1024, r=384.

Conservatively charge **2 FLOPs per element** for the added sum:

`C_extra <= 9 * 2 * 1024 * 384 = 7,077,888`.

Thus:

`C_RSRF <= 806,310,799,853`
and
`C_RSRF/B <= 0.36666770022429773`.

Raw-MSE break-even relative to V25:
`C_parent/C_RSRF = 0.9999912218861495`.

The exact-small admission gate is much stricter:
`MSE_RSRF/MSE_parent <= 0.95`.
At that gate the projected adjusted-score ratio is < 0.951.

No cost saving is assumed.

## 5. Single-run ordering

Only one standard free `ubuntu-24.04` Actions run is permitted. Repository visibility
is public; no paid runner/resource is authorized.

Within that one run the ordering is mandatory:

1. install pinned Python/NumPy/flopscope/whestbench;
2. fetch and git-blob verify pinned upstream V25;
3. run the **unchanged pinned V25 parent** on every frozen synthetic fixture;
4. if any parent fixture fails to execute or becomes non-finite:
   **R238_BASE_INCONCLUSIVE**, write evidence, do not construct candidate, do not
   resize/change fixture, do not run mini-100;
5. only if every parent fixture passes, construct the exact one-patch RSRF candidate;
6. freeze candidate predictions and deterministic replays;
7. only after predictions are frozen, construct exact target-free Gaussian truth;
8. apply all exact-small integrity/science/cost gates;
9. only `R238_SMALL_GO_RSRF` authorizes candidate validation + exactly one public
   `mini:all-100` run in the same Actions run;
10. no second Actions run, no rescue, no parameter/fixture change.

## 6. Frozen exact-small falsifier

Synthetic only. No benchmark/public targets/scorer are used in the falsifier.

Fixtures:
- width `n=12`;
- depth `L=10`;
- float32 estimator arithmetic;
- zero biases;
- Gaussian input `N(0,I_12)`;
- only input coordinates X0,X1 are live in the first layer;
- seeds `238120,238121,238122,238123`;
- first-layer weight scale `0.50`;
- later dense weight scale `0.65*sqrt(2/12)`.

Homologous compression settings for both unchanged parent source and candidate:
- `AGE_OLD=4`;
- `R_OLD=8`;
- `AGE_OLD2=7`;
- `R_OLD2=6`;
- `QPASS2=2`.

These are runtime class settings only; the fetched parent source bytes remain unchanged.
They are frozen before execution and used identically for parent/candidate.

At depth 10, tier-1 joins occur at layers 5..8. RSRF has three joins with prior Qp.
Conservative small extra bound:
`3*2*12*8 = 576 FLOPs`.

### Exact truth

Because only two Gaussian coordinates are active and all biases are zero, positive
homogeneity gives `F(Rq)=R F(q)`. The verifier recursively partitions angle
`[0,2pi)` at exact preactivation zeroes. Within each sector the network is linear in
`q=(cos theta,sin theta)`; integrate analytically and multiply by
`E[R]=sqrt(pi/2)`.

Sector cap: `200000`. Exceeding the cap is failure; no fixture modification.

## 7. Frozen exact-small gates

### Base prerequisite
All mandatory:
1. pinned parent git blob exact;
2. all four unchanged-source parent predictions execute;
3. parent predictions finite;
4. no benchmark/public/holdout/submission access before this gate.

Failure of any => terminal **INCONCLUSIVE**; candidate must not be constructed.

### Candidate integrity
All mandatory:
5. exact patch source block occurs once and only once;
6. candidate source differs only by the frozen RSRF lines;
7. candidate finite all fixtures;
8. bitwise deterministic replay exact all fixtures;
9. exact verifier finite;
10. final sector count <=200000;
11. candidate final prediction differs from parent on at least 3/4 fixtures.

### Scientific
All mandatory:
12. pooled `MSE_RSRF/MSE_parent <= 0.95`;
13. RSRF beats parent on at least 3/4 fixtures;
14. worst per-fixture `MSE_RSRF/MSE_parent <= 1.05`.

### Cost
All mandatory:
15. measured candidate-parent small FLOP delta is nonnegative and <=576;
16. production upper reconciles to `806310799853`;
17. production upper < budget;
18. pooled MSE ratio < production raw-MSE break-even `0.9999912218861495`.

All pass => **R238_SMALL_GO_RSRF**.
Any candidate/integrity/science/cost failure after base pass =>
**R238_SMALL_NO_GO_RSRF** and mini-100 is forbidden.

## 8. Conditional mini-100

Only `R238_SMALL_GO_RSRF` authorizes one candidate mini-100 in the same Actions run.

Exact command uses:
- candidate generated by the frozen falsifier;
- dataset `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`;
- split mini;
- streaming;
- n-mlps 100;
- runner local;
- flop budget `2**41`;
- wall limit 120 s;
- residual limit 0.4 s;
- max threads 1;
- pinned whestbench/flopscope/NumPy.

Existing normalized V25 is the parent; parent is not rerun on mini.

Mini acceptance, all mandatory:
1. exactly 100 rows and exact public mini panel;
2. failures = 0;
3. mean raw final MSE < `2.228303490170447e-8`;
4. mean official adjusted score <= 0.995 * `8.170397440117225e-9`;
5. all measured per-network FLOPs <= production upper `806310799853`;
6. no row adjusted-score ratio vs normalized V25 > 1.10;
7. candidate adjusted score beats normalized V25 on at least 60/100 rows.

If mini runs and any gate fails: terminal **SCIENTIFIC_REJECT** for frozen RSRF.
If all pass: report **R238_MINI_GO_RSRF**; no submission or canonical edit is authorized.

## 9. Explicit prohibitions

- no DRRE/Richardson/rescue;
- no fixture/rank/seed/weight-scale change after start;
- no second Actions run;
- no paid compute;
- no private/holdout data;
- no competition submission;
- no canonical V25 edit;
- no tuning on exact-small truth or mini outputs;
- no leaderboard/rank inference.
