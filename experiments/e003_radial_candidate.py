"""Submission entry point for the preregistered E003 radial candidate."""

from methods.fourth_moment_antithetic import FourthMomentAntitheticEstimator


class Estimator(FourthMomentAntitheticEstimator):
    """Validator-visible E003 estimator class; no parameter changes."""

    pass
