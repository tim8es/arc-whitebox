"""Independent exact small-width verifier helpers for E110 Householder orbit."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Sequence

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

TAU = 2.0 * math.pi
HALF_PI = 0.5 * math.pi


@dataclass(frozen=True)
class Sector:
    lo: float
    hi: float
    linear_map: np.ndarray


def direct_forward_vector(weights: Sequence[np.ndarray], q: np.ndarray) -> np.ndarray:
    h = np.asarray(q, dtype=np.float64)
    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        h = h @ w.T
        h = np.maximum(h, 0.0)
    return np.asarray(h, dtype=np.float64)


def direct_forward_angle(weights: Sequence[np.ndarray], theta: float) -> np.ndarray:
    q = np.asarray([math.cos(theta), math.sin(theta)], dtype=np.float64)
    return direct_forward_vector(weights, q)


def _roots_of_linear_form(c: np.ndarray, lo: float, hi: float) -> list[float]:
    a = float(c[0])
    b = float(c[1])
    if math.hypot(a, b) <= 1e-14:
        return []
    base = math.atan2(b, a) + HALF_PI
    out: list[float] = []
    for k in range(-4, 5):
        root = base + k * math.pi
        if lo + 1e-12 < root < hi - 1e-12:
            out.append(root)
    return out


def _unique_sorted(values: list[float], tol: float = 1e-12) -> list[float]:
    out: list[float] = []
    for value in sorted(values):
        if not out or abs(value - out[-1]) > tol:
            out.append(value)
    return out


def enumerate_relu_sectors(weights: Sequence[np.ndarray]) -> list[Sector]:
    if not weights:
        raise ValueError("weights must be non-empty")
    for raw_w in weights:
        if np.asarray(raw_w).shape != (2, 2):
            raise ValueError("exact verifier requires width=2 square weights")

    sectors = [Sector(0.0, TAU, np.eye(2, dtype=np.float64))]
    for raw_w in weights:
        w = np.asarray(raw_w, dtype=np.float64)
        nxt: list[Sector] = []
        for sector in sectors:
            pre_map = sector.linear_map @ w.T
            cuts = [sector.lo, sector.hi]
            for j in range(2):
                cuts.extend(_roots_of_linear_form(pre_map[:, j], sector.lo, sector.hi))
            cuts = _unique_sorted(cuts)
            for lo, hi in zip(cuts[:-1], cuts[1:]):
                if hi - lo <= 1e-13:
                    continue
                mid = 0.5 * (lo + hi)
                q = np.asarray([math.cos(mid), math.sin(mid)], dtype=np.float64)
                mask = (q @ pre_map) > 0.0
                nxt.append(Sector(lo, hi, pre_map * mask[None, :]))
        sectors = nxt
    return sectors


def validate_sector_partition(weights: Sequence[np.ndarray], sectors: Sequence[Sector]) -> float:
    max_abs = 0.0
    for sector in sectors:
        for frac in (0.21132486540518713, 0.5, 0.7886751345948129):
            theta = sector.lo + frac * (sector.hi - sector.lo)
            q = np.asarray([math.cos(theta), math.sin(theta)], dtype=np.float64)
            represented = q @ sector.linear_map
            direct = direct_forward_vector(weights, q)
            max_abs = max(max_abs, float(np.max(np.abs(represented - direct))))
    return max_abs


def _find_sector(sectors: Sequence[Sector], theta: float) -> Sector:
    x = theta % TAU
    for sector in sectors:
        if sector.lo - 1e-11 <= x <= sector.hi + 1e-11:
            return sector
    raise RuntimeError(f"angle {x} is not covered")


def direct_block_value(weights: Sequence[np.ndarray], theta: float) -> np.ndarray:
    values = [direct_forward_angle(weights, theta + k * HALF_PI) for k in range(4)]
    return np.mean(np.stack(values, axis=0), axis=0)


def block_partition(sectors: Sequence[Sector]) -> list[tuple[float, float, np.ndarray]]:
    cuts = [0.0, HALF_PI]
    for sector in sectors:
        for boundary in (sector.lo, sector.hi):
            if boundary <= 1e-12 or boundary >= TAU - 1e-12:
                continue
            for k in range(4):
                shifted = boundary - k * HALF_PI
                if 1e-12 < shifted < HALF_PI - 1e-12:
                    cuts.append(shifted)
    cuts = _unique_sorted(cuts)

    pieces: list[tuple[float, float, np.ndarray]] = []
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        if hi - lo <= 1e-13:
            continue
        mid = 0.5 * (lo + hi)
        coeff = np.zeros((2, 2), dtype=np.float64)
        for k in range(4):
            delta = k * HALF_PI
            sector = _find_sector(sectors, mid + delta)
            c = sector.linear_map
            cd = math.cos(delta)
            sd = math.sin(delta)
            coeff[0, :] += c[0, :] * cd + c[1, :] * sd
            coeff[1, :] += -c[0, :] * sd + c[1, :] * cd
        pieces.append((lo, hi, 0.25 * coeff))
    return pieces


def validate_block_partition(
    weights: Sequence[np.ndarray],
    pieces: Sequence[tuple[float, float, np.ndarray]],
) -> float:
    max_abs = 0.0
    for lo, hi, coeff in pieces:
        for frac in (0.25, 0.5, 0.75):
            theta = lo + frac * (hi - lo)
            q = np.asarray([math.cos(theta), math.sin(theta)], dtype=np.float64)
            represented = q @ coeff
            direct = direct_block_value(weights, theta)
            max_abs = max(max_abs, float(np.max(np.abs(represented - direct))))
    return max_abs


def deep_sensitivity(weights: Sequence[np.ndarray]) -> np.ndarray:
    n = int(np.asarray(weights[0]).shape[0])
    g = np.ones(n, dtype=np.float64) / math.sqrt(float(n))
    for raw_w in reversed(weights):
        g = 0.5 * np.asarray(raw_w, dtype=np.float64).T @ g
    norm = float(np.linalg.norm(g))
    if not math.isfinite(norm) or norm <= 1e-14:
        raise ValueError("non-finite or zero deep sensitivity norm")
    v = g / norm
    idx = int(np.argmax(np.abs(v)))
    if v[idx] < 0.0:
        v = -v
    return v


def householder(v: np.ndarray) -> np.ndarray:
    u = np.asarray(v, dtype=np.float64)
    return np.eye(u.size, dtype=np.float64) - 2.0 * np.outer(u, u)


def _integral_linear(a: float, b: float, lo: float, hi: float) -> float:
    return a * (math.sin(hi) - math.sin(lo)) + b * (math.cos(lo) - math.cos(hi))


def _integral_product(
    a: float,
    b: float,
    c: float,
    d: float,
    lo: float,
    hi: float,
) -> float:
    ic2 = 0.5 * (hi - lo) + 0.25 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    is2 = 0.5 * (hi - lo) - 0.25 * (math.sin(2.0 * hi) - math.sin(2.0 * lo))
    isc = 0.5 * (math.sin(hi) ** 2 - math.sin(lo) ** 2)
    return a * c * ic2 + b * d * is2 + (a * d + b * c) * isc


def full_sphere_mean(sectors: Sequence[Sector]) -> np.ndarray:
    out = np.zeros(2, dtype=np.float64)
    for sector in sectors:
        for j in range(2):
            a = float(sector.linear_map[0, j])
            b = float(sector.linear_map[1, j])
            out[j] += _integral_linear(a, b, sector.lo, sector.hi)
    return out / TAU


def _find_block_piece(
    pieces: Sequence[tuple[float, float, np.ndarray]],
    theta: float,
) -> tuple[float, float, np.ndarray]:
    x = theta % HALF_PI
    if abs(x - HALF_PI) <= 1e-14:
        x = 0.0
    for piece in pieces:
        if piece[0] - 1e-11 <= x <= piece[1] + 1e-11:
            return piece
    raise RuntimeError(f"block angle {x} is not covered")


def common_householder_partition(
    pieces: Sequence[tuple[float, float, np.ndarray]],
    v: np.ndarray,
) -> list[tuple[float, float, np.ndarray, np.ndarray]]:
    alpha = math.atan2(float(v[1]), float(v[0]))
    c = 2.0 * alpha
    cuts = [0.0, HALF_PI]

    for lo, hi, _ in pieces:
        for boundary in (lo, hi):
            if 1e-12 < boundary < HALF_PI - 1e-12:
                cuts.append(boundary)
            mapped = (c - boundary) % HALF_PI
            if 1e-12 < mapped < HALF_PI - 1e-12:
                cuts.append(mapped)
    cuts = _unique_sorted(cuts)

    out: list[tuple[float, float, np.ndarray, np.ndarray]] = []
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        if hi - lo <= 1e-13:
            continue
        mid = 0.5 * (lo + hi)
        _, _, original = _find_block_piece(pieces, mid)

        raw = c - mid
        k = math.floor(raw / HALF_PI)
        phi = raw - k * HALF_PI
        _, _, reflected_base = _find_block_piece(pieces, phi)
        d = c - k * HALF_PI

        cd = math.cos(d)
        sd = math.sin(d)
        reflected = np.empty_like(reflected_base)
        reflected[0, :] = reflected_base[0, :] * cd + reflected_base[1, :] * sd
        reflected[1, :] = reflected_base[0, :] * sd - reflected_base[1, :] * cd

        out.append((lo, hi, original.copy(), reflected))
    return out


def direct_reflected_block_value(
    weights: Sequence[np.ndarray],
    reflection: np.ndarray,
    theta: float,
) -> np.ndarray:
    q1 = np.asarray([math.cos(theta), math.sin(theta)], dtype=np.float64)
    q2 = np.asarray([-math.sin(theta), math.cos(theta)], dtype=np.float64)
    rows = [q1 @ reflection, q2 @ reflection]
    values = []
    for row in rows:
        values.append(direct_forward_vector(weights, row))
    for row in rows:
        values.append(direct_forward_vector(weights, -row))
    return np.mean(np.stack(values, axis=0), axis=0)


def validate_reflected_partition(
    weights: Sequence[np.ndarray],
    reflection: np.ndarray,
    common: Sequence[tuple[float, float, np.ndarray, np.ndarray]],
) -> float:
    max_abs = 0.0
    for lo, hi, _, reflected in common:
        for frac in (0.25, 0.5, 0.75):
            theta = lo + frac * (hi - lo)
            q = np.asarray([math.cos(theta), math.sin(theta)], dtype=np.float64)
            represented = q @ reflected
            direct = direct_reflected_block_value(weights, reflection, theta)
            max_abs = max(max_abs, float(np.max(np.abs(represented - direct))))
    return max_abs


def exact_householder_stats(weights: Sequence[np.ndarray]) -> dict:
    sectors = enumerate_relu_sectors(weights)
    pieces = block_partition(sectors)
    v = deep_sensitivity(weights)
    reflection = householder(v)
    common = common_householder_partition(pieces, v)

    sphere_mean = full_sphere_mean(sectors)
    mean_chi_2 = math.sqrt(math.pi / 2.0)
    gaussian_reference_mean = mean_chi_2 * sphere_mean

    outputs = []
    for j in range(2):
        i_b = 0.0
        i_r = 0.0
        i_b2 = 0.0
        i_r2 = 0.0
        i_br = 0.0
        for lo, hi, original, reflected in common:
            a, b = (float(original[0, j]), float(original[1, j]))
            c, d = (float(reflected[0, j]), float(reflected[1, j]))
            i_b += _integral_linear(a, b, lo, hi)
            i_r += _integral_linear(c, d, lo, hi)
            i_b2 += _integral_product(a, b, a, b, lo, hi)
            i_r2 += _integral_product(c, d, c, d, lo, hi)
            i_br += _integral_product(a, b, c, d, lo, hi)

        mean_b = i_b / HALF_PI
        mean_r = i_r / HALF_PI
        var_b = i_b2 / HALF_PI - mean_b * mean_b
        var_r = i_r2 / HALF_PI - mean_r * mean_r
        cov_br = i_br / HALF_PI - mean_b * mean_r

        for name, value in (("var_b", var_b), ("var_r", var_r)):
            if value < -1e-12:
                raise RuntimeError(f"negative exact variance {name}={value}")
        var_b = max(0.0, var_b)
        var_r = max(0.0, var_r)

        baseline_var = 0.5 * var_b
        candidate_var = 0.25 * (var_b + var_r + 2.0 * cov_br)
        if candidate_var < 0.0 and candidate_var > -1e-12:
            candidate_var = 0.0
        candidate_mean = 0.5 * (mean_b + mean_r)

        scale2 = mean_chi_2 * mean_chi_2
        baseline_var_gaussian = scale2 * baseline_var
        candidate_var_gaussian = scale2 * candidate_var
        ratio = (
            candidate_var_gaussian / baseline_var_gaussian
            if baseline_var_gaussian > 1e-18
            else None
        )
        outputs.append(
            {
                "output": j,
                "sphere_reference_mean": float(sphere_mean[j]),
                "gaussian_reference_mean": float(gaussian_reference_mean[j]),
                "block_mean": mean_b,
                "reflected_block_mean": mean_r,
                "candidate_gaussian_mean": mean_chi_2 * candidate_mean,
                "candidate_gaussian_mean_abs_error": abs(
                    mean_chi_2 * candidate_mean - gaussian_reference_mean[j]
                ),
                "reflected_marginal_mean_abs_error": abs(mean_r - mean_b),
                "block_variance": var_b,
                "reflected_block_variance": var_r,
                "block_reflection_covariance": cov_br,
                "independent_two_block_variance_gaussian": baseline_var_gaussian,
                "householder_coupled_variance_gaussian": candidate_var_gaussian,
                "variance_ratio": ratio,
                "nondegenerate": bool(baseline_var_gaussian > 1e-18),
            }
        )

    baseline_sum = sum(row["independent_two_block_variance_gaussian"] for row in outputs)
    candidate_sum = sum(row["householder_coupled_variance_gaussian"] for row in outputs)
    pooled_ratio = candidate_sum / baseline_sum if baseline_sum > 0.0 else math.inf

    return {
        "sector_count": len(sectors),
        "block_piece_count": len(pieces),
        "common_piece_count": len(common),
        "sensitivity_v": v.tolist(),
        "reflection": reflection.tolist(),
        "householder_orthogonality_max_abs": float(
            np.max(np.abs(reflection.T @ reflection - np.eye(2)))
        ),
        "sector_validation_max_abs": validate_sector_partition(weights, sectors),
        "block_validation_max_abs": validate_block_partition(weights, pieces),
        "reflected_validation_max_abs": validate_reflected_partition(weights, reflection, common),
        "mean_chi_2": mean_chi_2,
        "outputs": outputs,
        "pooled_independent_variance_gaussian": baseline_sum,
        "pooled_householder_variance_gaussian": candidate_sum,
        "pooled_variance_ratio": pooled_ratio,
        "max_candidate_mean_abs_error": max(
            row["candidate_gaussian_mean_abs_error"] for row in outputs
        ),
        "max_reflected_marginal_mean_abs_error": max(
            row["reflected_marginal_mean_abs_error"] for row in outputs
        ),
        "nondegenerate_outputs": sum(bool(row["nondegenerate"]) for row in outputs),
    }


def _billed_haar_basis(rng, n: int):
    g = rng.standard_normal((n, n))
    q, r = fnp.linalg.qr(g)
    signs = fnp.where(fnp.diag(r) < 0.0, -1.0, 1.0)
    return fnp.multiply(q, signs[None, :])


def _billed_forward(weights: Sequence[np.ndarray], h, checkpoints: list[int], ctx) -> object:
    for raw_w in weights:
        w = fnp.asarray(raw_w, dtype=fnp.float64)
        h = fnp.matmul(h, fnp.swapaxes(w, 0, 1))
        h = fnp.maximum(h, fnp.float64(0.0))
        checkpoints.append(int(ctx.flops_used))
    return h


def _digest(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def billed_householder_estimator(
    weights: Sequence[np.ndarray],
    seed: int,
    budget: int = 10**8,
) -> dict:
    n = int(np.asarray(weights[0]).shape[0])
    radius = math.sqrt(math.pi / 2.0)
    with flops.BudgetContext(flop_budget=budget, quiet=True) as ctx:
        start = int(ctx.flops_used)

        g = fnp.asarray(np.ones(n, dtype=np.float64) / math.sqrt(float(n)))
        for raw_w in reversed(weights):
            w = fnp.asarray(raw_w, dtype=fnp.float64)
            g = fnp.matmul(fnp.swapaxes(w, 0, 1), g)
            g = fnp.multiply(g, 0.5)
        norm = fnp.sqrt(fnp.sum(fnp.multiply(g, g)))
        v = g / norm
        vv = fnp.multiply(fnp.reshape(v, (n, 1)), fnp.reshape(v, (1, n)))
        reflection = fnp.asarray(np.eye(n, dtype=np.float64)) - fnp.multiply(vv, 2.0)
        after_direction = int(ctx.flops_used)

        rng = fnp.random.default_rng(int(seed))
        q = _billed_haar_basis(rng, n)
        qr = fnp.matmul(q, reflection)
        pos = fnp.concatenate((q, qr), axis=0)
        pos = fnp.multiply(pos, radius)
        inputs = fnp.concatenate((pos, -pos), axis=0)
        after_input = int(ctx.flops_used)

        layer_cumulative: list[int] = []
        h = _billed_forward(weights, inputs, layer_cumulative, ctx)
        prediction = fnp.mean(h, axis=0, dtype=fnp.float64)
        after_reduction = int(ctx.flops_used)

    out = np.asarray(prediction, dtype=np.float64).copy()
    inp = np.asarray(inputs, dtype=np.float64).copy()
    v_np = np.asarray(v, dtype=np.float64).copy()
    r_np = np.asarray(reflection, dtype=np.float64).copy()

    layer_flops = []
    previous = after_input
    for current in layer_cumulative:
        layer_flops.append(current - previous)
        previous = current
    ledger = {
        "direction_and_reflection": after_direction - start,
        "input_construction": after_input - after_direction,
        "layers": layer_flops,
        "layer_total": int(sum(layer_flops)),
        "reduction": after_reduction - previous,
        "total": after_reduction - start,
    }
    ledger["reconciled_sum"] = (
        ledger["direction_and_reflection"]
        + ledger["input_construction"]
        + ledger["layer_total"]
        + ledger["reduction"]
    )
    ledger["exact_reconciliation"] = ledger["reconciled_sum"] == ledger["total"]

    half = inp.shape[0] // 2
    return {
        "prediction": out,
        "prediction_sha256": _digest(out),
        "sensitivity_v": v_np,
        "reflection": r_np,
        "antithetic_pair_max_abs": float(np.max(np.abs(inp[:half] + inp[half:]))),
        "finite": bool(np.isfinite(out).all() and np.isfinite(v_np).all() and np.isfinite(r_np).all()),
        "flops": ledger,
    }


def billed_independent_baseline(
    weights: Sequence[np.ndarray],
    seed_a: int,
    seed_b: int,
    budget: int = 10**8,
) -> dict:
    n = int(np.asarray(weights[0]).shape[0])
    radius = math.sqrt(math.pi / 2.0)
    with flops.BudgetContext(flop_budget=budget, quiet=True) as ctx:
        start = int(ctx.flops_used)
        q1 = _billed_haar_basis(fnp.random.default_rng(int(seed_a)), n)
        q2 = _billed_haar_basis(fnp.random.default_rng(int(seed_b)), n)
        pos = fnp.concatenate((q1, q2), axis=0)
        pos = fnp.multiply(pos, radius)
        inputs = fnp.concatenate((pos, -pos), axis=0)
        after_input = int(ctx.flops_used)

        layer_cumulative: list[int] = []
        h = _billed_forward(weights, inputs, layer_cumulative, ctx)
        prediction = fnp.mean(h, axis=0, dtype=fnp.float64)
        after_reduction = int(ctx.flops_used)

    out = np.asarray(prediction, dtype=np.float64).copy()
    inp = np.asarray(inputs, dtype=np.float64).copy()

    layer_flops = []
    previous = after_input
    for current in layer_cumulative:
        layer_flops.append(current - previous)
        previous = current
    ledger = {
        "input_construction": after_input - start,
        "layers": layer_flops,
        "layer_total": int(sum(layer_flops)),
        "reduction": after_reduction - previous,
        "total": after_reduction - start,
    }
    ledger["reconciled_sum"] = ledger["input_construction"] + ledger["layer_total"] + ledger["reduction"]
    ledger["exact_reconciliation"] = ledger["reconciled_sum"] == ledger["total"]

    half = inp.shape[0] // 2
    return {
        "prediction": out,
        "prediction_sha256": _digest(out),
        "antithetic_pair_max_abs": float(np.max(np.abs(inp[:half] + inp[half:]))),
        "finite": bool(np.isfinite(out).all()),
        "flops": ledger,
    }
