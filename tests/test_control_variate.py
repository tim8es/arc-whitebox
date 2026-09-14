import numpy as np
from numpy.testing import assert_allclose

from baselines.covariance_propagation import CovarianceEstimator
from methods.residual_control_variate import ResidualControlVariateEstimator


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


def test_zero_residual_weight_equals_deterministic_branch() -> None:
    mlp = TinyMLP()
    hybrid = ResidualControlVariateEstimator(residual_weight=0.0)
    expected = np.asarray(CovarianceEstimator().predict(mlp, 2**24))
    actual = np.asarray(hybrid.predict(mlp, 2**24))
    assert_allclose(actual, expected, rtol=0.0, atol=0.0)
