"""Physical scalar activation-boundary state compression for E118."""

from __future__ import annotations

from dataclasses import dataclass
import heapq
import math

import numpy as np

_TWO_PI = 2.0 * math.pi
_MEAN_RADIUS_2D = math.sqrt(math.pi / 2.0)


@dataclass(frozen=True)
class State:
    layer: int
    lo: float
    hi: float
    coeff: np.ndarray


def make_network(seed: int, width: int = 8, depth: int = 4) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    weights = [
        np.asarray(rng.standard_normal((width, 2)), dtype=np.float64)
        * math.sqrt(2.0 / 2.0)
    ]
    scale = math.sqrt(2.0 / float(width))
    for _ in range(1, depth):
        weights.append(
            np.asarray(rng.standard_normal((width, width)), dtype=np.float64) * scale
        )
    return weights


def _roots(a: float, b: float, lo: float, hi: float) -> list[float]:
    if math.hypot(a, b) <= 1e-15:
        return []
    delta = math.atan2(b, a)
    base = delta + 0.5 * math.pi
    k0 = math.ceil((lo - base) / math.pi - 1e-13)
    k1 = math.floor((hi - base) / math.pi + 1e-13)
    out: list[float] = []
    for k in range(k0, k1 + 1):
        x = base + k * math.pi
        if lo + 1e-12 < x < hi - 1e-12:
            out.append(x)
    return out


def _dedup(xs: list[float]) -> list[float]:
    out: list[float] = []
    for x in sorted(xs):
        if not out or abs(x - out[-1]) > 1e-11:
            out.append(x)
    return out


def expand_state(state: State, weight: np.ndarray) -> tuple[list[State], dict]:
    pre = np.asarray(weight, dtype=np.float64) @ np.asarray(state.coeff, dtype=np.float64)
    boundaries = [state.lo, state.hi]
    root_checks = 0
    roots_materialized = 0
    for row in pre:
        root_checks += 1
        roots = _roots(float(row[0]), float(row[1]), state.lo, state.hi)
        roots_materialized += len(roots)
        boundaries.extend(roots)
    boundaries = _dedup(boundaries)

    children: list[State] = []
    for lo, hi in zip(boundaries[:-1], boundaries[1:]):
        if hi - lo <= 1e-13:
            continue
        mid = 0.5 * (lo + hi)
        q = np.array([math.cos(mid), math.sin(mid)], dtype=np.float64)
        coeff = pre.copy()
        coeff[(pre @ q) <= 0.0, :] = 0.0
        children.append(State(state.layer + 1, lo, hi, coeff))

    return children, {
        "root_checks": root_checks,
        "roots_materialized": roots_materialized,
        "children_materialized": len(children),
        "child_coefficient_bytes": int(sum(x.coeff.nbytes for x in children)),
    }


def _sector_q_integral(lo: float, hi: float) -> np.ndarray:
    return np.array(
        [math.sin(hi) - math.sin(lo), -math.cos(hi) + math.cos(lo)],
        dtype=np.float64,
    )


def scalar_coeff(state: State, width: int) -> np.ndarray:
    c = np.ones(width, dtype=np.float64) / math.sqrt(float(width))
    return c @ state.coeff


def final_sector_contribution(state: State, width: int) -> float:
    a = scalar_coeff(state, width)
    return float(
        _MEAN_RADIUS_2D
        / _TWO_PI
        * (a @ _sector_q_integral(state.lo, state.hi))
    )


