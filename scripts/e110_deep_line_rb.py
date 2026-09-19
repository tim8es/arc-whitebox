from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

WIDTH = 8
DEPTH = 5
WEIGHT_SEED = 110104
OUTER_SEED = 110105
OUTER_SAMPLES = 96
LAW_CHECK_SAMPLES = 4
GRID_POINTS = 32769
GRID_LIMIT = 8.0
INTERVAL_CAP = 20_000

TARGET_MSE = 1.89e-8
PRODUCTION_BUDGET = 2**41
PRODUCTION_UTIL_CAP = 0.13
PRODUCTION_REFERENCE_TRAJECTORIES = 4096
PRODUCTION_REFERENCE_LAYER_FLOPS = 137_573_171_200

OUT = Path("e110-smallwidth-law.json")


@dataclass
class Segment:
    lo: float
    hi: float
    slope: np.ndarray
    intercept: np.ndarray


def make_weights(width: int, depth: int, seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    scale = math.sqrt(2.0 / width)
    return [
        rng.standard_normal((width, width)).astype(np.float64) * scale
        for _ in range(depth)
    ]


def forward_final(weights: list[np.ndarray], x: np.ndarray) -> np.ndarray:
    h = np.asarray(x, dtype=np.float64)
    for w in weights:
        h = h @ w
        h = np.maximum(h, 0.0)
    return h


def deep_sensitivity_direction(weights: list[np.ndarray]) -> tuple[np.ndarray, float]:
    width = weights[0].shape[0]
    g = np.ones(width, dtype=np.float64) / math.sqrt(width)
    for w in reversed(weights):
        g = 0.5 * (w @ g)
    norm = float(np.linalg.norm(g))
    if not math.isfinite(norm) or norm <= 0.0:
        raise RuntimeError("non-finite or zero deep sensitivity direction norm")
    return g / norm, norm


def _probe(lo: float, hi: float) -> float:
    if math.isinf(lo) and math.isinf(hi):
        return 0.0
    if math.isinf(lo):
        return hi - 1.0
    if math.isinf(hi):
        return lo + 1.0
    return 0.5 * (lo + hi)


def _dedupe_roots(roots: list[float]) -> list[float]:
    if not roots:
        return []
    roots.sort()
    out = [roots[0]]
    for r in roots[1:]:
        prev = out[-1]
        tol = 1e-12 * (1.0 + abs(prev) + abs(r))
        if abs(r - prev) > tol:
            out.append(r)
    return out


def _phi(x: float) -> float:
    if math.isinf(x):
        return 0.0
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _Phi(x: float) -> float:
    if x == -math.inf:
        return 0.0
    if x == math.inf:
        return 1.0
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _partition_ok(segments: list[Segment]) -> bool:
    if not segments:
        return False
    if segments[0].lo != -math.inf or segments[-1].hi != math.inf:
        return False
    for left, right in zip(segments[:-1], segments[1:]):
        if left.hi != right.lo:
            return False
        if not (left.lo < left.hi and right.lo < right.hi):
            return False
    return all(seg.lo < seg.hi for seg in segments)


def conditional_mean_piecewise(
    weights: list[np.ndarray],
    z: np.ndarray,
    v: np.ndarray,
    interval_cap: int = INTERVAL_CAP,
) -> dict[str, object]:
    width = z.shape[0]
    segments = [
        Segment(
            lo=-math.inf,
            hi=math.inf,
            slope=np.asarray(v, dtype=np.float64).copy(),
            intercept=np.asarray(z, dtype=np.float64).copy(),
        )
    ]
    layer_input_counts: list[int] = []
    layer_output_counts: list[int] = []
    affine_matmul_flops_proxy = 0

    for w in weights:
        layer_input_counts.append(len(segments))
        next_segments: list[Segment] = []
        for seg in segments:
            # Two independent affine coefficient streams: slope and intercept.
            affine_matmul_flops_proxy += 4 * width * width
            pre_slope = seg.slope @ w
            pre_intercept = seg.intercept @ w

            roots: list[float] = []
            for a, b in zip(pre_slope, pre_intercept):
                if a == 0.0:
                    continue
                root = -b / a
                if math.isfinite(root) and seg.lo < root < seg.hi:
                    roots.append(float(root))
            roots = _dedupe_roots(roots)
            bounds = [seg.lo, *roots, seg.hi]

            for lo, hi in zip(bounds[:-1], bounds[1:]):
                probe = _probe(lo, hi)
                pre = pre_slope * probe + pre_intercept
                mask = pre > 0.0
                next_segments.append(
                    Segment(
                        lo=lo,
                        hi=hi,
                        slope=pre_slope * mask,
                        intercept=pre_intercept * mask,
                    )
                )
                if len(next_segments) > interval_cap:
                    raise OverflowError(
                        f"interval cap exceeded: {len(next_segments)} > {interval_cap}"
                    )
        segments = next_segments
        layer_output_counts.append(len(segments))

    if not _partition_ok(segments):
        raise RuntimeError("piecewise intervals do not form a complete ordered partition")

    mean = np.zeros(width, dtype=np.float64)
    for seg in segments:
        mass = _Phi(seg.hi) - _Phi(seg.lo)
        first_moment = _phi(seg.lo) - _phi(seg.hi)
        mean += seg.slope * first_moment + seg.intercept * mass

    return {
        "mean": mean,
        "segments": segments,
        "layer_input_counts": layer_input_counts,
        "layer_output_counts": layer_output_counts,
        "final_interval_count": len(segments),
        "affine_matmul_flops_proxy": affine_matmul_flops_proxy,
        "partition_ok": True,
    }


def dense_normal_integral(
    weights: list[np.ndarray],
    z: np.ndarray,
    v: np.ndarray,
    grid_points: int = GRID_POINTS,
    limit: float = GRID_LIMIT,
) -> np.ndarray:
    t = np.linspace(-limit, limit, grid_points, dtype=np.float64)
    x = z[None, :] + t[:, None] * v[None, :]
    y = forward_final(weights, x)
    density = np.exp(-0.5 * t * t) / math.sqrt(2.0 * math.pi)
    return np.trapezoid(y * density[:, None], t, axis=0)


def pooled_coordinate_variance(values: np.ndarray) -> float:
    arr = np.asarray(values, dtype=np.float64)
    return float(np.mean(np.var(arr, axis=0, ddof=1)))


def run() -> dict[str, object]:
    weights = make_weights(WIDTH, DEPTH, WEIGHT_SEED)
    v, direction_norm = deep_sensitivity_direction(weights)

    rng = np.random.Generator(np.random.PCG64(OUTER_SEED))
    x = rng.standard_normal((OUTER_SAMPLES, WIDTH)).astype(np.float64)
    t = x @ v
    z = x - t[:, None] * v[None, :]

    baseline = forward_final(weights, x)
    candidate_rows: list[np.ndarray] = []
    all_layer_inputs: list[list[int]] = []
    all_layer_outputs: list[list[int]] = []
    final_interval_counts: list[int] = []
    affine_flops: list[int] = []
    partition_all = True
    cap_overflow = False
    failure: str | None = None

    try:
        for i in range(OUTER_SAMPLES):
            res = conditional_mean_piecewise(weights, z[i], v, INTERVAL_CAP)
            candidate_rows.append(np.asarray(res["mean"], dtype=np.float64))
            all_layer_inputs.append([int(q) for q in res["layer_input_counts"]])
            all_layer_outputs.append([int(q) for q in res["layer_output_counts"]])
            final_interval_counts.append(int(res["final_interval_count"]))
            affine_flops.append(int(res["affine_matmul_flops_proxy"]))
            partition_all &= bool(res["partition_ok"])
    except OverflowError as exc:
        cap_overflow = True
        failure = str(exc)

    if cap_overflow:
        out = {
            "schema": "arc.whitebox.e110.smallwidth_law.v1",
            "experiment": "E110",
            "idempotency_key": "ARC-E110-DEEP-LINE-RB-20260919",
            "status": "TERMINAL_NO_GO_DROP",
            "failure": failure,
            "interval_cap_overflow": True,
            "scientific_go": False,
            "scope": {
                "small_width_synthetic_only": True,
                "public": False,
                "official_scorer": False,
                "holdout": False,
                "full_suite": False,
                "benchmark_targets": False,
                "tuning": False,
                "rerun": False,
            },
        }
        return out

    candidate = np.stack(candidate_rows, axis=0)

    law_abs_errors: list[float] = []
    law_rel_errors: list[float] = []
    for i in range(LAW_CHECK_SAMPLES):
        dense = dense_normal_integral(weights, z[i], v)
        exact = candidate[i]
        abs_err = float(np.max(np.abs(dense - exact)))
        denom = max(float(np.max(np.abs(exact))), 1e-12)
        law_abs_errors.append(abs_err)
        law_rel_errors.append(abs_err / denom)

    baseline_var = pooled_coordinate_variance(baseline)
    candidate_var = pooled_coordinate_variance(candidate)
    variance_ratio = candidate_var / baseline_var if baseline_var > 0.0 else math.inf
    relative_reduction = 1.0 - variance_ratio

    layer_inputs_np = np.asarray(all_layer_inputs, dtype=np.float64)
    layer_outputs_np = np.asarray(all_layer_outputs, dtype=np.float64)
    mean_interval_multiplier = float(np.mean(layer_inputs_np))
    max_layer_input_intervals = int(np.max(layer_inputs_np))
    max_final_intervals = int(np.max(final_interval_counts))
    mean_final_intervals = float(np.mean(final_interval_counts))
    mean_affine_flops = float(np.mean(affine_flops))

    cap_flops = PRODUCTION_UTIL_CAP * PRODUCTION_BUDGET
    optimistic_n_budget = math.floor(
        PRODUCTION_REFERENCE_TRAJECTORIES
        * cap_flops
        / (
            2.0
            * mean_interval_multiplier
            * PRODUCTION_REFERENCE_LAYER_FLOPS
        )
    )
    projected_risk = (
        candidate_var / optimistic_n_budget
        if optimistic_n_budget >= 1
        else math.inf
    )
    required_samples_target = math.ceil(candidate_var / TARGET_MSE)
    target_gap = projected_risk / TARGET_MSE if math.isfinite(projected_risk) else math.inf

    finite = bool(
        np.isfinite(baseline).all()
        and np.isfinite(candidate).all()
        and math.isfinite(baseline_var)
        and math.isfinite(candidate_var)
    )
    max_law_abs = max(law_abs_errors)
    max_law_rel = max(law_rel_errors)

    gates = {
        "direction_norm_finite_positive": math.isfinite(direction_norm)
        and direction_norm > 0.0,
        "outputs_finite": finite,
        "no_interval_cap_overflow": not cap_overflow,
        "partition_complete_ordered": partition_all,
        "independent_law_rel_le_2e_4": max_law_rel <= 2e-4,
        "candidate_variance_lt_baseline": candidate_var < baseline_var,
        "variance_ratio_le_0_80": variance_ratio <= 0.80,
        "optimistic_budget_samples_ge_1": optimistic_n_budget >= 1,
        "projected_budget_risk_le_1_89e_8": projected_risk <= TARGET_MSE,
    }
    go = bool(all(gates.values()))

    return {
        "schema": "arc.whitebox.e110.smallwidth_law.v1",
        "experiment": "E110",
        "idempotency_key": "ARC-E110-DEEP-LINE-RB-20260919",
        "status": (
            "SMALL_WIDTH_TARGET_FREE_PATH_GO"
            if go
            else "TERMINAL_NO_GO_DROP"
        ),
        "mechanism": "exact deep Gaussian-line Rao-Blackwellization by piecewise-affine breakpoint integration",
        "frozen_instance": {
            "width": WIDTH,
            "depth": DEPTH,
            "weight_seed": WEIGHT_SEED,
            "outer_seed": OUTER_SEED,
            "outer_samples": OUTER_SAMPLES,
            "law_check_samples": LAW_CHECK_SAMPLES,
            "dense_grid_points": GRID_POINTS,
            "dense_grid_limit": GRID_LIMIT,
            "interval_cap": INTERVAL_CAP,
        },
        "direction": {
            "rule": "mean-gate all-output deep sensitivity",
            "pre_normalization_norm": direction_norm,
            "unit_norm_error": abs(float(np.linalg.norm(v)) - 1.0),
        },
        "law_check": {
            "max_abs_error": max_law_abs,
            "max_relative_error": max_law_rel,
            "abs_errors": law_abs_errors,
            "relative_errors": law_rel_errors,
            "method": "independent dense trapezoidal N(0,1) integration over [-8,8]",
        },
        "risk": {
            "baseline_single_sample_pooled_variance": baseline_var,
            "conditional_single_sample_pooled_variance": candidate_var,
            "conditional_over_baseline": variance_ratio,
            "relative_variance_reduction": relative_reduction,
            "raw_target_mse_scale": TARGET_MSE,
            "samples_required_at_smallwidth_variance_for_target": required_samples_target,
        },
        "deep_piecewise_cost": {
            "layer_input_interval_counts_mean_by_layer": np.mean(
                layer_inputs_np, axis=0
            ).tolist(),
            "layer_output_interval_counts_mean_by_layer": np.mean(
                layer_outputs_np, axis=0
            ).tolist(),
            "mean_interval_multiplier": mean_interval_multiplier,
            "max_layer_input_intervals": max_layer_input_intervals,
            "mean_final_interval_count": mean_final_intervals,
            "max_final_interval_count": max_final_intervals,
            "mean_affine_matmul_flops_proxy_smallwidth": mean_affine_flops,
        },
        "production_path_diagnostic": {
            "production_budget": PRODUCTION_BUDGET,
            "utilization_cap": PRODUCTION_UTIL_CAP,
            "cap_flops": cap_flops,
            "reference_4096_layer_flops": PRODUCTION_REFERENCE_LAYER_FLOPS,
            "lower_bound_formula": "2 * measured_mean_interval_multiplier * reference_layer_flops * (N/4096); all non-layer costs omitted",
            "optimistic_conditioned_samples_under_cap": optimistic_n_budget,
            "projected_smallwidth_target_free_mse_at_optimistic_budget": projected_risk,
            "projected_over_target_scale": target_gap,
        },
        "gates": gates,
        "scientific_go": False,
        "decision": (
            "SMALL_WIDTH_TARGET_FREE_PATH_GO"
            if go
            else "TERMINAL_NO_GO_DROP"
        ),
        "scope": {
            "small_width_synthetic_only": True,
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


def main() -> None:
    out = run()
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E110_SMALLWIDTH_LAW=" + json.dumps(out, sort_keys=True), flush=True)
    if out["decision"] != "SMALL_WIDTH_TARGET_FREE_PATH_GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
