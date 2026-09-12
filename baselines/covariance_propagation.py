"""Official Phase-2 covariance-propagation baseline, vendored for research.

Upstream: AIcrowd/whest-starterkit
Path: examples/03_covariance_propagation.py
Commit: 3e1e3b5f3da3e03a128ff292d0b14251727aeb5e
License: MIT

The implementation is kept mathematically equivalent to the pinned official
example; only the estimator class name is changed for the local research API.
"""

from __future__ import annotations

import flopscope as flops
import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP

_COV_RESCALE_THRESHOLD = 1e30


class CovarianceEstimator(BaseEstimator):
    """Propagate full covariance with exact marginal ReLU moments."""

    def __init__(self) -> None:
        self._setup_rng = None

    def setup(self, ctx: SetupContext) -> None:
        self._setup_rng = fnp.random.default_rng(ctx.seed)

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        _rng = fnp.random.default_rng(mlp.seed)
        _ = _rng
        _ = budget
        width = mlp.width

        mu = fnp.zeros(width, dtype=fnp.float32)
        cov = flops.as_symmetric(
            fnp.eye(width, dtype=fnp.float32), symmetry=(0, 1)
        )
        log_scale = 0.0

        rows = []
        for weight in mlp.weights:
            cov_diag = fnp.diag(cov)
            max_var_np = float(fnp.max(cov_diag))
            if max_var_np > _COV_RESCALE_THRESHOLD:
                scale = float(fnp.sqrt(max_var_np))
                mu = mu / scale
                cov = cov / (scale * scale)
                log_scale += float(fnp.log(scale))

            mu_pre = weight.T @ mu
            cov_pre = fnp.einsum("ij,ia,jb->ab", cov, weight, weight)

            var_pre = fnp.maximum(fnp.diag(cov_pre), 1e-12)
            sigma_pre = fnp.sqrt(var_pre)
            alpha = mu_pre / sigma_pre
            phi_alpha = flops.stats.norm.pdf(alpha).astype(fnp.float32)
            Phi_alpha = flops.stats.norm.cdf(alpha).astype(fnp.float32)

            mu = mu_pre * Phi_alpha + sigma_pre * phi_alpha
            ez2 = (
                (mu_pre * mu_pre + var_pre) * Phi_alpha
                + mu_pre * sigma_pre * phi_alpha
            )
            var_post = fnp.maximum(ez2 - mu * mu, 0.0)

            zero32 = fnp.zeros((), dtype=fnp.float32)
            gain = fnp.where(sigma_pre > 1e-12, Phi_alpha, zero32)
            cov = fnp.multiply(fnp.outer(gain, gain), cov_pre)
            fnp.fill_diagonal(cov, var_post)
            cov = flops.as_symmetric(cov, symmetry=(0, 1))

            scale_factor = float(fnp.exp(log_scale))
            rows.append(mu * scale_factor)

        return fnp.stack(rows, axis=0)


Estimator = CovarianceEstimator
