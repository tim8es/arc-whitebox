# ARC owner archive addendum — E104 production PASS and successor assignment

Receipt key: `ARC-OWNER-E104-POSTPROD-20260919`

Parent archive receipt: `ARC-OWNER-FRONTIER-E094-E104-20260919`

Parent archive commit: `fb63782afdac68b2131479d108542cf884f22d37`

This is an append-only chronological addendum. It does not rewrite the parent receipt. The parent receipt correctly recorded E104 production-shaped status as UNEXECUTED at its creation time. During subsequent final verification, the already-frozen E104 production verifier completed on the authoritative E104 branch. This addendum records that later state transition.

## Identity firewall

Authoritative E104 remains only:

- `research/e104-haar-radial-raoblackwell-20260918`
- protocol `f85ce2487ae953f20b611b327d2269f1c54548fc`
- local Stage-A result commit `785be77d27eb6770b251a87182184281fb571949`

The separate branch `research/e104-orthogonal-antithetic-complete-billing-20260918` remains outside this identity and contributes no evidence here.

E091 and the conflicting later same-ID E100 shrinkage lane remain outside the E104 chain.

## E104 production independent verification

Frozen verifier provenance:

- freeze commit `31ba85f3f55e5b860671c0fbfc73ebc05e75f426`
- implementation commit `68ee13214342056c216ed500abd9a5ea6a77f5c6`
- workflow/head commit `95c353cc9cc6ca15837fc3da5d2cdd22d2ee2323`

Execution:

- run `35446062235`
- job `105905067035`
- workflow conclusion `success`
- artifact `e104-production-independent-verify`
- artifact ID `10584569066`
- artifact ZIP SHA256 `3a22b369883b141be19528acec69df9165be627976152ad845e35c5f90320237`
- artifact size `1017` bytes

Frozen production shape:

- width `1024`
- depth `16`
- trajectories `4096`
- weight seed `104104`
- direction/setup seed `104105`
- radius `E[chi_1024] = 31.992188454829048`
- mechanism unchanged from E104 local scientific GO
- targets/public/scorer/holdout/full: none

Execution evidence, repeated twice:

- finite: true
- prediction shape: `(16,1024)`
- prediction SHA256: `ae0bfae00c7379673320a3a098c716272c7d9164588bcc73bd59bc7516c017e0`
- predictions bitwise equal across repeats: true
- prediction repeat max abs: `0.0`
- FLOP ledgers exactly equal: true
- exact antithetic pair max abs: `0.0`
- homogeneity relative error: `6.874805456226369e-7`

Complete flopscope reconciliation:

- input construction: `11,474,238,128`
- each of 16 layers: `8,598,323,200`
- layer total: `137,573,171,200`
- finalization: `32,768`
- exact reconciled total: `149,047,442,096`
- flopscope total: `149,047,442,096`
- utilization: `0.06777892944955966`
- utilization <=0.12: PASS
- utilization <=0.135: PASS

All frozen production verification gates passed.

## Updated E104 classification

- E104 local scientific GO: **PRESERVED**
- production-shaped independent verification: **PASS / VERIFIED**
- production implementation determinism: **VERIFIED**
- complete flopscope accounting for the independent verifier: **VERIFIED**
- production-shape synthetic execution: **VERIFIED**
- raw final-layer MSE <=1.89e-8: **UNEXECUTED / UNKNOWN**
- benchmark/public accuracy: **UNEXECUTED**
- global competition-level `scientific_go`: **false**

The E103 accounting defect is not inherited by this independent E104 verifier: E104 explicitly reconciled its full measured ledger exactly. E103 remains sealed with its own append-only accounting correction.

## Frontier transition

The active chain is now:

`E100 orthogonal Gaussian antithetic law -> E103 packaging/accounting bridge -> E104 Haar radial Rao-Blackwell local scientific GO -> E104 production independent verify PASS`.

The remaining blocker is no longer implementation shape, determinism, marginal-law mechanism, or production compute. The unresolved quantity is the absolute final-layer stochastic risk of the E104 estimator at production shape.

## Next assigned step — E105 only

Collision check at assignment time:

- branch query `e105`: none
- commit query `E105`: none
- issue query `E105`: none

Reserve the next research task as:

**E105 — target-free two-Haar-block production risk certificate.**

No branch or implementation is created by this archive reconciliation commit; this section is the owner assignment only.

### Scientific identity

For a fixed zero-bias production-shape network, let `B1` and `B2` be the two independent one-Haar-basis block mean estimators already underlying one E104 production estimate,

`M = (B1 + B2)/2`.

Because each block has the same unbiased expectation `mu` and the Haar blocks are independent,

`E[(B1_j - B2_j)^2 / 4] = Var(M_j)`.

Therefore

`Rhat = mean_j((B1_j - B2_j)^2)/4`

is a target-free unbiased diagnostic of the expected final-layer coordinate MSE of the two-block E104 estimator with respect to its direction randomness, for the fixed network.

This diagnostic requires no benchmark target, no public data, no fitted coefficient, and no change to the E104 estimator law. It measures the only unresolved frontier quantity directly: production-shape stochastic risk scale.

### E105 owner constraints

E105 must be protocol-first and direct from canonical, with fresh collision-checked branch identity. It must:

1. keep the E104 production law, width=1024, depth=16, and two-Haar-block estimator unchanged;
2. expose the two block means separately only for diagnostic accounting;
3. use synthetic zero-bias production-shape networks only;
4. freeze all network/direction seeds before execution;
5. measure `Rhat` at the final layer and deterministic replay;
6. keep complete flopscope accounting for the estimator path;
7. read no public/public-mini/scorer/holdout/full targets;
8. perform no tuning, seed/rank/sample sweep, or coefficient fit;
9. return an immutable run/job/artifact/digest receipt.

Pre-code mathematical gate is PASS by the identity above. Promotion beyond E105 is not assigned here and must depend on the measured E105 risk relative to the project raw target `1.89e-8`.

No public step is authorized by this addendum.
