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
SEED = 113113
RAW_TARGET = 1.89e-8
VAR_EPS = 1e-15

PROD_WIDTH = 1024
PROD_DEPTH = 16
PROD_N = 4096
PROD_LATE_LAYERS = 4
BUDGET = 2**41
HARD_LIMIT = (13 * BUDGET) // 100
E104_BASE_FLOPS = 149_114_620_592

OUT = Path("e113-top2-gate-conditional.json")


def make_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(SEED))
    out: list[np.ndarray] = []
    w0 = rng.standard_normal((LATENT_DIM, WIDTH)).astype(np.float64)
    w0 *= math.sqrt(2.0 / LATENT_DIM)
    out.append(w0)
    for _ in range(1, DEPTH):
        w = rng.standard_normal((WIDTH, WIDTH)).astype(np.float64)
        w *= math.sqrt(2.0 / WIDTH)
        out.append(w)
    return out


def roots_in_interval(a: float, b: float, lo: float, hi: float) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    delta = math.atan2(b, a)
    base = delta + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    roots: list[float] = []
    for k in range(k0, k1 + 1):
        r = base + k * math.pi
        if lo + 1e-12 < r < hi - 1e-12:
            roots.append(r)
    return roots


def dedup(xs: list[float]) -> list[float]:
    out: list[float] = []
    for x in sorted(xs):
        if not out or abs(x - out[-1]) > 1e-11:
            out.append(x)
    return out


def integrate_linear_square(
    coeff: np.ndarray, lo: float, hi: float
) -> tuple[np.ndarray, np.ndarray]:
    a = coeff[:, 0]
    b = coeff[:, 1]
    d = hi - lo
    int_c = math.sin(hi) - math.sin(lo)
    int_s = -math.cos(hi) + math.cos(lo)
    int_c2 = 0.5 * d + 0.25 * (math.sin(2 * hi) - math.sin(2 * lo))
    int_s2 = 0.5 * d - 0.25 * (math.sin(2 * hi) - math.sin(2 * lo))
    int_cs = 0.5 * (math.sin(hi) ** 2 - math.sin(lo) ** 2)
    first = a * int_c + b * int_s
    second = a * a * int_c2 + b * b * int_s2 + 2.0 * a * b * int_cs
    return first, second


