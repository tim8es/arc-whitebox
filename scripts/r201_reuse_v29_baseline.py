#!/usr/bin/env python3
"""R201: normalize an existing V29 official report onto the E173 first-five panel.

No estimator is executed. This script only verifies and reuses immutable evidence.
Python standard library only.
"""
from __future__ import annotations
import argparse, hashlib, json, math, statistics, zipfile
from pathlib import Path

EXPECTED_ARTIFACT_SHA256 = "32c29ac79c5c59b841c88c6c274ed378daf2778a61d4344c7aa0b58f1da11681"
EXPECTED_REPORT_SHA256 = "76c496968b9a81dc1eae91e8204969c0dfe9d7f113dd46af0c0e7df82496a78b"
EXPECTED_DATASET_SHA256 = "264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"
EXPECTED_DATASET = "hf://aicrowd/arc-whestbench-public-2026@v2-phase2"
EXPECTED_NAMES = [
    "logan-fitzgerald", "william-graves", "raymond-barnes",
    "steven-rice", "sarah-kelley",
]
BUDGET = 2199023255552

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def official_score(row):
    if row["status"] == "failed":
        return float(row["official_adjusted_score"])
    return float(row["final_mse"]) * max(0.1, float(row["measured_flops"]) / float(row["budget_flops"]))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--e136-zip", type=Path, required=True)
    ap.add_argument("--e173-ago", type=Path, required=True)
    ap.add_argument("--normalizer-commit", required=True)
    ap.add_argument("--receipt-url", default="")
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()

    artifact_sha = sha256_file(args.e136_zip)
    if artifact_sha != EXPECTED_ARTIFACT_SHA256:
        raise SystemExit(f"artifact sha mismatch: {artifact_sha}")

    with zipfile.ZipFile(args.e136_zip) as z:
        report_bytes = z.read("report.json")
        report_sha = sha256_bytes(report_bytes)
        if report_sha != EXPECTED_REPORT_SHA256:
            raise SystemExit(f"report sha mismatch: {report_sha}")
        report = json.loads(report_bytes)
        env = z.read("environment.txt").decode("utf-8", "replace")

    ago = json.loads(args.e173_ago.read_text(encoding="utf-8"))
    cfg = report["run_config"]
    dset = cfg["dataset"]
    if dset["path"] != EXPECTED_DATASET or dset["sha256"] != EXPECTED_DATASET_SHA256:
        raise SystemExit("E136 dataset identity mismatch")
    if ago["panel"]["dataset"] != EXPECTED_DATASET or ago["panel"]["count"] != 5:
        raise SystemExit("E173 panel identity mismatch")
    if cfg["width"] != 1024 or cfg["depth"] != 16 or cfg["flop_budget"] != BUDGET:
        raise SystemExit("E136 shape/budget mismatch")
    if [r["mlp_name"] for r in report["results"]["per_mlp"][:5]] != EXPECTED_NAMES:
        raise SystemExit("E136 first-five order mismatch")
    if [r["name"] for r in ago["per_network"]] != EXPECTED_NAMES:
        raise SystemExit("E173 first-five order mismatch")
    if "flopscope 0.12.1" not in env:
        raise SystemExit("E136 meter mismatch")

    rows = []
    for src, panel_row in zip(report["results"]["per_mlp"][:5], ago["per_network"]):
        fail_reasons = []
        for key in ("budget_exhausted", "time_exhausted", "residual_wall_time_exhausted", "combined_budget_exhausted"):
            if src.get(key):
                fail_reasons.append(key)
        if src.get("traceback"):
            fail_reasons.append("traceback")
        status = "failed" if fail_reasons else "ok"
        row = {
            "budget_flops": BUDGET,
            "final_mse": float(src["final_layer_mse"]),
            "measured_flops": int(src["flops_used"]),
            "name": src["mlp_name"],
            "network_id": str(panel_row["network_id"]),
            "official_adjusted_score": float(src["adjusted_final_layer_score"]),
            "status": status,
            "target_sha256": panel_row["target_sha256"],
            "wall_time_s": float(src["wall_time_s"]),
            "residual_wall_time_s": float(src["residual_wall_time_s"]),
            "failure_reasons": fail_reasons,
        }
        expected = official_score(row)
        if not math.isclose(expected, row["official_adjusted_score"], rel_tol=1e-9, abs_tol=1e-18):
            raise SystemExit(f"official score mismatch for {row['name']}: {expected} != {row['official_adjusted_score']}")
        rows.append(row)

    normalized = {
        "attempt_id": "35544406064",
        "code_commit": "dff3dd65e9d2210e02418cca99e05556f6bf2c75",
        "evidence_level": "REUSED_IMMUTABLE_OFFICIAL_REPORT",
        "experiment_id": "R201",
        "hypothesis_id": "BASELINE-COMPARISON",
        "id": "R201-v29",
        "panel": dict(ago["panel"]),
        "parent_id": None,
        "per_network": rows,
        "receipt_url": args.receipt_url or None,
        "source": {
            "e136_workflow_run_id": 35544406064,
            "e136_job_id": 106167659295,
            "e136_artifact_id": 10617318650,
            "e136_artifact_sha256": EXPECTED_ARTIFACT_SHA256,
            "e136_report_sha256": EXPECTED_REPORT_SHA256,
            "e136_head_sha": "dff3dd65e9d2210e02418cca99e05556f6bf2c75",
            "v29_git_blob_sha1": "17df1a073a24f96c4705b04bcf61ef60fa06dd0c",
            "dataset_sha256": EXPECTED_DATASET_SHA256,
            "reuse_only": True,
            "new_scientific_run": False,
        },
    }

    v_scores = [official_score(r) for r in rows]
    a_scores = [
        float(r["final_mse"]) * max(0.1, float(r["measured_flops"]) / float(r["budget_flops"]))
        if r["status"] == "ok" else float(r["official_adjusted_score"])
        for r in ago["per_network"]
    ]
    deltas = [v - a for v, a in zip(v_scores, a_scores)]
    ok_v29 = [r["final_mse"] for r in rows if r["status"] == "ok"]
    comparison = {
        "v29_mean_raw_mse_all_rows": statistics.mean(r["final_mse"] for r in rows),
        "v29_mean_raw_mse_success_rows_only": statistics.mean(ok_v29),
        "v29_mean_official_adjusted_score": statistics.mean(v_scores),
        "v29_mean_measured_flops": statistics.mean(r["measured_flops"] for r in rows),
        "v29_failures": sum(r["status"] == "failed" for r in rows),
        "e173_ago_mean_raw_mse": statistics.mean(r["final_mse"] for r in ago["per_network"]),
        "e173_ago_mean_official_adjusted_score": statistics.mean(a_scores),
        "e173_ago_mean_measured_flops": statistics.mean(r["measured_flops"] for r in ago["per_network"]),
        "e173_ago_failures": sum(r["status"] == "failed" for r in ago["per_network"]),
        "v29_over_e173_ago_adjusted_score_ratio": statistics.mean(v_scores) / statistics.mean(a_scores),
        "e173_ago_improves_official_score_networks": sum(d > 0 for d in deltas),
        "paired_v29_minus_ago_score_mean": statistics.mean(deltas),
        "paired_v29_minus_ago_score_se": statistics.stdev(deltas) / math.sqrt(len(deltas)),
    }

    command = (
        "python scripts/r201_reuse_v29_baseline.py "
        "--e136-zip e136-followup-v29.zip "
        "--e173-ago research/results/E173-ago.json "
        f"--normalizer-commit {args.normalizer_commit} "
        f"--output {args.output.as_posix()} --receipt {args.receipt.as_posix()}"
    )
    receipt = {
        "schema": "arc.whitebox.r201.baseline_receipt.v1",
        "job_id": "R201",
        "owner": "baseline",
        "status": "COMPLETE",
        "mode": "EXISTING_EVIDENCE_REUSE",
        "command": command,
        "normalizer_commit": args.normalizer_commit,
        "budget": {
            "cap_usd": 100,
            "remaining_usd": None,
            "new_paid_runs_authorized": False,
            "paid_run_started": False,
        },
        "panel_bridge": {
            "dataset": EXPECTED_DATASET,
            "dataset_sha256": EXPECTED_DATASET_SHA256,
            "same_first_five_names_and_order": True,
            "target_hashes_from_pinned_e173_panel": True,
            "e173_result_id": "E173-ago",
        },
        "evidence": normalized["source"],
        "comparison": comparison,
        "per_network": rows,
        "conclusion": (
            "Comparable first-five V29 evidence already existed, so no duplicate experiment was run. "
            "V29 has four valid low-MSE rows but one official residual-time failure (william-graves), "
            "which dominates the five-network official adjusted-score mean. E173-AGO has zero failures."
        ),
    }
    dump(args.output, normalized)
    dump(args.receipt, receipt)
    print(json.dumps({
        "status": receipt["status"],
        "v29_failures": comparison["v29_failures"],
        "v29_mean_official_adjusted_score": comparison["v29_mean_official_adjusted_score"],
        "v29_mean_raw_mse_success_rows_only": comparison["v29_mean_raw_mse_success_rows_only"],
        "e173_ago_mean_official_adjusted_score": comparison["e173_ago_mean_official_adjusted_score"],
        "v29_over_e173_ago_adjusted_score_ratio": comparison["v29_over_e173_ago_adjusted_score_ratio"],
        "output": str(args.output),
        "receipt": str(args.receipt),
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
