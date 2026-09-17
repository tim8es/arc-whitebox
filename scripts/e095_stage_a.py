from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from methods.e095_output_subspace_sampling import (
    antithetic_final_mean,
    canonical_top_subspace,
    covariance_state,
    generate_synthetic_mlp,
    project_residual,
)

WIDTH = 32
DEPTH = 6
NETWORK_SEEDS = tuple(range(95000, 95008))
REFERENCE_SAMPLES = 65536
CANDIDATE_SAMPLES = 2048
RANK = 6

PROD_WIDTH = 1024
PROD_DEPTH = 16
PROD_SAMPLES = 4096
PROD_RANK = 6
BUDGET = 2**41


def _mse(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.mean(d * d, dtype=np.float64))


def _production_upper_bound() -> dict:
    w = PROD_WIDTH
    d = PROD_DEPTH
    n = PROD_SAMPLES
    k = PROD_RANK
    covariance = 5 * d * w**3
    eigenspace = 10 * w**3 + 4 * w**2
    sampling = 2 * n * d * w**2 + 2 * n * d * w
    reduction_projection = 4 * n * w + 6 * w * k + 10 * w
    total = int(covariance + eigenspace + sampling + reduction_projection)
    return {
        "covariance": int(covariance),
        "eigenspace": int(eigenspace),
        "sampling": int(sampling),
        "reduction_projection": int(reduction_projection),
        "total": total,
        "utilization": float(total / BUDGET),
    }


def run_once() -> dict:
    rows: list[dict] = []
    aggregate_base_sse = 0.0
    aggregate_full_sse = 0.0
    aggregate_projected_sse = 0.0
    projected_beats_base = 0
    projected_beats_full = 0
    capture_ge_half = 0
    finite_all = True
    deterministic_max_abs = 0.0

    for seed in NETWORK_SEEDS:
        weights = generate_synthetic_mlp(seed=seed, width=WIDTH, depth=DEPTH)
        means, cov = covariance_state(weights)
        base = means[-1]
        u = canonical_top_subspace(cov, rank=RANK)

        reference = antithetic_final_mean(
            weights,
            input_seed=2_000_000 + seed,
            samples=REFERENCE_SAMPLES,
        )
        full_sample = antithetic_final_mean(
            weights,
            input_seed=3_000_000 + seed,
            samples=CANDIDATE_SAMPLES,
        )
        projected = project_residual(base, full_sample, u)

        # Full deterministic replay of the target-free candidate path.
        means2, cov2 = covariance_state(weights)
        u2 = canonical_top_subspace(cov2, rank=RANK)
        full2 = antithetic_final_mean(
            weights,
            input_seed=3_000_000 + seed,
            samples=CANDIDATE_SAMPLES,
        )
        projected2 = project_residual(means2[-1], full2, u2)
        deterministic_max_abs = max(
            deterministic_max_abs,
            float(np.max(np.abs(u - u2))),
            float(np.max(np.abs(projected - projected2))),
        )

        base_err = base - reference
        full_err = full_sample - reference
        projected_err = projected - reference
        base_sse = float(np.sum(base_err * base_err, dtype=np.float64))
        full_sse = float(np.sum(full_err * full_err, dtype=np.float64))
        projected_sse = float(np.sum(projected_err * projected_err, dtype=np.float64))
        aggregate_base_sse += base_sse
        aggregate_full_sse += full_sse
        aggregate_projected_sse += projected_sse

        base_mse = base_sse / WIDTH
        full_mse = full_sse / WIDTH
        projected_mse = projected_sse / WIDTH
        ratio_base = projected_mse / max(base_mse, 1e-300)
        ratio_full = projected_mse / max(full_mse, 1e-300)

        delta = reference - base
        proj_delta = u @ (u.T @ delta)
        delta_energy = float(np.dot(delta, delta))
        capture = (
            float(np.dot(proj_delta, proj_delta)) / delta_energy
            if delta_energy > 0.0
            else 0.0
        )

        projected_beats_base += int(projected_mse < base_mse)
        projected_beats_full += int(projected_mse < full_mse)
        capture_ge_half += int(capture >= 0.50)

        finite = bool(
            np.isfinite(base).all()
            and np.isfinite(cov).all()
            and np.isfinite(u).all()
            and np.isfinite(reference).all()
            and np.isfinite(full_sample).all()
            and np.isfinite(projected).all()
        )
        finite_all = finite_all and finite

        rows.append(
            {
                "seed": seed,
                "baseline_mse": base_mse,
                "full_sample_mse": full_mse,
                "projected_mse": projected_mse,
                "projected_over_baseline": ratio_base,
                "projected_over_full_sample": ratio_full,
                "oracle_residual_energy_capture": capture,
                "finite": finite,
            }
        )

    aggregate_projected_over_base = aggregate_projected_sse / max(aggregate_base_sse, 1e-300)
    aggregate_projected_over_full = aggregate_projected_sse / max(aggregate_full_sse, 1e-300)
    captures = np.array([r["oracle_residual_energy_capture"] for r in rows], dtype=np.float64)
    ratios_base = np.array([r["projected_over_baseline"] for r in rows], dtype=np.float64)
    cost = _production_upper_bound()

    gates = {
        "finite_all": bool(finite_all),
        "deterministic_max_abs_eq_0": bool(deterministic_max_abs == 0.0),
        "aggregate_projected_over_baseline_le_0_80": bool(aggregate_projected_over_base <= 0.80),
        "aggregate_projected_over_full_sample_le_0_75": bool(aggregate_projected_over_full <= 0.75),
        "projected_beats_baseline_ge_6_of_8": bool(projected_beats_base >= 6),
        "projected_beats_full_sample_ge_6_of_8": bool(projected_beats_full >= 6),
        "worst_projected_over_baseline_le_1_50": bool(float(np.max(ratios_base)) <= 1.50),
        "mean_oracle_capture_ge_0_60": bool(float(np.mean(captures)) >= 0.60),
        "capture_ge_0_50_ge_6_of_8": bool(capture_ge_half >= 6),
        "production_utilization_upper_le_0_12": bool(cost["utilization"] <= 0.12),
    }
    go = bool(all(gates.values()))

    return {
        "schema": "arc.whitebox.e095.stage_a.v1",
        "experiment": "E095",
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
            "baseline_mse": aggregate_base_sse / (len(NETWORK_SEEDS) * WIDTH),
            "full_sample_mse": aggregate_full_sse / (len(NETWORK_SEEDS) * WIDTH),
            "projected_mse": aggregate_projected_sse / (len(NETWORK_SEEDS) * WIDTH),
            "projected_over_baseline": aggregate_projected_over_base,
            "projected_over_full_sample": aggregate_projected_over_full,
            "projected_beats_baseline": projected_beats_base,
            "projected_beats_full_sample": projected_beats_full,
            "worst_projected_over_baseline": float(np.max(ratios_base)),
            "mean_oracle_capture": float(np.mean(captures)),
            "capture_ge_0_50_count": capture_ge_half,
            "deterministic_max_abs": deterministic_max_abs,
        },
        "production_cost_upper": cost,
        "gates": gates,
        "go": go,
        "decision": "STAGE_A_GO" if go else "TERMINAL_NO_GO_DROP",
    }


def main() -> None:
    out = run_once()
    Path("e095-stage-a.json").write_text(
        json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
    )
    print("E095_STAGE_A_JSON=" + json.dumps(out, sort_keys=True), flush=True)
    Path("e095-stage-a-exit.txt").write_text("0\n" if out["go"] else "2\n", encoding="utf-8")
    if not out["go"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
