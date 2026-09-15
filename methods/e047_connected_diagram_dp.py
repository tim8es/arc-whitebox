from __future__ import annotations

import math
from typing import Iterable

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import BaseEstimator, SetupContext

KMAX = 6
PROBE_COUNT = 32
DTYPE = np.float64


def cumulants_to_moments(cumulants: np.ndarray, kmax: int = KMAX) -> np.ndarray:
    """Scalar moment-cumulant recurrence through kmax."""
    k = np.asarray(cumulants, dtype=np.float64)
    if k.shape[0] < kmax + 1:
        raise ValueError("cumulant vector too short")
    m = np.zeros(kmax + 1, dtype=np.float64)
    m[0] = 1.0
    for n in range(1, kmax + 1):
        total = 0.0
        for j in range(1, n + 1):
            total += math.comb(n - 1, j - 1) * k[j] * m[n - j]
        m[n] = total
    return m


def moments_to_cumulants(moments: np.ndarray, kmax: int = KMAX) -> np.ndarray:
    """Möbius-equivalent scalar cumulant recurrence through kmax."""
    m = np.asarray(moments, dtype=np.float64)
    if m.shape[0] < kmax + 1:
        raise ValueError("moment vector too short")
    k = np.zeros(kmax + 1, dtype=np.float64)
    for n in range(1, kmax + 1):
        total = m[n]
        for j in range(1, n):
            total -= math.comb(n - 1, j - 1) * k[j] * m[n - j]
        k[n] = total
    return k


def _gaussian_positive_raw_moments(mu: float, var: float, kmax: int) -> np.ndarray:
    """Raw moments E[ReLU(N(mu,var))^r] using exact tail recurrences."""
    if var < 0.0:
        raise ValueError("variance must be nonnegative")
    out = np.zeros(kmax + 1, dtype=np.float64)
    out[0] = 1.0
    if var <= 1e-18:
        x = max(float(mu), 0.0)
        for r in range(1, kmax + 1):
            out[r] = x**r
        return out
    sigma = math.sqrt(var)
    a = -float(mu) / sigma
    phi = math.exp(-0.5 * a * a) / math.sqrt(2.0 * math.pi)
    j = np.zeros(kmax + 1, dtype=np.float64)
    j[0] = 0.5 * math.erfc(a / math.sqrt(2.0))
    if kmax >= 1:
        j[1] = phi
    for n in range(2, kmax + 1):
        j[n] = (a ** (n - 1)) * phi + (n - 1) * j[n - 2]
    for r in range(1, kmax + 1):
        val = 0.0
        for p in range(0, r + 1):
            val += math.comb(r, p) * (float(mu) ** (r - p)) * (sigma**p) * j[p]
        out[r] = val
    return out


def _contracted_probe_cumulants(weight, mean, cov, probes, kmax: int) -> dict[int, np.ndarray]:
    w = np.asarray(weight, dtype=np.float64)
    mu = np.asarray(mean, dtype=np.float64)
    c = np.asarray(cov, dtype=np.float64)
    q = np.asarray(probes, dtype=np.float64)
    if w.ndim != 2 or mu.ndim != 1 or c.ndim != 2 or q.ndim != 2:
        raise ValueError("invalid ranks")
    if w.shape[0] != mu.size or c.shape != (mu.size, mu.size) or q.shape[1] != w.shape[1]:
        raise ValueError("shape mismatch")
    out = {order: np.zeros(q.shape[0], dtype=np.float64) for order in range(3, kmax + 1)}
    for i, probe in enumerate(q):
        back = w @ probe
        scalar_mu = float(back @ mu)
        scalar_var = float(back @ c @ back)
        moments = _gaussian_positive_raw_moments(scalar_mu, max(scalar_var, 0.0), kmax)
        cumulants = moments_to_cumulants(moments, kmax)
        for order in range(3, kmax + 1):
            out[order][i] = cumulants[order]
    return out


def contracted_connected_states(weight, mean, cov, probes, kmax: int = KMAX) -> dict[int, np.ndarray]:
    """Production-shape output contractions only; every returned object is rank-1."""
    return _contracted_probe_cumulants(weight, mean, cov, probes, kmax)


