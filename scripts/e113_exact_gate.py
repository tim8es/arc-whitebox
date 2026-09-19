from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

LATENT_DIM = 2
WIDTH = 8
DEPTH = 4
WEIGHT_SEED = 113113
TOPK = 4
STATE_COUNT = 16
RAW_TARGET = 1.89e-8
VAR_EPS = 1e-15
BUDGET = 2**41
PRODUCTION_BASE_FLOPS = 149_220_512_434
PRODUCTION_INCREMENT_UPPER = 2_500_000_000
PRODUCTION_UPPER = PRODUCTION_BASE_FLOPS + PRODUCTION_INCREMENT_UPPER
OUT = Path("e113-exact-gate.json")


def make_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    weights = []
    w0 = rng.standard_normal((LATENT_DIM, WIDTH)).astype(np.float64)
    w0 *= math.sqrt(2.0 / LATENT_DIM)
    weights.append(w0)
    for _ in range(1, DEPTH):
        w = rng.standard_normal((WIDTH, WIDTH)).astype(np.float64)
        w *= math.sqrt(2.0 / WIDTH)
        weights.append(w)
    return weights


def radial_moment(k: int) -> float:
    return (2.0 ** (0.5 * k)) * math.gamma(1.0 + 0.5 * k)


def roots_in_interval(a: float, b: float, lo: float, hi: float) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    delta = math.atan2(b, a)
    base = delta + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    out = []
    for k in range(k0, k1 + 1):
        x = base + k * math.pi
        if lo + 1e-12 < x < hi - 1e-12:
            out.append(x)
    return out


def dedup(xs: list[float]) -> list[float]:
    out: list[float] = []
    for x in sorted(xs):
        if not out or abs(x - out[-1]) > 1e-11:
            out.append(x)
    return out


