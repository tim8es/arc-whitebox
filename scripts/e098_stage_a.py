from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

WIDTH = 128
DEPTH = 6
RANK = 8
NETWORK_SEEDS = (98098, 98198, 98298)
MOMENT_INPUT_SEEDS = (198098, 198198, 198298)
REFERENCE_INPUT_SEEDS = (298098, 298198, 298298)
MOMENT_SAMPLES = 32768
REFERENCE_SAMPLES = 32768
SOURCE_LAYERS = (3, 4)
SIGNAL_FLOOR = 1e-5

PHASE2_W = 1024
PHASE2_R = 8
PHASE2_BUDGET = 2**41


def norm_pdf(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return np.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def norm_cdf(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    flat = x.ravel()
    vals = np.fromiter(
        (math.erf(float(v) / math.sqrt(2.0)) for v in flat),
        dtype=np.float64,
        count=flat.size,
    )
    return (0.5 * (1.0 + vals)).reshape(x.shape)


def generate_weights(seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    scale = math.sqrt(2.0 / WIDTH)
    return [
        rng.normal(0.0, scale, size=(WIDTH, WIDTH)).astype(np.float64, copy=False)
        for _ in range(DEPTH)
    ]


def make_inputs(seed: int, count: int) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(seed))
    return rng.normal(0.0, 1.0, size=(count, WIDTH)).astype(np.float64, copy=False)


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(x, 0.0)


def k22_state(h: np.ndarray) -> dict[str, object]:
    n = h.shape[0]
    mu = np.mean(h, axis=0)
    z = h - mu
    cov = (z.T @ z) / float(n)
    q = z * z
    m22 = (q.T @ q) / float(n)
    diag_cov = np.diag(cov)
    k22 = m22 - np.outer(diag_cov, diag_cov) - 2.0 * (cov * cov)
    np.fill_diagonal(k22, 0.0)
    k22 = 0.5 * (k22 + k22.T)

    eigvals, eigvecs = np.linalg.eigh(k22)
    order = np.argsort(np.abs(eigvals))[::-1]
    top = order[:RANK]
    lam = eigvals[top]
    u = eigvecs[:, top]

    sq = eigvals * eigvals
    total_energy = float(np.sum(sq))
    rank_energy = float(np.sum(lam * lam))
    captured = rank_energy / total_energy if total_energy > 0.0 else 0.0

    if total_energy > 0.0:
        p = sq / total_energy
        p = p[p > 0.0]
        effective_rank = float(np.exp(-np.sum(p * np.log(p))))
    else:
        effective_rank = 0.0

    k_norm = float(np.linalg.norm(k22))
    cov_norm = float(np.linalg.norm(cov))
    eligibility_ratio = k_norm / max(cov_norm * cov_norm, 1e-30)

    return {
        "mu": mu,
        "cov": cov,
        "k22": k22,
        "lam": lam,
        "u": u,
        "k22_frob": k_norm,
        "eligibility_ratio": eligibility_ratio,
        "rank8_energy": captured,
        "effective_rank": effective_rank,
    }


def one_step_observation(
    *,
    network_seed: int,
    source_layer: int,
    moment_h: np.ndarray,
    reference_h: np.ndarray,
    next_weight: np.ndarray,
) -> tuple[dict[str, object], dict[str, np.ndarray]]:
    state = k22_state(moment_h)
    mu = np.asarray(state["mu"], dtype=np.float64)
    cov = np.asarray(state["cov"], dtype=np.float64)
    k22 = np.asarray(state["k22"], dtype=np.float64)
    lam = np.asarray(state["lam"], dtype=np.float64)
    u = np.asarray(state["u"], dtype=np.float64)

    pre_mean = mu @ next_weight
    pre_var = np.sum(next_weight * (cov @ next_weight), axis=0)
    min_var = float(np.min(pre_var))
    if min_var <= 0.0:
        raise RuntimeError(f"non-positive preactivation variance: {min_var}")

    sigma = np.sqrt(pre_var)
    a = pre_mean / sigma
    t = -a
    gaussian = sigma * norm_pdf(a) + pre_mean * norm_cdf(a)

    weight_sq = next_weight * next_weight
    full_kappa4 = 3.0 * np.sum(weight_sq * (k22 @ weight_sq), axis=0)
    projected = u.T @ weight_sq
    rank8_kappa4 = 3.0 * np.sum(lam[:, None] * (projected * projected), axis=0)

    common = norm_pdf(t) * (t * t - 1.0) / (24.0 * sigma**3)
    delta_full = full_kappa4 * common
    delta_rank8 = rank8_kappa4 * common

    rank8_mean = gaussian + delta_rank8
    full_mean = gaussian + delta_full
    reference_next = np.mean(relu(reference_h @ next_weight), axis=0)

    base_err = gaussian - reference_next
    rank8_err = rank8_mean - reference_next
    full_err = full_mean - reference_next

    base_sse = float(np.sum(base_err * base_err))
    rank8_sse = float(np.sum(rank8_err * rank8_err))
    full_sse = float(np.sum(full_err * full_err))
    base_mse = base_sse / WIDTH
    rank8_mse = rank8_sse / WIDTH
    full_mse = full_sse / WIDTH

    finite = bool(
        np.isfinite(gaussian).all()
        and np.isfinite(rank8_mean).all()
        and np.isfinite(full_mean).all()
        and np.isfinite(reference_next).all()
        and np.isfinite(k22).all()
    )

    record = {
        "network_seed": int(network_seed),
        "source_layer": int(source_layer),
        "target_layer": int(source_layer + 1),
        "eligibility_ratio": float(state["eligibility_ratio"]),
        "eligible": bool(float(state["eligibility_ratio"]) >= SIGNAL_FLOOR),
        "k22_frob": float(state["k22_frob"]),
        "rank8_energy": float(state["rank8_energy"]),
        "effective_rank": float(state["effective_rank"]),
        "gaussian_base_mse": base_mse,
        "full_k22_mse": full_mse,
        "rank8_k22_mse": rank8_mse,
        "rank8_over_base": float(rank8_mse / base_mse) if base_mse > 0.0 else math.inf,
        "full_over_base": float(full_mse / base_mse) if base_mse > 0.0 else math.inf,
        "max_abs_rank8_correction": float(np.max(np.abs(delta_rank8))),
        "min_sigma": float(np.min(sigma)),
        "finite": finite,
    }
    arrays = {
        "gaussian": gaussian,
        "rank8_mean": rank8_mean,
        "full_mean": full_mean,
        "reference_next": reference_next,
    }
    return record, arrays


def static_cost() -> dict[str, object]:
    w = PHASE2_W
    r = PHASE2_R
    response = (2 * r + 4) * w * w + 16 * r * w + 32 * w
    two_late = 2 * (4 * r * w * w + 16 * r * r * w) + 2 * response
    return {
        "width": w,
        "rank": r,
        "budget": PHASE2_BUDGET,
        "response_flops": int(response),
        "response_fraction": float(response / PHASE2_BUDGET),
        "two_late_flops": int(two_late),
        "two_late_fraction": float(two_late / PHASE2_BUDGET),
        "response_gate": bool(response / PHASE2_BUDGET < 1e-5),
        "two_late_gate": bool(two_late / PHASE2_BUDGET < 1e-4),
    }


def run_once() -> dict[str, object]:
    observations: list[dict[str, object]] = []
    base_sse = 0.0
    rank8_sse = 0.0
    full_sse = 0.0
    count = 0

    for network_seed, moment_seed, reference_seed in zip(
        NETWORK_SEEDS, MOMENT_INPUT_SEEDS, REFERENCE_INPUT_SEEDS, strict=True
    ):
        weights = generate_weights(network_seed)
        moment_h = make_inputs(moment_seed, MOMENT_SAMPLES)
        reference_h = make_inputs(reference_seed, REFERENCE_SAMPLES)

        for layer, weight in enumerate(weights):
            moment_h = relu(moment_h @ weight)
            reference_h = relu(reference_h @ weight)

            if layer in SOURCE_LAYERS:
                record, arrays = one_step_observation(
                    network_seed=network_seed,
                    source_layer=layer,
                    moment_h=moment_h,
                    reference_h=reference_h,
                    next_weight=weights[layer + 1],
                )
                observations.append(record)

                b = arrays["gaussian"] - arrays["reference_next"]
                r = arrays["rank8_mean"] - arrays["reference_next"]
                f = arrays["full_mean"] - arrays["reference_next"]
                base_sse += float(np.sum(b * b))
                rank8_sse += float(np.sum(r * r))
                full_sse += float(np.sum(f * f))
                count += WIDTH

    if len(observations) != 6:
        raise AssertionError(f"expected 6 observations, got {len(observations)}")

    energies = np.asarray([float(x["rank8_energy"]) for x in observations], dtype=np.float64)
    rank_ratios = np.asarray([float(x["rank8_over_base"]) for x in observations], dtype=np.float64)
    base_mse = base_sse / count
    rank8_mse = rank8_sse / count
    full_mse = full_sse / count

    return {
        "observations": observations,
        "aggregate": {
            "gaussian_base_mse": float(base_mse),
            "rank8_k22_mse": float(rank8_mse),
            "full_k22_mse": float(full_mse),
            "rank8_over_base": float(rank8_mse / base_mse),
            "full_over_base": float(full_mse / base_mse),
            "rank8_wins": int(np.sum(rank_ratios < 1.0)),
            "worst_rank8_over_base": float(np.max(rank_ratios)),
            "median_rank8_energy": float(np.median(energies)),
            "worst_rank8_energy": float(np.min(energies)),
        },
        "cost": static_cost(),
    }


def scalar_vector(result: dict[str, object]) -> np.ndarray:
    vals: list[float] = []
    agg = result["aggregate"]
    for key in (
        "gaussian_base_mse",
        "rank8_k22_mse",
        "full_k22_mse",
        "rank8_over_base",
        "full_over_base",
        "rank8_wins",
        "worst_rank8_over_base",
        "median_rank8_energy",
        "worst_rank8_energy",
    ):
        vals.append(float(agg[key]))
    for obs in result["observations"]:
        for key in (
            "eligibility_ratio",
            "k22_frob",
            "rank8_energy",
            "effective_rank",
            "gaussian_base_mse",
            "full_k22_mse",
            "rank8_k22_mse",
            "rank8_over_base",
            "full_over_base",
            "max_abs_rank8_correction",
            "min_sigma",
        ):
            vals.append(float(obs[key]))
    return np.asarray(vals, dtype=np.float64)


def main() -> None:
    first = run_once()
    second = run_once()
    v1 = scalar_vector(first)
    v2 = scalar_vector(second)
    repeat_max_abs = float(np.max(np.abs(v1 - v2)))

    obs = first["observations"]
    agg = first["aggregate"]
    cost = first["cost"]

    gates = {
        "finite_and_eligible": bool(
            all(bool(x["finite"]) and bool(x["eligible"]) for x in obs)
        ),
        "sigma_gt_1e_10": bool(all(float(x["min_sigma"]) > 1e-10 for x in obs)),
        "median_rank8_energy_ge_0_82": bool(float(agg["median_rank8_energy"]) >= 0.82),
        "worst_rank8_energy_ge_0_70": bool(float(agg["worst_rank8_energy"]) >= 0.70),
        "rank8_over_base_le_0_90": bool(float(agg["rank8_over_base"]) <= 0.90),
        "full_over_base_le_0_90": bool(float(agg["full_over_base"]) <= 0.90),
        "rank8_wins_ge_4": bool(int(agg["rank8_wins"]) >= 4),
        "worst_rank8_over_base_le_1_35": bool(
            float(agg["worst_rank8_over_base"]) <= 1.35
        ),
        "repeat_max_abs_le_1e_12": bool(repeat_max_abs <= 1e-12),
        "response_cost_fraction_lt_1e_5": bool(cost["response_gate"]),
        "two_late_cost_fraction_lt_1e_4": bool(cost["two_late_gate"]),
    }
    stage_a_go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e098.late_k22_response_relevance.v1",
        "experiment": "E098",
        "idempotency_key": "ARC-E098-LATE-K22-RESPONSE-RELEVANCE-20260918",
        "scope": {
            "synthetic_only": True,
            "public": False,
            "official_scorer": False,
            "benchmark_holdout": False,
            "full_suite": False,
            "benchmark_targets_read": False,
        },
        "frozen": {
            "width": WIDTH,
            "depth": DEPTH,
            "rank": RANK,
            "network_seeds": list(NETWORK_SEEDS),
            "moment_input_seeds": list(MOMENT_INPUT_SEEDS),
            "reference_input_seeds": list(REFERENCE_INPUT_SEEDS),
            "moment_samples": MOMENT_SAMPLES,
            "reference_samples": REFERENCE_SAMPLES,
            "source_layers": list(SOURCE_LAYERS),
        },
        "observations": obs,
        "aggregate": agg,
        "repeat_scalar_max_abs": repeat_max_abs,
        "cost": cost,
        "gates": gates,
        "decision": "STAGE_A_GO" if stage_a_go else "STAGE_A_NO_GO",
        "scientific_go": False,
        "terminal_no_go": bool(not stage_a_go),
        "note": (
            "STAGE_A_GO is only synthetic oracle value-of-information evidence; "
            "it does not establish a deployable K22 birth/transport law or authorize benchmark access."
            if stage_a_go
            else "At least one preregistered synthetic gate failed; E098 is terminal NO-GO / DROP with no rescue or rerun."
        ),
    }

    out = Path("e098-stage-a.json")
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("E098_STAGE_A=" + json.dumps(result, sort_keys=True))

    if not stage_a_go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
