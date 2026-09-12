from estimator import Estimator
from whestbench import BaseEstimator


def test_estimator_entrypoint_is_valid_base_estimator() -> None:
    assert issubclass(Estimator, BaseEstimator)
