"""Whitened-antithetic Monte Carlo baseline for E001.

Adapted from the public WhestBench WMC implementation in
Oishi1029/arc-whestbench-2026, ``estimators/wmc.py`` (blob
207b0b3d4bfbee8e9c499ade5ace339b264f91d0).
"""

from __future__ import annotations

import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP

_MAC = 2.0
_EIGH_PER_CUBE = 9.0
_MATMUL_PER_CUBE = 2.0


class WhitenedAntitheticEstimator(BaseEstimator):
    """Moment-matched antithetic Monte Carlo estimator."""

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
        return _MAC * w * w * passes + 2.0 * w * float(depth)

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
        activations = fnp.maximum(
            self._fused_first_layer(samples, first_weight, sample_count),
            fnp.asarray(0.0, dtype=fnp.float32),
        )
        scale = fnp.asarray(1.0 / float(sample_count), dtype=fnp.float32)
        rows = [fnp.sum(activations, axis=0) * scale]

        for weight in mlp.weights[1:]:
            weight32 = fnp.asarray(weight, dtype=fnp.float32)
            activations = fnp.maximum(
                activations @ weight32,
                fnp.asarray(0.0, dtype=fnp.float32),
            )
            rows.append(fnp.sum(activations, axis=0) * scale)

        return fnp.stack(rows, axis=0)

    @staticmethod
    def _fused_first_layer(
        samples: fnp.ndarray,
        first_weight: fnp.ndarray,
        sample_count: int,
    ) -> fnp.ndarray:
        gram = (samples.T @ samples) / fnp.asarray(float(sample_count), dtype=fnp.float32)
        eigenvalues, eigenvectors = fnp.linalg.eigh(gram)
        eigenvalues = fnp.maximum(eigenvalues, 1e-6)
        whitener = (eigenvectors * fnp.power(eigenvalues, -0.5)) @ eigenvectors.T
        return samples @ (whitener @ first_weight)


Estimator = WhitenedAntitheticEstimator
