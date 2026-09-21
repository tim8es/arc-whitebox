#!/usr/bin/env python3
"""E159 clean-room published angular/radial K2 ablation.

Re-derived from the pinned public Phase-8 implementation evidence recorded in
research/E159_PRIMARY_SOURCE_NOTE.md. Synthetic weights and analytic references
only. No benchmark data, E151/E154/E157 imports, Strassen, or sampling.
"""
from __future__ import annotations

import argparse
import json
import math
import traceback
from pathlib import Path

import numpy as np

TOL = 2e-12
BUDGET = 2**41
COST_CAP = 0.135


def a1_exact(n: int) -> float:
    return math.sqrt(2.0 / n) * math.exp(
        math.lgamma((n + 1.0) / 2.0) - math.lgamma(n / 2.0)
    )


def _cdf(x: np.ndarray) -> np.ndarray:
    return 0.5 * np.vectorize(math.erfc)(-x / math.sqrt(2.0))


def wick(mean: np.ndarray, var: np.ndarray, k: int, p: int) -> np.ndarray:
    """E[d^k ReLU(Z)^p] for a matching marginal Gaussian."""
    s = np.sqrt(np.maximum(var, 1e-300))
    a = mean / s
    ph = np.exp(-0.5 * a * a) / math.sqrt(2.0 * math.pi)
    F = _cdf(a)

    if p == 1:
        table = {
            0: s * ph + mean * F,
            1: F,
            2: ph / s,
            3: -a * ph / s**2,
            4: (a * a - 1.0) * ph / s**3,
        }
    elif p == 2:
        table = {
            0: (mean * mean + var) * F + mean * s * ph,
            1: 2.0 * (s * ph + mean * F),
            2: 2.0 * F,
            3: 2.0 * ph / s,
            4: -2.0 * a * ph / s**2,
        }
    elif p == 3:
        table = {
            0: s**3 * ((2.0 + a * a) * ph + (3.0 * a + a**3) * F),
            1: 3.0 * s**2 * (a * ph + (1.0 + a * a) * F),
            2: 6.0 * (s * ph + mean * F),
            3: 6.0 * F,
            4: 6.0 * ph / s,
        }
    elif p == 4:
        table = {
            0: s**4
            * ((5.0 * a + a**3) * ph + (3.0 + 6.0 * a * a + a**4) * F),
            1: 4.0
            * s**3
            * ((2.0 + a * a) * ph + (3.0 * a + a**3) * F),
            2: 12.0 * s**2 * (a * ph + (1.0 + a * a) * F),
            3: 24.0 * (s * ph + mean * F),
            4: 24.0 * F,
        }
    else:
        raise ValueError(p)
    if k not in table:
        raise ValueError((k, p))
    return table[k]


def zero_diag(x: np.ndarray) -> np.ndarray:
    y = np.array(x, dtype=np.float64, copy=True)
    np.fill_diagonal(y, 0.0)
    return y


def sym(x: np.ndarray) -> np.ndarray:
    return 0.5 * (x + x.T)


def make_weights(n: int, depth: int, seed: int, adversarial: bool) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    if not adversarial:
        scale = math.sqrt(2.0 / n)
        return [
            rng.standard_normal((n, n), dtype=np.float64) * scale
            for _ in range(depth)
        ]

    gains = np.linspace(0.5, 1.5, n, dtype=np.float64)
    gains *= math.sqrt(2.0 / float(np.mean(gains * gains)))
    out = []
    for _ in range(depth):
        ql, rl = np.linalg.qr(rng.standard_normal((n, n), dtype=np.float64))
        qr, rr = np.linalg.qr(rng.standard_normal((n, n), dtype=np.float64))
        sl = np.sign(np.diag(rl))
        sr = np.sign(np.diag(rr))
        sl[sl == 0.0] = 1.0
        sr[sr == 0.0] = 1.0
        ql = ql * sl[None, :]
        qr = qr * sr[None, :]
        out.append((ql * gains[None, :]) @ qr.T)
    return out


