#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from methods.e114_exact_angular_reference import build_exact_reference, he_weights
from methods.e121_haar_plane_orbit import (
    PRODUCTION_FRAMES,
    PRODUCTION_PHASES,
    haar_plane_orbit_mean,
    iid_spherical_mean,
    production_cost_receipt,
)

RAW_MSE_SCALE = 1.89e-8
FRAMES = PRODUCTION_FRAMES
PHASES = PRODUCTION_PHASES
SAMPLES = FRAMES * PHASES
NETWORK_SEEDS_2D = (114200, 114201, 114202, 114203)
CANDIDATE_SEEDS_2D = (121200, 121201, 121202, 121203)
BLOCK_SEEDS = (121300, 121301, 121302, 121303)
CANDIDATE_SEEDS_8D = (121400, 121401, 121402, 121403)
IID_SEEDS = (121500, 121501, 121502, 121503)
OUT = Path("e121-haar-plane-orbit-falsifier.json")


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _mse(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.mean(d * d))


def _block_diag_2x2(blocks: list[np.ndarray]) -> np.ndarray:
    out = np.zeros((8, 8), dtype=np.float64)
    for i, b in enumerate(blocks):
        lo = 2 * i
        out[lo : lo + 2, lo : lo + 2] = np.asarray(b, dtype=np.float64)
    return out


def _build_block_network() -> tuple[list[np.ndarray], list[list[np.ndarray]]]:
    subnetworks = [
        he_weights(seed, width=2, depth=4) for seed in BLOCK_SEEDS
    ]
    full = []
    for layer in range(4):
        full.append(_block_diag_2x2([sub[layer] for sub in subnetworks]))
    return full, subnetworks


def _candidate_source_audit() -> dict:
    path = Path("methods/e121_haar_plane_orbit.py")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    forbidden_imports = [
        x for x in imports
        if (
            "e114_exact_angular_reference" in x
            or "e119_generic_boundary_flux" in x
            or "whestbench" in x
            or "datasets" == x
        )
    ]
    return {
        "candidate_path": str(path),
        "candidate_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "imports": sorted(imports),
        "forbidden_imports": forbidden_imports,
        "passes": not forbidden_imports,
    }


