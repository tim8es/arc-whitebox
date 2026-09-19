# E119 evidence monitor control note — 2026-09-19

Receipt key: `ARC-CONTROL-E119-EVIDENCE-MONITOR-20260919`

Scope: control-only audit of E119 commits, runs, jobs and artifacts for oracle leakage, FLOP completeness, remainder-proof completeness and premature GO. No scientific workflow was dispatched or rerun by this audit. No public/public-mini/scorer/holdout/full access.

## Authoritative owner evidence

Authoritative owner lane:

`research/e119-generic-boundary-flux-certificate-20260919`

Protocol-first evidence:

- protocol initial: `cd52016d8313cda5456ea9978cf18d2fd2c916f5`
- implementation initial: `03fafce1a09c1fa2c86a744afa6716091a8d24ae`
- frozen accounting/implementation: `3eadbd7bf1c8d0522868b0ebd9f7d81d6b710c18`
- frozen harness: `e17ed9efd5d6352e193b9bb8540f3446248671ca`
- workflow: `c8d382a30a7601ef888478da0dcd62d3a1f3a244`
- arm/executed head: `d731e845c96d401ac001da82c8998c06a03ec484`

Physical evidence:

- run `35458020001`
- job `105936659806`
- artifact `10589345345` / `e119-generic-boundary-flux-certificate`
- artifact ZIP SHA256 `7485a4380bca0175197afeb327aed9abeb2f5d14ca335cdff6571ad0c7ed78e3`
- run conclusion `success`
- attempt `1`; no rerun

Owner post-run receipts:

- result `9f1994a16526d76f55ee5e9bfb09e41786048c9e`
- sealed receipt `de346277894ccb89ceef39e76ca6d8f12853b2ee`
- direct production deployability NO-GO `41066799aedd413d81fe4bbe95e3aeaa1a5e2ba9`
- checkpoint terminal production NO-GO `ca608bb348cba4670737ae85131a66882f5b2e35`
- owner/verifier synchronization `a69e542fa8a53708dd581aac47739fc5d8e36955`

## Oracle/reference leakage audit

**No oracle leakage was found in the authoritative E119 candidate path.**

Verified boundaries:

- `methods/e119_generic_boundary_flux.py` accepts weights/budget and does not import the exact reference;
- generic candidate construction and deterministic repeat occur before the harness calls the exact reference;
- exact E114 angular state is used post-hoc for verification, not for atom selection;
- target-free cross-check poisoned exact-reference, fit and file-I/O APIs and the candidate remained finite and reproduced the same selection;
- no benchmark/public/public-mini/scorer/holdout/full data was read.

Target-free cross-check physical evidence:

- run `35458304957`
- job `105937430441`
- artifact `10588916206`
- SHA256 `d58ebb0c5f75615bfe2f8f9f86e20989fa32ca3599cb2e833eadc24649564795`

The branch `review/e119-exact-reference-extension-20260919` is explicitly oracle/reference engineering. Its run `35458239376`, job `105937257716`, artifact `10589800043`, SHA256 `723f467cb56301dea0b6daa76dd5dab72b0c08e31648a237e7f21227b0dd3266` may support post-hoc correctness only. It is **not candidate evidence** and must never be used to choose/tune a production mechanism.

## Remainder-proof audit

The owner small-width omission proof is mathematically valid but materially trivial:

- raw MSE gate: `1.89e-8`
- RMS/absolute-mean gate: `1.374772708486752e-4`
- frozen omitted-flux L1 budget: `6.89208828456787e-4`
- retained counts: `54/55, 60/61, 82/83, 54/55`
- every omitted atom is exactly zero-flux
- omitted nonzero atoms: `0,0,0,0`
- max certificate squared: `0`
- no material nonzero-atom compression is established

Independent/adversarial evidence closes the absolute-L1 compression interpretation as a generic material-compression mechanism:

- adversarial run `35458306325`
- job `105937434015`
- artifact `10589765209`
- SHA256 `d3667fa2215e0c748269d103329f56ade74733427a226c80fa191d5182cf0240`
- frozen positive scaling forces 100% retention of nonzero atoms in all three adversarial cases
- terminal verdict: `TERMINAL_NO_GO_E119_GENERIC_ABSOLUTE_L1_BOUNDARY_COMPRESSION`

A separate weight-only TV remainder mechanism is also terminal:

- branch `research/e119-output-flux-tv-remainder-20260919`
- protocol `f2236ea7715d1bf7c625355b6cc9bfb02b2e80f5`
- run `35458271579`
- job `105937346267`
- artifact `10589575446`
- SHA256 `3f75a6de98c9a79c966672aff2fd47fe3e5cbdb53448c12a3b6bd8c2beab5fc1`
- rigorous pooled RMS bound `1.84270085409586e-3`
- required RMS limit `1.3747727085e-4`
- bound misses by `13.403676423766163x`
- terminal verdict: `TERMINAL_MATHEMATICAL_NO_GO_CLOSE_TV_REMAINDER`

### Missing production error certificate

The componentwise E119 error-budget audit explicitly records:

- `helper_component_certified_pass=false`
- `final_materialization_component_certified_pass=false`
- `production_candidate_pass=false`
- `production_authorized=false`

