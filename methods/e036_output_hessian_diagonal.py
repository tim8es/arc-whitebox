from __future__ import annotations

import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP

H = 1.0
N_PROBES = 1024


def sylvester_hadamard(xp, n: int):
    if n < 1 or (n & (n - 1)) != 0:
        raise ValueError("Sylvester order must be a positive power of two")
    q = xp.ones((1, 1), dtype=xp.float64)
    size = 1
    while size < n:
        top = xp.concatenate([q, q], axis=1)
        bottom = xp.concatenate([q, -q], axis=1)
        q = xp.concatenate([top, bottom], axis=0)
        size *= 2
    return q


def static_dense_flop_envelope(n: int = 1024, depth: int = 16) -> int:
    return 2 * depth * n * n * (2 * n + 1)


def centered_prediction(xp, plus, zero, minus):
    directional_d2 = (plus - 2.0 * zero[None, :] + minus) / (H * H)
    trace_proxy = xp.mean(directional_d2, axis=0)
    return zero + 0.5 * trace_proxy


def run_centered_hessian(xp, weights):
    n = int(weights[0].shape[1])
    probes = sylvester_hadamard(xp, n)
    zero = xp.zeros((1, n), dtype=xp.float64)
    paths = xp.concatenate([probes, -probes, zero], axis=0)
    rows = []
    for w in weights:
        paths = xp.maximum(paths @ w.T, 0.0)
        rows.append(
            centered_prediction(
                xp,
                paths[:n],
                paths[-1],
                paths[n : 2 * n],
            )
        )
    return xp.stack(rows, axis=0)


class Estimator(BaseEstimator):
    def setup(self, context: SetupContext) -> None:
        del context

    def predict(self, mlp: MLP, budget: int):
        del budget
        return run_centered_hessian(fnp, list(mlp.weights))
