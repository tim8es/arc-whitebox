from __future__ import annotations

import math

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import BaseEstimator, SetupContext

WIDTH_EXPECTED = 1024
DEPTH_EXPECTED = 16
HARMONIC_DEGREE = 6
HARMONIC_RANK = 64
GH_ORDER = 12
EPS = 1e-12


def canonicalize_column_signs(q: np.ndarray) -> np.ndarray:
    out = np.array(q, dtype=np.float64, copy=True)
    if out.ndim != 2:
        raise ValueError("q must be rank-2")
    for j in range(out.shape[1]):
        pivot = int(np.argmax(np.abs(out[:, j])))
        if out[pivot, j] < 0.0:
            out[:, j] *= -1.0
    return out


def walsh_response_matrix(n: int = WIDTH_EXPECTED, count: int = HARMONIC_RANK) -> np.ndarray:
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


def hermite6(x):
    x2 = x * x
    return x2 * x2 * x2 - 15.0 * x2 * x2 + 45.0 * x2 - 15.0


def gauss_hermite_standard_normal(order: int = GH_ORDER) -> tuple[np.ndarray, np.ndarray]:
    if order != GH_ORDER:
        raise ValueError(f"E046 is frozen to Gauss-Hermite order {GH_ORDER}")
    x, w = np.polynomial.hermite.hermgauss(order)
    return np.sqrt(2.0) * x, w / np.sqrt(np.pi)


def reconstruct_harmonic_correction(
    response_directions: np.ndarray,
    defects: np.ndarray,
    local_coefficients: np.ndarray,
) -> np.ndarray:
    q = np.asarray(response_directions, dtype=np.float64)
    d = np.asarray(defects, dtype=np.float64)
    c = np.asarray(local_coefficients, dtype=np.float64)
    if q.ndim != 2 or q.shape[1] != HARMONIC_RANK:
        raise ValueError("response_directions must have frozen harmonic rank")
    if d.shape != (HARMONIC_RANK,) or c.shape != (HARMONIC_RANK,):
        raise ValueError("defects and coefficients must have frozen harmonic rank")
    return q @ (d * c)


def _canonical_sign_vector(q) -> np.ndarray:
    qq = np.asarray(q)
    pivots = np.argmax(np.abs(qq), axis=0)
    cols = np.arange(qq.shape[1])
    return np.where(qq[pivots, cols] < 0.0, -1.0, 1.0).astype(np.float64)


def _response_directions_fnp(next_weight, walsh):
    mapped = next_weight @ walsh
    q, _ = fnp.linalg.qr(mapped, mode="reduced")
    signs = fnp.asarray(_canonical_sign_vector(q), dtype=fnp.float64)
    return q * fnp.reshape(signs, (1, HARMONIC_RANK))


def _relu_gaussian_terms(mu_pre, var_pre, nodes, weights):
    sigma = fnp.sqrt(fnp.maximum(var_pre, EPS))
    alpha = mu_pre / sigma
    phi = flops.stats.norm.pdf(alpha).astype(fnp.float64)
    Phi = flops.stats.norm.cdf(alpha).astype(fnp.float64)
    mean = mu_pre * Phi + sigma * phi
    ez2 = (mu_pre * mu_pre + var_pre) * Phi + mu_pre * sigma * phi
    var_post = fnp.maximum(ez2 - mean * mean, EPS)

    z = fnp.reshape(mu_pre, (-1, 1)) + fnp.reshape(sigma, (-1, 1)) * fnp.reshape(nodes, (1, -1))
    relu = fnp.maximum(z, 0.0)
    centered = (relu - fnp.reshape(mean, (-1, 1))) / fnp.reshape(fnp.sqrt(var_post), (-1, 1))
    h6_post = hermite6(centered)
    marginal_d6 = h6_post @ weights

    standardized_pre = fnp.reshape(alpha, (-1, 1)) + fnp.reshape(nodes, (1, -1))
    relu_std = fnp.maximum(standardized_pre, 0.0)
    local_h6 = hermite6(nodes)
    coeff = (relu_std * fnp.reshape(local_h6 * weights, (1, -1))) @ fnp.ones(GH_ORDER, dtype=fnp.float64)
    coeff = coeff / 720.0
    return mean, var_post, marginal_d6, coeff, sigma


