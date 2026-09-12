"""E003: exact radial marginalisation for whitened-antithetic sampling.

The bias-free ReLU MLP is positively homogeneous: f(r u) = r f(u).  For a
standard Gaussian input, radius and direction are independent, so the Gaussian
radius can be integrated analytically.  This estimator keeps the E001
whitened-antithetic directions and applies one antithetic-symmetric weight
E[chi_width] / ||x_tilde|| to every layer contribution.

The extra whitened-norm pass is included in the sample-count cost model so the
candidate targets the same 9.9% utilization region as the frozen sampling
baseline.
"""

from __future__ import annotations

import math

import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP

_MAC = 2.0
_EIGH_PER_CUBE = 9.0
_MATMUL_PER_CUBE = 2.0


class RadialMarginalizedAntitheticEstimator(BaseEstimator):
    """Whitened-antithetic Monte Carlo with exact Gaussian radial integration."""

    def __init__(
        self,
        target_utilization: float = 0.099,
        min_samples: int = 512,
        max_samples: int = 400_000,
    ) -> None:
        self.target_utilization = target_utilization
        self.min_samples = min_samples
        self.max_samples = max_samples
        self._setup_rng = None

    def setup(self, ctx: SetupContext) -> None:
        self._setup_rng = fnp.random.default_rng(ctx.seed)

    @staticmethod
    def _fixed_cost(width: int) -> float:
        cube = float(width) ** 3
        return _EIGH_PER_CUBE * cube + 2.0 * _MATMUL_PER_CUBE * cube

    @staticmethod
    def _per_sample_cost(width: int, depth: int) -> float:
        w = float(width)
        passes = float(depth) + 1.0
        baseline = _MAC * w * w * passes + 2.0 * w * float(depth)
        # Recovering whitened norms costs one half-sample matmul: k/2 x w by
        # w x w => k*w^2 FLOPs in total.  Weighted layer reductions add one
        # multiply per activation; 4*w is conservative slack for norm work.
        radial = w * w + float(depth) * w + 4.0 * w
        return baseline + radial

    def sample_count(self, budget: int, width: int, depth: int) -> int:
        spend = self.target_utilization * float(budget) - self._fixed_cost(width)
        estimated = int(spend / self._per_sample_cost(width, depth))
        bounded = max(self.min_samples, min(self.max_samples, estimated))
        return max(2, (bounded // 2) * 2)

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        width, depth = mlp.width, mlp.depth
        sample_count = self.sample_count(int(budget), width, depth)
        half = sample_count // 2

        rng = fnp.random.default_rng(mlp.seed)
        positive = fnp.asarray(rng.standard_normal((half, width)), dtype=fnp.float32)
        samples = fnp.concatenate([positive, -positive], axis=0)

        first_weight = fnp.asarray(mlp.weights[0], dtype=fnp.float32)
        first, half_whitener = self._fused_first_layer(
            samples, first_weight, sample_count
        )
        radial_weights = self._radial_weights(positive, half_whitener, width)

        zero = fnp.asarray(0.0, dtype=fnp.float32)
        activations = fnp.maximum(first, zero)
        scale = fnp.asarray(1.0 / float(sample_count), dtype=fnp.float32)
        rows = [self._weighted_sum(activations, radial_weights) * scale]

        for weight in mlp.weights[1:]:
            weight32 = fnp.asarray(weight, dtype=fnp.float32)
            activations = fnp.maximum(activations @ weight32, zero)
            rows.append(self._weighted_sum(activations, radial_weights) * scale)

        return fnp.stack(rows, axis=0)

    @staticmethod
    def _weighted_sum(activations: fnp.ndarray, weights: fnp.ndarray) -> fnp.ndarray:
        return fnp.sum(activations * weights[:, None], axis=0)

    @staticmethod
    def _fused_first_layer(
        samples: fnp.ndarray,
        first_weight: fnp.ndarray,
        sample_count: int,
    ) -> tuple[fnp.ndarray, fnp.ndarray]:
        gram = (samples.T @ samples) / fnp.asarray(
            float(sample_count), dtype=fnp.float32
        )
        eigenvalues, eigenvectors = fnp.linalg.eigh(gram)
        eigenvalues = fnp.maximum(eigenvalues, 1e-6)
        inv_sqrt = fnp.power(eigenvalues, -0.5)
        half_whitener = eigenvectors * inv_sqrt
        whitener = half_whitener @ eigenvectors.T
        first = samples @ (whitener @ first_weight)
        return first, half_whitener

    @staticmethod
    def _radial_weights(
        positive: fnp.ndarray,
        half_whitener: fnp.ndarray,
        width: int,
    ) -> fnp.ndarray:
        transformed = positive @ half_whitener
        radius_sq = fnp.sum(transformed * transformed, axis=1)
        mean_radius = math.sqrt(2.0) * math.exp(
            math.lgamma((width + 1) / 2.0) - math.lgamma(width / 2.0)
        )
        half_weights = fnp.asarray(mean_radius, dtype=fnp.float32) / fnp.sqrt(
            fnp.maximum(radius_sq, fnp.asarray(1e-12, dtype=fnp.float32))
        )
        return fnp.concatenate([half_weights, half_weights], axis=0)


Estimator = RadialMarginalizedAntitheticEstimator
