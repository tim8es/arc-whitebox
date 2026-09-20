"""E127 sparse higher-order hypergraph closure with certified tail."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

import numpy as np

TWO_PI = 2.0 * math.pi
SECTOR_TOL = 1e-13
ROOT_TOL = 2.0 ** -40
BUDGET = 2**41
UTIL_CAP = 0.13
PRODUCTION_WIDTH = 1024
PRODUCTION_DEPTH = 16
PRODUCTION_SAMPLES = 4096
PRODUCTION_CAP_FLOPS = int(UTIL_CAP * BUDGET)
PRODUCTION_BASELINE_FLOPS = 134_176_174_592
PRODUCTION_HEADROOM_FLOPS = PRODUCTION_CAP_FLOPS - PRODUCTION_BASELINE_FLOPS
PRODUCTION_CLUSTER_UNIT_FLOPS = 2 * PRODUCTION_SAMPLES * PRODUCTION_WIDTH
PRODUCTION_CLUSTER_UNITS = PRODUCTION_HEADROOM_FLOPS / PRODUCTION_CLUSTER_UNIT_FLOPS
PRODUCTION_CLUSTER_UNITS_PER_SOURCE = PRODUCTION_CLUSTER_UNITS / PRODUCTION_WIDTH
SMALL_WIDTH = 8
SMALL_CLUSTER_UNIT_CAP = math.floor(SMALL_WIDTH * PRODUCTION_CLUSTER_UNITS_PER_SOURCE)
OPTIMISTIC_PAIR_COUNT_CAP = SMALL_CLUSTER_UNIT_CAP // 3


@dataclass(frozen=True)
class AngularSector:
    lo: float
    hi: float
    coeff: np.ndarray


def he_weights(seed: int, *, width: int, depth: int, input_dim: int = 2) -> list[np.ndarray]:
    if input_dim != 2:
        raise ValueError("E127 exact falsifier requires input_dim=2")
    if width <= 0 or depth <= 0:
        raise ValueError("width/depth must be positive")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    out: list[np.ndarray] = []
    first = rng.standard_normal((input_dim, width)).astype(np.float64)
    first *= math.sqrt(2.0 / input_dim)
    out.append(first)
    for _ in range(1, depth):
        w = rng.standard_normal((width, width)).astype(np.float64)
        w *= math.sqrt(2.0 / width)
        out.append(w)
    return out


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
        if lo + SECTOR_TOL < root < hi - SECTOR_TOL:
            roots.append(float(root))
    return roots


def _dedup(values: Iterable[float], tol: float = ROOT_TOL) -> list[float]:
    out: list[float] = []
    for value in sorted(float(v) for v in values):
        if not out or abs(value - out[-1]) > tol:
            out.append(value)
    return out


def _basis_integral(lo: float, hi: float) -> np.ndarray:
    return np.asarray(
        [math.sin(hi) - math.sin(lo), -math.cos(hi) + math.cos(lo)],
        dtype=np.float64,
    )


def _positive_linear_integral(a: float, b: float, lo: float, hi: float) -> float:
    boundaries = _dedup([lo, hi, *_roots_in_interval(a, b, lo, hi)])
    total = 0.0
    for left, right in zip(boundaries[:-1], boundaries[1:]):
        if right - left <= SECTOR_TOL:
            continue
        mid = 0.5 * (left + right)
        if a * math.cos(mid) + b * math.sin(mid) > 0.0:
            basis = _basis_integral(left, right)
            total += a * float(basis[0]) + b * float(basis[1])
    return float(total)


def propagate_one_layer(
    sectors: Sequence[AngularSector], weight: np.ndarray
) -> tuple[AngularSector, ...]:
    w = np.asarray(weight, dtype=np.float64)
    nxt: list[AngularSector] = []
    for sector in sectors:
        pre = w.T @ sector.coeff
        boundaries = [sector.lo, sector.hi]
        for row in pre:
            boundaries.extend(
                _roots_in_interval(
                    float(row[0]), float(row[1]), float(sector.lo), float(sector.hi)
                )
            )
        boundaries = _dedup(boundaries)
        for lo, hi in zip(boundaries[:-1], boundaries[1:]):
            if hi - lo <= SECTOR_TOL:
                continue
            mid = 0.5 * (lo + hi)
            q = np.asarray([math.cos(mid), math.sin(mid)], dtype=np.float64)
            active = (pre @ q) > 0.0
            coeff = pre.copy()
            coeff[~active, :] = 0.0
            nxt.append(AngularSector(float(lo), float(hi), coeff))
    if not nxt:
        raise RuntimeError("empty angular partition")
    return tuple(nxt)


def enumerate_sectors(weights: Sequence[np.ndarray]) -> tuple[AngularSector, ...]:
    if not weights:
        raise ValueError("weights must be non-empty")
    sectors: tuple[AngularSector, ...] = (
        AngularSector(0.0, TWO_PI, np.eye(2, dtype=np.float64)),
    )
    previous = 2
    for idx, raw in enumerate(weights):
        w = np.asarray(raw, dtype=np.float64)
        if w.ndim != 2 or w.shape[0] != previous:
            raise ValueError(f"incompatible weight {idx} shape {w.shape}")
        if not np.isfinite(w).all():
            raise ValueError("non-finite weight")
        sectors = propagate_one_layer(sectors, w)
        previous = int(w.shape[1])
    return sectors


def partition_diagnostics(sectors: Sequence[AngularSector]) -> dict:
    if not sectors:
        return {"finite": False, "complete": False, "ordered": False, "max_gap": math.inf}
    finite = True
    ordered = True
    complete = abs(float(sectors[0].lo)) <= 1e-12
    max_gap = 0.0
    prev = float(sectors[0].lo)
    for sector in sectors:
        lo = float(sector.lo)
        hi = float(sector.hi)
        finite &= math.isfinite(lo) and math.isfinite(hi) and np.isfinite(sector.coeff).all()
        ordered &= hi > lo
        gap = abs(lo - prev)
        max_gap = max(max_gap, gap)
        complete &= gap <= 1e-11
        prev = hi
    complete &= abs(prev - TWO_PI) <= 1e-11
    return {
        "finite": bool(finite),
        "complete": bool(complete),
        "ordered": bool(ordered),
        "max_gap": float(max_gap),
    }


def exact_gaussian_mean(sectors: Sequence[AngularSector]) -> np.ndarray:
    if not sectors:
        raise ValueError("sectors must be non-empty")
    width = int(sectors[0].coeff.shape[0])
    angular = np.zeros(width, dtype=np.float64)
    for sector in sectors:
        angular += sector.coeff @ _basis_integral(sector.lo, sector.hi)
    return math.sqrt(math.pi / 2.0) * angular / TWO_PI


def mask_indices(mask: int, n: int) -> tuple[int, ...]:
    return tuple(i for i in range(n) if mask & (1 << i))


def all_nonempty_masks(n: int) -> range:
    return range(1, 1 << n)


def exact_subset_observables(
    sectors: Sequence[AngularSector], final_weight: np.ndarray
) -> np.ndarray:
    if not sectors:
        raise ValueError("sectors must be non-empty")
    w = np.asarray(final_weight, dtype=np.float64)
    n = int(sectors[0].coeff.shape[0])
    if w.shape != (n, n):
        raise ValueError(f"final weight must have shape ({n},{n})")
    out = np.zeros((1 << n, n), dtype=np.float64)
    radial = math.sqrt(math.pi / 2.0) / TWO_PI
    for mask in all_nonempty_masks(n):
        idx = mask_indices(mask, n)
        ix = np.asarray(idx)
        acc = np.zeros(n, dtype=np.float64)
        for sector in sectors:
            pre = w[ix, :].T @ sector.coeff[ix, :]
            for j in range(n):
                acc[j] += _positive_linear_integral(
                    float(pre[j, 0]), float(pre[j, 1]), sector.lo, sector.hi
                )
        out[mask, :] = radial * acc
    return out


def mobius_clusters(subset_values: np.ndarray) -> np.ndarray:
    values = np.asarray(subset_values, dtype=np.float64)
    if values.ndim != 2:
        raise ValueError("subset_values must have shape (2^n, outputs)")
    m = int(values.shape[0])
    if m <= 0 or m & (m - 1):
        raise ValueError("first dimension must be a power of two")
    n = m.bit_length() - 1
    delta = values.copy()
    for bit in range(n):
        flag = 1 << bit
        for mask in range(m):
            if mask & flag:
                delta[mask, :] -= delta[mask ^ flag, :]
    return delta


def cluster_bounds(source_mean: np.ndarray, final_weight: np.ndarray) -> np.ndarray:
    m = np.asarray(source_mean, dtype=np.float64)
    w = np.asarray(final_weight, dtype=np.float64)
    n = int(m.shape[0])
    if w.shape != (n, n):
        raise ValueError(f"final weight must have shape ({n},{n})")
    out = np.zeros((1 << n, n), dtype=np.float64)
    abs_contrib = np.abs(w) * m[:, None]
    for mask in all_nonempty_masks(n):
        idx = mask_indices(mask, n)
        k = len(idx)
        out[mask, :] = (2.0 ** (k - 1)) * np.min(abs_contrib[np.asarray(idx), :], axis=0)
    return out


def envelope_diagnostics(delta: np.ndarray, bounds: np.ndarray) -> dict:
    excess = np.abs(delta) - bounds
    return {
        "max_excess": float(np.max(excess[1:, :])),
        "max_abs_cluster": float(np.max(np.abs(delta[1:, :]))),
        "max_bound": float(np.max(bounds[1:, :])),
        "pass_le_1e_12": bool(np.max(excess[1:, :]) <= 1e-12),
    }


def order_frontier(delta: np.ndarray, bounds: np.ndarray, rms_target: float) -> list[dict]:
    n = int(math.log2(delta.shape[0]))
    records: list[dict] = []
    for r in range(1, n + 1):
        selected = [mask for mask in all_nonempty_masks(n) if mask.bit_count() <= r]
        omitted = [mask for mask in all_nonempty_masks(n) if mask.bit_count() > r]
        candidate = (
            np.sum(delta[np.asarray(selected), :], axis=0)
            if selected
            else np.zeros(delta.shape[1])
        )
        tail = (
            np.sum(bounds[np.asarray(omitted), :], axis=0)
            if omitted
            else np.zeros(delta.shape[1])
        )
        cert_rms = float(np.sqrt(np.mean(tail * tail)))
        records.append(
            {
                "order": r,
                "selected_cluster_count": len(selected),
                "omitted_cluster_count": len(omitted),
                "certificate_rms": cert_rms,
                "certificate_pass": cert_rms <= rms_target,
                "candidate": candidate,
            }
        )
    return records


def rank_higher_clusters(bounds: np.ndarray) -> list[int]:
    n = int(math.log2(bounds.shape[0]))
    masks = [mask for mask in all_nonempty_masks(n) if mask.bit_count() >= 2]
    return sorted(
        masks,
        key=lambda mask: (
            -float(np.mean(bounds[mask, :])),
            mask.bit_count(),
            mask_indices(mask, n),
        ),
    )


def optimistic_required_cluster_count(bounds: np.ndarray, rms_target: float) -> dict:
    ranked = rank_higher_clusters(bounds)
    scores = [float(np.mean(bounds[mask, :])) for mask in ranked]
    remaining = float(sum(scores))
    kept = 0
    for score in scores:
        if remaining <= rms_target:
            break
        remaining -= score
        kept += 1
    return {
        "necessary_retained_non_singletons": kept,
        "optimistic_remaining_mean_tail": max(0.0, remaining),
        "higher_cluster_count": len(ranked),
        "optimistic_pair_count_cap": OPTIMISTIC_PAIR_COUNT_CAP,
        "passes_count_cap": kept <= OPTIMISTIC_PAIR_COUNT_CAP,
    }


def _all_nonempty_submasks(mask: int) -> list[int]:
    out: list[int] = []
    sub = mask
    while sub:
        out.append(sub)
        sub = (sub - 1) & mask
    return out


def sparse_family(bounds: np.ndarray, unit_cap: int = SMALL_CLUSTER_UNIT_CAP) -> dict:
    n = int(math.log2(bounds.shape[0]))
    selected = {1 << i for i in range(n)}
    units = 0
    for mask in rank_higher_clusters(bounds):
        closure = set(_all_nonempty_submasks(mask))
        missing = sorted(
            (m for m in closure if m not in selected and m.bit_count() >= 2),
            key=lambda m: (m.bit_count(), mask_indices(m, n)),
        )
        add_units = sum(m.bit_count() + 1 for m in missing)
        if units + add_units <= unit_cap:
            selected.update(closure)
            units += add_units
    selected_sorted = sorted(selected)
    omitted = [mask for mask in all_nonempty_masks(n) if mask not in selected]
    tail = (
        np.sum(bounds[np.asarray(omitted), :], axis=0)
        if omitted
        else np.zeros(bounds.shape[1])
    )
    return {
        "selected_masks": selected_sorted,
        "selected_non_singletons": [m for m in selected_sorted if m.bit_count() >= 2],
        "omitted_masks": omitted,
        "cluster_units": units,
        "unit_cap": unit_cap,
        "certificate_tail": tail,
        "certificate_rms": float(np.sqrt(np.mean(tail * tail))),
    }


def is_downward_closed(selected_masks: Sequence[int], n: int) -> bool:
    selected = set(int(x) for x in selected_masks)
    for mask in selected:
        sub = mask
        while sub:
            if sub not in selected:
                return False
            sub = (sub - 1) & mask
    return all((1 << i) in selected for i in range(n))


def production_flop_proof() -> dict:
    n = PRODUCTION_WIDTH
    samples = PRODUCTION_SAMPLES
    depth = PRODUCTION_DEPTH
    prefix = samples * (depth - 1) * (2 * n * n + 2 * n)
    rng = 32 * samples * n
    means = 8 * samples * n
    abs_stats = 8 * samples * n
    reserve = 5_000_000_000
    baseline = prefix + rng + means + abs_stats + reserve
    full_order = {}
    cumulative = 0
    for r in range(2, 9):
        count = math.comb(n, r)
        cost = count * 2 * samples * n * (r + 1)
        cumulative += cost
        total = baseline + cumulative
        full_order[str(r)] = {
            "new_order_cluster_count": count,
            "cumulative_cluster_work": cumulative,
            "total_upper_flops": total,
            "utilization_upper": total / BUDGET,
            "passes_cap": total <= PRODUCTION_CAP_FLOPS,
        }
    return {
        "width": n,
        "depth": depth,
        "samples": samples,
        "budget_flops": BUDGET,
        "utilization_cap": UTIL_CAP,
        "integer_cap_flops": PRODUCTION_CAP_FLOPS,
        "prefix_propagation": prefix,
        "input_rng_materialization": rng,
        "penultimate_mean_reductions": means,
        "absolute_source_stat_reductions": abs_stats,
        "helper_reserve": reserve,
        "baseline_total": baseline,
        "headroom_flops": PRODUCTION_CAP_FLOPS - baseline,
        "cluster_unit_flops": PRODUCTION_CLUSTER_UNIT_FLOPS,
        "cluster_units_total": PRODUCTION_CLUSTER_UNITS,
        "cluster_units_per_source": PRODUCTION_CLUSTER_UNITS_PER_SOURCE,
        "small_width_homologous_unit_cap": SMALL_CLUSTER_UNIT_CAP,
        "optimistic_pair_count_cap": OPTIMISTIC_PAIR_COUNT_CAP,
        "matches_frozen_baseline": baseline == PRODUCTION_BASELINE_FLOPS,
        "full_order": full_order,
    }