def main() -> None:
    source_audit = _candidate_source_audit()
    production_cost = production_cost_receipt()

    records_2d = []
    deterministic_all = True
    ledger_deterministic_all = True
    orth_max = 0.0

    # Candidate and comparator execute before the exact reference is built.
    for net_seed, cand_seed, iid_seed in zip(
        NETWORK_SEEDS_2D, CANDIDATE_SEEDS_2D, IID_SEEDS
    ):
        weights = he_weights(net_seed, width=8, depth=4)
        cand = haar_plane_orbit_mean(
            weights, frames=FRAMES, phases=PHASES, seed=cand_seed
        )
        replay = haar_plane_orbit_mean(
            weights, frames=FRAMES, phases=PHASES, seed=cand_seed
        )
        iid = iid_spherical_mean(
            weights, samples=SAMPLES, seed=iid_seed
        )

        replay_exact = bool(
            np.array_equal(cand.mean, replay.mean)
            and cand.frame_orthogonality_max_abs
            == replay.frame_orthogonality_max_abs
        )
        ledger_exact = cand.ledger == replay.ledger
        deterministic_all = deterministic_all and replay_exact
        ledger_deterministic_all = (
            ledger_deterministic_all and ledger_exact
        )
        orth_max = max(orth_max, cand.frame_orthogonality_max_abs)

        ref = build_exact_reference(weights)
        cand_mse = _mse(cand.mean, ref.mean)
        iid_mse = _mse(iid, ref.mean)

        records_2d.append(
            {
                "network_seed": net_seed,
                "candidate_seed": cand_seed,
                "iid_seed": iid_seed,
                "candidate_mse": cand_mse,
                "iid_mse": iid_mse,
                "candidate_over_iid": (
                    cand_mse / iid_mse if iid_mse > 0.0 else math.inf
                ),
                "candidate_over_raw_scale": cand_mse / RAW_MSE_SCALE,
                "candidate_mean_sha256": _sha(cand.mean),
                "iid_mean_sha256": _sha(iid),
                "exact_mean_sha256": _sha(ref.mean),
                "frame_orthogonality_max_abs": (
                    cand.frame_orthogonality_max_abs
                ),
                "deterministic_replay_exact": replay_exact,
                "ledger_replay_exact": ledger_exact,
                "candidate_finite": cand.finite,
                "candidate_ledger": cand.ledger,
                "exact_region_count": len(ref.sectors),
            }
        )

    pooled_2d_candidate = float(
        np.mean([r["candidate_mse"] for r in records_2d])
    )
    pooled_2d_iid = float(
        np.mean([r["iid_mse"] for r in records_2d])
    )
    ratio_2d = (
        pooled_2d_candidate / pooled_2d_iid
        if pooled_2d_iid > 0.0 else math.inf
    )

    # One exact 8-D block network, four independent frozen estimator seeds.
    block_weights, subnetworks = _build_block_network()
    records_8d = []
    candidate_means_8d = []
    iid_means_8d = []

    for cand_seed, iid_seed in zip(CANDIDATE_SEEDS_8D, IID_SEEDS):
        cand = haar_plane_orbit_mean(
            block_weights, frames=FRAMES, phases=PHASES, seed=cand_seed
        )
        replay = haar_plane_orbit_mean(
            block_weights, frames=FRAMES, phases=PHASES, seed=cand_seed
        )
        iid = iid_spherical_mean(
            block_weights, samples=SAMPLES, seed=iid_seed
        )
        replay_exact = bool(
            np.array_equal(cand.mean, replay.mean)
            and cand.frame_orthogonality_max_abs
            == replay.frame_orthogonality_max_abs
        )
        ledger_exact = cand.ledger == replay.ledger
        deterministic_all = deterministic_all and replay_exact
        ledger_deterministic_all = (
            ledger_deterministic_all and ledger_exact
        )
        orth_max = max(orth_max, cand.frame_orthogonality_max_abs)
        candidate_means_8d.append(cand.mean)
        iid_means_8d.append(iid)
        records_8d.append(
            {
                "candidate_seed": cand_seed,
                "iid_seed": iid_seed,
                "candidate_mean_sha256": _sha(cand.mean),
                "iid_mean_sha256": _sha(iid),
                "frame_orthogonality_max_abs": (
                    cand.frame_orthogonality_max_abs
                ),
                "deterministic_replay_exact": replay_exact,
                "ledger_replay_exact": ledger_exact,
                "candidate_finite": cand.finite,
                "candidate_ledger": cand.ledger,
            }
        )

    # Reference is assembled only after every 8-D candidate/comparator execution.
    exact_blocks = [build_exact_reference(sub).mean for sub in subnetworks]
    exact_8d = np.concatenate(exact_blocks).astype(np.float64, copy=False)

    for record, cand_mean, iid_mean in zip(
        records_8d, candidate_means_8d, iid_means_8d
    ):
        cand_mse = _mse(cand_mean, exact_8d)
        iid_mse = _mse(iid_mean, exact_8d)
        record.update(
            {
                "candidate_mse": cand_mse,
                "iid_mse": iid_mse,
                "candidate_over_iid": (
                    cand_mse / iid_mse if iid_mse > 0.0 else math.inf
                ),
                "candidate_over_raw_scale": cand_mse / RAW_MSE_SCALE,
                "exact_mean_sha256": _sha(exact_8d),
            }
        )

    pooled_8d_candidate = float(
        np.mean([r["candidate_mse"] for r in records_8d])
    )
    pooled_8d_iid = float(
        np.mean([r["iid_mse"] for r in records_8d])
    )
    ratio_8d = (
        pooled_8d_candidate / pooled_8d_iid
        if pooled_8d_iid > 0.0 else math.inf
    )

    finite_all = bool(
        all(r["candidate_finite"] for r in records_2d)
        and all(r["candidate_finite"] for r in records_8d)
        and np.isfinite(
            [
                pooled_2d_candidate,
                pooled_2d_iid,
                ratio_2d,
                pooled_8d_candidate,
                pooled_8d_iid,
                ratio_8d,
            ]
        ).all()
    )

    gates = {
        "candidate_outputs_finite_all": finite_all,
        "frame_orthogonality_le_2e_12": orth_max <= 2e-12,
        "deterministic_replay_bitwise_exact_all": deterministic_all,
        "accounting_ledger_replay_exact_all": ledger_deterministic_all,
        "exact_2d_candidate_beats_same_node_iid": (
            pooled_2d_candidate < pooled_2d_iid
        ),
        "exact_8d_block_candidate_over_iid_le_0_90": ratio_8d <= 0.90,
        "candidate_source_audit_no_reference_or_dataset_import": (
            source_audit["passes"]
        ),
        "production_all_in_util_le_0_13": production_cost["passes_cap"],
        "no_targets_public_scorer_holdout_full": True,
    }

    integrity_keys = [
        "candidate_outputs_finite_all",
        "frame_orthogonality_le_2e_12",
        "deterministic_replay_bitwise_exact_all",
        "accounting_ledger_replay_exact_all",
        "candidate_source_audit_no_reference_or_dataset_import",
        "production_all_in_util_le_0_13",
        "no_targets_public_scorer_holdout_full",
    ]
    integrity_ok = bool(all(gates[k] for k in integrity_keys))
    scientific_go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e121.haar_plane_orbit_falsifier.v1",
        "experiment": "E121",
        "idempotency_key": (
            "ARC-E121-HAAR-PLANE-ORBIT-SOURCE-MEMORY-20260919"
        ),
        "mechanism": {
            "name": "Haar-plane cyclic-orbit source-memory estimator",
            "frames": FRAMES,
            "phases_per_frame": PHASES,
            "directions": SAMPLES,
            "sign_cones_enumerated": False,
            "activation_boundaries_enumerated": False,
            "gaussian_plugin": False,
            "target_fit": False,
            "late_layer_source_memory": (
                "shared 2-D phase orbit propagated through every ReLU layer"
            ),
            "unbiasedness": (
                "each fixed phase of a Haar two-frame is uniform on the "
                "sphere; positive homogeneity supplies exact E[chi_d] radius"
            ),
        },
        "source_audit": source_audit,
        "exact_2d": {
            "network_seeds": list(NETWORK_SEEDS_2D),
            "candidate_seeds": list(CANDIDATE_SEEDS_2D),
            "iid_seeds": list(IID_SEEDS),
            "records": records_2d,
            "pooled_candidate_mse": pooled_2d_candidate,
            "pooled_iid_mse": pooled_2d_iid,
            "candidate_over_iid": ratio_2d,
            "candidate_over_raw_scale": (
                pooled_2d_candidate / RAW_MSE_SCALE
            ),
        },
        "exact_8d_block_stress": {
            "block_subnetwork_seeds": list(BLOCK_SEEDS),
            "candidate_seeds": list(CANDIDATE_SEEDS_8D),
            "iid_seeds": list(IID_SEEDS),
            "exact_reference_construction": (
                "concatenate four independent exact 2-D E114 subnetwork means"
            ),
            "candidate_received_block_decomposition": False,
            "records": records_8d,
            "pooled_candidate_mse": pooled_8d_candidate,
            "pooled_iid_mse": pooled_8d_iid,
            "candidate_over_iid": ratio_8d,
            "candidate_over_raw_scale": (
                pooled_8d_candidate / RAW_MSE_SCALE
            ),
        },
        "production_cost": production_cost,
        "summary": {
            "raw_mse_scale_diagnostic": RAW_MSE_SCALE,
            "max_frame_orthogonality_abs": orth_max,
            "deterministic_replay_exact_all": deterministic_all,
            "ledger_replay_exact_all": ledger_deterministic_all,
            "exact_2d_candidate_over_iid": ratio_2d,
            "exact_8d_candidate_over_iid": ratio_8d,
            "production_all_in_upper": production_cost["all_in_upper"],
            "production_utilization": production_cost["utilization"],
        },
        "gates": gates,
        "integrity_ok": integrity_ok,
        "scientific_go": scientific_go,
        "decision": (
            "E121_LOCAL_SCIENTIFIC_GO_HAAR_PLANE_ORBIT_SOURCE_MEMORY"
            if scientific_go
            else "E121_TERMINAL_NO_GO_CLOSE_HAAR_PLANE_ORBIT_SOURCE_MEMORY"
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
    print(
        "E121_HAAR_PLANE_ORBIT="
        + json.dumps(result, sort_keys=True),
        flush=True,
    )

    # A scientific NO-GO is a valid completed frozen falsifier. Only
    # instrumentation/accounting/source-purity failure makes the job fail.
    if not integrity_ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
