# ARC control violation — E134 reserved verifier reused as scientific owner

Recorded: 2026-09-20 21:08 +03

Control key: `ARC-CONTROL-E134-RESERVED-VERIFIER-REUSE-VIOLATION-20260920-2108`

Status: **FAIL-CLOSED / APPEND-ONLY CONTROL VIOLATION**.

## Live authoritative predecessor

Immediately before this note, authoritative control tip was `f0fab549f4eb02aa0d41045923f11d5e3a5294c4` (`control: seal E132 and watch E133-E135`). That receipt explicitly reserved E134 only for an independent review of the frozen E132 tuple and stated that E134 was not collision-free for unrelated new science. It identified E135 as the only clean owner namespace among E133/E134/E135.

## Violation

A conflicting scientific owner lane now exists:

- branch: `research/e134-source-k3-direct-closure-20260920`;
- terminal tip: `e0ad6c1563bcdbc8ca380b10dfdbb62fbc955193`;
- protocol commit claimed by its terminal receipt: `efe7fb20133944885a2af0f057ee531383107010`;
- candidate commit: `716dc606b6a181987279da520125b7f9bd8e7d6b`;
- executed workflow head: `0418edfa4f916121c53b9a591669f20877467ab4`;
- Actions run/job: `35526963588 / 106120701515`, attempt 1, conclusion `failure`;
- artifact: `10610071720`, `e134-source-k3-direct-closure`, SHA256 `db9c660ca93043b73c9cd7ce4f98cadde393434f9fef416cb493fa0015a49454`;
- immutable scientific terminal receipt: `research/E134_TERMINAL_RECEIPT.json` at `e0ad6c1563bcdbc8ca380b10dfdbb62fbc955193`.

The Actions job confirms focused tests passed, then `Sole frozen E134 exact-small scientific run` failed. The owner receipt states failure occurred before candidate/reference execution with `ModuleNotFoundError: No module named 'methods'`; therefore no scientific MSE or residual certificate was produced.

This is a namespace/control violation regardless of the terminal instrument NO-GO: E134 was already reserved as the sole review-only verifier identity for E132 and was not available for a new scientific mechanism.

## Independent production-cap check

The conflicting E134 receipt reports `all_in_upper_flops = 189262033408`, but compares it against its own `0.13 * 2^41 = 285873023221.76` cap. The authoritative control cap for successor production claims is `136758472261` incremental all-in FLOPs. Therefore this lane would also fail the authoritative production-cost gate:

- reported all-in: `189262033408`;
- authoritative cap: `136758472261`;
- excess: `52503561147` FLOPs;
- ratio: approximately `1.3839x` the authoritative cap.

No production GO, scientific GO, verifier status, or E132 verification may be inferred from this E134 lane.

## E119 invariant

No evidence in this event changes the E119 terminal closure or its sole authoritative execution tuple `35458020001 / 105936659806 / 10589345345 / sha256:7485a4380bca0175197afeb327aed9abeb2f5d14ca335cdff6571ad0c7ed78e3`.

## Exactly one bounded correction

**Quarantine E134 permanently as collided/invalid for both new science and E132 verification; do not rerun, repair, rename, or reinterpret this lane. The next new owner mechanism may use only a freshly live-verified collision-free ID, with E135 as the current candidate namespace, and must begin with a protocol-only first commit before any implementation or workflow execution.**

No canonical/ledger mutation, merge, scientific-branch mutation, rerun, rescue, tuning, public/public-mini/scorer/holdout/full access, or workflow dispatch is authorized by this receipt.
