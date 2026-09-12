from whestbench import BaseEstimator

from estimator import Estimator


def test_estimator_entrypoint_is_valid_base_estimator() -> None:
    assert issubclass(Estimator, BaseEstimator)
