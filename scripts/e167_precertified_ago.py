#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import math
from pathlib import Path

import numpy as np

from methods.e164_ago import (
    BUDGET_FLOPS,
    CAP_FLOPS,
    ago_estimate,
    parent_estimate,
    production_cost,
    radial_a1,
    to_angular,
    to_gaussian,
)

OUT = Path("e167-precertified-ago.json")
CANDIDATE_PATH = Path("methods/e164_ago.py")
PROTOCOL_COMMIT = "431685e6dcf80a2f1841e7f0229234bf5110eabf"
EXPECTED_CANDIDATE_SHA256 = "533149d0a1c05be12097b997b8762270b299c574cf6c32324de7d17ec285169c"

N = 1024
DEPTH = 16
WEIGHT_SEED = 1671024
REFERENCE_SAMPLES = 196_608
REFERENCE_BATCHES = 48
REFERENCE_SEED = 167196608
ABS_SE_GATE = 7.0e-4


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _mse(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.mean(d * d))


def _rel(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    return float(
        np.linalg.norm(aa - bb)
        / max(float(np.linalg.norm(bb)), 2.0**-500)
    )


def _weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    scale = math.sqrt(2.0 / N)
    return [
        rng.normal(0.0, scale, size=(N, N)).astype(np.float64)
        for _ in range(DEPTH)
    ]


def _weights_sha(weights: list[np.ndarray]) -> str:
    h = hashlib.sha256()
    for w in weights:
        h.update(np.ascontiguousarray(w).tobytes())
    return h.hexdigest()


def _freeze(est) -> dict:
    return {
        "final_mean_sha256": _sha(est.final_mean),
        "layer_mean_sha256": [_sha(s.mean) for s in est.layers],
        "layer_covariance_sha256": [_sha(s.covariance) for s in est.layers],
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
        "cost": est.cost,
    }


def _same(a, b) -> bool:
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
    return a.cost == b.cost


def _roundtrip_error(ago) -> float:
    if ago.first_angular_mean is None or ago.first_angular_covariance is None:
        return math.inf
    am, ac = to_angular(
        ago.first_gaussian_mean,
        ago.first_gaussian_covariance,
        N,
    )
    gm, gc = to_gaussian(am, ac, N)
    return float(
        max(
            _rel(am, ago.first_angular_mean),
            _rel(ac, ago.first_angular_covariance),
            _rel(gm, ago.first_gaussian_mean),
            _rel(gc, ago.first_gaussian_covariance),
        )
    )


def _source_audit() -> dict:
    src = CANDIDATE_PATH.read_text(encoding="utf-8")
    source_sha = hashlib.sha256(src.encode("utf-8")).hexdigest()
    tree = ast.parse(src)
    imports: list[str] = []
    io_calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "open", "eval", "exec"
            }:
                io_calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                name = ast.unparse(node.func).lower()
                if any(
                    term in name
                    for term in (
                        "read_text",
                        "read_bytes",
                        "urlopen",
                        "request",
                        "download",
                        "loadtxt",
                        "read_csv",
                        "read_parquet",
                    )
                ):
                    io_calls.append(name)

    forbidden_imports = [
        x for x in imports
        if any(
            term in x.lower()
            for term in (
                "whestbench",
                "dataset",
                "scorer",
                "requests",
                "urllib",
                "e167_reference",
            )
        )
    ]
    low = src.lower()
    forbidden_tokens = {
        token: token in low
        for token in (
            "k4",
            "d4",
            "d22",
            "c4",
            "strassen",
            "holdout",
            "submission",
            "public_target",
        )
    }
    parent_params = list(inspect.signature(parent_estimate).parameters)
    ago_params = list(inspect.signature(ago_estimate).parameters)

    return {
        "candidate_sha256": source_sha,
        "matches_frozen_e164_candidate": (
            source_sha == EXPECTED_CANDIDATE_SHA256
        ),
        "imports": sorted(imports),
        "forbidden_imports": forbidden_imports,
        "io_network_calls": io_calls,
        "forbidden_tokens": forbidden_tokens,
        "parent_parameters": parent_params,
        "ago_parameters": ago_params,
        "passes": bool(
            source_sha == EXPECTED_CANDIDATE_SHA256
            and not forbidden_imports
            and not io_calls
            and not any(forbidden_tokens.values())
            and parent_params == ["weights"]
            and ago_params == ["weights"]
        ),
    }


