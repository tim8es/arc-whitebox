"""E132 layer-born source-age D21 Hermite estimator.

Target-free candidate. Exact references are forbidden here.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


PROD_N = 1024
PROD_DEPTH = 16
PROD_PILOT = 256
PROD_EVAL = 2048
PROD_RY = 32
PROD_RS = 48
PROD_RN = 24
PROD_CAP = 136_758_472_261
RAW_MSE_TARGET = 1.89e-8


@dataclass(frozen=True)
class Factor:
    q: np.ndarray
    c: np.ndarray


@dataclass
class AgeState:
    y0: Factor | None = None
    y1: Factor | None = None
    qs: np.ndarray | None = None
    shared: dict[int, np.ndarray] | None = None
    rn: np.ndarray | None = None
    cold: np.ndarray | None = None


@dataclass(frozen=True)
class E132Estimate:
    mean: np.ndarray
    baseline_mean: np.ndarray
    d21_correction: np.ndarray
    certificate_mse: float
    birth_identity_max_abs: float
    nested_path_exercised: bool
    finite: bool
    ledger: dict
    diagnostics: dict


def ranks_for_width(n: int) -> tuple[int, int, int]:
    if n <= 0:
        raise ValueError("width must be positive")
    ry = max(1, math.ceil(n / 32))
    rs = max(1, math.ceil(3 * n / 64))
    rn = max(1, math.ceil(3 * n / 128))
    return min(n, ry), min(n, rs), min(n, rn)


def _canon_qr(y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    q, r = np.linalg.qr(np.asarray(y, dtype=np.float64), mode="reduced")
    for j in range(q.shape[1]):
        idx = int(np.argmax(np.abs(q[:, j])))
        if q[idx, j] < 0.0:
            q[:, j] *= -1.0
            r[j, :] *= -1.0
    return q, r


def _omega(rows: int, cols: int, seed: int) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    raw = rng.integers(0, 2, size=(rows, cols), dtype=np.int8)
    return (2.0 * raw.astype(np.float64) - 1.0) / math.sqrt(float(cols))


def _compress_matrix(a: np.ndarray, rank: int, seed: int) -> Factor:
    a = np.asarray(a, dtype=np.float64)
    r = min(int(rank), a.shape[0], a.shape[1])
    if r <= 0:
        raise ValueError("rank must be positive")
    y = a @ _omega(a.shape[1], r, seed)
    q, _ = _canon_qr(y)
    q = q[:, :r]
    c = q.T @ a
    return Factor(q=q, c=c)


def _materialize_factor(f: Factor | None, n: int) -> np.ndarray:
    if f is None:
        return np.zeros((n, n), dtype=np.float64)
    return f.q @ f.c


def _transport_factor(f: Factor | None, w: np.ndarray) -> Factor | None:
    if f is None:
        return None
    a = np.asarray(w, dtype=np.float64)
    left = (a * a).T @ f.q
    right = f.c @ a
    q, r = _canon_qr(left)
    return Factor(q=q, c=r @ right)


def _state_matrix(state: AgeState, n: int) -> np.ndarray:
    out = np.zeros((n, n), dtype=np.float64)
    if state.y0 is not None:
        out += state.y0.q @ state.y0.c
    if state.y1 is not None:
        out += state.y1.q @ state.y1.c
    if state.qs is not None and state.shared:
        csum = np.zeros((state.qs.shape[1], n), dtype=np.float64)
        for c in state.shared.values():
            csum += c
        if state.rn is not None and state.cold is not None:
            csum += state.rn @ state.cold
        out += state.qs @ csum
    return out


def _compress_nested(
    old_coeff: np.ndarray,
    rank: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    old_coeff = np.asarray(old_coeff, dtype=np.float64)
    r = min(rank, old_coeff.shape[0], old_coeff.shape[1])
    y = old_coeff @ _omega(old_coeff.shape[1], r, seed)
    q, _ = _canon_qr(y)
    q = q[:, :r]
    return q, q.T @ old_coeff


def _rebase_shared(
    components: dict[int, np.ndarray],
    old_matrix: np.ndarray | None,
    rank_s: int,
    rank_n: int,
    seed: int,
) -> tuple[np.ndarray | None, dict[int, np.ndarray], np.ndarray | None, np.ndarray | None]:
    mats = [np.asarray(m, dtype=np.float64) for m in components.values()]
    if old_matrix is not None:
        mats.append(np.asarray(old_matrix, dtype=np.float64))
    if not mats:
        return None, {}, None, None

    aggregate = np.zeros_like(mats[0])
    for m in mats:
        aggregate += m

    qs = _compress_matrix(aggregate, rank_s, seed).q
    shared: dict[int, np.ndarray] = {}
    for age, mat in sorted(components.items()):
        shared[int(age)] = qs.T @ mat

    rn = None
    cold = None
    if old_matrix is not None:
        old_coeff = qs.T @ old_matrix
        rn, cold = _compress_nested(old_coeff, rank_n, seed + 17)

    return qs, shared, rn, cold


def _transport_and_age(
    state: AgeState,
    w: np.ndarray,
    *,
    rank_s: int,
    rank_n: int,
    layer: int,
) -> AgeState:
    n = int(w.shape[1])
    new_y1 = _transport_factor(state.y0, w)
    age2_factor = _transport_factor(state.y1, w)

    components: dict[int, np.ndarray] = {}
    if age2_factor is not None:
        components[2] = age2_factor.q @ age2_factor.c

    old_matrix = None
    if state.qs is not None and state.shared:
        qst = (w * w).T @ state.qs
        qnew, rtri = _canon_qr(qst)

        for age, c in sorted(state.shared.items()):
            moved = qnew @ (rtri @ (c @ w))
            next_age = int(age) + 1
            if next_age <= 4:
                components[next_age] = moved
            else:
                old_matrix = moved if old_matrix is None else old_matrix + moved

        if state.rn is not None and state.cold is not None:
            moved_old = qnew @ (
                rtri @ state.rn @ (state.cold @ w)
            )
            old_matrix = (
                moved_old
                if old_matrix is None
                else old_matrix + moved_old
            )

    qs, shared, rn, cold = _rebase_shared(
        components,
        old_matrix,
        rank_s,
        rank_n,
        seed=132_000_000 + 1000 * layer + 31,
    )
    return AgeState(
        y0=None,
        y1=new_y1,
        qs=qs,
        shared=shared,
        rn=rn,
        cold=cold,
    )


def _empirical_d21(h: np.ndarray) -> np.ndarray:
    x = np.asarray(h, dtype=np.float64)
    centered = x - np.mean(x, axis=0, dtype=np.float64)
    return (centered * centered).T @ centered / float(x.shape[0])


def _propagate(x: np.ndarray, weights: Sequence[np.ndarray]) -> np.ndarray:
    h = np.asarray(x, dtype=np.float64)
    for w in weights:
        h = h @ np.asarray(w, dtype=np.float64)
        h = np.maximum(h, 0.0)
    return h


def _lipschitz_output_bounds(weights: Sequence[np.ndarray]) -> np.ndarray:
    if len(weights) < 1:
        raise ValueError("weights required")
    prod = 1.0
    for w in weights[:-1]:
        a = np.asarray(w, dtype=np.float64)
        one = float(np.max(np.sum(np.abs(a), axis=0)))
        inf = float(np.max(np.sum(np.abs(a), axis=1)))
        prod *= math.sqrt(one * inf)
    last = np.asarray(weights[-1], dtype=np.float64)
    return prod * np.linalg.norm(last, axis=0)


def _cost_formula(n: int, depth: int, pilot: int, evaluation: int) -> dict:
    ry, rs, rn = ranks_for_width(n)
    hidden = depth - 1
    per_layer = 2 * n * n + 2 * n

    rng = 32 * (pilot + evaluation) * n
    propagation = (pilot * hidden + evaluation * depth) * per_layer
    d21_stats = hidden * (2 * pilot * n * n + 12 * pilot * n)

    source_transport = hidden * (
        8 * n * n * ry
        + 8 * n * n * rs
        + 2 * n * n * rn
        + 4 * n * rs * rn
    )
    birth_compress = hidden * (
        4 * n * n * ry + 4 * n * ry * ry + 8 * ry**3
    )
    shared_rebase = hidden * (
        4 * n * n * rs
        + 4 * n * (rs + ry) ** 2
        + 8 * (rs + ry) ** 3
        + 4 * n * rs * ry
    )
    nested_rebase = hidden * (
        4 * n * rs * rn + 4 * rs * rn * rn + 8 * rn**3
    )
    state_reconstruction = hidden * (
        4 * n * n * ry + 2 * n * n * rs + 4 * n * rs * rn
    )

    direction_normalization = 6 * n * n
    direction_gram = 2 * n**3
    eval_input_projection = 2 * evaluation * n * n
    effective_rank = 2 * ry + 3 * rs + rn
    lowrank_d21_apply = 4 * evaluation * n * effective_rank
    final_d21_reconstruct = 2 * n * n * effective_rank
    rowwise_rho = 3 * n * n
    final_correction = 2 * evaluation * n * n + 8 * evaluation * n
    certificate = 16 * depth * n * n + 8 * n * n
    final_reductions = 8 * evaluation * n
    helper_reserve = 2_000_000_000 if n == PROD_N and depth == PROD_DEPTH else 0

    parts = {
        "rng_materialization_upper": int(rng),
        "network_propagation_upper": int(propagation),
        "pilot_d21_stats_upper": int(d21_stats),
        "source_age_transport_upper": int(source_transport),
        "birth_compression_upper": int(birth_compress),
        "shared_rebase_upper": int(shared_rebase),
        "nested_rebase_upper": int(nested_rebase),
        "state_reconstruction_upper": int(state_reconstruction),
        "direction_normalization_upper": int(direction_normalization),
        "direction_gram_upper": int(direction_gram),
        "evaluation_input_projection_upper": int(eval_input_projection),
        "lowrank_d21_apply_upper": int(lowrank_d21_apply),
        "final_d21_reconstruct_upper": int(final_d21_reconstruct),
        "rowwise_rho_upper": int(rowwise_rho),
        "final_correction_upper": int(final_correction),
        "certificate_upper": int(certificate),
        "final_reductions_upper": int(final_reductions),
        "helper_reserve": int(helper_reserve),
    }
    total = int(sum(parts.values()))
    return {
        "width": int(n),
        "depth": int(depth),
        "pilot": int(pilot),
        "evaluation": int(evaluation),
        "r_y": int(ry),
        "r_s": int(rs),
        "r_n": int(rn),
        "effective_rank_count": int(effective_rank),
        **parts,
        "all_in_upper": total,
    }


def production_cost_receipt() -> dict:
    out = _cost_formula(PROD_N, PROD_DEPTH, PROD_PILOT, PROD_EVAL)
    out.update(
        {
            "hard_cap_flops": PROD_CAP,
            "slack_flops": int(PROD_CAP - out["all_in_upper"]),
            "passes_cap": bool(out["all_in_upper"] <= PROD_CAP),
        }
    )
    return out


def layer_born_d21_estimate(
    weights: Sequence[np.ndarray],
    *,
    pilot: int,
    evaluation: int,
    seed: int,
) -> E132Estimate:
    if len(weights) < 6:
        raise ValueError("E132 needs depth >=6 to exercise nested source age")
    first = np.asarray(weights[0], dtype=np.float64)
    if first.ndim != 2:
        raise ValueError("weights must be matrices")
    d = int(first.shape[0])
    n = int(first.shape[1])
    prev = n
    for idx, raw in enumerate(weights[1:], start=1):
        w = np.asarray(raw, dtype=np.float64)
        if w.ndim != 2 or w.shape[0] != prev:
            raise ValueError(f"incompatible weight {idx}")
        prev = int(w.shape[1])
    if prev != n:
        raise ValueError("E132 frozen estimator expects constant hidden/output width")
    if pilot <= 0 or evaluation <= 0:
        raise ValueError("pilot/evaluation must be positive")

    ry, rs, rn = ranks_for_width(n)
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    x_pilot = rng.standard_normal((pilot, d)).astype(np.float64)
    x_eval = rng.standard_normal((evaluation, d)).astype(np.float64)

    state = AgeState(shared={})
    h = x_pilot
    birth_identity_max = 0.0
    nested_exercised = False
    layer_diag = []

    for layer, raw_w in enumerate(weights[:-1], start=1):
        w = np.asarray(raw_w, dtype=np.float64)
        h = np.maximum(h @ w, 0.0)
        d_emp = _empirical_d21(h)

        if layer > 1:
            state = _transport_and_age(
                state,
                w,
                rank_s=rs,
                rank_n=rn,
                layer=layer,
            )

        old = _state_matrix(state, n)
        birth = d_emp - old
        birth_identity_max = max(
            birth_identity_max,
            float(np.max(np.abs(d_emp - (old + birth)))),
        )
        state.y0 = _compress_matrix(
            birth,
            ry,
            seed=132_100_000 + 1000 * layer + 7,
        )
        nested_exercised = nested_exercised or (
            state.rn is not None and state.cold is not None
        )
        approx = _state_matrix(state, n)
        layer_diag.append(
            {
                "layer": layer,
                "d21_fro": float(np.linalg.norm(d_emp)),
                "approx_fro": float(np.linalg.norm(approx)),
                "compression_residual_fro": float(np.linalg.norm(d_emp - approx)),
                "nested_live": bool(
                    state.rn is not None and state.cold is not None
                ),
            }
        )

    d_corr = _state_matrix(state, n)
    np.fill_diagonal(d_corr, 0.0)

    w1 = np.asarray(weights[0], dtype=np.float64)
    norms = np.linalg.norm(w1, axis=0)
    u = np.zeros_like(w1)
    good = norms > 0.0
    u[:, good] = w1[:, good] / norms[good][None, :]

    a = x_eval @ u
    b = a @ d_corr.T
    rho = u.T @ u
    rvec = np.sum(d_corr * rho, axis=1, dtype=np.float64)
    v = (a * a - 1.0) * b - 2.0 * a * rvec[None, :]

    dnorm = float(np.linalg.norm(d_corr))
    gamma = 1.0 / (float(n) * max(1.0, dnorm))
    wlast = np.asarray(weights[-1], dtype=np.float64)
    correction = gamma * (v @ wlast)

    y_eval = _propagate(x_eval, weights)
    estimate = np.mean(y_eval - correction, axis=0, dtype=np.float64)
    baseline = np.mean(y_eval, axis=0, dtype=np.float64)

    lips = _lipschitz_output_bounds(weights)
    row_l1 = np.sum(np.abs(d_corr), axis=1, dtype=np.float64)
    sd_g = gamma * math.sqrt(6.0) * (row_l1 @ np.abs(wlast))
    certificate_mse = float(np.mean((lips + sd_g) ** 2) / float(evaluation))

    finite = bool(
        np.isfinite(estimate).all()
        and np.isfinite(baseline).all()
        and np.isfinite(d_corr).all()
        and math.isfinite(certificate_mse)
        and math.isfinite(birth_identity_max)
    )

    return E132Estimate(
        mean=estimate,
        baseline_mean=baseline,
        d21_correction=d_corr,
        certificate_mse=certificate_mse,
        birth_identity_max_abs=birth_identity_max,
        nested_path_exercised=nested_exercised,
        finite=finite,
        ledger=_cost_formula(n, len(weights), pilot, evaluation),
        diagnostics={
            "gamma": gamma,
            "d21_correction_fro": dnorm,
            "d21_correction_diag_max_abs": float(
                np.max(np.abs(np.diag(d_corr)))
            ),
            "lipschitz_bound_max": float(np.max(lips)),
            "hermite_sd_bound_max": float(np.max(sd_g)),
            "layers": layer_diag,
        },
    )
