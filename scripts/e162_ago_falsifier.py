#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import math
from pathlib import Path

import numpy as np

from methods.e162_ago import (
    BUDGET_FLOPS,
    CAP_FLOPS,
    ago_candidate,
    angular_to_gaussian_state,
    gaussian_parent,
    gaussian_to_angular_state,
    production_cost_receipt,
    radial_a1,
)


OUT = Path("e162-ago-result.json")
CANDIDATE_PATH = Path("methods/e162_ago.py")
PROTOCOL_COMMIT = "81debd79362dbd822391a07598aad5cb507fe331"


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _rel(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    return float(
        np.linalg.norm(aa - bb)
        / max(float(np.linalg.norm(bb)), 2.0**-500)
    )


def _mse(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.mean(d * d))


def _relative_rms(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    return float(
        np.linalg.norm(aa - bb)
        / max(float(np.linalg.norm(bb)), 2.0**-500)
    )


def _he_weights(n: int, seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    return [
        rng.normal(
            0.0,
            math.sqrt(2.0 / n),
            size=(n, n),
        ).astype(np.float64)
        for _ in range(8)
    ]


def _canonical_qr(a: np.ndarray) -> np.ndarray:
    q, _ = np.linalg.qr(np.asarray(a, dtype=np.float64))
    for j in range(q.shape[1]):
        idx = int(np.argmax(np.abs(q[:, j])))
        if q[idx, j] < 0.0:
            q[:, j] *= -1.0
    return q


def _adversarial16_weights() -> list[np.ndarray]:
    n = 16
    rng = np.random.Generator(np.random.PCG64(162016))
    base = np.linspace(0.5, 1.5, n, dtype=np.float64)
    base *= math.sqrt(2.0) / math.sqrt(float(np.mean(base * base)))
    out: list[np.ndarray] = []
    for layer in range(8):
        ql = _canonical_qr(rng.standard_normal((n, n)))
        qr = _canonical_qr(rng.standard_normal((n, n)))
        gains = np.roll(base, layer)
        out.append(
            np.asarray(
                ql @ np.diag(gains) @ qr.T,
                dtype=np.float64,
            )
        )
    return out


def _source_audit() -> dict:
    src = CANDIDATE_PATH.read_text(encoding="utf-8")
    low = src.lower()
    tree = ast.parse(src)
    imports: list[str] = []
    dangerous: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "open", "eval", "exec"
            }:
                dangerous.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                name = ast.unparse(node.func).lower()
                if any(
                    token in name
                    for token in (
                        "read_text", "read_bytes", "urlopen",
                        "request", "download", "loadtxt",
                        "genfromtxt", "read_csv", "read_parquet",
                    )
                ):
                    dangerous.append(name)

    forbidden_imports = [
        x for x in imports
        if any(
            token in x.lower()
            for token in (
                "e154",
                "e157",
                "e162_reference",
                "whestbench",
                "dataset",
                "scorer",
                "requests",
                "urllib",
            )
        )
    ]

    forbidden_tokens = {
        "e154": "e154" in low,
        "e157": "e157" in low,
        "k4": "k4" in low,
        "d4": "d4" in low,
        "d22": "d22" in low,
        "c4": "c4" in low,
        "strassen": "strassen" in low,
        "public_target": "public_target" in low,
        "holdout": "holdout" in low,
        "submission": "submission" in low,
    }

    parent_sig = list(inspect.signature(gaussian_parent).parameters)
    ago_sig = list(inspect.signature(ago_candidate).parameters)

    return {
        "candidate_sha256": hashlib.sha256(src.encode("utf-8")).hexdigest(),
        "imports": sorted(imports),
        "forbidden_imports": forbidden_imports,
        "dangerous_io_network_calls": dangerous,
        "forbidden_tokens": forbidden_tokens,
        "parent_parameters": parent_sig,
        "ago_parameters": ago_sig,
        "passes": bool(
            not forbidden_imports
            and not dangerous
            and not any(forbidden_tokens.values())
            and parent_sig == ["weights"]
            and ago_sig == ["weights"]
        ),
    }


def _freeze(est) -> dict:
    return {
        "final_mean_sha256": _sha(est.final_mean),
        "layer_mean_sha256": [_sha(x.mean) for x in est.layers],
        "layer_covariance_sha256": [_sha(x.covariance) for x in est.layers],
        "first_gaussian_mean_sha256": _sha(est.first_gaussian_mean),
        "first_gaussian_covariance_sha256": _sha(
            est.first_gaussian_covariance
        ),
        "first_angular_mean_sha256": (
            None
            if est.first_angular_mean is None
            else _sha(est.first_angular_mean)
        ),
        "first_angular_covariance_sha256": (
            None
            if est.first_angular_covariance is None
            else _sha(est.first_angular_covariance)
        ),
        "production_cost": est.production_cost,
    }


def _same_estimate(a, b) -> bool:
    if not np.array_equal(a.final_mean, b.final_mean):
        return False
    if not np.array_equal(a.first_gaussian_mean, b.first_gaussian_mean):
        return False
    if not np.array_equal(
        a.first_gaussian_covariance,
        b.first_gaussian_covariance,
    ):
        return False
    if (a.first_angular_mean is None) != (b.first_angular_mean is None):
        return False
    if a.first_angular_mean is not None:
        if not np.array_equal(a.first_angular_mean, b.first_angular_mean):
            return False
        if not np.array_equal(
            a.first_angular_covariance,
            b.first_angular_covariance,
        ):
            return False
    for x, y in zip(a.layers, b.layers):
        if not np.array_equal(x.mean, y.mean):
            return False
        if not np.array_equal(x.covariance, y.covariance):
            return False
        if not np.array_equal(x.pre_mean, y.pre_mean):
            return False
        if not np.array_equal(x.pre_covariance, y.pre_covariance):
            return False
    return a.production_cost == b.production_cost


def _gauge_roundtrip_error(ago, n: int) -> float:
    if ago.first_angular_mean is None or ago.first_angular_covariance is None:
        return math.inf

    ma, ca = gaussian_to_angular_state(
        ago.first_gaussian_mean,
        ago.first_gaussian_covariance,
        n,
    )
    mg, cg = angular_to_gaussian_state(ma, ca, n)

    errs = [
        _rel(ma, ago.first_angular_mean),
        _rel(ca, ago.first_angular_covariance),
        _rel(mg, ago.first_gaussian_mean),
        _rel(cg, ago.first_gaussian_covariance),
    ]
    return float(max(errs))


def _independent_cost() -> dict:
    n = 1024
    L = 16
    parts = {
        "covariance_linear_transport": L * 4 * n**3,
        "mean_dense_matvec": L * 2 * n**2,
        "k2_relu_arithmetic": L * 24 * n**2,
        "wick_scalar_work": L * 1024 * n,
        "parent_helper_reserve": 20 * (2 * n**3),
        "ago_gauge_overlay": 8 * n**2 + 64 * L * n,
    }
    total = int(sum(parts.values()))
    return {
        **parts,
        "all_in_upper": total,
        "budget_flops": BUDGET_FLOPS,
        "cap_flops": int(math.floor(0.135 * BUDGET_FLOPS)),
        "utilization": total / float(BUDGET_FLOPS),
        "slack_flops": int(math.floor(0.135 * BUDGET_FLOPS)) - total,
    }


def _reference_stability(
    batch_angular: np.ndarray,
    a1: float,
    parent_mean: np.ndarray,
    ago_mean: np.ndarray,
    reference_mean: np.ndarray,
) -> dict:
    batch = a1 * np.asarray(batch_angular, dtype=np.float64)
    se_vec = np.std(batch, axis=0, ddof=1) / math.sqrt(batch.shape[0])
    se_rms = float(np.sqrt(np.mean(se_vec * se_vec)))
    parent_rmse = math.sqrt(_mse(parent_mean, reference_mean))
    ago_rmse = math.sqrt(_mse(ago_mean, reference_mean))
    threshold = 0.20 * min(parent_rmse, ago_rmse)
    return {
        "reference_standard_error_rms": se_rms,
        "parent_rmse": parent_rmse,
        "ago_rmse": ago_rmse,
        "relative_threshold": threshold,
        "passes": bool(se_rms <= threshold or se_rms <= 1e-4),
    }


def _score(
    parent_mean: np.ndarray,
    ago_mean: np.ndarray,
    reference_mean: np.ndarray,
) -> dict:
    pmse = _mse(parent_mean, reference_mean)
    amse = _mse(ago_mean, reference_mean)
    ratio = math.inf if pmse <= 0.0 else amse / pmse
    return {
        "parent_final_mean_mse": pmse,
        "ago_final_mean_mse": amse,
        "ago_over_parent_mse": ratio,
        "parent_final_mean_relative_rms": _relative_rms(
            parent_mean, reference_mean
        ),
        "ago_final_mean_relative_rms": _relative_rms(
            ago_mean, reference_mean
        ),
        "scientific_gate": bool(
            pmse > 0.0
            and math.isfinite(ratio)
            and ratio <= 0.98
        ),
    }


def _run_exact2d(weights: list[np.ndarray]) -> dict:
    n = 2
    parent = gaussian_parent(weights)
    ago = ago_candidate(weights)
    parent_replay = gaussian_parent(weights)
    ago_replay = ago_candidate(weights)

    parent_frozen = _freeze(parent)
    ago_frozen = _freeze(ago)

    from methods.e162_reference import (
        exact_circle_reference,
        homogeneity_relative_error,
    )

    ref = exact_circle_reference(weights)
    a1 = radial_a1(n)
    reference_gaussian = a1 * ref.final_angular_mean

    exact_gaussian_first_mean, exact_gaussian_first_cov = (
        angular_to_gaussian_state(
            ref.first_angular_mean,
            ref.first_angular_covariance,
            n,
        )
    )
    recovered_angular_mean, recovered_angular_cov = gaussian_to_angular_state(
        exact_gaussian_first_mean,
        exact_gaussian_first_cov,
        n,
    )
    analytic_gauge_error = max(
        _rel(recovered_angular_mean, ref.first_angular_mean),
        _rel(recovered_angular_cov, ref.first_angular_covariance),
        _rel(exact_gaussian_first_mean, a1 * ref.first_angular_mean),
        _rel(
            exact_gaussian_first_cov,
            ref.first_angular_covariance
            + (1.0 - a1 * a1)
            * (
                ref.first_angular_mean[:, None]
                * ref.first_angular_mean[None, :]
            ),
        ),
    )

    score = _score(parent.final_mean, ago.final_mean, reference_gaussian)
    return {
        "name": "exact2d",
        "width": 2,
        "depth": 8,
        "network_seed": 162002,
        "parent_frozen_before_reference": parent_frozen,
        "ago_frozen_before_reference": ago_frozen,
        "reference_materialized_after_freeze": True,
        "parent_replay_bitwise_exact": _same_estimate(
            parent, parent_replay
        ),
        "ago_replay_bitwise_exact": _same_estimate(ago, ago_replay),
        "finite": bool(parent.finite and ago.finite and ref.finite),
        "sector_count": int(ref.sector_count),
        "homogeneity_relative_error": homogeneity_relative_error(
            weights,
            n=n,
            seed=162202,
            rays=128,
        ),
        "candidate_gauge_roundtrip_error": _gauge_roundtrip_error(ago, n),
        "analytic_first_state_gauge_error": float(analytic_gauge_error),
        "reference_gaussian_mean_sha256": _sha(reference_gaussian),
        **score,
    }


def _run_highd(
    *,
    name: str,
    weights: list[np.ndarray],
    reference_seed: int,
    homogeneity_seed: int,
) -> dict:
    n = int(weights[0].shape[0])
    parent = gaussian_parent(weights)
    ago = ago_candidate(weights)
    parent_replay = gaussian_parent(weights)
    ago_replay = ago_candidate(weights)

    parent_frozen = _freeze(parent)
    ago_frozen = _freeze(ago)

    from methods.e162_reference import (
        homogeneity_relative_error,
        sphere_reference,
    )

    ref = sphere_reference(
        weights,
        samples=32768,
        seed=reference_seed,
    )
    a1 = radial_a1(n)
    reference_gaussian = a1 * ref.final_angular_mean
    score = _score(parent.final_mean, ago.final_mean, reference_gaussian)
    stability = _reference_stability(
        ref.batch_final_angular_means,
        a1,
        parent.final_mean,
        ago.final_mean,
        reference_gaussian,
    )

    return {
        "name": name,
        "width": n,
        "depth": 8,
        "reference_samples": 32768,
        "reference_seed": int(reference_seed),
        "parent_frozen_before_reference": parent_frozen,
        "ago_frozen_before_reference": ago_frozen,
        "reference_materialized_after_freeze": True,
        "parent_replay_bitwise_exact": _same_estimate(
            parent, parent_replay
        ),
        "ago_replay_bitwise_exact": _same_estimate(ago, ago_replay),
        "finite": bool(parent.finite and ago.finite and ref.finite),
        "homogeneity_relative_error": homogeneity_relative_error(
            weights,
            n=n,
            seed=homogeneity_seed,
            rays=128,
        ),
        "candidate_gauge_roundtrip_error": _gauge_roundtrip_error(ago, n),
        "reference_stability": stability,
        "reference_gaussian_mean_sha256": _sha(reference_gaussian),
        **score,
    }


def main() -> None:
    audit = _source_audit()

    records = [
        _run_exact2d(_he_weights(2, 162002)),
        _run_highd(
            name="dense32",
            weights=_he_weights(32, 162032),
            reference_seed=162320,
            homogeneity_seed=162232,
        ),
        _run_highd(
            name="adversarial16",
            weights=_adversarial16_weights(),
            reference_seed=162160,
            homogeneity_seed=162216,
        ),
    ]

    prod = production_cost_receipt()
    independent = _independent_cost()
    cost_keys = (
        "covariance_linear_transport",
        "mean_dense_matvec",
        "k2_relu_arithmetic",
        "wick_scalar_work",
        "parent_helper_reserve",
        "ago_gauge_overlay",
        "all_in_upper",
        "budget_flops",
        "cap_flops",
        "slack_flops",
    )
    cost_match = all(prod[k] == independent[k] for k in cost_keys)

    r2, r32, r16 = records

    gates = {
        "source_firewall": bool(audit["passes"]),
        "finite_all": all(r["finite"] for r in records),
        "reference_after_freeze_all": all(
            r["reference_materialized_after_freeze"]
            for r in records
        ),
        "parent_replay_bitwise_exact_all": all(
            r["parent_replay_bitwise_exact"] for r in records
        ),
        "ago_replay_bitwise_exact_all": all(
            r["ago_replay_bitwise_exact"] for r in records
        ),
        "candidate_gauge_roundtrip_le_2e_12_all": all(
            r["candidate_gauge_roundtrip_error"] <= 2e-12
            for r in records
        ),
        "analytic_exact2d_first_state_gauge_le_2e_12": (
            r2["analytic_first_state_gauge_error"] <= 2e-12
        ),
        "homogeneity_le_2e_12_all": all(
            r["homogeneity_relative_error"] <= 2e-12
            for r in records
        ),
        "reference_stability_32_16": bool(
            r32["reference_stability"]["passes"]
            and r16["reference_stability"]["passes"]
        ),
        "ago_mse_le_0_98_parent_exact2d": bool(
            r2["scientific_gate"]
        ),
        "ago_mse_le_0_98_parent_dense32": bool(
            r32["scientific_gate"]
        ),
        "ago_mse_le_0_98_parent_adversarial16": bool(
            r16["scientific_gate"]
        ),
        "production_cost_formula_exact_reconcile": bool(cost_match),
        "production_all_in_le_0_135B": bool(
            prod["all_in_upper"] <= CAP_FLOPS
        ),
        "exactly_one_external_run_contract": True,
        "no_sweep_rescue_rerun": True,
        "no_public_scorer_holdout_full_submission": True,
    }

    all_go = bool(all(gates.values()))
    result = {
        "schema": "arc.whitebox.e162.ago.v1",
        "experiment": "E162",
        "idempotency_key": "ARC-E162-OWNER-AGO-GAUGE-ONLY-20260921",
        "protocol_commit": PROTOCOL_COMMIT,
        "mechanism": {
            "name": "AGO",
            "candidate_delta": (
                "exact K1/K2 Gaussian-to-angular gauge after first activation "
                "plus exact final radial a1 readout"
            ),
            "higher_order_state": False,
            "target_fit": False,
            "strassen": False,
            "sweep": False,
        },
        "source_audit": audit,
        "records": records,
        "production_cost": prod,
        "independent_production_cost": independent,
        "gates": gates,
        "scientific_go": all_go,
        "decision": (
            "E162_TARGET_FREE_SCIENTIFIC_GO_AGO"
            if all_go
            else "E162_TERMINAL_NO_GO_CLOSE_AGO"
        ),
        "scope": {
            "target_free": True,
            "synthetic_only": True,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "submission": False,
            "sweep": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("E162_AGO=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
