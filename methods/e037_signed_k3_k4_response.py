from __future__ import annotations

import flopscope as flops
import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP

GH_Z = (
    -6.6308781983931295, -5.472225705949343, -4.492955302520012,
    -3.6008736241715487, -2.760245047630702, -1.9519803457163336,
    -1.1638291005549648, -0.3867606045005574, 0.3867606045005574,
    1.1638291005549648, 1.9519803457163336, 2.760245047630702,
    3.6008736241715487, 4.492955302520012, 5.472225705949343,
    6.6308781983931295,
)

GH_WEIGHTS = (
    1.4978147231618314e-10, 1.3094732162868187e-07,
    1.5300032162487316e-05, 0.0005259849265739094,
    0.007266937601184743, 0.04728475235401403,
    0.15833837275094964, 0.28656852123801213,
    0.28656852123801213, 0.15833837275094964,
    0.04728475235401403, 0.007266937601184743,
    0.0005259849265739094, 1.5300032162487316e-05,
    1.3094732162868187e-07, 1.4978147231618314e-10,
)

RANK = 4


def cp_marginal3(xp, atoms, signs):
    return xp.sum((atoms * atoms * atoms) * xp.reshape(signs, (1, -1)), axis=1)


def cp_marginal4(xp, atoms, signs):
    a2 = atoms * atoms
    return xp.sum((a2 * a2) * xp.reshape(signs, (1, -1)), axis=1)


def leverage_birth3(xp, w, k3_diag):
    scores = xp.abs(k3_diag) * xp.sum(xp.abs(w) ** 3, axis=0)
    idx = int(xp.argmax(scores))
    kval = k3_diag[idx]
    sign = xp.where(kval < 0.0, -1.0, 1.0)
    scale = xp.abs(kval) ** (1.0 / 3.0)
    return w[:, idx] * scale, sign, idx


def leverage_birth4(xp, w, k4_diag):
    aw = xp.abs(w)
    aw2 = aw * aw
    scores = xp.abs(k4_diag) * xp.sum(aw2 * aw2, axis=0)
    idx = int(xp.argmax(scores))
    kval = k4_diag[idx]
    sign = xp.where(kval < 0.0, -1.0, 1.0)
    scale = xp.abs(kval) ** 0.25
    return w[:, idx] * scale, sign, idx


def push_fifo(xp, atoms, signs, atom, sign):
    return (
        xp.concatenate([atoms[:, 1:], xp.reshape(atom, (-1, 1))], axis=1),
        xp.concatenate([signs[1:], xp.reshape(sign, (1,))], axis=0),
    )


def linear_covariance(xp, w, cov):
    return (w @ cov) @ w.T


def connected_k4_from_raw(xp, m1, m2, m3, m4):
    del xp
    central4 = m4 - 4.0 * m1 * m3 + 6.0 * m1 * m1 * m2 - 3.0 * m1**4
    var = m2 - m1 * m1
    return central4 - 3.0 * var * var


def _gaussian_gain(xp, mu, sigma, z, q):
    if xp is fnp:
        return flops.stats.norm.cdf(mu / sigma)
    x = xp.reshape(mu, (1, -1)) + xp.reshape(sigma, (1, -1)) * z
    return xp.sum(q * (x > 0.0), axis=0)


def relu_k3_k4_moments(xp, mu, var, k3, k4):
    sigma = xp.sqrt(var)
    s2 = sigma * sigma
    gamma1 = k3 / (s2 * sigma)
    gamma2 = k4 / (s2 * s2)
    z = xp.reshape(xp.asarray(GH_Z, dtype=mu.dtype), (16, 1))
    q = xp.reshape(xp.asarray(GH_WEIGHTS, dtype=mu.dtype), (16, 1))
    z2 = z * z
    h3 = z * z2 - 3.0 * z
    h4 = z2 * z2 - 6.0 * z2 + 3.0
    density = (
        1.0
        + h3 * xp.reshape(gamma1, (1, -1)) / 6.0
        + h4 * xp.reshape(gamma2, (1, -1)) / 24.0
    )
    qw = q * density
    x = xp.reshape(mu, (1, -1)) + xp.reshape(sigma, (1, -1)) * z
    y = xp.maximum(x, 0.0)
    y2 = y * y
    y3 = y2 * y
    y4 = y2 * y2
    m1 = xp.sum(qw * y, axis=0)
    m2 = xp.sum(qw * y2, axis=0)
    m3 = xp.sum(qw * y3, axis=0)
    m4 = xp.sum(qw * y4, axis=0)
    out_var = m2 - m1 * m1
    out_k3 = m3 - 3.0 * m1 * m2 + 2.0 * m1 * m1 * m1
    out_k4 = connected_k4_from_raw(xp, m1, m2, m3, m4)
    gain = _gaussian_gain(xp, mu, sigma, z, q)
    return (
        m1,
        out_var,
        out_k3,
        out_k4,
        gain,
        xp.max(xp.abs(gamma1)),
        xp.max(xp.abs(gamma2)),
    )


