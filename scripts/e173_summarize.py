#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from methods.e173_starter_ago import analytic_cost_receipt


ROOT = Path("e173_artifacts")
PARENT_REPORT = ROOT / "parent_report.json"
AGO_REPORT = ROOT / "ago_report.json"
PARENT_VALIDATE = ROOT / "parent_validate.json"
AGO_VALIDATE = ROOT / "ago_validate.json"
VECTOR_MANIFEST = Path("e173_vector_manifest.json")
SUMMARY_PATH = ROOT / "E173_SUMMARY.json"

CAP_FLOPS = 296_868_139_499
EXPECTED_N = 5
MSE_ABS_TOL = 5.0e-10
MSE_REL_TOL = 5.0e-5


def _read_json(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size == 0:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_int(path: Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def _sha(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _per_mlp(report: dict) -> list[dict]:
    return list(report.get("results", {}).get("per_mlp", []) or [])


def _failure_free(item: dict) -> bool:
    flags = (
        "budget_exhausted",
        "time_exhausted",
        "residual_wall_time_exhausted",
        "combined_budget_exhausted",
    )
    if any(bool(item.get(k, False)) for k in flags):
        return False
    code = item.get("error_code")
    if code not in (None, "", "none", "None"):
        return False
    return True


def _mse_match(captured: float, official: float) -> dict:
    abs_err = abs(captured - official)
    rel_err = abs_err / max(abs(official), 2.0**-500)
    return {
        "captured": captured,
        "official": official,
        "abs_error": abs_err,
        "relative_error": rel_err,
        "pass": bool(abs_err <= MSE_ABS_TOL or rel_err <= MSE_REL_TOL),
    }


def _report_summary(report: dict) -> dict:
    cfg = report.get("run_config", {})
    res = report.get("results", {})
    per = _per_mlp(report)
    return {
        "schema_version": report.get("schema_version"),
        "whestbench_version": report.get("whestbench_version"),
        "dataset": cfg.get("dataset"),
        "n_mlps_requested": cfg.get("n_mlps"),
        "width": cfg.get("width"),
        "depth": cfg.get("depth"),
        "flop_budget": cfg.get("flop_budget"),
        "wall_time_limit_s": cfg.get("wall_time_limit_s"),
        "residual_wall_time_limit_s": cfg.get("residual_wall_time_limit_s"),
        "reported_n_mlps": len(per),
        "mean_final_layer_mse": res.get("final_layer_mse"),
        "mean_all_layers_mse": res.get("all_layers_mse"),
        "mean_effective_compute": res.get("mean_effective_compute"),
        "mean_compute_utilization": res.get("mean_compute_utilization"),
        "n_failed_mlps": res.get("n_failed_mlps"),
        "failure_breakdown": res.get("failure_breakdown"),
    }


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)

    parent_report = _read_json(PARENT_REPORT)
    ago_report = _read_json(AGO_REPORT)
    parent_validate = _read_json(PARENT_VALIDATE)
    ago_validate = _read_json(AGO_VALIDATE)
    manifest = _read_json(VECTOR_MANIFEST)

    parent_exit = _read_int(ROOT / "parent_run.exit")
    ago_exit = _read_int(ROOT / "ago_run.exit")
    parent_validate_exit = _read_int(ROOT / "parent_validate.exit")
    ago_validate_exit = _read_int(ROOT / "ago_validate.exit")
    focused_tests_exit = _read_int(ROOT / "focused_tests.exit")
    capture_exit = _read_int(ROOT / "capture.exit")

    parent_items = _per_mlp(parent_report)
    ago_items = _per_mlp(ago_report)
    parent_by_name = {str(x.get("mlp_name")): x for x in parent_items}
    ago_by_name = {str(x.get("mlp_name")): x for x in ago_items}

    records = list(manifest.get("records", []) or [])
    vector_names = [str(r.get("mlp_name")) for r in records]
    official_parent_names = [str(x.get("mlp_name")) for x in parent_items]
    official_ago_names = [str(x.get("mlp_name")) for x in ago_items]

    per_mlp: list[dict] = []
    all_reconcile = True
    all_payloads = True
    all_replay = True
    all_flops = True
    all_failures_clear = True

    for record in records:
        name = str(record["mlp_name"])
        p = parent_by_name.get(name)
        a = ago_by_name.get(name)
        if p is None or a is None:
            all_reconcile = False
            all_failures_clear = False
            per_mlp.append(
                {
                    "mlp_name": name,
                    "error": "missing matching official per-MLP record",
                }
            )
            continue

        captured_parent = float(record["parent_final_mse"])
        captured_ago = float(record["ago_final_mse"])
        official_parent = float(p.get("final_layer_mse"))
        official_ago = float(a.get("final_layer_mse"))

        parent_match = _mse_match(captured_parent, official_parent)
        ago_match = _mse_match(captured_ago, official_ago)
        reconcile = bool(parent_match["pass"] and ago_match["pass"])
        all_reconcile = all_reconcile and reconcile

        payloads = list(record.get("payloads", []) or [])
        payload_ok = len(payloads) == 7
        for entry in payloads:
            path = Path(str(entry["path"]))
            if not path.is_file():
                payload_ok = False
                continue
            loaded = np.load(path, allow_pickle=False)
            if list(loaded.shape) != list(entry["shape"]):
                payload_ok = False
            if str(loaded.dtype) != str(entry["dtype"]):
                payload_ok = False
            if _sha(path) != entry["file_sha256"]:
                payload_ok = False
            raw = hashlib.sha256(
                np.ascontiguousarray(loaded).tobytes()
            ).hexdigest()
            if raw != entry["raw_array_sha256"]:
                payload_ok = False

        all_payloads = all_payloads and payload_ok
        replay_ok = bool(
            record.get("parent_replay_bitwise_exact")
            and record.get("ago_replay_bitwise_exact")
        )
        all_replay = all_replay and replay_ok

        p_flops = int(p.get("flops_used", 0) or 0)
        a_flops = int(a.get("flops_used", 0) or 0)
        flop_ok = bool(
            0 < p_flops <= CAP_FLOPS
            and 0 < a_flops <= CAP_FLOPS
        )
        all_flops = all_flops and flop_ok

        failure_ok = bool(_failure_free(p) and _failure_free(a))
        all_failures_clear = all_failures_clear and failure_ok

        delta = official_parent - official_ago
        per_mlp.append(
            {
                "mlp_index": int(record["mlp_index"]),
                "mlp_id": int(record["mlp_id"]),
                "mlp_name": name,
                "input_mlp_seed": int(record["input_mlp_seed"]),
                "parent": {
                    "official_final_layer_mse": official_parent,
                    "captured_final_layer_mse": captured_parent,
                    "coordinate_mse_se": float(
                        record["parent_final_mse_coordinate_se"]
                    ),
                    "flops_used": p_flops,
                    "effective_compute": p.get("effective_compute"),
                    "wall_time_s": p.get("wall_time_s"),
                    "residual_wall_time_s": p.get(
                        "residual_wall_time_s"
                    ),
                    "failure_free": _failure_free(p),
                    "mse_reconciliation": parent_match,
                },
                "ago": {
                    "official_final_layer_mse": official_ago,
                    "captured_final_layer_mse": captured_ago,
                    "coordinate_mse_se": float(
                        record["ago_final_mse_coordinate_se"]
                    ),
                    "flops_used": a_flops,
                    "effective_compute": a.get("effective_compute"),
                    "wall_time_s": a.get("wall_time_s"),
                    "residual_wall_time_s": a.get(
                        "residual_wall_time_s"
                    ),
                    "failure_free": _failure_free(a),
                    "mse_reconciliation": ago_match,
                },
                "ago_over_parent": (
                    official_ago / official_parent
                    if official_parent > 0.0
                    else math.inf
                ),
                "paired_delta_parent_minus_ago": delta,
                "ago_improves": bool(delta > 0.0),
                "flop_gate": flop_ok,
                "payload_integrity": payload_ok,
                "replay": replay_ok,
                "parent_per_layer_mse": record[
                    "parent_per_layer_mse"
                ],
                "ago_per_layer_mse": record["ago_per_layer_mse"],
            }
        )

    official_pair_records = [
        x for x in per_mlp if "parent" in x and "ago" in x
    ]
    pvals = np.asarray(
        [
            x["parent"]["official_final_layer_mse"]
            for x in official_pair_records
        ],
        dtype=np.float64,
    )
    avals = np.asarray(
        [
            x["ago"]["official_final_layer_mse"]
            for x in official_pair_records
        ],
        dtype=np.float64,
    )
    deltas = pvals - avals

    mean_parent = float(np.mean(pvals)) if pvals.size else math.inf
    mean_ago = float(np.mean(avals)) if avals.size else math.inf
    ratio = (
        mean_ago / mean_parent
        if mean_parent > 0.0 and math.isfinite(mean_parent)
        else math.inf
    )
    improve_count = int(np.sum(deltas > 0.0)) if deltas.size else 0
    delta_mean = float(np.mean(deltas)) if deltas.size else -math.inf
    delta_se = (
        float(np.std(deltas, ddof=1) / math.sqrt(deltas.size))
        if deltas.size > 1
        else math.inf
    )

    parent_res = parent_report.get("results", {})
    ago_res = ago_report.get("results", {})
    no_failed_reports = bool(
        parent_res.get("n_failed_mlps") == 0
        and ago_res.get("n_failed_mlps") == 0
    )

    dataset_ok = bool(
        len(records) == EXPECTED_N
        and len(parent_items) == EXPECTED_N
        and len(ago_items) == EXPECTED_N
        and vector_names == official_parent_names
        and vector_names == official_ago_names
    )

    validation_ok = bool(
        parent_validate_exit == 0
        and ago_validate_exit == 0
        and parent_validate
        and ago_validate
    )

    analytic_cost = analytic_cost_receipt()

    gates = {
        "focused_tests_pass": focused_tests_exit == 0,
        "parent_validate_pass": parent_validate_exit == 0,
        "ago_validate_pass": ago_validate_exit == 0,
        "capture_pass": capture_exit == 0,
        "official_parent_run_exit_zero": parent_exit == 0,
        "official_ago_run_exit_zero": ago_exit == 0,
        "official_runs_exact_same_first_5_mini_mlps": dataset_ok,
        "zero_failed_mlps_both": no_failed_reports,
        "all_per_mlp_failure_flags_clear": all_failures_clear,
        "vector_payload_integrity_all": all_payloads,
        "deterministic_replay_all": all_replay,
        "captured_mse_matches_official_all": all_reconcile,
        "runtime_flops_le_0_135B_all_parent_and_ago": all_flops,
        "analytic_candidate_cost_le_0_135B": bool(
            analytic_cost["passes_cap"]
        ),
        "ago_improves_at_least_3_of_5": improve_count >= 3,
        "mean_ago_over_parent_mse_le_0_98": bool(
            math.isfinite(ratio) and ratio <= 0.98
        ),
        "paired_mean_parent_minus_ago_positive": delta_mean > 0.0,
        "no_external_submission_holdout_full_leaderboard": True,
    }

    go = bool(all(gates.values()))

    earliest_regression_layer = None
    aggregate_layer_parent = None
    aggregate_layer_ago = None
    if records:
        aggregate_layer_parent = np.mean(
            np.asarray(
                [r["parent_per_layer_mse"] for r in records],
                dtype=np.float64,
            ),
            axis=0,
        )
        aggregate_layer_ago = np.mean(
            np.asarray(
                [r["ago_per_layer_mse"] for r in records],
                dtype=np.float64,
            ),
            axis=0,
        )
        bad = np.flatnonzero(aggregate_layer_ago > aggregate_layer_parent)
        if bad.size:
            earliest_regression_layer = int(bad[0])

    if go:
        decision = "E173_OFFICIAL_LOCAL_MINI_GO_AGO"
        next_experiment = None
    else:
        decision = "E173_OFFICIAL_LOCAL_MINI_NO_GO"
        next_experiment = {
            "scope": "new separately-numbered synthetic mechanism experiment only",
            "full_split_forbidden": True,
            "new_public_mlps_forbidden": True,
            "earliest_layer_where_panel_ago_mse_exceeds_parent": (
                earliest_regression_layer
            ),
            "instruction": (
                "Use retained 5-MLP layerwise vectors to reproduce the earliest "
                "AGO-vs-parent layer-local regression synthetically before any "
                "wider benchmark run."
            ),
        }

    summary = {
        "schema": "arc.whitebox.e173.official_mini_integration.v1",
        "experiment": "E173",
        "decision": decision,
        "scientific_go": go,
        "pinned_scope": {
            "dataset": "hf://aicrowd/arc-whestbench-public-2026@v2-phase2",
            "split": "mini",
            "n_mlps": 5,
            "runner": "local",
            "flop_budget": 2**41,
            "flop_cap": CAP_FLOPS,
            "submission": False,
            "full": False,
            "holdout": False,
            "leaderboard_change": False,
        },
        "validation": {
            "parent_exit": parent_validate_exit,
            "ago_exit": ago_validate_exit,
            "parent_json_sha256": _sha(PARENT_VALIDATE),
            "ago_json_sha256": _sha(AGO_VALIDATE),
            "both_valid": validation_ok,
        },
        "reports": {
            "parent": _report_summary(parent_report),
            "ago": _report_summary(ago_report),
            "parent_report_sha256": _sha(PARENT_REPORT),
            "ago_report_sha256": _sha(AGO_REPORT),
        },
        "vector_manifest": {
            "path": str(VECTOR_MANIFEST),
            "sha256": _sha(VECTOR_MANIFEST),
            "record_count": len(records),
        },
        "per_mlp": per_mlp,
        "panel": {
            "mean_parent_final_layer_mse": mean_parent,
            "mean_ago_final_layer_mse": mean_ago,
            "ago_over_parent": ratio,
            "improvement_fraction": (
                1.0 - ratio if math.isfinite(ratio) else -math.inf
            ),
            "improve_count": improve_count,
            "paired_deltas": deltas.tolist(),
            "paired_delta_mean": delta_mean,
            "paired_delta_se": delta_se,
            "aggregate_parent_per_layer_mse": (
                None
                if aggregate_layer_parent is None
                else aggregate_layer_parent.tolist()
            ),
            "aggregate_ago_per_layer_mse": (
                None
                if aggregate_layer_ago is None
                else aggregate_layer_ago.tolist()
            ),
            "earliest_layer_where_ago_exceeds_parent": (
                earliest_regression_layer
            ),
        },
        "analytic_cost": analytic_cost,
        "gates": gates,
        "next_minimal_experiment_if_no_go": next_experiment,
    }

    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("E173_SUMMARY=" + json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