def _independent_cost() -> dict:
    n = 1024
    L = 16
    parts = {
        "covariance_linear_transport": L * 4 * n**3,
        "mean_matvec": L * 2 * n**2,
        "nonlinear_second_order_arithmetic": L * 24 * n**2,
        "normal_scalar_work": L * 1024 * n,
        "helper_reserve": 20 * (2 * n**3),
        "angular_gauge_overlay": 8 * n**2 + 64 * L * n,
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


def _emit(result: dict) -> None:
    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("E167_PRECERTIFIED_AGO=" + json.dumps(result, sort_keys=True))


def main() -> None:
    audit = _source_audit()
    weights = _weights()
    weights_hash = _weights_sha(weights)

    # Parent exists before reference and is replay-frozen before any candidate.
    parent = parent_estimate(weights)
    parent_replay = parent_estimate(weights)
    parent_replay_exact = _same(parent, parent_replay)
    parent_frozen = _freeze(parent)

    # Reference-only phase. Candidate has not been called.
    from methods.e167_reference_streaming import (
        homogeneity_error,
        streaming_sphere_reference,
    )

    ref = streaming_sphere_reference(
        weights,
        n=N,
        total_samples=REFERENCE_SAMPLES,
        batch_count=REFERENCE_BATCHES,
        seed=REFERENCE_SEED,
    )
    a1 = radial_a1(N)
    ref_mean = a1 * ref.angular_mean
    batch_means = a1 * ref.batch_angular_means

    se_vec = np.std(batch_means, axis=0, ddof=1) / math.sqrt(
        REFERENCE_BATCHES
    )
    se_ref = float(np.sqrt(np.mean(se_vec * se_vec)))

    parent_mse = _mse(parent.final_mean, ref_mean)
    parent_rmse = math.sqrt(parent_mse)

    pre_abs = bool(se_ref <= ABS_SE_GATE)
    pre_parent_rel = bool(se_ref <= 0.20 * parent_rmse)
    pre_reference_go = bool(
        audit["passes"]
        and parent.finite
        and ref.finite
        and parent_replay_exact
        and pre_abs
        and pre_parent_rel
    )

    hom = homogeneity_error(
        weights,
        n=N,
        seed=167167,
        rays=64,
    )

    prod = production_cost()
    independent = _independent_cost()
    cost_keys = (
        "covariance_linear_transport",
        "mean_matvec",
        "nonlinear_second_order_arithmetic",
        "normal_scalar_work",
        "helper_reserve",
        "angular_gauge_overlay",
        "all_in_upper",
        "budget_flops",
        "cap_flops",
        "slack_flops",
    )
    cost_match = all(prod[k] == independent[k] for k in cost_keys)

    common = {
        "schema": "arc.whitebox.e167.precertified_ago.v1",
        "experiment": "E167",
        "idempotency_key": "ARC-E167-PRECERTIFIED-REFERENCE-AGO-20260921",
        "protocol_commit": PROTOCOL_COMMIT,
        "fixture": {
            "width": N,
            "depth": DEPTH,
            "zero_bias": True,
            "weight_seed": WEIGHT_SEED,
            "weights_sha256": weights_hash,
        },
        "reference_design": {
            "samples": REFERENCE_SAMPLES,
            "seed": REFERENCE_SEED,
            "batches": REFERENCE_BATCHES,
            "batch_size": REFERENCE_SAMPLES // REFERENCE_BATCHES,
            "streaming": True,
            "reference_dense_eval_upper_flops": 6_597_069_766_656,
            "candidate_executed_only_after_pre_reference_go": True,
        },
        "source_audit": audit,
        "parent_freeze": parent_frozen,
        "pre_candidate_reference": {
            "reference_mean_sha256": _sha(ref_mean),
            "reference_se_rms": se_ref,
            "absolute_se_limit": ABS_SE_GATE,
            "absolute_se_gate": pre_abs,
            "parent_mse": parent_mse,
            "parent_rmse": parent_rmse,
            "parent_relative_se_limit": 0.20 * parent_rmse,
            "parent_relative_se_gate": pre_parent_rel,
            "parent_replay_bitwise_exact": parent_replay_exact,
            "reference_finite": ref.finite,
            "pre_reference_go": pre_reference_go,
        },
        "production_cost": prod,
        "independent_production_cost": independent,
        "pre_candidate_checks": {
            "source_firewall": bool(audit["passes"]),
            "parent_finite": bool(parent.finite),
            "parent_replay_bitwise_exact": bool(parent_replay_exact),
            "reference_finite": bool(ref.finite),
            "reference_absolute_se_gate": pre_abs,
            "reference_parent_relative_se_gate": pre_parent_rel,
            "homogeneity_le_2e_12": bool(hom <= 2e-12),
            "cost_formula_exact_reconcile": bool(cost_match),
            "complete_candidate_cost_le_0_135B": bool(
                prod["all_in_upper"] <= CAP_FLOPS
            ),
        },
        "scope": {
            "synthetic_only": True,
            "target_free": True,
            "production_shaped": True,
            "standalone_execution": True,
            "public": False,
            "public_mini": False,
            "benchmark_target": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "submission": False,
            "rerun": False,
            "rescue": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
            "public_blocked_pending_independent_e167_verifier_go": True,
        },
    }

    if not pre_reference_go:
        result = {
            **common,
            "candidate_executed": False,
            "metrics": None,
            "gates": {
                **common["pre_candidate_checks"],
                "pre_candidate_reference_certified": False,
                "aggregate_mse_ratio_le_0_98": "NOT_EVALUATED",
                "post_candidate_reference_gate": "NOT_EVALUATED",
                "batch_improvement_36_of_48": "NOT_EVALUATED",
                "batch_delta_mean_gt_3se": "NOT_EVALUATED",
                "ago_replay_bitwise_exact": "NOT_EVALUATED",
                "gauge_roundtrip_le_2e_12": "NOT_EVALUATED",
            },
            "scientific_go": False,
            "decision": "E167_TERMINAL_NO_GO_REFERENCE_PRECERTIFICATION",
        }
        _emit(result)
        return

    # Only now is AGO evaluated.
    ago = ago_estimate(weights)
    ago_replay = ago_estimate(weights)
    ago_replay_exact = _same(ago, ago_replay)
    ago_frozen = _freeze(ago)
    roundtrip = _roundtrip_error(ago)

    ago_mse = _mse(ago.final_mean, ref_mean)
    ago_rmse = math.sqrt(ago_mse)
    ratio = math.inf if parent_mse <= 0.0 else ago_mse / parent_mse

    batch_parent_mse = np.array(
        [_mse(parent.final_mean, b) for b in batch_means],
        dtype=np.float64,
    )
    batch_ago_mse = np.array(
        [_mse(ago.final_mean, b) for b in batch_means],
        dtype=np.float64,
    )
    delta = batch_parent_mse - batch_ago_mse
    improve_count = int(np.sum(delta > 0.0))
    delta_mean = float(np.mean(delta))
    delta_se = float(
        np.std(delta, ddof=1) / math.sqrt(REFERENCE_BATCHES)
    )

    post_ref_gate = bool(
        se_ref <= 0.20 * min(parent_rmse, ago_rmse)
    )

    gates = {
        **common["pre_candidate_checks"],
        "pre_candidate_reference_certified": True,
        "ago_finite": bool(ago.finite),
        "ago_replay_bitwise_exact": bool(ago_replay_exact),
        "gauge_roundtrip_le_2e_12": bool(roundtrip <= 2e-12),
        "aggregate_mse_ratio_le_0_98": bool(
            math.isfinite(ratio) and ratio <= 0.98
        ),
        "post_candidate_reference_gate": post_ref_gate,
        "batch_improvement_36_of_48": bool(improve_count >= 36),
        "batch_delta_mean_gt_3se": bool(
            delta_mean > 3.0 * delta_se
        ),
        "no_public_benchmark_scorer_holdout_full_submission": True,
        "no_sweep_rescue_rerun": True,
    }
    scientific_go = bool(all(v is True for v in gates.values()))

    result = {
        **common,
        "candidate_executed": True,
        "ago_freeze": ago_frozen,
        "metrics": {
            "parent_mse": parent_mse,
            "ago_mse": ago_mse,
            "ago_over_parent": ratio,
            "mse_improvement_fraction": (
                1.0 - ratio if math.isfinite(ratio) else -math.inf
            ),
            "parent_rmse": parent_rmse,
            "ago_rmse": ago_rmse,
            "parent_relative_rms": _rel(parent.final_mean, ref_mean),
            "ago_relative_rms": _rel(ago.final_mean, ref_mean),
            "reference_se_rms": se_ref,
            "batch_improvement_count": improve_count,
            "batch_count": REFERENCE_BATCHES,
            "batch_delta_mean": delta_mean,
            "batch_delta_se": delta_se,
            "batch_delta_mean_over_se": (
                math.inf if delta_se == 0.0 else delta_mean / delta_se
            ),
            "gauge_roundtrip_error": roundtrip,
            "homogeneity_error": hom,
            "batch_parent_mse": batch_parent_mse.tolist(),
            "batch_ago_mse": batch_ago_mse.tolist(),
        },
        "gates": gates,
        "scientific_go": scientific_go,
        "decision": (
            "E167_SYNTHETIC_PRODUCTION_SHAPED_OWNER_GO_AGO_PRECERTIFIED"
            if scientific_go
            else "E167_TERMINAL_NO_GO"
        ),
    }
    _emit(result)


if __name__ == "__main__":
    main()
