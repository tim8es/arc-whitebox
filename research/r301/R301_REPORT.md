# R301 — exact synthetic replay of the R300 analyzer self-check

Status: **COMPLETE — 21/21 SYNTHETIC CHECKS PASS / NO REAL CAPTURE**

Job: R301  
Run ID: `R301-r300-analyzer-selfcheck-20260924-controlcenter`  
Owner: `Control Center 7.09`

## Exact artifacts

Artifacts were fetched individually from the immutable R300 commit `813756ced282c780ac28f6da1e4228d8bc9c50b8`; no repository checkout was cloned.

- analyzer `research/r300/r300_capture_analyzer.py`: blob `2b99b8aefbe016092a3d01ea69a9609170cd2bd1`, SHA-256 `a4c0808535f5a3a7d14a27a5fbc7d26d25400e74b0b238edb22e017677365315`
- self-check `research/r300/r300_capture_analyzer_selfcheck.py`: blob `8a80ec16952117a0cdd730a61ae0c9c431b4c7df`, SHA-256 `d2054223b7876912fc7d3c842f9f15fa1876ad71180e68cf297dd345ea2a45b6`
- R300 receipt: blob `b7728caecfd9612e7fcaffab94562361279a4011`

Historical artifacts in the exact R300 tree match their existing receipts: R298 analyzer/checker blobs `f1d5a9da7872ff6e632fef1e6c7dd2c90a6091ea` / `e05443ffece962cf54c8b568c1536b60a2c071fb`; R299 analyzer/checker blobs `d8469b233f458dbe7813babdcfe21a82016664e1` / `03ebb9c9a1f7cba61cd199ac2b8b8066b1de466a`. No historical R298/R299/R300 source or receipt was changed.

## Replay result

Executed the committed script with synthetic fixtures only: `python r300_capture_analyzer_selfcheck.py`. Runtime was Python 3.13.13; no Python/dependency install occurred. The frozen R300 contract lists Python 3.11.16, so this is an exact-byte synthetic pass under the available interpreter, not a claim that Python 3.11.16 was tested.

Result: **PASS, all 21 substantive checks true; `pass=true`; exit code 0.** The suite covers valid sealed fixture, 50/50 FIT/EVAL split, frozen no-tuning rule, retained failure row, four diagnostic gates, OFFLINE_DIAGNOSTIC_ONLY label, production pins, corrupt hashes, duplicate IDs, split mismatch, target fingerprint mismatch, failure-flag mismatch, residual corruption, zero-energy semantics, negative explained energy, weighted global penalty, type-7 quantiles, binary32 counterexample, and aggregate coordinate-C consistency with the corrected-MSE path.

All generated capture bytes were synthetic and contained in the self-check's temporary directory. No real residual vectors were read or interpreted.

## Boundaries

No Actions, estimator/benchmark, real capture data, dependency/data download or installation, paid resource, holdout/private/full data, PR #36 edit, submission, leaderboard edit, or canonical-result edit occurred. R300 remains an offline diagnostic; this self-check does not establish scientific improvement or an official score.
