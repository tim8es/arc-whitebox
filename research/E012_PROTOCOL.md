# E012 Pair-Batched Joiner Transform Feasibility Protocol

Status: preregistered local cost/accuracy diagnostic.

## Objective

Test whether V29's exact A/P joiner-range-finder transforms can be scheduled as a two-item batch on the already-interleaved `(A,P)` storage, reducing flopscope wrapper/residual overhead without changing the mathematical estimator or metered arithmetic.

This is a feasibility screen only. It must not invoke the official `whest` scorer, the 100-MLP mini run, or any holdout.

## Provenance and isolation

- Canonical base: `research/bootstrap` commit `52eacc67dcc9af4813136ff641ea9b71c36c626f`.
- Branch: `research/e012-batched-joiner-transforms`.
- Upstream V29 reference: `504aldo/whest-p2-cumulant-k3` commit `18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.
- V29 blob: `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`.
- E010 is already canonical DROP because its frozen V29 mini run reached only 64/100 and showed residual-exhaustion failures; E012 does not rerun or alter E010.
- E011 is closed conceptually: no Hopcroft-Kerr leaf arithmetic, no block-size/rank schedule reuse.

No edits to E003, E006, E010, or `research/ledger.csv` are permitted.

## Frozen scientific comparator

Best locally reproduced scientific frontier remains E007 / V25:

- adjusted final-layer score: `8.17e-09`;
- raw final-layer MSE: `2.23e-08`;
- mean compute utilization: `0.36666448`;
- failures: `0/100`.

E012 changes only exact scheduling. Therefore any later scorer-level promotion, if separately authorized, must preserve the E007 scientific point: failures `0/100`, raw MSE within 1% of `2.23e-08`, utilization no worse than `0.36666448`, and adjusted score no worse than `8.17e-09`. These values are reference-only in E012; no scorer is authorized here.

## Repository evidence and mechanism

Pinned V29 stores source legs interleaved as `(slot, 2, n, n)`, with `[:,0]=A` and `[:,1]=P`. At each old-source join, the current code evaluates the two weighted Gram actions separately:

`A @ (dA * (A.T @ Omega))`

and

`P @ (dP * (P.T @ Omega))`.

The A/P pair is already contiguous in the interleaved leg slab, so no new staging copy is required to treat it as a leading batch dimension.

E012 candidate replaces only the scheduling of those two independent terms:

```text
AP      : (2, n, n)        # existing interleaved A/P view
weights : (2, n, 1)        # dA, dP
Omega   : (n, r)

inner = matmul(AP^T, Omega)       # (2,n,r), one batched call
inner = inner * weights           # one batched multiply
outer = matmul(AP, inner)         # (2,n,r), one batched call
Y     = outer[0] + outer[1]       # exact two-term reduction
```

The baseline performs the same work as two separate A and P paths. Mathematical FLOPs are identical; only call scheduling changes. No Strassen recursion is implemented in E012. The point of the diagnostic is to determine whether pairing is a credible way to reduce the residual cost of any later Strassen-priced joiner family.

## Frozen diagnostic shape

Use one Phase-2 competition-shape synthetic joiner kernel:

- `n = 1024`;
- `r = 384` (V29 `R_OLD` tier-1 rank);
- dtype `float32`;
- deterministic seed `20260914`;
- `AP.shape = (2,1024,1024)`;
- `weights.shape = (2,1024,1)`;
- `Omega.shape = (1024,384)`.

The tier-2 rank 224 is provenance context only. No second-shape run or rank sweep is allowed under E012.

## Baseline implementation

The comparator is exactly:

```text
tA = A.T @ Omega
tA = tA * dA
yA = A @ tA

tP = P.T @ Omega
tP = tP * dP
yP = P @ tP

Y_baseline = yA + yP
```

Every numeric operation must use `flopscope.numpy`, with preallocated `out=` buffers where supported.

## Candidate implementation

The candidate is exactly the two-item batched form above, using the existing interleaved AP layout and preallocated buffers. There is no copy/stack/concatenate allowed in the measured hot path.

## Metrics

Measure after one warm-up of each exact operation signature:

1. relative Frobenius error `||Y_batch-Y_sep||_F / ||Y_sep||_F`;
2. bitwise determinism across two identical candidate runs;
3. metered FLOPs for baseline and candidate;
4. participant residual wall time for baseline and candidate;
5. wrapper/backend/wall time for context;
6. additional persistent scratch bytes;
7. measured flopscope-call count from the explicit schedule: baseline 7 numeric calls, candidate 4 numeric calls.

## Preregistered GO gate

GO requires all conditions simultaneously:

1. relative Frobenius error `<= 5e-7`;
2. bitwise deterministic repeated candidate output;
3. candidate metered FLOPs `<= baseline metered FLOPs`;
4. candidate residual wall time `<= 0.70 * baseline residual wall time` (at least 30% reduction);
5. candidate added persistent scratch `<= 8 MiB` beyond the existing AP/Omega/weights inputs;
6. no measured-path `stack`, `concatenate`, host NumPy arithmetic, native-code helper, or data-dependent branch.

The residual ratio is the primary feasibility metric. A 30% local reduction is required because the public V29 report identifies roughly `+74–118 ms` residual as the blocker for pricing-polish/joiner Strassen work; a marginal single-digit-percent change is not enough to justify estimator integration.

## Kill rule

If any GO condition fails, E012 is `NO-GO` and stops immediately.

No retry, seed change, rank-224 run, shape sweep, alternative batching width, Strassen depth test, operation fusion variant, scorer run, or holdout is allowed under E012. Any materially different schedule requires a new experiment ID.

## Interpretation boundary

A local GO does not claim improved ARC score. It only establishes that an exact two-item scheduling primitive materially reduces residual overhead at equal billed arithmetic and is worth a separately preregistered estimator integration test.

A local NO-GO closes this batching primitive; it does not alter E007, E010, or any canonical estimator result.
