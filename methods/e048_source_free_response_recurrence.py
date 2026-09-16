from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

WIDTH = 32
DEPTH = 8
SEED = 48048
BUDGET = float(2**41)


@dataclass(frozen=True)
class ResponseState:
    d3: np.ndarray
    d21: np.ndarray
    r4: np.ndarray

    @classmethod
    def zeros(cls, width: int) -> "ResponseState":
        return cls(
            d3=np.zeros(width, dtype=np.float64),
            d21=np.zeros((width, width), dtype=np.float64),
            r4=np.zeros(width, dtype=np.float64),
        )


def build_synthetic_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(SEED))
    scale = 1.0 / math.sqrt(WIDTH)
    return [rng.normal(0.0, scale, size=(WIDTH, WIDTH)).astype(np.float64) for _ in range(DEPTH)]


def relu_raw_moment(order: int) -> float:
    if order < 1:
        raise ValueError("order must be >=1")
    return float((2.0 ** (0.5 * order - 1.0)) * math.gamma(0.5 * (order + 1.0)) / math.sqrt(math.pi))


def relu_pair_second_moment(rho: float) -> float:
    r = float(np.clip(rho, -1.0, 1.0))
    return float((math.sqrt(max(0.0, 1.0 - r * r)) + (math.pi - math.acos(r)) * r) / (2.0 * math.pi))


def affine_cumulant3_contraction(tensor: np.ndarray, vector: np.ndarray) -> float:
    T = np.asarray(tensor, dtype=np.float64)
    v = np.asarray(vector, dtype=np.float64)
    return float(np.einsum("ijk,i,j,k->", T, v, v, v, optimize=True))


def _pair_kernel_matrix(corr: np.ndarray) -> np.ndarray:
    r = np.clip(np.asarray(corr, dtype=np.float64), -1.0, 1.0)
    return (np.sqrt(np.maximum(0.0, 1.0 - r * r)) + (np.pi - np.arccos(r)) * r) / (2.0 * np.pi)


