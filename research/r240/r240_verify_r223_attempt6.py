#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import tempfile
import zipfile
from pathlib import Path
from typing import Any

BUDGET = 2**41
EXPECTED_DATASET_SHA = "264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"
EXPECTED_NAMES_SHA = "18c917b7f0870aa366a7d6803e79b0eaeadd7f2fc2944130cd019782298473ce"
PARENT_REPORT_SHA256 = "68683f9f2e8eca89a85fd18826998f5937d4770c2ce33bf6e6738fb236c8e5a3"
PARENT_NORMALIZED_BLOB = "0183d0570f7c9965e00e8553ffc003c313865232"
PARENT_NORMALIZED_SHA256 = "f1168e1004d736a2435d6a5800d184113e96105165edde15d9e945dd27f15742"

PARENT_MSE = 2.228303490170447e-8
PARENT_SCORE = 8.170397440117225e-9
PARENT_CB = 0.36666448157347986
TARGET_SCORE = 8.129545452916639e-9

EXPECTED_BLOBS = {
    "research/r223/R223_PROTOCOL.md": "1e88341a6320bf91c8f4eff0aa60d8b6a33cf484",
    "research/r223/R223_ATTEMPT2_PROTOCOL.md": "cc8fada8088942de9e284e09f1266d89278cb0b6",
    "research/r223/R223_ATTEMPT3_INFRA_PATCH.md": "d76406ae9292782c2592b3ef9377341d127fb348",
    "research/r223/R223_ATTEMPT4_PROVENANCE_PATCH.md": "e5c92d45e638bc85b66753c00c909e1f00aa9345",
    "research/r223/R223_ATTEMPT5_AUTH_PATCH.md": "82cb86a6d2a175c0dcaf2358f70d6d33206cd486",
    "research/r223/R223_ATTEMPT6_PATH_PATCH.md": "acdf3b788dfdf635533a23a9cf3d282a35241586",
    "methods/r223_estimator_v25_local_feed.py": "eb95d4ae46a031be5131eef8dd0909f2061b8749",
    "scripts/r223_verify_exact_transform.py": "961e5afb052e2cfdc15e1284de49e57ba1514a73",
    "scripts/r223_compare_panel.py": "fd1ce8711f92bb123f69d7bcddb37bb0fec3b8b0",
}
EXPECTED_WORKFLOW_BLOB = "d24e3f63e8ce447188868846e9b3e4ef755b395e"
EXPECTED_ARTIFACT_NAME = "r223-v25-local-feed-mini100-attempt6"
EXPECTED_CANDIDATE_RUN_ID = "R223-v25-local-feed-attempt6-20260923"

FAILURE_FLAGS = (
    "budget_exhausted",
    "time_exhausted",
    "residual_wall_time_exhausted",
    "combined_budget_exhausted",
)

