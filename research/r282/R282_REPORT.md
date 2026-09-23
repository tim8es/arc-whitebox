# R282 — existing-artifact recovery for V25 residual vectors

Status: **COMPLETE — NO RECOVERABLE RAW V25 RESIDUAL VECTORS**

Job: R282  
Owner: `r209-artifact-recovery`  
Run: `R282-r209-artifact-recovery-20260923`

## Scope

Read-only search of already-existing public GitHub Actions runs/artifacts plus committed R209/R223 evidence. No Actions were triggered, no benchmark dataset was downloaded, and no paid/private/holdout/full data was used.

## Important provenance correction to R278

R278's receipt labelled artifact `10617318650` as retained R209/V25 evidence. Live Actions metadata and the committed R209 archive audit show:

- `10617318650` = **e136-followup-v29**
- actual V25 artifact = **10617855153 / e136-followup-v25**

This does not change R278's substantive blocker: direct inspection of the actual V25 artifact also finds no raw prediction/target/residual vectors.

## R209 run 35544406064

Run:
- Actions run: `35544406064`
- head: `dff3dd65e9d2210e02418cca99e05556f6bf2c75`
- V25 source blob: `195373a110215256b759d7c172ba8c923c62e5cc`
- evaluator: WhestBench `0.16.1`
- meter: FlopScope `0.12.1+np2.4.6`
- panel: public `v2-phase2 mini:all-100`

Actual V25 artifact:
- id: `10617855153`
- name: `e136-followup-v25`
- size: `106,494` bytes
- ZIP SHA256: `820bf9368beac10ea537fc018c3c2185bbd310b9542603cbfa8309519c8e3e08`
- `report.json`: `1,015,117` bytes
- `report.json` SHA256: `68683f9f2e8eca89a85fd18826998f5937d4770c2ce33bf6e6738fb236c8e5a3`

The archive contains only:
`environment.txt`, `report.json`, run/validate exit+stderr files, `sha256.json`, and `whest_version.json`.

The 100-row `report.json` contains scalar per-MLP metrics, FLOPs/failure/timing/breakdown fields and `per_layer_mse` vectors of length 16. There are **no numeric arrays of length 1024 or 16384**, and no prediction, target, truth, or signed residual tensor fields.

The committed R209 archive audit already records `raw_prediction_vectors_archived=false`.

## Target fingerprints

R209's normalized record binds the public panel to R224 fingerprint run `35788780990`.

Existing fingerprint artifact:
- id: `10720913493`
- size: `9,297` bytes
- ZIP SHA256: `28feb5da04d3508b86a8b7afddc39a35f9a57a61bad76c0f63fbf3a2ee6de686`
- `R224_MINI100_FINGERPRINTS.json`: `36,337` bytes
- file SHA256: `ae0b3659568cc1297aeac89f6babf9f2df2b2752d0216e638141ec6411f629a4`

It contains 100 records with `network_id`, target dtype/shape and `target_sha256`, but **not target bytes**. SHA256 authenticates the target array but cannot reconstruct its signed coordinates.

## R223 attempt 6

The only R223 attempt that invoked the candidate mini-100 panel was Actions run `35810427656`; R240 confirms attempts 1–5 had zero panel invocations.

Attempt-6 artifact:
- id: `10730459690`
- name: `r223-v25-local-feed-mini100-attempt6`
- size: `261,400` bytes
- ZIP SHA256: `f144bfd2a5a8a82aaa3e600d1f384d68cfe5e525eb7e22e91eb1d7e843763e00`

Key files:
- copied R209 parent report SHA256: `68683f9f2e8eca89a85fd18826998f5937d4770c2ce33bf6e6738fb236c8e5a3`
- candidate report SHA256: `72821cf9117b484b2cc4fe4affa21e08ece737e86813508d9c1c6d01b02f6710`
- paired result SHA256: `52c5da262f442d3a499c2c77885abc91f81d596e10703c1ac582192ffc8dda65`

Both reports again have maximum numeric vector length 16. The paired result stores only scalar per-network comparisons. No raw `float32[1024]` prediction/target/residual vectors are present.

## Committed normalized records

- `research/results/R209-v25-mini100.json`: 50,981 bytes; blob `0183d0570f7c9965e00e8553ffc003c313865232`; SHA256 `f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742`.
- `research/results/R223-v25-local-feed-mini100.json`: 33,401 bytes; blob `c8b617c43ff1145977c38e7e1cca6d23985ec392`; SHA256 `3c8633826ac2efb74db73ba7f5640ec34f0ebb8c91c517f0cf418b6794184587`.

They retain names/network IDs, scalar MSE/score/FLOPs/failures and target fingerprints. They do not retain coordinate-level prediction or target bytes.

## Exact gap

For R278's global residual-direction diagnostic, the missing object is, for each public Mini network, either:

1. V25 final prediction `float32[1024]` **and** exact final target `float32[1024]`; or
2. the exact signed residual `target_final - prediction_final`, `float32[1024]`.

Neither exists in the searched artifacts or committed R209/R223 material.

## Minimal correct future capture point

Use WhestBench 0.16.1 `evaluate_estimator()` from source commit `4d08668b485c8a7d25a105c3c00d2f4fc2538f18`, `scoring.py` blob `9cf7653a0267c4d048617c9045ac8be127f3c8bf`.

Capture runner-side **after all failure-zeroing checks**, after:

- `pred_np = fnp.asarray(predictions, dtype=fnp.float32)`
- `final_pred = pred_np[-1]`
- `final_target = data.final_targets[i]`

and before `final_layer_mse` aggregation.

Persist network identity, failure flags/FLOPs, exact `final_pred` and `final_target` bytes, dtype/shape and SHA256. This is outside the participant `predict()` BudgetContext and therefore does not change estimator FLOP accounting.

## Conclusion

**No recoverable raw V25 residual vectors exist in the searched existing evidence.** The gap is exact and coordinate-level; hashes and scalar MSEs cannot substitute for the signed residual vector required by R278.
