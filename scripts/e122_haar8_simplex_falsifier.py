#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from methods.e114_exact_angular_reference import build_exact_reference, he_weights
from methods.e122_haar8_simplex_source import (
    CODEWORDS,
    PRODUCTION_CAP_FLOPS,
    PRODUCTION_DIRECTIONS,
    PRODUCTION_FRAMES,
    SOURCE_DIM,
    haar8_antipodal_simplex_mean,
    iid_spherical_mean,
    production_cost_receipt,
    regular_simplex_code,
    simplex_algebra_metrics,
)

RAW_MSE_SCALE = 1.89e-8
FRAMES = PRODUCTION_FRAMES
SAMPLES = PRODUCTION_DIRECTIONS
E121_8D_RATIO_DIAGNOSTIC = 11.435172907952149

BLOCK8_SEEDS = (121300, 121301, 121302, 121303)
CANDIDATE8_SEEDS = (122400, 122401, 122402, 122403)
IID8_SEEDS = (122500, 122501, 122502, 122503)

BLOCK16_SEEDS = (
    122300,
    122301,
    122302,
    122303,
    122304,
    122305,
    122306,
    122307,
)
CANDIDATE16_SEEDS = (122600, 122601, 122602, 122603)
IID16_SEEDS = (122700, 122701, 122702, 122703)

OUT = Path("e122-haar8-simplex-falsifier.json")


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _mse(a: np.ndarray, b: np.ndarray) -> float:
    delta = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.mean(delta * delta))


def _block_diag(blocks: list[np.ndarray]) -> np.ndarray:
    if not blocks:
        raise ValueError("blocks required")
    widths = [int(np.asarray(b).shape[0]) for b in blocks]
    if any(np.asarray(b).shape != (w, w) for b, w in zip(blocks, widths)):
        raise ValueError("square blocks required")
    total = sum(widths)
    out = np.zeros((total, total), dtype=np.float64)
    cursor = 0
    for raw, w in zip(blocks, widths):
        out[cursor : cursor + w, cursor : cursor + w] = np.asarray(
            raw, dtype=np.float64
        )
        cursor += w
    return out


def _build_block_network(
    seeds: tuple[int, ...],
) -> tuple[list[np.ndarray], list[list[np.ndarray]]]:
    subnetworks = [he_weights(seed, width=2, depth=4) for seed in seeds]
    full = [
        _block_diag([sub[layer] for sub in subnetworks])
        for layer in range(4)
    ]
    return full, subnetworks


def _candidate_source_audit() -> dict:
    path = Path("methods/e122_haar8_simplex_source.py")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")

    forbidden_fragments = (
        "e114_exact_angular_reference",
        "e119_generic_boundary_flux",
        "e121_haar_plane_orbit",
        "whestbench",
        "datasets",
    )
    forbidden_imports = [
        item
        for item in imports
        if any(fragment in item for fragment in forbidden_fragments)
    ]

    return {
        "candidate_path": str(path),
        "candidate_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "imports": sorted(imports),
        "forbidden_imports": forbidden_imports,
        "passes": not forbidden_imports,
    }


def _independent_production_cost() -> dict:
    d = 1024
    n = 1024
    depth = 16
    k = 8
    codewords = 18
    frames = 224
    directions = frames * codewords

    simplex_setup = 8 * k * (k + 1) + 256
    frame_setup = frames * (d * (2 * k * k + 17 * k) + 64 * k)
    source_materialization = frames * (2 * d * k * codewords)
    deep = directions * depth * (2 * n * n + 2 * n)
    final = directions * n + 2 * directions + 5 * n
    total = simplex_setup + frame_setup + source_materialization + deep + final

    return {
        "simplex_setup_upper": int(simplex_setup),
        "haar_frame_rng_mgs_upper": int(frame_setup),
        "source_code_materialization_upper": int(source_materialization),
        "deep_propagation_upper": int(deep),
        "final_reduction_radial_upper": int(final),
        "all_in_upper": int(total),
        "hard_cap_flops": PRODUCTION_CAP_FLOPS,
        "slack_flops": int(PRODUCTION_CAP_FLOPS - total),
        "passes_cap": bool(total <= PRODUCTION_CAP_FLOPS),
    }


