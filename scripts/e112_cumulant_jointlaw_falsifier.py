from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

LATENT_DIM = 2
WIDTH = 8
DEPTH = 4
WEIGHT_SEED = 111111
RAW_TARGET = 1.89e-8
E111_FINAL_BIAS = 1.6698051697168073e-3
BUDGET = 2**41
UTIL_CAP = 0.13
PRODUCTION_UPPER_FLOPS = 5_184_549_376
OUT = Path("e112-cumulant-jointlaw.json")

HERMITE = {
    0: {0: 1.0},
    3: {3: 1.0, 1: -3.0},
    4: {4: 1.0, 2: -6.0, 0: 3.0},
    6: {6: 1.0, 4: -15.0, 2: 45.0, 0: -15.0},
}


def make_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    weights: list[np.ndarray] = []
    w0 = rng.standard_normal((LATENT_DIM, WIDTH)).astype(np.float64)
    w0 *= math.sqrt(2.0 / LATENT_DIM)
    weights.append(w0)
    for _ in range(1, DEPTH):
        w = rng.standard_normal((WIDTH, WIDTH)).astype(np.float64)
        w *= math.sqrt(2.0 / WIDTH)
        weights.append(w)
    return weights


def _roots_in_interval(a: float, b: float, lo: float, hi: float) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    delta = math.atan2(b, a)
    base = delta + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    roots: list[float] = []
    for k in range(k0, k1 + 1):
        root = base + k * math.pi
        if lo + 1e-12 < root < hi - 1e-12:
            roots.append(root)
    return roots


def _dedup(values: list[float]) -> list[float]:
    out: list[float] = []
    for value in sorted(values):
        if not out or abs(value - out[-1]) > 1e-11:
            out.append(value)
    return out


def _cos_power_antiderivative(k: int, u: float) -> float:
    if k == 0:
        return u
    if k == 1:
        return math.sin(u)
    if k == 2:
        return 0.5 * u + 0.25 * math.sin(2.0 * u)
    if k == 3:
        return 0.25 * (3.0 * math.sin(u) + math.sin(3.0 * u) / 3.0)
    if k == 4:
        return (
            3.0 * u / 8.0
            + math.sin(2.0 * u) / 4.0
            + math.sin(4.0 * u) / 32.0
        )
    raise ValueError(k)


def _integrate_linear_power(
    coeff: np.ndarray, lo: float, hi: float, power: int
) -> np.ndarray:
    a = coeff[:, 0]
    b = coeff[:, 1]
    rho = np.hypot(a, b)
    delta = np.arctan2(b, a)
    out = np.zeros(coeff.shape[0], dtype=np.float64)
    for i in range(coeff.shape[0]):
        if rho[i] == 0.0:
            continue
        left = lo - float(delta[i])
        right = hi - float(delta[i])
        out[i] = (float(rho[i]) ** power) * (
            _cos_power_antiderivative(power, right)
            - _cos_power_antiderivative(power, left)
        )
    return out


def _basis_second_integral(lo: float, hi: float) -> np.ndarray:
    delta = hi - lo
    cc = 0.5 * delta + 0.25 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    ss = 0.5 * delta - 0.25 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    cs = 0.5 * (math.sin(hi) ** 2 - math.sin(lo) ** 2)
    return np.array([[cc, cs], [cs, ss]], dtype=np.float64)


def rayleigh_moment(power: int) -> float:
    return (2.0 ** (0.5 * power)) * math.gamma(1.0 + 0.5 * power)


