from __future__ import annotations

import json

import flopscope as flops
import numpy as np

from methods.e012_batched_joiner import (
    candidate_scratch_bytes,
    joiner_batched,
    joiner_separate,
)

N = 1024
RANK = 384
SEED = 20260914
ERROR_GATE = 5e-7
RESIDUAL_RATIO_GATE = 0.70
MEMORY_GATE_BYTES = 8 * 1024**2
FLOP_BUDGET = 5_000_000_000


def _buffers(dtype):
    return (
        np.empty((2, N, RANK), dtype=dtype),
        np.empty((2, N, RANK), dtype=dtype),
        np.empty((N, RANK), dtype=dtype),
    )


def _measure(fn):
    with flops.BudgetContext(
        flop_budget=FLOP_BUDGET,
        wall_time_limit_s=60.0,
    ) as ctx:
        out = fn()
    return np.asarray(out).copy(), ctx


def _residual_s(ctx) -> float:
    return float(ctx.residual_wall_time_s)


def _backend_s(ctx) -> float:
    return float(ctx.flopscope_backend_time_s)


def _overhead_s(ctx) -> float:
    return float(ctx.flopscope_overhead_time_s)


def _wall_s(ctx) -> float:
    return float(ctx.wall_time_s)


def main() -> int:
    rng = np.random.default_rng(SEED)
    ap = rng.standard_normal((2, N, N), dtype=np.float32)
    weights = rng.standard_normal((2, N, 1), dtype=np.float32)
    omega = rng.standard_normal((N, RANK), dtype=np.float32)

    sep_inner, sep_outer, sep_out = _buffers(ap.dtype)
    bat_inner, bat_outer, bat_out = _buffers(ap.dtype)
    det_inner, det_outer, det_out = _buffers(ap.dtype)

    def separate():
        return joiner_separate(
            ap,
            weights,
            omega,
            inner=sep_inner,
            outer=sep_outer,
            out=sep_out,
        )

    def batched():
        return joiner_batched(
            ap,
            weights,
            omega,
            inner=bat_inner,
            outer=bat_outer,
            out=bat_out,
        )

    def batched_repeat():
        return joiner_batched(
            ap,
            weights,
            omega,
            inner=det_inner,
            outer=det_outer,
            out=det_out,
        )

    # Warm the exact signatures once. Warm-up contexts are excluded from gates.
    _measure(separate)
    _measure(batched)

    baseline, baseline_ctx = _measure(separate)
    candidate, candidate_ctx = _measure(batched)
    candidate_repeat, _ = _measure(batched_repeat)

    rel_error = float(
        np.linalg.norm(candidate - baseline) / np.linalg.norm(baseline)
    )
    deterministic = bool(np.array_equal(candidate, candidate_repeat))
    baseline_flops = int(baseline_ctx.flops_used)
    candidate_flops = int(candidate_ctx.flops_used)
    baseline_residual = _residual_s(baseline_ctx)
    candidate_residual = _residual_s(candidate_ctx)
    residual_ratio = (
        candidate_residual / baseline_residual
        if baseline_residual > 0.0
        else float("inf")
    )
    scratch_bytes = candidate_scratch_bytes(N, RANK, 4)

    gates = {
        "correctness": rel_error <= ERROR_GATE,
        "determinism": deterministic,
        "metered_flops": candidate_flops <= baseline_flops,
        "residual_ratio": residual_ratio <= RESIDUAL_RATIO_GATE,
        "scratch_memory": scratch_bytes <= MEMORY_GATE_BYTES,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"

    result = {
        "experiment": "E012",
        "scope": "synthetic joiner transform only; no whest scorer",
        "seed": SEED,
        "n": N,
        "rank": RANK,
        "baseline_numeric_calls": 7,
        "candidate_numeric_calls": 4,
        "baseline_flops": baseline_flops,
        "candidate_flops": candidate_flops,
        "flop_ratio": candidate_flops / baseline_flops,
        "relative_frobenius_error": rel_error,
        "deterministic": deterministic,
        "baseline_residual_s": baseline_residual,
        "candidate_residual_s": candidate_residual,
        "residual_ratio": residual_ratio,
        "baseline_backend_s": _backend_s(baseline_ctx),
        "candidate_backend_s": _backend_s(candidate_ctx),
        "baseline_wrapper_overhead_s": _overhead_s(baseline_ctx),
        "candidate_wrapper_overhead_s": _overhead_s(candidate_ctx),
        "baseline_wall_s": _wall_s(baseline_ctx),
        "candidate_wall_s": _wall_s(candidate_ctx),
        "candidate_scratch_bytes": scratch_bytes,
        "candidate_scratch_mib": scratch_bytes / 1024**2,
        "gates": gates,
        "decision": decision,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"DECISION={decision}")

    if not gates["correctness"]:
        print("BLOCKER=batched schedule exceeds the fixed 5e-7 error gate")
    elif not gates["determinism"]:
        print("BLOCKER=identical candidate executions are not bit-identical")
    elif not gates["metered_flops"]:
        print("BLOCKER=batched schedule increases billed FLOPs")
    elif not gates["residual_ratio"]:
        print("BLOCKER=batched schedule does not reduce residual time by 30%")
    elif not gates["scratch_memory"]:
        print("BLOCKER=pair-batched scratch exceeds 8 MiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
