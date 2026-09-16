from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

WIDTH = 128
DEPTH = 6
N_SAMPLES = 32768
RANK = 8
WEIGHT_SEEDS = (97097, 97197)
INPUT_SEEDS = (197097, 197197)
PROD_WIDTH = 1024
PROD_DEPTH = 16
BUDGET = 2**41


def _energy(evals: np.ndarray, r: int) -> float:
    sq = np.square(np.asarray(evals, dtype=np.float64))
    total = float(np.sum(sq))
    if total == 0.0:
        return 0.0
    order = np.argsort(np.abs(evals))[::-1]
    return float(np.sum(sq[order[: min(r, len(order))]]) / total)


def _effective_rank(evals: np.ndarray) -> float:
    sq = np.square(np.asarray(evals, dtype=np.float64))
    total = float(np.sum(sq))
    if total == 0.0:
        return 0.0
    p = sq / total
    p = p[p > 0.0]
    return float(np.exp(-np.sum(p * np.log(p))))


def layer_metrics(h: np.ndarray, network: int, layer: int) -> dict:
    # Moment arithmetic is deliberately float64; the forward pass remains float32.
    x = np.asarray(h, dtype=np.float64)
    mu = np.mean(x, axis=0, dtype=np.float64)
    z = x - mu
    c = (z.T @ z) / float(x.shape[0])
    q = z * z
    m22 = (q.T @ q) / float(x.shape[0])
    var = np.diag(c).copy()
    k22 = m22 - np.outer(var, var) - 2.0 * (c * c)
    np.fill_diagonal(k22, 0.0)
    symmetry_error = float(np.max(np.abs(k22 - k22.T)))
    k22 = 0.5 * (k22 + k22.T)

    finite = bool(np.isfinite(k22).all() and np.isfinite(c).all())
    k_norm = float(np.linalg.norm(k22, ord="fro"))
    c_norm = float(np.linalg.norm(c, ord="fro"))
    signal_ratio = k_norm / max(c_norm * c_norm, 1e-30)

    evals = np.linalg.eigvalsh(k22)
    e1 = _energy(evals, 1)
    e4 = _energy(evals, 4)
    e8 = _energy(evals, 8)
    e16 = _energy(evals, 16)
    rel8 = float(math.sqrt(max(0.0, 1.0 - e8)))
    return {
        "network": network,
        "layer": layer,
        "finite": finite,
        "eligible": bool(signal_ratio >= 1e-5),
        "k22_off_frob": k_norm,
        "cov_frob": c_norm,
        "signal_ratio": signal_ratio,
        "symmetry_error": symmetry_error,
        "effective_rank": _effective_rank(evals),
        "top1_energy": e1,
        "top4_energy": e4,
        "top8_energy": e8,
        "top16_energy": e16,
        "rank8_rel_frob_error": rel8,
        "max_abs_k22": float(np.max(np.abs(k22))),
    }


def run_once() -> dict:
    observations: list[dict] = []
    scale = np.float32(np.sqrt(2.0 / WIDTH))
    for network, (wseed, xseed) in enumerate(zip(WEIGHT_SEEDS, INPUT_SEEDS, strict=True)):
        wrng = np.random.Generator(np.random.PCG64(wseed))
        xrng = np.random.Generator(np.random.PCG64(xseed))
        weights = [
            (wrng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * scale).astype(np.float32)
            for _ in range(DEPTH)
        ]
        h = xrng.standard_normal((N_SAMPLES, WIDTH), dtype=np.float32)
        for layer, w in enumerate(weights):
            h = h @ w.T
            np.maximum(h, np.float32(0.0), out=h)
            observations.append(layer_metrics(h, network, layer))

    energies = np.array([r["top8_energy"] for r in observations], dtype=np.float64)
    errors = np.array([r["rank8_rel_frob_error"] for r in observations], dtype=np.float64)
    final3 = np.array([r["top8_energy"] for r in observations if r["layer"] >= DEPTH - 3], dtype=np.float64)

    # Conservative static production bound: two dense n*n by n*r products per layer,
    # each counted as 2*n*n*r multiply/add FLOPs, plus 20*n*r*r factor arithmetic.
    transport_per_layer = 4 * PROD_WIDTH * PROD_WIDTH * RANK + 20 * PROD_WIDTH * RANK * RANK
    transport_total = int(PROD_DEPTH * transport_per_layer)
    transport_util = transport_total / BUDGET

    return {
        "observations": observations,
        "median_top8_energy": float(np.median(energies)),
        "worst_top8_energy": float(np.min(energies)),
        "worst_final3_top8_energy": float(np.min(final3)),
        "median_rank8_rel_frob_error": float(np.median(errors)),
        "transport_flops_bound": transport_total,
        "transport_util_bound": transport_util,
        "all_finite": bool(all(r["finite"] for r in observations)),
        "all_eligible": bool(all(r["eligible"] for r in observations)),
        "max_symmetry_error": float(max(r["symmetry_error"] for r in observations)),
    }


def scalar_signature(result: dict) -> np.ndarray:
    vals = [
        result["median_top8_energy"],
        result["worst_top8_energy"],
        result["worst_final3_top8_energy"],
        result["median_rank8_rel_frob_error"],
        result["transport_util_bound"],
        result["max_symmetry_error"],
    ]
    for row in result["observations"]:
        vals.extend(
            [
                row["k22_off_frob"],
                row["cov_frob"],
                row["signal_ratio"],
                row["effective_rank"],
                row["top1_energy"],
                row["top4_energy"],
                row["top8_energy"],
                row["top16_energy"],
                row["rank8_rel_frob_error"],
                row["max_abs_k22"],
            ]
        )
    return np.asarray(vals, dtype=np.float64)


def main() -> None:
    first = run_once()
    repeat = run_once()
    a = scalar_signature(first)
    b = scalar_signature(repeat)
    replay_max_abs = float(np.max(np.abs(a - b)))

    gates = {
        "all_finite": first["all_finite"],
        "all_eligible": first["all_eligible"],
        "median_top8_energy_ge_0_90": first["median_top8_energy"] >= 0.90,
        "final3_worst_top8_energy_ge_0_80": first["worst_final3_top8_energy"] >= 0.80,
        "median_rank8_rel_error_le_sqrt_0_10": first["median_rank8_rel_frob_error"] <= math.sqrt(0.10),
        "deterministic_replay_le_1e_12": replay_max_abs <= 1e-12,
        "transport_util_lt_0_01": first["transport_util_bound"] < 0.01,
    }
    go = bool(all(gates.values()))
    out = {
        "experiment": "E097",
        "stage": "A",
        "width": WIDTH,
        "depth": DEPTH,
        "n_samples": N_SAMPLES,
        "rank": RANK,
        "weight_seeds": WEIGHT_SEEDS,
        "input_seeds": INPUT_SEEDS,
        "first": first,
        "replay_max_abs": replay_max_abs,
        "gates": gates,
        "go": go,
        "terminal": "GO_NEW_IMPLEMENTATION_ID" if go else "NO-GO/DROP",
    }
    Path("e097-stage-a.json").write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print("E097_STAGE_A_JSON=" + json.dumps(out, sort_keys=True), flush=True)
    if not go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
