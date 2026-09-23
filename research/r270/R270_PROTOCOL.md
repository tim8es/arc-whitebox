# R270 Protocol — independent audit of R266 score-gap arithmetic

- Job: R270
- Owner: `score-gap-independent-audit`
- Dependency: R266 COMPLETE.
- Control baseline observed: revision 317; claim published at revision 318.
- Scope: independent desk-only recomputation from immutable normalized R209 V25/V29 rows plus official Phase-2 scoring source.
- Verify: mean adjusted score, mean cost factor, 0.1 floor behavior, conditional raw-MSE reduction needed to match the displayed 2.1e-9, rounding sensitivity, and V29 failure treatment.
- Mandatory comparability decision: no official rank/gap claim because R209 `mini:all-100` public development panel differs from current 50-visible + 50-sealed online evaluation.
- Forbidden: estimator execution, GitHub Actions, new dataset/data access, paid compute, private/holdout/full, submission, leaderboard/model/canonical changes.
- Deliverables: isolated append-only audit report and receipt with source hashes and commit, then finish R270.
