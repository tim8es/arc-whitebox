# E091 disjoint transfer falsifier

Status: **EVIDENCE NO-GO / DATA ABSENT** on branch head `cf517ff79574f297da19218cbf752a873ea788cd` before this falsifier commit.

Scope: verify the frozen disjoint-transfer condition for the E091 production bridge without public/scorer/holdout/full access, without refit on B, and without changing the frozen feature map, lambda, base estimator, or corpus membership after targets exist.

## Frozen production state

The production pre-target freeze is `c8c214b5f41d25516ad71118fa787bb4aa704f7e` and selects E043 at `d0108f7faccaa656d3908f5afeaa90e056881c71` solely because it is the only screened E042-E044 production-shaped base with measured utilization <= 0.135. The frozen production feature map is `final_layer_coordinate_features_v1`, `p=16`, with ridge `lambda=1.0` and no target-dependent preprocessing.

The immutable production bridge receipt records:

- `new_disjoint_production_corpus = UNEXECUTED`
- `ridge_fit = UNEXECUTED`
- `synthetic_network_holdout = UNEXECUTED`
- `raw_target_le_1.89e-8 = UNEXECUTED`

The subsequent archive-reconciliation commit `cf517ff79574f297da19218cbf752a873ea788cd` independently repeats the same gaps as `UNEXECUTED` and explicitly names the next admissible task as freezing a disjoint synthetic-network corpus before target materialization.

The committed `research/E091_CORPUS_MANIFEST.json` is explicitly `purpose = local_reproducibility_only`; it is not a frozen A/B production transfer split. Re-splitting that already-materialized corpus now would make corpus membership post-target, which is forbidden by the E091 freeze.

Therefore there is no admissible committed B corpus and no frozen A-side beta on which the disjoint transfer gate can be evaluated without changing the protocol after target materialization.

## Exact transfer gate

Let the A-fitted ridge vector be frozen before B is materialized/evaluated. For B, with baseline residual coordinates `r` and frozen correction coordinates `s = Z_B beta`, define

`q_B = mean(r * s)`

`v_B = mean(s * s)`

Then

`MSE_B(r) - MSE_B(r-s) = 2 q_B - v_B`.

Hence the frozen correction improves B if and only if

`q_B > v_B / 2`.

No refit, lambda change, feature selection, scaling update, or B-side coefficient adjustment is needed or allowed for this check.

## Leakage/disjointness gates

An admissible evidence package must prove all of the following before the numeric gate is accepted:

1. production freeze commit equals `c8c214b5f41d25516ad71118fa787bb4aa704f7e`;
2. base commit equals `d0108f7faccaa656d3908f5afeaa90e056881c71`;
3. feature map is exactly `final_layer_coordinate_features_v1`;
4. ridge lambda is exactly `1.0`;
5. beta, feature preprocessing, lambda, and corpus membership are frozen before B targets;
6. calibration and evaluation corpus IDs differ;
7. root realization/network identity sets A and B are both non-empty and disjoint;
8. residual and correction arrays are finite and shape-identical.

## Runnable check

Run:

```bash
python scripts/e091_disjoint_transfer_gate.py
```

On the current branch this must terminate with exit code `2` and verdict `DATA_ABSENT_NO_GATE_EVALUATION` because `research/E091_DISJOINT_TRANSFER_EVIDENCE.json` does not exist and both repository receipts record the required transfer work as unexecuted.

When a properly frozen evidence package exists, run:

```bash
python scripts/e091_disjoint_transfer_gate.py --evidence research/E091_DISJOINT_TRANSFER_EVIDENCE.json
```

The script rejects metadata/freeze mismatch or A/B root overlap before computing the numeric gate. For admissible evidence it reports `q_B`, `v_B`, `v_B/2`, `delta_B`, baseline MSE, corrected MSE, and verifies the MSE identity in float64.

Exit codes are frozen as: `0=PASS`, `1=FAIL/INVALID_EVIDENCE`, `2=DATA_ABSENT`.

## Verdict

**E091 disjoint transfer is not established. DATA ABSENT is the concrete falsifier result on the current repository state.**

This is stronger than an unknown result: the repository's own pre-target freeze, production receipt, and later archive reconciliation prove that the required disjoint production corpus, A-side ridge fit, and B-side whole-network holdout have not been executed. The existing local/LOO synthetic evidence cannot be substituted for this gate without violating frozen corpus-membership rules.

No public/scorer/holdout/full result is inferred. No canonical or ledger mutation is authorized by this receipt.

## Single next admissible candidate

Freeze exactly one **E091/E043 whole-network synthetic transfer corpus** before generating any residual target: commit deterministic train-network seeds A, disjoint evaluation-network seeds B, teacher/reference procedure, root IDs, and the already-frozen E043/base/feature/lambda metadata. Then materialize targets once, fit beta on A once, and evaluate the single `q_B > v_B/2` gate on B with no rescue or resplit.
