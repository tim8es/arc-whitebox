from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

WIDTH = 64
DEPTH = 8
NETWORK_SEEDS = (104800, 104801, 104802, 104803)
DIRECTION_SET_COUNT = 16
POSITIVE_DIRECTIONS = 256
CALIBRATION_REPLICATES = 8192
CALIBRATION_RADIUS_SEED = 704800
OUT = Path("e104-transfer-variance.json")


def make_weights(seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    scale = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        (rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * scale).astype(
            np.float32
        )
        for _ in range(DEPTH)
    ]


def mean_chi_radius(width: int) -> float:
    return math.sqrt(2.0) * math.exp(
        math.lgamma((width + 1.0) / 2.0) - math.lgamma(width / 2.0)
    )


def direction_seed(network_index: int, set_index: int) -> int:
    return 604800 + 100 * network_index + set_index


def haar_directions(seed: int) -> tuple[np.ndarray, float]:
    if POSITIVE_DIRECTIONS % WIDTH:
        raise RuntimeError("positive direction count must be divisible by width")
    rng = np.random.Generator(np.random.PCG64(seed))
    blocks: list[np.ndarray] = []
    orthogonality_max_abs = 0.0
    eye = np.eye(WIDTH, dtype=np.float64)
    for _ in range(POSITIVE_DIRECTIONS // WIDTH):
        g = rng.standard_normal((WIDTH, WIDTH)).astype(np.float64)
        q, r = np.linalg.qr(g)
        signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
        q = q * signs[None, :]
        err = float(np.max(np.abs(q @ q.T - eye)))
        orthogonality_max_abs = max(orthogonality_max_abs, err)
        blocks.append(q)
    return np.concatenate(blocks, axis=0), orthogonality_max_abs


def antithetic_response(
    weights: list[np.ndarray], directions: np.ndarray
) -> tuple[np.ndarray, float]:
    pos = directions.astype(np.float32)
    samples = np.concatenate((pos, -pos), axis=0)
    half = POSITIVE_DIRECTIONS
    pair_max_abs = float(np.max(np.abs(samples[:half] + samples[half:])))

    h = samples
    for w in weights:
        h = h @ w.T
        np.maximum(h, np.float32(0.0), out=h)

    response = 0.5 * (
        h[:half].astype(np.float64) + h[half:].astype(np.float64)
    )
    return response, pair_max_abs


def exact_terms(response: np.ndarray) -> tuple[np.ndarray, float]:
    m = response.shape[0]
    p = response.shape[1]
    mu_r = mean_chi_radius(WIDTH)
    var_r = WIDTH - mu_r * mu_r
    z = mu_r * np.mean(response, axis=0, dtype=np.float64)
    radial = var_r * float(np.sum(response * response)) / (m * m * p)
    return z, radial


def radial_calibration(
    response: np.ndarray, z: np.ndarray, analytic_radial: float
) -> dict:
    rng = np.random.Generator(np.random.PCG64(CALIBRATION_RADIUS_SEED))
    m, p = response.shape
    batch = 512
    sse = 0.0
    count = 0
    for start in range(0, CALIBRATION_REPLICATES, batch):
        k = min(batch, CALIBRATION_REPLICATES - start)
        radii = np.sqrt(rng.chisquare(df=WIDTH, size=(k, m)))
        estimates = (radii @ response) / m
        delta = estimates - z[None, :]
        sse += float(np.sum(delta * delta))
        count += k * p
    empirical = sse / count
    rel = abs(empirical - analytic_radial) / max(analytic_radial, 1e-300)
    return {
        "replicates": CALIBRATION_REPLICATES,
        "radius_seed": CALIBRATION_RADIUS_SEED,
        "analytic_radial_variance_per_coordinate": analytic_radial,
        "empirical_radial_variance_per_coordinate": empirical,
        "relative_error": rel,
    }


def run_once() -> dict:
    mu_r = mean_chi_radius(WIDTH)
    var_r = WIDTH - mu_r * mu_r

    rows = []
    max_orth = 0.0
    max_pair = 0.0
    all_finite = True
    calibration_payload = None

    for network_index, network_seed in enumerate(NETWORK_SEEDS):
        weights = make_weights(network_seed)
        z_rows = []
        radial_rows = []

        for set_index in range(DIRECTION_SET_COUNT):
            directions, orth = haar_directions(
                direction_seed(network_index, set_index)
            )
            response, pair = antithetic_response(weights, directions)
            z, radial = exact_terms(response)

            max_orth = max(max_orth, orth)
            max_pair = max(max_pair, pair)
            all_finite &= bool(
                np.isfinite(response).all()
                and np.isfinite(z).all()
                and math.isfinite(radial)
            )
            z_rows.append(z)
            radial_rows.append(radial)

            if network_index == 0 and set_index == 0:
                calibration_payload = radial_calibration(response, z, radial)

        z_stack = np.stack(z_rows, axis=0)
        center = np.mean(z_stack, axis=0, dtype=np.float64)
        directional_variance = float(
            np.sum((z_stack - center[None, :]) ** 2)
            / ((DIRECTION_SET_COUNT - 1) * WIDTH)
        )
        radial_variance = float(np.mean(radial_rows))
        total = directional_variance + radial_variance
        ratio = directional_variance / total if total > 0.0 else math.inf
        radial_share = radial_variance / total if total > 0.0 else 0.0

        rows.append(
            {
                "network_seed": network_seed,
                "directional_variance_per_coordinate": directional_variance,
                "mean_exact_radial_variance_per_coordinate": radial_variance,
                "predicted_total_e100_variance_per_coordinate": total,
                "predicted_rb_over_e100_variance": ratio,
                "exactly_removable_radial_share": radial_share,
            }
        )

    if calibration_payload is None:
        raise RuntimeError("missing calibration payload")

    aggregate_directional = float(
        np.mean([r["directional_variance_per_coordinate"] for r in rows])
    )
    aggregate_radial = float(
        np.mean([r["mean_exact_radial_variance_per_coordinate"] for r in rows])
    )
    aggregate_total = aggregate_directional + aggregate_radial
    aggregate_ratio = aggregate_directional / aggregate_total
    aggregate_share = aggregate_radial / aggregate_total

    shares = [r["exactly_removable_radial_share"] for r in rows]
    return {
        "rows": rows,
        "mean_chi_radius": mu_r,
        "chi_radius_variance": var_r,
        "aggregate_directional_variance_per_coordinate": aggregate_directional,
        "aggregate_exact_radial_variance_per_coordinate": aggregate_radial,
        "aggregate_predicted_total_e100_variance_per_coordinate": aggregate_total,
        "aggregate_predicted_rb_over_e100_variance": aggregate_ratio,
        "aggregate_exactly_removable_radial_share": aggregate_share,
        "networks_radial_share_ge_0_05": int(sum(x >= 0.05 for x in shares)),
        "max_direction_orthogonality_abs": max_orth,
        "antithetic_pair_max_abs": max_pair,
        "all_finite": bool(all_finite),
        "calibration": calibration_payload,
    }


def signature(result: dict) -> np.ndarray:
    values = [
        result["mean_chi_radius"],
        result["chi_radius_variance"],
        result["aggregate_directional_variance_per_coordinate"],
        result["aggregate_exact_radial_variance_per_coordinate"],
        result["aggregate_predicted_total_e100_variance_per_coordinate"],
        result["aggregate_predicted_rb_over_e100_variance"],
        result["aggregate_exactly_removable_radial_share"],
        float(result["networks_radial_share_ge_0_05"]),
        result["max_direction_orthogonality_abs"],
        result["antithetic_pair_max_abs"],
        result["calibration"]["analytic_radial_variance_per_coordinate"],
        result["calibration"]["empirical_radial_variance_per_coordinate"],
        result["calibration"]["relative_error"],
    ]
    for row in result["rows"]:
        values.extend(
            [
                row["directional_variance_per_coordinate"],
                row["mean_exact_radial_variance_per_coordinate"],
                row["predicted_total_e100_variance_per_coordinate"],
                row["predicted_rb_over_e100_variance"],
                row["exactly_removable_radial_share"],
            ]
        )
    return np.asarray(values, dtype=np.float64)


def main() -> None:
    first = run_once()
    second = run_once()
    repeat_max_abs = float(np.max(np.abs(signature(first) - signature(second))))

    scientific = {
        "aggregate_rb_over_e100_variance_le_0_90": (
            first["aggregate_predicted_rb_over_e100_variance"] <= 0.90
        ),
        "at_least_3_of_4_radial_share_ge_0_05": (
            first["networks_radial_share_ge_0_05"] >= 3
        ),
        "every_network_rb_over_e100_lt_1": all(
            row["predicted_rb_over_e100_variance"] < 1.0
            for row in first["rows"]
        ),
    }
    integrity = {
        "all_finite": first["all_finite"],
        "deterministic_repeat_eq_0": repeat_max_abs == 0.0,
        "orthogonality_le_1e_12": (
            first["max_direction_orthogonality_abs"] <= 1e-12
        ),
        "antithetic_pair_exact": first["antithetic_pair_max_abs"] == 0.0,
        "chi_radius_variance_positive": first["chi_radius_variance"] > 0.0,
        "every_network_radial_variance_positive": all(
            row["mean_exact_radial_variance_per_coordinate"] > 0.0
            for row in first["rows"]
        ),
        "radial_calibration_rel_le_0_05": (
            first["calibration"]["relative_error"] <= 0.05
        ),
    }
    go = bool(all(integrity.values()) and all(scientific.values()))

    out = {
        "schema": "arc.whitebox.e104.transfer_variance_decomp.v1",
        "experiment": "E104",
        "stage": "TRANSFER_VARIANCE",
        "width": WIDTH,
        "depth": DEPTH,
        "network_seeds": NETWORK_SEEDS,
        "direction_set_count_per_network": DIRECTION_SET_COUNT,
        "positive_directions_per_set": POSITIVE_DIRECTIONS,
        "total_antithetic_trajectories_per_set": 2 * POSITIVE_DIRECTIONS,
        "direction_seed_rule": "604800 + 100*network_index + set_index",
        "first": first,
        "repeat_max_abs": repeat_max_abs,
        "integrity_gates": integrity,
        "scientific_gates": scientific,
        "transfer_variance_go": go,
        "scientific_go": go,
        "decision": "TRANSFER_VARIANCE_GO" if go else "TRANSFER_VARIANCE_NO_GO",
        "accuracy_claim": False,
        "scope": {
            "synthetic_only": True,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
            "reference_targets": False,
            "tuning": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E104_TRANSFER_VARIANCE=" + json.dumps(out, sort_keys=True), flush=True)
    if not go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
