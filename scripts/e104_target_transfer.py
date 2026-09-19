from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

WIDTH = 1024
DEPTH = 16
TRAJECTORIES = 4096
WEIGHT_SEED = 104204
DIRECTION_SEED = 104205
BUDGET = 2**41
TARGET_MSE_SCALE = 1.89e-8
PRIOR_E104_PRODUCTION_FLOPS = 149_047_442_096
PRIOR_E104_PRODUCTION_UTIL = 0.06777892944955966
OUT = Path("e104-target-transfer.json")


def mean_chi_radius(width: int) -> float:
    return math.sqrt(2.0) * math.exp(
        math.lgamma((width + 1.0) / 2.0) - math.lgamma(width / 2.0)
    )


def chi_radius_variance(width: int) -> float:
    mu = mean_chi_radius(width)
    return float(width - mu * mu)


def make_weights(width: int, depth: int, seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    scale = np.float32(math.sqrt(2.0 / width))
    return [
        (rng.standard_normal((width, width), dtype=np.float32) * scale).astype(np.float32)
        for _ in range(depth)
    ]


def reference_haar_directions_numpy(
    width: int, trajectories: int, seed: int
) -> np.ndarray:
    positive = trajectories // 2
    if trajectories % 2 or positive % width:
        raise ValueError("trajectories/2 must be divisible by width")
    rng = np.random.Generator(np.random.PCG64(seed))
    blocks: list[np.ndarray] = []
    for _ in range(positive // width):
        g = rng.standard_normal((width, width)).astype(np.float64)
        q, r = np.linalg.qr(g)
        signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
        blocks.append(q * signs[None, :])
    return np.concatenate(blocks, axis=0)


def haar_block_orthogonality_max_abs(directions: np.ndarray, width: int) -> float:
    eye = np.eye(width, dtype=np.float64)
    worst = 0.0
    for start in range(0, directions.shape[0], width):
        block = directions[start : start + width]
        gram = block.T @ block
        worst = max(worst, float(np.max(np.abs(gram - eye))))
    return worst


def build_e104_inputs_billed(width: int, trajectories: int, seed: int):
    positive = trajectories // 2
    if trajectories % 2 or positive % width:
        raise ValueError("trajectories/2 must be divisible by width")
    rng = np.random.Generator(np.random.PCG64(seed))
    mu = mean_chi_radius(width)
    blocks = []
    for _ in range(positive // width):
        g = fnp.asarray(rng.standard_normal((width, width)).astype(np.float64))
        q, r = fnp.linalg.qr(g)
        signs = fnp.where(fnp.diag(r) < 0.0, -1.0, 1.0)
        q = fnp.multiply(q, signs[None, :])
        blocks.append(fnp.multiply(q, mu).astype(fnp.float32))
    pos = fnp.concatenate(blocks, axis=0)
    return fnp.concatenate((pos, -pos), axis=0)


def propagate_vector(weights: list[np.ndarray], x: np.ndarray) -> np.ndarray:
    h = np.asarray(x, dtype=np.float32)[None, :]
    rows = []
    for raw_w in weights:
        h = h @ raw_w.T
        np.maximum(h, np.float32(0.0), out=h)
        rows.append(h[0].astype(np.float64))
    return np.stack(rows, axis=0)


def homogeneity_relative_error(
    weights: list[np.ndarray], direction: np.ndarray, radius: float = 1.75
) -> float:
    r = np.float32(radius)
    base = propagate_vector(weights, direction)
    scaled = propagate_vector(weights, r * direction.astype(np.float32))
    denom = max(float(np.max(np.abs(scaled))), 1e-30)
    return float(np.max(np.abs(scaled - float(r) * base)) / denom)


def conditional_radial_mse_from_scaled_pairs(
    scaled_pairs: np.ndarray, chi_width: int
) -> float:
    pairs = np.asarray(scaled_pairs, dtype=np.float64)
    if pairs.ndim != 2:
        raise ValueError("scaled_pairs must be [positive_directions, output_width]")
    m, output_width = pairs.shape
    mu = mean_chi_radius(chi_width)
    relative_radius_variance = chi_radius_variance(chi_width) / (mu * mu)
    sum_sq = float(np.sum(pairs * pairs, dtype=np.float64))
    return float(relative_radius_variance * sum_sq / (m * m * output_width))


def run_transfer() -> dict[str, object]:
    weights = make_weights(WIDTH, DEPTH, WEIGHT_SEED)
    reference_directions = reference_haar_directions_numpy(
        WIDTH, TRAJECTORIES, DIRECTION_SEED
    )
    orthogonality = haar_block_orthogonality_max_abs(reference_directions, WIDTH)
    homogeneity = homogeneity_relative_error(weights, reference_directions[0])

    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        start_flops = int(ctx.flops_used)
        h = build_e104_inputs_billed(WIDTH, TRAJECTORIES, DIRECTION_SEED)
        after_input = int(ctx.flops_used)
        input_snapshot = np.asarray(h, dtype=np.float32).copy()

        rows = []
        layer_cumulative = []
        for raw_w in weights:
            w = fnp.asarray(raw_w)
            h = fnp.matmul(h, fnp.swapaxes(w, 0, 1))
            fnp.maximum(h, fnp.float32(0.0), out=h)
            rows.append(fnp.mean(h, axis=0, dtype=fnp.float64))
            layer_cumulative.append(int(ctx.flops_used))

        final_h = np.asarray(h, dtype=np.float32).copy()
        prediction = fnp.stack(rows, axis=0)
        after_stack = int(ctx.flops_used)
        total_flops = int(ctx.flops_used)

    wall_s = time.perf_counter() - started
    pred = np.asarray(prediction, dtype=np.float64).copy()

    input_flops = after_input - start_flops
    layer_flops: list[int] = []
    previous = after_input
    for current in layer_cumulative:
        layer_flops.append(current - previous)
        previous = current
    finalization_flops = after_stack - previous
    reconciled = input_flops + sum(layer_flops) + finalization_flops

    half = TRAJECTORIES // 2
    antithetic_pair_max_abs = float(
        np.max(np.abs(input_snapshot[:half] + input_snapshot[half:]))
    )
    mu = mean_chi_radius(WIDTH)
    billed_positive_directions = input_snapshot[:half].astype(np.float64) / mu
    direction_parity_max_abs = float(
        np.max(np.abs(billed_positive_directions - reference_directions))
    )

    final64 = final_h.astype(np.float64)
    scaled_pairs = 0.5 * (final64[:half] + final64[half:])
    rb_final_from_pairs = np.mean(scaled_pairs, axis=0, dtype=np.float64)
    final_prediction_pair_diff = float(
        np.max(np.abs(rb_final_from_pairs - pred[-1]))
    )

    radial_mse = conditional_radial_mse_from_scaled_pairs(scaled_pairs, WIDTH)
    radial_rms = math.sqrt(radial_mse)
    rb_signal_mse_about_zero = float(np.mean(rb_final_from_pairs * rb_final_from_pairs))
    rb_signal_rms = math.sqrt(rb_signal_mse_about_zero)
    target_scale_ratio = radial_mse / TARGET_MSE_SCALE
    radial_rms_over_signal_rms = (
        radial_rms / rb_signal_rms if rb_signal_rms > 0.0 else math.inf
    )

    finite = bool(
        np.isfinite(pred).all()
        and np.isfinite(final64).all()
        and math.isfinite(radial_mse)
        and math.isfinite(radial_rms)
    )
    utilization = total_flops / BUDGET

    gates = {
        "finite": finite,
        "prediction_shape_16x1024": list(pred.shape) == [DEPTH, WIDTH],
        "antithetic_input_pair_exact": antithetic_pair_max_abs == 0.0,
        "haar_orthogonality_le_1e_10": orthogonality <= 1e-10,
        "homogeneity_rel_le_2e_6": homogeneity <= 2e-6,
        "utilization_le_0_12": utilization <= 0.12,
        "radial_mse_finite_positive": math.isfinite(radial_mse) and radial_mse > 0.0,
        "target_scale_materiality_ge_1_89e_8": radial_mse >= TARGET_MSE_SCALE,
        "no_targets_read": True,
    }
    transfer_pass = bool(all(gates.values()))

    return {
        "schema": "arc.whitebox.e104.target_free_transfer.v1",
        "experiment": "E104",
        "idempotency_key": "ARC-E104-TARGET-FREE-TRANSFER-20260919",
        "mechanism_changed": False,
        "production_shape": {
            "width": WIDTH,
            "depth": DEPTH,
            "trajectories": TRAJECTORIES,
            "positive_directions": half,
            "weight_seed": WEIGHT_SEED,
            "direction_seed": DIRECTION_SEED,
            "budget": BUDGET,
            "mean_chi_radius": mu,
            "chi_radius_variance": chi_radius_variance(WIDTH),
        },
        "structural": {
            "prediction_shape": list(pred.shape),
            "prediction_sha256": hashlib.sha256(pred.tobytes()).hexdigest(),
            "prediction_max_abs": float(np.max(np.abs(pred))),
            "antithetic_input_pair_max_abs": antithetic_pair_max_abs,
            "haar_block_orthogonality_max_abs": orthogonality,
            "homogeneity_relative_error": homogeneity,
            "billed_vs_reference_direction_max_abs": direction_parity_max_abs,
            "final_prediction_pair_mean_max_abs_diff": final_prediction_pair_diff,
            "finite": finite,
        },
        "measured_estimator_cost": {
            "input_construction_flops": input_flops,
            "layer_flops": layer_flops,
            "layer_total_flops": int(sum(layer_flops)),
            "finalization_flops": finalization_flops,
            "reconciled_flops": int(reconciled),
            "flopscope_total_flops": total_flops,
            "exact_reconciliation": int(reconciled) == total_flops,
            "utilization": utilization,
            "wall_s": wall_s,
            "prior_e104_production_verify_flops": PRIOR_E104_PRODUCTION_FLOPS,
            "delta_vs_prior_e104_flops": total_flops - PRIOR_E104_PRODUCTION_FLOPS,
            "prior_e104_production_verify_utilization": PRIOR_E104_PRODUCTION_UTIL,
        },
        "target_free_transfer_metric": {
            "definition": "exact conditional pooled final-layer MSE of E100 random-radius estimator around E104 conditional mean, given the frozen Haar directions",
            "exact_conditional_radial_mse_removed": radial_mse,
            "radial_noise_rms": radial_rms,
            "rb_signal_mse_about_zero": rb_signal_mse_about_zero,
            "rb_signal_rms": rb_signal_rms,
            "radial_rms_over_rb_signal_rms": radial_rms_over_signal_rms,
            "competition_target_mse_scale": TARGET_MSE_SCALE,
            "radial_mse_over_target_scale": target_scale_ratio,
            "uses_targets": False,
        },
        "gates": gates,
        "transfer_established": transfer_pass,
        "decision": (
            "TARGET_FREE_TRANSFER_PASS"
            if transfer_pass
            else "TARGET_FREE_TRANSFER_NO_GO"
        ),
        "scientific_go": False,
        "raw_competition_mse": None,
        "raw_competition_mse_evaluated": False,
        "scope": {
            "synthetic_production_shape_only": True,
            "public": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
            "tuning": False,
            "sweep": False,
        },
    }


def main() -> None:
    out = run_transfer()
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E104_TARGET_TRANSFER=" + json.dumps(out, sort_keys=True), flush=True)
    if not out["transfer_established"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
