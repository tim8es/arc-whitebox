#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import math
from pathlib import Path

import numpy as np

from methods.e154_angular_radial_k4 import (
    BUDGET_FLOPS,
    CAP_FLOPS,
    STRASSEN_LEVELS,
    angular_closure,
    production_cost_receipt,
    radial_a1,
    sphere_input_k4_diag,
)

OUT = Path("e154-angular-radial-k4.json")
CANDIDATE_PATH = Path("methods/e154_angular_radial_k4.py")
PROTOCOL_COMMIT = "b4d3f6d034269d664c05c2fb4003160168b1fbd7"


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _rel(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    return float(
        np.linalg.norm(aa - bb)
        / max(float(np.linalg.norm(bb)), 2.0 ** -500)
    )


def _rms(a: np.ndarray) -> float:
    x = np.asarray(a, dtype=np.float64)
    return float(np.sqrt(np.mean(x * x)))


def _relative_rms(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    return float(
        np.sqrt(np.sum((aa - bb) ** 2))
        / max(float(np.sqrt(np.sum(bb * bb))), 2.0 ** -500)
    )


def _he_weights(n: int, seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    return [
        rng.normal(
            0.0, math.sqrt(2.0 / n), size=(n, n)
        ).astype(np.float64)
        for _ in range(8)
    ]


def _adversarial16_weights() -> list[np.ndarray]:
    n = 16
    rng = np.random.Generator(np.random.PCG64(154016))
    gains0 = np.geomspace(0.70, 1.30, n)
    out: list[np.ndarray] = []
    for layer in range(8):
        q1, _ = np.linalg.qr(rng.standard_normal((n, n)))
        q2, _ = np.linalg.qr(rng.standard_normal((n, n)))
        gains = np.roll(gains0, layer)
        w = math.sqrt(2.0) * q1 @ np.diag(gains) @ q2.T
        out.append(np.asarray(w, dtype=np.float64))
    return out


def _source_audit() -> dict:
    src = CANDIDATE_PATH.read_text(encoding="utf-8")
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
                "e151", "e154_reference", "whestbench",
                "dataset", "scorer", "requests", "urllib",
            )
        )
    ]
    sig = inspect.signature(angular_closure)
    params = list(sig.parameters)
    return {
        "candidate_sha256": hashlib.sha256(src.encode("utf-8")).hexdigest(),
        "imports": sorted(imports),
        "forbidden_imports": forbidden_imports,
        "dangerous_io_network_calls": dangerous,
        "callable_parameters": params,
        "strassen_levels": STRASSEN_LEVELS,
        "strassen_function_absent": "strassen_mm" not in src.lower(),
        "passes": bool(
            not forbidden_imports
            and not dangerous
            and params == ["weights", "use_k4"]
            and STRASSEN_LEVELS == 0
            and "strassen_mm" not in src.lower()
        ),
    }


def _independent_cost() -> dict:
    n = 1024
    L = 16
    parts = {
        "covariance_classical_two_gemm": L * 4 * n**3,
        "mean_matvec": L * 2 * n**2,
        "relu_covariance_update": L * 16 * n**2,
        "k4_diagonal_and_wick": L * 512 * n,
        "radial_scalar_helpers": L * 128 * n,
        "helper_accounting_reserve": 20 * (2 * n**3),
    }
    total = int(sum(parts.values()))
    return {
        **parts,
        "all_in_upper": total,
        "budget_flops": BUDGET_FLOPS,
        "cap_flops": int(math.floor(0.135 * BUDGET_FLOPS)),
        "utilization": total / float(BUDGET_FLOPS),
        "slack_flops": int(math.floor(0.135 * BUDGET_FLOPS)) - total,
        "strassen_levels": 0,
    }


def _freeze(est) -> dict:
    return {
        "angular_mean_sha256": _sha(est.angular_mean),
        "gaussian_mean_sha256": _sha(est.gaussian_mean),
        "pre_k4_sha256": [_sha(x.pre_k4_diag) for x in est.layers],
        "layer_mean_sha256": [_sha(x.mean) for x in est.layers],
        "layer_cov_sha256": [_sha(x.covariance) for x in est.layers],
        "production_cost": est.production_cost,
    }