def forward(weights: list[np.ndarray], x: np.ndarray) -> np.ndarray:
    h = np.asarray(x, dtype=np.float64)
    for w in weights:
        h = np.maximum(w @ h, 0.0)
    return h


def homogeneity_error(weights: list[np.ndarray], seed: int) -> float:
    n = weights[0].shape[1]
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(8):
        x = rng.standard_normal(n, dtype=np.float64)
        r = float(np.linalg.norm(x))
        y = math.sqrt(n) * x / r
        lhs = forward(weights, x)
        rhs = (r / math.sqrt(n)) * forward(weights, y)
        den = np.maximum(np.maximum(np.abs(lhs), np.abs(rhs)), 1e-300)
        worst = max(worst, float(np.max(np.abs(lhs - rhs) / den)))
    return worst


def layer0_gauge_identity(w0: np.ndarray) -> dict:
    """Independent algebraic check of the public first-state gauge conversion."""
    n = w0.shape[1]
    M = sym(w0 @ w0.T)
    var = np.diag(M)
    z = np.zeros(n, dtype=np.float64)
    mu_g = wick(z, var, 0, 1)
    p2 = wick(z, var, 0, 2)
    off = zero_diag(M)
    w11 = wick(z, var, 1, 1)
    w21 = wick(z, var, 2, 1)
    p11 = sym(
        off * (w11[:, None] * w11[None, :])
        + 0.5 * off**2 * (w21[:, None] * w21[None, :])
    )
    cov_g = p11.copy()
    np.fill_diagonal(cov_g, p2 - mu_g * mu_g)

    a1 = a1_exact(n)
    mu_a = mu_g / a1
    cov_a = sym(cov_g - (1.0 / (a1 * a1) - 1.0) * np.outer(mu_g, mu_g))

    mean_back = a1 * mu_a
    raw2_g = cov_g + np.outer(mu_g, mu_g)
    raw2_a = cov_a + np.outer(mu_a, mu_a)

    mean_den = max(float(np.linalg.norm(mu_g)), 1e-300)
    raw_den = max(float(np.linalg.norm(raw2_g)), 1e-300)
    return {
        "mean_conversion_rel": float(np.linalg.norm(mean_back - mu_g) / mean_den),
        "raw_second_invariance_rel": float(np.linalg.norm(raw2_a - raw2_g) / raw_den),
    }


def layer0_k4_identity(w0: np.ndarray) -> dict:
    n = w0.shape[1]
    M = w0 @ w0.T
    kappa = -2.0 / (n + 2.0)
    c4 = -6.0 / (n + 2.0)
    p1 = np.einsum("ab,cd->abcd", M, M)
    p2 = np.einsum("ac,bd->abcd", M, M)
    p3 = np.einsum("ad,bc->abcd", M, M)
    dense = kappa * (p1 + p2 + p3)
    idx = np.arange(n)
    d4 = dense[idx, idx, idx, idx]
    d22 = dense[idx[:, None], idx[:, None], idx[None, :], idx[None, :]]
    d = np.diag(M)
    s4 = c4 * d * d
    s22 = (c4 / 3.0) * zero_diag(d[:, None] * d[None, :] + 2.0 * M * M)
    d22_off = zero_diag(d22)

    def rel(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.linalg.norm(a - b) / max(float(np.linalg.norm(b)), 1e-300))

    return {
        "s4_dense_rel": rel(s4, d4),
        "s22_dense_offdiag_rel": rel(s22, d22_off),
    }


