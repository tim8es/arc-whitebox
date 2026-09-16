# E049 code-level delta: canonical -> frozen 504aldo V29

Frozen upstream: `504aldo/whest-p2-cumulant-k3@18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45`.
Frozen estimator blob: `estimators/estimator_v29.py` = Git blob `17df1a073a24f96c4705b04bcf61ef60fa06dd0c`, 93422 bytes.

## Mechanical delta

`methods/e049_v29_upstream.py` is byte-for-byte the upstream estimator. Algorithmic delta: **zero lines**.

Local canonical has no corresponding K3 source-factor transport implementation. Relative to `baselines/covariance_propagation.py`, V29 adds:

- factored K3 source state and fused D3/D21 contractions;
- memoryless K4 regeneration with the frozen V22/V25 lambda machinery;
- D21 rank-16 feedback thin legs;
- age-gated tier-1 old-source basis (`AGE_OLD=4`, `R_OLD=384`);
- nested tier-2 old-source basis (`AGE_OLD2=7`, `R_OLD2=224`);
- pooled recursive Strassen/Winograd transport (`STRASSEN_LEVELS=5`, minimum leaf side 32);
- V29 newborn/covariance slots riding the transport family and block-symmetric C_pre construction;
- final-layer trim and persistent scratch pools.

The E049 replay wrapper may only instantiate this exact class and measure it. It may not change environment kill switches, ranks, ages, lambda scale, beta, Strassen levels, precision, term tables, or numerical formulas.
