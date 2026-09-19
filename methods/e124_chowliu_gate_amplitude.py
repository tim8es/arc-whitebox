"""E124 exact small-width Chow-Liu gate-amplitude linked-cluster closure."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

import numpy as np

TWO_PI = 2.0 * math.pi
SECTOR_TOL = 1e-13
ROOT_TOL = 2.0 ** -40
PRODUCTION_FLOPS_UPPER = 143_078_584_832
BUDGET = 2**41


@dataclass(frozen=True)
class AngularSector:
    lo: float
    hi: float
    coeff: np.ndarray  # (width,2): h(theta)=coeff @ [cos,sin]


@dataclass(frozen=True)
class PenultimateStats:
    gate_prob: np.ndarray  # (n,)
    source_mean: np.ndarray  # full Gaussian mean (n,)
    pair_prob: np.ndarray  # (n,n,2,2)
    pair_cond_mean: np.ndarray  # (n,n,2,2,2), endpoint order i,k
    mutual_information: np.ndarray  # (n,n)
    tree_edges: tuple[tuple[int, int], ...]


def he_weights(seed: int, *, width: int, depth: int, input_dim: int = 2) -> list[np.ndarray]:
    if input_dim != 2:
        raise ValueError("E124 exact falsifier requires input_dim=2")
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
                    float(row[0]),
                    float(row[1]),
                    float(sector.lo),
                    float(sector.hi),
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
    mean_radius = math.sqrt(math.pi / 2.0)
    return mean_radius * angular / TWO_PI


def _gate_mask(sector: AngularSector) -> np.ndarray:
    mid = 0.5 * (sector.lo + sector.hi)
    q = np.asarray([math.cos(mid), math.sin(mid)], dtype=np.float64)
    values = sector.coeff @ q
    return values > 1e-14


def _binary_mi(p: np.ndarray) -> float:
    p = np.asarray(p, dtype=np.float64)
    pa = np.sum(p, axis=1)
    pb = np.sum(p, axis=0)
    value = 0.0
    for a in range(2):
        for b in range(2):
            x = float(p[a, b])
            denom = float(pa[a] * pb[b])
            if x > 0.0 and denom > 0.0:
                value += x * math.log(x / denom)
    return float(value)


def maximum_mi_tree(mi: np.ndarray) -> tuple[tuple[int, int], ...]:
    mat = np.asarray(mi, dtype=np.float64)
    if mat.ndim != 2 or mat.shape[0] != mat.shape[1]:
        raise ValueError("MI matrix must be square")
    n = int(mat.shape[0])
    if n == 1:
        return tuple()
    selected = {0}
    edges: list[tuple[int, int]] = []
    while len(selected) < n:
        best: tuple[float, int, int] | None = None
        for u in sorted(selected):
            for v in range(n):
                if v in selected:
                    continue
                score = float(mat[u, v])
                if best is None:
                    best = (score, u, v)
                else:
                    if score > best[0]:
                        best = (score, u, v)
                    elif score == best[0] and (u, v) < (best[1], best[2]):
                        best = (score, u, v)
        if best is None:
            raise RuntimeError("failed to construct spanning tree")
        _, u, v = best
        edges.append((min(u, v), max(u, v)))
        selected.add(v)
    return tuple(edges)


def penultimate_stats(sectors: Sequence[AngularSector]) -> PenultimateStats:
    if not sectors:
        raise ValueError("sectors must be non-empty")
    n = int(sectors[0].coeff.shape[0])
    gate_prob = np.zeros(n, dtype=np.float64)
    source_num = np.zeros(n, dtype=np.float64)
    pair_prob = np.zeros((n, n, 2, 2), dtype=np.float64)
    pair_source_num = np.zeros((n, n, 2, 2, 2), dtype=np.float64)
    mean_radius = math.sqrt(math.pi / 2.0)

    for sector in sectors:
        length_prob = float((sector.hi - sector.lo) / TWO_PI)
        mask = _gate_mask(sector)
        b1 = _basis_integral(sector.lo, sector.hi)
        # Full-Gaussian contribution E[R] * angular integral/(2*pi).
        h_num = mean_radius * (sector.coeff @ b1) / TWO_PI

        gate_prob += mask.astype(np.float64) * length_prob
        source_num += h_num

        for i in range(n):
            ai = 1 if mask[i] else 0
            for k in range(i + 1, n):
                bk = 1 if mask[k] else 0
                pair_prob[i, k, ai, bk] += length_prob
                pair_prob[k, i, bk, ai] += length_prob
                pair_source_num[i, k, ai, bk, 0] += h_num[i]
                pair_source_num[i, k, ai, bk, 1] += h_num[k]
                pair_source_num[k, i, bk, ai, 0] += h_num[k]
                pair_source_num[k, i, bk, ai, 1] += h_num[i]

    # Diagonal convenience law.
    for i in range(n):
        q = float(gate_prob[i])
        pair_prob[i, i, 0, 0] = 1.0 - q
        pair_prob[i, i, 1, 1] = q

    pair_cond = np.zeros_like(pair_source_num)
    for i in range(n):
        for k in range(n):
            if i == k:
                continue
            for a in range(2):
                for b in range(2):
                    p = float(pair_prob[i, k, a, b])
                    if p > 0.0:
                        pair_cond[i, k, a, b, :] = pair_source_num[i, k, a, b, :] / p

    mi = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for k in range(i + 1, n):
            value = _binary_mi(pair_prob[i, k])
            mi[i, k] = value
            mi[k, i] = value

    tree = maximum_mi_tree(mi)
    return PenultimateStats(
        gate_prob=gate_prob,
        source_mean=source_num,
        pair_prob=pair_prob,
        pair_cond_mean=pair_cond,
        mutual_information=mi,
        tree_edges=tree,
    )


def _relu(x: float) -> float:
    return x if x > 0.0 else 0.0


def linked_cluster_final_mean(
    stats: PenultimateStats,
    final_weight: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (independence-only, E124 tree-linked) final mean vectors."""
    w = np.asarray(final_weight, dtype=np.float64)
    n = int(stats.source_mean.shape[0])
    if w.shape != (n, n):
        raise ValueError(f"final weight must have shape ({n},{n})")

    m = np.asarray(stats.source_mean, dtype=np.float64)
    q = np.asarray(stats.gate_prob, dtype=np.float64)
    active_amp = np.zeros(n, dtype=np.float64)
    regular = q > 1e-15
    active_amp[regular] = m[regular] / q[regular]

    independent = np.zeros(n, dtype=np.float64)
    linked = np.zeros(n, dtype=np.float64)

    for j in range(n):
        weights_j = w[:, j]
        mu = float(m @ weights_j)
        base = _relu(mu)
        singles = np.zeros(n, dtype=np.float64)

        for i in range(n):
            wi = float(weights_j[i])
            e0 = _relu(mu + wi * (0.0 - float(m[i])))
            e1 = _relu(mu + wi * (float(active_amp[i]) - float(m[i])))
            singles[i] = (1.0 - float(q[i])) * e0 + float(q[i]) * e1

        c_ind = base + float(np.sum(singles - base))
        c_link = c_ind

        for i, k in stats.tree_edges:
            pair_e = 0.0
            for a in range(2):
                for b in range(2):
                    p = float(stats.pair_prob[i, k, a, b])
                    if p <= 0.0:
                        continue
                    mi_ab = float(stats.pair_cond_mean[i, k, a, b, 0])
                    mk_ab = float(stats.pair_cond_mean[i, k, a, b, 1])
                    shift = (
                        float(weights_j[i]) * (mi_ab - float(m[i]))
                        + float(weights_j[k]) * (mk_ab - float(m[k]))
                    )
                    pair_e += p * _relu(mu + shift)
            c_link += pair_e - float(singles[i]) - float(singles[k]) + base

        independent[j] = c_ind
        linked[j] = c_link

    return independent, linked