def exact_angular_reference(weights: list[np.ndarray]) -> dict:
    intervals: list[tuple[float, float, np.ndarray]] = [
        (0.0, 2.0 * math.pi, np.eye(LATENT_DIM, dtype=np.float64))
    ]
    layers: list[dict] = []

    for layer_index, w in enumerate(weights):
        pre_ang = {p: np.zeros(WIDTH, dtype=np.float64) for p in range(1, 5)}
        post_ang = {p: np.zeros(WIDTH, dtype=np.float64) for p in range(1, 5)}
        post_cross_ang = np.zeros((WIDTH, WIDTH), dtype=np.float64)
        next_intervals: list[tuple[float, float, np.ndarray]] = []

        for lo, hi, h_coeff in intervals:
            pre_coeff = w.T @ h_coeff
            for power in range(1, 5):
                pre_ang[power] += _integrate_linear_power(
                    pre_coeff, lo, hi, power
                )

            boundaries = [lo, hi]
            for neuron in range(WIDTH):
                boundaries.extend(
                    _roots_in_interval(
                        float(pre_coeff[neuron, 0]),
                        float(pre_coeff[neuron, 1]),
                        lo,
                        hi,
                    )
                )
            boundaries = _dedup(boundaries)

            for left, right in zip(boundaries[:-1], boundaries[1:]):
                if right - left <= 1e-13:
                    continue
                mid = 0.5 * (left + right)
                direction = np.array(
                    [math.cos(mid), math.sin(mid)], dtype=np.float64
                )
                active = (pre_coeff @ direction) > 0.0
                out_coeff = pre_coeff.copy()
                out_coeff[~active, :] = 0.0

                for power in range(1, 5):
                    post_ang[power] += _integrate_linear_power(
                        out_coeff, left, right, power
                    )

                basis2 = _basis_second_integral(left, right)
                post_cross_ang += out_coeff @ basis2 @ out_coeff.T
                next_intervals.append((left, right, out_coeff))

        angular_scale = 1.0 / (2.0 * math.pi)
        pre_raw = {
            p: rayleigh_moment(p) * pre_ang[p] * angular_scale
            for p in range(1, 5)
        }
        post_raw = {
            p: rayleigh_moment(p) * post_ang[p] * angular_scale
            for p in range(1, 5)
        }

        post_cross2 = rayleigh_moment(2) * post_cross_ang * angular_scale
        post_mean = post_raw[1]
        post_cov = post_cross2 - np.outer(post_mean, post_mean)
        offdiag = post_cov.copy()
        np.fill_diagonal(offdiag, 0.0)

        layers.append(
            {
                "layer": layer_index + 1,
                "interval_count_in": len(intervals),
                "interval_count_out": len(next_intervals),
                "pre_raw": {str(p): pre_raw[p] for p in range(1, 5)},
                "post_raw": {str(p): post_raw[p] for p in range(1, 5)},
                "post_cov": post_cov,
                "offdiag_cov_rms": float(np.sqrt(np.mean(offdiag * offdiag))),
                "offdiag_cov_max_abs": float(np.max(np.abs(offdiag))),
            }
        )
        intervals = next_intervals

    return {
        "layers": layers,
        "final_interval_count": len(intervals),
    }


def raw_to_cumulants(raw: np.ndarray) -> np.ndarray:
    m1, m2, m3, m4 = [float(v) for v in raw]
    k1 = m1
    k2 = m2 - m1 * m1
    k3 = m3 - 3.0 * m2 * m1 + 2.0 * m1**3
    central4 = (
        m4 - 4.0 * m3 * m1 + 6.0 * m2 * m1 * m1 - 3.0 * m1**4
    )
    k4 = central4 - 3.0 * k2 * k2
    return np.array([k1, k2, k3, k4], dtype=np.float64)


def _tail_monomials(a: float, max_power: int) -> list[float]:
    phi = math.exp(-0.5 * a * a) / math.sqrt(2.0 * math.pi)
    q = 0.5 * math.erfc(a / math.sqrt(2.0))
    vals = [0.0] * (max_power + 1)
    vals[0] = q
    if max_power >= 1:
        vals[1] = phi
    for power in range(2, max_power + 1):
        vals[power] = (
            (a ** (power - 1)) * phi + (power - 1) * vals[power - 2]
        )
    return vals


def _integral_y_power_hermite(m: int, hermite_order: int, a: float) -> float:
    coeffs = HERMITE[hermite_order]
    tails = _tail_monomials(a, m + hermite_order)
    return sum(coeff * tails[m + power] for power, coeff in coeffs.items())


def edgeworth_relu_raw_moment(
    mu: float,
    variance: float,
    kappa3: float,
    kappa4: float,
    power: int,
) -> float:
    if variance < 0.0:
        return float("nan")
    if variance <= 1e-15:
        return max(mu, 0.0) ** power

    sigma = math.sqrt(variance)
    a = -mu / sigma
    gamma1 = kappa3 / (sigma**3)
    gamma2 = kappa4 / (sigma**4)

    correction_terms = (
        (0, 1.0),
        (3, gamma1 / 6.0),
        (4, gamma2 / 24.0),
        (6, gamma1 * gamma1 / 72.0),
    )

    total = 0.0
    for m in range(power + 1):
        binomial = math.comb(power, m) * (mu ** (power - m)) * (sigma**m)
        integral = 0.0
        for hermite_order, scale in correction_terms:
            if hermite_order == 0:
                integral += scale * _tail_monomials(a, m)[m]
            else:
                integral += scale * _integral_y_power_hermite(
                    m, hermite_order, a
                )
        total += binomial * integral
    return total


