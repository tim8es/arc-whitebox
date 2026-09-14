"""Thin experiment entry point for the preregistered E001 coefficient grid."""

from __future__ import annotations

import os

from methods.residual_control_variate import ResidualControlVariateEstimator


class Estimator(ResidualControlVariateEstimator):
    def __init__(self) -> None:
        super().__init__(residual_weight=float(os.environ["E001_RESIDUAL_WEIGHT"]))