def explicit_connected_states(weight, mean, cov, probes, kmax: int = KMAX) -> dict[int, np.ndarray]:
    """Independent small-network reference by explicit probe-by-probe scalar diagrams."""
    w = np.asarray(weight, dtype=np.float64)
    mu = np.asarray(mean, dtype=np.float64)
    c = np.asarray(cov, dtype=np.float64)
    q = np.asarray(probes, dtype=np.float64)
    result = {order: [] for order in range(3, kmax + 1)}
    for probe in q:
        # Explicit multilinear contraction q^T W^T X = (Wq)^T X.
        back = np.zeros(w.shape[0], dtype=np.float64)
        for a in range(w.shape[0]):
            for b in range(w.shape[1]):
                back[a] += w[a, b] * probe[b]
        scalar_mu = sum(float(back[a] * mu[a]) for a in range(mu.size))
        scalar_var = 0.0
        for a in range(mu.size):
            for b in range(mu.size):
                scalar_var += float(back[a] * c[a, b] * back[b])
        moments = _gaussian_positive_raw_moments(scalar_mu, max(scalar_var, 0.0), kmax)
        cumulants = moments_to_cumulants(moments, kmax)
        for order in range(3, kmax + 1):
            result[order].append(cumulants[order])
    return {order: np.asarray(vals, dtype=np.float64) for order, vals in result.items()}


