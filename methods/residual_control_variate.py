"""Residual control-variate estimator for E001.

The deterministic branch is the official Phase-2 covariance propagation model.
Whitened-antithetic trajectories estimate a residual, while each layer's
pre-activation sample mean acts as a control variate with Gaussian ReLU gain
Phi(alpha). The sampling target leaves room for the covariance branch so total
measured utilization remains below the 10% score-floor target.
"""

from __future__ import annotations

import flopscope as flops
import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP

from baselines.covariance_propagation import CovarianceEstimator

_COV_RESCALE_THRESHOLD = 1e30
_MAC = 2.0
_EIGH_PER_CUBE = 9.0
_MATMUL_PER_CUBE = 2.0


class ResidualControlVariateEstimator(BaseEstimator):
    """Covariance prediction plus a whitened-antithetic control-variate residual."""

    def __init__(
        self,
        residual_weight: float = 1.0,
        target_sampling_utilization: float = 0.075,
        min_samples: int = 512,
        max_samples: int = 400_000,
    ) -> None:
        self.residual_weight = residual_weight
        self.target_sampling_utilization = target_sampling_utilization
        self.min_samples = min_samples
        self.max_samples = max_samples
        self._setup_rng = None

    def setup(self, ctx: SetupContext) -> None:
        self._setup_rng = fnp.random.default_rng(ctx.seed)

    @staticmethod
    def _fixed_sampling_cost(width: int) -> float:
        cube = float(width) ** 3
        return _EIGH_PER_CUBE * cube + 2.0 * _MATMUL_PER_CUBE * cube

    @staticmethod
    def _per_sample_cost(width: int, depth: int) -> float:
        w = float(width)
        passes = float(depth) + 1.0
        return _MAC * w * w * passes + 2.0 * w * float(depth)

    def sample_count(self, budget: int, width: int, depth: int) -> int:
        spend = (
            self.target_sampling_utilization * float(budget)
            - self._fixed_sampling_cost(width)
        )
        estimated = int(spend / self._per_sample_cost(width, depth))
        bounded = max(self.min_samples, min(self.max_samples, estimated))
        return max(2, (bounded // 2) * 2)

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        if self.residual_weight == 0.0:
            return CovarianceEstimator().predict(mlp, budget)

        deterministic, pre_means, gains = self._deterministic_controls(mlp)
        sample_count = self.sample_count(int(budget), mlp.width, mlp.depth)
        scale = fnp.asarray(1.0 / float(sample_count), dtype=fnp.float32)

        rng = fnp.random.default_rng(mlp.seed)
        half = sample_count // 2
        positive = fnp.asarray(
            rng.standard_normal((half, mlp.width)), dtype=fnp.float32
        )
        samples = fnp.concatenate([positive, -positive], axis=0)

        first_weight = fnp.asarray(mlp.weights[0], dtype=fnp.float32)
        pre = self._fused_whitened_first_layer(samples, first_weight, sample_count)
        activations = fnp.maximum(pre, fnp.asarray(0.0, dtype=fnp.float32))

        rows = [
            self._combine_layer(
                deterministic[0],
                pre_means[0],
                gains[0],
                pre,
                activations,
                scale,
            )
        ]

        for layer, weight in enumerate(mlp.weights[1:], start=1):
            weight32 = fnp.asarray(weight, dtype=fnp.float32)
            pre = activations @ weight32
            activations = fnp.maximum(pre, fnp.asarray(0.0, dtype=fnp.float32))
            rows.append(
                self._combine_layer(
                    deterministic[layer],
                    pre_means[layer],
                    gains[layer],
                    pre,
                    activations,
                    scale,
                )
            )

        return fnp.stack(rows, axis=0)

    def _combine_layer(
        self,
        deterministic_mean: fnp.ndarray,
        deterministic_pre_mean: fnp.ndarray,
        gain: fnp.ndarray,
        sample_pre: fnp.ndarray,
        sample_activation: fnp.ndarray,
        scale: fnp.ndarray,
    ) -> fnp.ndarray:
        sample_pre_mean = fnp.sum(sample_pre, axis=0) * scale
        sample_activation_mean = fnp.sum(sample_activation, axis=0) * scale
        control_adjusted = sample_activation_mean - gain * (
            sample_pre_mean - deterministic_pre_mean
        )
        residual = control_adjusted - deterministic_mean
        return deterministic_mean + self.residual_weight * residual

    @staticmethod
    def _fused_whitened_first_layer(
        samples: fnp.ndarray,
        first_weight: fnp.ndarray,
        sample_count: int,
    ) -> fnp.ndarray:
        gram = (samples.T @ samples) / fnp.asarray(
            float(sample_count), dtype=fnp.float32
        )
        eigenvalues, eigenvectors = fnp.linalg.eigh(gram)
        eigenvalues = fnp.maximum(eigenvalues, 1e-6)
        whitener = (
            eigenvectors * fnp.power(eigenvalues, -0.5)
        ) @ eigenvectors.T
        return samples @ (whitener @ first_weight)

    @staticmethod
    def _deterministic_controls(
        mlp: MLP,
    ) -> tuple[fnp.ndarray, tuple[fnp.ndarray, ...], tuple[fnp.ndarray, ...]]:
        width = mlp.width
        mu = fnp.zeros(width, dtype=fnp.float32)
        cov = flops.as_symmetric(
            fnp.eye(width, dtype=fnp.float32), symmetry=(0, 1)
        )
        log_scale = 0.0
        rows = []
        pre_rows = []
        gain_rows = []

        for weight in mlp.weights:
            cov_diag = fnp.diag(cov)
            max_var_np = float(fnp.max(cov_diag))
            if max_var_np > _COV_RESCALE_THRESHOLD:
                rescale = float(fnp.sqrt(max_var_np))
                mu = mu / rescale
                cov = cov / (rescale * rescale)
                log_scale += float(fnp.log(rescale))

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
            pre_rows.append(mu_pre * scale_factor)
            gain_rows.append(gain)

        return fnp.stack(rows, axis=0), tuple(pre_rows), tuple(gain_rows)


Estimator = ResidualControlVariateEstimator
