from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from methods.hybrid_deep_kink_remainder import layer_hybrid_identity

WIDTH = 8
DEPTH = 4
WEIGHT_SEED = 111104
DIRECTION_SEED = 111105
BUDGET = 2**41
BASE_FLOPS = 149_114_550_960
OVERLAY_RESERVE = 1_000_000_000
UTIL_CAP = 0.13
OUT = Path("hybrid-deep-kink-remainder-smallwidth.json")


def mean_chi_radius(width: int) -> float:
    return math.sqrt(2.0) * math.exp(
        math.lgamma((width + 1.0) / 2.0) - math.lgamma(width / 2.0)
    )


def make_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    scale = math.sqrt(2.0 / WIDTH)
    return [
        rng.standard_normal((WIDTH, WIDTH)).astype(np.float64) * scale
        for _ in range(DEPTH)
    ]


def make_inputs() -> tuple[np.ndarray, float, float]:
    rng = np.random.Generator(np.random.PCG64(DIRECTION_SEED))
    blocks = []
    max_orth = 0.0
    for _ in range(2):
        g = rng.standard_normal((WIDTH, WIDTH)).astype(np.float64)
        q, r = np.linalg.qr(g)
        signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
        q = q * signs[None, :]
        max_orth = max(
            max_orth,
            float(np.max(np.abs(q.T @ q - np.eye(WIDTH, dtype=np.float64)))),
        )
        blocks.append(mean_chi_radius(WIDTH) * q)
    pos = np.concatenate(blocks, axis=0)
    x = np.concatenate((pos, -pos), axis=0)
    pair = float(np.max(np.abs(x[: 2 * WIDTH] + x[2 * WIDTH :])))
    return x, pair, max_orth


def run_once() -> dict[str, object]:
    weights = make_weights()
    h, pair_max_abs, orth_max_abs = make_inputs()
    layer_rows = []

    max_mean = 0.0
    max_pointwise = 0.0
    max_piecewise = 0.0
    max_offsupport = 0.0
    max_anchor_mean = 0.0
    min_remainder = math.inf

    for index, w in enumerate(weights, start=1):
        h, stats = layer_hybrid_identity(h, w)
        layer_rows.append({"layer": index, **stats})
        max_mean = max(max_mean, float(stats["mean_reconstruction_max_abs"]))
        max_pointwise = max(max_pointwise, float(stats["pointwise_identity_max_abs"]))
        max_piecewise = max(max_piecewise, float(stats["piecewise_remainder_max_abs"]))
        max_offsupport = max(max_offsupport, float(stats["offsupport_remainder_max_abs"]))
        max_anchor_mean = max(
            max_anchor_mean,
            float(stats["anchor_vs_direct_preactivation_mean_max_abs"]),
        )
        min_remainder = min(min_remainder, float(stats["remainder_min"]))

    support_fraction_mean = float(
        np.mean([row["support_fraction"] for row in layer_rows])
    )
    support_fraction_max = float(
        np.max([row["support_fraction"] for row in layer_rows])
    )
    energy_fraction_mean = float(
        np.mean([row["remainder_energy_fraction_vs_activation"] for row in layer_rows])
    )
    energy_fraction_max = float(
        np.max([row["remainder_energy_fraction_vs_activation"] for row in layer_rows])
    )

    final = np.asarray(h, dtype=np.float64)
    return {
        "finite": bool(np.isfinite(final).all()),
        "final_sha256": hashlib.sha256(
            np.ascontiguousarray(final).tobytes()
        ).hexdigest(),
        "antithetic_pair_max_abs": pair_max_abs,
        "haar_orthogonality_max_abs": orth_max_abs,
        "max_mean_reconstruction_abs": max_mean,
        "max_pointwise_identity_abs": max_pointwise,
        "max_piecewise_remainder_abs": max_piecewise,
        "max_offsupport_remainder_abs": max_offsupport,
        "max_anchor_vs_direct_preactivation_mean_abs": max_anchor_mean,
        "minimum_remainder": min_remainder,
        "mean_support_fraction": support_fraction_mean,
        "max_support_fraction": support_fraction_max,
        "mean_remainder_energy_fraction_vs_activation": energy_fraction_mean,
        "max_remainder_energy_fraction_vs_activation": energy_fraction_max,
        "layers": layer_rows,
    }