def _relu_gaussian_mean_cov_np(mean_pre: np.ndarray, cov_pre: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n = mean_pre.size
    mean = np.zeros(n, dtype=np.float64)
    var_post = np.zeros(n, dtype=np.float64)
    gain = np.zeros(n, dtype=np.float64)
    for i in range(n):
        moments = _gaussian_positive_raw_moments(float(mean_pre[i]), max(float(cov_pre[i, i]), 0.0), 2)
        mean[i] = moments[1]
        var_post[i] = max(moments[2] - moments[1] * moments[1], 0.0)
        sigma = math.sqrt(max(float(cov_pre[i, i]), 1e-18))
        alpha = float(mean_pre[i]) / sigma
        gain[i] = 0.5 * math.erfc(-alpha / math.sqrt(2.0))
    cov = np.outer(gain, gain) * cov_pre
    np.fill_diagonal(cov, var_post)
    return mean, cov


def _propagate_reference(
    weights: Iterable[np.ndarray], mean: np.ndarray, cov: np.ndarray, probes: np.ndarray,
    kmax: int, explicit: bool,
) -> dict[int, np.ndarray]:
    mu = np.asarray(mean, dtype=np.float64).copy()
    c = np.asarray(cov, dtype=np.float64).copy()
    p = np.asarray(probes, dtype=np.float64)
    last = {order: np.zeros(p.shape[0], dtype=np.float64) for order in range(3, kmax + 1)}
    fn = explicit_connected_states if explicit else contracted_connected_states
    for w in weights:
        ww = np.asarray(w, dtype=np.float64)
        last = fn(ww, mu, c, p, kmax=kmax)
        mu_pre = ww.T @ mu
        cov_pre = ww.T @ c @ ww
        mu, c = _relu_gaussian_mean_cov_np(mu_pre, cov_pre)
    return last


def propagate_contracted_network(weights, mean, cov, probes, kmax: int = KMAX) -> dict[int, np.ndarray]:
    return _propagate_reference(weights, mean, cov, probes, kmax, explicit=False)


def propagate_explicit_network(weights, mean, cov, probes, kmax: int = KMAX) -> dict[int, np.ndarray]:
    return _propagate_reference(weights, mean, cov, probes, kmax, explicit=True)


def _walsh_probes(width: int, count: int = PROBE_COUNT) -> np.ndarray:
    if width <= 0 or (width & (width - 1)) != 0:
        raise ValueError("production width must be a positive power of two")
    count = min(count, width)
    i = np.arange(width, dtype=np.uint64)
    out = np.empty((count, width), dtype=np.float64)
    scale = 1.0 / math.sqrt(float(width))
    bits = int(math.log2(width))
    for j in range(count):
        x = i & np.uint64(j)
        parity = np.zeros(width, dtype=np.uint8)
        for b in range(bits):
            parity ^= ((x >> np.uint64(b)) & np.uint64(1)).astype(np.uint8)
        out[j] = np.where(parity == 0, scale, -scale)
    return out


def _fnp_positive_moments(mu, var, kmax: int):
    sigma = fnp.sqrt(fnp.maximum(var, 1e-18))
    alpha = mu / sigma
    phi = flops.stats.norm.pdf(alpha).astype(fnp.float64)
    Phi = flops.stats.norm.cdf(alpha).astype(fnp.float64)
    # J_p for standard-normal tail Z > -alpha.
    a = -alpha
    js = [Phi, phi]
    for n in range(2, kmax + 1):
        js.append((a ** (n - 1)) * phi + float(n - 1) * js[n - 2])
    moments = [fnp.ones_like(mu)]
    for r in range(1, kmax + 1):
        val = fnp.zeros_like(mu)
        for p in range(0, r + 1):
            val = val + float(math.comb(r, p)) * (mu ** (r - p)) * (sigma**p) * js[p]
        moments.append(val)
    return moments


def _fnp_cumulants_from_moments(moments, kmax: int):
    cumulants = [fnp.zeros_like(moments[0])]
    for n in range(1, kmax + 1):
        val = moments[n]
        for j in range(1, n):
            val = val - float(math.comb(n - 1, j - 1)) * cumulants[j] * moments[n - j]
        cumulants.append(val)
    return cumulants


class Estimator(BaseEstimator):
    """E047 K<=6 output-contracted connected-state estimator."""

    KMAX = KMAX
    PROBE_COUNT = PROBE_COUNT

    def setup(self, ctx: SetupContext) -> None:
        self._ctx = ctx

    def teardown(self) -> None:
        return None

    def predict(self, mlp, flop_budget: int):
        n = int(mlp.width)
        if n != 1024:
            raise ValueError(f"E047 frozen production width is 1024, got {n}")
        probes_np = _walsh_probes(n, PROBE_COUNT)
        probes = fnp.asarray(probes_np, dtype=fnp.float64)
        mu = fnp.zeros(n, dtype=fnp.float64)
        cov = flops.as_symmetric(fnp.eye(n, dtype=fnp.float64), symmetry=(0, 1))
        rows = []
        self._e047_state_ranks = []
        self._e047_order_counts = []
        self._e047_probe_counts = []
        self._e047_max_abs_connected = 0.0

        for weight in mlp.weights:
            w = fnp.asarray(weight, dtype=fnp.float64)
            mu_pre = w.T @ mu
            cov_pre = fnp.einsum("ij,ia,jb->ab", cov, w, w)
            var_pre = fnp.maximum(fnp.diag(cov_pre), 1e-18)

            # Output-contracted connected states only: shape (32,) per order.
            back = w @ probes.T  # (width, probes)
            proj_mu = back.T @ mu
            proj_var = fnp.einsum("ip,ij,jp->p", back, cov, back)
            proj_moments = _fnp_positive_moments(proj_mu, proj_var, KMAX)
            proj_cumulants = _fnp_cumulants_from_moments(proj_moments, KMAX)
            connected = [proj_cumulants[k] for k in range(3, KMAX + 1)]

            moments = _fnp_positive_moments(mu_pre, var_pre, 2)
            mu = moments[1]
            var_post = fnp.maximum(moments[2] - mu * mu, 0.0)
            sigma = fnp.sqrt(var_pre)
            alpha = mu_pre / sigma
            gain = flops.stats.norm.cdf(alpha).astype(fnp.float64)
            cov = fnp.multiply(fnp.outer(gain, gain), cov_pre)
            fnp.fill_diagonal(cov, var_post)
            cov = flops.as_symmetric(cov, symmetry=(0, 1))

            # Fixed connected correction projected back through the frozen Walsh frame.
            corr_probe = fnp.zeros(PROBE_COUNT, dtype=fnp.float64)
            for idx, order in enumerate(range(3, KMAX + 1)):
                corr_probe = corr_probe + connected[idx] / float(math.factorial(order))
            correction = probes.T @ corr_probe
            corrected_mean = mu + correction
            rows.append(corrected_mean)

            self._e047_state_ranks.append([int(x.ndim) for x in connected])
            self._e047_order_counts.append(KMAX - 2)
            self._e047_probe_counts.append(PROBE_COUNT)
            max_conn = max(float(np.max(np.abs(np.asarray(x)))) for x in connected)
            self._e047_max_abs_connected = max(self._e047_max_abs_connected, max_conn)

        return fnp.stack(rows, axis=0)
