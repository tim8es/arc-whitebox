from __future__ import annotations

import math

import flopscope as flops
import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP

GH_Z = (
    -6.6308781983931295,
    -5.472225705949343,
    -4.492955302520012,
    -3.6008736241715487,
    -2.760245047630702,
    -1.9519803457163336,
    -1.1638291005549648,
    -0.3867606045005574,
    0.3867606045005574,
    1.1638291005549648,
    1.9519803457163336,
    2.760245047630702,
    3.6008736241715487,
    4.492955302520012,
    5.472225705949343,
    6.6308781983931295,
)

GH_WEIGHTS = (
    1.4978147231618314e-10,
    1.3094732162868187e-07,
    1.5300032162487316e-05,
    0.0005259849265739094,
    0.007266937601184743,
    0.04728475235401403,
    0.15833837275094964,
    0.28656852123801213,
    0.28656852123801213,
    0.15833837275094964,
    0.04728475235401403,
    0.007266937601184743,
    0.0005259849265739094,
    1.5300032162487316e-05,
    1.3094732162868187e-07,
    1.4978147231618314e-10,
)

_INV_SQRT_2PI = 0.3989422804014327
_INV_SQRT_2 = 0.7071067811865476


def cp_marginal(xp, atoms, signs):
    return xp.sum((atoms * atoms * atoms) * xp.reshape(signs, (1, -1)), axis=1)


def leverage_birth(xp, w, k3_diag):
    scores = xp.abs(k3_diag) * xp.sum(xp.abs(w) ** 3, axis=0)
    idx = int(xp.argmax(scores))
    kval = k3_diag[idx]
    sign = xp.where(kval < 0.0, -1.0, 1.0)
    scale = xp.abs(kval) ** (1.0 / 3.0)
    atom = w[:, idx] * scale
    return atom, sign, idx


def push_fifo(xp, atoms, signs, atom, sign):
    return (
        xp.concatenate([atoms[:, 1:], xp.reshape(atom, (-1, 1))], axis=1),
        xp.concatenate([signs[1:], xp.reshape(sign, (1,))], axis=0),
    )


def linear_covariance(xp, w, cov):
    return (w @ cov) @ w.T


def _cdf(xp, alpha):
    if xp is fnp:
        return flops.stats.norm.cdf(alpha).astype(alpha.dtype)
    flat = alpha.reshape(-1)
    vals = [0.5 * (1.0 + math.erf(float(v) * _INV_SQRT_2)) for v in flat]
    return xp.asarray(vals, dtype=alpha.dtype).reshape(alpha.shape)


def price_coefficients(xp, mu, var):
    sigma = xp.sqrt(var)
    alpha = mu / sigma
    phi = xp.exp(-0.5 * alpha * alpha) * _INV_SQRT_2PI
    p = _cdf(xp, alpha)
    q = phi / sigma
    r = -(alpha * phi) / (sigma * sigma)
    s = ((alpha * alpha - 1.0) * phi) / (sigma * sigma * sigma)
    return p, q, r, s


def price4_offdiag(xp, cov_pre, p, q, r, s):
    c2 = cov_pre * cov_pre
    c3 = c2 * cov_pre
    c4 = c2 * c2
    return (
        cov_pre * xp.outer(p, p)
        + 0.5 * c2 * xp.outer(q, q)
        + (c3 / 6.0) * xp.outer(r, r)
        + (c4 / 24.0) * xp.outer(s, s)
    )


def covariance_update_price4(xp, cov_pre, p, q, r, s, var_post):
    base = price4_offdiag(xp, cov_pre, p, q, r, s)
    base = 0.5 * (base + base.T)
    return base + xp.diag(var_post - xp.diag(base))


def relu_k3_moments(xp, mu, var, k3):
    sigma = xp.sqrt(var)
    gamma1 = k3 / (sigma * sigma * sigma)
    z = xp.reshape(xp.asarray(GH_Z, dtype=mu.dtype), (16, 1))
    qgh = xp.reshape(xp.asarray(GH_WEIGHTS, dtype=mu.dtype), (16, 1))
    h3 = z * z * z - 3.0 * z
    density = 1.0 + h3 * xp.reshape(gamma1, (1, -1)) / 6.0
    qw = qgh * density
    x = xp.reshape(mu, (1, -1)) + xp.reshape(sigma, (1, -1)) * z
    y = xp.maximum(x, 0.0)
    y2 = y * y
    y3 = y2 * y
    m1 = xp.sum(qw * y, axis=0)
    m2 = xp.sum(qw * y2, axis=0)
    m3 = xp.sum(qw * y3, axis=0)
    out_var = m2 - m1 * m1
    out_k3 = m3 - 3.0 * m1 * m2 + 2.0 * m1 * m1 * m1
    p, _, _, _ = price_coefficients(xp, mu, var)
    return m1, out_var, out_k3, p, xp.max(xp.abs(gamma1))


def run_carrier(xp, weights):
    n = int(weights[0].shape[0])
    dtype = weights[0].dtype
    mu = xp.zeros(n, dtype=dtype)
    cov = xp.eye(n, dtype=dtype)
    k3_diag = xp.zeros(n, dtype=dtype)
    atoms = xp.zeros((n, 4), dtype=dtype)
    signs = xp.ones(4, dtype=dtype)
    rows = []
    selected = []
    max_skew = xp.asarray(0.0, dtype=dtype)
    max_diag_error = xp.asarray(0.0, dtype=dtype)

    for w_raw in weights:
        w = w_raw.T
        mu_pre = w @ mu
        cov_pre = linear_covariance(xp, w, cov)
        var_pre = xp.diag(cov_pre)

        atoms_pre = w @ atoms
        w2 = w * w
        k3_pre = (w2 * w) @ k3_diag + cp_marginal(xp, atoms_pre, signs)

        newborn, newborn_sign, idx = leverage_birth(xp, w, k3_diag)
        atoms_pre, signs = push_fifo(xp, atoms_pre, signs, newborn, newborn_sign)
        selected.append(idx)

        mu, var_post, k3_total, p, layer_skew = relu_k3_moments(
            xp, mu_pre, var_pre, k3_pre
        )
        p2, q2, r2, s2 = price_coefficients(xp, mu_pre, var_pre)
        cov = covariance_update_price4(xp, cov_pre, p2, q2, r2, s2, var_post)
        diag_error = xp.max(xp.abs(xp.diag(cov) - var_post))
        max_diag_error = xp.maximum(max_diag_error, diag_error)

        atoms = atoms_pre * xp.reshape(p, (-1, 1))
        k3_diag = k3_total - cp_marginal(xp, atoms, signs)
        max_skew = xp.maximum(max_skew, layer_skew)
        rows.append(mu)

    return xp.stack(rows, axis=0), max_skew, selected, max_diag_error


class Estimator(BaseEstimator):
    def setup(self, context: SetupContext) -> None:
        del context

    def predict(self, mlp: MLP, budget: int):
        del budget
        output, _, _, _ = run_carrier(fnp, list(mlp.weights))
        return output