def normal_pdf(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def normal_cdf(x: np.ndarray) -> np.ndarray:
    flat = np.asarray(x, dtype=np.float64).reshape(-1)
    vals = [0.5 * (1.0 + math.erf(float(v) / math.sqrt(2.0))) for v in flat]
    return np.asarray(vals, dtype=np.float64).reshape(np.shape(x))


def gaussian_relu_moments(mu: np.ndarray, var: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = np.asarray(mu, dtype=np.float64)
    var = np.asarray(var, dtype=np.float64)
    mean = np.empty_like(mu)
    raw2 = np.empty_like(mu)
    deg = var <= VAR_EPS
    reg = ~deg
    mean[deg] = np.maximum(mu[deg], 0.0)
    raw2[deg] = mean[deg] * mean[deg]
    if np.any(reg):
        m = mu[reg]
        v = var[reg]
        s = np.sqrt(v)
        a = m / s
        phi = normal_pdf(a)
        Phi = normal_cdf(a)
        mean[reg] = s * phi + m * Phi
        raw2[reg] = (m * m + v) * Phi + m * s * phi
    return mean, raw2


def top2_indices(column: np.ndarray) -> tuple[int, int]:
    vals = np.abs(np.asarray(column, dtype=np.float64))
    # Stable tie-break: descending absolute value, then lower index.
    order = sorted(range(vals.size), key=lambda i: (-float(vals[i]), i))
    return int(order[0]), int(order[1])


def exact_and_candidate(weights: list[np.ndarray]) -> dict:
    # interval = (lo, hi, postactivation coefficient matrix, previous mask)
    intervals: list[tuple[float, float, np.ndarray, np.ndarray | None]] = [
        (0.0, 2.0 * math.pi, np.eye(LATENT_DIM, dtype=np.float64), None)
    ]
    e_r = math.sqrt(math.pi / 2.0)
    e_r2 = 2.0
    twopi = 2.0 * math.pi

    layers = []

    for li, w in enumerate(weights):
        exact_post_i1 = np.zeros(WIDTH, dtype=np.float64)
        exact_post_i2 = np.zeros(WIDTH, dtype=np.float64)
        pre_i1 = np.zeros(WIDTH, dtype=np.float64)
        pre_i2 = np.zeros(WIDTH, dtype=np.float64)
        next_intervals: list[tuple[float, float, np.ndarray, np.ndarray]] = []

        selected: list[tuple[int, int] | None] = []
        if li == 0:
            selected = [None] * WIDTH
            group_acc = None
        else:
            selected = [top2_indices(w[:, j]) for j in range(WIDTH)]
            # per output, 4 groups: angular length, int z, int z^2
            group_acc = np.zeros((WIDTH, 4, 3), dtype=np.float64)

        for lo, hi, h_coeff, prev_mask in intervals:
            pre_coeff = w.T @ h_coeff
            p1, p2 = integrate_linear_square(pre_coeff, lo, hi)
            pre_i1 += p1
            pre_i2 += p2

            if li > 0:
                assert group_acc is not None
                assert prev_mask is not None
                delta = hi - lo
                for j, pair in enumerate(selected):
                    assert pair is not None
                    i1, i2 = pair
                    key = (int(prev_mask[i1]) << 1) | int(prev_mask[i2])
                    group_acc[j, key, 0] += delta
                    group_acc[j, key, 1] += p1[j]
                    group_acc[j, key, 2] += p2[j]

            bounds = [lo, hi]
            for j in range(WIDTH):
                bounds.extend(
                    roots_in_interval(
                        float(pre_coeff[j, 0]),
                        float(pre_coeff[j, 1]),
                        lo,
                        hi,
                    )
                )
            bounds = dedup(bounds)

            for left, right in zip(bounds[:-1], bounds[1:]):
                if right - left <= 1e-13:
                    continue
                mid = 0.5 * (left + right)
                direction = np.array([math.cos(mid), math.sin(mid)], dtype=np.float64)
                mask = (pre_coeff @ direction) > 0.0
                out_coeff = pre_coeff.copy()
                out_coeff[~mask, :] = 0.0
                q1, q2 = integrate_linear_square(out_coeff, left, right)
                exact_post_i1 += q1
                exact_post_i2 += q2
                next_intervals.append((left, right, out_coeff, mask.copy()))

        pre_mean = e_r * pre_i1 / twopi
        pre_raw2 = e_r2 * pre_i2 / twopi
        pre_var = np.maximum(pre_raw2 - pre_mean * pre_mean, 0.0)

        exact_mean = e_r * exact_post_i1 / twopi
        exact_raw2 = e_r2 * exact_post_i2 / twopi
        exact_var = np.maximum(exact_raw2 - exact_mean * exact_mean, 0.0)

        if li == 0:
            cand_mean, cand_raw2 = gaussian_relu_moments(pre_mean, pre_var)
            group_probabilities = [[1.0] for _ in range(WIDTH)]
        else:
            assert group_acc is not None
            cand_mean = np.zeros(WIDTH, dtype=np.float64)
            cand_raw2 = np.zeros(WIDTH, dtype=np.float64)
            group_probabilities: list[list[float]] = []
            for j in range(WIDTH):
                probs = []
                for g in range(4):
                    length = float(group_acc[j, g, 0])
                    p = length / twopi
                    probs.append(p)
                    if length <= 1e-14:
                        continue
                    mu = np.asarray([e_r * group_acc[j, g, 1] / length])
                    raw2 = np.asarray([e_r2 * group_acc[j, g, 2] / length])
                    var = np.maximum(raw2 - mu * mu, 0.0)
                    gm, gr2 = gaussian_relu_moments(mu, var)
                    cand_mean[j] += p * float(gm[0])
                    cand_raw2[j] += p * float(gr2[0])
                group_probabilities.append(probs)

        cand_var = np.maximum(cand_raw2 - cand_mean * cand_mean, 0.0)
        mean_bias = cand_mean - exact_mean
        var_bias = cand_var - exact_var

        layers.append(
            {
                "layer": li,
                "interval_count_in": len(intervals),
                "interval_count_out": len(next_intervals),
                "selected_gate_pairs": [
                    None if p is None else [int(p[0]), int(p[1])] for p in selected
                ],
                "group_probabilities": group_probabilities,
                "pre_mean": pre_mean.tolist(),
                "pre_variance": pre_var.tolist(),
                "exact_post_mean": exact_mean.tolist(),
                "exact_post_variance": exact_var.tolist(),
                "candidate_post_mean": cand_mean.tolist(),
                "candidate_post_variance": cand_var.tolist(),
                "mean_bias": mean_bias.tolist(),
                "mean_bias_mse": float(np.mean(mean_bias * mean_bias)),
                "mean_bias_max_abs": float(np.max(np.abs(mean_bias))),
                "mean_bias_signed_average": float(np.mean(mean_bias)),
                "variance_bias_mse": float(np.mean(var_bias * var_bias)),
                "variance_bias_max_abs": float(np.max(np.abs(var_bias))),
            }
        )
        intervals = next_intervals

    return {"layers": layers, "final_interval_count": len(intervals)}


def max_repeat_delta(a: dict, b: dict) -> float:
    d = 0.0
    for xa, xb in zip(a["layers"], b["layers"]):
        for key in (
            "mean_bias_mse",
            "mean_bias_max_abs",
            "mean_bias_signed_average",
            "variance_bias_mse",
            "variance_bias_max_abs",
        ):
            d = max(d, abs(float(xa[key]) - float(xb[key])))
        for key in (
            "pre_mean",
            "pre_variance",
            "exact_post_mean",
            "exact_post_variance",
            "candidate_post_mean",
            "candidate_post_variance",
            "mean_bias",
        ):
            va = np.asarray(xa[key], dtype=np.float64)
            vb = np.asarray(xb[key], dtype=np.float64)
            d = max(d, float(np.max(np.abs(va - vb))))
    return d


def measure_production_formula_flops() -> int:
    # 3 estimates (full + two independent blocks) * 4 sign groups * width.
    size = 3 * 4 * PROD_WIDTH
    mu_np = np.linspace(-1.0, 1.0, size, dtype=np.float64)
    var_np = np.linspace(0.25, 1.25, size, dtype=np.float64)
    prob_np = np.full(size, 0.25, dtype=np.float64)
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        mu = fnp.asarray(mu_np, dtype=fnp.float64)
        var = fnp.asarray(var_np, dtype=fnp.float64)
        prob = fnp.asarray(prob_np, dtype=fnp.float64)
        var = fnp.maximum(var, fnp.float64(VAR_EPS))
        sigma = fnp.sqrt(var)
        alpha = fnp.divide(mu, sigma)
        phi = flops.stats.norm.pdf(alpha)
        Phi = flops.stats.norm.cdf(alpha)
        mean = fnp.add(fnp.multiply(sigma, phi), fnp.multiply(mu, Phi))
        raw2 = fnp.add(
            fnp.multiply(fnp.add(fnp.multiply(mu, mu), var), Phi),
            fnp.multiply(fnp.multiply(mu, sigma), phi),
        )
        _ = fnp.sum(fnp.multiply(prob, mean), dtype=fnp.float64)
        _ = fnp.sum(fnp.multiply(prob, raw2), dtype=fnp.float64)
    return int(ctx.flops_used)


def production_cost() -> dict:
    n = PROD_WIDTH
    N = PROD_N
    per_layer_gate_scan = 6 * n * n
    per_layer_group_accum = 32 * N * n
    per_layer_error_reduction = 8 * n
    per_layer_special = measure_production_formula_flops()
    per_layer = (
        per_layer_gate_scan
        + per_layer_group_accum
        + per_layer_error_reduction
        + per_layer_special
    )
    raw_increment = PROD_LATE_LAYERS * per_layer
    safety_increment = 2 * raw_increment
    total = E104_BASE_FLOPS + safety_increment
    return {
        "e104_base_flops": E104_BASE_FLOPS,
        "late_layers": PROD_LATE_LAYERS,
        "per_layer_gate_scan_upper": per_layer_gate_scan,
        "per_layer_group_accum_upper": per_layer_group_accum,
        "per_layer_error_reduction_upper": per_layer_error_reduction,
        "per_layer_special_measured": per_layer_special,
        "per_layer_total_before_safety": per_layer,
        "raw_increment_upper": raw_increment,
        "safety_factor": 2,
        "safety_factored_increment": safety_increment,
        "all_in_upper_flops": total,
        "all_in_utilization": total / BUDGET,
        "hard_limit_flops": HARD_LIMIT,
        "remaining_flops": HARD_LIMIT - total,
        "fits_0_13": total <= HARD_LIMIT,
        "fresh_rng": False,
        "fresh_forward_trajectories": False,
    }


def main() -> None:
    weights = make_weights()
    first = exact_and_candidate(weights)
    second = exact_and_candidate(weights)
    repeat = max_repeat_delta(first, second)
    cost = production_cost()

    mses = [float(x["mean_bias_mse"]) for x in first["layers"]]
    final_mse = mses[-1]
    finite = all(
        math.isfinite(float(x[k]))
        for x in first["layers"]
        for k in (
            "mean_bias_mse",
            "mean_bias_max_abs",
            "variance_bias_mse",
            "variance_bias_max_abs",
        )
    )

    gates = {
        "finite": finite,
        "deterministic_repeat_max_abs_eq_0": repeat == 0.0,
        "layer1_bias_mse_le_target": mses[0] <= RAW_TARGET,
        "every_later_layer_bias_mse_le_target": all(m <= RAW_TARGET for m in mses[1:]),
        "final_layer_bias_mse_le_target": final_mse <= RAW_TARGET,
        "production_cost_fits_0_13": bool(cost["fits_0_13"]),
    }
    pass_all = all(gates.values())

    result = {
        "schema": "arc.whitebox.e113.top2_gate_conditional_moments.v1",
        "experiment": "E113",
        "freeze_commit": "e51c92b159f6c2b99a1d1a0653b9cf5df7c17e4a",
        "network": {
            "latent_dimension": LATENT_DIM,
            "width": WIDTH,
            "depth": DEPTH,
            "seed": SEED,
            "biases": "all_zero",
        },
        "candidate": {
            "conditioning_bits_per_output": 2,
            "group_count": 4,
            "gate_selection": "two largest abs current weights, stable lower-index tie break",
            "conditional_payload": "exact group probability + preactivation mean/variance",
            "closure": "Gaussian-ReLU mean/second moment within each group",
            "target_free": True,
        },
        "reference": {
            "type": "exact angular activation-region integration with analytic Rayleigh moments",
            "monte_carlo": False,
            "numerical_quadrature": False,
            "final_interval_count": first["final_interval_count"],
        },
        "layers": first["layers"],
        "bias_summary": {
            "target_mse": RAW_TARGET,
            "layer_mean_bias_mse": mses,
            "max_layer_mean_bias_mse": max(mses),
            "final_layer_mean_bias_mse": final_mse,
            "final_over_target_ratio": final_mse / RAW_TARGET,
            "final_mean_bias_max_abs": first["layers"][-1]["mean_bias_max_abs"],
            "final_mean_bias_signed_average": first["layers"][-1][
                "mean_bias_signed_average"
            ],
        },
        "variance_summary": {
            "layer_variance_bias_mse": [
                float(x["variance_bias_mse"]) for x in first["layers"]
            ],
            "layer_variance_bias_max_abs": [
                float(x["variance_bias_max_abs"]) for x in first["layers"]
            ],
            "decisive": False,
        },
        "determinism": {"repeat_max_abs": repeat},
        "production_cost_extrapolation": cost,
        "gates": gates,
        "decision": (
            "SMALL_EXACT_GO"
            if pass_all
            else (
                "TERMINAL_COST_NO_GO"
                if not cost["fits_0_13"]
                else "TERMINAL_BIAS_NO_GO"
            )
        ),
        "scientific_go": False,
        "scope": {
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
            "tuning": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E113_FALSIFIER=" + json.dumps(result, sort_keys=True), flush=True)

    # A scientific NO-GO is a completed falsifier, not a CI failure.
    if not finite or repeat != 0.0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
