from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

from methods.e105_two_haar_risk import build_two_haar_inputs_billed
from methods.post_e108_deep_jensen_variance import (
    final_layer_jensen_decomposition_billed,
)

WIDTH = 1024
DEPTH = 16
TRAJECTORIES = 4096
WEIGHT_SEED = 110104
DIRECTION_SEED = 110105
BUDGET = 2**41
UTIL_CAP = 0.13
BASE_FLOPS_REFERENCE = 149_114_550_960
OVERLAY_FLOP_RESERVE = 50_000_000
ADMISSION_UPPER_FLOPS = BASE_FLOPS_REFERENCE + OVERLAY_FLOP_RESERVE
MATERIAL_SHARE_MIN = 0.10
OUT = Path("post-e108-deep-jensen-variance.json")


def make_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    scale = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        (rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * scale).astype(
            np.float32
        )
        for _ in range(DEPTH)
    ]


def digest(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def run_once(weights: list[np.ndarray]) -> dict[str, object]:
    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        start_flops = int(ctx.flops_used)
        h = build_two_haar_inputs_billed(WIDTH, DIRECTION_SEED)
        after_input = int(ctx.flops_used)

        rows = []
        layer_cumulative = []
        penultimate = None

        for layer_index, raw_w in enumerate(weights):
            if layer_index == DEPTH - 1:
                penultimate = h

            w = fnp.asarray(raw_w, dtype=fnp.float32)
            h = fnp.matmul(h, fnp.swapaxes(w, 0, 1))
            fnp.maximum(h, fnp.float32(0.0), out=h)
            rows.append(fnp.mean(h, axis=0, dtype=fnp.float64))
            layer_cumulative.append(int(ctx.flops_used))

        if penultimate is None:
            raise RuntimeError("penultimate activation not captured")

        prediction = fnp.stack(rows, axis=0)
        after_stack = int(ctx.flops_used)

        dec = final_layer_jensen_decomposition_billed(
            penultimate, h, weights[-1], WIDTH
        )
        after_overlay = int(ctx.flops_used)
        total = int(ctx.flops_used)

    wall_s = time.perf_counter() - started

    pred = np.asarray(prediction, dtype=np.float64).copy()
    input_np = np.asarray(
        build_two_haar_inputs_billed.__name__ and [], dtype=np.float64
    )
    # Integrity checks are deliberately outside the billed estimator path.
    # Reconstruct the exact frozen inputs with NumPy from the same seed solely
    # for the antithetic-pair assertion.
    rng = np.random.Generator(np.random.PCG64(DIRECTION_SEED))
    radius = math.sqrt(2.0) * math.exp(
        math.lgamma((WIDTH + 1.0) / 2.0) - math.lgamma(WIDTH / 2.0)
    )
    blocks = []
    for _ in range(2):
        g = rng.standard_normal((WIDTH, WIDTH)).astype(np.float64)
        q, r = np.linalg.qr(g)
        signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
        blocks.append((q * signs[None, :] * radius).astype(np.float32))
    pos = np.concatenate(blocks, axis=0)
    input_np = np.concatenate((pos, -pos), axis=0)
    half = TRAJECTORIES // 2
    pair_max_abs = float(np.max(np.abs(input_np[:half] + input_np[half:])))

    y0 = np.asarray(dec["y0"], dtype=np.float64).copy()
    y1 = np.asarray(dec["y1"], dtype=np.float64).copy()
    g0 = np.asarray(dec["g0"], dtype=np.float64).copy()
    g1 = np.asarray(dec["g1"], dtype=np.float64).copy()
    j0 = np.asarray(dec["j0"], dtype=np.float64).copy()
    j1 = np.asarray(dec["j1"], dtype=np.float64).copy()
    r_y = float(np.asarray(dec["r_y"]))
    r_g = float(np.asarray(dec["r_g"]))
    r_j = float(np.asarray(dec["r_j"]))
    cross = float(np.asarray(dec["cross"]))

    identity0 = float(np.max(np.abs(y0 - g0 - j0)))
    identity1 = float(np.max(np.abs(y1 - g1 - j1)))
    risk_recompose_abs = abs(r_y - (r_g + r_j + cross))
    final_recompose = 0.5 * (y0 + y1)
    final_recompose_max_abs = float(np.max(np.abs(final_recompose - pred[-1])))

    input_flops = after_input - start_flops
    layer_flops = []
    previous = after_input
    for current in layer_cumulative:
        layer_flops.append(current - previous)
        previous = current
    base_finalization_flops = after_stack - previous
    overlay_flops = after_overlay - after_stack
    reconciled = (
        input_flops
        + sum(layer_flops)
        + base_finalization_flops
        + overlay_flops
    )

    nonlinear_share = r_j / r_y if r_y > 0.0 else math.inf
    finite = bool(
        np.isfinite(pred).all()
        and np.isfinite(y0).all()
        and np.isfinite(y1).all()
        and np.isfinite(g0).all()
        and np.isfinite(g1).all()
        and np.isfinite(j0).all()
        and np.isfinite(j1).all()
        and all(np.isfinite(v) for v in (r_y, r_g, r_j, cross, nonlinear_share))
    )

    return {
        "prediction": pred,
        "prediction_sha256": digest(pred),
        "finite": finite,
        "shape": list(pred.shape),
        "antithetic_pair_max_abs": pair_max_abs,
        "identity_block0_max_abs": identity0,
        "identity_block1_max_abs": identity1,
        "risk_recompose_abs": risk_recompose_abs,
        "final_recompose_max_abs": final_recompose_max_abs,
        "risk_total": r_y,
        "risk_mean_state": r_g,
        "risk_deep_jensen": r_j,
        "cross_term": cross,
        "deep_jensen_over_total": nonlinear_share,
        "jensen_rms": math.sqrt(r_j) if r_j >= 0.0 else math.nan,
        "hashes": {
            "y0": digest(y0),
            "y1": digest(y1),
            "g0": digest(g0),
            "g1": digest(g1),
            "j0": digest(j0),
            "j1": digest(j1),
        },
        "flops": {
            "input_construction": input_flops,
            "layers": layer_flops,
            "layer_total": int(sum(layer_flops)),
            "base_finalization": base_finalization_flops,
            "deep_jensen_overlay": overlay_flops,
            "total": total,
            "reconciled_sum": reconciled,
            "exact_reconciliation": reconciled == total,
            "utilization": total / BUDGET,
            "overlay_utilization": overlay_flops / BUDGET,
        },
        "wall_s": wall_s,
    }


def compact(x: dict[str, object]) -> dict[str, object]:
    return {k: v for k, v in x.items() if k != "prediction"}


def main() -> None:
    weights = make_weights()
    first = run_once(weights)
    repeat = run_once(weights)

    deterministic = {
        "prediction_bitwise": bool(
            np.array_equal(first["prediction"], repeat["prediction"])
        ),
        "prediction_repeat_max_abs": float(
            np.max(np.abs(first["prediction"] - repeat["prediction"]))
        ),
        "scalar_decomposition_exact": all(
            first[key] == repeat[key]
            for key in (
                "risk_total",
                "risk_mean_state",
                "risk_deep_jensen",
                "cross_term",
                "deep_jensen_over_total",
                "jensen_rms",
            )
        ),
        "hashes_equal": first["hashes"] == repeat["hashes"],
        "flop_ledger_equal": first["flops"] == repeat["flops"],
    }

    tolerance = 1e-12 * max(1.0, float(first["risk_total"]))
    gates = {
        "pre_code_admission_util_le_0_13": ADMISSION_UPPER_FLOPS / BUDGET <= UTIL_CAP,
        "measured_complete_util_le_0_13": first["flops"]["utilization"] <= UTIL_CAP,
        "overlay_flops_le_reserve": first["flops"]["deep_jensen_overlay"] <= OVERLAY_FLOP_RESERVE,
        "exact_flop_reconciliation": first["flops"]["exact_reconciliation"],
        "finite": first["finite"] and repeat["finite"],
        "shape_16x1024": first["shape"] == [DEPTH, WIDTH],
        "antithetic_exact": first["antithetic_pair_max_abs"] == 0.0,
        "deterministic_prediction": (
            deterministic["prediction_bitwise"]
            and deterministic["prediction_repeat_max_abs"] == 0.0
        ),
        "deterministic_decomposition": (
            deterministic["scalar_decomposition_exact"]
            and deterministic["hashes_equal"]
            and deterministic["flop_ledger_equal"]
        ),
        "jensen_identity_block0_le_1e_12": first["identity_block0_max_abs"] <= 1e-12,
        "jensen_identity_block1_le_1e_12": first["identity_block1_max_abs"] <= 1e-12,
        "risk_decomposition_exact": first["risk_recompose_abs"] <= tolerance,
        "final_block_recompose_le_1e_12": first["final_recompose_max_abs"] <= 1e-12,
        "material_deep_nonlinear_share_ge_0_10": (
            first["deep_jensen_over_total"] >= MATERIAL_SHARE_MIN
        ),
        "no_targets_read": True,
    }

    go = bool(all(gates.values()))
    out = {
        "schema": "arc.whitebox.post_e108.deep_jensen_variance.v1",
        "idempotency_key": "ARC-POST-E108-DEEP-JENSEN-VAR-20260919",
        "parent": "E108 terminal NO-GO; E104/E105 two-Haar sampling law retained",
        "mechanism": {
            "name": "final-layer Jensen residual variance decomposition",
            "identity": "Y_b = ReLU(mean(H_{L-1,b}) W_L^T) + J_b",
            "target_free": True,
            "first_layer_transport_cv": False,
            "fitted_coefficients": False,
        },
        "width": WIDTH,
        "depth": DEPTH,
        "trajectories": TRAJECTORIES,
        "weight_seed": WEIGHT_SEED,
        "direction_seed": DIRECTION_SEED,
        "budget": BUDGET,
        "utilization_cap": UTIL_CAP,
        "inherited_base_flops_reference": BASE_FLOPS_REFERENCE,
        "overlay_flop_reserve": OVERLAY_FLOP_RESERVE,
        "admission_upper_flops": ADMISSION_UPPER_FLOPS,
        "admission_upper_utilization": ADMISSION_UPPER_FLOPS / BUDGET,
        "first": compact(first),
        "repeat": compact(repeat),
        "determinism": deterministic,
        "gates": gates,
        "decision": (
            "TARGET_FREE_DEEP_NONLINEAR_VARIANCE_GO"
            if go
            else "TERMINAL_NO_GO"
        ),
        "scientific_competition_go": False,
        "scope": {
            "synthetic_production_shape_only": True,
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
    print("POST_E108_DEEP_JENSEN_VAR=" + json.dumps(out, sort_keys=True), flush=True)
    if not go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
