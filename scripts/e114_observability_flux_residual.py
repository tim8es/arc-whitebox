from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

INPUT_DIM = 2
WIDTH = 8
DEPTH = 4
WEIGHT_SEED = 114214
RANK = 2
REFERENCE_N = 4096
TARGET_MSE = 1.89e-8
TWO_PI = 2.0 * math.pi
ROOT_TOL = 1e-13
MERGE_TOL = 1e-12

OUT = Path("e114-support-falsifier.json")


@dataclass
class Segment:
    lo: float
    hi: float
    coeff: np.ndarray


def make_weights(
    input_dim: int, width: int, depth: int, seed: int
) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    weights: list[np.ndarray] = []
    fan_in = input_dim
    for layer in range(depth):
        fan_out = width
        scale = math.sqrt(2.0 / fan_in)
        w = rng.standard_normal((fan_in, fan_out)).astype(np.float64) * scale
        weights.append(w)
        fan_in = fan_out
    return weights


def forward(weights: list[np.ndarray], x: np.ndarray) -> np.ndarray:
    h = np.asarray(x, dtype=np.float64)
    for w in weights:
        h = np.maximum(h @ w, 0.0)
    return h


def qvec(theta: float) -> np.ndarray:
    return np.array([math.cos(theta), math.sin(theta)], dtype=np.float64)


def tangent(theta: float) -> np.ndarray:
    return np.array([-math.sin(theta), math.cos(theta)], dtype=np.float64)


def _unique_sorted(values: list[float], tol: float = ROOT_TOL) -> list[float]:
    if not values:
        return []
    xs = sorted(values)
    out = [xs[0]]
    for x in xs[1:]:
        if abs(x - out[-1]) > tol * (1.0 + abs(x) + abs(out[-1])):
            out.append(x)
    return out


def roots_on_circle(a: float, b: float) -> tuple[float, float] | None:
    if abs(a) + abs(b) <= 1e-15:
        return None
    phi = math.atan2(b, a)
    base = (phi + 0.5 * math.pi) % math.pi
    return base, base + math.pi


def partition_ok(segments: list[Segment]) -> bool:
    if not segments:
        return False
    if abs(segments[0].lo) > 1e-14:
        return False
    if abs(segments[-1].hi - TWO_PI) > 1e-14:
        return False
    for seg in segments:
        if not (seg.lo < seg.hi):
            return False
        if not np.isfinite(seg.coeff).all():
            return False
    for left, right in zip(segments[:-1], segments[1:]):
        if abs(left.hi - right.lo) > 1e-14:
            return False
    return True


def merge_adjacent(segments: list[Segment]) -> list[Segment]:
    if not segments:
        return []
    merged: list[Segment] = [segments[0]]
    for seg in segments[1:]:
        prev = merged[-1]
        if (
            abs(prev.hi - seg.lo) <= 1e-14
            and np.allclose(
                prev.coeff,
                seg.coeff,
                rtol=MERGE_TOL,
                atol=MERGE_TOL,
            )
        ):
            merged[-1] = Segment(prev.lo, seg.hi, prev.coeff)
        else:
            merged.append(seg)
    return merged


def propagate_angular_partition(
    weights: list[np.ndarray],
) -> tuple[list[Segment], list[int]]:
    segments = [
        Segment(
            0.0,
            TWO_PI,
            np.eye(INPUT_DIM, dtype=np.float64),
        )
    ]
    counts: list[int] = []

    for w in weights:
        next_segments: list[Segment] = []
        for seg in segments:
            pre_coeff = seg.coeff @ w
            roots: list[float] = []
            for j in range(pre_coeff.shape[1]):
                pair = roots_on_circle(
                    float(pre_coeff[0, j]),
                    float(pre_coeff[1, j]),
                )
                if pair is None:
                    continue
                for root in pair:
                    if seg.lo + ROOT_TOL < root < seg.hi - ROOT_TOL:
                        roots.append(root)

            bounds = [seg.lo, *_unique_sorted(roots), seg.hi]
            for lo, hi in zip(bounds[:-1], bounds[1:]):
                mid = 0.5 * (lo + hi)
                mask = (qvec(mid) @ pre_coeff) > 0.0
                coeff = pre_coeff * mask[None, :]
                next_segments.append(Segment(lo, hi, coeff))

        segments = merge_adjacent(next_segments)
        if not partition_ok(segments):
            raise RuntimeError("angular partition lost coverage/order")
        counts.append(len(segments))

    return segments, counts


