from __future__ import annotations

import json
import math
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

LATENT_DIM = 2
WIDTH = 8
DEPTH = 4
WEIGHT_SEED = 111111
RAW_TARGET = 1.89e-8
VAR_EPS = 1e-15

PRODUCTION_ALL_IN_FLOPS = 149_220_512_434
PRODUCTION_ALL_IN_UTIL = 0.06785763272728218
PRODUCTION_UTIL_LIMIT = 0.13
BUDGET = 2**41

OUT = Path("e111-bias-falsifier.json")


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
    roots = []
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


def _integrate_linear_and_square(
    coeff: np.ndarray, lo: float, hi: float
) -> tuple[np.ndarray, np.ndarray]:
    a = coeff[:, 0]
    b = coeff[:, 1]
    delta = hi - lo

    int_cos = math.sin(hi) - math.sin(lo)
    int_sin = -math.cos(hi) + math.cos(lo)

    int_cos2 = 0.5 * delta + 0.25 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    int_sin2 = 0.5 * delta - 0.25 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    int_sincos = 0.5 * (math.sin(hi) ** 2 - math.sin(lo) ** 2)

    first = a * int_cos + b * int_sin
    second = (
        a * a * int_cos2
        + b * b * int_sin2
        + 2.0 * a * b * int_sincos
    )
    return first, second


