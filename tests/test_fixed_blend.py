import numpy as np
from numpy.testing import assert_allclose

from baselines.covariance_propagation import CovarianceEstimator
from methods.fixed_blend import FixedBlendEstimator
from methods.whitened_antithetic import WhitenedAntitheticEstimator


class TinyMLP:
    width = 4
    depth = 2
    seed = 12345
    weights = (
        np.asarray(
            [
                [0.2, -0.1, 0.3, 0.4],
                [0.1, 0.5, -0.2, 0.3],
                [-0.4, 0.2, 0.1, 0.2],
                [0.3, -0.3, 0.2, 0.1],
            ],
            dtype=np.float32,
        ),
        np.asarray(
            [
                [0.2, 0.1, -0.2, 0.3],
                [-0.1, 0.4, 0.2, 0.1],
                [0.3, -0.2, 0.5, -0.1],
                [0.1, 0.2, 0.1, 0.4],
            ],
            dtype=np.float32,
        ),
    )


def test_fixed_blend_matches_preregistered_branches() -> None:
    mlp = TinyMLP()
    budget = 2**24
    covariance = np.asarray(CovarianceEstimator().predict(mlp, budget))
    sampling = np.asarray(
        WhitenedAntitheticEstimator(target_utilization=0.075).predict(mlp, budget)
    )
    expected = (
        np.float32(0.75) * covariance + np.float32(0.25) * sampling
    )

    estimator = FixedBlendEstimator()
    actual = np.asarray(estimator.predict(mlp, budget))

    assert estimator.sampling_target_utilization == 0.075
    assert_allclose(actual, expected, rtol=0.0, atol=0.0)
