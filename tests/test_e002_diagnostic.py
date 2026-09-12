import numpy as np
from numpy.testing import assert_allclose

from scripts.e002_diagnostic import fit_ridge_rule, oracle_covariance_weight


def test_oracle_covariance_weight_recovers_known_scalar() -> None:
    sampling = np.asarray([0.0, 0.0, 0.0], dtype=np.float64)
    covariance = np.asarray([1.0, 2.0, -1.0], dtype=np.float64)
    target = 0.25 * covariance

    weight = oracle_covariance_weight(target, covariance, sampling)

    assert_allclose(weight, 0.25, rtol=0.0, atol=1e-12)


def test_oracle_covariance_weight_clips_to_unit_interval() -> None:
    sampling = np.asarray([0.0, 0.0], dtype=np.float64)
    covariance = np.asarray([1.0, 1.0], dtype=np.float64)

    assert oracle_covariance_weight(2.0 * covariance, covariance, sampling) == 1.0
    assert oracle_covariance_weight(-covariance, covariance, sampling) == 0.0


def test_ridge_rule_recovers_low_capacity_linear_signal() -> None:
    x = np.asarray(
        [
            [-2.0, 0.0],
            [-1.0, 1.0],
            [0.0, -1.0],
            [1.0, 0.5],
            [2.0, -0.5],
            [3.0, 1.5],
        ],
        dtype=np.float64,
    )
    y = 0.7 + 0.04 * x[:, 0] - 0.02 * x[:, 1]

    fitted = fit_ridge_rule(x, y, lambdas=(0.0, 1.0, 10.0))
    pred = fitted.predict(x)

    assert fitted.ridge_lambda == 0.0
    assert_allclose(pred, y, rtol=0.0, atol=1e-10)
