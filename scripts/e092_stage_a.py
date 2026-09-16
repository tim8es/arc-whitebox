from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from methods.e092_frozen_residual_calibrator import (
    antithetic_reference,
    apply_frozen_ridge,
    covariance_baseline_numpy,
    final_layer_features,
    fit_frozen_ridge,
    generate_synthetic_mlp,
)

WIDTH = 8
DEPTH = 4
SAMPLES = 32768
LAMBDA = 1e-2
TRAIN_SEEDS = tuple(range(92000, 92016))
HOLDOUT_SEEDS = tuple(range(92100, 92108))
BUDGET = 2**41
PHASE2_WIDTH = 1024


def corpus_row(seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    weights = generate_synthetic_mlp(seed=seed, width=WIDTH, depth=DEPTH)
    baseline = covariance_baseline_numpy(weights)
    reference = antithetic_reference(
        weights,
        input_seed=1_000_000 + seed,
        samples=SAMPLES,
    )
    features = final_layer_features(baseline, weights[-1])
    base_final = baseline[-1]
    reference_final = reference[-1]
    rms = math.sqrt(float(np.mean(base_final * base_final)) + 1e-12)
    return features, base_final, reference_final, rms


def build_training() -> tuple[np.ndarray, np.ndarray]:
    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    for seed in TRAIN_SEEDS:
        features, base_final, reference_final, rms = corpus_row(seed)
        xs.append(features)
        ys.append((reference_final - base_final) / rms)
    return np.concatenate(xs, axis=0), np.concatenate(ys, axis=0)


def evaluate_model(model) -> tuple[list[dict[str, float | int]], float, float, int, float]:
    rows: list[dict[str, float | int]] = []
    baseline_sq: list[np.ndarray] = []
    adjusted_sq: list[np.ndarray] = []
    wins = 0
    max_degradation = 0.0

    for seed in HOLDOUT_SEEDS:
        features, base_final, reference_final, rms = corpus_row(seed)
        normalized_correction = apply_frozen_ridge(
            features,
            np.zeros_like(base_final),
            model,
        )
        adjusted = base_final + rms * normalized_correction
        base_err = (base_final - reference_final) ** 2
        adjusted_err = (adjusted - reference_final) ** 2
        base_mse = float(np.mean(base_err))
        adjusted_mse = float(np.mean(adjusted_err))
        ratio = adjusted_mse / base_mse if base_mse > 0.0 else float("inf")
        wins += int(adjusted_mse < base_mse)
        max_degradation = max(max_degradation, ratio)
        baseline_sq.append(base_err)
        adjusted_sq.append(adjusted_err)
        rows.append(
            {
                "seed": seed,
                "baseline_mse": base_mse,
                "adjusted_mse": adjusted_mse,
                "ratio": ratio,
            }
        )

    baseline_mse = float(np.mean(np.concatenate(baseline_sq)))
    adjusted_mse = float(np.mean(np.concatenate(adjusted_sq)))
    return rows, baseline_mse, adjusted_mse, wins, max_degradation


def main() -> int:
    x, y = build_training()
    model = fit_frozen_ridge(x, y, lambda_=LAMBDA)
    model_repeat = fit_frozen_ridge(x.copy(), y.copy(), lambda_=LAMBDA)
    deterministic_diff = float(
        max(
            np.max(np.abs(model.coefficients - model_repeat.coefficients)),
            np.max(np.abs(model.feature_mean - model_repeat.feature_mean)),
            np.max(np.abs(model.feature_scale - model_repeat.feature_scale)),
        )
    )

    heldout, baseline_mse, adjusted_mse, wins, max_degradation = evaluate_model(model)
    ratio = adjusted_mse / baseline_mse if baseline_mse > 0.0 else float("inf")
    coef_norm = float(np.linalg.norm(model.coefficients))
    deploy_flops_upper = int(17 * PHASE2_WIDTH**2 + 64 * PHASE2_WIDTH + 64)
    deploy_fraction = float(deploy_flops_upper / BUDGET)

    finite = bool(
        np.all(np.isfinite(model.coefficients))
        and np.all(np.isfinite(model.feature_mean))
        and np.all(np.isfinite(model.feature_scale))
        and np.isfinite(baseline_mse)
        and np.isfinite(adjusted_mse)
    )

    gates = {
        "finite": finite,
        "deterministic": deterministic_diff == 0.0,
        "aggregate_ratio_le_0_95": ratio <= 0.95,
        "wins_ge_6_of_8": wins >= 6,
        "max_degradation_le_1_25": max_degradation <= 1.25,
        "coefficient_norm_le_5": coef_norm <= 5.0,
        "deploy_fraction_lt_1e_5": deploy_fraction < 1e-5,
    }
    go = all(gates.values())

    receipt = {
        "schema": "arc.e092.stage_a.v1",
        "experiment": "E092",
        "protocol_commit": "ff0d2602db84f0efc9cb4684fed5c54f170b6d98",
        "implementation_commit_expected_parent": "b69fca5a182155aa27c6625cca719b5826ea663d",
        "corpus": {
            "width": WIDTH,
            "depth": DEPTH,
            "samples_per_mlp": SAMPLES,
            "train_seeds": list(TRAIN_SEEDS),
            "holdout_seeds": list(HOLDOUT_SEEDS),
            "reference_input_seed_rule": "1000000 + mlp_seed",
        },
        "model": {
            "feature_dim": 8,
            "lambda": LAMBDA,
            "coefficients": model.coefficients.tolist(),
            "feature_mean": model.feature_mean.tolist(),
            "feature_scale": model.feature_scale.tolist(),
            "coefficient_l2": coef_norm,
        },
        "metrics": {
            "baseline_mse": baseline_mse,
            "adjusted_mse": adjusted_mse,
            "adjusted_over_baseline": ratio,
            "heldout_wins": wins,
            "heldout_count": len(HOLDOUT_SEEDS),
            "max_network_degradation_ratio": max_degradation,
            "deterministic_max_abs_diff": deterministic_diff,
            "deploy_flops_upper": deploy_flops_upper,
            "phase2_budget": BUDGET,
            "deploy_budget_fraction": deploy_fraction,
        },
        "heldout": heldout,
        "gates": gates,
        "decision": "GO" if go else "NO-GO / DROP",
        "public_access": False,
        "holdout_full_access": False,
        "official_scorer": False,
    }

    path = Path("artifacts/e092_stage_a_receipt.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if go else 1


if __name__ == "__main__":
    raise SystemExit(main())
