from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

# Frozen target-free calibration probe.
WIDTH = 64
DEPTH = 8
NETWORK_SEED = 104960
REPLICATES = 32
SEED_BASE = 804960

# Frozen production-shape overlay probe inherited from E104 independent verify.
PROD_WIDTH = 1024
PROD_TRAJECTORIES = 4096
PROD_BASE_FLOPS = 149_047_442_096
BUDGET = 2**41
UTIL_LIMIT = 0.135
OVERLAY_UTIL_LIMIT = 0.001
OUT = Path("e104-target-free-blockvar-probe.json")


def mean_chi_radius(width: int) -> float:
    return math.sqrt(2.0) * math.exp(
        math.lgamma((width + 1.0) / 2.0) - math.lgamma(width / 2.0)
    )


def make_weights(seed: int, width: int, depth: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    scale = np.float32(math.sqrt(2.0 / width))
    return [
        (rng.standard_normal((width, width), dtype=np.float32) * scale).astype(
            np.float32
        )
        for _ in range(depth)
    ]


def haar_block(seed: int, width: int) -> tuple[np.ndarray, float]:
    rng = np.random.Generator(np.random.PCG64(seed))
    g = rng.standard_normal((width, width)).astype(np.float64)
    q, r = np.linalg.qr(g)
    signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
    q = q * signs[None, :]
    orth = q.T @ q
    orth_err = float(np.max(np.abs(orth - np.eye(width, dtype=np.float64))))
    return q, orth_err


def block_mean(
    weights: list[np.ndarray], seed: int, width: int
) -> tuple[np.ndarray, float, float]:
    q, orth_err = haar_block(seed, width)
    pos = (mean_chi_radius(width) * q).astype(np.float32)
    x = np.concatenate((pos, -pos), axis=0)
    pair_err = float(np.max(np.abs(x[:width] + x[width:])))

    h = x
    for w in weights:
        h = h @ w.T
        np.maximum(h, np.float32(0.0), out=h)
    mean = np.mean(h, axis=0, dtype=np.float64)
    return mean, orth_err, pair_err


def run_calibration() -> tuple[dict[str, object], np.ndarray, np.ndarray]:
    weights = make_weights(NETWORK_SEED, WIDTH, DEPTH)
    estimates = []
    predicted_scalar = []
    max_orth = 0.0
    max_pair = 0.0
    all_finite = True

    for r in range(REPLICATES):
        y1, o1, p1 = block_mean(weights, SEED_BASE + 2 * r, WIDTH)
        y2, o2, p2 = block_mean(weights, SEED_BASE + 2 * r + 1, WIDTH)
        m = 0.5 * (y1 + y2)
        vcoord = 0.25 * (y1 - y2) ** 2
        estimates.append(m)
        predicted_scalar.append(float(np.mean(vcoord)))
        max_orth = max(max_orth, o1, o2)
        max_pair = max(max_pair, p1, p2)
        all_finite = bool(
            all_finite
            and np.isfinite(y1).all()
            and np.isfinite(y2).all()
            and np.isfinite(m).all()
            and np.isfinite(vcoord).all()
        )

    estimate_arr = np.stack(estimates, axis=0)
    predicted_arr = np.asarray(predicted_scalar, dtype=np.float64)
    empirical_coord_var = np.var(estimate_arr, axis=0, ddof=1)
    empirical = float(np.mean(empirical_coord_var))
    predicted = float(np.mean(predicted_arr))
    ratio = predicted / empirical if empirical > 0.0 else math.inf

    summary = {
        "width": WIDTH,
        "depth": DEPTH,
        "network_seed": NETWORK_SEED,
        "replicates": REPLICATES,
        "seed_base": SEED_BASE,
        "mean_chi_radius": mean_chi_radius(WIDTH),
        "all_finite": all_finite,
        "haar_orthogonality_max_abs": max_orth,
        "antithetic_pair_max_abs": max_pair,
        "mean_predicted_variance": predicted,
        "empirical_repeat_variance": empirical,
        "calibration_ratio": ratio,
        "rms_standard_error": math.sqrt(predicted) if predicted >= 0.0 else math.nan,
        "estimate_sha256": hashlib.sha256(estimate_arr.tobytes()).hexdigest(),
        "predicted_variance_sha256": hashlib.sha256(
            predicted_arr.tobytes()
        ).hexdigest(),
    }
    return summary, estimate_arr, predicted_arr


def production_overlay_once() -> dict[str, object]:
    rng = np.random.Generator(np.random.PCG64(904104))
    raw = rng.standard_normal(
        (PROD_TRAJECTORIES, PROD_WIDTH), dtype=np.float32
    )
    raw = np.maximum(raw, np.float32(0.0))
    h = fnp.asarray(raw)

    half = PROD_TRAJECTORIES // 2
    block = PROD_WIDTH
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        p0 = fnp.mean(h[0:block], axis=0, dtype=fnp.float64)
        n0 = fnp.mean(h[half : half + block], axis=0, dtype=fnp.float64)
        y0 = fnp.multiply(fnp.add(p0, n0), 0.5)

        p1 = fnp.mean(h[block : 2 * block], axis=0, dtype=fnp.float64)
        n1 = fnp.mean(
            h[half + block : half + 2 * block], axis=0, dtype=fnp.float64
        )
        y1 = fnp.multiply(fnp.add(p1, n1), 0.5)

        diff = fnp.subtract(y0, y1)
        vcoord = fnp.multiply(fnp.multiply(diff, diff), 0.25)
        vmean = fnp.mean(vcoord, dtype=fnp.float64)
        rms = fnp.sqrt(vmean)
        overlay_flops = int(ctx.flops_used)

    variance = float(np.asarray(vmean))
    rms_value = float(np.asarray(rms))
    layered_flops = PROD_BASE_FLOPS + overlay_flops
    return {
        "overlay_flops": overlay_flops,
        "overlay_utilization": overlay_flops / BUDGET,
        "base_flops": PROD_BASE_FLOPS,
        "base_utilization": PROD_BASE_FLOPS / BUDGET,
        "layered_flops_upper": layered_flops,
        "layered_utilization_upper": layered_flops / BUDGET,
        "variance_scalar": variance,
        "rms_standard_error": rms_value,
        "finite": bool(np.isfinite(variance) and np.isfinite(rms_value)),
    }


def main() -> None:
    first, first_est, first_pred = run_calibration()
    second, second_est, second_pred = run_calibration()
    replay_max_abs = float(
        max(
            np.max(np.abs(first_est - second_est)),
            np.max(np.abs(first_pred - second_pred)),
        )
    )

    overlay_first = production_overlay_once()
    overlay_second = production_overlay_once()
    overlay_deterministic = bool(
        overlay_first["overlay_flops"] == overlay_second["overlay_flops"]
        and overlay_first["variance_scalar"] == overlay_second["variance_scalar"]
        and overlay_first["rms_standard_error"]
        == overlay_second["rms_standard_error"]
    )

    ratio = float(first["calibration_ratio"])
    gates = {
        "calibration_all_finite": bool(first["all_finite"]),
        "antithetic_pair_exact": first["antithetic_pair_max_abs"] == 0.0,
        "haar_orthogonality_le_1e_12": (
            float(first["haar_orthogonality_max_abs"]) <= 1e-12
        ),
        "deterministic_replay_max_abs_eq_0": replay_max_abs == 0.0,
        "empirical_variance_positive": float(first["empirical_repeat_variance"]) > 0.0,
        "predicted_variance_positive": float(first["mean_predicted_variance"]) > 0.0,
        "calibration_ratio_0_70_to_1_30": 0.70 <= ratio <= 1.30,
        "overlay_flops_positive": int(overlay_first["overlay_flops"]) > 0,
        "overlay_repeat_flops_equal": (
            overlay_first["overlay_flops"] == overlay_second["overlay_flops"]
        ),
        "overlay_deterministic": overlay_deterministic,
        "layered_utilization_le_0_135": (
            float(overlay_first["layered_utilization_upper"]) <= UTIL_LIMIT
        ),
        "overlay_utilization_le_0_001": (
            float(overlay_first["overlay_utilization"]) <= OVERLAY_UTIL_LIMIT
        ),
        "overlay_finite": bool(overlay_first["finite"]),
    }
    go = bool(all(gates.values()))

    out = {
        "schema": "arc.whitebox.e104.target_free_blockvar_probe.v1",
        "experiment": "E104",
        "idempotency_key": "ARC-E104-TARGET-FREE-BLOCKVAR-20260919",
        "estimator": {
            "coordinate_variance": "(Y1-Y2)^2/4",
            "scalar_variance": "mean_j coordinate_variance",
            "rms_standard_error": "sqrt(scalar_variance)",
            "target_free": True,
            "absolute_error_bound": False,
            "interpretation": (
                "unbiased sampling-variance estimator for the mean of two iid Haar "
                "block estimates; RMS value is a standard-error scale, not a "
                "deterministic error certificate"
            ),
        },
        "calibration": first,
        "deterministic_replay_max_abs": replay_max_abs,
        "production_overlay": overlay_first,
        "production_overlay_repeat": overlay_second,
        "gates": gates,
        "decision": "TARGET_FREE_VARIANCE_ESTIMATOR_GO" if go else "TERMINAL_NO_GO",
        "scientific_competition_go": False,
        "scope": {
            "synthetic_only": True,
            "benchmark_targets_read": False,
            "public": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "sweep": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E104_TARGET_FREE_BLOCKVAR_PROBE=" + json.dumps(out, sort_keys=True), flush=True)
    if not go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