Therefore a production claim currently lacks a complete machine-verifiable joint remainder/error proof. Observed small-width numerical error is not a substitute for a rigorous production-shape bound.

## FLOP audit

Small-width owner accounting is complete only for its frozen scope:

- max physical flopscope dense FLOPs: `51,456`
- max manual geometry FLOP-equivalent: `53,816`
- max protocol-defined all-in: `105,272`

This does **not** prove production cost.

The direct exact full-dimensional owner path is already terminal pre-production on structural cost/state grounds:

- production input/width/depth: `1024/1024/16`
- live affine coefficients per cell: `1,048,576`
- dense coefficient propagation per cell transition: `2,147,483,648 FLOPs`
- frozen incremental cap: `136,758,472,261 FLOPs`
- at most `63` such dense transitions fit before other work
- full-rank square first layer induces `2^1024` nonempty sign cones

Thus direct exact region materialization is terminal NO-GO before deeper splitting/certificate/output work.

A separate independent production audit also found an explicit incomplete-FLOP blocker in the older physical boundary path:

- run `35457993173`
- job `105936589306`
- artifact `10588514800`
- SHA256 `b1edd9bc14facea17c0c414929edd8be76441de6bbe6ea0a574f916b883b795b`
- declared helper reserve: `3.6e9 FLOPs`
- physical flopscope for helpers: absent
- helper reserve derived/measured: false
- unbilled/underived classes include root solving/checks, root sort/dedup, trig midpoint direction, mask tests, coefficient materialization, heap operations, suffix norms, remainder accumulation, sector integration and state bookkeeping

That path is not authorized and must not be revived as E119 evidence.

## Premature-GO audit

Allowed positive statement:

`E119 small-width generic weight-driven boundary construction + frozen L1 certificate is verified for input dimension 2, width<=8, depth<=4.`

Not allowed:

- production GO
- production scientific accuracy GO
- competition GO
- material compression GO
- generic scalable boundary enumeration GO
- a claim that all production error components are certified
- a claim that production all-in FLOPs are proven for a successor mechanism

The owner receipt's `scientific_go=true` is valid only in the narrow frozen small-width protocol scope. The support branch `support/e119-streaming-boundary-sweep-20260919` also records `scientific_go=true`, but its own receipt limits this to 2-D theory support and explicitly leaves boundary-event growth unresolved. Neither may be promoted to production GO.

Streaming support physical evidence:

- run `35458357993`
- job `105937575876`
- artifact `10588941191`
- SHA256 `6d3248ded9df768f7375101726f3e3918ceca54841b2b8487ed9c9647f9ce6cb`
- exact small-width sweep: PASS
- production path: unproved / unauthorized

## Same-ID evidence pollution

At audit time at least ten E119-named branches exist. Multiple scientific/support runs have been executed under the E119 label after the authoritative owner one-run was consumed.

Control classification:

- authoritative E119 owner lane: `research/e119-generic-boundary-flux-certificate-20260919`
- verifier/cross-check/reference branches: verification evidence only
- output-TV remainder: terminal alternative, non-authoritative
- adversarial scaling: terminal falsification/support, non-authoritative
- streaming sweep: support-only, non-authoritative
- older independent physical boundary audit: reviews a distinct E118 physical mechanism, not owner E119

No further E119 scientific mechanism may be opened or rerun. Same-ID evidence must not be aggregated into a synthetic production GO.

## Active blocker

**BLOCKER: E119 has no production-admissible mechanism with both (a) a complete pre-materialization target-free remainder/error certificate and (b) complete production-shape all-in FLOP accounting.**

The exact materializer is structurally impossible at production dimension. The absolute-L1 compression certificate removes no nonzero atoms and is adversarially terminal. The weight-only TV certificate is rigorous but misses the RMS limit by 13.4x. Helper/final-materialization error certificates remain missing for any production claim.

## Assigned correction — one exact next action

**STOP E119 execution. Do not rerun, rescue, retune, change rank/cell count/norm, or open another E119 branch.**

The next scientific owner may proceed only under a **fresh collision-free experiment ID** and must make its **first commit protocol-only**, containing before implementation:

1. a candidate path that does not enumerate full-dimensional activation cells;
2. a target-free remainder/error certificate available before exact-reference/oracle comparison;
3. explicit component bounds for omitted approximation, numerical geometry, helpers and final materialization whose deterministic sum is `<=1.374772708486752e-4`;
4. a complete production-shape all-in FLOP derivation `<=136,758,472,261`, including every helper/materialization/certificate class;
5. an oracle firewall: exact reference may be used only after the candidate output is frozen, for verification, never for fit/select/tune/normalize.

Until such a protocol-only commit exists, **implementation and workflow execution are BLOCKED**.

Control verdict:

`E119_SMALLWIDTH_VERIFIED__PRODUCTION_TERMINAL_NO_GO__NO_ORACLE_LEAKAGE_IN_OWNER_CANDIDATE__PRODUCTION_REMAINDER_AND_FLOP_PROOF_INCOMPLETE_FOR_ANY_SUCCESSOR__STOP_E119`.
