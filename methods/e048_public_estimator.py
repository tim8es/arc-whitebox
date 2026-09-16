from __future__ import annotations

import math

import flopscope as flops
import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP

PAIR_FACTOR_NUMERATOR_OFFSET = 1.0
CORE_GEMM_EQUIVALENTS = 4
TOTAL_GEMM_EQUIVALENTS = 7
BUDGET = 2**41


class SourceFreeResponseEstimator(BaseEstimator):
    def __init__(self) -> None:
        self._setup_rng = None
        self._e048_state_ranks: list[tuple[int, int, int]] = []
        self._e048_state_shapes: list[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]] = []
        self._e048_max_abs_state = 0.0
        self._e048_core_projected_utilization = 0.0

    def setup(self, ctx: SetupContext) -> None:
        self._setup_rng = fnp.random.default_rng(ctx.seed)

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        _ = budget
        width = int(mlp.width)
        depth = int(mlp.depth)
        mu = fnp.zeros(width, dtype=fnp.float64)
        cov = flops.as_symmetric(fnp.eye(width, dtype=fnp.float64), symmetry=(0, 1))
        d3 = fnp.zeros(width, dtype=fnp.float64)
        d21 = fnp.zeros((width, width), dtype=fnp.float64)
        r4 = fnp.zeros(width, dtype=fnp.float64)
        pair_factor = 1.0 - PAIR_FACTOR_NUMERATOR_OFFSET / (2.0 * float(width))
        inv_sqrt_2pi = 1.0 / math.sqrt(2.0 * math.pi)
        rows = []

        for weight in mlp.weights:
            mu_pre = weight.T @ mu
            cov_pre = fnp.einsum("ij,ia,jb->ab", cov, weight, weight)
            var_pre = fnp.maximum(fnp.diag(cov_pre), 1e-15)
            sigma_pre = fnp.sqrt(var_pre)
            denom = fnp.outer(sigma_pre, sigma_pre)
            corr = cov_pre / denom

            alpha = mu_pre / sigma_pre
            phi = flops.stats.norm.pdf(alpha).astype(fnp.float64)
            Phi = flops.stats.norm.cdf(alpha).astype(fnp.float64)
            mu_g = mu_pre * Phi + sigma_pre * phi
            ez2 = (mu_pre * mu_pre + var_pre) * Phi + mu_pre * sigma_pre * phi
            var_post = fnp.maximum(ez2 - mu_g * mu_g, 0.0)
            gain = Phi
            cov = fnp.multiply(fnp.outer(gain, gain), cov_pre)
            fnp.fill_diagonal(cov, var_post)
            cov = flops.as_symmetric(cov, symmetry=(0, 1))

            # Source-free response transport. D21 uses exactly two dense GEMMs;
            # D3 and R4 use diagonal multilinear contractions only.
            d21_pre = weight.T @ d21 @ weight
            d21_pre = d21_pre / (fnp.outer(sigma_pre, sigma_pre) * sigma_pre[:, None])
            d3_pre = (weight * weight * weight).T @ d3
            d3_pre = d3_pre / (sigma_pre * sigma_pre * sigma_pre)
            r4_pre = (weight * weight * weight * weight).T @ r4
            r4_pre = r4_pre / (var_pre * var_pre)

            angular_derivative = (math.pi - fnp.arccos(corr)) / (2.0 * math.pi)
            pair_birth = angular_derivative * corr * (1.0 - corr * corr)
            d21 = d21_pre + pair_factor * pair_birth

            # Exact zero-bias half-normal cumulants are fixed analytic constants.
            m1 = inv_sqrt_2pi
            m2 = 0.5
            m3 = math.sqrt(2.0 / math.pi)
            m4 = 1.5
            k3_birth = m3 - 3.0 * m2 * m1 + 2.0 * m1**3
            central4 = m4 - 4.0 * m3 * m1 + 6.0 * m2 * m1**2 - 3.0 * m1**4
            k4_birth = central4 - 3.0 * (m2 - m1**2) ** 2
            d3 = d3_pre + k3_birth
            r4 = r4_pre + k4_birth

            pair_mean_response = fnp.mean(d21, axis=1)
            correction = sigma_pre * (
                pair_mean_response * (inv_sqrt_2pi / 12.0)
                - r4 * (inv_sqrt_2pi / 24.0)
            )
            mu = mu_g + correction
            fnp.fill_diagonal(cov, fnp.maximum(var_post + mu_g * mu_g - mu * mu, 0.0))
            cov = flops.as_symmetric(cov, symmetry=(0, 1))

            self._e048_state_ranks.append((d3.ndim, d21.ndim, r4.ndim))
            self._e048_state_shapes.append((tuple(d3.shape), tuple(d21.shape), tuple(r4.shape)))
            self._e048_max_abs_state = max(
                self._e048_max_abs_state,
                float(fnp.max(fnp.abs(d3))),
                float(fnp.max(fnp.abs(d21))),
                float(fnp.max(fnp.abs(r4))),
            )
            rows.append(mu)

        gemm = 2.0 * width**3
        core_flops = CORE_GEMM_EQUIVALENTS * depth * gemm + 24.0 * depth * width**2
        self._e048_core_projected_utilization = float(core_flops / BUDGET)
        return fnp.stack(rows, axis=0)


Estimator = SourceFreeResponseEstimator