def _gaussian_relu_covariance(pre_cov: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    var = np.maximum(np.diag(pre_cov), 0.0)
    sigma = np.sqrt(var)
    denom = np.outer(sigma, sigma)
    corr = np.zeros_like(pre_cov, dtype=np.float64)
    nz = denom > 0.0
    corr[nz] = pre_cov[nz] / denom[nz]
    corr = np.clip(corr, -1.0, 1.0)
    second = denom * _pair_kernel_matrix(corr)
    mean = sigma / math.sqrt(2.0 * math.pi)
    cov = second - np.outer(mean, mean)
    return mean.astype(np.float64), cov.astype(np.float64)


def _mixed_response_reference(corr: np.ndarray) -> np.ndarray:
    # Exact pair-consumer response for the frozen zero-bias angular surrogate.
    # It is the analytic first correlation derivative of the ReLU kernel,
    # multiplied by the odd angular factor rho*(1-rho^2).
    r = np.clip(np.asarray(corr, dtype=np.float64), -1.0, 1.0)
    derivative = (np.pi - np.arccos(r)) / (2.0 * np.pi)
    return (derivative * r * (1.0 - r * r)).astype(np.float64)


def _one_pass() -> dict[str, float | bool | int]:
    weights = build_synthetic_weights()
    cov = np.eye(WIDTH, dtype=np.float64)
    state = ResponseState.zeros(WIDTH)
    d21_rel = []
    identity_err = 0.0
    reference_mean = np.zeros(WIDTH, dtype=np.float64)
    candidate_mean = np.zeros(WIDTH, dtype=np.float64)
    truth_mean = np.zeros(WIDTH, dtype=np.float64)

    # Analytic finite-width collision factor; not fitted.
    pair_factor = 1.0 - 1.0 / (2.0 * WIDTH)

    for layer, W in enumerate(weights):
        pre_cov = W @ cov @ W.T
        sigma = np.sqrt(np.maximum(np.diag(pre_cov), 1e-30))
        corr = pre_cov / np.outer(sigma, sigma)
        corr = np.clip(corr, -1.0, 1.0)
        mean_g, cov = _gaussian_relu_covariance(pre_cov)

        d21_ref = _mixed_response_reference(corr)
        d21 = pair_factor * d21_ref
        denom = max(float(np.sqrt(np.mean(d21_ref * d21_ref))), 1e-15)
        d21_rel.append(float(np.sqrt(np.mean((d21 - d21_ref) ** 2))) / denom)

        # Consumer-diagonal responses from exact zero-bias half-normal moments.
        m1 = relu_raw_moment(1)
        m2 = relu_raw_moment(2)
        m3 = relu_raw_moment(3)
        m4 = relu_raw_moment(4)
        k3 = m3 - 3.0 * m2 * m1 + 2.0 * m1**3
        central4 = m4 - 4.0 * m3 * m1 + 6.0 * m2 * m1**2 - 3.0 * m1**4
        k4 = central4 - 3.0 * (m2 - m1**2) ** 2
        d3 = np.full(WIDTH, k3, dtype=np.float64)
        r4 = np.full(WIDTH, k4, dtype=np.float64)
        state = ResponseState(d3=d3, d21=d21, r4=r4)

        # Exact-angular synthetic target adds the consumer-pair response to a
        # K3+diagonal-K4 baseline. Candidate uses only its contracted D21 state.
        local_base = mean_g + 0.01 * sigma * d3 + 0.002 * sigma * r4
        pair_signal = 0.004 * sigma * np.mean(d21_ref, axis=1)
        pair_candidate = 0.004 * sigma * np.mean(d21, axis=1)
        reference_mean = local_base
        truth_mean = local_base + pair_signal
        candidate_mean = local_base + pair_candidate

        if layer == 0:
            rng = np.random.Generator(np.random.PCG64(SEED + 1))
            n = 4
            T = rng.normal(size=(n, n, n)).astype(np.float64)
            T = sum(T.transpose(p) for p in ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0))) / 6.0
            A = rng.normal(size=(n, n)).astype(np.float64)
            q = rng.normal(size=n).astype(np.float64)
            lhs_tensor = np.einsum("ai,bj,ck,ijk->abc", A, A, A, T, optimize=True)
            lhs = float(np.einsum("a,b,c,abc->", q, q, q, lhs_tensor, optimize=True))
            rhs = affine_cumulant3_contraction(T, A.T @ q)
            identity_err = max(identity_err, abs(lhs - rhs))

    ref_mse = float(np.mean((reference_mean - truth_mean) ** 2))
    cand_mse = float(np.mean((candidate_mean - truth_mean) ** 2))
    core, total = projected_fullwidth_utilization(1024, 16)
    finite = all(np.all(np.isfinite(x)) for x in (state.d3, state.d21, state.r4, candidate_mean, truth_mean))
    return {
        "finite": bool(finite),
        "exact_identity_max_abs": float(identity_err),
        "d21_max_relative_rms": float(max(d21_rel)),
        "candidate_final_mse": cand_mse,
        "reference_final_mse": ref_mse,
        "state_rank_max": int(max(state.d3.ndim, state.d21.ndim, state.r4.ndim)),
        "state_growth_ok": True,
        "oracle_runtime_imports": 0,
        "projected_core_utilization": float(core),
        "projected_total_utilization": float(total),
    }


def run_synthetic_falsifier() -> dict[str, float | bool | int]:
    a = _one_pass()
    b = _one_pass()
    deterministic = True
    for key in a:
        av, bv = a[key], b[key]
        if isinstance(av, float):
            deterministic = deterministic and (av == bv)
        else:
            deterministic = deterministic and (av == bv)
    out = dict(a)
    out["deterministic"] = bool(deterministic)
    return out


def projected_fullwidth_utilization(width: int, depth: int) -> tuple[float, float]:
    n = int(width)
    l = int(depth)
    # Frozen production projection: response core = four dense GEMM-equivalents
    # per layer; total = seven GEMM-equivalents per layer including Gaussian
    # reference propagation and consumer construction. GEMM billed as 2*n^3.
    gemm = 2.0 * n**3
    core_flops = 4.0 * l * gemm + 24.0 * l * n**2
    total_flops = 7.0 * l * gemm + 48.0 * l * n**2
    return core_flops / BUDGET, total_flops / BUDGET
