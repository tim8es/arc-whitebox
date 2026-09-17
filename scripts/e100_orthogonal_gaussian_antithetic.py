from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

WIDTH = 32
DEPTH = 6
NETWORK_SEEDS = tuple(range(100000, 100008))
REFERENCE_SAMPLES = 65536
CANDIDATE_SAMPLES = 2048
REFERENCE_SEEDS = tuple(range(400000, 400008))
IID_SEEDS = tuple(range(300000, 300008))
ORTHO_SEEDS = tuple(range(200000, 200008))

PROD_WIDTH = 1024
PROD_DEPTH = 16
PROD_SAMPLES = 4096
BUDGET = 2**41


def make_weights(seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    scale = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        (rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * scale).astype(np.float32)
        for _ in range(DEPTH)
    ]


def antithetic_iid(seed: int, total_samples: int) -> np.ndarray:
    if total_samples % 2:
        raise ValueError("total_samples must be even")
    rng = np.random.Generator(np.random.PCG64(seed))
    pos = rng.standard_normal((total_samples // 2, WIDTH), dtype=np.float32)
    return np.concatenate([pos, -pos], axis=0)


def haar_orthogonal_antithetic(seed: int, total_samples: int) -> np.ndarray:
    if total_samples % (2 * WIDTH):
        raise ValueError("total_samples must be divisible by 2*WIDTH")
    rng = np.random.Generator(np.random.PCG64(seed))
    positive_blocks: list[np.ndarray] = []
    n_blocks = total_samples // (2 * WIDTH)
    for _ in range(n_blocks):
        g = rng.standard_normal((WIDTH, WIDTH)).astype(np.float64)
        q, r = np.linalg.qr(g)
        diag = np.diag(r)
        signs = np.where(diag < 0.0, -1.0, 1.0)
        q = q * signs[None, :]
        radii = np.sqrt(rng.chisquare(df=WIDTH, size=WIDTH)).astype(np.float64)
        block = (radii[:, None] * q).astype(np.float32)
        positive_blocks.append(block)
    pos = np.concatenate(positive_blocks, axis=0)
    return np.concatenate([pos, -pos], axis=0)


def final_mean(weights: list[np.ndarray], x: np.ndarray) -> np.ndarray:
    h = np.asarray(x, dtype=np.float32)
    for w in weights:
        h = h @ w.T
        np.maximum(h, np.float32(0.0), out=h)
    return np.mean(h, axis=0, dtype=np.float64)


def mse(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.mean(d * d))


def production_cost_bound() -> dict:
    n = PROD_WIDTH
    N = PROD_SAMPLES
    forward = int(2 * N * PROD_DEPTH * n * n)
    qr = int(math.ceil(2.0 * (4.0 / 3.0) * n**3))
    radial_and_reduction = int(4 * N * n)
    total = forward + qr + radial_and_reduction
    return {
        "forward_flops": forward,
        "qr_flops": qr,
        "radial_and_reduction_flops": radial_and_reduction,
        "total_flops": total,
        "utilization": float(total / BUDGET),
    }


def run_once() -> dict:
    rows: list[dict] = []
    iid_sse = 0.0
    ortho_sse = 0.0
    coord_count = 0

    for i, net_seed in enumerate(NETWORK_SEEDS):
        weights = make_weights(net_seed)
        reference = final_mean(
            weights, antithetic_iid(REFERENCE_SEEDS[i], REFERENCE_SAMPLES)
        )
        iid = final_mean(weights, antithetic_iid(IID_SEEDS[i], CANDIDATE_SAMPLES))
        ortho = final_mean(
            weights, haar_orthogonal_antithetic(ORTHO_SEEDS[i], CANDIDATE_SAMPLES)
        )

        iid_err = iid - reference
        ortho_err = ortho - reference
        iid_mse = float(np.mean(iid_err * iid_err))
        ortho_mse = float(np.mean(ortho_err * ortho_err))
        iid_sse += float(np.sum(iid_err * iid_err))
        ortho_sse += float(np.sum(ortho_err * ortho_err))
        coord_count += WIDTH

        rows.append(
            {
                "network_seed": net_seed,
                "iid_mse": iid_mse,
                "orthogonal_mse": ortho_mse,
                "orthogonal_over_iid": ortho_mse / iid_mse if iid_mse > 0.0 else math.inf,
                "iid_max_abs_error": float(np.max(np.abs(iid_err))),
                "orthogonal_max_abs_error": float(np.max(np.abs(ortho_err))),
                "finite": bool(
                    np.isfinite(reference).all()
                    and np.isfinite(iid).all()
                    and np.isfinite(ortho).all()
                ),
            }
        )

    ratios = np.asarray([r["orthogonal_over_iid"] for r in rows], dtype=np.float64)
    return {
        "rows": rows,
        "aggregate_iid_mse": float(iid_sse / coord_count),
        "aggregate_orthogonal_mse": float(ortho_sse / coord_count),
        "aggregate_orthogonal_over_iid": float(ortho_sse / iid_sse)
        if iid_sse > 0.0
        else math.inf,
        "orthogonal_wins": int(np.sum(ratios < 1.0)),
        "worst_orthogonal_over_iid": float(np.max(ratios)),
        "all_finite": bool(all(r["finite"] for r in rows)),
        "cost": production_cost_bound(),
    }


def scalar_signature(result: dict) -> np.ndarray:
    vals = [
        result["aggregate_iid_mse"],
        result["aggregate_orthogonal_mse"],
        result["aggregate_orthogonal_over_iid"],
        float(result["orthogonal_wins"]),
        result["worst_orthogonal_over_iid"],
        result["cost"]["utilization"],
    ]
    for row in result["rows"]:
        vals.extend(
            [
                row["iid_mse"],
                row["orthogonal_mse"],
                row["orthogonal_over_iid"],
                row["iid_max_abs_error"],
                row["orthogonal_max_abs_error"],
            ]
        )
    return np.asarray(vals, dtype=np.float64)


def main() -> None:
    first = run_once()
    repeat = run_once()
    replay_max_abs = float(
        np.max(np.abs(scalar_signature(first) - scalar_signature(repeat)))
    )

    gates = {
        "all_finite": first["all_finite"],
        "deterministic_replay_le_1e_12": replay_max_abs <= 1e-12,
        "aggregate_ratio_le_0_75": first["aggregate_orthogonal_over_iid"] <= 0.75,
        "orthogonal_wins_ge_6_of_8": first["orthogonal_wins"] >= 6,
        "worst_ratio_le_1_25": first["worst_orthogonal_over_iid"] <= 1.25,
        "production_util_le_0_12": first["cost"]["utilization"] <= 0.12,
    }
    go = bool(all(gates.values()))
    out = {
        "schema": "arc.whitebox.e100.orthogonal_gaussian_antithetic.stage_a.v1",
        "experiment": "E100",
        "stage": "A",
        "scope": {
            "synthetic_only": True,
            "public": False,
            "official_scorer": False,
            "benchmark_holdout": False,
            "full_suite": False,
            "target_fitting": False,
        },
        "width": WIDTH,
        "depth": DEPTH,
        "network_seeds": NETWORK_SEEDS,
        "reference_samples": REFERENCE_SAMPLES,
        "candidate_samples": CANDIDATE_SAMPLES,
        "reference_seeds": REFERENCE_SEEDS,
        "iid_seeds": IID_SEEDS,
        "orthogonal_seeds": ORTHO_SEEDS,
        "first": first,
        "replay_max_abs": replay_max_abs,
        "gates": gates,
        "go": go,
        "scientific_go": False,
        "decision": "GO_NEW_IMPLEMENTATION_ID" if go else "NO-GO/DROP",
    }
    Path("e100-stage-a.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("E100_STAGE_A_JSON=" + json.dumps(out, sort_keys=True), flush=True)
    if not go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
