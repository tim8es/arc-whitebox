"""E147 RAP-K3 exact-small candidate.

Target-free implementation of the frozen response-aligned projected K3
architecture.  The candidate never materializes an n^3 K3 tensor and has no
dependency on the exact-small reference.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


BUDGET_FLOPS = 2**41
CAP_FLOPS = int(math.floor(0.135 * BUDGET_FLOPS))
PROD_N = 1024
PROD_DEPTH = 16
PROD_Q = 96
PROD_R = 48
SIGMA_EPS = 2.0 ** -40


@dataclass(frozen=True)
class LayerState:
    mean: np.ndarray
    covariance: np.ndarray
    pre_mean: np.ndarray
    pre_var: np.ndarray
    wick1: np.ndarray
    birth_k3: np.ndarray
    birth_k4: np.ndarray


@dataclass(frozen=True)
class RapLayer:
    core: np.ndarray
    d3: np.ndarray
    d21: np.ndarray
    rho: float
    d21_abs_certificate: float
    d21_rel_certificate: float
    transport_projection_bound: float
    birth_projection_bound: float
    fp_bound: float
    pullback_residual_u: float
    pullback_residual_v: float
    transport_core: np.ndarray | None


@dataclass(frozen=True)
class RapEstimate:
    final_mean: np.ndarray
    final_mean_certificate: float
    layers: tuple[RapLayer, ...]
    bases_u: tuple[np.ndarray, ...]
    bases_v: tuple[np.ndarray, ...]
    pull_ru: tuple[np.ndarray | None, ...]
    pull_rv: tuple[np.ndarray | None, ...]
    transports: tuple[np.ndarray, ...]
    scaffold: tuple[LayerState, ...]
    final_pre_d3: np.ndarray
    final_pre_rho: float
    pooled_d21_certificate: float
    finite: bool
    production_cost: dict


def ranks_for_width(n: int) -> tuple[int, int]:
    if n <= 0:
        raise ValueError("width must be positive")
    q = min(n, max(8, math.ceil(3 * n / 32)))
    r = min(q, max(4, math.ceil(3 * n / 64)))
    return int(q), int(r)


def _canon_qr(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    q, r = np.linalg.qr(np.asarray(a, dtype=np.float64), mode="reduced")
    for j in range(q.shape[1]):
        idx = int(np.argmax(np.abs(q[:, j])))
        if q[idx, j] < 0.0:
            q[:, j] *= -1.0
            r[j, :] *= -1.0
    return q, r


def _orth_block(n: int, rank: int, seed: int) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    q, _ = _canon_qr(rng.standard_normal((n, rank)))
    return q[:, :rank]


def _normal_pdf(a: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * a * a) / math.sqrt(2.0 * math.pi)


def _normal_cdf(a: np.ndarray) -> np.ndarray:
    return np.array(
        [0.5 * (1.0 + math.erf(float(x) / math.sqrt(2.0))) for x in a],
        dtype=np.float64,
    )


def _relu_gaussian_moments(
    mean: np.ndarray,
    var: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mu = np.asarray(mean, dtype=np.float64)
    vv = np.maximum(np.asarray(var, dtype=np.float64), SIGMA_EPS**2)
    sig = np.sqrt(vv)
    a = mu / sig
    phi = _normal_pdf(a)
    Phi = _normal_cdf(a)

    m1 = sig * phi + mu * Phi
    m2 = (mu * mu + vv) * Phi + mu * sig * phi
    m3 = (mu**3 + 3.0 * mu * vv) * Phi + (
        mu * mu * sig + 2.0 * sig**3
    ) * phi
    m4 = (mu**4 + 6.0 * mu * mu * vv + 3.0 * vv * vv) * Phi + (
        mu**3 * sig + 5.0 * mu * sig**3
    ) * phi

    out_var = np.maximum(m2 - m1 * m1, SIGMA_EPS**2)
    k3 = m3 - 3.0 * m1 * m2 + 2.0 * m1**3
    central4 = m4 - 4.0 * m1 * m3 + 6.0 * m1 * m1 * m2 - 3.0 * m1**4
    k4 = central4 - 3.0 * out_var * out_var
    return m1, out_var, Phi, k3, k4


def build_scaffold(weights: Sequence[np.ndarray]) -> tuple[LayerState, ...]:
    if not weights:
        raise ValueError("weights required")
    n = int(np.asarray(weights[0]).shape[0])
    mu = np.zeros(n, dtype=np.float64)
    cov = np.eye(n, dtype=np.float64)
    out: list[LayerState] = []

    for idx, raw in enumerate(weights):
        w = np.asarray(raw, dtype=np.float64)
        if w.shape != (n, n):
            raise ValueError(f"weight {idx} shape {w.shape}, expected {(n, n)}")
        pre_mu = w.T @ mu
        pre_cov = w.T @ cov @ w
        pre_cov = 0.5 * (pre_cov + pre_cov.T)
        pre_var = np.maximum(np.diag(pre_cov), SIGMA_EPS**2)

        mean, out_var, wick1, birth3, birth4 = _relu_gaussian_moments(
            pre_mu, pre_var
        )
        cov_next = (wick1[:, None] * pre_cov) * wick1[None, :]
        np.fill_diagonal(cov_next, out_var)
        cov_next = 0.5 * (cov_next + cov_next.T)

        out.append(
            LayerState(
                mean=mean.copy(),
                covariance=cov_next.copy(),
                pre_mean=pre_mu.copy(),
                pre_var=pre_var.copy(),
                wick1=wick1.copy(),
                birth_k3=birth3.copy(),
                birth_k4=birth4.copy(),
            )
        )
        mu = mean
        cov = cov_next

    return tuple(out)


def _build_bases(
    weights: Sequence[np.ndarray],
    scaffold: Sequence[LayerState],
    *,
    qrank: int,
    rrank: int,
    final_basis_seed: int,
) -> tuple[
    tuple[np.ndarray, ...],
    tuple[np.ndarray, ...],
    tuple[np.ndarray | None, ...],
    tuple[np.ndarray | None, ...],
    tuple[np.ndarray, ...],
    tuple[tuple[float, float], ...],
]:
    depth = len(weights)
    n = np.asarray(weights[0]).shape[0]
    u: list[np.ndarray | None] = [None] * depth
    v: list[np.ndarray | None] = [None] * depth
    ru: list[np.ndarray | None] = [None] * depth
    rv: list[np.ndarray | None] = [None] * depth
    transports: list[np.ndarray] = []

    for l, raw in enumerate(weights):
        w = np.asarray(raw, dtype=np.float64)
        transports.append(scaffold[l].wick1[:, None] * w.T)

    u[-1] = _orth_block(n, qrank, final_basis_seed)
    v[-1] = _orth_block(n, rrank, final_basis_seed + 1)

    residuals: list[tuple[float, float]] = [(0.0, 0.0)] * depth
    eye = np.eye(n, dtype=np.float64)

    for l in range(depth - 1, 0, -1):
        t = transports[l]
        au = t.T @ u[l]
        av = t.T @ v[l]
        up, r_u = _canon_qr(au)
        vp, r_v = _canon_qr(av)
        u[l - 1] = up[:, :qrank]
        v[l - 1] = vp[:, :rrank]
        ru[l] = r_u[:qrank, :qrank]
        rv[l] = r_v[:rrank, :rrank]

        pu = u[l - 1] @ u[l - 1].T
        pv = v[l - 1] @ v[l - 1].T
        res_u = float(np.linalg.norm(u[l].T @ t @ (eye - pu)))
        res_v = float(np.linalg.norm(v[l].T @ t @ (eye - pv)))
        residuals[l] = (res_u, res_v)

    return (
        tuple(np.asarray(x) for x in u),
        tuple(np.asarray(x) for x in v),
        tuple(ru),
        tuple(rv),
        tuple(transports),
        tuple(residuals),
    )


def _transport_core(
    core: np.ndarray,
    ru: np.ndarray,
    rv: np.ndarray,
) -> np.ndarray:
    return np.einsum(
        "ijk,ia,jb,kc->abc",
        core,
        ru,
        ru,
        rv,
        optimize=True,
    )


def _birth_core(
    birth: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
) -> np.ndarray:
    return np.einsum("i,ia,ib,ic->abc", birth, u, u, v, optimize=True)


def _slices(
    core: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    d3 = np.einsum("abc,ia,ib,ic->i", core, u, u, v, optimize=True)
    d21 = np.einsum("abc,ia,ib,jc->ij", core, u, u, v, optimize=True)
    d21 = np.asarray(d21, dtype=np.float64)
    np.fill_diagonal(d21, 0.0)
    return d3, d21


def _birth_projection_bound(
    birth: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
) -> float:
    pu = np.sqrt(np.maximum(np.sum(u * u, axis=1), 0.0))
    pv = np.sqrt(np.maximum(np.sum(v * v, axis=1), 0.0))
    du = np.sqrt(np.maximum(1.0 - pu * pu, 0.0))
    dv = np.sqrt(np.maximum(1.0 - pv * pv, 0.0))
    atom = du + pu * du + pu * pu * dv
    return float(np.sum(np.abs(birth) * atom, dtype=np.float64))


def _transport_projection_bound(
    core: np.ndarray,
    u_prev: np.ndarray,
    v_prev: np.ndarray,
    t: np.ndarray,
    u_next: np.ndarray,
    v_next: np.ndarray,
) -> float:
    x = t @ u_prev
    z = t @ v_prev
    nx = np.linalg.norm(x, axis=0)
    nz = np.linalg.norm(z, axis=0)
    px = np.linalg.norm(u_next.T @ x, axis=0)
    pz = np.linalg.norm(v_next.T @ z, axis=0)
    dx = np.sqrt(np.maximum(nx * nx - px * px, 0.0))
    dz = np.sqrt(np.maximum(nz * nz - pz * pz, 0.0))

    a = (
        dx[:, None, None] * nx[None, :, None] * nz[None, None, :]
        + px[:, None, None] * dx[None, :, None] * nz[None, None, :]
        + px[:, None, None] * px[None, :, None] * dz[None, None, :]
    )
    return float(np.sum(np.abs(core) * a, dtype=np.float64))


def _fp_bound(
    core: np.ndarray,
    birth: np.ndarray,
    qrank: int,
    rrank: int,
    n: int,
) -> float:
    ueps = 2.0 ** -52
    m = 16 * n + 8 * qrank * qrank * rrank + 64
    gamma = (m * ueps) / max(1.0 - m * ueps, 2.0 ** -20)
    scale = float(np.sum(np.abs(core), dtype=np.float64))
    scale += float(np.sum(np.abs(birth), dtype=np.float64))
    return gamma * max(scale, 1.0)


def _pre_d3_action(
    core_prev: np.ndarray,
    u_prev: np.ndarray,
    v_prev: np.ndarray,
    w: np.ndarray,
) -> np.ndarray:
    a = np.asarray(w, dtype=np.float64).T @ u_prev
    b = np.asarray(w, dtype=np.float64).T @ v_prev
    return np.einsum("abc,ia,ib,ic->i", core_prev, a, a, b, optimize=True)


def _edgeworth_final_mean(
    gaussian_mean: np.ndarray,
    pre_mean: np.ndarray,
    pre_var: np.ndarray,
    pre_d3: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    sig = np.sqrt(np.maximum(pre_var, SIGMA_EPS**2))
    alpha = pre_mean / sig
    phi = _normal_pdf(alpha)
    coeff = -pre_mean * phi / (6.0 * sig**3)
    return gaussian_mean + coeff * pre_d3, coeff


def production_cost_receipt() -> dict:
    n = PROD_N
    q = PROD_Q
    r = PROD_R
    transitions = PROD_DEPTH - 1

    parts = {
        "retained_low_order_public_style_allowance": 38 * (2**31),
        "backward_response_basis_dense": transitions * 2 * n * n * (q + r),
        "thin_qr_sign_canonicalization": transitions * 8 * n * (q * q + r * r),
        "projected_k3_core_transport": transitions * (
            4 * r * q**3 + 2 * r * r * q * q
        ),
        "d21_response_and_surrogate": transitions * (
            2 * n * q * q * r + 2 * n * n * r
        ),
        "direct_projected_nonlinear_k3_birth": transitions * (
            8 * n * q * q * r + 8 * n * q * r * r + 16 * n * n * r
        ),
        "error_certificate": transitions * (
            8 * n * q * q * r + 8 * n * n * r
        ),
        "helper_accounting_reserve": 10 * (2**31),
    }
    total = int(sum(parts.values()))
    return {
        **parts,
        "all_in_upper": total,
        "budget_flops": BUDGET_FLOPS,
        "cap_flops": CAP_FLOPS,
        "utilization": total / float(BUDGET_FLOPS),
        "slack_flops": CAP_FLOPS - total,
        "formula_matches_frozen_total": total == 281_324_027_904,
        "passes_cap": total <= CAP_FLOPS,
    }


def rap_k3_estimate(
    weights: Sequence[np.ndarray],
    *,
    final_basis_seed: int,
) -> RapEstimate:
    if len(weights) != 8:
        raise ValueError("frozen exact-small depth is 8")
    n = int(np.asarray(weights[0]).shape[0])
    qrank, rrank = ranks_for_width(n)
    scaffold = build_scaffold(weights)

    u, v, ru, rv, transports, pull_res = _build_bases(
        weights,
        scaffold,
        qrank=qrank,
        rrank=rrank,
        final_basis_seed=final_basis_seed,
    )

    core = np.zeros((qrank, qrank, rrank), dtype=np.float64)
    rho = 0.0
    layers: list[RapLayer] = []
    pooled_num = 0.0
    pooled_den = 0.0
    final_pre_d3 = np.zeros(n, dtype=np.float64)
    final_pre_rho = 0.0
    final_mean = scaffold[-1].mean.copy()
    final_mean_certificate = 0.0

    for l, raw_w in enumerate(weights):
        w = np.asarray(raw_w, dtype=np.float64)
        transport_core = None
        transport_proj = 0.0

        if l == len(weights) - 1:
            if l == 0:
                final_pre_d3 = np.zeros(n, dtype=np.float64)
                final_pre_rho = 0.0
            else:
                final_pre_d3 = _pre_d3_action(core, u[l - 1], v[l - 1], w)
                final_pre_rho = (
                    float(np.linalg.norm(w, 2)) ** 3 * rho
                )
            final_mean, final_coeff = _edgeworth_final_mean(
                scaffold[l].mean,
                scaffold[l].pre_mean,
                scaffold[l].pre_var,
                final_pre_d3,
            )
            final_mean_certificate = float(
                np.linalg.norm(final_coeff) * final_pre_rho
            )

        if l > 0:
            t = transports[l]
            transport_proj = _transport_projection_bound(
                core,
                u[l - 1],
                v[l - 1],
                t,
                u[l],
                v[l],
            )
            rho = float(np.linalg.norm(t, 2)) ** 3 * rho + transport_proj
            transport_core = _transport_core(core, ru[l], rv[l])
            core = transport_core

        birth = scaffold[l].birth_k3
        birth_bound = _birth_projection_bound(birth, u[l], v[l])
        birth_core = _birth_core(birth, u[l], v[l])
        core = core + birth_core

        fp = _fp_bound(core, birth, qrank, rrank, n)
        rho = rho + birth_bound + fp

        d3, d21 = _slices(core, u[l], v[l])
        dnorm = float(np.linalg.norm(d21))
        lower = dnorm - rho
        eps = math.inf if lower <= 0.0 else rho / lower
        pooled_num += rho * rho
        pooled_den += max(lower, 0.0) ** 2

        layers.append(
            RapLayer(
                core=core.copy(),
                d3=d3.copy(),
                d21=d21.copy(),
                rho=float(rho),
                d21_abs_certificate=float(rho),
                d21_rel_certificate=float(eps),
                transport_projection_bound=float(transport_proj),
                birth_projection_bound=float(birth_bound),
                fp_bound=float(fp),
                pullback_residual_u=float(pull_res[l][0]),
                pullback_residual_v=float(pull_res[l][1]),
                transport_core=(
                    None if transport_core is None else transport_core.copy()
                ),
            )
        )

    pooled = (
        math.inf
        if pooled_den <= 0.0
        else math.sqrt(pooled_num / pooled_den)
    )
    finite = bool(
        np.isfinite(final_mean).all()
        and np.isfinite(final_pre_d3).all()
        and all(
            np.isfinite(layer.core).all()
            and np.isfinite(layer.d3).all()
            and np.isfinite(layer.d21).all()
            and math.isfinite(layer.rho)
            for layer in layers
        )
    )

    return RapEstimate(
        final_mean=final_mean,
        final_mean_certificate=float(final_mean_certificate),
        layers=tuple(layers),
        bases_u=u,
        bases_v=v,
        pull_ru=ru,
        pull_rv=rv,
        transports=transports,
        scaffold=scaffold,
        final_pre_d3=final_pre_d3,
        final_pre_rho=float(final_pre_rho),
        pooled_d21_certificate=float(pooled),
        finite=finite,
        production_cost=production_cost_receipt(),
    )
