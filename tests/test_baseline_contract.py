from baselines.covariance_propagation import CovarianceEstimator


def test_covariance_estimator_is_submission_estimator() -> None:
    assert hasattr(CovarianceEstimator, "predict")
