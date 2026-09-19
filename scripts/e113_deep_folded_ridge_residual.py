from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

WIDTH = 8
DEPTH = 4
WEIGHT_SEED = 113104
HAAR_ROOT_SEED = 113105
REALIZATIONS = 1024

TARGET_MSE_SCALE = 1.89e-8
PRODUCTION_BUDGET = 2**41
PRODUCTION_BASE_FLOPS = 149_047_442_096
PRODUCTION_OVERHEAD_UPPER = 200_000_000
PRODUCTION_UTIL_CAP = 0.13

OUT = Path("e113-smallwidth-falsifier.json")


def make_weights(width: int, depth: int, seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    scale = math.sqrt(2.0 / width)
    return [
        rng.standard_normal((width, width)).astype(np.float64) * scale
        for _ in range(depth)
    ]


def forward(weights: list[np.ndarray], x: np.ndarray) -> np.ndarray:
    h = np.asarray(x, dtype=np.float64)
    for w in weights:
        h = h @ w
        h = np.maximum(h, 0.0)
    return h


def forward_with_masks(
    weights: list[np.ndarray], x: np.ndarray
) -> tuple[np.ndarray, list[np.ndarray], list[np.ndarray]]:
    h = np.asarray(x, dtype=np.float64)
    pres: list[np.ndarray] = []
    masks: list[np.ndarray] = []
    for w in weights:
        z = h @ w
        mask = z > 0.0
        pres.append(z)
        masks.append(mask)
        h = np.maximum(z, 0.0)
    return h, pres, masks


def deep_probe_direction(
    weights: list[np.ndarray],
) -> tuple[np.ndarray, dict[str, float]]:
    width = weights[0].shape[0]
    probe = np.ones(width, dtype=np.float64) / math.sqrt(width)
    _, pres, masks = forward_with_masks(weights, probe)

    g = np.ones(width, dtype=np.float64) / math.sqrt(width)
    for w, mask in zip(reversed(weights), reversed(masks)):
        g = (g * mask.astype(np.float64)) @ w.T

    norm = float(np.linalg.norm(g))
    if not math.isfinite(norm) or norm <= 1e-12:
        raise RuntimeError(f"invalid deep probe gradient norm: {norm}")
    v = g / norm

    min_abs_probe_preact = min(
        float(np.min(np.abs(z))) for z in pres
    )
    return v, {
        "gradient_norm": norm,
        "unit_norm_error": abs(float(np.linalg.norm(v)) - 1.0),
        "probe_min_abs_preactivation": min_abs_probe_preact,
    }


def chi_mean(n: int) -> float:
    return math.exp(
        0.5 * math.log(2.0)
        + math.lgamma((n + 1.0) / 2.0)
        - math.lgamma(n / 2.0)
    )


def sphere_abs_projection_mean(n: int) -> float:
    return math.exp(
        math.lgamma(n / 2.0)
        - 0.5 * math.log(math.pi)
        - math.lgamma((n + 1.0) / 2.0)
    )


def canonical_haar(
    rng: np.random.Generator, n: int
) -> tuple[np.ndarray, float]:
    a = rng.standard_normal((n, n)).astype(np.float64)
    q, r = np.linalg.qr(a)
    diag = np.diag(r)
    signs = np.where(diag < 0.0, -1.0, 1.0)
    q = q * signs[None, :]
    ortho_err = float(np.max(np.abs(q @ q.T - np.eye(n))))
    return q, ortho_err


def deterministic_ray_coefficient(
    weights: list[np.ndarray], v: np.ndarray
) -> np.ndarray:
    return 0.5 * (forward(weights, v) + forward(weights, -v))


def block_contributions(
    weights: list[np.ndarray],
    q: np.ndarray,
    v: np.ndarray,
    ray_coeff: np.ndarray,
    mu_r: float,
    m_sphere: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pair_mean = 0.5 * (forward(weights, q) + forward(weights, -q))
    baseline_rows = mu_r * pair_mean
    centered = np.abs(q @ v) - m_sphere
    candidate_rows = baseline_rows - (
        mu_r * centered[:, None] * ray_coeff[None, :]
    )
    return baseline_rows, candidate_rows, centered


def estimator_realizations(
    weights: list[np.ndarray],
    v: np.ndarray,
    ray_coeff: np.ndarray,
    root_seed: int,
    realizations: int,
) -> dict[str, object]:
    n = v.shape[0]
    mu_r = chi_mean(n)
    m_sphere = sphere_abs_projection_mean(n)
    rng = np.random.Generator(np.random.PCG64(root_seed))

    baseline = np.empty((realizations, n), dtype=np.float64)
    candidate = np.empty((realizations, n), dtype=np.float64)
    control_means = np.empty(realizations, dtype=np.float64)

    max_ortho = 0.0
    max_abs_control = 0.0
    control_sum = 0.0
    control_sq_sum = 0.0
    control_count = 0

    for ridx in range(realizations):
        base_rows_all: list[np.ndarray] = []
        cand_rows_all: list[np.ndarray] = []
        centered_all: list[np.ndarray] = []

        for _ in range(2):
            q, ortho = canonical_haar(rng, n)
            max_ortho = max(max_ortho, ortho)
            b_rows, c_rows, centered = block_contributions(
                weights, q, v, ray_coeff, mu_r, m_sphere
            )
            base_rows_all.append(b_rows)
            cand_rows_all.append(c_rows)
            centered_all.append(centered)

        bcat = np.concatenate(base_rows_all, axis=0)
        ccat = np.concatenate(cand_rows_all, axis=0)
        zcat = np.concatenate(centered_all, axis=0)

        baseline[ridx] = np.mean(bcat, axis=0)
        candidate[ridx] = np.mean(ccat, axis=0)
        control_means[ridx] = float(np.mean(zcat))

        max_abs_control = max(max_abs_control, float(np.max(np.abs(zcat))))
        control_sum += float(np.sum(zcat))
        control_sq_sum += float(np.sum(zcat * zcat))
        control_count += int(zcat.size)

    empirical_control_mean = control_sum / control_count
    empirical_control_second = control_sq_sum / control_count

    return {
        "baseline": baseline,
        "candidate": candidate,
        "control_means": control_means,
        "max_haar_orthogonality_error": max_ortho,
        "max_abs_centered_control": max_abs_control,
        "empirical_control_mean": empirical_control_mean,
        "empirical_control_second_moment": empirical_control_second,
    }


def pooled_risk(values: np.ndarray) -> float:
    return float(np.mean(np.var(values, axis=0, ddof=1)))


def digest_array(x: np.ndarray) -> str:
    import hashlib

    return hashlib.sha256(
        np.ascontiguousarray(x, dtype=np.float64).tobytes()
    ).hexdigest()


def run_once() -> dict[str, object]:
    weights = make_weights(WIDTH, DEPTH, WEIGHT_SEED)
    v, direction_diag = deep_probe_direction(weights)
    ray_coeff = deterministic_ray_coefficient(weights, v)

    mu_r = chi_mean(WIDTH)
    m_sphere = sphere_abs_projection_mean(WIDTH)
    analytic_control_second = 1.0 / WIDTH - m_sphere * m_sphere

    sims = estimator_realizations(
        weights,
        v,
        ray_coeff,
        HAAR_ROOT_SEED,
        REALIZATIONS,
    )
    baseline = np.asarray(sims["baseline"], dtype=np.float64)
    candidate = np.asarray(sims["candidate"], dtype=np.float64)

    base_risk = pooled_risk(baseline)
    cand_risk = pooled_risk(candidate)
    ratio = cand_risk / base_risk if base_risk > 0.0 else math.inf

    mean_shift_vector = np.mean(candidate - baseline, axis=0)
    mean_shift_rms = float(
        math.sqrt(np.mean(mean_shift_vector * mean_shift_vector))
    )
    mean_shift_threshold = 4.0 * math.sqrt(base_risk / REALIZATIONS)

    coeff_l2 = float(np.linalg.norm(ray_coeff))
    coeff_rms = float(math.sqrt(np.mean(ray_coeff * ray_coeff)))
    coeff_max_abs = float(np.max(np.abs(ray_coeff)))
    deterministic_correction_l2_bound = mu_r * coeff_l2

    finite = bool(
        np.isfinite(baseline).all()
        and np.isfinite(candidate).all()
        and np.isfinite(ray_coeff).all()
        and math.isfinite(base_risk)
        and math.isfinite(cand_risk)
        and math.isfinite(analytic_control_second)
    )

    gates = {
        "deep_direction_norm_gt_1e_12": direction_diag["gradient_norm"] > 1e-12,
        "direction_unit_error_le_1e_12": direction_diag["unit_norm_error"] <= 1e-12,
        "all_finite": finite,
        "haar_orthogonality_le_1e_12": sims["max_haar_orthogonality_error"] <= 1e-12,
        "analytic_control_second_moment_positive": analytic_control_second > 0.0,
        "candidate_risk_lt_baseline": cand_risk < base_risk,
        "risk_ratio_le_0_80": ratio <= 0.80,
        "mean_shift_within_4se": mean_shift_rms <= mean_shift_threshold,
    }

    return {
        "baseline": baseline,
        "candidate": candidate,
        "payload": {
            "frozen_instance": {
                "width": WIDTH,
                "depth": DEPTH,
                "weight_seed": WEIGHT_SEED,
                "haar_root_seed": HAAR_ROOT_SEED,
                "realizations": REALIZATIONS,
                "haar_bases_per_realization": 2,
                "directions_per_realization": 2 * WIDTH,
            },
            "direction": {
                **direction_diag,
                "sha256": digest_array(v),
            },
            "coefficient": {
                "construction": "0.5*(F(v)+F(-v)); no fit and no covariance/variance division",
                "l2": coeff_l2,
                "rms": coeff_rms,
                "max_abs": coeff_max_abs,
                "sha256": digest_array(ray_coeff),
            },
            "exact_control_law": {
                "chi_mean": mu_r,
                "sphere_abs_projection_mean": m_sphere,
                "analytic_centered_second_moment": analytic_control_second,
                "max_abs_centered_control_observed": sims[
                    "max_abs_centered_control"
                ],
                "deterministic_per_direction_correction_l2_bound": deterministic_correction_l2_bound,
                "empirical_control_mean": sims["empirical_control_mean"],
                "empirical_control_second_moment": sims[
                    "empirical_control_second_moment"
                ],
            },
            "risk": {
                "baseline_target_free_pooled_variance": base_risk,
                "candidate_target_free_pooled_variance": cand_risk,
                "candidate_over_baseline": ratio,
                "relative_variance_reduction": 1.0 - ratio,
                "baseline_over_raw_target_scale": base_risk / TARGET_MSE_SCALE,
                "candidate_over_raw_target_scale": cand_risk / TARGET_MSE_SCALE,
                "raw_target_scale_diagnostic": TARGET_MSE_SCALE,
            },
            "unbiasedness_diagnostic": {
                "candidate_minus_baseline_mean_shift_rms": mean_shift_rms,
                "frozen_4se_threshold": mean_shift_threshold,
            },
            "integrity": {
                "max_haar_orthogonality_error": sims[
                    "max_haar_orthogonality_error"
                ],
                "finite": finite,
            },
            "gates": gates,
            "prediction_sha256": {
                "baseline": digest_array(baseline),
                "candidate": digest_array(candidate),
            },
        },
    }


def main() -> None:
    first = run_once()
    second = run_once()

    deterministic = bool(
        np.array_equal(first["baseline"], second["baseline"])
        and np.array_equal(first["candidate"], second["candidate"])
        and first["payload"] == second["payload"]
    )

    payload = first["payload"]
    payload["gates"]["deterministic_exact_replay"] = deterministic
    all_gates = bool(all(payload["gates"].values()))

    production_upper = PRODUCTION_BASE_FLOPS + PRODUCTION_OVERHEAD_UPPER
    production_upper_util = production_upper / PRODUCTION_BUDGET

    out = {
        "schema": "arc.whitebox.e113.smallwidth_falsifier.v1",
        "experiment": "E113",
        "idempotency_key": "ARC-E113-DEEP-FOLDED-RIDGE-RESIDUAL-20260919",
        "mechanism": "deterministic deep folded-ridge residual control",
        "status": (
            "SMALL_WIDTH_DETERMINISTIC_DEEP_RESIDUAL_GO"
            if all_gates
            else "TERMINAL_NO_GO_DROP"
        ),
        **payload,
        "production_admission": {
            "reference_base_flops": PRODUCTION_BASE_FLOPS,
            "overhead_upper_flops": PRODUCTION_OVERHEAD_UPPER,
            "all_in_upper_flops": production_upper,
            "budget": PRODUCTION_BUDGET,
            "utilization_upper": production_upper_util,
            "utilization_cap": PRODUCTION_UTIL_CAP,
            "pass": production_upper_util <= PRODUCTION_UTIL_CAP,
            "production_execution_authorized": False,
        },
        "scientific_go": False,
        "scope": {
            "small_width_synthetic_only": True,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
            "target_fitting": False,
            "gaussian_relu_plugin": False,
            "covariance_division": False,
            "variance_division": False,
            "ridge_solve": False,
            "tuning": False,
            "sweep": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
        "decision": (
            "SMALL_WIDTH_DETERMINISTIC_DEEP_RESIDUAL_GO"
            if all_gates
            else "TERMINAL_NO_GO_DROP"
        ),
    }

    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E113_SMALLWIDTH_FALSIFIER=" + json.dumps(out, sort_keys=True), flush=True)

    if not all_gates:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
