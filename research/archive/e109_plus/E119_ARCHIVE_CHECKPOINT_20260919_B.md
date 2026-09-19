# E119 archive checkpoint — new evidence after deployability snapshot

Snapshot: `ARC-E119-ARCHIVE-CHECKPOINT-20260919-B`

This is an append-only archive delta. Source experiment/review branches are untouched; canonical and ledger are untouched.

## E118 proof remains separate

E118 output-specific flux sketch remains the proof-level result:

- UID: `ARC-HYP-20260919-E118B-OUTPUT-SPECIFIC-FLUX-SKETCH`
- sealed head: `5db88d151cef14fa32bfbc146188a0cdf10e0f4f`
- run/job: `35457418719 / 105935065614`
- artifact: `10588194482`
- pooled small-corpus exact-reference bias MSE: `1.7613237067793404e-12`
- production scientific execution: **not performed**
- competition GO: **false**

No new E118 scientific run appeared in this checkpoint.

## E119 primary deployment path is now terminal at production scale

The owner branch advanced to:

`a69e542fa8a53708dd581aac47739fc5d8e36955`

without a new scientific run. The checkpoint synchronizes the independent verifier and records a structural production blocker:

- exact first layer at width 1024 has `2^1024` nonempty sign cones for full-rank square W1;
- direct live affine state is 8,388,608 bytes per cell;
- dense coefficient propagation costs `2,147,483,648` FLOPs per cell transition;
- the frozen incremental cap permits at most 63 such transitions.

Therefore the same E119 exact-materialization path is:

**small-width generic bridge VERIFIED GO; production deployability TERMINAL NO-GO; production run UNEXECUTED and unauthorized.**

## New E119 scientific mechanism: TV remainder

`ARC-HYP-20260919-E119B-OUTPUT-FLUX-TV-REMAINDER`

Run `35458271579`, artifact `10589575446`.

The weight-only total-variation certificate is rigorous and cheap, but its RMS bound is `13.403676423766163x` the permitted threshold. The mechanism is terminal NO-GO; the underlying E118 sketch bias itself remains small.

## New support evidence

- **Adversarial scaling:** run `35458306325`, artifact `10589765209`. Positive layer scaling proves the fixed absolute-L1 certificate can be forced to retain 100% of nonzero atoms while boundary geometry is unchanged.
- **Error-budget allocation:** static receipt `549f6097...`; no run. Production admission requires four separately certified deterministic error components; missing helper/final-materialization certificates are failures.
- **Exact-reference extension:** run `35458239376`, artifact `10589800043`; six heterogeneous small dense networks match the independent exact oracle to roundoff.
- **Independent generic verifier:** receipt `630edb7d...`; no new scientific run. It independently reconstructs the owner artifact and confirms small-width generic GO only.
- **Target-free hygiene:** run `35458304957`, artifact `10588916206`; poisoned exact-reference/fitting/file-I/O APIs are not touched by candidate construction.
- **Streaming boundary sweep:** run `35458357993`, artifact `10588941191`; exact 2-D boundary flux can be streamed with boundary-count-independent working memory, but runtime still visits every boundary event.

No support result authorizes production/public/scorer/holdout/full execution.

Machine-readable checkpoint:
`research/archive/e109_plus/E119_ARCHIVE_CHECKPOINT_20260919_B.jsonl`