class Estimator(BaseEstimator):
    """E046 fixed rank-64 degree-6 harmonic defect controller."""

    HARMONIC_DEGREE = HARMONIC_DEGREE
    HARMONIC_RANK = HARMONIC_RANK
    GH_ORDER = GH_ORDER

    def setup(self, ctx: SetupContext) -> None:
        self._ctx = ctx

    def teardown(self) -> None:
        return None

    def predict(self, mlp, flop_budget: int):
        del flop_budget
        n = int(mlp.width)
        depth = int(mlp.depth)
        if n != WIDTH_EXPECTED or depth != DEPTH_EXPECTED:
            raise ValueError(f"E046 frozen architecture is {WIDTH_EXPECTED}x{DEPTH_EXPECTED}, got {n}x{depth}")
        if len(mlp.weights) != depth:
            raise ValueError("MLP depth/weight count mismatch")

        dtype = fnp.float64
        walsh = fnp.asarray(walsh_response_matrix(n, HARMONIC_RANK), dtype=dtype)
        gh_nodes_np, gh_weights_np = gauss_hermite_standard_normal(GH_ORDER)
        gh_nodes = fnp.asarray(gh_nodes_np, dtype=dtype)
        gh_weights = fnp.asarray(gh_weights_np, dtype=dtype)

        mu = fnp.zeros(n, dtype=dtype)
        cov = flops.as_symmetric(fnp.eye(n, dtype=dtype), symmetry=(0, 1))
        q = walsh
        defects = fnp.zeros(HARMONIC_RANK, dtype=dtype)

        self._e046_rank_counts = []
        self._e046_degree_counts = []
        self._e046_gh_orders = []
        self._e046_max_abs_defect = 0.0
        rows = []

        for li, weight in enumerate(mlp.weights):
            w = fnp.asarray(weight, dtype=dtype)
            mu_pre = w.T @ mu
            cov_pre = fnp.einsum("ij,ia,jb->ab", cov, w, w)
            var_pre = fnp.maximum(fnp.diag(cov_pre), EPS)

            response_var = fnp.diag(q.T @ cov @ q)
            cross = q.T @ cov @ w
            denom = fnp.sqrt(
                fnp.reshape(fnp.maximum(response_var, EPS), (-1, 1))
                * fnp.reshape(var_pre, (1, -1))
            )
            corr = cross / denom
            pre_defect = fnp.sum((corr * corr * corr) ** 2 * fnp.reshape(defects, (-1, 1)), axis=0)

            gaussian_mean, var_post, marginal_d6, relu_h6_coeff, sigma_pre = _relu_gaussian_terms(
                mu_pre, var_pre, gh_nodes, gh_weights
            )
            harmonic_correction = sigma_pre * relu_h6_coeff * pre_defect
            mu = gaussian_mean + harmonic_correction

            ez2 = var_post + gaussian_mean * gaussian_mean
            cov = fnp.multiply(
                fnp.outer(
                    flops.stats.norm.cdf(mu_pre / fnp.sqrt(var_pre)).astype(dtype),
                    flops.stats.norm.cdf(mu_pre / fnp.sqrt(var_pre)).astype(dtype),
                ),
                cov_pre,
            )
            corrected_var = fnp.maximum(ez2 - mu * mu, EPS)
            fnp.fill_diagonal(cov, corrected_var)
            cov = flops.as_symmetric((cov + cov.T) * 0.5, symmetry=(0, 1))
            rows.append(mu)

            if li == depth - 1:
                break

            next_w = fnp.asarray(mlp.weights[li + 1], dtype=dtype)
            q = _response_directions_fnp(next_w, walsh)
            response_var_post = fnp.maximum(fnp.diag(q.T @ cov @ q), EPS)
            q6 = q * q
            q6 = q6 * q6 * q6
            numerator = q6.T @ (marginal_d6 * (var_post * var_post * var_post))
            defects = numerator / (response_var_post * response_var_post * response_var_post)

            max_abs_defect = float(np.max(np.abs(np.asarray(defects))))
            if not np.isfinite(max_abs_defect):
                raise FloatingPointError("non-finite harmonic defect state")
            self._e046_max_abs_defect = max(self._e046_max_abs_defect, max_abs_defect)
            self._e046_rank_counts.append(HARMONIC_RANK)
            self._e046_degree_counts.append(HARMONIC_DEGREE)
            self._e046_gh_orders.append(GH_ORDER)

        return fnp.stack(rows, axis=0)