def covariance_update(xp, cov_pre, gain, var_post):
    g = xp.reshape(gain, (-1, 1))
    base = (g * cov_pre) * xp.reshape(gain, (1, -1))
    base = 0.5 * (base + base.T)
    return base + xp.diag(var_post - xp.diag(base))


def run_carrier(xp, weights):
    n = int(weights[0].shape[0])
    dtype = weights[0].dtype
    mu = xp.zeros(n, dtype=dtype)
    cov = xp.eye(n, dtype=dtype)
    k3_diag = xp.zeros(n, dtype=dtype)
    k4_diag = xp.zeros(n, dtype=dtype)
    atoms3 = xp.zeros((n, RANK), dtype=dtype)
    atoms4 = xp.zeros((n, RANK), dtype=dtype)
    signs3 = xp.ones(RANK, dtype=dtype)
    signs4 = xp.ones(RANK, dtype=dtype)
    rows = []
    selected3 = []
    selected4 = []
    max_skew = xp.asarray(0.0, dtype=dtype)
    max_kurt = xp.asarray(0.0, dtype=dtype)
    max_diag_error = xp.asarray(0.0, dtype=dtype)

    for w_raw in weights:
        w = w_raw.T
        mu_pre = w @ mu
        cov_pre = linear_covariance(xp, w, cov)
        var_pre = xp.diag(cov_pre)

        atoms3_pre = w @ atoms3
        w2 = w * w
        k3_pre = (w2 * w) @ k3_diag + cp_marginal3(xp, atoms3_pre, signs3)
        newborn3, sign3, idx3 = leverage_birth3(xp, w, k3_diag)
        atoms3_pre, signs3 = push_fifo(xp, atoms3_pre, signs3, newborn3, sign3)
        selected3.append(idx3)

        atoms4_pre = w @ atoms4
        w4 = w2 * w2
        k4_pre = w4 @ k4_diag + cp_marginal4(xp, atoms4_pre, signs4)
        newborn4, sign4, idx4 = leverage_birth4(xp, w, k4_diag)
        atoms4_pre, signs4 = push_fifo(xp, atoms4_pre, signs4, newborn4, sign4)
        selected4.append(idx4)

        mu, var_post, k3_total, k4_total, gain, layer_skew, layer_kurt = relu_k3_k4_moments(
            xp, mu_pre, var_pre, k3_pre, k4_pre
        )
        cov = covariance_update(xp, cov_pre, gain, var_post)
        diag_error = xp.max(xp.abs(xp.diag(cov) - var_post))
        max_diag_error = xp.maximum(max_diag_error, diag_error)

        response = xp.reshape(gain, (-1, 1))
        atoms3 = atoms3_pre * response
        atoms4 = atoms4_pre * response
        k3_diag = k3_total - cp_marginal3(xp, atoms3, signs3)
        k4_diag = k4_total - cp_marginal4(xp, atoms4, signs4)
        max_skew = xp.maximum(max_skew, layer_skew)
        max_kurt = xp.maximum(max_kurt, layer_kurt)
        rows.append(mu)

    return (
        xp.stack(rows, axis=0),
        max_skew,
        max_kurt,
        selected3,
        selected4,
        max_diag_error,
    )


class Estimator(BaseEstimator):
    def setup(self, context: SetupContext) -> None:
        del context

    def predict(self, mlp: MLP, budget: int):
        del budget
        output, _, _, _, _, _ = run_carrier(fnp, list(mlp.weights))
        return output
