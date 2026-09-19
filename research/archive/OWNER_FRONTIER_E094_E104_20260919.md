# ARC research owner archive receipt — E094..E104 unified frontier

Receipt key: `ARC-OWNER-FRONTIER-E094-E104-20260919`

Archive branch: `research/owner-frontier-e094-e104-20260919`

Canonical reference: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`

Canonical ledger blob at archive creation: `research/ledger.csv@e2c39bf39b1365e5293f44e0dff1d9b9bdaaaf1c`

This is an append-only owner reconciliation receipt. It does not merge experiment branches, rerun scientific workflows, mutate canonical, mutate the ledger, grant public access, or overwrite any experiment-local result.

## Identity firewall

The archive uses branch/protocol chronology rather than bare experiment numbers where collisions exist.

- **E091 is not part of this E094-E104 frontier receipt.** No E091 result, identity, metric, calibration, or receipt is folded into E100 or E104.
- **Authoritative E100 frontier identity** is `research/e100-orthogonal-gaussian-antithetic-20260918`, because its protocol-first commit `e94a485b80a3e89bcb564dd43106727bea77450f` predates the conflicting later same-ID shrinkage protocol `d113433552638818688516f9c8d0526ecbd51341`. The branch `research/e100-crossfit-two-subspace-shrinkage-20260918` remains a separate historical same-ID collision and is **not** used as the E100 frontier identity here.
- **Authoritative E104 frontier identity** is `research/e104-haar-radial-raoblackwell-20260918`, receipt key `ARC-E104-HAAR-RADIAL-RAOBLACKWELL-20260918`. The separate branch `research/e104-orthogonal-antithetic-complete-billing-20260918` is not merged into the Haar/Rao-Blackwell E104 identity and contributes no evidence to the E104 scientific GO recorded below.
- E098 has two same-ID terminal branches. Both are terminal NO-GO variants; their metrics are not merged. The owner frontier uses only the common conclusion that the tested late-K22 fixed-response family did not promote.

## E094-E104 reconciled status

| ID | Authoritative evidence / branch | Owner status | Frontier consequence |
|---|---|---|---|
| E094 | `research/e094-source-axis-joint-compression-20260917@8a76ae3a9cbfcf2c6b01b7cb17a91718c4859f91` | **TERMINAL NO-GO / DROP** | Stage-A algebra passed, but the frozen official-shape V29 spectrum probe failed before source-spectrum capture because the exact baseline became non-finite. No claim about real source-axis rank. |
| E095 | `research/e095-output-subspace-residual-sampling-20260917@855db7eafb9a7f79f1d069b4171973951200670f` | **TERMINAL NO-GO / DROP** | Rank-6 projected residual beat covariance but lost to the same 2048-sample full mean on 0/8 networks. Hard output-subspace projection is closed. |
| E096 | `research/e096-v29-matmul-callsite-attribution-20260917@4fde205a835f509769674d5059631d407549d54a` | **COMPLETE / VALID ATTRIBUTION** | 91.18% matmul coverage; source transport/hub dominate. No local top-callsite optimization can by itself reach util <=0.135. Evidence only; no estimator promotion. |
| E097 | `research/e097-rank8-k22-memory-feasibility-20260917@a0977fabb97e0c096d63203b9a34deadd494ee0c` | **TERMINAL NO-GO / DROP** | Persistent rank-8 K22 memory fails representation gates despite cheap transport; late-depth low-rank structure motivated the separately tested E098 family. |
| E098 | `research/e098-late-k22-edgeworth-response-20260918@b104198343551725182319688cdc8824dec0ff6b` plus independent same-ID relevance branch | **TERMINAL NO-GO / DROP** | Late K22 is compressible, but the frozen pair-K22 fixed Edgeworth/response correction worsened Gaussian closure in aggregate; compression was not the blocker. |
| E099 | `research/e099-shared-latent-2g-closure-20260918@6bd0db022c097d92c7b1d6de338a3dd50dc6ac08` | **TERMINAL STRUCTURAL NO-GO** | Exact shared two-point latent skew matching forces non-PSD residual covariance at width 1024. |
| E100 | `research/e100-orthogonal-gaussian-antithetic-20260918@49ed8dc17de34463deea254da7d113f7fc828b97` + append-only cost correction `review/e100-orthogonal-cost-correction-20260918@1fd08b93c3c2f5a05bbf2d9058a560c1a8e1cc65` | **LOCAL STAGE-A GO + INDEPENDENT REVIEW PASS; scientific_go=false** | Haar-QR + chi-radius antithetic sampling gave pooled synthetic MSE ratio 0.18833 vs iid and 8/8 wins. Marginal-law proof/review passed. Original QR cost line is superseded; corrected conservative envelope 151B FLOPs / util 0.06866685 remains feasible. Production/public accuracy remained unexecuted under E100. |
| E101 | `research/e101-multilatent-skew-rank-bound-20260918@ddbf3cece1da0c9721043cec3d5bc6cdf2ca0504` | **TERMINAL ANALYTIC NO-GO** | Exact independent-binary multi-latent skew closure needs at least 741 latent dimensions at width 1024; compact explicit mixture closure closed. |
| E102 | `research/e102-k3-tensor-rank-bound-20260918@015c5103546ebac6b5a56cbe3992aca552fcd04b` | **TERMINAL ANALYTIC NO-GO** | Exact additive independent scalar-latent representation of full first-layer K3 needs at least 1024 factors. |
| E103 | `research/e103-orthogonal-antithetic-production-shape-20260918@051e4f391fe86bac93949bb67788160ccbc26ce0` | **SEALED; execution VERIFIED, complete accounting NOT VERIFIED, scientific_go=false** | Sole width-1024/depth-16/N=4096 run succeeded. The original measured FLOP claim omitted NumPy RNG outside flopscope. Corrected minimum is 149,114,620,592 FLOPs / util 0.0678094787, still safely below gates. Package-safe complete billing is not verified. Production/public accuracy is UNEXECUTED. |
| E104 | `research/e104-haar-radial-raoblackwell-20260918@95c353cc9cc6ca15837fc3da5d2cdd22d2ee2323` | **LOCAL SCIENTIFIC GO; PRODUCTION-SHAPED UNEXECUTED** | Exact Rao-Blackwellization removes random chi radii under positive homogeneity. Frozen local Stage-A passed all gates: pooled E104/E100 same-direction MSE ratio 0.83356888, 6/8 wins. A frozen independent production verification spec exists, but no production-shaped E104 workflow/run has executed. |

## E103 accounting correction — authoritative interpretation

The execution facts from E103 remain valid:

- run `35287256818`
- job `105422236549`
- artifact `10525181002`
- artifact ZIP SHA256 `2141c794724b30e706822f1b1a04d61a73bb7d979db04d7c078933e73099630f`
- output shape `(16,1024)`
- finite = true
- exact antithetic pair max abs = `0.0`
- originally reported flopscope FLOPs = `149047446192`

The authoritative append-only correction is:

- two `1024 x 1024` Gaussian RNG matrices and two chi-radius vectors were generated by plain NumPy outside flopscope;
- minimum omitted RNG bill = `67,174,400` FLOPs;
- corrected minimum = `149,114,620,592` FLOPs;
- corrected minimum utilization = `0.06780947869265219`;
- cost feasibility remains VERIFIED analytically below both 0.12 and 0.135;
- complete package-safe flopscope billing remains **NOT VERIFIED**;
- E103 is sealed and must not be rerun/rescued.

Do not reuse the unqualified phrase “E103 measured complete utilization = 0.0677789”. That number is an incomplete flopscope ledger.

## E104 local scientific GO — production boundary

Authoritative local evidence:

- Stage-A run `35287541033`
- job `105423103388`
- artifact `10524219347`
- artifact ZIP SHA256 `37fc50e20a084aa1e59a59443da9ce7022a2dbee13a88e7d643970d291af4301`
- pooled same-direction E104/E100 MSE ratio `0.8335688800492203`
- E104 wins `6/8`
- worst ratio `1.170455041103274`
- deterministic replay delta `0.0`
- exact antithetic pair max abs `0.0`
- all finite

The scientific identity is stronger than a fitted/tuned variance observation: for zero-bias ReLU networks, positive homogeneity and Gaussian polar decomposition make analytic replacement of each independent chi radius by `E[R]` the conditional expectation of the E100 estimator given Haar directions. This preserves expectation and cannot increase exact-arithmetic coordinatewise variance.

**Classification: E104 LOCAL SCIENTIFIC GO.**

Production boundary at archive time:

- frozen independent production verification spec exists at `research/E104_PRODUCTION_VERIFY_FREEZE.json`;
- frozen shape is width `1024`, depth `16`, trajectories `4096`, weight seed `104104`, direction/setup seed `104105`;
- required verifier is an independent reimplementation with exact prediction and FLOP-ledger deterministic replay;
- production/public/holdout/scorer targets are prohibited by the freeze;
- branch action history contains only the Stage-A run above;
- **E104 production-shaped status = UNEXECUTED**.

No E103 production result may be relabeled as an E104 production run.

## Unified frontier

Closed / non-promotable families:

1. V29 local-callsite arithmetic reduction alone: insufficient by E096.
2. Source-axis compression path as frozen in E094: terminal on its official-shape gate.
3. Persistent or late fixed-response K22 mechanisms: E097/E098 closed.
4. Exact compact independent-latent skew/K3 closures: E099/E101/E102 closed.
5. Hard projected residual sampling: E095 closed.
6. The later same-ID E100 plug-in shrinkage collision is not part of the authoritative orthogonal-sampling frontier and is not a rescue path.

Live promoted scientific frontier:

`E100 orthogonal Gaussian antithetic law -> E103 production-shape packaging/accounting bridge -> E104 Haar radial Rao-Blackwellization`.

Evidence strength along that chain:

- E100: local Stage-A GO + independent law review PASS; no scientific_go/public accuracy.
- E103: production-shape execution verified; accounting correction required; complete billing and accuracy unresolved.
- E104: local scientific GO by exact conditional-expectation mechanism + frozen synthetic confirmation; production-shaped verification not yet executed.

The only unresolved active gate in this receipt is therefore the **frozen E104 independent production-shaped verification**. No new method family, new experiment ID, public diagnostic, scorer, holdout/full run, or successor scientific task is assigned before that production receipt exists.

## Owner sequencing rule

**Current action only:** execute the already-frozen E104 production independent verification exactly as `research/E104_PRODUCTION_VERIFY_FREEZE.json` specifies, without mechanism/seed/shape changes.

**Post-run next step:** intentionally **UNASSIGNED** in this receipt. The research owner must inspect the immutable E104 production run/job/artifact/FLOP ledger first. A successor action may be assigned only after that evidence is archived.

## Scope / mutation check

- public/public-mini: none
- official scorer: none
- holdout/full: none
- tuning/sweep: none
- canonical mutation: none
- ledger mutation: none
- experiment-branch merge: none
- E103 rerun: none
- E104 production run: none at receipt time

This receipt is archival reconciliation only and must not be cited as scientific evidence beyond the underlying experiment receipts it references.
