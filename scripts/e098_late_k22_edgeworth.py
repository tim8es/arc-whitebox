from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

WIDTH = 128
DEPTH = 7
N_SAMPLES = 32768
RANK = 8
WEIGHT_SEEDS = (98098, 98198)
INPUT_SEEDS = (198098, 198198)
SOURCE_LAYERS = (3, 4, 5)
PROD_WIDTH = 1024
PROD_REMAINING_LAYERS = 12
BUDGET = 2**41


def normal_pdf(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return np.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def normal_cdf(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    inv_sqrt2 = 1.0 / math.sqrt(2.0)
    return 0.5 * (1.0 + np.asarray([math.erf(float(v) * inv_sqrt2) for v in x]))


def gaussian_relu_mean(mean: np.ndarray, variance: np.ndarray) -> np.ndarray:
    mean = np.asarray(mean, dtype=np.float64)
    variance = np.asarray(variance, dtype=np.float64)
    sigma = np.sqrt(np.maximum(variance, 1e-30))
    t = mean / sigma
    return sigma * normal_pdf(t) + mean * normal_cdf(t)


def k22_from_samples(h: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    x = np.asarray(h, dtype=np.float64)
    mu = np.mean(x, axis=0, dtype=np.float64)
    z = x - mu
    cov = (z.T @ z) / float(x.shape[0])
    q = z * z
    m22 = (q.T @ q) / float(x.shape[0])
    var = np.diag(cov).copy()
    k22 = m22 - np.outer(var, var) - 2.0 * (cov * cov)
    np.fill_diagonal(k22, 0.0)
    symmetry_error = float(np.max(np.abs(k22 - k22.T)))
    k22 = 0.5 * (k22 + k22.T)
    return mu, cov, k22, symmetry_error


def rank_approx(k22: np.ndarray, rank: int) -> tuple[np.ndarray, float, float]:
    evals, evecs = np.linalg.eigh(np.asarray(k22, dtype=np.float64))
    order = np.argsort(np.abs(evals))[::-1]
    idx = order[: min(rank, len(order))]
    total = float(np.sum(evals * evals))
    kept = float(np.sum(evals[idx] * evals[idx]))
    energy = kept / total if total > 0.0 else 0.0
    u = evecs[:, idx]
    approx = (u * evals[idx][None, :]) @ u.T
    rel = math.sqrt(max(0.0, 1.0 - energy))
    return approx, energy, rel


def pair_kappa4(weights: np.ndarray, k22: np.ndarray) -> np.ndarray:
    squared = np.asarray(weights, dtype=np.float64) ** 2
    return 3.0 * np.einsum("ji,ik,jk->j", squared, k22, squared, optimize=True)


def edgeworth_delta(
    pre_mean: np.ndarray, pre_var: np.ndarray, kappa4_pair: np.ndarray
) -> np.ndarray:
    pre_mean = np.asarray(pre_mean, dtype=np.float64)
    pre_var = np.asarray(pre_var, dtype=np.float64)
    sigma = np.sqrt(np.maximum(pre_var, 1e-30))
    a = -pre_mean / sigma
    return (
        np.asarray(kappa4_pair, dtype=np.float64)
        * normal_pdf(a)
        * (a * a - 1.0)
        / (24.0 * sigma**3)
    )


def mse(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.mean(d * d))


def transition_metrics(
    h: np.ndarray,
    next_h: np.ndarray,
    next_weight: np.ndarray,
    network: int,
    source_layer: int,
) -> dict:
    mu, cov, k22, symmetry_error = k22_from_samples(h)
    cov_norm = float(np.linalg.norm(cov, ord="fro"))
    k_norm = float(np.linalg.norm(k22, ord="fro"))
    signal_ratio = k_norm / max(cov_norm * cov_norm, 1e-30)
    k8, energy8, rel8 = rank_approx(k22, RANK)

    w = np.asarray(next_weight, dtype=np.float64)
    pre_mean = w @ mu
    pre_var = np.einsum("ji,ik,jk->j", w, cov, w, optimize=True)
    baseline = gaussian_relu_mean(pre_mean, pre_var)

    full_delta = edgeworth_delta(pre_mean, pre_var, pair_kappa4(w, k22))
    rank8_delta = edgeworth_delta(pre_mean, pre_var, pair_kappa4(w, k8))
    full_prediction = baseline + full_delta
    rank8_prediction = baseline + rank8_delta
    truth = np.mean(np.asarray(next_h, dtype=np.float64), axis=0, dtype=np.float64)

    base_mse = mse(baseline, truth)
    full_mse = mse(full_prediction, truth)
    rank8_mse = mse(rank8_prediction, truth)
    response_denom = max(float(np.linalg.norm(full_delta)), 1e-30)
    response_rel = float(np.linalg.norm(rank8_delta - full_delta) / response_denom)

    return {
        "network": network,
        "source_layer": source_layer,
        "target_layer": source_layer + 1,
        "finite": bool(
            np.isfinite(k22).all()
            and np.isfinite(baseline).all()
            and np.isfinite(full_prediction).all()
            and np.isfinite(rank8_prediction).all()
        ),
        "eligible": bool(signal_ratio >= 1e-5),
        "signal_ratio": signal_ratio,
        "symmetry_error": symmetry_error,
        "rank8_energy": energy8,
        "rank8_rel_frob_error": rel8,
        "gaussian_mse": base_mse,
        "full_k22_mse": full_mse,
        "rank8_k22_mse": rank8_mse,
        "full_over_gaussian": full_mse / base_mse if base_mse > 0.0 else math.inf,
        "rank8_over_gaussian": rank8_mse / base_mse if base_mse > 0.0 else math.inf,
        "rank8_response_vs_full_rel_l2": response_rel,
        "max_abs_full_correction": float(np.max(np.abs(full_delta))),
        "max_abs_rank8_correction": float(np.max(np.abs(rank8_delta))),
        "min_sigma": float(np.sqrt(np.maximum(pre_var, 1e-30)).min()),
        "target_mean_abs_max": float(np.max(np.abs(truth))),
    }


def production_cost_bound() -> dict:
    n = PROD_WIDTH
    r = RANK
    transport = 4 * n * n * r
    maintenance = 20 * n * r * r
    response = 8 * n * n * r
    per_layer = transport + maintenance + response
    total = int(PROD_REMAINING_LAYERS * per_layer)
    return {
        "per_layer_flops": int(per_layer),
        "total_flops": total,
        "utilization": float(total / BUDGET),
    }


def run_once() -> dict:
    rows: list[dict] = []
    scale = np.float32(math.sqrt(2.0 / WIDTH))

    for network, (wseed, xseed) in enumerate(zip(WEIGHT_SEEDS, INPUT_SEEDS, strict=True)):
        wrng = np.random.Generator(np.random.PCG64(wseed))
        xrng = np.random.Generator(np.random.PCG64(xseed))
        weights = [
            (wrng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * scale).astype(np.float32)
            for _ in range(DEPTH)
        ]
        h = xrng.standard_normal((N_SAMPLES, WIDTH), dtype=np.float32)

        for layer in range(SOURCE_LAYERS[0] + 1):
            h = h @ weights[layer].T
            np.maximum(h, np.float32(0.0), out=h)

        for source_layer in SOURCE_LAYERS:
            if source_layer > SOURCE_LAYERS[0]:
                # h was already advanced to this source layer at the previous iteration.
                pass
            next_h = h @ weights[source_layer + 1].T
            np.maximum(next_h, np.float32(0.0), out=next_h)
            rows.append(
                transition_metrics(
                    h=h,
                    next_h=next_h,
                    next_weight=weights[source_layer + 1],
                    network=network,
                    source_layer=source_layer,
                )
            )
            h = next_h

    gaussian_sum = float(sum(r["gaussian_mse"] for r in rows))
    full_sum = float(sum(r["full_k22_mse"] for r in rows))
    rank8_sum = float(sum(r["rank8_k22_mse"] for r in rows))
    energies = np.asarray([r["rank8_energy"] for r in rows], dtype=np.float64)
    response_errors = np.asarray(
        [r["rank8_response_vs_full_rel_l2"] for r in rows], dtype=np.float64
    )
    rank8_ratios = np.asarray([r["rank8_over_gaussian"] for r in rows], dtype=np.float64)
    cost = production_cost_bound()

    return {
        "rows": rows,
        "aggregate_gaussian_mse": gaussian_sum / len(rows),
        "aggregate_full_k22_mse": full_sum / len(rows),
        "aggregate_rank8_k22_mse": rank8_sum / len(rows),
        "aggregate_rank8_over_gaussian": rank8_sum / gaussian_sum if gaussian_sum > 0.0 else math.inf,
        "median_rank8_energy": float(np.median(energies)),
        "median_response_preservation_rel_l2": float(np.median(response_errors)),
        "worst_rank8_over_gaussian": float(np.max(rank8_ratios)),
        "rank8_improvement_count": int(np.sum(rank8_ratios < 1.0)),
        "all_finite": bool(all(r["finite"] for r in rows)),
        "all_eligible": bool(all(r["eligible"] for r in rows)),
        "cost": cost,
    }


def scalar_signature(result: dict) -> np.ndarray:
    vals = [
        result["aggregate_gaussian_mse"],
        result["aggregate_full_k22_mse"],
        result["aggregate_rank8_k22_mse"],
        result["aggregate_rank8_over_gaussian"],
        result["median_rank8_energy"],
        result["median_response_preservation_rel_l2"],
        result["worst_rank8_over_gaussian"],
        float(result["rank8_improvement_count"]),
        result["cost"]["utilization"],
    ]
    for row in result["rows"]:
        for key in (
            "signal_ratio",
            "symmetry_error",
            "rank8_energy",
            "rank8_rel_frob_error",
            "gaussian_mse",
            "full_k22_mse",
            "rank8_k22_mse",
            "full_over_gaussian",
            "rank8_over_gaussian",
            "rank8_response_vs_full_rel_l2",
            "max_abs_full_correction",
            "max_abs_rank8_correction",
            "min_sigma",
            "target_mean_abs_max",
        ):
            vals.append(float(row[key]))
    return np.asarray(vals, dtype=np.float64)


def main() -> None:
    first = run_once()
    repeat = run_once()
    replay_max_abs = float(
        np.max(np.abs(scalar_signature(first) - scalar_signature(repeat)))
    )

    gates = {
        "all_finite": first["all_finite"],
        "all_eligible": first["all_eligible"],
        "median_rank8_energy_ge_0_80": first["median_rank8_energy"] >= 0.80,
        "median_response_error_le_0_20": first["median_response_preservation_rel_l2"] <= 0.20,
        "aggregate_rank8_ratio_le_0_95": first["aggregate_rank8_over_gaussian"] <= 0.95,
        "improves_at_least_4_of_6": first["rank8_improvement_count"] >= 4,
        "worst_rank8_ratio_le_1_25": first["worst_rank8_over_gaussian"] <= 1.25,
        "deterministic_replay_le_1e_12": replay_max_abs <= 1e-12,
        "production_cost_util_lt_0_01": first["cost"]["utilization"] < 0.01,
    }
    go = bool(all(gates.values()))
    result = {
        "schema": "arc.whitebox.e098.late_k22_edgeworth_stage_a.v1",
        "experiment": "E098",
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
        "n_samples": N_SAMPLES,
        "rank": RANK,
        "weight_seeds": WEIGHT_SEEDS,
        "input_seeds": INPUT_SEEDS,
        "source_layers": SOURCE_LAYERS,
        "first": first,
        "replay_max_abs": replay_max_abs,
        "gates": gates,
        "go": go,
        "scientific_go": False,
        "decision": "GO_NEW_PROPAGATION_ID" if go else "NO-GO/DROP",
    }
    Path("e098-stage-a.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("E098_STAGE_A_JSON=" + json.dumps(result, sort_keys=True), flush=True)
    if not go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
