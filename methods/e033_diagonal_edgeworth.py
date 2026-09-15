from __future__ import annotations

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


def linear_transport(xp, w, mu, var, k3, k4):
    w2 = w * w
    w3 = w2 * w
    w4 = w2 * w2
    return w @ mu, w2 @ var, w3 @ k3, w4 @ k4


def relu_edgeworth_moments(xp, mu, var, k3, k4):
    safe_var = xp.maximum(var, 1.0e-12)
    sigma = xp.sqrt(safe_var)
    gamma1 = k3 / (sigma * sigma * sigma)
    gamma2 = k4 / (safe_var * safe_var)

    z = xp.asarray(GH_Z, dtype=xp.float64)[:, None]
    base_w = xp.asarray(GH_WEIGHTS, dtype=xp.float64)[:, None]
    h3 = z * z * z - 3.0 * z
    z2 = z * z
    z4 = z2 * z2
    h4 = z4 - 6.0 * z2 + 3.0
    h6 = z4 * z2 - 15.0 * z4 + 45.0 * z2 - 15.0
    density = (
        1.0
        + (h3 * gamma1[None, :]) / 6.0
        + (h4 * gamma2[None, :]) / 24.0
        + (h6 * (gamma1 * gamma1)[None, :]) / 72.0
    )
    qw = base_w * density
    y = mu[None, :] + sigma[None, :] * z
    r = xp.maximum(y, 0.0)
    r2 = r * r
    r3 = r2 * r
    r4 = r2 * r2
    m1 = xp.sum(qw * r, axis=0)
    m2 = xp.sum(qw * r2, axis=0)
    m3 = xp.sum(qw * r3, axis=0)
    m4 = xp.sum(qw * r4, axis=0)

    out_var = m2 - m1 * m1
    out_k3 = m3 - 3.0 * m1 * m2 + 2.0 * m1 * m1 * m1
    central4 = m4 - 4.0 * m1 * m3 + 6.0 * m1 * m1 * m2 - 3.0 * m1**4
    out_k4 = central4 - 3.0 * out_var * out_var
    max_skew = xp.max(xp.abs(gamma1))
    max_kurt = xp.max(xp.abs(gamma2))
    return m1, out_var, out_k3, out_k4, max_skew, max_kurt


def run_carrier(xp, weights):
    n = int(weights[0].shape[1])
    mu = xp.zeros(n, dtype=xp.float64)
    var = xp.ones(n, dtype=xp.float64)
    k3 = xp.zeros(n, dtype=xp.float64)
    k4 = xp.zeros(n, dtype=xp.float64)
    rows = []
    max_skew = xp.asarray(0.0, dtype=xp.float64)
    max_kurt = xp.asarray(0.0, dtype=xp.float64)
    for w in weights:
        mu, var, k3, k4 = linear_transport(xp, w, mu, var, k3, k4)
        mu, var, k3, k4, layer_skew, layer_kurt = relu_edgeworth_moments(
            xp, mu, var, k3, k4
        )
        max_skew = xp.maximum(max_skew, layer_skew)
        max_kurt = xp.maximum(max_kurt, layer_kurt)
        rows.append(mu)
    return xp.stack(rows, axis=0), max_skew, max_kurt


class Estimator(BaseEstimator):
    def setup(self, context: SetupContext) -> None:
        del context

    def predict(self, mlp: MLP, budget: int):
        del budget
        output, _, _ = run_carrier(fnp, list(mlp.weights))
        return output
