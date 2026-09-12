"""ARC White-Box Phase 2 estimator entry point.

Keep this file submission-compatible. Research methods should be promoted here only
when they have reproducible evidence in research/ledger.csv.
"""

from __future__ import annotations

import flopscope.numpy as fnp
from whestbench import MLP, BaseEstimator


class Estimator(BaseEstimator):
    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        """Return predicted mean post-ReLU activation for every hidden neuron.

        Current state: zero baseline. The first milestone is to replace this with a
        reproducible official baseline and then beat it on the public Phase 2 set.
        """
        _ = budget
        return fnp.zeros((mlp.depth, mlp.width))
