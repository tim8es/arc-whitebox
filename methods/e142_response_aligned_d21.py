"""E142 response-aligned sufficient statistic for old K3/D21 contractions.

This module contains only target-free algebra on source factors and response
directions. It does not materialize the omitted residual D21 matrix.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


BUDGET_FLOPS = 2**41
MODULE_CAP_FLOPS = int(math.floor(0.135 * BUDGET_FLOPS))

PROD_N = 1024
PROD_LAYERS = 16
PROD_RESPONSE_RANK = 16
PROD_Q1 = 384
PROD_Q2 = 224
PROD_K1 = 16
PROD_K2 = 16
PROD_PASSES = 4


@dataclass(frozen=True)
class TierFactors:
    la: np.ndarray
    lp: np.ndarray
    fa: np.ndarray
    fp: np.ndarray

    def validate(self, *, n: int, q: int) -> None:
        la = np.asarray(self.la)
        lp = np.asarray(self.lp)
        fa = np.asarray(self.fa)
        fp = np.asarray(self.fp)
        if la.ndim != 3 or lp.ndim != 3 or fa.ndim != 3 or fp.ndim != 3:
            raise ValueError("tier factors must be rank-3 arrays")
        k = la.shape[0]
        if la.shape != (k, n, n) or lp.shape != (k, n, n):
            raise ValueError("left factor shape mismatch")
        if fa.shape != (k, q, n) or fp.shape != (k, q, n):
            raise ValueError("right factor shape mismatch")
        if not all(np.isfinite(x).all() for x in (la, lp, fa, fp)):
            raise ValueError("non-finite tier factor")


@dataclass(frozen=True)
class ResidualState:
    q_c: np.ndarray
    u2: np.ndarray
    shared: TierFactors
    nested: TierFactors

    def validate(self) -> tuple[int, int, int]:
        q_c = np.asarray(self.q_c, dtype=np.float64)
        u2 = np.asarray(self.u2, dtype=np.float64)
        if q_c.ndim != 2 or u2.ndim != 2:
            raise ValueError("basis arrays must be matrices")
        n, q1 = q_c.shape
        if u2.shape[0] != q1:
            raise ValueError("nested basis row mismatch")
        q2 = int(u2.shape[1])
        self.shared.validate(n=n, q=q1)
        self.nested.validate(n=n, q=q2)
        return n, q1, q2


@dataclass(frozen=True)
class ActionResult:
    value: np.ndarray
    fp_certificate: float
    source_scale: float


@dataclass(frozen=True)
class AdaptiveResult:
    y1: np.ndarray
    q1: np.ndarray
    z1: np.ndarray
    y2: np.ndarray
    q2: np.ndarray
    b: np.ndarray
    right_queries: tuple[np.ndarray, np.ndarray]
    left_queries: tuple[np.ndarray, np.ndarray]
    action_results: tuple[ActionResult, ActionResult, ActionResult, ActionResult]


def canonical_qr(x: np.ndarray) -> np.ndarray:
    q, _ = np.linalg.qr(np.asarray(x, dtype=np.float64), mode="reduced")
    for j in range(q.shape[1]):
        idx = int(np.argmax(np.abs(q[:, j])))
        if q[idx, j] < 0.0:
            q[:, j] *= -1.0
    return q


def _gamma_m(n: int, q1: int, q2: int) -> float:
    u = 2.0 ** -52
    m = 4 * n + 4 * q1 + 4 * q2 + 32
    mu = float(m) * u
    if mu >= 1.0:
        return math.inf
    return mu / (1.0 - mu)


def _tier_right(
    tier: TierFactors,
    v: np.ndarray,
) -> tuple[np.ndarray, float]:
    n = tier.la.shape[1]
    r = v.shape[1]
    out = np.zeros((n, r), dtype=np.float64)
    scale = 0.0
    for s in range(tier.la.shape[0]):
        fav = tier.fa[s].T @ v
        fpv = tier.fp[s].T @ v
        out += tier.la[s] @ fav
        out += tier.lp[s] @ fpv
        scale += float(np.linalg.norm(tier.la[s])) * float(np.linalg.norm(fav))
        scale += float(np.linalg.norm(tier.lp[s])) * float(np.linalg.norm(fpv))
    return out, scale


def _tier_left(
    tier: TierFactors,
    t: np.ndarray,
) -> tuple[np.ndarray, float]:
    q = tier.fa.shape[1]
    r = t.shape[1]
    out = np.zeros((q, r), dtype=np.float64)
    scale = 0.0
    for s in range(tier.la.shape[0]):
        lat = tier.la[s].T @ t
        lpt = tier.lp[s].T @ t
        out += tier.fa[s] @ lat
        out += tier.fp[s] @ lpt
        scale += float(np.linalg.norm(tier.fa[s])) * float(np.linalg.norm(lat))
        scale += float(np.linalg.norm(tier.fp[s])) * float(np.linalg.norm(lpt))
    return out, scale


def residual_right_action(
    state: ResidualState,
    s: np.ndarray,
) -> ActionResult:
    n, q1, q2 = state.validate()
    s = np.asarray(s, dtype=np.float64)
    if s.ndim != 2 or s.shape[0] != n:
        raise ValueError("right response shape mismatch")
    v1 = state.q_c.T @ s
    v2 = state.u2.T @ v1
    y1, scale1 = _tier_right(state.shared, v1)
    y2, scale2 = _tier_right(state.nested, v2)
    value = y1 + y2
    scale = scale1 + scale2
    return ActionResult(
        value=value,
        fp_certificate=_gamma_m(n, q1, q2) * scale,
        source_scale=scale,
    )


def residual_left_action(
    state: ResidualState,
    t: np.ndarray,
) -> ActionResult:
    n, q1, q2 = state.validate()
    t = np.asarray(t, dtype=np.float64)
    if t.ndim != 2 or t.shape[0] != n:
        raise ValueError("left response shape mismatch")
    z1, scale1 = _tier_left(state.shared, t)
    z2, scale2 = _tier_left(state.nested, t)
    inner = z1 + state.u2 @ z2
    value = state.q_c @ inner
    scale = scale1 + scale2
    return ActionResult(
        value=value,
        fp_certificate=_gamma_m(n, q1, q2) * scale,
        source_scale=scale,
    )


def adaptive_response_sequence(
    retained_d: np.ndarray,
    residual_state: ResidualState,
    omega: np.ndarray,
) -> AdaptiveResult:
    n, _, _ = residual_state.validate()
    retained_d = np.asarray(retained_d, dtype=np.float64)
    omega = np.asarray(omega, dtype=np.float64)
    if retained_d.shape != (n, n):
        raise ValueError("retained D21 shape mismatch")
    if omega.ndim != 2 or omega.shape[0] != n:
        raise ValueError("omega shape mismatch")

    a1 = residual_right_action(residual_state, omega)
    y1 = retained_d @ omega + a1.value
    q1 = canonical_qr(y1)

    a2 = residual_left_action(residual_state, q1)
    z1 = retained_d.T @ q1 + a2.value

    a3 = residual_right_action(residual_state, z1)
    y2 = retained_d @ z1 + a3.value
    q2 = canonical_qr(y2)

    a4 = residual_left_action(residual_state, q2)
    b = retained_d.T @ q2 + a4.value

    return AdaptiveResult(
        y1=y1,
        q1=q1,
        z1=z1,
        y2=y2,
        q2=q2,
        b=b,
        right_queries=(omega.copy(), z1.copy()),
        left_queries=(q1.copy(), q2.copy()),
        action_results=(a1, a2, a3, a4),
    )


def response_basis(right_queries: Sequence[np.ndarray]) -> np.ndarray:
    mats = [np.asarray(x, dtype=np.float64) for x in right_queries]
    if not mats:
        raise ValueError("at least one query required")
    n = mats[0].shape[0]
    if any(x.ndim != 2 or x.shape[0] != n for x in mats):
        raise ValueError("query shape mismatch")
    joined = np.concatenate(mats, axis=1)
    return canonical_qr(joined)


def heldout_projection(
    retained_d: np.ndarray,
    residual_state: ResidualState,
    basis: np.ndarray,
    heldout: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, ActionResult]:
    """Approximate D @ heldout using exact residual action only on basis.

    Returns (approximation, off-subspace E, residual_action_on_basis).
    """
    basis = np.asarray(basis, dtype=np.float64)
    heldout = np.asarray(heldout, dtype=np.float64)
    residual_basis = residual_right_action(residual_state, basis)
    coeff = basis.T @ heldout
    e = heldout - basis @ coeff
    approx = (
        np.asarray(retained_d, dtype=np.float64) @ heldout
        + residual_basis.value @ coeff
    )
    return approx, e, residual_basis


def orientation_certificate(
    state: ResidualState,
    e: np.ndarray,
) -> tuple[float, float]:
    """Return orientation-aware and sourcewise norm-only bounds."""
    n, _, _ = state.validate()
    e = np.asarray(e, dtype=np.float64)
    if e.ndim != 2 or e.shape[0] != n:
        raise ValueError("held-out residual response shape mismatch")

    v1 = state.q_c.T @ e
    v2 = state.u2.T @ v1

    orient = 0.0
    norm_only = 0.0

    for tier, v in ((state.shared, v1), (state.nested, v2)):
        vnorm = float(np.linalg.norm(v))
        for s in range(tier.la.shape[0]):
            fav = tier.fa[s].T @ v
            fpv = tier.fp[s].T @ v

            nla = float(np.linalg.norm(tier.la[s]))
            nlp = float(np.linalg.norm(tier.lp[s]))
            nfa = float(np.linalg.norm(tier.fa[s]))
            nfp = float(np.linalg.norm(tier.fp[s]))

            orient += nla * float(np.linalg.norm(fav))
            orient += nlp * float(np.linalg.norm(fpv))

            norm_only += nla * nfa * vnorm
            norm_only += nlp * nfp * vnorm

    return orient, norm_only


def module_cost_formula(
    *,
    n: int,
    layers: int,
    response_rank: int,
    q1: int,
    q2: int,
    k1: int,
    k2: int,
    passes: int,
    helper_reserve: int,
) -> dict:
    c_a = 32 * (k1 + k2) * n * n * layers
    c_b = passes * layers * k1 * 4 * n * response_rank * (n + q1)
    c_c = passes * layers * k2 * 4 * n * response_rank * (n + q2)
    c_d = passes * layers * (
        2 * n * q1 * response_rank
        + 2 * q1 * q2 * response_rank
    )
    c_e = 16 * n * response_rank * response_rank * layers
    c_f = passes * layers * 8 * n * response_rank * response_rank
    c_g = passes * layers * (k1 + k2) * (
        4 * n * n + 8 * n * response_rank
    )
    total = c_a + c_b + c_c + c_d + c_e + c_f + c_g + helper_reserve
    return {
        "n": int(n),
        "layers": int(layers),
        "response_rank": int(response_rank),
        "q1": int(q1),
        "q2": int(q2),
        "k1": int(k1),
        "k2": int(k2),
        "passes": int(passes),
        "left_factor_build_upper": int(c_a),
        "shared_response_actions_upper": int(c_b),
        "nested_response_actions_upper": int(c_c),
        "basis_lifts_upper": int(c_d),
        "adaptive_qr_upper": int(c_e),
        "adaptive_query_products_upper": int(c_f),
        "certificate_norms_upper": int(c_g),
        "helper_reserve": int(helper_reserve),
        "all_in_upper": int(total),
    }


def production_cost_receipt() -> dict:
    out = module_cost_formula(
        n=PROD_N,
        layers=PROD_LAYERS,
        response_rank=PROD_RESPONSE_RANK,
        q1=PROD_Q1,
        q2=PROD_Q2,
        k1=PROD_K1,
        k2=PROD_K2,
        passes=PROD_PASSES,
        helper_reserve=20_000_000_000,
    )
    out.update(
        {
            "budget_flops": BUDGET_FLOPS,
            "cap_fraction": 0.135,
            "module_cap_flops": MODULE_CAP_FLOPS,
            "utilization": out["all_in_upper"] / float(BUDGET_FLOPS),
            "slack_to_module_cap": MODULE_CAP_FLOPS - out["all_in_upper"],
            "passes_cap": out["all_in_upper"] <= MODULE_CAP_FLOPS,
            "scope": "E142 old-tier response-statistic module only",
        }
    )
    return out
