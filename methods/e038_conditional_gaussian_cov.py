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

INV_SQRT_2PI = 0.3989422804014327
INV_SQRT2 = 0.7071067811865476
COND_EPS = 1.0e-15


def _norm_pdf(xp, x):
    return INV_SQRT_2PI * xp.exp(-0.5 * x * x)


def _norm_cdf(xp, x):
    if xp is fnp:
        return flops.stats.norm.cdf(x)
    flat = xp.asarray(x).reshape(-1)
    values = [0.5 * (1.0 + math.erf(float(v) * INV_SQRT2)) for v in flat]
    return xp.asarray(values, dtype=x.dtype).reshape(x.shape)


def _gaussian_relu_raw(xp, mu, var):
    sigma = xp.sqrt(var)
    alpha = mu / sigma
    phi = _norm_pdf(xp, alpha)
    cdf = _norm_cdf(xp, alpha)
    mean = sigma * phi + mu * cdf
    second = (mu * mu + var) * cdf + mu * sigma * phi
    return mean, second


def gaussian_relu_moments(xp, mu, var):
    mean, second = _gaussian_relu_raw(xp, mu, var)
    return mean, second - mean * mean


def linear_covariance(xp, w, cov):
    return (w @ cov) @ w.T


def conditional_second_moment(xp, mu, cov):
    var = xp.diag(cov)
    sigma = xp.sqrt(var)
    sigma_i = xp.reshape(sigma, (-1, 1))
    sigma_j = xp.reshape(sigma, (1, -1))
    rho = cov / (sigma_i * sigma_j)
    max_abs_corr = xp.max(xp.abs(rho))
    rho = xp.minimum(1.0, xp.maximum(-1.0, rho))

    cond_sigma = sigma_j * xp.sqrt(xp.maximum(1.0 - rho * rho, COND_EPS))
    mu_i = xp.reshape(mu, (-1, 1))
    mu_j = xp.reshape(mu, (1, -1))

    second = xp.zeros_like(cov)
    for z, q in zip(GH_Z, GH_WEIGHTS, strict=True):
        relu_x = xp.maximum(mu_i + sigma_i * z, 0.0)
        cond_mean = mu_j + (sigma_j * rho) * z
        cond_alpha = cond_mean / cond_sigma
        cond_relu = cond_sigma * _norm_pdf(xp, cond_alpha) + cond_mean * _norm_cdf(
            xp, cond_alpha
        )
        second = second + q * relu_x * cond_relu

    second = 0.5 * (second + second.T)
    mean, marginal_second = _gaussian_relu_raw(xp, mu, var)
    independent = rho == 0.0
    mean_outer = xp.reshape(mean, (-1, 1)) * xp.reshape(mean, (1, -1))
    second = xp.where(independent, mean_outer, second)
    second = second + xp.diag(marginal_second - xp.diag(second))
    return second, max_abs_corr


def run_carrier(xp, weights):
    n = int(weights[0].shape[0])
    dtype = weights[0].dtype
    mu = xp.zeros(n, dtype=dtype)
    cov = xp.eye(n, dtype=dtype)
    rows = []
    max_diag_error = xp.asarray(0.0, dtype=dtype)
    max_abs_corr = xp.asarray(0.0, dtype=dtype)

    for w_raw in weights:
        w = w_raw.T
        mu_pre = w @ mu
        cov_pre = linear_covariance(xp, w, cov)
        var_pre = xp.diag(cov_pre)
        mu, var_post = gaussian_relu_moments(xp, mu_pre, var_pre)
        second, layer_corr = conditional_second_moment(xp, mu_pre, cov_pre)
        mean_outer = xp.reshape(mu, (-1, 1)) * xp.reshape(mu, (1, -1))
        base = second - mean_outer
        cov = base + xp.diag(var_post - xp.diag(base))
        diag_error = xp.max(xp.abs(xp.diag(cov) - var_post))
        max_diag_error = xp.maximum(max_diag_error, diag_error)
        max_abs_corr = xp.maximum(max_abs_corr, layer_corr)
        rows.append(mu)

    return xp.stack(rows, axis=0), max_diag_error, max_abs_corr


class Estimator(BaseEstimator):
    def setup(self, context: SetupContext) -> None:
        del context

    def predict(self, mlp: MLP, budget: int):
        del budget
        output, _, _ = run_carrier(fnp, list(mlp.weights))
        return output
