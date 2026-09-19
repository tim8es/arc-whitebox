# E121 evidence-gate blocker — 2026-09-19

Control classification: **E121 TERMINAL SCIENTIFIC NO-GO CONFIRMED; NOT PRODUCTION GO**.

This note is append-only control evidence. It does not mutate the E121 scientific branch, authorize a rerun, or reopen E119.

## Live evidence

Fresh successor branch: `research/e121-haar-plane-orbit-source-memory-20260919`.

Terminal receipt tip: `e2c7473a2919b4444daa581b14d1ed706960f7d8` (`research/E121_TERMINAL_RECEIPT.json`).

Protocol-only first scientific commit: `baa802af0b11152389c7f6229648f9212d8257ff` (`research/E121_PROTOCOL.md`). The receipt records subsequent pre-code protocol corrections `d7535b9f146781b03d28a52d1365ac98518aecb4` and `62ab89ffa7f39e62245e79e8dc062fbf78104b83`, then implementation `8aac202bda370849b31ba4e19ca0aa385341fe90`.

Sole E121 scientific execution recorded by the terminal receipt: run `35460988924`, job `105944694427`, attempt `1`, artifact `10588818925`, artifact ZIP SHA-256 `fb49a9be2945d0ffb3c8aaad3ae59600fd7cdc7493fd8959666319284632d836`.

Measured falsifier result: exact 8-D block-stress pooled candidate MSE `1.0381126736820251e-4`; same-node iid pooled MSE `9.0782420348022e-6`; ratio `11.435172907952149`, failing the frozen `<=0.90` gate. E121 therefore correctly closes as terminal NO-GO.

## Independent control-gate audit

### 1. Target/oracle firewall

No contrary leakage evidence is established by the inspected protocol/terminal receipt: candidate construction is frozen before verifier comparison; the exact E114 reference is declared verifier-only; public/public-mini/scorer/holdout/full are false. This does not rescue the failed scientific gate.

### 2. Remainder/error proof — FAIL CLOSED

The protocol freezes empirical exact-reference MSE comparisons and an unbiasedness identity, but does **not** provide a pre-oracle deterministic total remainder/error certificate covering stochastic sampling error, numerical geometry, helpers and final materialization with certified absolute error `<=1.374772708486752e-4` for a production claim. Unbiasedness and small-width empirical MSE are not such a certificate.

Therefore E121 cannot satisfy the successor production evidence gate even independently of its measured 8-D scientific failure.

### 3. Production all-in FLOPs — FAIL against authoritative cap

The E121 protocol/receipt accounts production all-in cost as `275,184,628,736` FLOPs for `d=n=1024`, depth `16`, `P=128`, `M=64`, `8192` propagated directions.

It compares this against an internal `0.13 * 2^41 = 285,873,023,221.76` cap and marks that local gate passed.

The authoritative successor control cap is instead `136,758,472,261` incremental production all-in FLOPs.

Thus E121 exceeds the authoritative cap by `138,426,156,475` FLOPs, or about `2.0122x` the allowed total. Its local FLOP PASS must not be interpreted as a control/production PASS.

## Control decision

- E119 remains terminally closed; no E119 action is authorized.
- E121 protocol-first ordering is recognized, but E121 is **TERMINAL NO-GO** from its own frozen 8-D falsifier.
- E121 additionally fails the control production-evidence gate on both missing certified total remainder and authoritative all-in FLOP cap.
- No E121 rerun, rescue, P/M rebalance, retuning, scientific mutation, benchmark/public access, merge, canonical mutation, or ledger mutation is authorized.

## Exactly one bounded correction

For the next collision-free successor identity (E122 or later after a fresh live namespace check), create a **protocol-only first commit** that, before any implementation or workflow execution, freezes both (a) a pre-oracle deterministic total error/remainder certificate with all missing components failing closed and production threshold `<=1.374772708486752e-4`, and (b) a complete production all-in accounting path capped at exactly `136,758,472,261` incremental FLOPs. Do not implement or execute until that protocol intake passes.
