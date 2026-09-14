"""Thin reproducibility entry point for the frozen E006 radial grid.

No automated scoring workflow references this file. It is retained only so the
already-measured frozen estimator can be validated or inspected under its E006
administrative ID without changing the estimator implementation.
"""

from __future__ import annotations

import os

from methods.radial_fourth_moment import RadialFourthMomentEstimator


class Estimator(RadialFourthMomentEstimator):
    def __init__(self) -> None:
        super().__init__(radial_strength=float(os.environ["E006_RADIAL_STRENGTH"]))