def full_exact_reference(weights: list[np.ndarray]) -> dict:
    states = [State(0, 0.0, _TWO_PI, np.eye(2, dtype=np.float64))]
    root_checks = 0
    roots_materialized = 0
    child_states = 0
    coeff_bytes = int(states[0].coeff.nbytes)
    layer_counts = [1]

    for weight in weights:
        next_states: list[State] = []
        for state in states:
            children, ledger = expand_state(state, weight)
            next_states.extend(children)
            root_checks += ledger["root_checks"]
            roots_materialized += ledger["roots_materialized"]
            child_states += ledger["children_materialized"]
            coeff_bytes += ledger["child_coefficient_bytes"]
        states = next_states
        layer_counts.append(len(states))

    states = sorted(states, key=lambda s: (s.lo, s.hi))
    width = int(weights[-1].shape[0])
    sector_mean = float(sum(final_sector_contribution(s, width) for s in states))

    angular_sector_integral = 0.0
    coeffs: list[np.ndarray] = []
    for state in states:
        a = scalar_coeff(state, width)
        coeffs.append(a)
        angular_sector_integral += float(
            a @ _sector_q_integral(state.lo, state.hi)
        )

    jump_sum = 0.0
    for idx, state in enumerate(states):
        right = coeffs[idx]
        left = coeffs[idx - 1]
        theta = state.lo
        tangent = np.array([-math.sin(theta), math.cos(theta)], dtype=np.float64)
        jump_sum += float((right - left) @ tangent)

    flux_mean = _MEAN_RADIUS_2D / _TWO_PI * jump_sum
    return {
        "mean": sector_mean,
        "flux_mean": float(flux_mean),
        "angular_sector_integral": float(angular_sector_integral),
        "boundary_jump_sum": float(jump_sum),
        "flux_sector_abs_diff": float(abs(flux_mean - sector_mean)),
        "final_interval_count": len(states),
        "layer_state_counts": layer_counts,
        "root_checks": root_checks,
        "roots_materialized": roots_materialized,
        "child_states_materialized": child_states,
        "coefficient_bytes_materialized": coeff_bytes,
    }


def suffix_frobenius_products(weights: list[np.ndarray]) -> list[float]:
    depth = len(weights)
    out = [1.0] * (depth + 1)
    product = 1.0
    for idx in range(depth - 1, -1, -1):
        product *= float(np.linalg.norm(weights[idx], ord="fro"))
        out[idx] = product
    return out


def unresolved_bound(state: State, suffix_fro: list[float]) -> float:
    envelope = float(np.linalg.norm(state.coeff, ord="fro")) * suffix_fro[state.layer]
    return float(
        _MEAN_RADIUS_2D / _TWO_PI * (state.hi - state.lo) * envelope
    )


def compressed_physical_estimate(
    weights: list[np.ndarray], *, expansion_cap: int
) -> dict:
    width = int(weights[-1].shape[0])
    suffix = suffix_frobenius_products(weights)
    root = State(0, 0.0, _TWO_PI, np.eye(2, dtype=np.float64))

    counter = 0
    heap: list[tuple[float, int, State]] = [
        (-unresolved_bound(root, suffix), counter, root)
    ]
    estimate = 0.0
    expansions = 0
    resolved_final_states = 0
    child_states_materialized = 0
    root_checks = 0
    roots_materialized = 0
    coefficient_bytes_materialized = int(root.coeff.nbytes)
    max_live_queue = 1
    expansions_by_layer = [0] * len(weights)
    materialized_by_layer = [1] + [0] * len(weights)

    while heap and expansions < expansion_cap:
        _, _, state = heapq.heappop(heap)
        children, ledger = expand_state(state, weights[state.layer])
        expansions += 1
        expansions_by_layer[state.layer] += 1
        child_states_materialized += ledger["children_materialized"]
        root_checks += ledger["root_checks"]
        roots_materialized += ledger["roots_materialized"]
        coefficient_bytes_materialized += ledger["child_coefficient_bytes"]

        for child in children:
            materialized_by_layer[child.layer] += 1
            if child.layer == len(weights):
                estimate += final_sector_contribution(child, width)
                resolved_final_states += 1
            else:
                counter += 1
                bound = unresolved_bound(child, suffix)
                heapq.heappush(heap, (-bound, counter, child))
        max_live_queue = max(max_live_queue, len(heap))

    unresolved = [item[2] for item in heap]
    remainder = float(sum(unresolved_bound(s, suffix) for s in unresolved))
    live_coefficient_bytes = int(sum(s.coeff.nbytes for s in unresolved))

    return {
        "estimate": float(estimate),
        "remainder_certificate": remainder,
        "expansions": expansions,
        "expansions_by_layer": expansions_by_layer,
        "resolved_final_states": resolved_final_states,
        "unresolved_state_count": len(unresolved),
        "max_live_queue": max_live_queue,
        "child_states_materialized": child_states_materialized,
        "materialized_by_layer": materialized_by_layer,
        "root_checks": root_checks,
        "roots_materialized": roots_materialized,
        "coefficient_bytes_materialized": coefficient_bytes_materialized,
        "live_coefficient_bytes_at_stop": live_coefficient_bytes,
        "queue_exhausted": len(unresolved) == 0,
    }