def coeff_at(segments: list[Segment], theta: float) -> np.ndarray:
    t = theta % TWO_PI
    if abs(t - TWO_PI) <= 1e-14:
        t = 0.0
    for i, seg in enumerate(segments):
        if seg.lo <= t < seg.hi:
            return seg.coeff
        if i == len(segments) - 1 and abs(t - seg.hi) <= 1e-14:
            return segments[0].coeff
    raise RuntimeError(f"theta not covered: {theta}")


def angular_first_moment(lo: float, hi: float) -> np.ndarray:
    return np.array(
        [
            math.sin(hi) - math.sin(lo),
            -math.cos(hi) + math.cos(lo),
        ],
        dtype=np.float64,
    )


def angular_second_moment(lo: float, hi: float) -> np.ndarray:
    span = hi - lo
    s2 = math.sin(2.0 * hi) - math.sin(2.0 * lo)
    cc = 0.5 * span + 0.25 * s2
    ss = 0.5 * span - 0.25 * s2
    cs = 0.5 * (
        math.sin(hi) * math.sin(hi)
        - math.sin(lo) * math.sin(lo)
    )
    return np.array([[cc, cs], [cs, ss]], dtype=np.float64)


def sector_angular_integral(segments: list[Segment]) -> np.ndarray:
    out = np.zeros(segments[0].coeff.shape[1], dtype=np.float64)
    for seg in segments:
        out += angular_first_moment(seg.lo, seg.hi) @ seg.coeff
    return out


def derivative_jump_rows(
    segments: list[Segment],
) -> tuple[np.ndarray, np.ndarray]:
    angles: list[float] = []
    jumps: list[np.ndarray] = []

    # Cyclic boundary at zero.
    delta0 = tangent(0.0) @ (segments[0].coeff - segments[-1].coeff)
    if float(np.linalg.norm(delta0)) > 1e-12:
        angles.append(0.0)
        jumps.append(delta0)

    for left, right in zip(segments[:-1], segments[1:]):
        theta = right.lo
        delta = tangent(theta) @ (right.coeff - left.coeff)
        if float(np.linalg.norm(delta)) > 1e-12:
            angles.append(theta)
            jumps.append(delta)

    if not jumps:
        return (
            np.zeros((0,), dtype=np.float64),
            np.zeros((0, segments[0].coeff.shape[1]), dtype=np.float64),
        )
    return np.asarray(angles, dtype=np.float64), np.stack(jumps, axis=0)


def chi_mean_2d() -> float:
    return math.sqrt(math.pi / 2.0)


def boundary_flux_gaussian_mean(segments: list[Segment]) -> dict[str, object]:
    angles, jumps = derivative_jump_rows(segments)
    jump_sum = (
        np.sum(jumps, axis=0)
        if jumps.shape[0]
        else np.zeros(segments[0].coeff.shape[1], dtype=np.float64)
    )
    sector_integral = sector_angular_integral(segments)
    scale = chi_mean_2d() / TWO_PI
    return {
        "angles": angles,
        "jumps": jumps,
        "jump_sum": jump_sum,
        "sector_integral": sector_integral,
        "flux_mean": scale * jump_sum,
        "sector_mean": scale * sector_integral,
    }


def _pair_boundaries(segments: list[Segment]) -> list[float]:
    vals = [0.0, TWO_PI]
    raw = [seg.lo for seg in segments[1:]]
    vals.extend(raw)
    for theta in raw:
        vals.append((theta - math.pi) % TWO_PI)
    vals.extend(
        [
            (0.0 - math.pi) % TWO_PI,
        ]
    )
    vals = [0.0 if abs(v - TWO_PI) <= 1e-14 else v for v in vals]
    vals = _unique_sorted(vals, tol=1e-12)
    vals = [v for v in vals if 0.0 <= v < TWO_PI]
    vals = _unique_sorted(vals, tol=1e-12)
    if not vals or abs(vals[0]) > 1e-14:
        vals = [0.0, *vals]
    if abs(vals[-1] - TWO_PI) > 1e-14:
        vals.append(TWO_PI)
    return vals