def stats_integrity(stats: PenultimateStats) -> dict:
    n = int(stats.gate_prob.shape[0])
    prob_range_ok = bool(
        np.all(stats.gate_prob >= -1e-14) and np.all(stats.gate_prob <= 1.0 + 1e-14)
    )
    pair_nonnegative = True
    pair_sum_error = 0.0
    pair_marginal_error = 0.0
    pair_mean_reconstruction_error = 0.0

    for i in range(n):
        for k in range(i + 1, n):
            p = np.asarray(stats.pair_prob[i, k], dtype=np.float64)
            pair_nonnegative &= bool(np.all(p >= -1e-14))
            pair_sum_error = max(pair_sum_error, abs(float(np.sum(p)) - 1.0))
            pair_marginal_error = max(
                pair_marginal_error,
                abs(float(np.sum(p[1, :])) - float(stats.gate_prob[i])),
                abs(float(np.sum(p[:, 1])) - float(stats.gate_prob[k])),
            )
            rec_i = 0.0
            rec_k = 0.0
            for a in range(2):
                for b in range(2):
                    rec_i += float(p[a, b]) * float(stats.pair_cond_mean[i, k, a, b, 0])
                    rec_k += float(p[a, b]) * float(stats.pair_cond_mean[i, k, a, b, 1])
            pair_mean_reconstruction_error = max(
                pair_mean_reconstruction_error,
                abs(rec_i - float(stats.source_mean[i])),
                abs(rec_k - float(stats.source_mean[k])),
            )

    # Tree connectivity/acyclicity.
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    acyclic = True
    for u, v in stats.tree_edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            acyclic = False
            break
        parent[rv] = ru
    connected = len({find(i) for i in range(n)}) == 1 if n else True

    marginal_reconstruction_error = 0.0
    for i in range(n):
        q = float(stats.gate_prob[i])
        active = float(stats.source_mean[i] / q) if q > 1e-15 else 0.0
        rec = q * active
        marginal_reconstruction_error = max(
            marginal_reconstruction_error, abs(rec - float(stats.source_mean[i]))
        )

    finite = bool(
        np.isfinite(stats.gate_prob).all()
        and np.isfinite(stats.source_mean).all()
        and np.isfinite(stats.pair_prob).all()
        and np.isfinite(stats.pair_cond_mean).all()
        and np.isfinite(stats.mutual_information).all()
    )

    return {
        "finite": finite,
        "gate_probability_range_ok": prob_range_ok,
        "pair_nonnegative": bool(pair_nonnegative),
        "pair_sum_max_abs_error": float(pair_sum_error),
        "pair_marginal_max_abs_error": float(pair_marginal_error),
        "marginal_mean_reconstruction_max_abs_error": float(marginal_reconstruction_error),
        "pair_mean_reconstruction_max_abs_error": float(pair_mean_reconstruction_error),
        "tree_edge_count": len(stats.tree_edges),
        "tree_connected": bool(connected),
        "tree_acyclic": bool(acyclic),
    }


