from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


def radial_moment_ratio(n: int, p: float) -> float:
    """E[chi_n**p] / n**(p/2), evaluated stably."""
    return math.exp(
        0.5 * p * math.log(2.0)
        + math.lgamma(0.5 * (n + p))
        - math.lgamma(0.5 * n)
        - 0.5 * p * math.log(n)
    )


def angular_k4_diagonal(n: int) -> float:
    """Cum4(Y_i,Y_i,Y_i,Y_i) for Y uniform on S^(n-1)(sqrt(n))."""
    return -6.0 / (n + 2.0)


def angular_k4_pair_coefficient(n: int) -> float:
    """Coefficient c in K4_ijkl=c*(dij*dkl+dik*djl+dil*djk)."""
    return -2.0 / (n + 2.0)


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(x, 0.0)


def forward(weights: list[np.ndarray], x: np.ndarray) -> np.ndarray:
    h = x
    for w in weights:
        h = relu(w @ h)
    return h


def one_level_strassen(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """One exact-algebra Strassen level; pads odd dimensions deterministically."""
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[0]:
        raise ValueError("incompatible matrices")
    m, k = a.shape
    _, p = b.shape
    mp = m + (m & 1)
    kp = k + (k & 1)
    pp = p + (p & 1)
    ap = np.pad(a, ((0, mp - m), (0, kp - k)))
    bp = np.pad(b, ((0, kp - k), (0, pp - p)))

    mh, kh, ph = mp // 2, kp // 2, pp // 2
    a11, a12 = ap[:mh, :kh], ap[:mh, kh:]
    a21, a22 = ap[mh:, :kh], ap[mh:, kh:]
    b11, b12 = bp[:kh, :ph], bp[:kh, ph:]
    b21, b22 = bp[kh:, :ph], bp[kh:, ph:]

    m1 = (a11 + a22) @ (b11 + b22)
    m2 = (a21 + a22) @ b11
    m3 = a11 @ (b12 - b22)
    m4 = a22 @ (b21 - b11)
    m5 = (a11 + a12) @ b22
    m6 = (a21 - a11) @ (b11 + b12)
    m7 = (a12 - a22) @ (b21 + b22)

    c11 = m1 + m4 - m5 + m7
    c12 = m3 + m5
    c21 = m2 + m4
    c22 = m1 - m2 + m3 + m6
    out = np.block([[c11, c12], [c21, c22]])
    return out[:m, :p]


def classic_square_flops(n: int) -> int:
    return 2 * n**3


def strassen1_square_flops(n: int) -> int:
    if n % 2:
        raise ValueError("frozen analytic cost requires even n")
    h = n // 2
    # Seven half-size GEMMs plus 10 input and 8 output half-size additions.
    return 7 * 2 * h**3 + 18 * h**2


def strassen1_square_ratio(n: int) -> float:
    return strassen1_square_flops(n) / classic_square_flops(n)


def required_eligible_fraction(util_before: float, util_cap: float, rho: float) -> float:
    """q in U_after/U_before = (1-q)+q*rho."""
    if not (0.0 < rho < 1.0):
        raise ValueError("rho must be in (0,1)")
    return (1.0 - util_cap / util_before) / (1.0 - rho)


@dataclass(frozen=True)
class Sector:
    lo: float
    hi: float
    linear_map: np.ndarray


def _roots_in_interval(c: float, s: float, lo: float, hi: float) -> list[float]:
    if c == 0.0 and s == 0.0:
        return []
    phi = math.atan2(s, c)
    roots = []
    base = phi + 0.5 * math.pi
    for k in range(-3, 5):
        x = base + k * math.pi
        if lo + 1e-14 < x < hi - 1e-14:
            roots.append(x)
    return roots


def exact_circle_sectors(weights: list[np.ndarray]) -> list[Sector]:
    """Enumerate exact activation sectors for a zero-bias 2D-input ReLU MLP."""
    sectors = [Sector(0.0, 2.0 * math.pi, np.eye(2, dtype=np.float64))]
    for w in weights:
        next_sectors: list[Sector] = []
        for sec in sectors:
            pre = w @ sec.linear_map
            cuts = [sec.lo, sec.hi]
            for row in pre:
                cuts.extend(_roots_in_interval(float(row[0]), float(row[1]), sec.lo, sec.hi))
            cuts = sorted(set(round(x, 15) for x in cuts))
            for a, b in zip(cuts[:-1], cuts[1:]):
                if b - a <= 1e-14:
                    continue
                mid = 0.5 * (a + b)
                xmid = np.array([math.cos(mid), math.sin(mid)])
                active = (pre @ xmid) > 0.0
                amap = pre * active[:, None]
                next_sectors.append(Sector(a, b, amap))
        sectors = next_sectors
    return sectors


def exact_unit_circle_mean(weights: list[np.ndarray]) -> np.ndarray:
    sectors = exact_circle_sectors(weights)
    out_dim = weights[-1].shape[0]
    total = np.zeros(out_dim, dtype=np.float64)
    for sec in sectors:
        int_x = np.array(
            [
                math.sin(sec.hi) - math.sin(sec.lo),
                math.cos(sec.lo) - math.cos(sec.hi),
            ],
            dtype=np.float64,
        )
        total += sec.linear_map @ int_x
    return total / (2.0 * math.pi)


def exact_gaussian_mean_2d(weights: list[np.ndarray]) -> np.ndarray:
    # X=R*U in 2D, E[R]=sqrt(pi/2).
    return math.sqrt(math.pi / 2.0) * exact_unit_circle_mean(weights)


def dense_he_weights(input_dim: int, width: int, depth: int, seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    dims = [input_dim] + [width] * depth
    ret = []
    for l in range(depth):
        scale = 1.0 if l == 0 else math.sqrt(2.0)
        ret.append(rng.standard_normal((dims[l + 1], dims[l])) * (scale / math.sqrt(dims[l])))
    return ret


def adversarial_square_weights(n: int, depth: int, seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    base = np.linspace(0.55, 1.45, n)
    base /= math.sqrt(float(np.mean(base * base)))
    ret = []
    for l in range(depth):
        q1, _ = np.linalg.qr(rng.standard_normal((n, n)))
        q2, _ = np.linalg.qr(rng.standard_normal((n, n)))
        gains = np.roll(base if l % 2 == 0 else base[::-1], (5 * l) % n)
        scale = 1.0 if l == 0 else math.sqrt(2.0)
        ret.append(scale * (q1 @ np.diag(gains) @ q2.T))
    return ret
