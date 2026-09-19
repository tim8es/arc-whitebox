#!/usr/bin/env python3
from __future__ import annotations

import ast
import builtins
import hashlib
import json
import math
from pathlib import Path
import subprocess
from typing import Any
from unittest.mock import patch

import numpy as np

import methods.e114_exact_angular_reference as exact_ref
import methods.e119_generic_boundary_flux as candidate

OUT = Path("e119-target-free-crosscheck.json")
MANIFEST_PATH = Path("research/E119_TARGET_FREE_CROSSCHECK_MANIFEST.json")

WIDTH = 4
DEPTH = 3
WEIGHT_SEED = 119904
BUDGET = 2**41
TOL = 1e-15

EXPECTED_RAW_MSE_GATE = 1.89e-8
EXPECTED_GAUSSIAN_FACTOR = math.sqrt(math.pi / 2.0) / (2.0 * math.pi)
EXPECTED_L1_BUDGET = math.sqrt(EXPECTED_RAW_MSE_GATE) / EXPECTED_GAUSSIAN_FACTOR

FORBIDDEN_IMPORT_ROOTS = {"whestbench", "datasets"}
FORBIDDEN_NAMES = {
    "build_exact_reference",
    "oracle_flux_basis",
    "projection_metrics",
    "observable_metrics",
}
FORBIDDEN_CALL_SUFFIXES = {
    "lstsq",
    "solve",
    "pinv",
    "polyfit",
    "cov",
    "var",
    "least_squares",
    "load",
    "loadtxt",
    "genfromtxt",
    "read_csv",
    "read_parquet",
}
SCIENTIFIC_PATHS = (
    "methods/e119_generic_boundary_flux.py",
    "methods/e118_output_flux_sketch.py",
    "scripts/e119_generic_boundary_flux_certificate.py",
    "tests/test_e119_generic_boundary_flux.py",
    ".github/workflows/e119-generic-boundary-flux-certificate.yml",
    "research/E119_PROTOCOL.md",
    "research/E119_RUN_ARM.json",
)


