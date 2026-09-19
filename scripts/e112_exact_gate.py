from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

LATENT_DIM = 2
WIDTH = 8
DEPTH = 4
WEIGHT_SEED = 112112
RAW_TARGET = 1.89e-8
VAR_EPS = 1e-15
BUDGET = 2**41
PRODUCTION_BASE_FLOPS = 149_220_512_434
PRODUCTION_INCREMENT_UPPER = 500_000_000
PRODUCTION_UPPER = PRODUCTION_BASE_FLOPS + PRODUCTION_INCREMENT_UPPER
OUT = Path("e112-exact-gate.json")


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


def primitive_cos_power(x: float, k: int) -> float:
    if k == 1:
        return math.sin(x)
    if k == 2:
        return 0.5 * x + 0.25 * math.sin(2.0 * x)
    if k == 3:
        return 0.25 * (3.0 * math.sin(x) + math.sin(3.0 * x) / 3.0)
    if k == 4:
        return (
            3.0 * x / 8.0
            + math.sin(2.0 * x) / 4.0
            + math.sin(4.0 * x) / 32.0
        )
    raise ValueError(k)


def integrate_power(coeff: np.ndarray, lo: float, hi: float, k: int) -> np.ndarray:
    a = coeff[:, 0]
    b = coeff[:, 1]
    amp = np.hypot(a, b)
    phase = np.arctan2(b, a)
    vals = np.empty(coeff.shape[0], dtype=np.float64)
    for i in range(coeff.shape[0]):
        if amp[i] <= 1e-30:
            vals[i] = 0.0
        else:
            left = lo - float(phase[i])
            right = hi - float(phase[i])
            vals[i] = (float(amp[i]) ** k) * (
                primitive_cos_power(right, k) - primitive_cos_power(left, k)
            )
    return vals


