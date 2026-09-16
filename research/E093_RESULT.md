# E093 Result — terminal NO-GO / DROP

Branch: `research/e093-deep-strassen-leaf-feasibility-20260917`

Canonical base: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`

Protocol commit: `177b2c08fe97f734eff195b1ed59f0c804e51347`

Implementation/workflow commit: `03a1b2e5296897888d0307f262f6a6946205db07`

## Frozen Stage-A evidence

- GitHub Actions run: `35158764675`
- job: `105004365117`
- artifact: `e093-stage-a`, ID `10471909740`
- artifact SHA256: `52a08ab898dd55c857ce2a71e5bb2021f3b20195ca3b71a0646feec2fdaa8e39`
- upstream V29 blob: `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`
- width/depth/seed: `1024 / 16 / 93093`
- budget: `2^41 = 2199023255552`

Observed exact V29 reproduction:

- `predict_flops = 587262754287`
- reference E051 `predict_flops = 587262754287`
- reference drift = `0.0`
- finite = `true`
- deterministic = `true`
- deterministic max abs = `0.0`
- intercepted matmul calls = `1085`
- independent conventional matmul arithmetic estimate = `535480902656`

The transparent call profiler found no top-level `32x32x32`/`<=32` matmul calls. The current V29 fused leaf arithmetic is therefore not exposed as the proposed standalone leaf call class at the instrumentation boundary. This by itself fails the frozen `leaf32_present` gate.

More importantly, an instrumentation-independent impossibility bound kills the mechanism class even under assumptions much more favorable than reality. Five extra Strassen levels reduce multiplication count by at best `(7/8)^5 = 0.512908935546875` if **all Strassen additions are treated as free**. Pretending **100% of all V29 billed FLOPs** are eligible for that reduction gives:

- fantasy lower-bound utilization = `0.13697550193122476`
- required utilization = `<= 0.135`

Thus even a physically impossible best case misses the target before recursive-Strassen additions, non-matmul arithmetic, memory traffic/residual time, or ineligible operations are counted.

The exact 32x32 recursive arithmetic model also shows deeper recursion is not free:

- depth 0: `65536`
- depth 1: `61952` (`0.9453125x`, best)
- depth 2: `62848`
- depth 3: `70688`
- depth 4: `89896`
- depth 5: `128312` (`1.9578857421875x`)

So full 32->1 recursion is actually more expensive once additions are honestly billed.

## Frozen decision

`terminal = NO-GO / DROP`.

E093 may not proceed to Stage B. No implementation, alternate leaf classification, different recursion depth, tuning, widening to other operation classes, rerun, or rescue is authorized under this experiment ID.

No public/public-mini dataset, official scorer, holdout/full split, benchmark labels, target fitting, sweep, canonical mutation, or merge was performed.
