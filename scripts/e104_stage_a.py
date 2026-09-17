from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

WIDTH = 32
DEPTH = 6
NETWORK_SEEDS = tuple(range(104000, 104008))
REFERENCE_SEEDS = tuple(range(404000, 404008))
DIRECTION_SEEDS = tuple(range(204000, 204008))
RADIUS_SEEDS = tuple(range(304000, 304008))
REFERENCE_SAMPLES = 65536
CANDIDATE_SAMPLES = 2048
PROD_UTIL_UPPER = 0.0677789313122048
OUT = Path("e104-stage-a.json")


def make_weights(seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    scale = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        (rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * scale).astype(np.float32)
        for _ in range(DEPTH)
    ]


def iid_antithetic(seed: int, total: int) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(seed))
    pos = rng.standard_normal((total // 2, WIDTH), dtype=np.float32)
    return np.concatenate((pos, -pos), axis=0)


def haar_directions(seed: int, total: int) -> np.ndarray:
    if total % (2 * WIDTH):
        raise ValueError("total must be divisible by 2*WIDTH")
    rng = np.random.Generator(np.random.PCG64(seed))
    blocks = []
    for _ in range(total // (2 * WIDTH)):
        g = rng.standard_normal((WIDTH, WIDTH)).astype(np.float64)
        q, r = np.linalg.qr(g)
        diag = np.diag(r)
        signs = np.where(diag < 0.0, -1.0, 1.0)
        blocks.append(q * signs[None, :])
    return np.concatenate(blocks, axis=0)


def mean_radius(width: int) -> float:
    return math.sqrt(2.0) * math.exp(
        math.lgamma((width + 1.0) / 2.0) - math.lgamma(width / 2.0)
    )


def samples_random_radius(directions: np.ndarray, radius_seed: int) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(radius_seed))
    radii = np.sqrt(rng.chisquare(df=WIDTH, size=directions.shape[0]))
    pos = (radii[:, None] * directions).astype(np.float32)
    return np.concatenate((pos, -pos), axis=0)


def samples_rb(directions: np.ndarray) -> np.ndarray:
    pos = (mean_radius(WIDTH) * directions).astype(np.float32)
    return np.concatenate((pos, -pos), axis=0)


def final_mean(weights: list[np.ndarray], samples: np.ndarray) -> np.ndarray:
    h = np.asarray(samples, dtype=np.float32)
    for w in weights:
        h = h @ w.T
        np.maximum(h, np.float32(0.0), out=h)
    return np.mean(h, axis=0, dtype=np.float64)


def layer_vector(weights: list[np.ndarray], x: np.ndarray) -> np.ndarray:
    h = np.asarray(x, dtype=np.float32)[None, :]
    rows = []
    for w in weights:
        h = h @ w.T
        np.maximum(h, np.float32(0.0), out=h)
        rows.append(h[0].astype(np.float64))
    return np.stack(rows)


def mse(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.mean(d * d))


def run_once() -> dict:
    rows = []
    sse_random = 0.0
    sse_rb = 0.0
    coordinates = 0
    homogeneity_max_rel = 0.0
    all_finite = True
    pair_max_abs = 0.0
    direction_hashes_match = True

    for i, network_seed in enumerate(NETWORK_SEEDS):
        weights = make_weights(network_seed)
        directions = haar_directions(DIRECTION_SEEDS[i], CANDIDATE_SAMPLES)
        digest_before = hashlib.sha256(directions.tobytes()).hexdigest()

        random_samples = samples_random_radius(directions, RADIUS_SEEDS[i])
        digest_after_random = hashlib.sha256(directions.tobytes()).hexdigest()
        rb_samples = samples_rb(directions)
        digest_after_rb = hashlib.sha256(directions.tobytes()).hexdigest()
        direction_hashes_match &= (
            digest_before == digest_after_random == digest_after_rb
        )

        half = CANDIDATE_SAMPLES // 2
        pair_max_abs = max(
            pair_max_abs,
            float(np.max(np.abs(random_samples[:half] + random_samples[half:]))),
            float(np.max(np.abs(rb_samples[:half] + rb_samples[half:]))),
        )

        reference = final_mean(
            weights, iid_antithetic(REFERENCE_SEEDS[i], REFERENCE_SAMPLES)
        )
        random_mean = final_mean(weights, random_samples)
        rb_mean = final_mean(weights, rb_samples)

        random_mse = mse(random_mean, reference)
        rb_mse = mse(rb_mean, reference)
        random_err = random_mean - reference
        rb_err = rb_mean - reference
        sse_random += float(np.sum(random_err * random_err))
        sse_rb += float(np.sum(rb_err * rb_err))
        coordinates += WIDTH

        q = directions[0].astype(np.float32)
        radius = np.float32(1.75)
        h_q = layer_vector(weights, q)
        h_rq = layer_vector(weights, radius * q)
        scale = max(float(np.max(np.abs(h_rq))), 1e-30)
        hom_rel = float(np.max(np.abs(h_rq - float(radius) * h_q)) / scale)
        homogeneity_max_rel = max(homogeneity_max_rel, hom_rel)

        finite = bool(
            np.isfinite(reference).all()
            and np.isfinite(random_mean).all()
            and np.isfinite(rb_mean).all()
        )
        all_finite &= finite
        rows.append(
            {
                "network_seed": network_seed,
                "random_radius_mse": random_mse,
                "rao_blackwell_mse": rb_mse,
                "rb_over_random": rb_mse / random_mse if random_mse > 0.0 else math.inf,
                "finite": finite,
                "homogeneity_relative_error": hom_rel,
            }
        )

    ratios = np.asarray([r["rb_over_random"] for r in rows], dtype=np.float64)
    aggregate_random = sse_random / coordinates
    aggregate_rb = sse_rb / coordinates
    return {
        "rows": rows,
        "aggregate_random_radius_mse": float(aggregate_random),
        "aggregate_rao_blackwell_mse": float(aggregate_rb),
        "aggregate_rb_over_random": float(sse_rb / sse_random),
        "rb_wins": int(np.sum(ratios < 1.0)),
        "worst_rb_over_random": float(np.max(ratios)),
        "homogeneity_max_relative_error": homogeneity_max_rel,
        "direction_hashes_unchanged": bool(direction_hashes_match),
        "antithetic_pair_max_abs": pair_max_abs,
        "all_finite": bool(all_finite),
        "mean_radius": mean_radius(WIDTH),
    }


def signature(result: dict) -> np.ndarray:
    vals = [
        result["aggregate_random_radius_mse"],
        result["aggregate_rao_blackwell_mse"],
        result["aggregate_rb_over_random"],
        float(result["rb_wins"]),
        result["worst_rb_over_random"],
        result["homogeneity_max_relative_error"],
        result["antithetic_pair_max_abs"],
    ]
    for row in result["rows"]:
        vals.extend(
            [
                row["random_radius_mse"],
                row["rao_blackwell_mse"],
                row["rb_over_random"],
                row["homogeneity_relative_error"],
            ]
        )
    return np.asarray(vals, dtype=np.float64)


def main() -> None:
    first = run_once()
    repeat = run_once()
    replay_max_abs = float(np.max(np.abs(signature(first) - signature(repeat))))

    gates = {
        "all_finite": first["all_finite"],
        "deterministic_replay_eq_0": replay_max_abs == 0.0,
        "homogeneity_rel_le_2e_6": first["homogeneity_max_relative_error"] <= 2e-6,
        "directions_unchanged": first["direction_hashes_unchanged"],
        "antithetic_pair_exact": first["antithetic_pair_max_abs"] == 0.0,
        "aggregate_rb_over_random_le_0_90": first["aggregate_rb_over_random"] <= 0.90,
        "rb_wins_ge_6_of_8": first["rb_wins"] >= 6,
        "worst_rb_over_random_le_1_25": first["worst_rb_over_random"] <= 1.25,
        "production_util_upper_le_0_12": PROD_UTIL_UPPER <= 0.12,
    }
    go = bool(all(gates.values()))
    out = {
        "schema": "arc.whitebox.e104.haar_radial_raoblackwell.stage_a.v1",
        "experiment": "E104",
        "stage": "A",
        "width": WIDTH,
        "depth": DEPTH,
        "network_seeds": NETWORK_SEEDS,
        "reference_seeds": REFERENCE_SEEDS,
        "direction_seeds": DIRECTION_SEEDS,
        "radius_seeds": RADIUS_SEEDS,
        "reference_samples": REFERENCE_SAMPLES,
        "candidate_samples": CANDIDATE_SAMPLES,
        "first": first,
        "replay_max_abs": replay_max_abs,
        "production_utilization_upper_bound_from_e103": PROD_UTIL_UPPER,
        "gates": gates,
        "go": go,
        "scientific_go": bool(go),
        "decision": "LOCAL_SCIENTIFIC_GO" if go else "TERMINAL_NO_GO_DROP",
        "scope": {
            "synthetic_only": True,
            "public": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "targets_from_benchmark": False,
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E104_STAGE_A=" + json.dumps(out, sort_keys=True), flush=True)
    if not go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
