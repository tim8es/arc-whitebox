"""Fourth-moment/radial correction for the whitened-antithetic sampler.

The correction adaptively rotates consecutive sample-row pairs before the
existing whitening step. Each rotation is orthogonal, so the sample Gram matrix
is unchanged exactly; antithetic concatenation still makes the mean and odd
moments zero. Only fourth and higher sample moments are changed.
"""

from __future__ import annotations

import flopscope.numpy as fnp
from whestbench.domain import MLP

from methods.whitened_antithetic import WhitenedAntitheticEstimator


class RadialFourthMomentEstimator(WhitenedAntitheticEstimator):
    """Whitened-antithetic MC with a Gram-preserving radial spread correction."""

    def __init__(self, radial_strength: float = 0.5, **kwargs: object) -> None:
        super().__init__(**kwargs)
        if not 0.0 <= radial_strength <= 1.0:
            raise ValueError("radial_strength must be in [0, 1]")
        self.radial_strength = float(radial_strength)

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        width, depth = mlp.width, mlp.depth
        sample_count = self.sample_count(int(budget), width, depth)
        half = sample_count // 2

        rng = fnp.random.default_rng(mlp.seed)
        positive = fnp.asarray(rng.standard_normal((half, width)), dtype=fnp.float32)
        positive = self._spread_pairs(positive, self.radial_strength)
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
    def _spread_pairs(positive: fnp.ndarray, strength: float) -> fnp.ndarray:
        """Increase pairwise radial spread while preserving the row Gram matrix.

        For each row pair, the full-strength rotation diagonalizes its 2x2 Gram
        block, maximizing the difference between the two row norms. Intermediate
        strengths interpolate from the identity rotation and renormalize back to
        an orthogonal 2x2 rotation.
        """
        if strength <= 0.0 or positive.shape[0] < 2:
            return positive

        pair_rows = (positive.shape[0] // 2) * 2
        paired = positive[:pair_rows]
        a = paired[0::2]
        b = paired[1::2]

        norm_a = fnp.sum(a * a, axis=1, keepdims=True)
        norm_b = fnp.sum(b * b, axis=1, keepdims=True)
        twice_cross = fnp.asarray(2.0, dtype=fnp.float32) * fnp.sum(
            a * b, axis=1, keepdims=True
        )
        difference = norm_a - norm_b
        radius = fnp.sqrt(
            fnp.maximum(
                difference * difference + twice_cross * twice_cross,
                fnp.asarray(1e-20, dtype=fnp.float32),
            )
        )

        cos2 = difference / radius
        sin2 = twice_cross / radius
        one = fnp.asarray(1.0, dtype=fnp.float32)
        half = fnp.asarray(0.5, dtype=fnp.float32)
        zero = fnp.asarray(0.0, dtype=fnp.float32)

        cos_eq = fnp.sqrt(fnp.maximum((one + cos2) * half, zero))
        sin_mag = fnp.sqrt(fnp.maximum((one - cos2) * half, zero))
        sin_sign = fnp.where(sin2 >= zero, one, -one)
        sin_eq = sin_sign * sin_mag

        lam = fnp.asarray(float(strength), dtype=fnp.float32)
        cos_raw = (one - lam) + lam * cos_eq
        sin_raw = lam * sin_eq
        rotation_norm = fnp.sqrt(cos_raw * cos_raw + sin_raw * sin_raw)
        cos_theta = cos_raw / rotation_norm
        sin_theta = sin_raw / rotation_norm

        spread_a = cos_theta * a + sin_theta * b
        spread_b = -sin_theta * a + cos_theta * b
        spread = fnp.reshape(
            fnp.stack([spread_a, spread_b], axis=1),
            (pair_rows, positive.shape[1]),
        )

        if pair_rows == positive.shape[0]:
            return spread
        return fnp.concatenate([spread, positive[pair_rows:]], axis=0)


Estimator = RadialFourthMomentEstimator
