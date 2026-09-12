"""Thin experiment entry point for the preregistered E003 radial grid."""

from __future__ import annotations

import os

from methods.radial_fourth_moment import RadialFourthMomentEstimator


class Estimator(RadialFourthMomentEstimator):
    def __init__(self) -> None:
        super().__init__(radial_strength=float(os.environ["E003_RADIAL_STRENGTH"]))