def exact_radial_rb_moments(
    segments: list[Segment],
) -> dict[str, np.ndarray | int]:
    width = segments[0].coeff.shape[1]
    mu_r = chi_mean_2d()
    bounds = _pair_boundaries(segments)

    first = np.zeros(width, dtype=np.float64)
    second = np.zeros((width, width), dtype=np.float64)

    for lo, hi in zip(bounds[:-1], bounds[1:]):
        mid = 0.5 * (lo + hi)
        a_plus = coeff_at(segments, mid)
        a_minus_region = coeff_at(segments, mid + math.pi)

        # F(-q) = -q^T A_minus_region.
        pair_coeff = 0.5 * mu_r * (a_plus - a_minus_region)

        first += angular_first_moment(lo, hi) @ pair_coeff
        second += pair_coeff.T @ angular_second_moment(lo, hi) @ pair_coeff

    mean = first / TWO_PI
    second = second / TWO_PI
    covariance = second - np.outer(mean, mean)
    covariance = 0.5 * (covariance + covariance.T)

    return {
        "mean": mean,
        "second": second,
        "covariance": covariance,
        "pair_interval_count": len(bounds) - 1,
    }


def observability_projector(
    weights: list[np.ndarray], rank: int
) -> dict[str, object]:
    width = weights[-1].shape[1]
    dmap = np.eye(width, dtype=np.float64)
    gram = dmap.T @ dmap

    for w in reversed(weights):
        dmap = 0.5 * (w @ dmap)
        gram += dmap.T @ dmap

    gram = 0.5 * (gram + gram.T)
    evals, evecs = np.linalg.eigh(gram)
    order = np.argsort(evals)[::-1]
    evals_desc = evals[order]
    u = evecs[:, order[:rank]]
    projector = u @ u.T
    residual = np.eye(width, dtype=np.float64) - projector

    lambda_r = float(evals_desc[rank - 1])
    lambda_next = float(evals_desc[rank])
    rel_gap = (lambda_r - lambda_next) / max(lambda_r, 1e-300)

    return {
        "gram": gram,
        "eigenvalues_desc": evals_desc,
        "u": u,
        "projector": projector,
        "residual": residual,
        "relative_eigengap": rel_gap,
        "symmetry_error": float(np.max(np.abs(projector - projector.T))),
        "idempotence_error": float(
            np.max(np.abs(projector @ projector - projector))
        ),
    }


def sha256_array(x: np.ndarray) -> str:
    return hashlib.sha256(
        np.ascontiguousarray(x, dtype=np.float64).tobytes()
    ).hexdigest()