def production_flop_proof() -> dict:
    n = 1024
    samples = 4096
    depth = 16
    per_layer = 2 * n * n + 2 * n
    prefix = samples * (depth - 1) * per_layer
    rng = 32 * samples * n
    gate_gram = 2 * samples * n * n
    marginal = 8 * samples * n
    mi = 64 * n * n
    mst = 32 * n * n
    edge_stats = 32 * samples * n
    cluster = 106 * n * n
    reserve = 5_000_000_000
    total = prefix + rng + gate_gram + marginal + mi + mst + edge_stats + cluster + reserve
    return {
        "width": n,
        "depth": depth,
        "samples": samples,
        "prefix_propagation": prefix,
        "input_rng_materialization": rng,
        "gate_cooccurrence": gate_gram,
        "marginal_reductions": marginal,
        "mutual_information": mi,
        "maximum_spanning_tree": mst,
        "edge_conditional_amplitude_stats": edge_stats,
        "final_linked_cluster": cluster,
        "helper_reserve": reserve,
        "total_upper_flops": total,
        "budget_flops": BUDGET,
        "utilization_upper": total / BUDGET,
        "cap": 0.13,
        "headroom_flops": 0.13 * BUDGET - total,
        "matches_frozen_protocol_upper": total == PRODUCTION_FLOPS_UPPER,
    }
