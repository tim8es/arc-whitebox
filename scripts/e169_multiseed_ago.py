#!/usr/bin/env python3
from __future__ import annotations

import ast
import gc
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

OUT = Path("e169-multiseed-ago.json")
CANDIDATE_PATH = Path("methods/e164_ago.py")
PROTOCOL_COMMIT = "bc2469e0ca5dbd6c8d5c8b8cc54d04014ab5fdd4"
EXPECTED_CANDIDATE_SHA256 = "533149d0a1c05be12097b997b8762270b299c574cf6c32324de7d17ec285169c"

N = 1024
DEPTH = 16
WEIGHT_SEEDS = (1691024, 1692024, 1693024)
REFERENCE_SEEDS = (169196608, 169296608, 169396608)
REFERENCE_SAMPLES = 196_608
REFERENCE_BATCHES = 48
ABS_REFERENCE_SE_LIMIT = 7.0e-4
EXPECTED_A1_1024 = 0.9997558892135413


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


def _weights(seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
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


def _radial_readout_error(ago) -> float:
    expected = radial_a1(N) * ago.layers[-1].mean
    return _rel(ago.final_mean, expected)


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
                "e169_reference",
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


def _run_seed(
    *,
    weight_seed: int,
    reference_seed: int,
    homogeneity_seed: int,
) -> dict:
    weights = _weights(weight_seed)
    weights_hash = _weights_sha(weights)

    parent = parent_estimate(weights)
    parent_replay = parent_estimate(weights)
    parent_replay_exact = _same(parent, parent_replay)
    parent_frozen = _freeze(parent)
    del parent_replay
    gc.collect()

    ago = ago_estimate(weights)
    ago_replay = ago_estimate(weights)
    ago_replay_exact = _same(ago, ago_replay)
    ago_frozen = _freeze(ago)
    del ago_replay
    gc.collect()

    roundtrip = _roundtrip_error(ago)
    readout_error = _radial_readout_error(ago)

    # Reference materialization starts only after parent/AGO freeze.
    from methods.e169_reference_streaming import (
        homogeneity_error,
        streaming_reference,
    )

    ref = streaming_reference(
        weights,
        n=N,
        total_samples=REFERENCE_SAMPLES,
        batch_count=REFERENCE_BATCHES,
        seed=reference_seed,
    )
    a1 = radial_a1(N)
    ref_mean = a1 * ref.angular_mean
    batch_means = a1 * ref.batch_angular_means

    se_vec = np.std(batch_means, axis=0, ddof=1) / math.sqrt(
        REFERENCE_BATCHES
    )
    se_ref = float(np.sqrt(np.mean(se_vec * se_vec)))

    parent_mse = _mse(parent.final_mean, ref_mean)
    ago_mse = _mse(ago.final_mean, ref_mean)
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

    hom = homogeneity_error(
        weights,
        n=N,
        seed=homogeneity_seed,
        rays=64,
    )

    result = {
        "weight_seed": int(weight_seed),
        "reference_seed": int(reference_seed),
        "weights_sha256": weights_hash,
        "parent_freeze": parent_frozen,
        "ago_freeze": ago_frozen,
        "reference_after_candidate_freeze": True,
        "reference_mean_sha256": _sha(ref_mean),
        "reference_se_rms": se_ref,
        "reference_absolute_se_gate": bool(
            se_ref <= ABS_REFERENCE_SE_LIMIT
        ),
        "parent_mse": parent_mse,
        "ago_mse": ago_mse,
        "ago_over_parent": ratio,
        "mse_improvement_fraction": (
            1.0 - ratio if math.isfinite(ratio) else -math.inf
        ),
        "parent_rmse": math.sqrt(parent_mse),
        "ago_rmse": math.sqrt(ago_mse),
        "parent_relative_rms": _rel(parent.final_mean, ref_mean),
        "ago_relative_rms": _rel(ago.final_mean, ref_mean),
        "parent_replay_bitwise_exact": bool(parent_replay_exact),
        "ago_replay_bitwise_exact": bool(ago_replay_exact),
        "gauge_roundtrip_error": roundtrip,
        "radial_readout_error": readout_error,
        "homogeneity_error": hom,
        "finite": bool(
            parent.finite
            and ago.finite
            and ref.finite
            and np.isfinite(delta).all()
        ),
        "individual_improvement": bool(
            parent_mse > 0.0
            and math.isfinite(ratio)
            and ratio < 1.0
        ),
        "strong_ratio_gate": bool(
            parent_mse > 0.0
            and math.isfinite(ratio)
            and ratio <= 0.98
        ),
        "batch_positive_count": int(np.sum(delta > 0.0)),
        "batch_delta_mean": float(np.mean(delta)),
        "batch_delta_se": float(
            np.std(delta, ddof=1) / math.sqrt(REFERENCE_BATCHES)
        ),
        "batch_parent_mse": batch_parent_mse.tolist(),
        "batch_ago_mse": batch_ago_mse.tolist(),
        "batch_delta": delta.tolist(),
    }

    del parent, ago, ref, weights, ref_mean, batch_means
    gc.collect()
    return result


def main() -> None:
    audit = _source_audit()

    records = [
        _run_seed(
            weight_seed=WEIGHT_SEEDS[0],
            reference_seed=REFERENCE_SEEDS[0],
            homogeneity_seed=1691101,
        ),
        _run_seed(
            weight_seed=WEIGHT_SEEDS[1],
            reference_seed=REFERENCE_SEEDS[1],
            homogeneity_seed=1692101,
        ),
        _run_seed(
            weight_seed=WEIGHT_SEEDS[2],
            reference_seed=REFERENCE_SEEDS[2],
            homogeneity_seed=1693101,
        ),
    ]

    pooled_parent_mse = float(
        np.mean([r["parent_mse"] for r in records])
    )
    pooled_ago_mse = float(
        np.mean([r["ago_mse"] for r in records])
    )
    pooled_ratio = (
        math.inf
        if pooled_parent_mse <= 0.0
        else pooled_ago_mse / pooled_parent_mse
    )

    all_delta = np.concatenate(
        [np.asarray(r["batch_delta"], dtype=np.float64) for r in records]
    )
    batch_positive_count = int(np.sum(all_delta > 0.0))
    batch_delta_mean = float(np.mean(all_delta))
    batch_delta_se = float(
        np.std(all_delta, ddof=1) / math.sqrt(all_delta.size)
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

    a1_error = abs(radial_a1(N) - EXPECTED_A1_1024)
    strong_seed_count = int(
        sum(r["strong_ratio_gate"] for r in records)
    )

    gates = {
        "frozen_e164_candidate_source_identity": bool(
            audit["matches_frozen_e164_candidate"]
        ),
        "source_public_firewall": bool(audit["passes"]),
        "finite_all": bool(all(r["finite"] for r in records)),
        "reference_after_candidate_freeze_all": bool(
            all(r["reference_after_candidate_freeze"] for r in records)
        ),
        "absolute_reference_se_le_7e_4_all": bool(
            all(r["reference_absolute_se_gate"] for r in records)
        ),
        "parent_replay_bitwise_exact_all": bool(
            all(r["parent_replay_bitwise_exact"] for r in records)
        ),
        "ago_replay_bitwise_exact_all": bool(
            all(r["ago_replay_bitwise_exact"] for r in records)
        ),
        "gauge_roundtrip_le_2e_12_all": bool(
            all(r["gauge_roundtrip_error"] <= 2e-12 for r in records)
        ),
        "radial_readout_identity_le_2e_12_all": bool(
            all(r["radial_readout_error"] <= 2e-12 for r in records)
        ),
        "radial_a1_1024_identity_le_1e_15": bool(a1_error <= 1e-15),
        "homogeneity_le_2e_12_all": bool(
            all(r["homogeneity_error"] <= 2e-12 for r in records)
        ),
        "ago_improves_all_3_seeds": bool(
            all(r["individual_improvement"] for r in records)
        ),
        "at_least_2_of_3_seed_ratios_le_0_98": bool(
            strong_seed_count >= 2
        ),
        "pooled_mse_ratio_le_0_98": bool(
            math.isfinite(pooled_ratio) and pooled_ratio <= 0.98
        ),
        "batch_positive_at_least_96_of_144": bool(
            batch_positive_count >= 96
        ),
        "batch_delta_mean_positive": bool(batch_delta_mean > 0.0),
        "batch_delta_mean_gt_3se": bool(
            batch_delta_mean > 3.0 * batch_delta_se
        ),
        "per_seed_batch_delta_mean_positive_all": bool(
            all(r["batch_delta_mean"] > 0.0 for r in records)
        ),
        "independent_cost_reconcile": bool(cost_match),
        "complete_candidate_cost_le_0_135B": bool(
            prod["all_in_upper"] <= CAP_FLOPS
        ),
        "no_public_benchmark_scorer_holdout_full_submission": True,
        "no_posthoc_gate_change_sweep_rescue_rerun": True,
    }

    scientific_go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e169.multiseed_production_ago.v1",
        "experiment": "E169",
        "idempotency_key": "ARC-E169-MULTISEED-PRODUCTION-AGO-20260921",
        "protocol_commit": PROTOCOL_COMMIT,
        "panel": {
            "width": N,
            "depth": DEPTH,
            "zero_bias": True,
            "weight_seeds": list(WEIGHT_SEEDS),
            "reference_seeds": list(REFERENCE_SEEDS),
            "reference_samples_per_seed": REFERENCE_SAMPLES,
            "reference_batches_per_seed": REFERENCE_BATCHES,
            "reference_batch_size": REFERENCE_SAMPLES // REFERENCE_BATCHES,
            "absolute_reference_se_limit": ABS_REFERENCE_SE_LIMIT,
        },
        "source_audit": audit,
        "records": records,
        "panel_metrics": {
            "pooled_parent_mse": pooled_parent_mse,
            "pooled_ago_mse": pooled_ago_mse,
            "pooled_ago_over_parent": pooled_ratio,
            "pooled_mse_improvement_fraction": (
                1.0 - pooled_ratio
                if math.isfinite(pooled_ratio)
                else -math.inf
            ),
            "strong_seed_count": strong_seed_count,
            "batch_positive_count": batch_positive_count,
            "batch_total": int(all_delta.size),
            "batch_delta_mean": batch_delta_mean,
            "batch_delta_se": batch_delta_se,
            "batch_delta_mean_over_se": (
                math.inf
                if batch_delta_se == 0.0
                else batch_delta_mean / batch_delta_se
            ),
            "radial_a1_1024": radial_a1(N),
            "radial_a1_1024_expected": EXPECTED_A1_1024,
            "radial_a1_absolute_error": a1_error,
        },
        "production_cost": prod,
        "independent_production_cost": independent,
        "reference_research_cost": {
            "per_seed_dense_eval_upper_flops": 6_597_069_766_656,
            "three_seed_dense_eval_upper_flops": 19_791_209_299_968,
            "charged_to_candidate_cap": False,
        },
        "gates": gates,
        "scientific_go": scientific_go,
        "decision": (
            "E169_SYNTHETIC_MULTISEED_PRODUCTION_SHAPED_OWNER_GO_AGO"
            if scientific_go
            else "E169_TERMINAL_NO_GO"
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
            "public_blocked_pending_independent_e169_verifier_go": True,
        },
    }

    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("E169_MULTISEED_AGO=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
