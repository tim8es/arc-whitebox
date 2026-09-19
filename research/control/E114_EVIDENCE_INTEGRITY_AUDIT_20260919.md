# E114 evidence-integrity control audit — 2026-09-19

Receipt key: `ARC-CONTROL-E114-EVIDENCE-INTEGRITY-20260919`

Control branch: `control/arc-deep-error-frontier-20260919`

This is a control-plane evidence note. It does not rerun E114, mutate canonical/ledger, access public/scorer/holdout/full, or alter any scientific payload.

## Authoritative E114 identity

Authoritative E114 remains:

- branch: `research/e114-activation-boundary-flux-20260919`
- protocol-first commit: `2ef10a3cc00c7f1e6b8b967d3c0ced210ee1b11c`
- executable commit: `800fc858c0a0b142f5ceecc18d929dffaaabe911`
- workflow commit: `d9d37664bcd3f89d5dece2473a1614203ae0d99c`
- result commit: `3cb02a60b16848af14e0c0dd9199509af9fb0767`
- sealed receipt commit: `b9f64030f65da9b32fc7718d04fb108ee1a73dab`

Physical evidence:

- run: `35455223230`
- job: `105929190535`
- artifact: `e114-activation-boundary-flux`
- artifact ID: `10588126544`
- artifact ZIP SHA256: `dd7a49166fe7f3cc469b145914e8b8b00680bfbeaa574b8539cdbad50defb84f`
- run conclusion: `success`
- deterministic repeat: exact
- direct piecewise max abs: `1.1102230246251565e-16`
- flux sum: `1.1231056256176606`
- exact sector integral: `1.1231056256176606`
- Gaussian boundary-flux value: `0.22402715970779358`
- closed-form value: `0.22402715970779363`

No direct benchmark/public/public-mini/scorer/holdout/full target access occurred in this run.

### Control classification

The evidence supports:

`E114 = SMALL_WIDTH_EXACT_MATHEMATICAL_IDENTITY_VERIFIED`

It does **not** support:

- production feasibility GO;
- production estimator GO;
- competition accuracy GO;
- a claim that activation-boundary enumeration/compression fits the ARC budget;
- a claim that the general production-shape boundary representation is computationally tractable.

The field `scientific_go=true` in the experiment-local receipt is therefore scope-sensitive. It is acceptable only as shorthand for the frozen exact mathematical closure. It must not be quoted as portfolio-level, production, or competition scientific GO.

## Independent verifier audit

Verifier branch:

`review/e114-independent-verifier-20260919`

Evidence:

- verifier script commit: `ef23766b3fc1aecf97673528cbd61e659c136a28`
- verifier workflow commit: `8d0b6d995346a2e7a8e3d1de1d09abb7745e6cda`
- arm commit: `14b443486acc708edd7244929173cb41991fe01e`
- run: `35456190095`
- job: `105931767316`
- artifact ID: `10588302608`
- artifact name: `e114-independent-verifier`
- artifact ZIP SHA256: `811b593497ab3344aebaf05fc98d11ac84163115c5b334d642dfbfda04e00ade`
- receipt commit: `0920aa5175cd1708efa5f210288f0e2e91165cc3`
- verdict: `SMALL_WIDTH_EXACT_GATE_VERIFIED`
- production authorized: false

The verifier independently reproduces the small fixture/reference and artifact hashes. This is valid reproducibility evidence.

### Verifier protocol gap

No distinct protocol-first verifier artifact was committed before the verifier script. The sequence is:

1. verifier script `ef23766...`
2. workflow `8d0b6d...`
3. arm `14b443...`
4. run/result
5. receipt `0920aa...`

Therefore the verifier is **post-hoc frozen executable verification**, not protocol-first independent preregistration. This does not erase its reproducibility value, but it must not be represented as a protocol-first independent scientific gate.

One verifier gate also checks that the owner receipt contains `scientific_go=true`; that check verifies receipt consistency, not scientific truth, and must not be counted as independent confirmation of GO.

## E114 same-ID collision audit

Current E114 surfaces include four branches:

1. `research/e114-activation-boundary-flux-20260919`
2. `research/e114-exact-reference-output-compression-20260919`
3. `research/e114-output-schur-finalmean-20260919`
4. `review/e114-independent-verifier-20260919`

Only (1) is the authoritative E114 scientific identity. (4) is verifier evidence for (1).

Branches (2) and (3) are successor work and must not be merged semantically into the original E114 result.

This is particularly important because the current control frontier already records that the E114 scientific one-run rule is consumed and that any production feasibility/compression mechanism requires a new unique ID.

## Exact-reference output-compression branch

Branch:

`research/e114-exact-reference-output-compression-20260919`

Observed protocol-first commit:

`c5bbae91fec244f0b33f02d55df7555eea94948f`

Current observed development includes exact angular reference implementation/tests/harness, with head observed during audit at least through:

`762d8fa62de745a93a04552fe645f314d03d6f3c`

At audit snapshot:

- no GitHub Actions run;
- no artifact;
- no result receipt;
- no deployable compression mechanism defined by the protocol;
- protocol explicitly classifies itself as reference engineering / oracle capacity diagnostic only.

