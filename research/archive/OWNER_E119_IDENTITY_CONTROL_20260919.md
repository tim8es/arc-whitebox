# E119 portfolio identity control — owner/verifier handoff

Control key: `ARC-E119-IDENTITY-CONTROL-20260919`

Status: **IDENTITY FROZEN / SINGLE VERIFIER GATE OPEN**.

Canonical remains `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

This is a portfolio-control note only. It does not authorize a second E119 scientific mechanism, a rerun of the owner experiment, production/public/scorer/holdout/full access, tuning, rescue, canonical/ledger mutation or merge.

## Single authoritative E119 identity

Experiment ID: **E119**

Idempotency key:

`ARC-E119-GENERIC-BOUNDARY-FLUX-CERT-20260919`

Owner branch:

`research/e119-generic-boundary-flux-certificate-20260919`

Owner sealed head:

`de346277894ccb89ceef39e76ca6d8f12853b2ee`

Owner executed arm head:

`d731e845c96d401ac001da82c8998c06a03ec484`

Owner result:

- status: `E119_GENERIC_BOUNDARY_FLUX_CERTIFICATE_GO`;
- scientific construction/certificate GO: true;
- material nonzero-atom compression: **NOT ESTABLISHED**;
- production scientific GO: false;
- generic construction verified only for input dimension 2, width<=8, depth<=4;
- retained fractions on the frozen corpus: about 98.18%–98.80%; the rigorous L1 certificate omits only the periodic zero-flux atom.

Physical owner evidence:

- workflow run `35458020001`, attempt 1, success;
- job `105936659806`, success;
- artifact `e119-generic-boundary-flux-certificate`, ID `10589345345`;
- artifact digest `sha256:7485a4380bca0175197afeb327aed9abeb2f5d14ca335cdff6571ad0c7ed78e3`;
- no rerun.

The owner branch is now **frozen for E119 scientific work**. No additional owner implementation, certificate variant, rank/threshold change, compression rule, seed change or workflow run is allowed under E119.

## Designated verifier identity

The only designated E119 verifier branch is:

`review/e119-exact-reference-extension-20260919`

Current verifier head:

`e7b454fef6264ec48e5644509105cefdbcd92fc5`

Identity check:

- branch descends from sealed owner head `de346277894ccb89ceef39e76ca6d8f12853b2ee`;
- it is exactly 3 commits ahead of the sealed owner head;
- verifier-only changed paths relative to owner are:
  - `methods/e114_exact_angular_reference.py`;
  - `methods/e119_exact_reference_compare.py`;
  - `tests/test_e119_exact_reference_extension.py`;
- current Actions runs on this verifier branch: **0**;
- the comparator independently checks generic E119 sectors/boundaries/jumps/means against the reusable exact angular reference and direct raw-network probes;
- verifier test corpus includes arbitrary dense rectangular width chains and a hand-specified dense chain, rather than changing the owner scientific gate.

This branch is a verifier extension only. It may not alter `methods/e119_generic_boundary_flux.py`, owner protocol/gates, owner receipt, owner run identity or the frozen compression rule.

## Mis-scoped same-ID review branch

`review/e119-independent-boundary-audit-20260919` is **not an E119 verifier for the authoritative E119 owner identity**.

Its immutable receipt explicitly reviews:

- `research/e118-boundary-flux-physical-compression-20260919`;
- reviewed head `9e1ef4c27fb68e7371ee9d025bf055ab8e33527d`.

Its run `35457993173`, job `105936589306`, and production NO-GO are valid only as review evidence for that E118 physical-compression line. The branch diverges from the authoritative E119 lineage before the E119 owner protocol and therefore must not be combined with, override, or be counted as independent verification of `ARC-E119-GENERIC-BOUNDARY-FLUX-CERT-20260919`.

The branch is retained as historical evidence; it is not deleted or rewritten.

## Duplicate-prevention rule

Effective immediately for portfolio accounting:

1. no new `research/e119-*` scientific branch is admissible;
2. no additional `review/e119-*` branch is admissible while the designated verifier branch above is open;
3. any different mechanism proposed under E119 must be re-keyed to a fresh experiment ID after portfolio collision check;
4. chat/status updates, branch reservations and unexecuted plans do not count as E119 progress;
5. only the owner evidence listed above plus the designated verifier receipt may determine E119 portfolio state.

## Single next gate — E119-V1 independent exact-reference verification

**Owner:** frozen / no action.

**Verifier:** `review/e119-exact-reference-extension-20260919`.

Exactly one next gate is open:

> Run one review-only, path-isolated verification of the existing exact-reference extension, then append one immutable verifier receipt tied to the sealed owner head. Do not rerun the owner scientific workflow.

The verifier receipt must establish all of the following:

1. owner identity exactly
   `research/e119-generic-boundary-flux-certificate-20260919@de346277894ccb89ceef39e76ca6d8f12853b2ee`;
2. owner physical evidence exactly run `35458020001`, job `105936659806`, artifact ID `10589345345`, artifact digest `7485a4380bca0175197afeb327aed9abeb2f5d14ca335cdff6571ad0c7ed78e3`;
3. verifier code does not modify or substitute the owner candidate;
4. all frozen arbitrary-width-chain and hand-specified exact-reference tests pass;
5. partition completeness/order and layer/final region counts match;
6. sector endpoints/coefficients and direct raw-network probes satisfy the committed test tolerances;
7. boundary angles/jumps and generic-vs-reference mean satisfy the committed E119 tolerances;
8. deterministic comparator replay passes;
9. no benchmark/public/scorer/holdout/full target is accessed;
10. the verifier preserves the owner's narrow interpretation:
    **generic exact construction/certificate verified; material nonzero-atom compression and production deployability remain unestablished**.

Gate result:

- all checks PASS => append `E119_INDEPENDENT_VERIFIED` receipt and **seal E119**;
- any check FAIL => append `E119_VERIFICATION_NO_GO` receipt and **seal E119**;
- in either case there is no second E119 scientific run and no rescue under E119.

No E120+ scientific allocation is authorized by this note; that is a separate portfolio decision after E119-V1 is immutable.
