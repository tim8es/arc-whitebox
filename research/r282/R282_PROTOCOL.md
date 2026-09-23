# R282 Protocol — recover retained V25 residual vectors from existing artifacts

Job: R282  
Owner: `r209-artifact-recovery`

## Scope

Search only already-existing public GitHub Actions runs/artifacts and committed R209/R223 material for raw V25 predictions, targets/truth vectors, or equivalent tensors sufficient for the R278 fixed global residual-direction diagnostic.

No new Actions, no reruns, no benchmark dataset download, no paid resource, no private/holdout/full data.

## Pinned references

- R209 dependency: COMPLETE.
- R209 canonical public mini:all-100 source: `research/results/R209-v25-mini100.json`, blob `0183d0570f7c9965e00e8553ffc003c313865232`.
- R209 V25 source commit: `dff3dd65e9d2210e02418cca99e05556f6bf2c75`.
- V25 source blob: `195373a110215256b759d7c172ba8c923c62e5cc`.
- Pinned evaluator/meter from R209: WhestBench 0.16.1; FlopScope 0.12.1+np2.4.6.
- R278 receipt commit: `83dfbe710cad5fbb1cab6e5b6fce0ccd06d47966`.
- Required residual objects: per-network final prediction vector and exact final target vector, or an exactly equivalent residual vector, with stable network identity and provenance.

## Search order

1. R209 run `35544406064`: list all artifacts/logs and inspect every retained file manifest/name/size.
2. Other already-existing R209 public run artifacts referenced by committed R209 material.
3. R223 committed material and any existing public run artifacts referenced there.
4. Related immutable artifacts only where their provenance explicitly ties them to the same pinned V25/evaluator and exact public mini panel.

## Recovery acceptance rule

A recovered object is usable only if all are true:

- exact run/source/evaluator provenance is identifiable;
- per-network identity maps unambiguously to the R209 100-row panel;
- vector dimensionality/dtype/semantics are known;
- target/prediction relationship is exact enough to reconstruct `target_final - prediction_final`;
- file size and SHA256 can be recorded;
- no hidden/private/full data is mixed in.

Anything less is logged as insufficient, not inferred.

## If absent

Report the exact missing object(s) and retain R278's minimal faithful future capture point: inside WhestBench 0.16.1 `evaluate_estimator()`, after failure zeroing and after `pred_np`, `final_pred`, and `final_target` exist, before MSE aggregation.
