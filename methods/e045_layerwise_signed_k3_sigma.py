from __future__ import annotations

import math

import flopscope.numpy as fnp
import numpy as np
from whestbench import BaseEstimator, SetupContext

PAIR_COUNT = 1024
POINT_COUNT = 2049
RESPONSE_COUNT = 32


def canonicalize_eigenvector_signs(evecs: np.ndarray) -> np.ndarray:
    q = np.array(evecs, dtype=np.float64, copy=True)
    if q.ndim != 2:
        raise ValueError("evecs must be rank-2")
    for j in range(q.shape[1]):
        pivot = int(np.argmax(np.abs(q[:, j])))
        if q[pivot, j] < 0.0:
            q[:, j] *= -1.0
    return q


def walsh_response_matrix(n: int = PAIR_COUNT, count: int = RESPONSE_COUNT) -> np.ndarray:
    if n <= 0 or (n & (n - 1)) != 0:
        raise ValueError("n must be a positive power of two")
    if not (1 <= count <= n):
        raise ValueError("count must be in [1, n]")
    i = np.arange(n, dtype=np.uint64)
    out = np.empty((n, count), dtype=np.float64)
    scale = 1.0 / math.sqrt(float(n))
    nbits = int(math.log2(n))
    for j in range(count):
        x = i & np.uint64(j)
        parity = np.zeros(n, dtype=np.uint8)
        for b in range(nbits):
            parity ^= ((x >> np.uint64(b)) & np.uint64(1)).astype(np.uint8)
        out[:, j] = np.where(parity == 0, scale, -scale)
    return out