def _run_stress(
    *,
    name: str,
    block_seeds: tuple[int, ...],
    candidate_seeds: tuple[int, ...],
    iid_seeds: tuple[int, ...],
) -> tuple[dict, bool, bool, float, float]:
    weights, subnetworks = _build_block_network(block_seeds)

    records = []
    candidate_means: list[np.ndarray] = []
    iid_means: list[np.ndarray] = []
    deterministic_all = True
    ledger_all = True
    orth_max = 0.0
    norm_max = 0.0

    # Candidate and iid comparator execute without exact-reference objects.
    for candidate_seed, iid_seed in zip(candidate_seeds, iid_seeds):
        candidate = haar8_antipodal_simplex_mean(
            weights,
            frames=FRAMES,
            seed=candidate_seed,
        )
        replay = haar8_antipodal_simplex_mean(
            weights,
            frames=FRAMES,
            seed=candidate_seed,
        )
        iid = iid_spherical_mean(
            weights,
            samples=SAMPLES,
            seed=iid_seed,
        )

        replay_exact = bool(
            np.array_equal(candidate.mean, replay.mean)
            and candidate.frame_orthogonality_max_abs
            == replay.frame_orthogonality_max_abs
            and candidate.source_direction_norm_max_abs
            == replay.source_direction_norm_max_abs
        )
        ledger_exact = candidate.ledger == replay.ledger
        deterministic_all = deterministic_all and replay_exact
        ledger_all = ledger_all and ledger_exact
        orth_max = max(orth_max, candidate.frame_orthogonality_max_abs)
        norm_max = max(norm_max, candidate.source_direction_norm_max_abs)

        candidate_means.append(candidate.mean)
        iid_means.append(iid)
        records.append(
            {
                "candidate_seed": candidate_seed,
                "iid_seed": iid_seed,
                "candidate_mean_sha256": _sha(candidate.mean),
                "iid_mean_sha256": _sha(iid),
                "candidate_finite": candidate.finite,
                "frame_orthogonality_max_abs": (
                    candidate.frame_orthogonality_max_abs
                ),
                "source_direction_norm_max_abs": (
                    candidate.source_direction_norm_max_abs
                ),
                "deterministic_replay_exact": replay_exact,
                "ledger_replay_exact": ledger_exact,
                "candidate_ledger": candidate.ledger,
            }
        )

    # Verifier-only exact reference is built after candidate/comparator execution.
    exact_parts = [build_exact_reference(sub).mean for sub in subnetworks]
    exact = np.concatenate(exact_parts).astype(np.float64, copy=False)

    for record, candidate_mean, iid_mean in zip(
        records, candidate_means, iid_means
    ):
        candidate_mse = _mse(candidate_mean, exact)
        iid_mse = _mse(iid_mean, exact)
        record.update(
            {
                "candidate_mse": candidate_mse,
                "iid_mse": iid_mse,
                "candidate_over_iid": (
                    candidate_mse / iid_mse if iid_mse > 0.0 else math.inf
                ),
                "candidate_over_raw_scale": candidate_mse / RAW_MSE_SCALE,
                "exact_mean_sha256": _sha(exact),
            }
        )

    pooled_candidate = float(np.mean([r["candidate_mse"] for r in records]))
    pooled_iid = float(np.mean([r["iid_mse"] for r in records]))
    ratio = (
        pooled_candidate / pooled_iid if pooled_iid > 0.0 else math.inf
    )

    result = {
        "name": name,
        "input_dimension": 2 * len(block_seeds),
        "width": 2 * len(block_seeds),
        "depth": 4,
        "block_subnetwork_seeds": list(block_seeds),
        "candidate_seeds": list(candidate_seeds),
        "iid_seeds": list(iid_seeds),
        "candidate_received_block_decomposition": False,
        "exact_reference_construction": (
            "verifier-only concatenation of exact E114 2-D subnetwork means"
        ),
        "directions_per_estimate": SAMPLES,
        "records": records,
        "pooled_candidate_mse": pooled_candidate,
        "pooled_iid_mse": pooled_iid,
        "candidate_over_iid": ratio,
        "candidate_over_raw_scale": pooled_candidate / RAW_MSE_SCALE,
        "max_frame_orthogonality_abs": orth_max,
        "max_source_direction_norm_abs": norm_max,
        "candidate_outputs_finite_all": all(
            bool(r["candidate_finite"]) for r in records
        ),
    }
    return result, deterministic_all, ledger_all, orth_max, norm_max