def predict(
    weights: list[np.ndarray],
    *,
    angular: bool,
    use_k4: bool,
) -> tuple[np.ndarray, dict]:
    """Clean-room reconstruction of the public K2/K2K4 arithmetic."""
    n = weights[0].shape[1]
    depth = len(weights)
    a1 = a1_exact(n)
    mu = np.zeros(n, dtype=np.float64)
    cov = np.eye(n, dtype=np.float64)
    c4 = (-6.0 / (n + 2.0)) if (angular and use_k4) else (0.0 if use_k4 else None)
    preds: list[np.ndarray] = []
    k4_update_calls = 0

    for layer, W in enumerate(weights):
        terminal = layer == depth - 1
        if terminal:
            mu_pre = W @ mu
            var_pre = np.sum((W @ cov) * W, axis=1)
            dM = np.sum(W * W, axis=1)
            s4 = c4 * dM * dM if use_k4 else None
            out = wick(mu_pre, var_pre, 0, 1)
            if use_k4:
                out = out + wick(mu_pre, var_pre, 4, 1) * s4 / 24.0
            preds.append(a1 * out if angular else out)
            break

        if layer == 0:
            M = W @ W.T
            cov_pre = sym(M)
            mu_pre = np.zeros(n, dtype=np.float64)
        else:
            mu_pre = W @ mu
            WC = W @ cov
            cov_pre = sym(WC @ W.T)
            M = W @ W.T

        dM = np.diag(M)
        if use_k4:
            s4 = c4 * dM * dM
            s22 = (c4 / 3.0) * zero_diag(
                dM[:, None] * dM[None, :] + 2.0 * M * M
            )
        else:
            s4 = None
            s22 = None

        var = np.diag(cov_pre)
        off = zero_diag(cov_pre)

        P = {}
        for p in (1, 2, 3, 4):
            P[p] = wick(mu_pre, var, 0, p)
            if use_k4:
                P[p] = P[p] + wick(mu_pre, var, 4, p) * s4 / 24.0

        w11 = wick(mu_pre, var, 1, 1)
        w21 = wick(mu_pre, var, 2, 1)
        P11 = (
            off * (w11[:, None] * w11[None, :])
            + 0.5 * off**2 * (w21[:, None] * w21[None, :])
        )
        if use_k4:
            P11 = P11 + 0.25 * s22 * (w21[:, None] * w21[None, :])
        P11 = sym(P11)

        w12 = wick(mu_pre, var, 1, 2)
        w22 = wick(mu_pre, var, 2, 2)
        P21 = (
            off * (w12[:, None] * w11[None, :])
            + 0.5 * off**2 * (w22[:, None] * w21[None, :])
        )
        if use_k4:
            P21 = P21 + 0.25 * s22 * (w22[:, None] * w21[None, :])

        k1 = P[1]
        k2 = P[2] - P[1] ** 2
        k4diag = (
            P[4]
            - 4.0 * P[1] * P[3]
            - 3.0 * P[2] ** 2
            + 12.0 * P[1] ** 2 * P[2]
            - 6.0 * P[1] ** 4
        )
        k21 = zero_diag(P21 - 2.0 * (P[1][:, None] * P11))

        mu = k1.copy()
        cov = P11.copy()
        np.fill_diagonal(cov, k2)
        cov = sym(cov)

        if layer == 0 and angular:
            mu_g = mu.copy()
            mu = mu / a1
            cov = sym(cov - (1.0 / (a1 * a1) - 1.0) * np.outer(mu_g, mu_g))

        if use_k4:
            a2 = w12
            b2 = w22
            H = 0.5 * off**2 + 0.25 * s22
            rows_e22 = a2 * (off @ a2) + b2 * (H @ b2)
            r22 = (
                rows_e22
                - 2.0 * (k21 @ P[1] + P[1] * np.sum(k21, axis=0))
                - 2.0 * np.sum(P11**2, axis=1)
                + 4.0 * P[1] * (P11 @ P[1])
            )
            c4 = float(
                (3.0 / (n * (n + 2.0)))
                * (float(np.sum(k4diag)) + float(np.sum(r22)))
            )
            k4_update_calls += 1

        preds.append(a1 * mu if angular else mu.copy())

    return np.stack(preds, axis=0), {
        "k4_update_calls": k4_update_calls,
        "k4_runtime_enabled": bool(use_k4),
        "angular": bool(angular),
    }


