# ARC portfolio control receipt — E094–E104

Receipt key: `ARC-PORTFOLIO-CONTROL-E094-E104-20260919`

Control branch: `research/owner-frontier-e094-e104-20260919`

Canonical verified live: `research/bootstrap@29bee3f8d23fc620b77aaed414b1b7a928af4b83`.

This is an append-only control receipt. It does not modify experiment branches, rerun workflows, change scientific gates, mutate canonical/ledger, or grant public/scorer/holdout/full access.

## Portfolio identity / duplicate audit

| ID | Current authoritative state | Duplicate/collision handling |
|---|---|---|
| E094 | `research/e094-source-axis-joint-compression-20260917` — terminal NO-GO/DROP | `research/owner-frontier-e094-e104-20260919` is administrative only, not a scientific E094 lane |
| E095 | `research/e095-output-subspace-residual-sampling-20260917` — terminal NO-GO/DROP | no live successor under E095 |
| E096 | `research/e096-v29-matmul-callsite-attribution-20260917` — COMPLETE / valid attribution; no estimator modification authorized | do not reopen as another callsite micro-optimization lane |
| E097 | `research/e097-rank8-k22-memory-feasibility-20260917` — terminal NO-GO/DROP | no rescue under E097 |
| E098 | both same-ID branches are terminal NO-GO/DROP: `research/e098-late-k22-edgeworth-response-20260918` and `research/e098-late-k22-response-relevance-20260918` | same-ID collision exists; both fixed-response variants are closed and must not seed a third E098 lane |
| E099 | `research/e099-shared-latent-2g-closure-20260918` — terminal structural NO-GO | no rescue |
| E100 | authoritative frontier identity: `research/e100-orthogonal-gaussian-antithetic-20260918` — local Stage-A GO + independent law review PASS, competition scientific_go=false | `research/e100-crossfit-two-subspace-shrinkage-20260918` is a same-ID collision and terminal NO-GO; `review/e100-orthogonal-cost-correction-20260918` is append-only review evidence for the authoritative orthogonal lane |
| E101 | `research/e101-multilatent-skew-rank-bound-20260918` — terminal analytic NO-GO | no rescue |
| E102 | `research/e102-k3-tensor-rank-bound-20260918` — terminal analytic NO-GO | no rescue |
| E103 | `research/e103-orthogonal-antithetic-production-shape-20260918` — sealed; production-shape execution verified, original complete-accounting claim corrected; competition accuracy unexecuted | E103 rerun/rescue prohibited |
| E104 | authoritative identity: `research/e104-haar-radial-raoblackwell-20260918` — local scientific GO preserved; production independent verification PASS/VERIFIED; competition scientific_go=false | `research/e104-orthogonal-antithetic-complete-billing-20260918` is a same-ID collision carrying the E100/E103 orthogonal-antithetic accounting continuation and must not be mixed into Haar/Rao-Blackwell E104 evidence |

## Stale-claim audit

1. **STALE:** any statement that authoritative E104 production-shaped verification is UNEXECUTED. It executed successfully as run `35446062235`, job `105905067035`.
2. **STALE / superseded as a complete-accounting claim:** unqualified E103 “measured complete utilization = 0.0677789313”. E103 omitted plain-NumPy RNG from flopscope; append-only correction gives minimum `149114620592` FLOPs / `0.06780947869265219` utilization and marks complete package-safe accounting NOT VERIFIED.
3. **NOT PROGRESS / DO NOT EXECUTE:** authoritative E104 head `58e884fe0fe8446c6c9e47cb6800d00db9b66626` adds only `research/E104_INDEPENDENT_ERROR_VERIFY_FREEZE.json` (“freeze independent error comparison”). No Actions run exists for that freeze. Later owner process instruction commit `fe46b0d7e69238ec5ad1024ddb4a8368f863cdab` explicitly seals E104 and leaves **E105 only** as successor. Therefore the freeze is a superseded planning artifact, not executable portfolio progress.
4. Older owner receipts that recorded E104 production as unexecuted were correct at their creation time but are chronologically superseded by the production receipt, post-production addendum, and process reconciliation.

## Single highest-value gate selected and verified

Selected gate: **authoritative E104 independent production-shaped verification**.

Owner: **research owner / tim8es**.

Authoritative branch: `research/e104-haar-radial-raoblackwell-20260918`.

Frozen run head: `95c353cc9cc6ca15837fc3da5d2cdd22d2ee2323`.

Required metrics / gates:

- width = `1024`, depth = `16`, trajectories = `4096`;
- prediction shape = `[16,1024]`;
- finite output;
- bitwise deterministic prediction replay and repeat max abs = `0.0`;
- exact antithetic pair max abs = `0.0`;
- homogeneity relative error <= `2e-6`;
- exact deterministic FLOP-ledger reconciliation;
- all-in utilization <= `0.12` and <= `0.135`;
- no benchmark/public/scorer/holdout/full target access;
- raw competition MSE remains explicitly unevaluated.

Verified physical evidence:

- workflow: `E104 independent production verifier`;
- run `35446062235`, attempt 1 — **success**;
- job `105905067035` — **success**;
- artifact `e104-production-independent-verify`, ID `10584569066`;
- artifact ZIP SHA256 `3a22b369883b141be19528acec69df9165be627976152ad845e35c5f90320237`;
- prediction SHA256 `ae0bfae00c7379673320a3a098c716272c7d9164588bcc73bd59bc7516c017e0`;
- finite = true;
- prediction bitwise replay = true; repeat max abs = `0.0`;
- antithetic pair max abs = `0.0`;
- homogeneity relative error = `6.874805456226369e-7`;
- exact FLOP reconciliation = true;
- flopscope / reconciled total = `149047442096`;
- utilization = `0.06777892944955966`;
- utilization <=0.12 = PASS; <=0.135 = PASS;
- targets/public/scorer/holdout/full = false;
- raw competition MSE evaluated = false.

Gate disposition: **PASS / VERIFIED / CONSUMED**.

A second E104 production run would be duplicate work and is prohibited.

## Next action

**Do not run or rerun E104.** Treat the production gate as complete and sealed.

The single portfolio successor remains **E105 only**, per owner addendum `eec00f043be542248680ffa8606e435fcb9b6b4c` and later process instruction `fe46b0d7e69238ec5ad1024ddb4a8368f863cdab`.

E105 must consume the immutable E104 production receipt, be protocol-first and target-free, and produce its own run/job/artifact/digest evidence. No chat response, idle reservation, or unexecuted freeze counts as progress.

No public/public-mini, official scorer, holdout/full access, tuning, rerun, canonical mutation, ledger mutation, or experiment-branch merge is authorized by this control receipt.
