from __future__ import annotations

import hashlib
import inspect
import json
import math
from pathlib import Path

import numpy as np

from methods.e110_householder_exact_verifier import (
    billed_householder_estimator,
    billed_independent_baseline,
    deep_sensitivity,
    exact_householder_stats,
    householder,
)

WIDTH = 2
DEPTH = 4
WEIGHT_SEED = 110104
CANDIDATE_HAAR_SEED = 110105
BASELINE_SECOND_HAAR_SEED = 110106
OUT = Path("e110-householder-smallwidth-verifier.json")


def make_weights() -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(WEIGHT_SEED))
    scale = math.sqrt(2.0 / WIDTH)
    return [
        rng.standard_normal((WIDTH, WIDTH)).astype(np.float64) * scale
        for _ in range(DEPTH)
    ]


def digest_arrays(arrays: list[np.ndarray]) -> str:
    h = hashlib.sha256()
    for array in arrays:
        h.update(np.ascontiguousarray(array).tobytes())
    return h.hexdigest()


def compact_billed(record: dict) -> dict:
    return {
        "prediction_sha256": record["prediction_sha256"],
        "prediction": np.asarray(record["prediction"], dtype=np.float64).tolist(),
        "antithetic_pair_max_abs": record["antithetic_pair_max_abs"],
        "finite": record["finite"],
        "flops": record["flops"],
    }


def no_external_access_static_check() -> bool:
    funcs = (exact_householder_stats, billed_householder_estimator, billed_independent_baseline)
    source = "\n".join(inspect.getsource(fn) for fn in funcs).lower()
    forbidden = (
        "aicrowd",
        "load_dataset",
        "final_means",
        "official_scorer",
        "requests.get",
        "huggingface",
    )
    return all(token not in source for token in forbidden)


