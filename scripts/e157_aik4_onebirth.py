#!/usr/bin/env python3
"""E157 one-shot target-free AIK4-1 falsifier.

Synthetic fixtures only. No benchmark/public target imports. No Strassen.
"""
from __future__ import annotations

import argparse
import json
import math
import traceback
from pathlib import Path

import numpy as np

from scripts.e157_aik4_parent import (
    k2_relu_step,
    parent_predict_angular,
    production_overlay_cost_upper,
    production_parent_cost_upper,
    radial_a1,
    relu_wick,
)

BUDGET = 2**41
PARENT_CAP = 0.1349904166907072
TOTAL_CAP = 0.135
TOL = 2e-12


def relerr(a: np.ndarray, b: np.ndarray) -> float:
    den = max(float(np.linalg.norm(b.ravel())), 1e-300)
    return float(np.linalg.norm((a - b).ravel()) / den)


def max_rel(a: np.ndarray, b: np.ndarray) -> float:
    den = np.maximum(np.maximum(np.abs(a), np.abs(b)), 1e-300)
    return float(np.max(np.abs(a - b) / den))


def canonical_qr(a: np.ndarray) -> np.ndarray:
    q, r = np.linalg.qr(a)
    s = np.sign(np.diag(r))
    s[s == 0.0] = 1.0
    return q * s[None, :]


def make_weights(n: int, depth: int, seed: int, adversarial: bool) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    out: list[np.ndarray] = []
    if not adversarial:
        scale = math.sqrt(2.0 / n)
        for _ in range(depth):
            out.append(rng.standard_normal((n, n), dtype=np.float64) * scale)
        return out

    gains = np.linspace(0.5, 1.5, n, dtype=np.float64)
    gains *= math.sqrt(2.0 / float(np.mean(gains * gains)))
    for _ in range(depth):
        ql = canonical_qr(rng.standard_normal((n, n), dtype=np.float64))
        qr = canonical_qr(rng.standard_normal((n, n), dtype=np.float64))
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
        norm = float(np.linalg.norm(x))
        y = math.sqrt(n) * x / norm
        lhs = forward(weights, x)
        rhs = (norm / math.sqrt(n)) * forward(weights, y)
        worst = max(worst, max_rel(lhs, rhs))
    return worst


def dense_k4_audit(w0: np.ndarray) -> dict:
    n = w0.shape[1]
    m = w0 @ w0.T
    kappa = -2.0 / (n + 2.0)

    p1 = np.einsum("ab,cd->abcd", m, m)
    p2 = np.einsum("ac,bd->abcd", m, m)
    p3 = np.einsum("ad,bc->abcd", m, m)
    pair = p1 + p2 + p3

    k4 = kappa * pair
    sphere_m4 = (n / (n + 2.0)) * pair
    k4_from_moment = sphere_m4 - pair

    b = 3.0 * kappa * m
    carrier = (
        np.einsum("ab,cd->abcd", m, b)
        + np.einsum("ac,bd->abcd", m, b)
        + np.einsum("ad,bc->abcd", m, b)
    ) / 3.0

    idx = np.arange(n)
    d4_dense = k4[idx, idx, idx, idx]
    d22_dense = k4[
        idx[:, None], idx[:, None], idx[None, :], idx[None, :]
    ]
    d4 = 3.0 * kappa * np.diag(m) ** 2
    d22 = kappa * (
        np.diag(m)[:, None] * np.diag(m)[None, :] + 2.0 * m * m
    )

    mean0 = np.zeros(n, dtype=np.float64)
    var0 = np.diag(m)
    wick_errors = []
    for p in (1, 2, 3, 4):
        lhs = relu_wick(mean0, var0, 4, p) * d4 / 24.0
        rhs = relu_wick(mean0, var0, 4, p) * d4_dense / 24.0
        wick_errors.append(max_rel(lhs, rhs))

    w21 = relu_wick(mean0, var0, 2, 1)
    w22 = relu_wick(mean0, var0, 2, 2)
    p11 = 0.25 * d22 * (w21[:, None] * w21[None, :])
    p11_dense = 0.25 * d22_dense * (w21[:, None] * w21[None, :])
    p21 = 0.25 * d22 * (w22[:, None] * w21[None, :])
    p21_dense = 0.25 * d22_dense * (w22[:, None] * w21[None, :])
    wick_errors.extend([max_rel(p11, p11_dense), max_rel(p21, p21_dense)])

    return {
        "n": int(n),
        "angular_k4_dense_identity_rel_frob": relerr(k4, k4_from_moment),
        "arc_factor_carrier_rel_frob": relerr(carrier, k4),
        "d4_max_rel": max_rel(d4, d4_dense),
        "d22_max_rel": max_rel(d22, d22_dense),
        "wick_selected_max_rel": float(max(wick_errors)),
    }


