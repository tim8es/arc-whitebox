from __future__ import annotations

import numpy as np
from scipy.special import ndtri
from scipy.stats import qmc

import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP

DIMENSION = 1024
N_SAMPLES = 8192
M_POWER = 13
SCRAMBLE_SEED = 38038


def build_samples() -> np.ndarray:
    engine = qmc.Sobol(d=DIMENSION, scramble=True, seed=SCRAMBLE_SEED)
    uniforms = engine.random_base2(m=M_POWER)
    samples = ndtri(uniforms).astype(np.float32)
    return samples


def run_trajectories(xp, samples, weights):
    x = xp.asarray(samples)
    rows = []
    for w in weights:
        x = xp.maximum(x @ w, 0.0)
        rows.append(xp.mean(x, axis=0))
    return xp.stack(rows, axis=0)


class Estimator(BaseEstimator):
    def __init__(self) -> None:
        self._samples = None

    def setup(self, context: SetupContext) -> None:
        del context
        self._samples = build_samples()

    def predict(self, mlp: MLP, budget: int):
        del budget
        if self._samples is None:
            raise RuntimeError("setup() must be called before predict()")
        return run_trajectories(fnp, self._samples, list(mlp.weights))