def angle_zeros(row: np.ndarray) -> list[float]:
    if float(np.linalg.norm(row)) <= 1e-15:
        return []
    phi = math.atan2(float(row[1]), float(row[0]))
    z = (phi + math.pi / 2.0) % (2.0 * math.pi)
    return [z, (z + math.pi) % (2.0 * math.pi)]


def exact_gaussian_mean_2d(weights: list[np.ndarray]) -> tuple[np.ndarray, int]:
    """Analytic sector integral; no sampling."""
    sectors: list[tuple[float, float, np.ndarray]] = [
        (0.0, 2.0 * math.pi, np.eye(2, dtype=np.float64))
    ]
    eps = 2e-14
    for W in weights:
        nxt: list[tuple[float, float, np.ndarray]] = []
        for lo, hi, A in sectors:
            pre = W @ A
            cuts = [lo, hi]
            for row in pre:
                for z in angle_zeros(row):
                    if lo + eps < z < hi - eps:
                        cuts.append(z)
            cuts.sort()
            uniq = []
            for z in cuts:
                if not uniq or abs(z - uniq[-1]) > eps:
                    uniq.append(z)
            for a, b in zip(uniq[:-1], uniq[1:]):
                if b - a <= eps:
                    continue
                mid = 0.5 * (a + b)
                u = np.array([math.cos(mid), math.sin(mid)], dtype=np.float64)
                mask = (pre @ u) > 0.0
                B = pre.copy()
                B[~mask, :] = 0.0
                nxt.append((a, b, B))
        sectors = nxt

    integ = np.zeros(2, dtype=np.float64)
    for lo, hi, A in sectors:
        iu = np.array(
            [math.sin(hi) - math.sin(lo), -math.cos(hi) + math.cos(lo)],
            dtype=np.float64,
        )
        integ += A @ iu
    sphere_mean = integ / (2.0 * math.pi)
    return math.sqrt(math.pi / 2.0) * sphere_mean, len(sectors)


def production_cost_upper(n: int = 1024, depth: int = 16) -> dict:
    gemm = (6 * depth - 8) * n**3
    non_gemm = 10000 * depth * n**2
    setup = 10000 * n**2
    total = gemm + non_gemm + setup
    return {
        "n": n,
        "depth": depth,
        "gemm_flops": int(gemm),
        "non_gemm_complete_reserve_flops": int(non_gemm),
        "setup_complete_reserve_flops": int(setup),
        "all_in_upper_flops": int(total),
        "budget_flops": BUDGET,
        "utilization_upper": total / BUDGET,
        "cap": COST_CAP,
    }


def fixture_audit(name: str, weights: list[np.ndarray], hom_seed: int) -> dict:
    gauge = layer0_gauge_identity(weights[0])
    k4 = layer0_k4_identity(weights[0])
    return {
        "name": name,
        "homogeneity_max_rel": homogeneity_error(weights, hom_seed),
        **gauge,
        **k4,
    }