def normal_pdf(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def normal_cdf(x: np.ndarray) -> np.ndarray:
    flat = np.asarray(x, dtype=np.float64).ravel()
    vals = np.fromiter(
        (0.5 * (1.0 + math.erf(float(v) / math.sqrt(2.0))) for v in flat),
        dtype=np.float64,
        count=flat.size,
    )
    return vals.reshape(np.shape(x))


def gaussian_relu(mu: np.ndarray, var: np.ndarray) -> np.ndarray:
    m = np.asarray(mu, dtype=np.float64)
    v = np.asarray(var, dtype=np.float64)
    out = np.maximum(m, 0.0).copy()
    regular = v > VAR_EPS
    if np.any(regular):
        sigma = np.sqrt(v[regular])
        alpha = m[regular] / sigma
        out[regular] = sigma * normal_pdf(alpha) + m[regular] * normal_cdf(alpha)
    return out


def edgeworth4_relu(
    mu: np.ndarray,
    var: np.ndarray,
    central3: np.ndarray,
    central4: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    m = np.asarray(mu, dtype=np.float64)
    v = np.asarray(var, dtype=np.float64)
    out = gaussian_relu(m, v)
    skew = np.zeros_like(m)
    excess = np.zeros_like(m)
    regular = v > VAR_EPS
    if np.any(regular):
        sigma = np.sqrt(v[regular])
        skew_r = central3[regular] / (sigma**3)
        excess_r = central4[regular] / (v[regular] ** 2) - 3.0
        a = -m[regular] / sigma
        phi = normal_pdf(a)
        h1 = a
        h2 = a * a - 1.0
        h4 = a**4 - 6.0 * a * a + 3.0
        correction = sigma * phi * (
            (skew_r / 6.0) * h1
            + (excess_r / 24.0) * h2
            + ((skew_r * skew_r) / 72.0) * h4
        )
        out[regular] = out[regular] + correction
        skew[regular] = skew_r
        excess[regular] = excess_r
    return out, skew, excess


def exact_reference(weights: list[np.ndarray]) -> dict:
    intervals: list[tuple[float, float, np.ndarray]] = [
        (0.0, 2.0 * math.pi, np.eye(LATENT_DIM, dtype=np.float64))
    ]
    layers = []

    for layer_index, w in enumerate(weights):
        raw_integrals = [np.zeros(WIDTH, dtype=np.float64) for _ in range(4)]
        post_first = np.zeros(WIDTH, dtype=np.float64)
        next_intervals: list[tuple[float, float, np.ndarray]] = []

        for lo, hi, h_coeff in intervals:
            pre_coeff = w.T @ h_coeff
            for k in range(1, 5):
                raw_integrals[k - 1] += integrate_power(pre_coeff, lo, hi, k)

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
                post_first += integrate_power(out_coeff, left, right, 1)
                next_intervals.append((left, right, out_coeff))

        scale = 1.0 / (2.0 * math.pi)
        raw = [
            radial_moment(k) * raw_integrals[k - 1] * scale
            for k in range(1, 5)
        ]
        mu, r2, r3, r4 = raw
        var = np.maximum(r2 - mu * mu, 0.0)
        c3 = r3 - 3.0 * mu * r2 + 2.0 * mu**3
        c4 = r4 - 4.0 * mu * r3 + 6.0 * mu * mu * r2 - 3.0 * mu**4
        exact_post = radial_moment(1) * post_first * scale
        gaussian = gaussian_relu(mu, var)
        e4, skew, excess = edgeworth4_relu(mu, var, c3, c4)

        gbias = gaussian - exact_post
        ebias = e4 - exact_post
        gmse = float(np.mean(gbias * gbias))
        emse = float(np.mean(ebias * ebias))
        layers.append(
            {
                "layer": layer_index + 1,
                "interval_count_in": len(intervals),
                "interval_count_out": len(next_intervals),
                "exact_post_mean": exact_post.tolist(),
                "gaussian_mean": gaussian.tolist(),
                "edgeworth4_mean": e4.tolist(),
                "gaussian_bias_mse": gmse,
                "edgeworth4_bias_mse": emse,
                "edgeworth4_over_gaussian": (emse / gmse if gmse > 0.0 else 0.0),
                "edgeworth4_bias_max_abs": float(np.max(np.abs(ebias))),
                "skew_min": float(np.min(skew)),
                "skew_max": float(np.max(skew)),
                "excess_kurtosis_min": float(np.min(excess)),
                "excess_kurtosis_max": float(np.max(excess)),
            }
        )
        intervals = next_intervals

    return {"layers": layers, "final_interval_count": len(intervals)}


def numeric_delta(a: dict, b: dict) -> float:
    d = 0.0
    for la, lb in zip(a["layers"], b["layers"]):
        for key in (
            "gaussian_bias_mse",
            "edgeworth4_bias_mse",
            "edgeworth4_over_gaussian",
            "edgeworth4_bias_max_abs",
            "skew_min",
            "skew_max",
            "excess_kurtosis_min",
            "excess_kurtosis_max",
        ):
            d = max(d, abs(float(la[key]) - float(lb[key])))
        for key in ("exact_post_mean", "gaussian_mean", "edgeworth4_mean"):
            xa = np.asarray(la[key], dtype=np.float64)
            xb = np.asarray(lb[key], dtype=np.float64)
            d = max(d, float(np.max(np.abs(xa - xb))))
    return d


def main() -> None:
    weights = make_weights()
    first = exact_reference(weights)
    second = exact_reference(weights)
    repeat = numeric_delta(first, second)

    layer_e = [float(x["edgeworth4_bias_mse"]) for x in first["layers"]]
    layer_g = [float(x["gaussian_bias_mse"]) for x in first["layers"]]
    final_e = layer_e[-1]
    final_g = layer_g[-1]
    all_layer = float(np.mean(layer_e))

    finite = all(
        math.isfinite(v)
        for layer in first["layers"]
        for key, value in layer.items()
        for v in (
            value if isinstance(value, list) else [value]
        )
        if isinstance(v, (int, float))
    )

    gates = {
        "reference_and_candidate_finite": finite,
        "deterministic_repeat_max_abs_eq_0": repeat == 0.0,
        "first_layer_bias_mse_le_1e_24": layer_e[0] <= 1e-24,
        "final_layer_bias_mse_le_1_89e_8": final_e <= RAW_TARGET,
        "pooled_all_layer_bias_mse_le_1_89e_8": all_layer <= RAW_TARGET,
        "final_edgeworth_strictly_better_than_gaussian": final_e < final_g,
        "production_cost_admission_le_0_13": PRODUCTION_UPPER / BUDGET <= 0.13,
    }
    survive = bool(all(gates.values()))
    decision = "SMALL_EXACT_SCIENTIFIC_GO" if survive else "TERMINAL_NO_GO_DROP"

    out = {
        "schema": "arc.whitebox.e112.edgeworth4_exact_gate.v1",
        "experiment": "E112",
        "idempotency_key": "ARC-E112-EDGEWORTH4-RELU-PLUGIN-20260919",
        "network": {
            "latent_dim": LATENT_DIM,
            "width": WIDTH,
            "depth": DEPTH,
            "weight_seed": WEIGHT_SEED,
            "zero_bias": True,
        },
        "reference": {
            "type": "exact piecewise angular integration with analytic Rayleigh moments through order 4",
            "monte_carlo": False,
            "numerical_quadrature": False,
            "final_interval_count": first["final_interval_count"],
        },
        "layers": first["layers"],
        "aggregate": {
            "layer_edgeworth4_bias_mse": layer_e,
            "layer_gaussian_bias_mse": layer_g,
            "pooled_all_layer_edgeworth4_bias_mse": all_layer,
            "final_edgeworth4_bias_mse": final_e,
            "final_gaussian_bias_mse": final_g,
            "final_edgeworth4_over_gaussian": final_e / final_g if final_g > 0.0 else 0.0,
            "raw_target": RAW_TARGET,
            "final_edgeworth4_over_target": final_e / RAW_TARGET,
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
    print("E112_EXACT_GATE=" + json.dumps(out, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