def _normal_pdf(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _normal_cdf(x: np.ndarray) -> np.ndarray:
    flat = x.reshape(-1)
    vals = [0.5 * (1.0 + math.erf(float(v) / math.sqrt(2.0))) for v in flat]
    return np.asarray(vals, dtype=np.float64).reshape(x.shape)


def gaussian_relu_plugin(
    pre_mean: np.ndarray, pre_var: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    mean = np.empty_like(pre_mean, dtype=np.float64)
    var = np.empty_like(pre_var, dtype=np.float64)

    degenerate = pre_var <= VAR_EPS
    regular = ~degenerate

    mean[degenerate] = np.maximum(pre_mean[degenerate], 0.0)
    var[degenerate] = 0.0

    if np.any(regular):
        mu = pre_mean[regular]
        sigma2 = pre_var[regular]
        sigma = np.sqrt(sigma2)
        alpha = mu / sigma
        phi = _normal_pdf(alpha)
        Phi = _normal_cdf(alpha)
        m = sigma * phi + mu * Phi
        second = (mu * mu + sigma2) * Phi + mu * sigma * phi
        mean[regular] = m
        var[regular] = np.maximum(second - m * m, 0.0)

    return mean, var


def exact_angular_reference(weights: list[np.ndarray]) -> dict:
    # On a fixed angular interval every zero-bias deep ReLU activation is exactly
    # c0*cos(theta)+c1*sin(theta). Split intervals at every exact preactivation zero.
    intervals: list[tuple[float, float, np.ndarray]] = [
        (0.0, 2.0 * math.pi, np.eye(LATENT_DIM, dtype=np.float64))
    ]

    e_r = math.sqrt(math.pi / 2.0)
    e_r2 = 2.0

    layers = []
    exact_post_means = []
    exact_post_vars = []
    exact_pre_means = []
    exact_pre_vars = []

    for layer_index, w in enumerate(weights):
        pre_first_ang = np.zeros(WIDTH, dtype=np.float64)
        pre_second_ang = np.zeros(WIDTH, dtype=np.float64)
        post_first_ang = np.zeros(WIDTH, dtype=np.float64)
        post_second_ang = np.zeros(WIDTH, dtype=np.float64)
        next_intervals: list[tuple[float, float, np.ndarray]] = []

        for lo, hi, h_coeff in intervals:
            pre_coeff = w.T @ h_coeff
            p1, p2 = _integrate_linear_and_square(pre_coeff, lo, hi)
            pre_first_ang += p1
            pre_second_ang += p2

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
                direction = np.array([math.cos(mid), math.sin(mid)], dtype=np.float64)
                signs = (pre_coeff @ direction) > 0.0
                out_coeff = pre_coeff.copy()
                out_coeff[~signs, :] = 0.0
                q1, q2 = _integrate_linear_and_square(out_coeff, left, right)
                post_first_ang += q1
                post_second_ang += q2
                next_intervals.append((left, right, out_coeff))

        angular_scale = 1.0 / (2.0 * math.pi)
        pre_mean = e_r * pre_first_ang * angular_scale
        pre_raw2 = e_r2 * pre_second_ang * angular_scale
        pre_var = np.maximum(pre_raw2 - pre_mean * pre_mean, 0.0)

        post_mean = e_r * post_first_ang * angular_scale
        post_raw2 = e_r2 * post_second_ang * angular_scale
        post_var = np.maximum(post_raw2 - post_mean * post_mean, 0.0)

        plugin_mean, plugin_var = gaussian_relu_plugin(pre_mean, pre_var)
        mean_bias = plugin_mean - post_mean
        var_bias = plugin_var - post_var

        layer = {
            "layer": layer_index,
            "interval_count_in": len(intervals),
            "interval_count_out": len(next_intervals),
            "pre_mean": pre_mean.tolist(),
            "pre_variance": pre_var.tolist(),
            "exact_post_mean": post_mean.tolist(),
            "exact_post_variance": post_var.tolist(),
            "plugin_mean": plugin_mean.tolist(),
            "plugin_variance": plugin_var.tolist(),
            "mean_bias": mean_bias.tolist(),
            "mean_bias_mse": float(np.mean(mean_bias * mean_bias)),
            "mean_bias_max_abs": float(np.max(np.abs(mean_bias))),
            "mean_bias_signed_average": float(np.mean(mean_bias)),
            "variance_bias_mse": float(np.mean(var_bias * var_bias)),
            "variance_bias_max_abs": float(np.max(np.abs(var_bias))),
        }
        layers.append(layer)
        exact_pre_means.append(pre_mean)
        exact_pre_vars.append(pre_var)
        exact_post_means.append(post_mean)
        exact_post_vars.append(post_var)
        intervals = next_intervals

    return {
        "layers": layers,
        "pre_means": np.stack(exact_pre_means, axis=0),
        "pre_vars": np.stack(exact_pre_vars, axis=0),
        "post_means": np.stack(exact_post_means, axis=0),
        "post_vars": np.stack(exact_post_vars, axis=0),
        "final_interval_count": len(intervals),
    }


def billed_plugin_formula(pre_means: np.ndarray, pre_vars: np.ndarray) -> dict:
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        mu = fnp.asarray(pre_means, dtype=fnp.float64)
        var = fnp.asarray(pre_vars, dtype=fnp.float64)
        var = fnp.maximum(var, fnp.float64(VAR_EPS))
        sigma = fnp.sqrt(var)
        alpha = fnp.divide(mu, sigma)
        phi = flops.stats.norm.pdf(alpha)
        Phi = flops.stats.norm.cdf(alpha)
        plugin = fnp.add(fnp.multiply(sigma, phi), fnp.multiply(mu, Phi))

    arr = np.asarray(plugin, dtype=np.float64)
    return {
        "formula_flops": int(ctx.flops_used),
        "shape": list(arr.shape),
        "finite": bool(np.isfinite(arr).all()),
        "max_abs": float(np.max(np.abs(arr))),
    }


def _max_numeric_delta(a: dict, b: dict) -> float:
    delta = 0.0
    for la, lb in zip(a["layers"], b["layers"]):
        for key in (
            "mean_bias_mse",
            "mean_bias_max_abs",
            "mean_bias_signed_average",
            "variance_bias_mse",
            "variance_bias_max_abs",
        ):
            delta = max(delta, abs(float(la[key]) - float(lb[key])))
        for key in (
            "pre_mean",
            "pre_variance",
            "exact_post_mean",
            "exact_post_variance",
            "plugin_mean",
            "plugin_variance",
            "mean_bias",
        ):
            xa = np.asarray(la[key], dtype=np.float64)
            xb = np.asarray(lb[key], dtype=np.float64)
            delta = max(delta, float(np.max(np.abs(xa - xb))))
    return delta


def main() -> None:
    weights = make_weights()

    first = exact_angular_reference(weights)
    second = exact_angular_reference(weights)
    repeat_max_abs = _max_numeric_delta(first, second)

    cost = billed_plugin_formula(first["pre_means"], first["pre_vars"])

    layer_mses = [float(layer["mean_bias_mse"]) for layer in first["layers"]]
    final_mse = layer_mses[-1]
    max_layer_mse = max(layer_mses)

    integrity = {
        "finite_reference": bool(
            np.isfinite(first["pre_means"]).all()
            and np.isfinite(first["pre_vars"]).all()
            and np.isfinite(first["post_means"]).all()
            and np.isfinite(first["post_vars"]).all()
        ),
        "finite_billed_plugin_formula": cost["finite"],
        "deterministic_repeat_max_abs_eq_0": repeat_max_abs == 0.0,
        "depth_exact": len(first["layers"]) == DEPTH,
        "width_exact": first["post_means"].shape == (DEPTH, WIDTH),
    }
    scientific = {
        "every_layer_mean_bias_mse_le_1_89e_8": all(m <= RAW_TARGET for m in layer_mses),
        "final_layer_mean_bias_mse_le_1_89e_8": final_mse <= RAW_TARGET,
    }

    terminal_no_go = not all(scientific.values())
    decision = (
        "TERMINAL_BIAS_NO_GO"
        if terminal_no_go
        else "BIAS_ADMISSION_PASS_FREEZE_PRODUCTION_SHAPED_PROTOCOL"
    )

    result = {
        "schema": "arc.whitebox.e111.exact_angular_bias_falsifier.v1",
        "experiment": "E111",
        "freeze_commit": "a7ca77a4c7360d9920f3302b2d6e7df6ce13a467",
        "network": {
            "latent_gaussian_dimension": LATENT_DIM,
            "width": WIDTH,
            "depth": DEPTH,
            "weight_seed": WEIGHT_SEED,
            "biases": "all_zero",
            "weight_dtype": "float64",
        },
        "reference": {
            "type": "exact piecewise angular integration + analytic Rayleigh radial moments",
            "quadrature": False,
            "E_R": math.sqrt(math.pi / 2.0),
            "E_R2": 2.0,
            "final_interval_count": first["final_interval_count"],
            "target_free": True,
        },
        "layers": first["layers"],
        "bias_summary": {
            "raw_target_mse": RAW_TARGET,
            "layer_mean_bias_mse": layer_mses,
            "max_layer_mean_bias_mse": max_layer_mse,
            "final_layer_mean_bias_mse": final_mse,
            "final_layer_mean_bias_max_abs": first["layers"][-1]["mean_bias_max_abs"],
            "final_layer_mean_bias_signed_average": first["layers"][-1][
                "mean_bias_signed_average"
            ],
        },
        "variance_summary": {
            "layer_variance_bias_mse": [
                float(layer["variance_bias_mse"]) for layer in first["layers"]
            ],
            "layer_variance_bias_max_abs": [
                float(layer["variance_bias_max_abs"]) for layer in first["layers"]
            ],
            "decisive": False,
        },
        "determinism": {
            "repeat_max_abs": repeat_max_abs,
        },
        "cost": {
            "small_shape_billed_plugin_formula_flops": cost["formula_flops"],
            "small_shape_billed_plugin_formula_shape": cost["shape"],
            "production_cost_receipt_flops": PRODUCTION_ALL_IN_FLOPS,
            "production_cost_receipt_utilization": PRODUCTION_ALL_IN_UTIL,
            "production_utilization_limit": PRODUCTION_UTIL_LIMIT,
            "production_cost_gate_still_passes": PRODUCTION_ALL_IN_UTIL
            <= PRODUCTION_UTIL_LIMIT,
            "reference_integration_cost_classification": (
                "research truth construction; not candidate production cost"
            ),
        },
        "gates": {
            **integrity,
            **scientific,
        },
        "decision": decision,
        "terminal_no_go": terminal_no_go,
        "scientific_go": False,
        "scope": {
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E111_BIAS_FALSIFIER=" + json.dumps(result, sort_keys=True), flush=True)

    # Scientific NO-GO is a valid completed falsifier, not a workflow failure.
    if not all(integrity.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