def cumulant_joint_closure(weights: list[np.ndarray]) -> dict:
    # Input law: two independent standard Gaussian sources.
    sources = np.zeros((LATENT_DIM, 4), dtype=np.float64)
    sources[:, 1] = 1.0

    layers: list[dict] = []

    for layer_index, w in enumerate(weights):
        pre = np.zeros((w.shape[1], 4), dtype=np.float64)

        # Exact cumulant convolution under the frozen factorized-source law.
        for neuron in range(w.shape[1]):
            col = w[:, neuron]
            pre[neuron, 0] = np.sum(col * sources[:, 0])
            pre[neuron, 1] = np.sum((col**2) * sources[:, 1])
            pre[neuron, 2] = np.sum((col**3) * sources[:, 2])
            pre[neuron, 3] = np.sum((col**4) * sources[:, 3])

        post_raw = np.zeros((w.shape[1], 4), dtype=np.float64)
        for neuron in range(w.shape[1]):
            for power in range(1, 5):
                post_raw[neuron, power - 1] = edgeworth_relu_raw_moment(
                    float(pre[neuron, 0]),
                    float(pre[neuron, 1]),
                    float(pre[neuron, 2]),
                    float(pre[neuron, 3]),
                    power,
                )

        post_cumulants = np.stack(
            [raw_to_cumulants(row) for row in post_raw], axis=0
        )

        layers.append(
            {
                "layer": layer_index + 1,
                "pre_cumulants": pre,
                "post_raw": post_raw,
                "post_cumulants": post_cumulants,
            }
        )
        sources = post_cumulants

    return {"layers": layers}


def _max_reference_delta(a: dict, b: dict) -> float:
    delta = 0.0
    for la, lb in zip(a["layers"], b["layers"]):
        for p in range(1, 5):
            xa = np.asarray(la["pre_raw"][str(p)], dtype=np.float64)
            xb = np.asarray(lb["pre_raw"][str(p)], dtype=np.float64)
            ya = np.asarray(la["post_raw"][str(p)], dtype=np.float64)
            yb = np.asarray(lb["post_raw"][str(p)], dtype=np.float64)
            delta = max(delta, float(np.max(np.abs(xa - xb))))
            delta = max(delta, float(np.max(np.abs(ya - yb))))
        delta = max(
            delta,
            float(
                np.max(
                    np.abs(
                        np.asarray(la["post_cov"], dtype=np.float64)
                        - np.asarray(lb["post_cov"], dtype=np.float64)
                    )
                )
            ),
        )
    return delta


def _max_closure_delta(a: dict, b: dict) -> float:
    delta = 0.0
    for la, lb in zip(a["layers"], b["layers"]):
        for key in ("pre_cumulants", "post_raw", "post_cumulants"):
            xa = np.asarray(la[key], dtype=np.float64)
            xb = np.asarray(lb[key], dtype=np.float64)
            delta = max(delta, float(np.nanmax(np.abs(xa - xb))))
    return delta


