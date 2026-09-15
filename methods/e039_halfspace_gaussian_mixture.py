from __future__ import annotations

import math

import flopscope as flops
import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP

SQRT_2_OVER_PI = math.sqrt(2.0 / math.pi)
INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)


def frozen_initial_state(xp, n: int):
    dtype = xp.float64
    direction = xp.ones(n, dtype=dtype) / math.sqrt(float(n))
    m_plus = SQRT_2_OVER_PI * direction
    m_minus = -m_plus
    cov = xp.eye(n, dtype=dtype) - (2.0 / math.pi) * xp.outer(direction, direction)
    weights = xp.asarray([0.5, 0.5], dtype=dtype)
    return m_plus, m_minus, cov, weights, direction


def linear_covariance(xp, w, cov):
    return (w @ cov) @ w.T


def _normal_cdf_pdf(xp, alpha):
    if xp is fnp:
        cdf = flops.stats.norm.cdf(alpha)
        pdf = flops.stats.norm.pdf(alpha)
        return cdf, pdf
    erf = xp.vectorize(math.erf)
    cdf = 0.5 * (1.0 + erf(alpha / math.sqrt(2.0)))
    pdf = INV_SQRT_2PI * xp.exp(-0.5 * alpha * alpha)
    return cdf, pdf


def component_relu_moments(xp, mean, var):
    sigma = xp.sqrt(var)
    alpha = mean / sigma
    gain, pdf = _normal_cdf_pdf(xp, alpha)
    post_mean = sigma * pdf + mean * gain
    second = (var + mean * mean) * gain + mean * sigma * pdf
    post_var = second - post_mean * post_mean
    return post_mean, post_var, gain


def update_component_covariance(xp, cov_pre, gain, var_post):
    g = xp.reshape(gain, (-1, 1))
    base = (g * cov_pre) * xp.reshape(gain, (1, -1))
    base = 0.5 * (base + base.T)
    return base + xp.diag(var_post - xp.diag(base))


def run_halfspace_mixture(xp, weights):
    n = int(weights[0].shape[0])
    m_plus, m_minus, cov, mix_weights, direction = frozen_initial_state(xp, n)
    init_mean_error = xp.max(xp.abs(0.5 * m_plus + 0.5 * m_minus))
    init_cov_error = xp.max(xp.abs(cov + xp.outer(m_plus, m_plus) - xp.eye(n, dtype=cov.dtype)))
    max_diag_error = xp.asarray(0.0, dtype=cov.dtype)
    rows = []

    for w_raw in weights:
        w = w_raw.T
        plus_pre = w @ m_plus
        minus_pre = w @ m_minus
        cov_pre = linear_covariance(xp, w, cov)
        var_pre = xp.diag(cov_pre)

        plus_mean, plus_var, plus_gain = component_relu_moments(xp, plus_pre, var_pre)
        minus_mean, minus_var, minus_gain = component_relu_moments(xp, minus_pre, var_pre)

        cov_plus = update_component_covariance(xp, cov_pre, plus_gain, plus_var)
        cov_minus = update_component_covariance(xp, cov_pre, minus_gain, minus_var)
        plus_err = xp.max(xp.abs(xp.diag(cov_plus) - plus_var))
        minus_err = xp.max(xp.abs(xp.diag(cov_minus) - minus_var))
        max_diag_error = xp.maximum(max_diag_error, xp.maximum(plus_err, minus_err))

        cov = 0.5 * cov_plus + 0.5 * cov_minus
        m_plus = plus_mean
        m_minus = minus_mean
        rows.append(0.5 * m_plus + 0.5 * m_minus)

    output = xp.stack(rows, axis=0)
    diagnostics = {
        "component_count": 2,
        "weights": [0.5, 0.5],
        "init_mean_error": float(init_mean_error),
        "init_cov_error": float(init_cov_error),
        "max_diag_error": float(max_diag_error),
        "direction_sum": float(xp.sum(direction)),
    }
    return output, diagnostics


class Estimator(BaseEstimator):
    def setup(self, context: SetupContext) -> None:
        del context

    def predict(self, mlp: MLP, budget: int):
        del budget
        output, _ = run_halfspace_mixture(fnp, list(mlp.weights))
        return output
