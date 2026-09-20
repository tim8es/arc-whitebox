"""E134 source-age K=3 direct ReLU-mean closure.

Target-free candidate. No exact-reference or benchmark dependency is permitted.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


RAW_MSE_TARGET = 1.89e-8
PROD_N = 1024
PROD_DEPTH = 16
PROD_M = 4096
PROD_RY = 32
PROD_RS = 48
PROD_RN = 24
BUDGET = 2**41
UTIL_CAP = 0.13
SIGMA_EPS = 2.0 ** -40


@dataclass(frozen=True)
class Source:
    age: int
    q: np.ndarray
    core: np.ndarray


@dataclass(frozen=True)
class E134Estimate:
    mean: np.ndarray
    baseline_mean: np.ndarray
    full_empirical_k3_closure_mean: np.ndarray
    certificate_bounds: np.ndarray
    certificate_mse: float
    actual_closure_residual: np.ndarray
    penultimate_tensor_residual_fro: float
    kappa3_compressed: np.ndarray
    kappa3_empirical: np.ndarray
    deterministic_state_digest: dict
    nested_path_exercised: bool
    max_core_symmetry_error: float
    max_slice_disagreement: float
    max_birth_projection_identity_error: float
    finite: bool
    ledger: dict
    diagnostics: dict


def ranks_for_width(n: int) -> tuple[int, int, int]:
    if n <= 0:
        raise ValueError("width must be positive")
    return (
        min(n, max(1, math.ceil(n / 32))),
        min(n, max(1, math.ceil(3 * n / 64))),
        min(n, max(1, math.ceil(3 * n / 128))),
    )


def _canon_columns(q: np.ndarray) -> np.ndarray:
    out = np.asarray(q, dtype=np.float64).copy()
    for j in range(out.shape[1]):
        col = out[:, j]
        idx = int(np.argmax(np.abs(col)))
        if col[idx] < 0.0:
            out[:, j] *= -1.0
    return out


def _canon_qr(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    q, r = np.linalg.qr(np.asarray(a, dtype=np.float64), mode="reduced")
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


def _transform_core(core: np.ndarray, t: np.ndarray) -> np.ndarray:
    c = np.asarray(core, dtype=np.float64)
    a = np.asarray(t, dtype=np.float64)
    return np.einsum(
        "abc,ua,vb,wc->uvw",
        c,
        a,
        a,
        a,
        optimize=True,
    )


def _core_symmetry_error(core: np.ndarray) -> float:
    c = np.asarray(core, dtype=np.float64)
    errs = [
        np.max(np.abs(c - np.transpose(c, axes)))
        for axes in [
            (0, 2, 1),
            (1, 0, 2),
            (1, 2, 0),
            (2, 0, 1),
            (2, 1, 0),
        ]
    ]
    return float(max(errs, default=0.0))


def _transport_source(source: Source, w: np.ndarray, *, age_increment: int = 1) -> Source:
    a = np.asarray(w, dtype=np.float64).T @ source.q
    q, r = _canon_qr(a)
    core = _transform_core(source.core, r)
    return Source(age=source.age + age_increment, q=q, core=core)


def _project_core(source: Source, qnew: np.ndarray) -> np.ndarray:
    t = np.asarray(qnew, dtype=np.float64).T @ source.q
    return _transform_core(source.core, t)


def _weighted_union_basis(sources: Sequence[Source], rank: int) -> np.ndarray:
    if not sources:
        raise ValueError("sources required")
    blocks = []
    for source in sources:
        weight = max(float(np.linalg.norm(source.core)), 2.0 ** -100) ** (1.0 / 3.0)
        blocks.append(source.q * weight)
    a = np.concatenate(blocks, axis=1)
    u, _, _ = np.linalg.svd(a, full_matrices=False)
    r = min(int(rank), u.shape[1])
    return _canon_columns(u[:, :r])


def _nested_basis(qs: np.ndarray, old_core: np.ndarray, rank: int) -> np.ndarray:
    gram = np.einsum("abc,dbc->ad", old_core, old_core, optimize=True)
    gram = 0.5 * (gram + gram.T)
    evals, evecs = np.linalg.eigh(gram)
    order = np.argsort(evals)[::-1]
    r = min(int(rank), qs.shape[1])
    v = _canon_columns(evecs[:, order[:r]])
    return _canon_columns(qs @ v)


def _rebase_aged_sources(
    sources: Sequence[Source],
    *,
    rank_s: int,
    rank_n: int,
) -> list[Source]:
    young = [s for s in sources if s.age <= 1]
    middle = [s for s in sources if 2 <= s.age <= 4]
    old = [s for s in sources if s.age >= 5]

    if not middle and not old:
        return list(young)

    qs = _weighted_union_basis([*middle, *old], rank_s)
    out = list(young)
    for source in middle:
        out.append(
            Source(
                age=source.age,
                q=qs,
                core=_project_core(source, qs),
            )
        )

    if old:
        old_core = np.zeros((qs.shape[1],) * 3, dtype=np.float64)
        for source in old:
            old_core += _project_core(source, qs)
        qn = _nested_basis(qs, old_core, rank_n)
        t = qn.T @ qs
        cn = _transform_core(old_core, t)
        out.append(Source(age=5, q=qn, core=cn))

    return out


def _range_basis(x: np.ndarray, rank: int, layer: int) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    omega = _omega(
        x.shape[0],
        rank,
        seed=134_100_000 + 1009 * int(layer) + 17,
    )
    y = x.T @ omega
    q, _ = _canon_qr(y)
    return q[:, : min(rank, q.shape[1])]


def _empirical_projected_core(x: np.ndarray, q: np.ndarray) -> np.ndarray:
    u = np.asarray(x, dtype=np.float64) @ np.asarray(q, dtype=np.float64)
    return np.einsum("pa,pb,pc->abc", u, u, u, optimize=True) / float(x.shape[0])


def _state_projected_core(sources: Sequence[Source], q: np.ndarray) -> np.ndarray:
    r = q.shape[1]
    out = np.zeros((r, r, r), dtype=np.float64)
    for source in sources:
        out += _project_core(source, q)
    return out


def _materialize_source(source: Source) -> np.ndarray:
    return np.einsum(
        "abc,ia,jb,kc->ijk",
        source.core,
        source.q,
        source.q,
        source.q,
        optimize=True,
    )


def _materialize_state(sources: Sequence[Source], n: int) -> np.ndarray:
    out = np.zeros((n, n, n), dtype=np.float64)
    for source in sources:
        out += _materialize_source(source)
    return out


def _empirical_k3(x: np.ndarray) -> np.ndarray:
    a = np.asarray(x, dtype=np.float64)
    return np.einsum("pi,pj,pk->ijk", a, a, a, optimize=True) / float(a.shape[0])


def _direct_slices(sources: Sequence[Source], n: int) -> tuple[np.ndarray, np.ndarray]:
    d3 = np.zeros(n, dtype=np.float64)
    d21 = np.zeros((n, n), dtype=np.float64)
    for source in sources:
        q = source.q
        c = source.core
        d3 += np.einsum("abc,ia,ib,ic->i", c, q, q, q, optimize=True)
        d21 += np.einsum("abc,ia,ib,jc->ij", c, q, q, q, optimize=True)
    return d3, d21


def _slice_disagreement(sources: Sequence[Source], n: int) -> float:
    materialized = _materialize_state(sources, n)
    d3_a = np.einsum("iii->i", materialized)
    d21_a = np.empty((n, n), dtype=np.float64)
    for i in range(n):
        d21_a[i, :] = materialized[i, i, :]
    d3_b, d21_b = _direct_slices(sources, n)
    return float(
        max(
            np.max(np.abs(d3_a - d3_b)),
            np.max(np.abs(d21_a - d21_b)),
        )
    )


def _normal_pdf(a: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * a * a) / math.sqrt(2.0 * math.pi)


def _normal_cdf(a: np.ndarray) -> np.ndarray:
    # numpy has no erf ufunc in the minimal dependency contract.
    return np.array(
        [0.5 * (1.0 + math.erf(float(v) / math.sqrt(2.0))) for v in a],
        dtype=np.float64,
    )


def _edgeworth_relu_mean(
    mu: np.ndarray,
    sigma: np.ndarray,
    kappa3: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    mu = np.asarray(mu, dtype=np.float64)
    sigma = np.asarray(sigma, dtype=np.float64)
    kappa3 = np.asarray(kappa3, dtype=np.float64)
    out = np.maximum(mu, 0.0)
    coeff = np.zeros_like(mu)
    good = sigma > SIGMA_EPS
    if np.any(good):
        a = mu[good] / sigma[good]
        phi = _normal_pdf(a)
        base = sigma[good] * phi + mu[good] * _normal_cdf(a)
        coeff_good = -mu[good] * phi / (6.0 * sigma[good] ** 3)
        out[good] = base + coeff_good * kappa3[good]
        coeff[good] = coeff_good
    return out, coeff


def _state_digest(sources: Sequence[Source]) -> dict:
    return {
        "ages": [int(s.age) for s in sources],
        "ranks": [int(s.q.shape[1]) for s in sources],
        "q_sums": [float(np.sum(s.q, dtype=np.float64)) for s in sources],
        "core_sums": [float(np.sum(s.core, dtype=np.float64)) for s in sources],
        "core_fro": [float(np.linalg.norm(s.core)) for s in sources],
    }


def production_cost_receipt() -> dict:
    n = PROD_N
    l = PROD_DEPTH
    m = PROD_M
    ry, rs, rn = PROD_RY, PROD_RS, PROD_RN
    hidden = l - 1

    parts = {
        "rng_materialization_upper": 32 * m * n,
        "dense_propagation_upper": m * l * (2 * n * n + 2 * n),
        "hidden_centering_moment_reductions_upper": hidden * 8 * m * n,
        "birth_sketch_projection_qr_upper": hidden * (
            4 * m * n * ry + 4 * n * ry * ry + 8 * ry**3
        ),
        "birth_cubic_core_upper": hidden * (8 * m * ry**3),
        "represented_source_basis_transport_upper": hidden * (
            2 * n * n * (2 * ry + rs + rn)
        ),
        "cubic_core_basis_transform_upper": hidden * (
            8 * (2 * ry**4 + rs**4 + rn**4)
        ),
        "shared_nested_rebase_upper": hidden * (
            4 * n * (2 * ry + 3 * rs + rn) ** 2
            + 16 * (rs + ry) ** 4
            + 16 * rn**4
        ),
        "final_k3_diagonal_upper": 8 * n * (
            2 * ry**3 + 3 * rs**3 + rn**3
        ),
        "final_mean_variance_reductions_upper": 8 * m * n,
        "edgeworth_scalar_helpers_upper": 64 * n,
        "helper_certificate_accounting_reserve": 5_000_000_000,
    }
    total = int(sum(parts.values()))
    return {
        **parts,
        "all_in_upper": total,
        "budget": BUDGET,
        "utilization": total / float(BUDGET),
        "utilization_cap": UTIL_CAP,
        "cap_flops": UTIL_CAP * BUDGET,
        "slack_flops": UTIL_CAP * BUDGET - total,
        "expected_all_in": 189_262_033_408,
        "formula_matches_frozen_total": total == 189_262_033_408,
        "passes_cap": total <= UTIL_CAP * BUDGET,
    }


def source_k3_direct_estimate(
    weights: Sequence[np.ndarray],
    *,
    trajectories: int,
    seed: int,
) -> E134Estimate:
    if len(weights) < 7:
        raise ValueError("depth must be >=7 to exercise age>=5 source path")
    first = np.asarray(weights[0], dtype=np.float64)
    if first.ndim != 2:
        raise ValueError("weights must be matrices")
    d = int(first.shape[0])
    n = int(first.shape[1])
    if trajectories <= 0:
        raise ValueError("trajectories must be positive")
    prev = n
    for idx, raw in enumerate(weights[1:], start=1):
        w = np.asarray(raw, dtype=np.float64)
        if w.ndim != 2 or w.shape[0] != prev or w.shape[1] != n:
            raise ValueError(f"incompatible constant-width weight {idx}: {w.shape}")
        prev = int(w.shape[1])

    ry, rs, rn = ranks_for_width(n)
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    h = rng.standard_normal((trajectories, d)).astype(np.float64)

    sources: list[Source] = []
    nested_exercised = False
    max_sym = 0.0
    max_slice = 0.0
    max_birth_identity = 0.0
    layer_diag = []

    for layer, raw_w in enumerate(weights[:-1], start=1):
        w = np.asarray(raw_w, dtype=np.float64)
        h = np.maximum(h @ w, 0.0)
        x = h - np.mean(h, axis=0, dtype=np.float64)

        if sources:
            transported = [
                _transport_source(source, w, age_increment=1)
                for source in sources
            ]
            sources = _rebase_aged_sources(
                transported,
                rank_s=rs,
                rank_n=rn,
            )

        qbirth = _range_basis(x, ry, layer)
        emp_core = _empirical_projected_core(x, qbirth)
        old_proj = _state_projected_core(sources, qbirth)
        birth_core = emp_core - old_proj
        max_birth_identity = max(
            max_birth_identity,
            float(np.max(np.abs(emp_core - (old_proj + birth_core)))),
        )
        sources.append(Source(age=0, q=qbirth, core=birth_core))

        nested_exercised = nested_exercised or any(s.age >= 5 for s in sources)
        for source in sources:
            max_sym = max(max_sym, _core_symmetry_error(source.core))
        max_slice = max(max_slice, _slice_disagreement(sources, n))
        d3, d21 = _direct_slices(sources, n)
        layer_diag.append(
            {
                "layer": int(layer),
                "source_ages": [int(s.age) for s in sources],
                "source_ranks": [int(s.q.shape[1]) for s in sources],
                "d3_fro": float(np.linalg.norm(d3)),
                "d21_fro": float(np.linalg.norm(d21)),
                "max_core_symmetry_error": float(
                    max(_core_symmetry_error(s.core) for s in sources)
                ),
            }
        )

    penultimate_h = h
    xpen = penultimate_h - np.mean(
        penultimate_h, axis=0, dtype=np.float64
    )

    wlast = np.asarray(weights[-1], dtype=np.float64)
    z = penultimate_h @ wlast
    mu = np.mean(z, axis=0, dtype=np.float64)
    centered_z = z - mu[None, :]
    sigma = np.sqrt(
        np.mean(centered_z * centered_z, axis=0, dtype=np.float64)
    )

    final_sources = [
        _transport_source(source, wlast, age_increment=0)
        for source in sources
    ]
    kappa3_compressed, _ = _direct_slices(final_sources, n)
    kappa3_empirical = np.mean(centered_z**3, axis=0, dtype=np.float64)

    estimate, coeff = _edgeworth_relu_mean(
        mu, sigma, kappa3_compressed
    )
    full_closure, _ = _edgeworth_relu_mean(
        mu, sigma, kappa3_empirical
    )
    baseline = np.mean(np.maximum(z, 0.0), axis=0, dtype=np.float64)

    # Target-free source-compression residual certificate.
    empirical_tensor = _empirical_k3(xpen)
    source_tensor = _materialize_state(sources, n)
    residual_tensor = empirical_tensor - source_tensor
    residual_fro = float(np.linalg.norm(residual_tensor))
    wnorm = np.linalg.norm(wlast, axis=0)
    bounds = np.abs(coeff) * residual_fro * (wnorm**3)
    actual_residual = estimate - full_closure
    certificate_mse = float(np.mean(bounds * bounds))

    finite = bool(
        np.isfinite(estimate).all()
        and np.isfinite(baseline).all()
        and np.isfinite(full_closure).all()
        and np.isfinite(bounds).all()
        and np.isfinite(actual_residual).all()
        and np.isfinite(kappa3_compressed).all()
        and np.isfinite(kappa3_empirical).all()
        and math.isfinite(certificate_mse)
        and math.isfinite(residual_fro)
    )

    ledger = {
        "width": n,
        "depth": len(weights),
        "trajectories": trajectories,
        "r_y": ry,
        "r_s": rs,
        "r_n": rn,
        "hidden_dense_propagations": trajectories * (len(weights) - 1),
        "final_linear_preactivations": trajectories,
        "source_layers": len(weights) - 1,
    }

    return E134Estimate(
        mean=estimate,
        baseline_mean=baseline,
        full_empirical_k3_closure_mean=full_closure,
        certificate_bounds=bounds,
        certificate_mse=certificate_mse,
        actual_closure_residual=actual_residual,
        penultimate_tensor_residual_fro=residual_fro,
        kappa3_compressed=kappa3_compressed,
        kappa3_empirical=kappa3_empirical,
        deterministic_state_digest=_state_digest(sources),
        nested_path_exercised=nested_exercised,
        max_core_symmetry_error=max_sym,
        max_slice_disagreement=max_slice,
        max_birth_projection_identity_error=max_birth_identity,
        finite=finite,
        ledger=ledger,
        diagnostics={
            "mu_max_abs": float(np.max(np.abs(mu))),
            "sigma_min": float(np.min(sigma)),
            "sigma_max": float(np.max(sigma)),
            "compressed_kappa3_fro": float(np.linalg.norm(kappa3_compressed)),
            "empirical_kappa3_fro": float(np.linalg.norm(kappa3_empirical)),
            "certificate_max_abs": float(np.max(bounds)),
            "actual_closure_residual_max_abs": float(
                np.max(np.abs(actual_residual))
            ),
            "layers": layer_diag,
        },
    )
