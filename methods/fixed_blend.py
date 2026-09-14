"""Fixed analytic/sampling blend baseline for E002."""

from __future__ import annotations

import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP

from baselines.covariance_propagation import CovarianceEstimator
from methods.whitened_antithetic import WhitenedAntitheticEstimator


class FixedBlendEstimator(BaseEstimator):
    """Blend covariance propagation with reduced-budget whitened sampling."""

    def __init__(
        self,
        covariance_weight: float = 0.75,
        sampling_weight: float = 0.25,
        sampling_target_utilization: float = 0.075,
    ) -> None:
        self.covariance_weight = covariance_weight
        self.sampling_weight = sampling_weight
        self.sampling_target_utilization = sampling_target_utilization
        self._covariance = CovarianceEstimator()
        self._sampling = WhitenedAntitheticEstimator(
            target_utilization=sampling_target_utilization
        )

    def setup(self, ctx: SetupContext) -> None:
        self._covariance.setup(ctx)
        self._sampling.setup(ctx)

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        covariance = self._covariance.predict(mlp, budget)
        sampling = self._sampling.predict(mlp, budget)
        covariance_weight = fnp.asarray(self.covariance_weight, dtype=fnp.float32)
        sampling_weight = fnp.asarray(self.sampling_weight, dtype=fnp.float32)
        return covariance_weight * covariance + sampling_weight * sampling


Estimator = FixedBlendEstimator