The frozen oracle ranks `{1,2,4}` use exact flux geometry and are explicitly unavailable to a deployable estimator. Results from this harness, if later executed, must not be promoted as candidate GO or used as an implicit rank sweep for an E114 rescue.

Control disposition:

`QUARANTINE_UNEXECUTED_SAME_ID_REFERENCE_EXTENSION`

Do not arm it under E114.

## Output-Schur same-ID successor

Branch:

`research/e114-output-schur-finalmean-20260919`

Protocol-first commit:

`3926781c8109d6329aac064e453ecbc4a2d7986b`

The branch defined a distinct rank-2 small-width Schur-compression mechanism, then executed a sole exact falsifier under the E114 ID despite the existing authoritative E114 lane and consumed one-run control status.

Physical execution:

- run: `35456264281`
- job: `105931961172`
- run head: `08d5a5e2a6d5f8f03d3881e0c6c4f002734ad4de`
- workflow conclusion: `failure`
- artifact: `e114-output-schur`
- artifact ID: `10587988095`
- artifact ZIP SHA256: `bfe043ca060c73698dd370c8b3b17c346630f75e953f5d3ff629402ed847fd65`

Frozen exact small-width result:

- decision: `TERMINAL_NO_GO_DROP_OUTPUT_SCHUR_VARIANT`
- pooled actual proxy bias MSE: `0.0027233238128475485`
- pooled actual / target: `144091.20702897082x`
- pooled Schur remainder bound MSE: `0.7674294368086603`
- pooled bound / target: `40604732.10627832x`
- worst observed actual / target: `293806.5739359178x`
- every target-scale remainder gate: FAIL
- finite/integrity/determinism/bound-validity gates: PASS
- direct benchmark/public/scorer/holdout/full access: none

This route is scientifically dead on its frozen exact gate.

### Cost-accounting audit

The protocol records:

- base FLOPs: `149114620592`
- all-in upper: `184614620592`
- utilization: `0.08395300964912167 <= 0.13`

No production execution occurred, so this is admission arithmetic only, not measured production cost.

The base is mislabeled as an “E104 complete measured cost reference.” The authoritative Haar/Rao-Blackwell E114-parent production verifier measured `149047442096` FLOPs, while `149114620592` comes from the corrected E103 / separate complete-billing lineage. The chosen base is slightly larger, so this identity mix does **not** create a cost undercount; it is conservative. But it is an evidence-identity defect and must not be cited as an authoritative E104 measured ledger.

The rank-64 production extrapolation is unexecuted and therefore remains unverified.

Control disposition:

`TERMINAL_NO_GO__SAME_ID_SUCCESSOR__NO_RERUN_NO_RESCUE`

## Target-leakage audit

No direct target tensor, benchmark record, official scorer, holdout or full split was found in:

- authoritative E114 activation-boundary run;
- independent E114 verifier;
- output-Schur small-width falsifier;
- unexecuted exact-reference extension.

However, the repository-wide public-target contamination boundary remains the earlier authorized E104 mini0 event:

- run `35449587126`
- public record read: one mini0 target
- raw MSE `9.730479418246265e-6`

E114 and later hypothesis selection happened after that event. Therefore the portfolio is no longer globally target-naive. E114 evidence may be called **direct-target-free**, but not “portfolio target-naive.”

No evidence was found that the mini0 target tensor/residuals were imported into the E114 scripts. Using the public competition threshold `1.89e-8` as a preregistered gate is not itself target leakage.

## Premature/fake GO audit

Invalid promotions:

- E114 `scientific_go=true` -> production GO: INVALID
- E114 `scientific_go=true` -> competition GO: INVALID
- independent verifier success -> production tractability: INVALID
- exact-reference oracle capacity -> deployable compression GO: INVALID
- output-Schur integrity PASS -> scientific GO: INVALID; target-scale gate failed catastrophically
- workflow success -> scientific GO: INVALID

The only surviving positive claim is the small-width exact activation-boundary mathematical identity.

## Exact next action

### Required action

Create **one append-only terminal result/receipt commit on**
`research/e114-output-schur-finalmean-20260919`
that seals physical run `35456264281`, job `105931961172`, artifact `10587988095`, digest `bfe043...`, and the terminal target-scale failure metrics above.

The receipt must state:

- terminal NO-GO / DROP for the output-Schur variant;
- no rerun/rescue/rank change/seed change;
- no production authorization;
- cost evidence is pre-code arithmetic only;
- no target leakage;
- same-ID execution does not alter the authoritative activation-boundary E114 identity.

### After that receipt

**STOP E114.**

Do not execute the exact-reference output-compression branch under E114.
Do not open another E114 mechanism.
Do not reinterpret the boundary-flux identity as production tractability.

Any future activation-boundary compression mechanism requires an explicitly reopened control window and a fresh collision-free experiment ID before protocol/implementation/run. Current control v3 already blocks additional candidate allocation.

Control verdict:

`E114_SMALL_WIDTH_MATH_VERIFIED__OUTPUT_SCHUR_TERMINAL_NO_GO__OTHER_SAME_ID_EXTENSION_QUARANTINED__NO_FURTHER_E114_EXECUTION`.
