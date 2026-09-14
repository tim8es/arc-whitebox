from __future__ import annotations

import argparse
import json
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

from methods.hk_rectangular import (
    SparseBilinearScheme,
    dense_matmul_flops,
    direct_sparse_nonproduct_flops,
    hk_leaf_128x48_128,
)

CATALOG_COMMIT = "f3a7f0f61b1005666c2cb03f98f2a16727604ea0"
CATALOG_BLOB = "82d1af82132941726bbe67d2e374f77f6e1031a6"
SEED = 20260914
BLOCK = 8
RANK_CHUNK = 64
ERROR_GATE = 2e-6
COST_RATIO_GATE = 0.85
RESIDUAL_OVERHEAD_GATE_S = 0.002
MEMORY_GATE_BYTES = 128 * 1024**2


def _run_measured(fn):
    with flops.BudgetContext(flop_budget=100_000_000, wall_time_limit_s=60.0) as ctx:
        out = fn()
    return out, ctx


def _residual_s(ctx) -> float:
    return float(ctx.residual_wall_time_s)


def _backend_s(ctx) -> float:
    return float(ctx.flopscope_backend_time_s)


def _overhead_s(ctx) -> float:
    return float(ctx.flopscope_overhead_time_s)


def _wall_s(ctx) -> float:
    return float(ctx.wall_time_s)


def main() -> int:
    parser = argparse.ArgumentParser(description="E011 cost-only HK leaf feasibility diagnostic")
    parser.add_argument("--scheme-json", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.scheme_json.read_text(encoding="utf-8"))
    if data.get("n") != [2, 16, 16] or int(data.get("m", -1)) != 392:
        raise RuntimeError("pinned HK source has unexpected shape/rank")
    if data.get("verified") is not True:
        raise RuntimeError("pinned HK source is not marked verified")
    if data.get("commutative") is True:
        raise RuntimeError("pinned HK source is commutative-only and cannot be block-lifted")

    scheme = SparseBilinearScheme.from_catalog_json(data).orient_16_2_16()
    if any(abs(c) != 1 for cols in (scheme.u, scheme.v, scheme.w) for col in cols for c in col.coeffs):
        raise RuntimeError("prototype requires the pinned +/-1 integer HK schedule")

    rng = np.random.default_rng(SEED)
    a = rng.standard_normal((128, 48), dtype=np.float32)
    b = rng.standard_normal((48, 128), dtype=np.float32)

    # Warm exact operation signatures once; these runs are not used for the gate.
    _run_measured(lambda: fnp.matmul(a, b))
    _run_measured(lambda: hk_leaf_128x48_128(a, b, scheme, block=BLOCK, rank_chunk=RANK_CHUNK))

    dense, dense_ctx = _run_measured(lambda: fnp.matmul(a, b))
    candidate, hk_ctx = _run_measured(
        lambda: hk_leaf_128x48_128(a, b, scheme, block=BLOCK, rank_chunk=RANK_CHUNK)
    )
    candidate_2, _ = _run_measured(
        lambda: hk_leaf_128x48_128(a, b, scheme, block=BLOCK, rank_chunk=RANK_CHUNK)
    )

    dense_np = np.asarray(dense)
    candidate_np = np.asarray(candidate)
    candidate_2_np = np.asarray(candidate_2)
    rel_error = float(np.linalg.norm(candidate_np - dense_np) / np.linalg.norm(dense_np))
    deterministic = bool(np.array_equal(candidate_np, candidate_2_np))
    dense_flops = int(dense_ctx.flops_used)
    hk_flops = int(hk_ctx.flops_used)
    cost_ratio = hk_flops / dense_flops
    residual_overhead = _residual_s(hk_ctx) - _residual_s(dense_ctx)

    expected_dense = dense_matmul_flops(128, 48, 128)
    rank_product_flops = 3 * 392 * dense_matmul_flops(8, 8, 8)
    measured_nonproduct = hk_flops - rank_product_flops
    schedule_nonproduct = direct_sparse_nonproduct_flops(scheme, block=BLOCK, pairs=3)
    nonproduct_allowance = int(COST_RATIO_GATE * expected_dense) - rank_product_flops

    # Projection for production vectorisation: by<=6, P=343, chunk=64, three L/R/M buffers.
    projected_rank_buffers = 6 * 343 * RANK_CHUNK * BLOCK * BLOCK * 4 * 3

    gates = {
        "correctness": rel_error <= ERROR_GATE,
        "metered_cost": cost_ratio <= COST_RATIO_GATE,
        "residual": residual_overhead <= RESIDUAL_OVERHEAD_GATE_S,
        "memory_projection": projected_rank_buffers <= MEMORY_GATE_BYTES,
        "determinism": deterministic,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"

    result = {
        "experiment": "E011",
        "scope": "synthetic tier-1 leaf only; no whest scorer",
        "catalog_commit": CATALOG_COMMIT,
        "catalog_blob": CATALOG_BLOB,
        "seed": SEED,
        "shape": "128x48 @ 48x128",
        "block": BLOCK,
        "rank": scheme.rank,
        "rank_chunk": RANK_CHUNK,
        "dense_flops_expected": expected_dense,
        "dense_flops_measured": dense_flops,
        "hk_rank_product_flops": rank_product_flops,
        "hk_nonproduct_flops_schedule": schedule_nonproduct,
        "hk_nonproduct_flops_measured": measured_nonproduct,
        "hk_total_flops_measured": hk_flops,
        "cost_ratio": cost_ratio,
        "relative_frobenius_error": rel_error,
        "deterministic": deterministic,
        "dense_wall_s": _wall_s(dense_ctx),
        "dense_residual_s": _residual_s(dense_ctx),
        "dense_backend_s": _backend_s(dense_ctx),
        "dense_wrapper_overhead_s": _overhead_s(dense_ctx),
        "hk_wall_s": _wall_s(hk_ctx),
        "hk_residual_s": _residual_s(hk_ctx),
        "residual_overhead_s": residual_overhead,
        "hk_backend_s": _backend_s(hk_ctx),
        "hk_wrapper_overhead_s": _overhead_s(hk_ctx),
        "projected_rank_buffers_bytes": projected_rank_buffers,
        "projected_rank_buffers_mib": projected_rank_buffers / 1024**2,
        "nonproduct_flop_allowance_for_15pct_gate": nonproduct_allowance,
        "gates": gates,
        "decision": decision,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"DECISION={decision}")
    if not gates["correctness"]:
        print("BLOCKER=float32 relative error exceeds 2e-6")
    elif not gates["metered_cost"]:
        print(
            "BLOCKER=metered encode/decode/accumulation overhead exceeds the fixed 15% "
            "leaf-cost gate"
        )
    elif not gates["residual"]:
        print("BLOCKER=participant residual overhead exceeds 2 ms on the smallest leaf diagnostic")
    elif not gates["memory_projection"]:
        print("BLOCKER=rank-chunk production buffer projection exceeds 128 MiB")
    elif not gates["determinism"]:
        print("BLOCKER=identical seeded executions are not bit-identical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
