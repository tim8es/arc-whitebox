# R262 independent audit — R260 target-free evidence

Status: **COMPLETE / R260 SCIENTIFIC_REJECT VERIFIED / NO RERUN**

R262 independently audited frozen R260 commit `5b2be00dc92ff4d0ced32bfaf67f6a691cadd967`. No estimator execution or Actions dispatch occurred.

## Integrity

Committed blobs: protocol `745b76fae2b57cd5b3231a731ebd3d7f7ff7b0d6`; frozen manifest `a3f169799c45d222b707167e2ebb9c93f83bcca0`; receipt `6aa4d9827a068fd14c2e516c148d4e8018a1caf7`; terminal report `16fc2f81b99d0c85b74cdf89d053d51beecfd175`; artifact index `2f785ae84d3382c878ac9ebedb2b88f3163a2f5b`.

Artifact 10741778766 ZIP SHA256 independently recomputed as `5f5522220664c028bef19906d66213826061bd85758ca63e01934f59aef9e22d`. All 26 entries in `R260_ARTIFACT_HASHES.json` independently recomputed with zero mismatches.

## Frozen target-free gates

From immutable `R260_TARGET_FREE_RESULT.json`: parent/candidate final MSE `0.06571899191579027` / `0.06574015420536944`, recomputed ratio **1.0003220117801912 > 0.95 FAIL**. Parent/candidate all-layer MSE `0.032378284555651254` / `0.032379599124054775`, recomputed ratio **1.0000406003104108 > 0.98 FAIL** (stored value 1.0000406003104105 differs only by floating-point last bits).

Per-layer ratios: `[1.0,0.9999999958857602,0.9999999991753694,1.0000000022477689,0.9999999872314507,0.9999999310657202,0.9999999095828702,0.9999998986180056,0.9999997583938911,0.9999998710043455,0.9999997496267689,0.9999996029063719,0.9999993916698338,0.9999993904500915,0.9999998076999257,1.0003220117801912]`. Improved layers = **13 >= 12 PASS**; max degradation = **1.0003220117801912 <= 1.10 PASS**. FLOP ratio = **1.0 PASS**. Residual limit = `1.05*0.32413096299903543+0.005 = 0.3453375111489872 s`; candidate `0.31171112699985315 s` => **PASS**. Shape `[16,1024]`, finite layers, zero symmetry residual and frozen source identities pass.

Only failures are exactly `final_mse_ratio` and `all_layer_mse_ratio`.

## Workflow/science and public skip

Official GitHub run 35843525739 attempt 1 at head `ed4ffbe1029d08cdc48648dc7a2877df308bba3d` concluded **success**. Immutable evidence says `candidate_go=false` and `SCIENTIFIC_REJECT_TARGET_FREE`. These are coherent: workflow success preserved terminal evidence and is not a scientific GO.

R260 receipt records validation=false, R209 identity access=false, mini100=false, public measurements=0 and public gate=false because target-free candidate_go=false. This matches the frozen protocol's fail-closed ordering.

## Verdict

**R260 terminal scientific rejection is independently verified.** No material discrepancy found. R260 remains terminal; this audit authorizes no rerun, repair, public execution, or new hypothesis.