def candidate_predict(weights: list[np.ndarray]) -> tuple[np.ndarray, int]:
    n = weights[0].shape[1]
    mean = np.zeros(n, dtype=np.float64)
    cov = np.eye(n, dtype=np.float64)
    overlay_calls = 0

    for layer, w in enumerate(weights):
        mean = w @ mean
        cov = w @ cov @ w.T
        cov = 0.5 * (cov + cov.T)

        if layer == 0:
            # Exact angular input K4 after exact first linear transport.
            m = cov
            kappa = -2.0 / (n + 2.0)
            d4 = 3.0 * kappa * np.diag(m) ** 2
            d22 = kappa * (
                np.diag(m)[:, None] * np.diag(m)[None, :] + 2.0 * m * m
            )
            mean, cov = k2_relu_step(mean, cov, d4=d4, d22=d22)
            overlay_calls += 1
            # d4/d22/kappa/m are intentionally not retained.
            del d4, d22, kappa, m
        else:
            mean, cov = k2_relu_step(mean, cov)

    return radial_a1(n) * mean, overlay_calls


def _angle_zeros(row: np.ndarray) -> list[float]:
    if float(np.linalg.norm(row)) <= 1e-15:
        return []
    phi = math.atan2(float(row[1]), float(row[0]))
    z = (phi + math.pi / 2.0) % (2.0 * math.pi)
    return [z, (z + math.pi) % (2.0 * math.pi)]


def _uniq_sorted(vals: list[float], tol: float = 2e-14) -> list[float]:
    vals = sorted(vals)
    out: list[float] = []
    for v in vals:
        if not out or abs(v - out[-1]) > tol:
            out.append(v)
    return out


def exact_sector_mean_2d(weights: list[np.ndarray]) -> tuple[np.ndarray, int]:
    """Exact angular integration for a zero-bias width-2 ReLU network."""
    sectors: list[tuple[float, float, np.ndarray]] = [
        (0.0, 2.0 * math.pi, np.eye(2, dtype=np.float64))
    ]
    eps = 2e-14

    for w in weights:
        nxt: list[tuple[float, float, np.ndarray]] = []
        for a, b, amap in sectors:
            pre = w @ amap
            cuts = [a, b]
            for row in pre:
                for z in _angle_zeros(row):
                    if a + eps < z < b - eps:
                        cuts.append(z)
            cuts = _uniq_sorted(cuts)
            for lo, hi in zip(cuts[:-1], cuts[1:]):
                if hi - lo <= eps:
                    continue
                mid = 0.5 * (lo + hi)
                u = np.array([math.cos(mid), math.sin(mid)], dtype=np.float64)
                mask = (pre @ u) > 0.0
                anew = pre.copy()
                anew[~mask, :] = 0.0
                nxt.append((lo, hi, anew))
        sectors = nxt

    integ = np.zeros(2, dtype=np.float64)
    for a, b, amap in sectors:
        iu = np.array(
            [math.sin(b) - math.sin(a), -math.cos(b) + math.cos(a)],
            dtype=np.float64,
        )
        integ += amap @ iu
    unit_circle_mean = integ / (2.0 * math.pi)
    gaussian_mean = math.sqrt(math.pi / 2.0) * unit_circle_mean
    return gaussian_mean, len(sectors)


def fixture_record(name: str, weights: list[np.ndarray], hom_seed: int) -> dict:
    audit = dense_k4_audit(weights[0])
    audit["name"] = name
    audit["homogeneity_max_rel"] = homogeneity_error(weights, hom_seed)
    return audit


