# R203 Evidence Audit — history/E173 normalization

Date: 2026-09-22  
Branch: `review/r203-evidence-audit-20260922`  
Base: E174 verifier `c2dde864c51d1fe54f176dd9dbd2e84bc78c10a7`

Scope: evidence audit only. No scientific rerun, benchmark rerun, submission,
leaderboard action, baseline mutation, or canonical-ledger mutation. R201/R202
implementation work is not duplicated.

## Command actually executed

The immutable E173 Actions artifact `10650296065` was materialized and checked with:

```bash
unzip -q e173-official-mini-ago.zip -d /tmp/e173_art
python scripts/r203_evidence_audit.py /tmp/e173_art \
  --zip e173-official-mini-ago.zip \
  --expected-zip-sha256 7869fe6ac1af128f406be84f057568422dc0ab99b9cd31114e0ec46605182c4e
```

The audit command was replayed identically. Both JSON outputs had SHA256:

`f363e8a587d75802859c031e8ae0a8b44782301b9e3baee0aa7621ebf6115741`.

## VERIFIED

### Immutable E173 evidence

- Artifact size: `1,062,163` bytes.
- Artifact SHA256 exactly matches E173/E174:
  `7869fe6ac1af128f406be84f057568422dc0ab99b9cd31114e0ec46605182c4e`.
- Retained SHA256 map: `61/61` files verified.
- Vector manifest: `5/5` records verified for file SHA256, raw-array SHA256,
  dtype, shape and nbytes.
- Retained focused tests: exit `0`, `10 passed`.
- Parent validator: exit `0`.
- AGO validator: exit `0`.
- Parent official-local run: exit `0`.
- AGO official-local run: exit `0`.
- Frozen summarizer: exit `0`.

These are checks of immutable retained evidence, not a new benchmark execution.

### E173 normalization

Both parent and AGO reports use:

`mean_score_multiplier = 0.1`.

R203 verified at aggregate and per-MLP level:

`adjusted_final_layer_score = raw final_layer_mse * 0.1`.

Therefore a history entry storing `adjusted_final_layer_score` must be divided
by `0.1` before comparison to raw MSE. Mixing adjusted score with raw MSE creates
an exact 10x scale error.

### Exact compatible panel

The E173 panel is:

1. `logan-fitzgerald`
2. `william-graves`
3. `raymond-barnes`
4. `steven-rice`
5. `sarah-kelley`

Dataset: `hf://aicrowd/arc-whestbench-public-2026@v2-phase2`, split `mini`,
first five in official order, width 1024, depth 16, WhestBench 0.16.1.

### Strongest reproducible historical result on that exact panel

The strongest currently VERIFIED exact-panel, cap-compatible historical result is
**E173 AGO**:

- official mean raw final-layer MSE:
  `3.50171694663004e-06`;
- independently recomputed from retained coordinate vectors:
  `3.501716933665207e-06`;
- adjusted final-layer score:
  `3.50171694663004e-07`;
- E173 parent raw MSE:
  `4.2111157199542505e-06`;
- AGO/parent:
  `0.8315413727619156`;
- improvement:
  `16.845862723808436%`;
- improves:
  `5/5`;
- paired delta mean:
  `7.093987733242102e-07`;
- paired delta SE:
  `8.90210264475203e-08`;
- mean metered AGO FLOPs:
  `69,159,064,030`;
- failures:
  `0`;
- E174 independent verification:
  `GO`.

E136 V29 reports a much lower 3-MLP raw number (`2.33e-8`), but it is not an
exact-panel comparator: only the first 3 public Mini MLPs were used and its mean
cost is about `0.25769B`, above the `0.135B` comparison cap. E171 is a
production-shaped synthetic 3-seed panel; E176 is a synthetic 256x8 fixture.
Neither is the exact E173 public five-panel.

## UNKNOWN

No `history.json` was found in the inspected E173 branch tree, E174 verifier
branch tree, downloaded immutable E173 artifact, or the visible R202 branch tree
at audit time.

Therefore R203 cannot verify any external/local history row as stronger than
E173. In particular, the following comparison evidence is missing:

1. the immutable `history.json` object itself and its content hash;
2. mapping of a candidate history row to the exact five E173 MLPs/order and
   `v2-phase2` revision;
3. field semantics proving whether the stored score is raw
   `final_layer_mse` or adjusted score;
4. per-MLP values or target/prediction hashes sufficient for paired
   recomputation;
5. estimator commit/blob identity for the history row;
6. FLOP/failure/residual-time metadata under the E173 `0.135B` comparison
   contract.

## Conclusion

**VERIFIED:** E173 AGO is the strongest currently reproducible historical
comparator for the exact E173 five-MLP public Mini panel under the E173 cost
contract, and its raw-vs-adjusted normalization is now independently checked.

**UNKNOWN:** whether an external/local `history.json` contains a stronger
fully comparable result. Until that file is preserved with provenance and the
six fields above, such a comparison is not auditable.

Machine-readable receipt: `research/R203_EVIDENCE_RECEIPT.json`.  
Audit script: `scripts/r203_evidence_audit.py`.