def run_once() -> dict[str, object]:
    weights = make_weights(INPUT_DIM, WIDTH, DEPTH, WEIGHT_SEED)
    segments, layer_counts = propagate_angular_partition(weights)
    flux = boundary_flux_gaussian_mean(segments)
    rb = exact_radial_rb_moments(segments)
    obs = observability_projector(weights, RANK)

    flux_mean = np.asarray(flux["flux_mean"], dtype=np.float64)
    sector_mean = np.asarray(flux["sector_mean"], dtype=np.float64)
    rb_mean = np.asarray(rb["mean"], dtype=np.float64)
    covariance = np.asarray(rb["covariance"], dtype=np.float64)

    projector = np.asarray(obs["projector"], dtype=np.float64)
    residual = np.asarray(obs["residual"], dtype=np.float64)

    residual_cov = residual @ covariance @ residual
    residual_cov = 0.5 * (residual_cov + residual_cov.T)

    base_var = float(np.mean(np.diag(covariance)))
    residual_var = float(np.mean(np.diag(residual_cov)))
    ratio = residual_var / base_var if base_var > 0.0 else math.inf

    base_risk_4096 = base_var / REFERENCE_N
    residual_risk_4096 = residual_var / REFERENCE_N

    mean_flux_sector_err = float(np.max(np.abs(flux_mean - sector_mean)))
    mean_rb_flux_err = float(np.max(np.abs(rb_mean - flux_mean)))

    jumps = np.asarray(flux["jumps"], dtype=np.float64)
    finite = bool(
        all(np.isfinite(w).all() for w in weights)
        and all(np.isfinite(seg.coeff).all() for seg in segments)
        and np.isfinite(jumps).all()
        and np.isfinite(covariance).all()
        and np.isfinite(projector).all()
        and math.isfinite(base_var)
        and math.isfinite(residual_var)
    )

    gates = {
        "all_finite": finite,
        "partition_complete": partition_ok(segments),
        "boundary_flux_vs_sector_mean_le_1e_11": mean_flux_sector_err <= 1e-11,
        "paired_mean_vs_boundary_flux_le_1e_11": mean_rb_flux_err <= 1e-11,
        "projector_symmetry_le_1e_11": float(obs["symmetry_error"]) <= 1e-11,
        "projector_idempotence_le_1e_11": float(obs["idempotence_error"]) <= 1e-11,
        "relative_eigengap_ge_1e_6": float(obs["relative_eigengap"]) >= 1e-6,
        "residual_variance_lt_baseline": residual_var < base_var,
        "residual_over_baseline_le_0_50": ratio <= 0.50,
        "residual_risk_4096_le_1_89e_8": residual_risk_4096 <= TARGET_MSE,
    }

    payload = {
        "schema": "arc.whitebox.e114.observable_flux_support.v1",
        "experiment": "E114",
        "idempotency_key": "ARC-E114-OBSERVABILITY-FLUX-RESIDUAL-SUPPORT-20260919",
        "mechanism": "weight-only observability subspace + exact boundary-flux analytic backbone + sampled orthogonal residual",
        "frozen_instance": {
            "input_dimension": INPUT_DIM,
            "width": WIDTH,
            "depth": DEPTH,
            "weight_seed": WEIGHT_SEED,
            "compression_rank": RANK,
            "reference_sample_count": REFERENCE_N,
        },
        "partition": {
            "layer_region_counts": layer_counts,
            "final_region_count": len(segments),
            "nonzero_boundary_count": int(jumps.shape[0]),
            "paired_interval_count": int(rb["pair_interval_count"]),
        },
        "observability": {
            "eigenvalues_desc": np.asarray(
                obs["eigenvalues_desc"], dtype=np.float64
            ).tolist(),
            "relative_eigengap": float(obs["relative_eigengap"]),
            "projector_symmetry_error": float(obs["symmetry_error"]),
            "projector_idempotence_error": float(obs["idempotence_error"]),
            "projector_sha256": sha256_array(projector),
        },
        "exact_mean_checks": {
            "boundary_flux_vs_sector_max_abs": mean_flux_sector_err,
            "paired_radial_rb_vs_boundary_flux_max_abs": mean_rb_flux_err,
            "gaussian_mean_sha256": sha256_array(flux_mean),
        },
        "exact_target_free_variance": {
            "baseline_pooled_variance": base_var,
            "residual_pooled_variance": residual_var,
            "residual_over_baseline": ratio,
            "relative_variance_reduction": 1.0 - ratio,
            "baseline_risk_at_4096": base_risk_4096,
            "residual_risk_at_4096": residual_risk_4096,
            "raw_target_scale": TARGET_MSE,
            "residual_risk_over_target_scale": residual_risk_4096 / TARGET_MSE,
        },
        "stability": {
            "stochastic_denominator": False,
            "covariance_or_variance_division": False,
            "target_fitted_coefficients": False,
            "gaussian_relu_plugin": False,
            "full_mask_state_table": False,
            "projector_operator_norm_bound": 1.0,
        },
        "gates": gates,
        "scientific_go": False,
        "scope": {
            "exact_small_network_only": True,
            "monte_carlo_scientific_reference": False,
            "numerical_quadrature_scientific_reference": False,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "target_fitting": False,
            "gaussian_relu_plugin": False,
            "full_mask_state_table": False,
            "tuning": False,
            "sweep": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }
    return payload


def main() -> None:
    first = run_once()
    second = run_once()
    deterministic = first == second
    first["gates"]["deterministic_exact_replay"] = deterministic
    all_gates = bool(all(first["gates"].values()))
    first["decision"] = (
        "E114_OBSERVABLE_STRUCTURE_SUPPORT_GO"
        if all_gates
        else "TERMINAL_SUPPORT_NO_GO"
    )
    first["status"] = first["decision"]

    OUT.write_text(
        json.dumps(first, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "E114_SUPPORT_FALSIFIER=" + json.dumps(first, sort_keys=True),
        flush=True,
    )
    if not all_gates:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