def run_once() -> dict:
    f0 = make_weights(2, 8, 159002, False)
    f1 = make_weights(32, 8, 159032, False)
    f2 = make_weights(16, 8, 159016, True)

    fixtures = [
        fixture_audit("exact2d_depth8", f0, 259002),
        fixture_audit("dense32_depth8", f1, 259032),
        fixture_audit("adversarial16_depth8", f2, 259016),
    ]

    exact, sectors = exact_gaussian_mean_2d(f0)
    arms = {}
    configs = {
        "G-K2": (False, False),
        "A-K2": (True, False),
        "G-K2K4": (False, True),
        "A-K2K4": (True, True),
    }
    for name, (angular, use_k4) in configs.items():
        pred, state = predict(f0, angular=angular, use_k4=use_k4)
        final = pred[-1]
        arms[name] = {
            "final_mean": final.tolist(),
            "mse": float(np.mean((final - exact) ** 2)),
            "state": state,
        }

    EG = arms["G-K2"]["mse"]
    EA = arms["A-K2"]["mse"]
    EGK = arms["G-K2K4"]["mse"]
    EAK = arms["A-K2K4"]["mse"]
    cost = production_cost_upper()

    gates = {
        "target_firewall": True,
        "radial_homogeneity": max(x["homogeneity_max_rel"] for x in fixtures) <= TOL,
        "layer0_mean_conversion": max(x["mean_conversion_rel"] for x in fixtures) <= TOL,
        "layer0_raw_second_invariance": max(
            x["raw_second_invariance_rel"] for x in fixtures
        ) <= TOL,
        "angular_k4_s4_identity": max(x["s4_dense_rel"] for x in fixtures) <= TOL,
        "angular_k4_s22_identity": max(
            x["s22_dense_offdiag_rel"] for x in fixtures
        ) <= TOL,
        "k4_off_runtime_clean": (
            arms["G-K2"]["state"]["k4_update_calls"] == 0
            and arms["A-K2"]["state"]["k4_update_calls"] == 0
            and not arms["G-K2"]["state"]["k4_runtime_enabled"]
            and not arms["A-K2"]["state"]["k4_runtime_enabled"]
        ),
        "gauge_only_scientific": EA <= 0.98 * EG,
        "complete_cost": cost["utilization_upper"] <= COST_CAP,
    }

    return {
        "experiment": "E159",
        "mechanism": "published_angular_radial_K2_ablation",
        "target_free": True,
        "fixtures": fixtures,
        "exact2d": {
            "sector_count": int(sectors),
            "exact_gaussian_mean": exact.tolist(),
            "arms": arms,
            "effects": {
                "gauge_delta_mse": EA - EG,
                "gauge_ratio": EA / max(EG, 1e-300),
                "k4_given_angular_delta_mse": EAK - EA,
                "k4_given_angular_ratio": EAK / max(EA, 1e-300),
                "k4_given_gaussian_delta_mse": EGK - EG,
                "k4_given_gaussian_ratio": EGK / max(EG, 1e-300),
                "published_switch_k2k4_ratio": EAK / max(EGK, 1e-300),
            },
            "primary_required_gauge_ratio_max": 0.98,
        },
        "cost": cost,
        "gates": gates,
        "firewall": {
            "benchmark_networks": False,
            "public_targets": False,
            "mini": False,
            "scorer": False,
            "holdout": False,
            "full_suite": False,
            "submission": False,
            "sampling": False,
            "strassen": False,
            "E151_E154_E157_imports": False,
        },
    }


def canonical(x: dict) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        first = run_once()
        replay = run_once()
        det = canonical(first) == canonical(replay)
        first["gates"]["deterministic_replay"] = det
        first["gates"]["exactly_one_external_run"] = True
        passed = all(bool(v) for v in first["gates"].values())
        first["status"] = "GO" if passed else "TERMINAL_NO_GO"
        first["decision"] = (
            "E159_TARGET_FREE_SCIENTIFIC_GO_ANGULAR_GAUGE"
            if passed
            else "E159_TERMINAL_NO_GO_PUBLISHED_ANGULAR_GAUGE"
        )
        first["run_policy"] = {
            "external_scientific_runs_authorized": 1,
            "in_process_replays": 2,
            "rerun": False,
            "rescue": False,
            "sweep": False,
        }
        out.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n")
        print(json.dumps(first, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        receipt = {
            "experiment": "E159",
            "status": "TERMINAL_NO_GO",
            "decision": "E159_TERMINAL_NO_GO_PUBLISHED_ANGULAR_GAUGE",
            "reason": "ONE_SHOT_EXECUTION_EXCEPTION",
            "exception_type": type(exc).__name__,
            "exception": str(exc),
            "traceback": traceback.format_exc(),
            "target_free": True,
            "rerun": False,
            "rescue": False,
            "sweep": False,
        }
        out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
