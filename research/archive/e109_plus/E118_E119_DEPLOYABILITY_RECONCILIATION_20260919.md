# E118 proof vs E119 deployability reconciliation — 2026-09-19

Snapshot: `ARC-ARCHIVE-E118-E119-DEPLOYABILITY-20260919`

This archive update is append-only. It does not modify source experiment branches, `research/bootstrap`, or `research/ledger.csv`.

## E118 proof is not E119 deployability

The archive keeps the two scientific claims separate.

### E118B — output-specific compressed flux proof

Unique UID:

`ARC-HYP-20260919-E118B-OUTPUT-SPECIFIC-FLUX-SKETCH`

This is the strongest positive E118 proof record.

Evidence chain:

- protocol: `17a1a0f8422cc70824e064703653a3b3c14acc92`
- implementation: `2de68e5e2010564c2dde26304a988abc7c8333f7`
- frozen workflow: `7986e1b525bf6e6de20d2b4d16d5e1dd750b9a83`
- arm: `4f7bae911dcfa85e4e96c39b599d639622602f9c`
- run/job: `35457418719 / 105935065614`
- artifact: `10588194482`
- artifact SHA256: `f88ca8168f9b938081bd63a8667012872f61b2d8ae7039ace341cbcf45fc41d3`
- result: `2d577c8df161a3daf85e551bea7c591515b4c0a0`
- sealed receipt: `5db88d151cef14fa32bfbc146188a0cdf10e0f4f`

The representation stores 1024 scalar atoms, uses no full-mask enumeration, and has pooled exact-reference bias MSE `1.7613237067793404e-12` on the frozen four-network corpus. Its preregistered production upper bound is utilization `0.03352373675443232`.

Classification:

**VERIFIED PROOF-LEVEL SMALL-CORPUS GO**

but **not production GO** and **not competition GO**. No production-shaped scientific accuracy run exists.

### E118A — physical best-first compression

Unique UID:

`ARC-HYP-20260919-E118A-PHYSICAL-BOUNDARY-FLUX-COMPRESSION`

Run `35457354702` / job `105934894435` / artifact `10588344207` is terminal NO-GO.

At the frozen 62-transition cap:

- actual scalar error = `0.11816601715407549`
- RMS limit = `0.000137477270849`
- actual error / limit = `859.5313`
- rigorous remainder certificate / limit = `12587.4567`
- unresolved states = `29`

This negative result is preserved separately from E118B.

## E119 deployability bridge

Unique UID:

`ARC-HYP-20260919-E119A-GENERIC-BOUNDARY-FLUX-CERTIFICATE`

Evidence chain:

- frozen protocol: `4b7b8fa36e0d61ee45f172d1ab130825cb432e35`
- frozen implementation: `3eadbd7bf1c8d0522868b0ebd9f7d81d6b710c18`
- tests: `5f58ac2c1867eb836d2b4f53e2bf1437406e5033`
- frozen harness: `e17ed9efd5d6352e193b9bb8540f3446248671ca`
- workflow: `c8d382a30a7601ef888478da0dcd62d3a1f3a244`
- arm: `d731e845c96d401ac001da82c8998c06a03ec484`
- run/job: `35458020001 / 105936659806`
- artifact: `10589345345`
- artifact SHA256: `7485a4380bca0175197afeb327aed9abeb2f5d14ca335cdff6571ad0c7ed78e3`
- result: `9f1994a16526d76f55ee5e9bfb09e41786048c9e`
- sealed receipt: `de346277894ccb89ceef39e76ca6d8f12853b2ee`

What E119 actually verifies:

- generic weight-driven region construction for input dimension 2, width <=8, depth <=4;
- exact matching of frozen E114/E118 small-width boundary geometry and scalar flux;
- computable rigorous omitted-flux certificate;
- deterministic accounting.

What it does **not** establish:

- material boundary compression;
- width-1024/depth-16 deployability;
- production scientific accuracy;
- competition accuracy.

The certificate omits only one zero-flux periodic atom per frozen network; 98.18%-98.80% of atoms remain. Therefore:

**GENERIC CONSTRUCTION + CERTIFICATE VERIFIED; MATERIAL COMPRESSION / PRODUCTION DEPLOYABILITY NOT ESTABLISHED.**

## Independent support receipts

Two support audits are archived separately:

- E118 deployability audit: run `35457278466`, artifact `10588359138`, receipt `462725994f992f1207bec9a9f771636d731b3abd`.
- E119 independent physical-boundary audit: run `35457993173`, artifact `10588514800`, receipt `d553cb2b812d93796e947901823cb47c65b28dd5`.

Both block production authorization for the physical boundary-enumeration route.

Machine-readable source:
`research/archive/e109_plus/E118_E119_DEPLOYABILITY_RECONCILIATION_20260919.jsonl`
