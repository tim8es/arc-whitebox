from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from methods.e100_crossfit_shrinkage import (
    antithetic_final_samples,
    canonical_top_subspace,
    covariance_state,
    crossfit_estimate,
    generate_synthetic_mlp,
)

WIDTH = 32
DEPTH = 6
NETWORK_SEEDS = tuple(range(100000, 100008))
REFERENCE_SAMPLES = 65536
CANDIDATE_SAMPLES = 2048
RANK = 6

PROD_WIDTH = 1024
PROD_DEPTH = 16
PROD_SAMPLES = 4096
PROD_RANK = 6
BUDGET = 2**41


def _production_upper() -> dict:
    w = PROD_WIDTH
    d = PROD_DEPTH
    n = PROD_SAMPLES
    k = PROD_RANK
    covariance = 5 * d * w**3
    eigenspace = 10 * w**3 + 4 * w**2
    sampling = 2 * n * d * w**2 + 2 * n * d * w
    statistics = 8 * n * w * k + 12 * n * w + 20 * w * k + 20 * w
    total = int(covariance + eigenspace + sampling + statistics)
    return {
        "covariance": int(covariance),
        "eigenspace": int(eigenspace),
        "sampling": int(sampling),
        "statistics_crossfit": int(statistics),
        "total": total,
        "utilization": float(total / BUDGET),
    }