def main() -> None:
    weights = make_weights()

    exact_a = exact_angular_reference(weights)
    exact_b = exact_angular_reference(weights)
    exact_repeat_max_abs = _max_reference_delta(exact_a, exact_b)

    closure_a = cumulant_joint_closure(weights)
    closure_b = cumulant_joint_closure(weights)
    closure_repeat_max_abs = _max_closure_delta(closure_a, closure_b)

    layer_mean_bias_mse: list[float] = []
    layer_mean_bias_max_abs: list[float] = []
    negative_mean_counts: list[int] = []
    negative_variance_counts: list[int] = []
    predicted_variance_min: list[float] = []
    exact_offdiag_cov_rms: list[float] = []
    exact_offdiag_cov_max_abs: list[float] = []

    closure_finite = True

    for exact_layer, closure_layer in zip(
        exact_a["layers"], closure_a["layers"]
    ):
        exact_mean = np.asarray(exact_layer["post_raw"]["1"], dtype=np.float64)
        predicted_mean = np.asarray(
            closure_layer["post_raw"][:, 0], dtype=np.float64
        )
        predicted_var = np.asarray(
            closure_layer["post_cumulants"][:, 1], dtype=np.float64
        )

        bias = predicted_mean - exact_mean
        layer_mean_bias_mse.append(float(np.mean(bias * bias)))
        layer_mean_bias_max_abs.append(float(np.max(np.abs(bias))))
        negative_mean_counts.append(int(np.sum(predicted_mean < 0.0)))
        negative_variance_counts.append(int(np.sum(predicted_var < 0.0)))
        predicted_variance_min.append(float(np.min(predicted_var)))
        exact_offdiag_cov_rms.append(float(exact_layer["offdiag_cov_rms"]))
        exact_offdiag_cov_max_abs.append(
            float(exact_layer["offdiag_cov_max_abs"])
        )

        closure_finite = closure_finite and bool(
            np.isfinite(closure_layer["pre_cumulants"]).all()
            and np.isfinite(closure_layer["post_raw"]).all()
            and np.isfinite(closure_layer["post_cumulants"]).all()
        )

    final_bias = layer_mean_bias_mse[-1]
    first_layer_bias = layer_mean_bias_mse[0]

    gates = {
        "budget_upper_util_le_0_13": PRODUCTION_UPPER_FLOPS / BUDGET <= UTIL_CAP,
        "exact_reference_finite": all(
            np.isfinite(np.asarray(layer["post_cov"], dtype=np.float64)).all()
            and all(
                np.isfinite(
                    np.asarray(layer["post_raw"][str(p)], dtype=np.float64)
                ).all()
                for p in range(1, 5)
            )
            for layer in exact_a["layers"]
        ),
        "exact_reference_deterministic": exact_repeat_max_abs == 0.0,
        "closure_deterministic": closure_repeat_max_abs == 0.0,
        "closure_finite_all_layers": closure_finite,
        "first_layer_mean_mse_le_1e_24": first_layer_bias <= 1e-24,
        "all_predicted_relu_means_nonnegative": all(
            count == 0 for count in negative_mean_counts
        ),
        "all_predicted_relu_variances_nonnegative": all(
            count == 0 for count in negative_variance_counts
        ),
        "every_layer_mean_bias_mse_le_1_89e_8": all(
            mse <= RAW_TARGET for mse in layer_mean_bias_mse
        ),
        "final_layer_mean_bias_mse_le_1_89e_8": final_bias <= RAW_TARGET,
        "final_bias_improves_e111_gaussian_plugin": final_bias < E111_FINAL_BIAS,
        "no_targets_read": True,
    }

    scientific_go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e112.cumulant_jointlaw_exact_falsifier.v1",
        "experiment": "E112",
        "idempotency_key": "ARC-E112-CUMULANT-JOINTLAW-20260919",
        "mechanism": {
            "name": "factorized fourth-cumulant joint-CGF closure",
            "linear_step": "exact order-1..4 cumulant convolution under factorized non-Gaussian sources",
            "relu_step": "analytic second-order Edgeworth/Hermite positive-part moments through order four",
            "post_relu_closure": "refactorize coordinates into non-Gaussian marginals",
            "gaussian_plugin": False,
            "stein_or_jvp": False,
            "qmc_or_cubature": False,
            "latent_mixture": False,
        },
        "network": {
            "latent_gaussian_dimension": LATENT_DIM,
            "width": WIDTH,
            "depth": DEPTH,
            "weight_seed": WEIGHT_SEED,
            "biases": "all_zero",
            "weight_dtype": "float64",
        },
        "exact_reference": {
            "type": "recursive exact angular-sector integration with analytic Rayleigh moments p=1..4 and exact pair products",
            "monte_carlo": False,
            "numerical_quadrature": False,
            "final_interval_count": exact_a["final_interval_count"],
            "repeat_max_abs": exact_repeat_max_abs,
            "layer_offdiag_cov_rms": exact_offdiag_cov_rms,
            "layer_offdiag_cov_max_abs": exact_offdiag_cov_max_abs,
        },
        "closure": {
            "repeat_max_abs": closure_repeat_max_abs,
            "layer_mean_bias_mse": layer_mean_bias_mse,
            "layer_mean_bias_max_abs": layer_mean_bias_max_abs,
            "negative_relu_mean_counts": negative_mean_counts,
            "negative_relu_variance_counts": negative_variance_counts,
            "predicted_variance_min": predicted_variance_min,
            "final_bias_over_e111_gaussian_plugin": final_bias / E111_FINAL_BIAS,
            "final_bias_over_raw_target": final_bias / RAW_TARGET,
        },
        "budget_admission": {
            "budget_flops": BUDGET,
            "utilization_cap": UTIL_CAP,
            "dense_core_flops": 11 * DEPTH * (1024**2),
            "nonlinear_and_helper_reserve_flops": 5_000_000_000,
            "production_upper_flops": PRODUCTION_UPPER_FLOPS,
            "production_upper_utilization": PRODUCTION_UPPER_FLOPS / BUDGET,
            "gate": PRODUCTION_UPPER_FLOPS / BUDGET <= UTIL_CAP,
        },
        "gates": gates,
        "scientific_go": scientific_go,
        "decision": (
            "TARGET_FREE_NON_GAUSSIAN_LAW_GO"
            if scientific_go
            else "TERMINAL_NO_GO_DROP"
        ),
        "scope": {
            "target_free": True,
            "small_exact_falsifier_only": True,
            "production_scientific_run": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
            "tuning": False,
            "sweep": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        "E112_CUMULANT_JOINTLAW="
        + json.dumps(result, sort_keys=True, allow_nan=False),
        flush=True,
    )

    # A scientific NO-GO is a valid completed falsifier.
    integrity_ok = (
        gates["budget_upper_util_le_0_13"]
        and gates["exact_reference_finite"]
        and gates["exact_reference_deterministic"]
        and gates["closure_deterministic"]
        and gates["no_targets_read"]
    )
    if not integrity_ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