def _same_estimate(a, b) -> bool:
    if not np.array_equal(a.angular_mean, b.angular_mean):
        return False
    if not np.array_equal(a.gaussian_mean, b.gaussian_mean):
        return False
    for x, y in zip(a.layers, b.layers):
        if not np.array_equal(x.pre_k4_diag, y.pre_k4_diag):
            return False
        if not np.array_equal(x.mean, y.mean):
            return False
        if not np.array_equal(x.covariance, y.covariance):
            return False
    return True


def _reference_stability(
    batch_angular: np.ndarray,
    a1: float,
    candidate_gaussian: np.ndarray,
    reference_gaussian: np.ndarray,
) -> dict:
    batch = a1 * np.asarray(batch_angular, dtype=np.float64)
    se_vec = np.std(batch, axis=0, ddof=1) / math.sqrt(batch.shape[0])
    se_rms = _rms(se_vec)
    err_rms = _rms(
        np.asarray(candidate_gaussian) - np.asarray(reference_gaussian)
    )
    return {
        "reference_standard_error_rms": se_rms,
        "candidate_error_rms": err_rms,
        "passes": bool(
            se_rms <= 0.20 * err_rms or se_rms <= 1e-4
        ),
    }


def _run_2d(weights: list[np.ndarray]) -> dict:
    baseline = angular_closure(weights, use_k4=False)
    candidate = angular_closure(weights, use_k4=True)
    replay = angular_closure(weights, use_k4=True)
    frozen = _freeze(candidate)

    from methods.e154_reference import (
        exact_circle_angular_mean,
        homogeneity_relative_error,
    )

    exact_angular, sector_count = exact_circle_angular_mean(weights)
    a1 = radial_a1(2)
    exact_gaussian = a1 * exact_angular
    b_err = _rel(baseline.gaussian_mean, exact_gaussian)
    c_err = _rel(candidate.gaussian_mean, exact_gaussian)
    hom = homogeneity_relative_error(
        weights, n=2, seed=154202, rays=128
    )
    input_identity_abs = abs(sphere_input_k4_diag(2) + 1.5)

    return {
        "name": "exact2d",
        "width": 2,
        "depth": 8,
        "network_seed": 154002,
        "candidate_frozen_before_reference": frozen,
        "reference_materialized_after_candidate_freeze": True,
        "candidate_replay_bitwise_exact": _same_estimate(candidate, replay),
        "candidate_finite": bool(candidate.finite),
        "reference_finite": bool(np.isfinite(exact_gaussian).all()),
        "sector_count": int(sector_count),
        "homogeneity_relative_error": hom,
        "input_k4_identity_absolute_error": input_identity_abs,
        "baseline_final_mean_relative_rms": b_err,
        "candidate_final_mean_relative_rms": c_err,
        "candidate_over_baseline": (
            c_err / b_err if b_err > 0.0 else math.inf
        ),
        "exact_angular_mean_sha256": _sha(exact_angular),
        "exact_gaussian_mean_sha256": _sha(exact_gaussian),
    }