MANDATORY_EVIDENCE = {
    "compute_gate.json",
    "whest_version.json",
    "environment.txt",
    "source_transform_guard.json",
    "static_feed_identity.json",
    "parent-report.json",
    "validate.json",
    "validate.stderr",
    "validate.exit",
    "candidate-report.json",
    "run.stderr",
    "run.exit",
    "R223_ATTEMPT6_RESULT.json",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    hdr = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(hdr + data).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def is_failed(row: dict[str, Any]) -> bool:
    # Canonical whestbench 0.16.1 aggregate predicate:
    # error_code OR any budget/time/residual/combined exhaustion flag.
    return bool(row.get("error_code")) or any(bool(row.get(k)) for k in FAILURE_FLAGS)


def official_score(row: dict[str, Any]) -> float:
    mse = float(row["final_layer_mse"])
    c = float(row.get("effective_compute", row.get("flops_used", 0.0)))
    multiplier = 1.0 if is_failed(row) else max(0.1, c / BUDGET)
    return mse * multiplier


def close(a: float, b: float, *, rel: float = 5e-12, abs_: float = 1e-18) -> bool:
    return math.isclose(float(a), float(b), rel_tol=rel, abs_tol=abs_)


def names_sha(rows: list[dict[str, Any]]) -> str:
    names = [r["mlp_name"] for r in rows]
    return hashlib.sha256(
        json.dumps(names, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def row_identity(parent: list[dict[str, Any]], candidate: list[dict[str, Any]]) -> bool:
    if len(parent) != 100 or len(candidate) != 100:
        return False
    return all(
        (p.get("mlp_index"), p.get("mlp_name"))
        == (c.get("mlp_index"), c.get("mlp_name"))
        for p, c in zip(parent, candidate)
    )


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def paired_se(xs: list[float]) -> float:
    return statistics.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else 0.0


def verify_report_scores(report: dict[str, Any]) -> dict[str, Any]:
    rows = report["results"]["per_mlp"]
    mismatches = []
    for i, row in enumerate(rows):
        got = official_score(row)
        reported = float(row["adjusted_final_layer_score"])
        if not close(got, reported):
            mismatches.append(
                {
                    "row": i,
                    "mlp_name": row.get("mlp_name"),
                    "recomputed": got,
                    "reported": reported,
                    "failed": is_failed(row),
                }
            )
    recomputed_mean = mean([official_score(r) for r in rows])
    reported_mean = float(report["results"]["adjusted_final_layer_score"])
    return {
        "rows": len(rows),
        "row_score_mismatches": mismatches,
        "recomputed_mean_adjusted": recomputed_mean,
        "reported_mean_adjusted": reported_mean,
        "aggregate_adjusted_matches": close(recomputed_mean, reported_mean),
    }


def manifest_key_for_artifact_path(rel: str) -> str:
    prefix = "r223_attempt6_evidence/"
    if rel.startswith(prefix):
        return rel[len(prefix):]
    return rel


def verify_manifest(root: Path) -> dict[str, Any]:
    manifest_path = root / "r223_attempt6_evidence" / "sha256.json"
    if not manifest_path.is_file():
        return {"ok": False, "error": "missing sha256.json"}
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict) or not manifest:
        return {"ok": False, "error": "manifest must be non-empty object"}

    actual_files = sorted(
        p for p in root.rglob("*")
        if p.is_file() and p != manifest_path
    )
    actual_keys = {
        manifest_key_for_artifact_path(p.relative_to(root).as_posix())
        for p in actual_files
    }
    manifest_keys = set(manifest)
    missing_from_manifest = sorted(actual_keys - manifest_keys)
    extra_in_manifest = sorted(manifest_keys - actual_keys)
    hash_mismatches = []
    for p in actual_files:
        rel = p.relative_to(root).as_posix()
        key = manifest_key_for_artifact_path(rel)
        if key in manifest:
            got = sha256_bytes(p.read_bytes())
            if got != manifest[key]:
                hash_mismatches.append(
                    {"path": rel, "manifest_key": key, "expected": manifest[key], "got": got}
                )
    mandatory_missing = sorted(
        x for x in MANDATORY_EVIDENCE
        if not (root / "r223_attempt6_evidence" / x).is_file()
    )
    return {
        "ok": not missing_from_manifest and not extra_in_manifest
              and not hash_mismatches and not mandatory_missing,
        "manifest_entries": len(manifest),
        "actual_files_excluding_manifest": len(actual_files),
        "missing_from_manifest": missing_from_manifest,
        "extra_in_manifest": extra_in_manifest,
        "hash_mismatches": hash_mismatches,
        "mandatory_evidence_missing": mandatory_missing,
    }


def verify_frozen_blobs(root: Path) -> dict[str, Any]:
    observed = {}
    mismatches = []
    for rel, expected in EXPECTED_BLOBS.items():
        p = root / rel
        if not p.is_file():
            mismatches.append({"path": rel, "error": "missing"})
            continue
        got = git_blob_sha1(p.read_bytes())
        observed[rel] = got
        if got != expected:
            mismatches.append({"path": rel, "expected": expected, "got": got})
    return {"ok": not mismatches, "observed": observed, "mismatches": mismatches}


def verify_provenance(root: Path) -> dict[str, Any]:
    e = root / "r223_attempt6_evidence"
    problems = []

    if sha256_bytes((e / "parent-report.json").read_bytes()) != PARENT_REPORT_SHA256:
        problems.append("parent-report SHA256 mismatch")

    transform = read_json(e / "source_transform_guard.json")
    for key in (
        "candidate_equals_attempt1_after_docstring_and_terminal_lf_normalization",
        "candidate_equals_exact_preregistered_parent_transform",
        "formula_and_clamp_tokens_exact",
    ):
        if transform.get(key) is not True:
            problems.append(f"source transform guard false: {key}")
    if transform.get("target_access") is not False:
        problems.append("source transform target_access not false")
    if transform.get("candidate_git_blob_sha1") != EXPECTED_BLOBS[
        "methods/r223_estimator_v25_local_feed.py"
    ]:
        problems.append("candidate blob in source transform guard mismatch")

    static = read_json(e / "static_feed_identity.json")
    if static.get("constant_ratio_identity_exact") is not True:
        problems.append("static constant-ratio identity failed")
    if float(static.get("heterogeneous_mean_lambda_error", math.inf)) > 2e-15:
        problems.append("static heterogeneous mean-lambda error exceeds 2e-15")
    if static.get("all_finite") is not True:
        problems.append("static all_finite false")
    if static.get("clamp") != [0.5, 2.0]:
        problems.append("static clamp mismatch")

    if (e / "validate.exit").read_text().strip() != "0":
        problems.append("validate.exit != 0")
    if (e / "run.exit").read_text().strip() != "0":
        problems.append("run.exit != 0")

    compute = read_json(e / "compute_gate.json")
    if compute.get("private") is not False or compute.get("visibility") != "public":
        problems.append("free/public compute gate mismatch")
    if compute.get("runs_on") != "ubuntu-24.04":
        problems.append("runner label mismatch")
    if compute.get("larger_runner_requested") is not False:
        problems.append("larger runner requested")
    if compute.get("verified_free_existing_compute") is not True:
        problems.append("compute not verified free/existing")

    env = (e / "environment.txt").read_text(encoding="utf-8")
    for token in ("numpy 2.4.6", "flopscope_distribution 0.12.1", "whestbench_distribution 0.16.1"):
        if token not in env:
            problems.append(f"environment missing {token!r}")

    return {"ok": not problems, "problems": problems}


def compare_normalized_parent(
    normalized: dict[str, Any], parent_report: dict[str, Any]
) -> dict[str, Any]:
    nr = normalized["per_network"]
    pr = parent_report["results"]["per_mlp"]
    problems = []
    if len(nr) != 100 or len(pr) != 100:
        problems.append(f"row counts normalized={len(nr)} raw={len(pr)}")
    for i, (n, p) in enumerate(zip(nr, pr)):
        if n["name"] != p["mlp_name"] or i != int(p["mlp_index"]):
            problems.append(f"identity mismatch at row {i}")
            continue
        if not close(n["final_mse"], p["final_layer_mse"]):
            problems.append(f"MSE mismatch at row {i}")
        if int(n["measured_flops"]) != int(p["flops_used"]):
            problems.append(f"FLOPs mismatch at row {i}")
        if not close(n["official_adjusted_score"], p["adjusted_final_layer_score"]):
            problems.append(f"adjusted mismatch at row {i}")
        if bool(n["failure_reasons"]) != is_failed(p):
            problems.append(f"failure mismatch at row {i}")
    return {"ok": not problems, "problems": problems[:50], "problem_count": len(problems)}


def apply_frozen_gates(
    parent_report: dict[str, Any],
    candidate_report: dict[str, Any],
    *,
    provenance_ok: bool,
    observed_candidate_panel_runs: int,
) -> dict[str, Any]:
    pr = parent_report["results"]["per_mlp"]
    cr = candidate_report["results"]["per_mlp"]
    pds = parent_report["run_config"]["dataset"]["sha256"]
    cds = candidate_report["run_config"]["dataset"]["sha256"]

    deltas = [official_score(p) - official_score(c) for p, c in zip(pr, cr)]
    improved = sum(official_score(c) < official_score(p) for p, c in zip(pr, cr))
    failures = sum(is_failed(r) for r in cr)
    cmse = mean([float(r["final_layer_mse"]) for r in cr])
    cscore = mean([official_score(r) for r in cr])
    ccompute = mean([float(r["effective_compute"]) for r in cr])
    ccb = ccompute / BUDGET
    dmean = mean(deltas)
    dse = paired_se(deltas)
    maxres = max(float(r["residual_wall_time_s"]) for r in cr)

    gates = {
        "exact_100_name_order_identity":
            row_identity(pr, cr)
            and names_sha(pr) == EXPECTED_NAMES_SHA
            and names_sha(cr) == EXPECTED_NAMES_SHA,
        "dataset_sha_identical":
            pds == EXPECTED_DATASET_SHA and cds == EXPECTED_DATASET_SHA,
        "candidate_failures_zero": failures == 0,
        "candidate_mean_raw_mse_lt_parent": cmse < PARENT_MSE,
        "candidate_mean_adjusted_le_0p995_parent": cscore <= TARGET_SCORE,
        "improves_at_least_55_of_100": improved >= 55,
        "paired_delta_mean_gt_2se": dmean > 2.0 * dse,
        "candidate_mean_cb_le_parent_plus_1e_5": ccb <= PARENT_CB + 1e-5,
        "max_residual_lt_0p4": maxres < 0.4,
        "exact_candidate_source_config_provenance": bool(provenance_ok),
        "only_one_candidate_panel_run": observed_candidate_panel_runs == 1,
    }
    return {
        "gates": gates,
        "development_go": all(gates.values()),
        "candidate": {
            "mean_raw_mse": cmse,
            "mean_adjusted_score": cscore,
            "mean_effective_compute": ccompute,
            "mean_c_over_b": ccb,
            "failures": failures,
            "max_residual_s": maxres,
        },
        "paired": {
            "improved_networks": improved,
            "delta_mean_parent_minus_candidate": dmean,
            "delta_se": dse,
            "delta_mean_over_se": (dmean / dse if dse else None),
        },
    }


def verify_zip(
    zip_path: Path,
    *,
    expected_zip_sha256: str,
    normalized_parent_path: Path,
    workflow_path: Path,
    observed_candidate_panel_runs: int,
) -> dict[str, Any]:
    zip_sha = sha256_bytes(zip_path.read_bytes())
    result: dict[str, Any] = {
        "schema": "arc.whitebox.r240.r223_attempt6_postflight.v1",
        "artifact_zip_sha256": zip_sha,
        "expected_artifact_zip_sha256": expected_zip_sha256,
        "zip_digest_ok": zip_sha == expected_zip_sha256,
        "expected_artifact_name": EXPECTED_ARTIFACT_NAME,
        "r223_run_id": EXPECTED_CANDIDATE_RUN_ID,
    }
    if not result["zip_digest_ok"]:
        result["verdict"] = "PROTOCOL_INVALID"
        return result

    workflow_blob = git_blob_sha1(workflow_path.read_bytes())
    result["workflow_blob"] = workflow_blob
    result["workflow_blob_ok"] = workflow_blob == EXPECTED_WORKFLOW_BLOB

    normalized_bytes = normalized_parent_path.read_bytes()
    result["normalized_parent_sha256"] = sha256_bytes(normalized_bytes)
    result["normalized_parent_sha256_ok"] = (
        result["normalized_parent_sha256"] == PARENT_NORMALIZED_SHA256
    )

    with tempfile.TemporaryDirectory(prefix="r240-") as td:
        root = Path(td)
        with zipfile.ZipFile(zip_path) as zf:
            bad_member = next(
                (
                    n for n in zf.namelist()
                    if Path(n).is_absolute() or ".." in Path(n).parts
                ),
                None,
            )
            if bad_member:
                result["archive_safe_paths"] = False
                result["archive_bad_member"] = bad_member
                result["verdict"] = "PROTOCOL_INVALID"
                return result
            zf.extractall(root)
        result["archive_safe_paths"] = True

        manifest = verify_manifest(root)
        blobs = verify_frozen_blobs(root)
        result["manifest"] = manifest
        result["frozen_blobs"] = blobs

        e = root / "r223_attempt6_evidence"
        if not (e / "candidate-report.json").is_file() or not (e / "parent-report.json").is_file():
            result["verdict"] = "NOT_MEASURABLE_MISSING_REPORT"
            return result

        parent = read_json(e / "parent-report.json")
        candidate = read_json(e / "candidate-report.json")
        normalized = json.loads(normalized_bytes.decode("utf-8"))

        parent_scores = verify_report_scores(parent)
        candidate_scores = verify_report_scores(candidate)
        normalized_parent = compare_normalized_parent(normalized, parent)
        provenance = verify_provenance(root)

        result["parent_score_recompute"] = parent_scores
        result["candidate_score_recompute"] = candidate_scores
        result["normalized_parent_match"] = normalized_parent
        result["provenance"] = provenance

        provenance_ok = all(
            [
                manifest.get("ok", False),
                blobs.get("ok", False),
                provenance.get("ok", False),
                result["workflow_blob_ok"],
                result["normalized_parent_sha256_ok"],
                not parent_scores["row_score_mismatches"],
                parent_scores["aggregate_adjusted_matches"],
                not candidate_scores["row_score_mismatches"],
                candidate_scores["aggregate_adjusted_matches"],
                normalized_parent["ok"],
            ]
        )

        frozen = apply_frozen_gates(
            parent,
            candidate,
            provenance_ok=provenance_ok,
            observed_candidate_panel_runs=observed_candidate_panel_runs,
        )
        result["frozen_gate_recompute"] = frozen
        result["verdict"] = (
            "R240_INDEPENDENT_DEVELOPMENT_GO"
            if frozen["development_go"]
            else "R240_INDEPENDENT_DEVELOPMENT_NO_GO"
        )
        result["competition_claim"] = (
            "NONE: same exposed mini-100 development panel only; no leaderboard, "
            "holdout, scorer or submission claim."
        )
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact-zip", type=Path, required=True)
    ap.add_argument("--expected-zip-sha256", required=True)
    ap.add_argument("--normalized-parent", type=Path, required=True)
    ap.add_argument("--workflow", type=Path, required=True)
    ap.add_argument("--observed-candidate-panel-runs", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    out = verify_zip(
        args.artifact_zip,
        expected_zip_sha256=args.expected_zip_sha256,
        normalized_parent_path=args.normalized_parent,
        workflow_path=args.workflow,
        observed_candidate_panel_runs=args.observed_candidate_panel_runs,
    )
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("frozen_blobs",)}, sort_keys=True))


if __name__ == "__main__":
    main()