def main() -> None:
    weights = make_weights()
    weight_sha256 = digest_arrays(weights)

    exact_a = exact_householder_stats(weights)
    exact_b = exact_householder_stats(weights)
    exact_replay_equal = (
        json.dumps(exact_a, sort_keys=True, separators=(",", ":"))
        == json.dumps(exact_b, sort_keys=True, separators=(",", ":"))
    )

    candidate_a = billed_householder_estimator(weights, CANDIDATE_HAAR_SEED)
    candidate_b = billed_householder_estimator(weights, CANDIDATE_HAAR_SEED)
    baseline_a = billed_independent_baseline(
        weights, CANDIDATE_HAAR_SEED, BASELINE_SECOND_HAAR_SEED
    )
    baseline_b = billed_independent_baseline(
        weights, CANDIDATE_HAAR_SEED, BASELINE_SECOND_HAAR_SEED
    )

    candidate_bitwise = bool(
        np.array_equal(candidate_a["prediction"], candidate_b["prediction"])
    )
    baseline_bitwise = bool(
        np.array_equal(baseline_a["prediction"], baseline_b["prediction"])
    )
    candidate_flops_replay = candidate_a["flops"] == candidate_b["flops"]
    baseline_flops_replay = baseline_a["flops"] == baseline_b["flops"]

    nondegenerate = [row for row in exact_a["outputs"] if row["nondegenerate"]]
    per_output_nonincrease = all(
        row["variance_ratio"] is not None and row["variance_ratio"] <= 1.0
        for row in nondegenerate
    )

    sensitivity = deep_sensitivity(weights)
    reflection = householder(sensitivity)
    orthogonality = float(
        np.max(np.abs(reflection.T @ reflection - np.eye(WIDTH)))
    )

    no_external = no_external_access_static_check()

    gates = {
        "width_le_8": WIDTH <= 8,
        "depth_le_4": DEPTH <= 4,
        "sector_validation_le_1e_11": exact_a["sector_validation_max_abs"] <= 1e-11,
        "block_validation_le_1e_11": exact_a["block_validation_max_abs"] <= 1e-11,
        "householder_orthogonality_le_1e_12": orthogonality <= 1e-12,
        "reflected_validation_le_1e_11": exact_a["reflected_validation_max_abs"] <= 1e-11,
        "nondegenerate_output_exists": exact_a["nondegenerate_outputs"] >= 1,
        "candidate_exact_mean_bias_le_1e_12": exact_a["max_candidate_mean_abs_error"] <= 1e-12,
        "reflected_marginal_mean_bias_le_1e_12": exact_a["max_reflected_marginal_mean_abs_error"] <= 1e-12,
        "pooled_variance_ratio_le_0_80": exact_a["pooled_variance_ratio"] <= 0.80,
        "candidate_nonincrease_each_nondegenerate_output": per_output_nonincrease,
        "exact_replay_equal": exact_replay_equal,
        "candidate_billed_bitwise_replay": candidate_bitwise,
        "baseline_billed_bitwise_replay": baseline_bitwise,
        "candidate_flops_replay": candidate_flops_replay,
        "baseline_flops_replay": baseline_flops_replay,
        "candidate_antithetic_exact": candidate_a["antithetic_pair_max_abs"] == 0.0,
        "baseline_antithetic_exact": baseline_a["antithetic_pair_max_abs"] == 0.0,
        "candidate_flops_exact_reconciliation": candidate_a["flops"]["exact_reconciliation"],
        "baseline_flops_exact_reconciliation": baseline_a["flops"]["exact_reconciliation"],
        "finite_all": candidate_a["finite"] and candidate_b["finite"] and baseline_a["finite"] and baseline_b["finite"],
        "no_external_target_access": no_external,
    }
    passed = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e110.householder_smallwidth_independent_verifier.v1",
        "experiment": "E110",
        "tracking_id": "ARC-E110-HOUSEHOLDER-SMALLWIDTH-VERIFIER-20260919",
        "candidate_protocol_tracking_id": "ARC-E110-DEEP-HOUSEHOLDER-ORBIT-20260919",
        "candidate_protocol_tip": "ca6d9430644e745d174c46cbc27334332671d1f0",
        "width": WIDTH,
        "depth": DEPTH,
        "weight_seed": WEIGHT_SEED,
        "candidate_haar_seed": CANDIDATE_HAAR_SEED,
        "baseline_second_haar_seed": BASELINE_SECOND_HAAR_SEED,
        "weight_sha256": weight_sha256,
        "exact_reference": exact_a,
        "exact_replay_equal": exact_replay_equal,
        "candidate_billed": compact_billed(candidate_a),
        "candidate_billed_repeat": compact_billed(candidate_b),
        "baseline_billed": compact_billed(baseline_a),
        "baseline_billed_repeat": compact_billed(baseline_b),
        "determinism": {
            "candidate_prediction_bitwise": candidate_bitwise,
            "baseline_prediction_bitwise": baseline_bitwise,
            "candidate_prediction_sha_equal": candidate_a["prediction_sha256"] == candidate_b["prediction_sha256"],
            "baseline_prediction_sha_equal": baseline_a["prediction_sha256"] == baseline_b["prediction_sha256"],
            "candidate_flops_equal": candidate_flops_replay,
            "baseline_flops_equal": baseline_flops_replay,
        },
        "full_flops": {
            "candidate_all_in_smallwidth": candidate_a["flops"]["total"],
            "candidate_reconciled": candidate_a["flops"]["reconciled_sum"],
            "baseline_all_in_smallwidth": baseline_a["flops"]["total"],
            "baseline_reconciled": baseline_a["flops"]["reconciled_sum"],
            "reference_integration": "VERIFIER_ONLY_NOT_COMPETITION_ESTIMATOR_COMPUTE",
        },
        "gates": gates,
        "decision": (
            "SMALLWIDTH_BREAKTHROUGH_CONFIRMED"
            if passed
            else "NO_GO_BREAKTHROUGH_NOT_CONFIRMED"
        ),
        "scientific_go": passed,
        "failures": 0,
        "scope": {
            "synthetic_small_exact_only": True,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
            "target_fitting": False,
            "tuning": False,
            "sweep": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
            "owner_candidate_branch_mutated": False,
        },
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "E110_HOUSEHOLDER_SMALLWIDTH_VERIFIER="
        + json.dumps(result, sort_keys=True),
        flush=True,
    )


if __name__ == "__main__":
    main()