def _run_highd(
    *,
    name: str,
    weights: list[np.ndarray],
    reference_seed: int,
) -> dict:
    n = weights[0].shape[0]
    baseline = angular_closure(weights, use_k4=False)
    candidate = angular_closure(weights, use_k4=True)
    replay = angular_closure(weights, use_k4=True)
    frozen = _freeze(candidate)

    from methods.e154_reference import (
        homogeneity_relative_error,
        sphere_reference,
    )

    ref = sphere_reference(
        weights,
        samples=32768,
        seed=reference_seed,
    )
    a1 = radial_a1(n)
    ref_gaussian = a1 * ref.final_angular_mean

    analytic_input = np.full(n, sphere_input_k4_diag(n), dtype=np.float64)
    input_k4_rel = _relative_rms(ref.input_k4_diag, analytic_input)

    first_analytic = candidate.layers[0].pre_k4_diag
    first_k4_rel = _relative_rms(ref.pre_k4_diag[0], first_analytic)

    cand_deep = np.concatenate(
        [x.pre_k4_diag for x in candidate.layers[1:]]
    )
    ref_deep = np.concatenate(list(ref.pre_k4_diag[1:]))
    deep_k4_rel = _relative_rms(cand_deep, ref_deep)

    b_err = _rel(baseline.gaussian_mean, ref_gaussian)
    c_err = _rel(candidate.gaussian_mean, ref_gaussian)
    stability = _reference_stability(
        ref.batch_final_means,
        a1,
        candidate.gaussian_mean,
        ref_gaussian,
    )
    hom = homogeneity_relative_error(
        weights,
        n=n,
        seed=reference_seed + 777,
        rays=128,
    )

    return {
        "name": name,
        "width": int(n),
        "depth": 8,
        "reference_samples": 32768,
        "reference_seed": int(reference_seed),
        "candidate_frozen_before_reference": frozen,
        "reference_materialized_after_candidate_freeze": True,
        "candidate_replay_bitwise_exact": _same_estimate(candidate, replay),
        "candidate_finite": bool(candidate.finite),
        "reference_finite": bool(ref.finite),
        "homogeneity_relative_error": hom,
        "input_k4_relative_rms": input_k4_rel,
        "first_preactivation_k4_relative_rms": first_k4_rel,
        "deep_preactivation_k4_relative_rms": deep_k4_rel,
        "baseline_final_mean_relative_rms": b_err,
        "candidate_final_mean_relative_rms": c_err,
        "candidate_over_baseline": (
            c_err / b_err if b_err > 0.0 else math.inf
        ),
        "reference_stability": stability,
        "reference_gaussian_mean_sha256": _sha(ref_gaussian),
        "reference_input_k4_sha256": _sha(ref.input_k4_diag),
        "reference_pre_k4_sha256": [_sha(x) for x in ref.pre_k4_diag],
    }