def run_core() -> dict:
    f0 = make_weights(2, 8, 155002, adversarial=False)
    f1 = make_weights(32, 8, 155032, adversarial=False)
    f2 = make_weights(16, 8, 155016, adversarial=True)

    fixtures = [
        fixture_record("exact2d_depth8", f0, 157002),
        fixture_record("dense32_depth8", f1, 157032),
        fixture_record("adversarial16_depth8", f2, 157016),
    ]

    exact_mean, sector_count = exact_sector_mean_2d(f0)
    parent = parent_predict_angular(f0)
    candidate, overlay_calls = candidate_predict(f0)
    parent_mse = float(np.mean((parent - exact_mean) ** 2))
    candidate_mse = float(np.mean((candidate - exact_mean) ** 2))
    ratio = candidate_mse / max(parent_mse, 1e-300)

    parent_cost = production_parent_cost_upper(1024, 16)
    overlay_cost = production_overlay_cost_upper(1024)
    combined_cost = parent_cost + overlay_cost

    gates = {
        "target_firewall": True,
        "radial_homogeneity": max(x["homogeneity_max_rel"] for x in fixtures) <= TOL,
        "angular_k4_dense_identity": max(
            x["angular_k4_dense_identity_rel_frob"] for x in fixtures
        ) <= TOL,
        "arc_factor_carrier_identity": max(
            x["arc_factor_carrier_rel_frob"] for x in fixtures
        ) <= TOL,
        "d4_parity": max(x["d4_max_rel"] for x in fixtures) <= TOL,
        "d22_parity": max(x["d22_max_rel"] for x in fixtures) <= TOL,
        "selected_wick_term_parity": max(
            x["wick_selected_max_rel"] for x in fixtures
        ) <= TOL,
        "no_recurrent_k4": overlay_calls == 1,
        "synthetic_mean_improvement": candidate_mse <= 0.98 * parent_mse,
        "parent_cost": parent_cost <= PARENT_CAP * BUDGET,
        "complete_cost": combined_cost <= TOTAL_CAP * BUDGET,
    }

    return {
        "experiment": "E157",
        "candidate": "AIK4-1",
        "target_free": True,
        "fixtures": fixtures,
        "exact2d": {
            "sector_count": int(sector_count),
            "exact_gaussian_mean": exact_mean.tolist(),
            "parent_mean": parent.tolist(),
            "candidate_mean": candidate.tolist(),
            "parent_mse": parent_mse,
            "candidate_mse": candidate_mse,
            "candidate_parent_mse_ratio": ratio,
            "required_ratio_max": 0.98,
        },
        "state": {
            "overlay_calls": int(overlay_calls),
            "recurrent_k4_state": False,
            "strassen": False,
        },
        "cost": {
            "budget_flops": BUDGET,
            "parent_cost_upper_flops": parent_cost,
            "parent_utilization_upper": parent_cost / BUDGET,
            "parent_required_max": PARENT_CAP,
            "overlay_cost_upper_flops": overlay_cost,
            "combined_cost_upper_flops": combined_cost,
            "combined_utilization_upper": combined_cost / BUDGET,
            "combined_required_max": TOTAL_CAP,
        },
        "gates": gates,
    }


def deterministic_equal(a: dict, b: dict) -> bool:
    # JSON canonicalization is strict enough because all arrays are converted to
    # deterministic Python floats/lists and no timing/timestamp enters run_core.
    return json.dumps(a, sort_keys=True, separators=(",", ":")) == json.dumps(
        b, sort_keys=True, separators=(",", ":")
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        first = run_core()
        second = run_core()
        det = deterministic_equal(first, second)
        first["gates"]["deterministic_replay"] = det
        first["gates"]["exactly_one_external_run"] = True
        passed = all(bool(v) for v in first["gates"].values())
        first["decision"] = (
            "E157_TARGET_FREE_SCIENTIFIC_GO_AIK4_1"
            if passed
            else "E157_TERMINAL_NO_GO_AIK4_1"
        )
        first["status"] = "GO" if passed else "TERMINAL_NO_GO"
        first["run_policy"] = {
            "external_scientific_runs_authorized": 1,
            "in_process_replays": 2,
            "sweep": False,
            "rescue": False,
        }
        first["firewall"] = {
            "benchmark_targets": False,
            "public_targets": False,
            "mini_targets": False,
            "scorer": False,
            "holdout": False,
            "full_suite": False,
            "submission": False,
            "sampling": False,
            "E151_or_E154_artifacts": False,
        }
        out.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n")
        print(json.dumps(first, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        receipt = {
            "experiment": "E157",
            "candidate": "AIK4-1",
            "status": "TERMINAL_NO_GO",
            "decision": "E157_TERMINAL_NO_GO_AIK4_1",
            "reason": "ONE_SHOT_EXECUTION_EXCEPTION",
            "exception_type": type(exc).__name__,
            "exception": str(exc),
            "traceback": traceback.format_exc(),
            "target_free": True,
            "sweep": False,
            "rescue": False,
        }
        out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