def main() -> None:
    code = regular_simplex_code(SOURCE_DIM)
    simplex = simplex_algebra_metrics(code)
    source_audit = _candidate_source_audit()

    method_cost = production_cost_receipt()
    independent_cost = _independent_production_cost()
    cost_reconciles = method_cost["all_in_upper"] == independent_cost["all_in_upper"]

    stress8, det8, ledger8, orth8, norm8 = _run_stress(
        name="8d_four_source",
        block_seeds=BLOCK8_SEEDS,
        candidate_seeds=CANDIDATE8_SEEDS,
        iid_seeds=IID8_SEEDS,
    )
    stress16, det16, ledger16, orth16, norm16 = _run_stress(
        name="16d_eight_source",
        block_seeds=BLOCK16_SEEDS,
        candidate_seeds=CANDIDATE16_SEEDS,
        iid_seeds=IID16_SEEDS,
    )

    deterministic_all = bool(det8 and det16)
    ledger_all = bool(ledger8 and ledger16)
    orth_max = max(orth8, orth16)
    norm_max = max(norm8, norm16)

    simplex_gate = bool(
        simplex["max_vertex_norm_error"] <= 2e-14
        and simplex["max_vertex_gram_error"] <= 2e-14
        and simplex["vertex_sum_inf"] <= 2e-14
        and simplex["second_moment_max_abs_error"] <= 2e-14
    )

    gates = {
        "simplex_algebra_exact": simplex_gate,
        "candidate_outputs_finite_all": bool(
            stress8["candidate_outputs_finite_all"]
            and stress16["candidate_outputs_finite_all"]
        ),
        "frame_orthogonality_le_2e_12": orth_max <= 2e-12,
        "source_direction_norm_le_2e_12": norm_max <= 2e-12,
        "deterministic_replay_bitwise_exact_all": deterministic_all,
        "accounting_ledger_replay_exact_all": ledger_all,
        "exact_8d_candidate_over_iid_le_0_90": (
            stress8["candidate_over_iid"] <= 0.90
        ),
        "exact_16d_candidate_over_iid_le_0_95": (
            stress16["candidate_over_iid"] <= 0.95
        ),
        "candidate_source_audit_pass": source_audit["passes"],
        "production_cost_independent_reconciliation": cost_reconciles,
        "production_all_in_le_hard_cap": bool(
            independent_cost["passes_cap"]
            and method_cost["passes_cap"]
        ),
        "no_targets_public_scorer_holdout_full": True,
    }

    integrity_keys = (
        "simplex_algebra_exact",
        "candidate_outputs_finite_all",
        "frame_orthogonality_le_2e_12",
        "source_direction_norm_le_2e_12",
        "deterministic_replay_bitwise_exact_all",
        "accounting_ledger_replay_exact_all",
        "candidate_source_audit_pass",
        "production_cost_independent_reconciliation",
        "production_all_in_le_hard_cap",
        "no_targets_public_scorer_holdout_full",
    )
    integrity_ok = bool(all(gates[k] for k in integrity_keys))
    scientific_go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e122.haar8_simplex_falsifier.v1",
        "experiment": "E122",
        "idempotency_key": "ARC-E122-HAAR8-ANTIPODAL-SIMPLEX-SOURCE-CODE-20260920",
        "mechanism": {
            "name": "Haar-8 antipodal regular-simplex source-code estimator",
            "source_dimension": SOURCE_DIM,
            "simplex_vertices": SOURCE_DIM + 1,
            "codewords": CODEWORDS,
            "frames": FRAMES,
            "directions": SAMPLES,
            "unbiasedness": (
                "for each fixed unit coefficient a, Haar Stiefel U gives Ua "
                "uniform on the sphere; equal-weight finite code average "
                "therefore has the correct spherical expectation"
            ),
            "sign_cone_enumeration": False,
            "factorized_cumulants": False,
            "hermite": False,
            "gaussian_plugin": False,
            "boundary_compression": False,
            "e121_rescue": False,
            "target_fit": False,
        },
        "simplex_algebra": simplex,
        "source_audit": source_audit,
        "exact_8d_stress": stress8,
        "exact_16d_stress": stress16,
        "historical_e121_8d_candidate_over_iid_diagnostic": (
            E121_8D_RATIO_DIAGNOSTIC
        ),
        "production_cost_method": method_cost,
        "production_cost_independent": independent_cost,
        "summary": {
            "raw_mse_scale_diagnostic": RAW_MSE_SCALE,
            "exact_8d_candidate_over_iid": stress8["candidate_over_iid"],
            "exact_16d_candidate_over_iid": stress16["candidate_over_iid"],
            "max_frame_orthogonality_abs": orth_max,
            "max_source_direction_norm_abs": norm_max,
            "deterministic_replay_exact_all": deterministic_all,
            "ledger_replay_exact_all": ledger_all,
            "production_all_in_upper": independent_cost["all_in_upper"],
            "production_hard_cap": PRODUCTION_CAP_FLOPS,
            "production_slack": independent_cost["slack_flops"],
        },
        "gates": gates,
        "integrity_ok": integrity_ok,
        "scientific_go": scientific_go,
        "decision": (
            "E122_LOCAL_SCIENTIFIC_GO_MULTI_SOURCE_ALGEBRAIC_SOURCE_CODE"
            if scientific_go
            else "E122_TERMINAL_NO_GO_CLOSE_HAAR8_ANTIPODAL_SIMPLEX_SOURCE_CODE"
        ),
        "scope": {
            "target_free": True,
            "synthetic_exact_reference_only": True,
            "production_execution": False,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "tuning": False,
            "sweep": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
            "merged": False,
        },
    }

    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("E122_HAAR8_SIMPLEX=" + json.dumps(result, sort_keys=True), flush=True)

    # Scientific failure is a valid terminal result. Only integrity/purity/
    # determinism/accounting failure fails the Actions job.
    if not integrity_ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