def main() -> None:
    weights2 = _he_weights(2, 154002)
    weights32 = _he_weights(32, 154032)
    weights16 = _adversarial16_weights()

    audit = _source_audit()

    records = [
        _run_2d(weights2),
        _run_highd(
            name="dense32",
            weights=weights32,
            reference_seed=154320,
        ),
        _run_highd(
            name="adversarial16",
            weights=weights16,
            reference_seed=154160,
        ),
    ]

    prod = production_cost_receipt()
    independent = _independent_cost()
    keys = (
        "covariance_classical_two_gemm",
        "mean_matvec",
        "relu_covariance_update",
        "k4_diagonal_and_wick",
        "radial_scalar_helpers",
        "helper_accounting_reserve",
        "all_in_upper",
        "budget_flops",
        "cap_flops",
        "slack_flops",
        "strassen_levels",
    )
    cost_match = all(prod[k] == independent[k] for k in keys)

    r2, r32, r16 = records
    gates = {
        "candidate_and_reference_finite_all": all(
            r["candidate_finite"] and r["reference_finite"]
            for r in records
        ),
        "deterministic_replay_bitwise_exact_all": all(
            r["candidate_replay_bitwise_exact"] for r in records
        ),
        "candidate_source_firewall_pass": bool(audit["passes"]),
        "reference_after_candidate_freeze_all": all(
            r["reference_materialized_after_candidate_freeze"]
            for r in records
        ),
        "homogeneity_relative_error_le_1e_12_all": all(
            r["homogeneity_relative_error"] <= 1e-12
            for r in records
        ),
        "analytic_2d_input_k4_abs_le_1e_14": (
            r2["input_k4_identity_absolute_error"] <= 1e-14
        ),
        "empirical_input_k4_rel_le_0_06_32_16": (
            r32["input_k4_relative_rms"] <= 0.06
            and r16["input_k4_relative_rms"] <= 0.06
        ),
        "first_preactivation_k4_rel_le_0_06_32_16": (
            r32["first_preactivation_k4_relative_rms"] <= 0.06
            and r16["first_preactivation_k4_relative_rms"] <= 0.06
        ),
        "deep_preactivation_k4_rel_le_0_35_32_16": (
            r32["deep_preactivation_k4_relative_rms"] <= 0.35
            and r16["deep_preactivation_k4_relative_rms"] <= 0.35
        ),
        "ark4_strictly_improves_final_mean_all": all(
            r["candidate_final_mean_relative_rms"]
            < r["baseline_final_mean_relative_rms"]
            for r in records
        ),
        "ark4_over_baseline_le_0_95_32": (
            r32["candidate_over_baseline"] <= 0.95
        ),
        "ark4_over_baseline_le_0_95_16": (
            r16["candidate_over_baseline"] <= 0.95
        ),
        "ark4_final_mean_rel_le_0_05_2d": (
            r2["candidate_final_mean_relative_rms"] <= 0.05
        ),
        "ark4_final_mean_rel_le_0_05_32": (
            r32["candidate_final_mean_relative_rms"] <= 0.05
        ),
        "ark4_final_mean_rel_le_0_05_16": (
            r16["candidate_final_mean_relative_rms"] <= 0.05
        ),
        "reference_stability_32_16": (
            r32["reference_stability"]["passes"]
            and r16["reference_stability"]["passes"]
        ),
        "production_cost_formula_exact_reconcile": bool(cost_match),
        "production_all_in_le_0_135B": bool(
            prod["all_in_upper"] <= CAP_FLOPS
        ),
        "strassen_disabled": bool(
            prod["strassen_levels"] == 0
            and independent["strassen_levels"] == 0
        ),
        "no_public_scorer_holdout_full_submission": True,
    }

    integrity_keys = [
        "candidate_and_reference_finite_all",
        "deterministic_replay_bitwise_exact_all",
        "candidate_source_firewall_pass",
        "reference_after_candidate_freeze_all",
        "homogeneity_relative_error_le_1e_12_all",
        "analytic_2d_input_k4_abs_le_1e_14",
        "empirical_input_k4_rel_le_0_06_32_16",
        "first_preactivation_k4_rel_le_0_06_32_16",
        "reference_stability_32_16",
        "production_cost_formula_exact_reconcile",
        "production_all_in_le_0_135B",
        "strassen_disabled",
        "no_public_scorer_holdout_full_submission",
    ]
    scientific_keys = [
        "deep_preactivation_k4_rel_le_0_35_32_16",
        "ark4_strictly_improves_final_mean_all",
        "ark4_over_baseline_le_0_95_32",
        "ark4_over_baseline_le_0_95_16",
        "ark4_final_mean_rel_le_0_05_2d",
        "ark4_final_mean_rel_le_0_05_32",
        "ark4_final_mean_rel_le_0_05_16",
    ]
    integrity_go = bool(all(gates[k] for k in integrity_keys))
    scientific_go = bool(
        integrity_go and all(gates[k] for k in scientific_keys)
    )

    result = {
        "schema": "arc.whitebox.e154.angular_radial_k4.v1",
        "experiment": "E154",
        "idempotency_key": "ARC-E154-CLEAN-ANGULAR-RADIAL-K4-20260921",
        "protocol_commit": PROTOCOL_COMMIT,
        "mechanism": {
            "name": "ARK4",
            "clean_room": True,
            "e151_code_used": False,
            "exact_radial_homogeneity": True,
            "analytic_sphere_k4": True,
            "memoryless_post_relu_k4_hypothesis": True,
            "v29_compatible_scope": (
                "full covariance plus fourth-Wick ReLU correction; "
                "no V29 fitted tables or K3 source stack"
            ),
            "strassen_levels": 0,
            "target_fit": False,
        },
        "source_audit": audit,
        "records": records,
        "production_cost": prod,
        "independent_production_cost": independent,
        "gates": gates,
        "integrity_go": integrity_go,
        "scientific_go": scientific_go,
        "decision": (
            "E154_TARGET_FREE_SCIENTIFIC_GO_ARK4"
            if scientific_go
            else "E154_TERMINAL_NO_GO_CLOSE_ARK4"
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
            "strassen": False,
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
    print("E154_ANGULAR_RADIAL_K4=" + json.dumps(result, sort_keys=True))

    if not integrity_go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
