"""Parameter-free fourth-moment/radial correction for E003.

The estimator starts from the frozen whitened-antithetic sampler. It restores
pairwise Gaussian radii after the first whitening, normalizes them so empirical
E[r^2] equals the input dimension, then applies one final whitening pass. This
keeps antithetic symmetry and exact empirical covariance while moving radial
fourth moments back toward the Gaussian sample distribution.
"""

from __future__ import annotations

import flopscope.numpy as fnp
from whestbench.domain import MLP

from methods.whitened_antithetic import WhitenedAntitheticEstimator

_MAC = 2.0
_EIGH_PER_CUBE = 9.0
_MATMUL_PER_CUBE = 2.0
_RADIAL_PER_ELEMENT = 10.0


class FourthMomentAntitheticEstimator(WhitenedAntitheticEstimator):
    """Whitened antithetic sampling with parameter-free radial restoration."""

    @staticmethod
    def _fixed_cost(width: int) -> float:
        cube = float(width) ** 3
        # Two eigendecompositions, two whitener constructions, and the final
        # whitener-times-first-weight product used by the fused first layer.
        return 2.0 * _EIGH_PER_CUBE * cube + 3.0 * _MATMUL_PER_CUBE * cube

    @staticmethod
    def _per_sample_cost(width: int, depth: int) -> float:
        w = float(width)
        # Relative to the frozen sampler, radial restoration materializes the
        # first whitened samples and forms a second Gram matrix. The remaining
        # depth propagation is unchanged.
        matrix_passes = float(depth) + 3.0
        return (
            _MAC * w * w * matrix_passes
            + _RADIAL_PER_ELEMENT * w
            + 2.0 * w * float(depth)
        )

    @staticmethod
    def _whitener(samples: fnp.ndarray, sample_count: int) -> fnp.ndarray:
        denom = fnp.asarray(float(sample_count), dtype=fnp.float32)
        gram = (samples.T @ samples) / denom
        eigenvalues, eigenvectors = fnp.linalg.eigh(gram)
        eigenvalues = fnp.maximum(eigenvalues, 1e-6)
        return (eigenvectors * fnp.power(eigenvalues, -0.5)) @ eigenvectors.T

    @classmethod
    def _fused_radial_first_layer(
        cls,
        samples: fnp.ndarray,
        positive: fnp.ndarray,
        first_weight: fnp.ndarray,
        sample_count: int,
        width: int,
    ) -> fnp.ndarray:
        first_whitener = cls._whitener(samples, sample_count)
        whitened = samples @ first_whitener

        half = sample_count // 2
        whitened_positive = whitened[:half]
        raw_radius_sq = fnp.sum(positive * positive, axis=1)
        white_radius_sq = fnp.sum(
            whitened_positive * whitened_positive,
            axis=1,
        )

        mean_raw_radius_sq = fnp.sum(raw_radius_sq) / fnp.asarray(
            float(half), dtype=fnp.float32
        )
        target_radius_sq = raw_radius_sq * (
            fnp.asarray(float(width), dtype=fnp.float32) / mean_raw_radius_sq
        )
        pair_scale = fnp.sqrt(
            target_radius_sq / fnp.maximum(white_radius_sq, 1e-12)
        )
        scales = fnp.concatenate([pair_scale, pair_scale], axis=0)
        radial = whitened * scales[:, None]

        final_whitener = cls._whitener(radial, sample_count)
        return radial @ (final_whitener @ first_weight)

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        width, depth = mlp.width, mlp.depth
        sample_count = self.sample_count(int(budget), width, depth)
        half = sample_count // 2

        rng = fnp.random.default_rng(mlp.seed)
        positive = fnp.asarray(
            rng.standard_normal((half, width)), dtype=fnp.float32
        )
        samples = fnp.concatenate([positive, -positive], axis=0)

        first_weight = fnp.asarray(mlp.weights[0], dtype=fnp.float32)
        pre = self._fused_radial_first_layer(
            samples,
            positive,
            first_weight,
            sample_count,
            width,
        )
        activations = fnp.maximum(pre, fnp.asarray(0.0, dtype=fnp.float32))
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


Estimator = FourthMomentAntitheticEstimator