def run_once() -> dict:
    rows: list[dict] = []
    base_sse_total = 0.0
    full_sse_total = 0.0
    e100_sse_total = 0.0
    beats_full = 0
    active_networks = 0
    finite_all = True
    coeffs_bounded = True
    deterministic_max_abs = 0.0

    for seed in NETWORK_SEEDS:
        weights = generate_synthetic_mlp(seed=seed, width=WIDTH, depth=DEPTH)
        means, cov = covariance_state(weights)
        base = means[-1]
        u = canonical_top_subspace(cov, rank=RANK)

        ref_samples = antithetic_final_samples(
            weights,
            input_seed=2_100_000 + seed,
            samples=REFERENCE_SAMPLES,
        )
        reference = np.mean(ref_samples, axis=0, dtype=np.float64)

        samples = antithetic_final_samples(
            weights,
            input_seed=3_100_000 + seed,
            samples=CANDIDATE_SAMPLES,
        )
        full = np.mean(samples, axis=0, dtype=np.float64)
        candidate, sa, sb = crossfit_estimate(base, samples, u)

        # Complete target-free replay for deterministic gate.
        means2, cov2 = covariance_state(weights)
        u2 = canonical_top_subspace(cov2, rank=RANK)
        samples2 = antithetic_final_samples(
            weights,
            input_seed=3_100_000 + seed,
            samples=CANDIDATE_SAMPLES,
        )
        candidate2, sa2, sb2 = crossfit_estimate(means2[-1], samples2, u2)
        deterministic_max_abs = max(
            deterministic_max_abs,
            float(np.max(np.abs(u - u2))),
            float(np.max(np.abs(candidate - candidate2))),
            abs(float(sa["a_p"]) - float(sa2["a_p"])),
            abs(float(sa["a_q"]) - float(sa2["a_q"])),
            abs(float(sb["a_p"]) - float(sb2["a_p"])),
            abs(float(sb["a_q"]) - float(sb2["a_q"])),
        )

        base_err = base - reference
        full_err = full - reference
        cand_err = candidate - reference
        base_sse = float(np.sum(base_err * base_err, dtype=np.float64))
        full_sse = float(np.sum(full_err * full_err, dtype=np.float64))
        cand_sse = float(np.sum(cand_err * cand_err, dtype=np.float64))
        base_sse_total += base_sse
        full_sse_total += full_sse
        e100_sse_total += cand_sse

        base_mse = base_sse / WIDTH
        full_mse = full_sse / WIDTH
        cand_mse = cand_sse / WIDTH
        ratio_base = cand_mse / max(base_mse, 1e-300)
        ratio_full = cand_mse / max(full_mse, 1e-300)
        beats_full += int(cand_mse < full_mse)

        coeff_values = [
            float(sa["a_p"]),
            float(sa["a_q"]),
            float(sb["a_p"]),
            float(sb["a_q"]),
        ]
        active = any(v < 0.99 for v in coeff_values)
        active_networks += int(active)
        bounded = all(0.0 <= v <= 1.0 for v in coeff_values)
        coeffs_bounded = coeffs_bounded and bounded
        finite = bool(
            np.isfinite(base).all()
            and np.isfinite(cov).all()
            and np.isfinite(u).all()
            and np.isfinite(reference).all()
            and np.isfinite(full).all()
            and np.isfinite(candidate).all()
            and all(np.isfinite(v) for v in coeff_values)
        )
        finite_all = finite_all and finite

        rows.append(
            {
                "seed": seed,
                "baseline_mse": base_mse,
                "full_sample_mse": full_mse,
                "e100_mse": cand_mse,
                "e100_over_baseline": ratio_base,
                "e100_over_full_sample": ratio_full,
                "coefficients": {
                    "a_p_A": coeff_values[0],
                    "a_q_A": coeff_values[1],
                    "a_p_B": coeff_values[2],
                    "a_q_B": coeff_values[3],
                },
                "noise_energy": {
                    "tau_p_A": float(sa["tau_p"]),
                    "tau_q_A": float(sa["tau_q"]),
                    "tau_p_B": float(sb["tau_p"]),
                    "tau_q_B": float(sb["tau_q"]),
                },
                "active": active,
                "finite": finite,
            }
        )

    ncoords = len(NETWORK_SEEDS) * WIDTH
    base_mse_agg = base_sse_total / ncoords
    full_mse_agg = full_sse_total / ncoords
    e100_mse_agg = e100_sse_total / ncoords
    ratio_base_agg = e100_sse_total / max(base_sse_total, 1e-300)
    ratio_full_agg = e100_sse_total / max(full_sse_total, 1e-300)
    worst_full = max(r["e100_over_full_sample"] for r in rows)
    cost = _production_upper()

    gates = {
        "finite_all": bool(finite_all),
        "deterministic_max_abs_eq_0": bool(deterministic_max_abs == 0.0),
        "aggregate_e100_over_baseline_le_0_20": bool(ratio_base_agg <= 0.20),
        "aggregate_e100_over_full_le_0_95": bool(ratio_full_agg <= 0.95),
        "beats_full_ge_6_of_8": bool(beats_full >= 6),
        "worst_e100_over_full_le_1_25": bool(worst_full <= 1.25),
        "coefficients_bounded_0_1": bool(coeffs_bounded),
        "active_networks_ge_4_of_8": bool(active_networks >= 4),
        "production_utilization_upper_le_0_12": bool(cost["utilization"] <= 0.12),
    }
    go = bool(all(gates.values()))

    return {
        "schema": "arc.whitebox.e100.stage_a.v1",
        "experiment": "E100",
        "stage": "A",
        "scope": {
            "synthetic_only": True,
            "public": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
        },
        "freeze": {
            "width": WIDTH,
            "depth": DEPTH,
            "network_seeds": NETWORK_SEEDS,
            "reference_samples": REFERENCE_SAMPLES,
            "candidate_samples": CANDIDATE_SAMPLES,
            "rank": RANK,
        },
        "rows": rows,
        "aggregate": {
            "baseline_mse": base_mse_agg,
            "full_sample_mse": full_mse_agg,
            "e100_mse": e100_mse_agg,
            "e100_over_baseline": ratio_base_agg,
            "e100_over_full_sample": ratio_full_agg,
            "beats_full_sample": beats_full,
            "worst_e100_over_full_sample": worst_full,
            "active_networks": active_networks,
            "deterministic_max_abs": deterministic_max_abs,
        },
        "production_cost_upper": cost,
        "gates": gates,
        "go": go,
        "decision": "STAGE_A_GO" if go else "TERMINAL_NO_GO_DROP",
    }


def main() -> None:
    out = run_once()
    Path("e100-stage-a.json").write_text(
        json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
    )
    Path("e100-stage-a-exit.txt").write_text(
        "0\n" if out["go"] else "2\n", encoding="utf-8"
    )
    print("E100_STAGE_A_JSON=" + json.dumps(out, sort_keys=True), flush=True)
    if not out["go"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
