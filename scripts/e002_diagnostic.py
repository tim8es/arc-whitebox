"""Preregistered E002 diagnostic fit on the first 20 Phase-2 mini MLPs."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
import whestbench

from methods.whitened_antithetic import WhitenedAntitheticEstimator

_FEATURE_NAMES = (
    "late_relu_uncertainty",
    "late_offdiag_ratio",
    "final_relu_uncertainty",
    "final_offdiag_ratio",
)
_COV_RESCALE_THRESHOLD = 1e30
_WEIGHT_LOWER = 0.55
_WEIGHT_UPPER = 0.90


def oracle_covariance_weight(
    target: np.ndarray,
    covariance: np.ndarray,
    sampling: np.ndarray,
) -> float:
    """Least-squares covariance weight for s + w * (c - s), clipped to [0, 1]."""
    delta = np.asarray(covariance, dtype=np.float64) - np.asarray(
        sampling, dtype=np.float64
    )
    residual = np.asarray(target, dtype=np.float64) - np.asarray(
        sampling, dtype=np.float64
    )
    denominator = float(np.dot(delta, delta))
    if denominator <= 0.0:
        return 0.75
    weight = float(np.dot(residual, delta) / denominator)
    return float(np.clip(weight, 0.0, 1.0))


@dataclass(frozen=True)
class RidgeRule:
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    coefficients: np.ndarray
    intercept: float
    ridge_lambda: float
    loo_mse: float

    def predict(self, features: np.ndarray) -> np.ndarray:
        x = np.asarray(features, dtype=np.float64)
        z = (x - self.feature_mean) / self.feature_scale
        raw = self.intercept + z @ self.coefficients
        return np.clip(raw, _WEIGHT_LOWER, _WEIGHT_UPPER)


def _fit_one_ridge(
    features: np.ndarray,
    targets: np.ndarray,
    ridge_lambda: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    x = np.asarray(features, dtype=np.float64)
    y = np.asarray(targets, dtype=np.float64)
    feature_mean = x.mean(axis=0)
    feature_scale = x.std(axis=0)
    feature_scale = np.where(feature_scale > 1e-12, feature_scale, 1.0)
    z = (x - feature_mean) / feature_scale
    intercept = float(y.mean())
    centered = y - intercept
    gram = z.T @ z
    rhs = z.T @ centered
    if ridge_lambda == 0.0:
        coefficients = np.linalg.lstsq(gram, rhs, rcond=None)[0]
    else:
        coefficients = np.linalg.solve(
            gram + ridge_lambda * np.eye(gram.shape[0], dtype=np.float64),
            rhs,
        )
    return feature_mean, feature_scale, coefficients, intercept


def _predict_one(
    row: np.ndarray,
    feature_mean: np.ndarray,
    feature_scale: np.ndarray,
    coefficients: np.ndarray,
    intercept: float,
) -> float:
    z = (np.asarray(row, dtype=np.float64) - feature_mean) / feature_scale
    return float(
        np.clip(intercept + float(z @ coefficients), _WEIGHT_LOWER, _WEIGHT_UPPER)
    )


def fit_ridge_rule(
    features: np.ndarray,
    targets: np.ndarray,
    *,
    lambdas: Iterable[float] = (0.0, 1.0, 10.0),
) -> RidgeRule:
    """Select preregistered ridge lambda by deterministic leave-one-out MSE."""
    x = np.asarray(features, dtype=np.float64)
    y = np.asarray(targets, dtype=np.float64)
    if x.ndim != 2 or y.ndim != 1 or x.shape[0] != y.shape[0]:
        raise ValueError("features must be (n, p) and targets must be (n,)")
    if x.shape[0] < 3:
        raise ValueError("at least three diagnostic rows are required")

    scored: list[tuple[float, float]] = []
    for ridge_lambda in lambdas:
        predictions = []
        for held_out in range(x.shape[0]):
            mask = np.arange(x.shape[0]) != held_out
            mean, scale, coefficients, intercept = _fit_one_ridge(
                x[mask], y[mask], float(ridge_lambda)
            )
            predictions.append(
                _predict_one(
                    x[held_out], mean, scale, coefficients, intercept
                )
            )
        loo_mse = float(np.mean((np.asarray(predictions) - y) ** 2))
        scored.append((loo_mse, float(ridge_lambda)))

    loo_mse, selected_lambda = min(scored, key=lambda item: (item[0], item[1]))
    mean, scale, coefficients, intercept = _fit_one_ridge(
        x, y, selected_lambda
    )
    return RidgeRule(
        feature_mean=mean,
        feature_scale=scale,
        coefficients=coefficients,
        intercept=intercept,
        ridge_lambda=selected_lambda,
        loo_mse=loo_mse,
    )


def _covariance_prediction_and_features(mlp: object) -> tuple[np.ndarray, np.ndarray]:
    width = int(mlp.width)
    mu = fnp.zeros(width, dtype=fnp.float32)
    cov = flops.as_symmetric(
        fnp.eye(width, dtype=fnp.float32), symmetry=(0, 1)
    )
    log_scale = 0.0
    uncertainties: list[float] = []
    offdiag_ratios: list[float] = []
    final_prediction: np.ndarray | None = None

    for weight in mlp.weights:
        cov_diag = fnp.diag(cov)
        max_var = float(fnp.max(cov_diag))
        if max_var > _COV_RESCALE_THRESHOLD:
            rescale = float(fnp.sqrt(max_var))
            mu = mu / rescale
            cov = cov / (rescale * rescale)
            log_scale += float(fnp.log(rescale))

        mu_pre = weight.T @ mu
        cov_pre = fnp.einsum("ij,ia,jb->ab", cov, weight, weight)
        var_pre = fnp.maximum(fnp.diag(cov_pre), 1e-12)
        sigma_pre = fnp.sqrt(var_pre)
        alpha = mu_pre / sigma_pre
        phi_alpha = flops.stats.norm.pdf(alpha).astype(fnp.float32)
        phi_cdf = flops.stats.norm.cdf(alpha).astype(fnp.float32)

        uncertainty = 4.0 * np.asarray(phi_cdf, dtype=np.float64) * (
            1.0 - np.asarray(phi_cdf, dtype=np.float64)
        )
        uncertainties.append(float(uncertainty.mean()))

        mu = mu_pre * phi_cdf + sigma_pre * phi_alpha
        ez2 = (
            (mu_pre * mu_pre + var_pre) * phi_cdf
            + mu_pre * sigma_pre * phi_alpha
        )
        var_post = fnp.maximum(ez2 - mu * mu, 0.0)
        zero32 = fnp.zeros((), dtype=fnp.float32)
        gain = fnp.where(sigma_pre > 1e-12, phi_cdf, zero32)
        cov = fnp.multiply(fnp.outer(gain, gain), cov_pre)
        fnp.fill_diagonal(cov, var_post)
        cov = flops.as_symmetric(cov, symmetry=(0, 1))

        cov_np = np.asarray(cov, dtype=np.float64)
        total_energy = float(np.sum(cov_np * cov_np))
        diagonal = np.diag(cov_np)
        diagonal_energy = float(np.dot(diagonal, diagonal))
        offdiag = max(0.0, total_energy - diagonal_energy)
        offdiag_ratios.append(offdiag / max(total_energy, 1e-30))

        scale_factor = float(fnp.exp(log_scale))
        final_prediction = np.asarray(mu * scale_factor, dtype=np.float64)

    if final_prediction is None:
        raise ValueError("MLP contains no layers")

    late_count = min(4, len(uncertainties))
    features = np.asarray(
        [
            np.mean(uncertainties[-late_count:]),
            np.mean(offdiag_ratios[-late_count:]),
            uncertainties[-1],
            offdiag_ratios[-1],
        ],
        dtype=np.float64,
    )
    return final_prediction, features


def _mse(prediction: np.ndarray, target: np.ndarray) -> float:
    delta = np.asarray(prediction, dtype=np.float64) - np.asarray(
        target, dtype=np.float64
    )
    return float(np.mean(delta * delta))


def run_diagnostic(n_rows: int = 20) -> dict[str, object]:
    if n_rows != 20:
        raise ValueError("E002 preregistration fixes the diagnostic subset at 20 rows")

    dataset = whestbench.load_dataset(
        "aicrowd/arc-whestbench-public-2026",
        revision="v2-phase2",
        split="mini",
    )
    sampler = WhitenedAntitheticEstimator(target_utilization=0.075)
    feature_rows: list[np.ndarray] = []
    oracle_weights: list[float] = []
    fixed_mses: list[float] = []
    oracle_mses: list[float] = []

    for index in range(n_rows):
        row = dataset[index]
        mlp = whestbench.mlp_at(dataset, index)
        target = np.asarray(row["final_means"], dtype=np.float64)
        covariance, features = _covariance_prediction_and_features(mlp)
        sampling = np.asarray(
            sampler.predict(mlp, 2**41)[-1], dtype=np.float64
        )
        oracle = oracle_covariance_weight(target, covariance, sampling)
        fixed_prediction = 0.75 * covariance + 0.25 * sampling
        oracle_prediction = oracle * covariance + (1.0 - oracle) * sampling

        feature_rows.append(features)
        oracle_weights.append(oracle)
        fixed_mses.append(_mse(fixed_prediction, target))
        oracle_mses.append(_mse(oracle_prediction, target))
        print(
            f"row={index:02d} oracle_w={oracle:.8f} "
            f"fixed_mse={fixed_mses[-1]:.8e} oracle_mse={oracle_mses[-1]:.8e}"
        )

    x = np.stack(feature_rows, axis=0)
    y = np.asarray(oracle_weights, dtype=np.float64)
    fitted = fit_ridge_rule(x, y)
    correlations: dict[str, float] = {}
    for column, name in enumerate(_FEATURE_NAMES):
        feature = x[:, column]
        if float(feature.std()) <= 1e-12 or float(y.std()) <= 1e-12:
            correlations[name] = 0.0
        else:
            correlations[name] = float(np.corrcoef(feature, y)[0, 1])

    result: dict[str, object] = {
        "n_rows": n_rows,
        "feature_names": list(_FEATURE_NAMES),
        "feature_mean": fitted.feature_mean.tolist(),
        "feature_scale": fitted.feature_scale.tolist(),
        "coefficients": fitted.coefficients.tolist(),
        "intercept": fitted.intercept,
        "ridge_lambda": fitted.ridge_lambda,
        "loo_weight_mse": fitted.loo_mse,
        "weight_clip": [_WEIGHT_LOWER, _WEIGHT_UPPER],
        "oracle_weight_mean": float(y.mean()),
        "oracle_weight_std": float(y.std()),
        "oracle_weight_min": float(y.min()),
        "oracle_weight_max": float(y.max()),
        "feature_oracle_correlations": correlations,
        "fixed_aggregate_mse": float(np.mean(fixed_mses)),
        "oracle_aggregate_mse": float(np.mean(oracle_mses)),
        "oracle_weights": y.tolist(),
        "features": x.tolist(),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("e002-diagnostic.json"))
    args = parser.parse_args()
    result = run_diagnostic()
    serialized = json.dumps(result, sort_keys=True, indent=2)
    args.output.write_text(serialized + "\n", encoding="utf-8")
    print("E002_DIAGNOSTIC_JSON=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