def integrate_linear_and_square(
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
    second = a * a * int_cos2 + b * b * int_sin2 + 2.0 * a * b * int_sincos
    return first, second


def normal_pdf_scalar(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def gaussian_relu_scalar(mu: float, var: float) -> float:
    if var <= VAR_EPS:
        return max(mu, 0.0)
    sigma = math.sqrt(var)
    alpha = mu / sigma
    Phi = 0.5 * (1.0 + math.erf(alpha / math.sqrt(2.0)))
    return sigma * normal_pdf_scalar(alpha) + mu * Phi


def gaussian_relu_vec(mu: np.ndarray, var: np.ndarray) -> np.ndarray:
    out = np.empty_like(mu, dtype=np.float64)
    for i in range(mu.size):
        out[i] = gaussian_relu_scalar(float(mu[i]), float(var[i]))
    return out


def select_top4(w: np.ndarray) -> np.ndarray:
    parents = np.empty((WIDTH, TOPK), dtype=np.int64)
    indices = np.arange(WIDTH, dtype=np.int64)
    for j in range(WIDTH):
        order = np.lexsort((indices, -np.abs(w[:, j])))
        parents[j] = order[:TOPK]
    return parents


def state_code(active: np.ndarray, selected: np.ndarray) -> int:
    code = 0
    for bit, idx in enumerate(selected):
        if bool(active[int(idx)]):
            code |= 1 << bit
    return code


def exact_reference(weights: list[np.ndarray]) -> dict:
    intervals: list[tuple[float, float, np.ndarray]] = [
        (0.0, 2.0 * math.pi, np.eye(LATENT_DIM, dtype=np.float64))
    ]
    layers = []

    for layer_index, w in enumerate(weights):
        pre_first = np.zeros(WIDTH, dtype=np.float64)
        pre_second = np.zeros(WIDTH, dtype=np.float64)
        post_first = np.zeros(WIDTH, dtype=np.float64)
        next_intervals: list[tuple[float, float, np.ndarray]] = []

        selected = None
        state_len = state_first = state_second = None
        if layer_index > 0:
            selected = select_top4(w)
            state_len = np.zeros((WIDTH, STATE_COUNT), dtype=np.float64)
            state_first = np.zeros((WIDTH, STATE_COUNT), dtype=np.float64)
            state_second = np.zeros((WIDTH, STATE_COUNT), dtype=np.float64)

        for lo, hi, h_coeff in intervals:
            pre_coeff = w.T @ h_coeff
            p1, p2 = integrate_linear_and_square(pre_coeff, lo, hi)
            pre_first += p1
            pre_second += p2

            if layer_index > 0:
                active_parent = np.linalg.norm(h_coeff, axis=1) > 1e-14
                span = hi - lo
                assert selected is not None
                assert state_len is not None and state_first is not None and state_second is not None
                for j in range(WIDTH):
                    s = state_code(active_parent, selected[j])
                    state_len[j, s] += span
                    state_first[j, s] += p1[j]
                    state_second[j, s] += p2[j]

            boundaries = [lo, hi]
            for neuron in range(WIDTH):
                boundaries.extend(
                    roots_in_interval(
                        float(pre_coeff[neuron, 0]),
                        float(pre_coeff[neuron, 1]),
                        lo,
                        hi,
                    )
                )
            boundaries = dedup(boundaries)

            for left, right in zip(boundaries[:-1], boundaries[1:]):
                if right - left <= 1e-13:
                    continue
                mid = 0.5 * (left + right)
                direction = np.array([math.cos(mid), math.sin(mid)], dtype=np.float64)
                active = (pre_coeff @ direction) > 0.0
                out_coeff = pre_coeff.copy()
                out_coeff[~active, :] = 0.0
                q1, _ = integrate_linear_and_square(out_coeff, left, right)
                post_first += q1
                next_intervals.append((left, right, out_coeff))

        angular = 1.0 / (2.0 * math.pi)
        mu = radial_moment(1) * pre_first * angular
        raw2 = radial_moment(2) * pre_second * angular
        var = np.maximum(raw2 - mu * mu, 0.0)
        exact_post = radial_moment(1) * post_first * angular
        gaussian = gaussian_relu_vec(mu, var)

        state_prob_error = 0.0
        occupied_counts: list[int] = []
        if layer_index == 0:
            candidate = gaussian.copy()
            occupied_counts = [1] * WIDTH
        else:
            assert state_len is not None and state_first is not None and state_second is not None
            candidate = np.zeros(WIDTH, dtype=np.float64)
            for j in range(WIDTH):
                prob_sum = 0.0
                occupied = 0
                for s in range(STATE_COUNT):
                    length = float(state_len[j, s])
                    if length <= 1e-15:
                        continue
                    occupied += 1
                    p = length * angular
                    prob_sum += p
                    c_mu = radial_moment(1) * float(state_first[j, s]) / length
                    c_raw2 = radial_moment(2) * float(state_second[j, s]) / length
                    c_var = max(c_raw2 - c_mu * c_mu, 0.0)
                    candidate[j] += p * gaussian_relu_scalar(c_mu, c_var)
                occupied_counts.append(occupied)
                state_prob_error = max(state_prob_error, abs(prob_sum - 1.0))

        gbias = gaussian - exact_post
        cbias = candidate - exact_post
        gmse = float(np.mean(gbias * gbias))
        cmse = float(np.mean(cbias * cbias))
        layers.append(
            {
                "layer": layer_index + 1,
                "interval_count_in": len(intervals),
                "interval_count_out": len(next_intervals),
                "exact_post_mean": exact_post.tolist(),
                "gaussian_mean": gaussian.tolist(),
                "conditional_mean": candidate.tolist(),
                "gaussian_bias_mse": gmse,
                "conditional_bias_mse": cmse,
                "conditional_over_gaussian": cmse / gmse if gmse > 0.0 else 0.0,
                "conditional_bias_max_abs": float(np.max(np.abs(cbias))),
                "state_probability_max_abs_error": state_prob_error,
                "occupied_state_count_min": int(min(occupied_counts)),
                "occupied_state_count_max": int(max(occupied_counts)),
                "occupied_state_count_mean": float(np.mean(occupied_counts)),
            }
        )
        intervals = next_intervals

    return {"layers": layers, "final_interval_count": len(intervals)}


def numeric_delta(a: dict, b: dict) -> float:
    d = 0.0
    for la, lb in zip(a["layers"], b["layers"]):
        for key in (
            "gaussian_bias_mse",
            "conditional_bias_mse",
            "conditional_over_gaussian",
            "conditional_bias_max_abs",
            "state_probability_max_abs_error",
            "occupied_state_count_mean",
        ):
            d = max(d, abs(float(la[key]) - float(lb[key])))
        for key in ("exact_post_mean", "gaussian_mean", "conditional_mean"):
            xa = np.asarray(la[key], dtype=np.float64)
            xb = np.asarray(lb[key], dtype=np.float64)
            d = max(d, float(np.max(np.abs(xa - xb))))
    return d


def main() -> None:
    weights = make_weights()
    first = exact_reference(weights)
    second = exact_reference(weights)
    repeat = numeric_delta(first, second)

    layer_c = [float(x["conditional_bias_mse"]) for x in first["layers"]]
    layer_g = [float(x["gaussian_bias_mse"]) for x in first["layers"]]
    final_c = layer_c[-1]
    final_g = layer_g[-1]
    all_layer = float(np.mean(layer_c))
    max_prob_error = max(float(x["state_probability_max_abs_error"]) for x in first["layers"])

    finite = all(
        math.isfinite(v)
        for layer in first["layers"]
        for key, value in layer.items()
        for v in (value if isinstance(value, list) else [value])
        if isinstance(v, (int, float))
    )

    gates = {
        "reference_and_candidate_finite": finite,
        "state_probabilities_sum_to_one_le_1e_14": max_prob_error <= 1e-14,
        "deterministic_repeat_max_abs_eq_0": repeat == 0.0,
        "first_layer_bias_mse_le_1e_24": layer_c[0] <= 1e-24,
        "final_layer_bias_mse_le_1_89e_8": final_c <= RAW_TARGET,
        "pooled_all_layer_bias_mse_le_1_89e_8": all_layer <= RAW_TARGET,
        "final_conditional_strictly_better_than_gaussian": final_c < final_g,
        "production_cost_admission_le_0_13": PRODUCTION_UPPER / BUDGET <= 0.13,
    }
    survive = bool(all(gates.values()))
    decision = "SMALL_EXACT_SCIENTIFIC_GO" if survive else "TERMINAL_NO_GO_DROP"

    out = {
        "schema": "arc.whitebox.e113.top4_gate_conditioned_exact_gate.v1",
        "experiment": "E113",
        "idempotency_key": "ARC-E113-TOP4-GATE-CONDITIONED-PLUGIN-20260919",
        "network": {
            "latent_dim": LATENT_DIM,
            "width": WIDTH,
            "depth": DEPTH,
            "weight_seed": WEIGHT_SEED,
            "zero_bias": True,
            "topk_parent_gates": TOPK,
            "state_count": STATE_COUNT,
        },
        "reference": {
            "type": "exact piecewise angular integration with exact actual upstream gate states",
            "monte_carlo": False,
            "numerical_quadrature": False,
            "final_interval_count": first["final_interval_count"],
        },
        "layers": first["layers"],
        "aggregate": {
            "layer_conditional_bias_mse": layer_c,
            "layer_gaussian_bias_mse": layer_g,
            "pooled_all_layer_conditional_bias_mse": all_layer,
            "final_conditional_bias_mse": final_c,
            "final_gaussian_bias_mse": final_g,
            "final_conditional_over_gaussian": final_c / final_g if final_g > 0.0 else 0.0,
            "raw_target": RAW_TARGET,
            "final_conditional_over_target": final_c / RAW_TARGET,
            "max_state_probability_abs_error": max_prob_error,
            "deterministic_repeat_max_abs": repeat,
        },
        "cost_admission": {
            "inherited_all_in_flops": PRODUCTION_BASE_FLOPS,
            "increment_upper_flops": PRODUCTION_INCREMENT_UPPER,
            "all_in_upper_flops": PRODUCTION_UPPER,
            "utilization": PRODUCTION_UPPER / BUDGET,
            "cap": 0.13,
        },
        "gates": gates,
        "decision": decision,
        "small_exact_scientific_go": survive,
        "competition_go": False,
        "scope": {
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
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E113_EXACT_GATE=" + json.dumps(out, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