def make_sigma_geometry_from_eigendecomposition(
    mean: np.ndarray,
    evals: np.ndarray,
    evecs: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    mean = np.asarray(mean, dtype=np.float64)
    evals = np.asarray(evals, dtype=np.float64)
    evecs = np.asarray(evecs, dtype=np.float64)
    n = mean.shape[0]
    if n != PAIR_COUNT:
        raise ValueError(f"E045 is frozen to width {PAIR_COUNT}, got {n}")
    if evals.shape != (n,) or evecs.shape != (n, n):
        raise ValueError("eigendecomposition shapes do not match mean")
    if np.any(evals < 0.0):
        raise ValueError("negative covariance eigenvalue; E045 forbids clipping")
    q = canonicalize_eigenvector_signs(evecs)
    radii = np.sqrt(float(n) * evals)
    dev = (q * radii[None, :]).T
    points = np.empty((2 * n + 1, n), dtype=np.float64)
    points[0] = mean
    points[1 : 1 + n] = mean[None, :] + dev
    points[1 + n :] = mean[None, :] - dev
    weights = np.zeros(2 * n + 1, dtype=np.float64)
    weights[1:] = 1.0 / float(2 * n)
    return points, weights


def solve_response_antisymmetry(pair_response: np.ndarray, target: np.ndarray) -> np.ndarray:
    r = np.asarray(pair_response, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    if r.shape != (PAIR_COUNT, RESPONSE_COUNT):
        raise ValueError(f"pair_response must be {(PAIR_COUNT, RESPONSE_COUNT)}, got {r.shape}")
    if target.shape != (RESPONSE_COUNT,):
        raise ValueError(f"target must be {(RESPONSE_COUNT,)}, got {target.shape}")
    a = np.concatenate([r.T, (r * r * r).T], axis=0)
    b = np.concatenate([np.zeros(RESPONSE_COUNT, dtype=np.float64), target])
    # Moore-Penrose minimum-norm equality solution; no ridge.
    delta, *_ = np.linalg.lstsq(a, b, rcond=None)
    return delta


def _canonical_signs_from_array(q: np.ndarray) -> np.ndarray:
    """Comparison-only sign extraction; arithmetic sign application stays in flopscope."""
    qq = np.asarray(q)
    piv = np.argmax(np.abs(qq), axis=0)
    cols = np.arange(qq.shape[1])
    return np.where(qq[piv, cols] < 0.0, -1.0, 1.0).astype(np.float64)


def _response_delta_fnp(pair_response, target_half):
    cubic = pair_response * pair_response * pair_response
    a = fnp.concatenate([pair_response.T, cubic.T], axis=0)
    b = fnp.concatenate([fnp.zeros(RESPONSE_COUNT, dtype=fnp.float64), target_half], axis=0)
    gram = a @ a.T
    coeff = fnp.linalg.solve(gram, b)
    return a.T @ coeff


class Estimator(BaseEstimator):
    """E045 layerwise signed-sigma third-moment carrier.

    The symmetric 2048 endpoints carry mean/covariance with nonnegative base
    weights.  A signed antisymmetric perturbation is rebuilt each layer to match
    32 Walsh directional third central moments while keeping zero first-moment
    drift in those same response coordinates.  No source stack or replay exists.
    """

    PAIR_COUNT = PAIR_COUNT
    POINT_COUNT = POINT_COUNT
    RESPONSE_COUNT = RESPONSE_COUNT

    def setup(self, ctx: SetupContext) -> None:
        self._ctx = ctx

    def teardown(self) -> None:
        return None

    def predict(self, mlp, flop_budget: int):
        n = int(mlp.width)
        depth = int(mlp.depth)
        if n != PAIR_COUNT:
            raise ValueError(f"E045 is frozen to width {PAIR_COUNT}, got {n}")
        if depth != len(mlp.weights):
            raise ValueError("MLP depth/weight count mismatch")

        dtype = fnp.float64
        base_pair = 1.0 / float(2 * n)
        h = fnp.asarray(walsh_response_matrix(n, RESPONSE_COUNT), dtype=dtype)

        mean = fnp.zeros(n, dtype=dtype)
        dev = fnp.eye(n, dtype=dtype) * math.sqrt(float(n))
        points = fnp.concatenate(
            [fnp.reshape(mean, (1, n)), dev, -dev],
            axis=0,
        )
        base_weights = fnp.concatenate(
            [fnp.zeros(1, dtype=dtype), fnp.ones(2 * n, dtype=dtype) * base_pair],
            axis=0,
        )
        signed_weights = base_weights

        self._e045_rebuilds = 0
        self._e045_point_counts = []
        self._e045_response_counts = []
        self._e045_max_norm_error = 0.0
        self._e045_max_first_error = 0.0
        self._e045_max_third_error = 0.0
        rows = []

        for li, w in enumerate(mlp.weights):
            wf = fnp.asarray(w, dtype=dtype)
            transformed = fnp.maximum(points @ wf, 0.0)

            # Symmetric component defines the first two moments.  Keeping these
            # weights nonnegative preserves a PSD covariance by construction.
            mean = base_weights @ transformed
            centered = transformed - fnp.reshape(mean, (1, n))
            weighted_centered = centered * fnp.reshape(base_weights, (-1, 1))
            cov = centered.T @ weighted_centered
            cov = (cov + cov.T) * 0.5
            rows.append(mean)

            if li == depth - 1:
                break

            responses = centered @ h
            signed_third = signed_weights @ (responses * responses * responses)

            evals, evecs = fnp.linalg.eigh(cov)
            evals = evals[::-1]
            evecs = evecs[:, ::-1]
            # E045 preregistration forbids eigenvalue clipping.  Tiny negative
            # eigenvalues are therefore a hard numerical failure, not repaired.
            if bool(np.any(np.asarray(evals) < 0.0)):
                raise FloatingPointError("negative covariance eigenvalue; clipping forbidden")

            signs_np = _canonical_signs_from_array(np.asarray(evecs))
            signs = fnp.asarray(signs_np, dtype=dtype)
            evecs = evecs * fnp.reshape(signs, (1, n))
            radii = fnp.sqrt(evals * float(n))
            deviations = (evecs * fnp.reshape(radii, (1, n))).T

            pair_response = deviations @ h
            delta = _response_delta_fnp(pair_response, signed_third * 0.5)

            plus_w = fnp.ones(n, dtype=dtype) * base_pair + delta
            minus_w = fnp.ones(n, dtype=dtype) * base_pair - delta
            signed_weights = fnp.concatenate(
                [fnp.zeros(1, dtype=dtype), plus_w, minus_w], axis=0
            )
            points = fnp.concatenate(
                [
                    fnp.reshape(mean, (1, n)),
                    fnp.reshape(mean, (1, n)) + deviations,
                    fnp.reshape(mean, (1, n)) - deviations,
                ],
                axis=0,
            )

            # Frozen constraint diagnostics; comparisons happen outside the
            # scorer output and do not alter the state or point count.
            norm_error = float(abs(float(np.asarray(signed_weights).sum()) - 1.0))
            first_error = float(np.max(np.abs(np.asarray(pair_response.T @ delta))))
            cubic = pair_response * pair_response * pair_response
            third_error = float(
                np.max(
                    np.abs(
                        np.asarray(cubic.T @ delta)
                        - 0.5 * np.asarray(signed_third)
                    )
                )
            )
            self._e045_max_norm_error = max(self._e045_max_norm_error, norm_error)
            self._e045_max_first_error = max(self._e045_max_first_error, first_error)
            self._e045_max_third_error = max(self._e045_max_third_error, third_error)
            self._e045_rebuilds += 1
            self._e045_point_counts.append(int(points.shape[0]))
            self._e045_response_counts.append(int(pair_response.shape[1]))

        return fnp.stack(rows, axis=0)
