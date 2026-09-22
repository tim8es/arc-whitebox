# R230 — Public leader methods transfer audit protocol

Frozen before inspecting competitor submission details.

- Job: R230 / PUBLIC-LEADER-METHODS-TRANSFER-AUDIT.
- Scope: read-only audit of official AIcrowd Phase-2 submission detail pages for IDs 331539 and 331308 from the R228 leaderboard snapshot.
- Access gate: first determine whether each official detail page exposes method/source/artifact information publicly and whether the exposed material is intended for public viewing. Do not bypass access controls, authenticate into another user's private materials, enumerate hidden endpoints, download source archives, or run competitor code.
- Evidence policy: method claims require text or metadata visible on an official AIcrowd public page/artifact. If a method is not explicitly exposed, record UNKNOWN/NOT_PUBLIC rather than infer it from score, runtime, filename, participant identity, or leaderboard behavior.
- Comparison scope: compare only publicly evidenced mechanisms against repository experiment history and the normalized R209 V25/V29 records. Similarity means documented mechanism overlap, not authorship or code equivalence.
- Novelty outputs: produce a deduplication/novelty table and at most two transferable hypotheses. Each hypothesis must be supported by public evidence, remain distinct from tested history, and include a bounded cost gate and evidence/falsifier gate. If evidence is insufficient, produce zero hypotheses.
- Repository limits: append-only docs/research artifacts only. No estimator run, paid compute, competition submission, private/holdout data, competitor-code download/execution, external mutation, or canonical result edits.
- Planned outputs: `research/R230_PUBLIC_LEADER_METHOD_AUDIT.md` and `research/R230_PUBLIC_LEADER_METHOD_AUDIT_RECEIPT.json`.