def signature(out: dict[str, object]) -> np.ndarray:
    vals = [
        out["antithetic_pair_max_abs"],
        out["haar_orthogonality_max_abs"],
        out["max_mean_reconstruction_abs"],
        out["max_pointwise_identity_abs"],
        out["max_piecewise_remainder_abs"],
        out["max_offsupport_remainder_abs"],
        out["max_anchor_vs_direct_preactivation_mean_abs"],
        out["minimum_remainder"],
        out["mean_support_fraction"],
        out["max_support_fraction"],
        out["mean_remainder_energy_fraction_vs_activation"],
        out["max_remainder_energy_fraction_vs_activation"],
    ]
    for row in out["layers"]:
        vals.extend(
            [
                row["mean_reconstruction_max_abs"],
                row["pointwise_identity_max_abs"],
                row["piecewise_remainder_max_abs"],
                row["offsupport_remainder_max_abs"],
                row["support_fraction"],
                row["remainder_energy_fraction_vs_activation"],
            ]
        )
    return np.asarray(vals, dtype=np.float64)


def main() -> None:
    first = run_once()
    second = run_once()
    replay = float(np.max(np.abs(signature(first) - signature(second))))

    production_upper_flops = BASE_FLOPS + OVERLAY_RESERVE
    production_upper_util = production_upper_flops / BUDGET

    gates = {
        "finite": first["finite"] and second["finite"],
        "antithetic_exact": first["antithetic_pair_max_abs"] == 0.0,
        "pointwise_identity_le_1e_12": first["max_pointwise_identity_abs"] <= 1e-12,
        "mean_reconstruction_le_1e_12": first["max_mean_reconstruction_abs"] <= 1e-12,
        "piecewise_remainder_le_1e_12": first["max_piecewise_remainder_abs"] <= 1e-12,
        "offsupport_remainder_le_1e_12": first["max_offsupport_remainder_abs"] <= 1e-12,
        "remainder_nonnegative_to_1e_12": first["minimum_remainder"] >= -1e-12,
        "deterministic_replay_eq_0": replay == 0.0,
        "production_static_budget_util_le_0_13": production_upper_util <= UTIL_CAP,
        "no_targets_read": True,
    }
    go = bool(all(gates.values()))

    out = {
        "schema": "arc.whitebox.hybrid_deep_kink_remainder.smallwidth.v1",
        "idempotency_key": "ARC-HYBRID-DEEP-KINK-REMAINDER-20260919",
        "width": WIDTH,
        "depth": DEPTH,
        "trajectories": 4 * WIDTH,
        "weight_seed": WEIGHT_SEED,
        "direction_seed": DIRECTION_SEED,
        "first": first,
        "repeat": second,
        "deterministic_replay_max_abs": replay,
        "budget_admission": {
            "budget": BUDGET,
            "base_flops": BASE_FLOPS,
            "overlay_reserve_flops": OVERLAY_RESERVE,
            "upper_flops": production_upper_flops,
            "upper_utilization": production_upper_util,
            "cap": UTIL_CAP,
            "production_executed": False,
        },
        "gates": gates,
        "decision": (
            "SMALLWIDTH_IDENTITY_AND_BUDGET_GO"
            if go
            else "TERMINAL_SMALLWIDTH_NO_GO"
        ),
        "production_successor_authorized_by_this_result": bool(go),
        "scope": {
            "small_width_only": True,
            "production_shape_executed": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
            "target_fitting": False,
            "tuning": False,
            "sweep": False,
            "rescue": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("HYBRID_DEEP_KINK_REMAINDER=" + json.dumps(out, sort_keys=True), flush=True)
    if not go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
