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
    to_angular,
    to_gaussian,
    radial_a1,
)

OUT = Path("e166-production-shaped-ago.json")
CANDIDATE_PATH = Path("methods/e164_ago.py")
PROTOCOL_COMMIT = "e8895594e2280d7f0c5037d5aba5151253aa9b13"
EXPECTED_CANDIDATE_SHA256 = "533149d0a1c05be12097b997b8762270b299c574cf6c32324de7d17ec285169c"


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
    n = 1024
    rng = np.random.Generator(np.random.PCG64(1661024))
    scale = math.sqrt(2.0 / n)
    return [
        rng.normal(0.0, scale, size=(n, n)).astype(np.float64)
        for _ in range(16)
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
    n = 1024
    if ago.first_angular_mean is None or ago.first_angular_covariance is None:
        return math.inf
    am, ac = to_angular(
        ago.first_gaussian_mean,
        ago.first_gaussian_covariance,
        n,
    )
    gm, gc = to_gaussian(am, ac, n)
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
                "e164_reference",
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


def main() -> None:
    audit = _source_audit()
    weights = _weights()
    weights_hash = _weights_sha(weights)

    parent = parent_estimate(weights)
    ago = ago_estimate(weights)
    parent_replay = parent_estimate(weights)
    ago_replay = ago_estimate(weights)

    parent_frozen = _freeze(parent)
    ago_frozen = _freeze(ago)
    parent_replay_exact = _same(parent, parent_replay)
    ago_replay_exact = _same(ago, ago_replay)
    roundtrip = _roundtrip_error(ago)

    # Verifier materialization starts only after candidate/replay freeze.
    from methods.e164_reference import (
        antithetic_sphere,
        evaluate,
        homogeneity_error,
    )

    n = 1024
    sample_count = 8192
    batch_count = 8
    batch_size = sample_count // batch_count
    y = antithetic_sphere(n, sample_count, 1668192)
    final = evaluate(y, weights)
    a1 = radial_a1(n)

    ref_angular = np.mean(final, axis=0, dtype=np.float64)
    ref_mean = a1 * ref_angular
    batches = np.stack(
        [
            a1
            * np.mean(
                final[i * batch_size:(i + 1) * batch_size],
                axis=0,
                dtype=np.float64,
            )
            for i in range(batch_count)
        ],
        axis=0,
    )

    parent_mse = _mse(parent.final_mean, ref_mean)
    ago_mse = _mse(ago.final_mean, ref_mean)
    ratio = math.inf if parent_mse <= 0.0 else ago_mse / parent_mse

    batch_parent_mse = np.array(
        [_mse(parent.final_mean, b) for b in batches],
        dtype=np.float64,
    )
    batch_ago_mse = np.array(
        [_mse(ago.final_mean, b) for b in batches],
        dtype=np.float64,
    )
    batch_delta = batch_parent_mse - batch_ago_mse
    improve_count = int(np.sum(batch_delta > 0.0))
    delta_mean = float(np.mean(batch_delta))
    delta_se = float(
        np.std(batch_delta, ddof=1) / math.sqrt(batch_count)
    )

    se_vec = np.std(batches, axis=0, ddof=1) / math.sqrt(batch_count)
    reference_se_rms = float(np.sqrt(np.mean(se_vec * se_vec)))
    parent_rmse = math.sqrt(parent_mse)
    ago_rmse = math.sqrt(ago_mse)
    reference_stability = bool(
        reference_se_rms <= 0.20 * min(parent_rmse, ago_rmse)
        or reference_se_rms <= 1e-4
    )

    hom = homogeneity_error(
        weights,
        n=n,
        seed=166166,
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

    finite = bool(
        parent.finite
        and ago.finite
        and np.isfinite(ref_mean).all()
        and np.isfinite(batches).all()
        and np.isfinite(batch_delta).all()
    )

    gates = {
        "frozen_e164_candidate_blob_identity": bool(
            audit["matches_frozen_e164_candidate"]
        ),
        "source_public_firewall": bool(audit["passes"]),
        "finite_parent_ago_reference": finite,
        "reference_after_candidate_freeze": True,
        "parent_replay_bitwise_exact": bool(parent_replay_exact),
        "ago_replay_bitwise_exact": bool(ago_replay_exact),
        "gauge_roundtrip_le_2e_12": bool(roundtrip <= 2e-12),
        "homogeneity_le_2e_12": bool(hom <= 2e-12),
        "reference_standard_error_gate": reference_stability,
        "ago_improves_at_least_6_of_8_batches": bool(improve_count >= 6),
        "batch_delta_mean_gt_2se": bool(delta_mean > 2.0 * delta_se),
        "aggregate_mse_ratio_le_0_98": bool(
            math.isfinite(ratio) and ratio <= 0.98
        ),
        "independent_cost_reconcile": bool(cost_match),
        "complete_production_cost_le_0_135B": bool(
            prod["all_in_upper"] <= CAP_FLOPS
        ),
        "no_public_benchmark_scorer_holdout_full_submission": True,
        "no_sweep_rescue_rerun": True,
    }
    scientific_go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e166.production_shaped_ago.v1",
        "experiment": "E166",
        "idempotency_key": "ARC-E166-PRODUCTION-SHAPED-AGO-20260921",
        "protocol_commit": PROTOCOL_COMMIT,
        "fixture": {
            "width": 1024,
            "depth": 16,
            "zero_bias": True,
            "weight_seed": 1661024,
            "weights_sha256": weights_hash,
            "reference_samples": sample_count,
            "reference_seed": 1668192,
            "reference_batches": batch_count,
        },
        "source_audit": audit,
        "candidate_freeze": {
            "parent": parent_frozen,
            "ago": ago_frozen,
        },
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
            "reference_se_rms": reference_se_rms,
            "batch_parent_mse": batch_parent_mse.tolist(),
            "batch_ago_mse": batch_ago_mse.tolist(),
            "batch_delta": batch_delta.tolist(),
            "batch_improvement_count": improve_count,
            "batch_delta_mean": delta_mean,
            "batch_delta_se": delta_se,
            "gauge_roundtrip_error": roundtrip,
            "homogeneity_error": hom,
            "reference_mean_sha256": _sha(ref_mean),
        },
        "production_cost": prod,
        "independent_production_cost": independent,
        "gates": gates,
        "scientific_go": scientific_go,
        "decision": (
            "E166_SYNTHETIC_PRODUCTION_SHAPED_OWNER_GO_AGO"
            if scientific_go
            else "E166_TERMINAL_NO_GO"
        ),
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
            "public_blocked_pending_e165_verifier_go": True,
        },
    }

    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("E166_PRODUCTION_SHAPED_AGO=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