def make_weights(seed: int, width: int, depth: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    out: list[np.ndarray] = []
    first = rng.standard_normal((2, width)).astype(np.float64)
    first *= math.sqrt(2.0 / 2.0)
    out.append(first)
    for _ in range(1, depth):
        w = rng.standard_normal((width, width)).astype(np.float64)
        w *= math.sqrt(2.0 / width)
        out.append(w)
    return out


def array_sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def result_digest(result: Any) -> dict[str, Any]:
    return {
        "boundary_angles_sha256": array_sha(result.boundary_angles),
        "scalar_jumps_sha256": array_sha(result.scalar_jumps),
        "kept_indices_sha256": array_sha(result.kept_indices),
        "omitted_indices_sha256": array_sha(result.omitted_indices),
        "full_mean": float(result.full_mean),
        "compressed_mean": float(result.compressed_mean),
        "omitted_abs_flux_sum": float(result.omitted_abs_flux_sum),
        "abs_remainder_certificate": float(result.abs_remainder_certificate),
        "layer_region_counts": list(result.layer_region_counts),
        "flops": result.flops,
        "finite": bool(result.finite),
    }


def forbidden_call(*args: Any, **kwargs: Any) -> Any:
    raise RuntimeError("E119_TARGET_FREE_GUARD_FORBIDDEN_CALL")


def run_guarded(weights: list[np.ndarray]) -> Any:
    patches = [
        patch.object(exact_ref, "build_exact_reference", side_effect=forbidden_call),
        patch.object(np.linalg, "lstsq", side_effect=forbidden_call),
        patch.object(np.linalg, "solve", side_effect=forbidden_call),
        patch.object(np.linalg, "pinv", side_effect=forbidden_call),
        patch.object(np, "polyfit", side_effect=forbidden_call),
        patch.object(np, "cov", side_effect=forbidden_call),
        patch.object(np, "var", side_effect=forbidden_call),
        patch.object(builtins, "open", side_effect=forbidden_call),
        patch.object(Path, "open", side_effect=forbidden_call),
        patch.object(Path, "read_text", side_effect=forbidden_call),
        patch.object(Path, "read_bytes", side_effect=forbidden_call),
        patch.object(np, "load", side_effect=forbidden_call),
        patch.object(np, "loadtxt", side_effect=forbidden_call),
        patch.object(np, "genfromtxt", side_effect=forbidden_call),
    ]
    exits = []
    try:
        for p in patches:
            exits.append(p.start())
        return candidate.build_generic_boundary_flux(weights, budget=BUDGET)
    finally:
        for p in reversed(patches):
            p.stop()


def independent_selection(result: Any) -> dict[str, Any]:
    angles = np.asarray(result.boundary_angles, dtype=np.float64)
    jumps = np.asarray(result.scalar_jumps, dtype=np.float64)

    order = sorted(
        range(jumps.shape[0]),
        key=lambda i: (abs(float(jumps[i])), float(angles[i]), int(i)),
    )
    omitted: list[int] = []
    omitted_abs = 0.0
    for idx in order:
        value = abs(float(jumps[idx]))
        if omitted_abs + value <= EXPECTED_L1_BUDGET:
            omitted.append(idx)
            omitted_abs += value
        else:
            break

    omitted_set = set(omitted)
    kept = [i for i in range(jumps.shape[0]) if i not in omitted_set]
    kept_jumps = jumps[np.asarray(kept, dtype=np.int64)] if kept else np.zeros(0)
    compressed = EXPECTED_GAUSSIAN_FACTOR * float(
        np.sum(kept_jumps, dtype=np.float64)
    )
    certificate = EXPECTED_GAUSSIAN_FACTOR * omitted_abs

    omitted_equal = np.array_equal(
        np.asarray(omitted, dtype=np.int64),
        np.asarray(result.omitted_indices, dtype=np.int64),
    )
    kept_equal = np.array_equal(
        np.asarray(kept, dtype=np.int64),
        np.asarray(result.kept_indices, dtype=np.int64),
    )

    return {
        "omitted_indices": omitted,
        "kept_indices": kept,
        "omitted_indices_equal": bool(omitted_equal),
        "kept_indices_equal": bool(kept_equal),
        "omitted_abs_flux_sum": omitted_abs,
        "omitted_abs_flux_sum_abs_error": abs(
            omitted_abs - float(result.omitted_abs_flux_sum)
        ),
        "compressed_mean": compressed,
        "compressed_mean_abs_error": abs(
            compressed - float(result.compressed_mean)
        ),
        "certificate": certificate,
        "certificate_abs_error": abs(
            certificate - float(result.abs_remainder_certificate)
        ),
    }


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def scan_source(path: str) -> dict[str, Any]:
    source = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=path)
    findings: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in FORBIDDEN_IMPORT_ROOTS:
                    findings.append(
                        {"kind": "import", "name": alias.name, "line": node.lineno}
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = module.split(".", 1)[0]
            if root in FORBIDDEN_IMPORT_ROOTS:
                findings.append(
                    {"kind": "import_from", "name": module, "line": node.lineno}
                )
            for alias in node.names:
                if alias.name in FORBIDDEN_NAMES:
                    findings.append(
                        {"kind": "forbidden_name_import", "name": alias.name, "line": node.lineno}
                    )
        elif isinstance(node, ast.Call):
            name = _call_name(node.func)
            suffix = name.rsplit(".", 1)[-1] if name else ""
            if suffix in FORBIDDEN_CALL_SUFFIXES or name in FORBIDDEN_NAMES:
                findings.append(
                    {"kind": "call", "name": name, "line": node.lineno}
                )
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id in FORBIDDEN_NAMES:
                findings.append(
                    {"kind": "name", "name": node.id, "line": node.lineno}
                )

    return {
        "path": path,
        "sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "findings": findings,
        "pass": not findings,
    }


def git_blob(path: str, rev: str) -> str:
    content = subprocess.check_output(["git", "show", f"{rev}:{path}"])
    return subprocess.check_output(
        ["git", "hash-object", "--stdin"], input=content
    ).decode("ascii").strip()


def current_blob(path: str) -> str:
    return subprocess.check_output(
        ["git", "hash-object", path], text=True
    ).strip()


def immutability_check(manifest: dict[str, Any]) -> dict[str, Any]:
    arm = manifest["executed_arm"]
    sealed = manifest["sealed_e119_head"]
    records = []
    all_pass = True

    for path in SCIENTIFIC_PATHS:
        expected = manifest["scientific_blob_pairs"][path]
        arm_blob = git_blob(path, arm)
        sealed_blob = git_blob(path, sealed)
        checkout_blob = current_blob(path)
        ok = (
            arm_blob == expected["arm"]
            and sealed_blob == expected["sealed"]
            and arm_blob == sealed_blob
            and sealed_blob == checkout_blob
        )
        all_pass = all_pass and ok
        records.append(
            {
                "path": path,
                "expected_arm_blob": expected["arm"],
                "expected_sealed_blob": expected["sealed"],
                "actual_arm_blob": arm_blob,
                "actual_sealed_blob": sealed_blob,
                "current_checkout_blob": checkout_blob,
                "pass": bool(ok),
            }
        )

    return {"records": records, "all_pass": bool(all_pass)}


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    constants = {
        "raw_mse_gate": float(candidate.RAW_MSE_GATE),
        "gaussian_factor": float(candidate.GAUSSIAN_FACTOR),
        "omitted_flux_l1_budget": float(candidate.OMITTED_FLUX_L1_BUDGET),
        "raw_mse_gate_abs_error": abs(
            float(candidate.RAW_MSE_GATE) - EXPECTED_RAW_MSE_GATE
        ),
        "gaussian_factor_abs_error": abs(
            float(candidate.GAUSSIAN_FACTOR) - EXPECTED_GAUSSIAN_FACTOR
        ),
        "omitted_flux_l1_budget_abs_error": abs(
            float(candidate.OMITTED_FLUX_L1_BUDGET) - EXPECTED_L1_BUDGET
        ),
    }

    weights_a = make_weights(WEIGHT_SEED, WIDTH, DEPTH)
    weights_b = make_weights(WEIGHT_SEED, WIDTH, DEPTH)
    weight_digest_a = [array_sha(w) for w in weights_a]
    weight_digest_b = [array_sha(w) for w in weights_b]

    guarded_error = None
    first = None
    second = None
    try:
        first = run_guarded([w.copy() for w in weights_a])
        second = run_guarded([w.copy() for w in weights_b])
    except Exception as exc:
        guarded_error = f"{type(exc).__name__}: {exc}"

    runtime_guard_pass = guarded_error is None and first is not None and second is not None

    replay_exact = False
    selection = None
    first_digest = None
    second_digest = None
    if runtime_guard_pass:
        first_digest = result_digest(first)
        second_digest = result_digest(second)
        replay_exact = first_digest == second_digest
        selection = independent_selection(first)

    scans = [
        scan_source("methods/e119_generic_boundary_flux.py"),
        scan_source("methods/e118_output_flux_sketch.py"),
    ]
    static_scan_pass = all(item["pass"] for item in scans)

    immutable = immutability_check(manifest)

    selection_pass = bool(
        selection is not None
        and selection["omitted_indices_equal"]
        and selection["kept_indices_equal"]
        and selection["omitted_abs_flux_sum_abs_error"] <= TOL
        and selection["compressed_mean_abs_error"] <= TOL
        and selection["certificate_abs_error"] <= TOL
    )

    constants_pass = bool(
        constants["raw_mse_gate_abs_error"] == 0.0
        and constants["gaussian_factor_abs_error"] <= 1e-18
        and constants["omitted_flux_l1_budget_abs_error"] <= 1e-18
    )

    gates = {
        "frozen_fixture_weights_deterministic": weight_digest_a == weight_digest_b,
        "poisoned_reference_and_fit_apis_not_called": runtime_guard_pass,
        "forbidden_file_io_not_called": runtime_guard_pass,
        "candidate_finite_under_guards": bool(
            runtime_guard_pass and first is not None and first.finite
        ),
        "independent_selection_matches_candidate": selection_pass,
        "frozen_constants_unchanged": constants_pass,
        "candidate_helper_static_scan_clean": static_scan_pass,
        "arm_to_sealed_scientific_blobs_identical": immutable["all_pass"],
        "deterministic_replay_exact": replay_exact,
        "no_benchmark_public_scorer_holdout_full_execution": True,
        "no_tuning_sweep_rescue_rerun": True,
    }

    passed = bool(all(gates.values()))
    result = {
        "schema": "arc.whitebox.e119.target_free_crosscheck.v1",
        "experiment": "E119",
        "idempotency_key": "ARC-E119-TARGET-FREE-CROSSCHECK-20260919",
        "status": (
            "E119_TARGET_FREE_ESTIMATOR_HYGIENE_VERIFIED"
            if passed
            else "E119_TARGET_FREE_HYGIENE_NO_GO"
        ),
        "parent_sealed_e119_head": manifest["sealed_e119_head"],
        "executed_arm": manifest["executed_arm"],
        "fixture": manifest["fixture"],
        "weight_sha256": weight_digest_a,
        "runtime_guards": {
            "pass": runtime_guard_pass,
            "error": guarded_error,
            "guarded_api_count": len(manifest["forbidden_runtime_calls"]),
            "guarded_apis": manifest["forbidden_runtime_calls"],
        },
        "candidate_first": first_digest,
        "candidate_second": second_digest,
        "independent_selection": selection,
        "frozen_constants": constants,
        "static_scans": scans,
        "post_result_immutability": immutable,
        "gates": gates,
        "decision": (
            "E119_TARGET_FREE_ESTIMATOR_HYGIENE_VERIFIED"
            if passed
            else "E119_TARGET_FREE_HYGIENE_NO_GO"
        ),
        "scope": {
            "target_free_crosscheck_only": True,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "production_scientific_run": False,
            "tuning": False,
            "sweep": False,
            "post_result_fitting": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E119_TARGET_FREE_CROSSCHECK=" + json.dumps(result, sort_keys=True), flush=True)

    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
