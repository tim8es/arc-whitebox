#!/usr/bin/env python3
"""Independent offline verifier for the frozen R218 six-block crossover artifact.

R234 prepares this verifier only. It never launches whest/estimators and never accesses
holdout data. R220 may run it after R218 is COMPLETE against the immutable artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import re
import statistics

BLOCKS = ["U", "C0", "C1", "C1", "C0", "U"]
PROTOCOL_SHA256 = "40d7153775efcc882410ff414a909ab6f6bab24193ecb2d746d7acdab33f6968"
DATASET_SHA256 = "264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"
ESTIMATOR_SHA256 = "86d9ca9b28e6fe2b6c74750a0b6ae4bba4c14f742ddc3f5f56bc7fb4ec9d8e27"
FLOP_BUDGET = 2199023255552
RESIDUAL_LIMIT = 0.4
EXPECTED_SHAPE = (16, 1024)
FAIL_KEYS = (
    "budget_exhausted",
    "combined_budget_exhausted",
    "time_exhausted",
    "residual_wall_time_exhausted",
)
GO = {
    "primary_delta_s_min": 0.020,
    "cpu0_slower_count_min": 35,
    "failure_difference_min": 10,
}
REQUIRED_THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}


def read_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_gate(gates, name, ok, detail=None):
    gates[name] = {"pass": bool(ok)}
    if detail is not None:
        gates[name]["detail"] = detail


def parse_env(path: pathlib.Path):
    out = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k] = v
    return out


def expand_cpuset(spec: str):
    cpus = set()
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            a, b = token.split("-", 1)
            cpus.update(range(int(a), int(b) + 1))
        else:
            cpus.add(int(token))
    return cpus


def taskset_cpus(text: str):
    m = re.search(r"affinity list:\s*([^\n]+)", text)
    if not m:
        return None
    try:
        return expand_cpuset(m.group(1).strip())
    except Exception:
        return None


def lscpu_identity(path: pathlib.Path):
    obj = read_json(path)
    values = {}
    for item in obj.get("lscpu", []):
        field = str(item.get("field", "")).rstrip(":")
        values[field] = item.get("data")
    keys = (
        "Architecture", "CPU(s)", "Vendor ID", "Model name", "CPU family",
        "Model", "Stepping", "Socket(s)", "Core(s) per socket",
        "Thread(s) per core", "NUMA node(s)",
    )
    return {k: values.get(k) for k in keys}


def normalize_report_rows(report, block_index, condition):
    rows = []
    for i, x in enumerate(report["results"]["per_mlp"]):
        reasons = [k for k in FAIL_KEYS if x.get(k)]
        if x.get("traceback"):
            reasons.append("traceback")
        rows.append({
            "block_index": block_index,
            "condition": condition,
            "mlp_index": i,
            "mlp_name": x.get("mlp_name"),
            "final_mse": x.get("final_layer_mse"),
            "measured_flops": x.get("flops_used"),
            "residual_wall_time_s": x.get("residual_wall_time_s"),
            "wall_time_s": x.get("wall_time_s"),
            "official_adjusted_score": x.get("adjusted_final_layer_score"),
            "status": "failed" if reasons else "ok",
            "failure_reasons": reasons,
        })
    return rows


def summary(xs):
    vals = [float(x) for x in xs]
    return {
        "n": len(vals),
        "mean": statistics.mean(vals),
        "median": statistics.median(vals),
        "min": min(vals),
        "max": max(vals),
        "sd": statistics.stdev(vals) if len(vals) > 1 else 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact-dir", required=True, type=pathlib.Path)
    ap.add_argument("--protocol", required=True, type=pathlib.Path)
    ap.add_argument("--expected-panel", required=True, type=pathlib.Path)
    ap.add_argument(
        "--actions-evidence",
        type=pathlib.Path,
        help=(
            "Optional R220-produced JSON from independent GitHub Actions inspection. "
            "Final GO/NO-GO is withheld until this is supplied and validates same run/job."
        ),
    )
    ap.add_argument("--out", required=True, type=pathlib.Path)
    args = ap.parse_args()

    root = args.artifact_dir
    gates = {}
    protocol = read_json(args.protocol)
    expected = read_json(args.expected_panel)

    add_gate(gates, "protocol_sha256", sha256(args.protocol) == PROTOCOL_SHA256)
    add_gate(gates, "protocol_block_sequence", protocol.get("design", {}).get("block_sequence") == BLOCKS)
    add_gate(gates, "protocol_evaluations_300", protocol.get("design", {}).get("evaluations") == 300)
    add_gate(gates, "protocol_flop_budget", protocol.get("design", {}).get("flop_budget") == FLOP_BUDGET)
    add_gate(gates, "protocol_residual_limit", protocol.get("design", {}).get("residual_wall_time_limit_s") == RESIDUAL_LIMIT)
    add_gate(gates, "protocol_source_hash", protocol.get("contract_gates", {}).get("source_sha256") == ESTIMATOR_SHA256)
    add_gate(gates, "protocol_dataset_hash", protocol.get("contract_gates", {}).get("dataset_sha256") == DATASET_SHA256)

    panel = expected.get("panel", [])
    expected_names = [x.get("mlp_name") for x in panel]
    expected_flops = [int(x.get("measured_flops")) for x in panel]
    add_gate(gates, "expected_panel_50", len(panel) == 50)
    add_gate(gates, "expected_panel_indices", [x.get("mlp_index") for x in panel] == list(range(50)))
    add_gate(gates, "expected_dataset_hash", expected.get("dataset", {}).get("sha256") == DATASET_SHA256)
    add_gate(gates, "expected_source_hash", expected.get("source", {}).get("sha256") == ESTIMATOR_SHA256)

    manifest_path = root / "sha256.json"
    manifest_ok = manifest_path.is_file()
    manifest_errors = []
    manifest = {}
    if manifest_ok:
        manifest = read_json(manifest_path)
        for rel, digest in sorted(manifest.items()):
            p = root / rel
            if not p.is_file():
                manifest_errors.append(f"missing:{rel}")
            elif sha256(p) != digest:
                manifest_errors.append(f"hash:{rel}")
    add_gate(gates, "artifact_manifest", manifest_ok and not manifest_errors, manifest_errors)

    preflight_path = root / "preflight.json"
    preflight = read_json(preflight_path) if preflight_path.is_file() else {}
    add_gate(gates, "preflight_present", bool(preflight))
    add_gate(gates, "preflight_all_pass", preflight.get("all_pass") is True)
    pgates = preflight.get("gates", {})
    add_gate(gates, "preflight_all_named_gates_true", bool(pgates) and all(pgates.values()))
    allowed = set(preflight.get("allowed_cpu_affinity", []))
    add_gate(gates, "preflight_cpu0_cpu1_allowed", 0 in allowed and 1 in allowed, sorted(allowed))
    add_gate(gates, "preflight_v26_strassen", preflight.get("V26_STRASSEN") == "4")
    add_gate(
        gates,
        "preflight_thread_env",
        all(preflight.get("thread_env", {}).get(k) == v for k, v in REQUIRED_THREAD_ENV.items()),
        preflight.get("thread_env"),
    )

    env_path = root / "runner_env.txt"
    runner_env = parse_env(env_path) if env_path.is_file() else {}
    add_gate(gates, "runner_env_present", bool(runner_env))
    github = preflight.get("github", {})
    for key in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_JOB", "RUNNER_NAME"):
        add_gate(
            gates,
            f"runner_env_matches_preflight_{key}",
            bool(github.get(key)) and runner_env.get(key) == github.get(key),
            {"preflight": github.get(key), "runner_env": runner_env.get(key)},
        )

    all_rows = []
    block_summaries = []
    lscpu_identities = []
    block_affinities = []
    for bi, condition in enumerate(BLOCKS, 1):
        report_path = root / f"block_{bi:02d}_{condition}_report.json"
        report = read_json(report_path) if report_path.is_file() else None
        add_gate(gates, f"block_{bi:02d}_report_present", report is not None)
        if report is None:
            continue

        rows = normalize_report_rows(report, bi, condition)
        all_rows.extend(rows)
        cfg = report.get("run_config", {})
        ds = cfg.get("dataset", {})
        names = [r["mlp_name"] for r in rows]
        flops = [int(r["measured_flops"]) for r in rows]

        add_gate(gates, f"block_{bi:02d}_count_50", len(rows) == 50)
        add_gate(gates, f"block_{bi:02d}_name_order", names == expected_names)
        add_gate(gates, f"block_{bi:02d}_flops", flops == expected_flops)
        add_gate(gates, f"block_{bi:02d}_dataset_hash", ds.get("sha256") == DATASET_SHA256)
        add_gate(gates, f"block_{bi:02d}_flop_budget", cfg.get("flop_budget") == FLOP_BUDGET)
        add_gate(gates, f"block_{bi:02d}_residual_limit", cfg.get("residual_wall_time_limit_s") == RESIDUAL_LIMIT)
        add_gate(gates, f"block_{bi:02d}_shape", (cfg.get("depth"), cfg.get("width")) == EXPECTED_SHAPE)
        add_gate(gates, f"block_{bi:02d}_whestbench", report.get("whestbench_version") == "0.16.1")

        td = root / "telemetry" / f"block_{bi:02d}_{condition}"
        aff_path = td / "orchestrator_affinity.json"
        taskset_path = td / "child_taskset.txt"
        lscpu_path = td / "lscpu.json"
        add_gate(gates, f"block_{bi:02d}_telemetry_dir", td.is_dir())
        add_gate(gates, f"block_{bi:02d}_orchestrator_affinity_present", aff_path.is_file())
        add_gate(gates, f"block_{bi:02d}_child_taskset_present", taskset_path.is_file())
        add_gate(gates, f"block_{bi:02d}_lscpu_present", lscpu_path.is_file())

        orchestrator_allowed = set()
        if aff_path.is_file():
            orchestrator_allowed = set(read_json(aff_path).get("sched_getaffinity", []))
            add_gate(
                gates,
                f"block_{bi:02d}_orchestrator_allowed_matches_preflight",
                orchestrator_allowed == allowed,
                {"block": sorted(orchestrator_allowed), "preflight": sorted(allowed)},
            )
        child = taskset_cpus(taskset_path.read_text(encoding="utf-8", errors="replace")) if taskset_path.is_file() else None
        block_affinities.append({"block_index": bi, "condition": condition, "child_cpus": sorted(child) if child is not None else None})
        if condition == "C0":
            affinity_ok = child == {0}
        elif condition == "C1":
            affinity_ok = child == {1}
        else:
            affinity_ok = child == allowed and 0 in child and 1 in child if child is not None else False
        add_gate(gates, f"block_{bi:02d}_child_affinity_{condition}", affinity_ok, sorted(child) if child is not None else None)

        if lscpu_path.is_file():
            lscpu_identities.append(lscpu_identity(lscpu_path))

        failures = sum(r["status"] == "failed" for r in rows)
        block_summaries.append({
            "block_index": bi,
            "condition": condition,
            "failures": failures,
            "mean_residual_wall_time_s": statistics.mean(float(r["residual_wall_time_s"]) for r in rows),
            "median_residual_wall_time_s": statistics.median(float(r["residual_wall_time_s"]) for r in rows),
            "official_adjusted_score_from_report": report.get("results", {}).get("adjusted_final_layer_score"),
            "report_sha256": sha256(report_path),
        })

    add_gate(gates, "exact_300_rows", len(all_rows) == 300, len(all_rows))
    add_gate(
        gates,
        "six_lscpu_identities_present",
        len(lscpu_identities) == 6,
        len(lscpu_identities),
    )
    add_gate(
        gates,
        "stable_lscpu_identity_across_blocks",
        len(lscpu_identities) == 6 and all(x == lscpu_identities[0] for x in lscpu_identities[1:]),
        lscpu_identities,
    )

    counts = {c: sum(r["condition"] == c for r in all_rows) for c in ("U", "C0", "C1")}
    add_gate(gates, "two_blocks_each_condition", counts == {"U": 100, "C0": 100, "C1": 100}, counts)

    per_condition = {}
    per_mlp = {}
    if len(all_rows) == 300 and counts == {"U": 100, "C0": 100, "C1": 100}:
        for c in ("U", "C0", "C1"):
            rr = [r for r in all_rows if r["condition"] == c]
            per_condition[c] = {
                "residual_wall_time_s": summary([r["residual_wall_time_s"] for r in rr]),
                "failures_across_two_blocks": sum(r["status"] == "failed" for r in rr),
                "mean_official_adjusted_score": statistics.mean(float(r["official_adjusted_score"]) for r in rr),
            }
        for i in range(50):
            entry = {"mlp_index": i, "mlp_name": expected_names[i]}
            for c in ("U", "C0", "C1"):
                rr = [r for r in all_rows if r["condition"] == c and r["mlp_index"] == i]
                if len(rr) != 2:
                    add_gate(gates, f"mlp_{i:02d}_{c}_two_observations", False, len(rr))
                    continue
                add_gate(gates, f"mlp_{i:02d}_{c}_two_observations", True)
                entry[f"{c}_mean_residual_s"] = statistics.mean(float(r["residual_wall_time_s"]) for r in rr)
            per_mlp[i] = entry

    analysis = {}
    if len(per_mlp) == 50 and all("C0_mean_residual_s" in x and "C1_mean_residual_s" in x and "U_mean_residual_s" in x for x in per_mlp.values()):
        deltas = [per_mlp[i]["C0_mean_residual_s"] - per_mlp[i]["C1_mean_residual_s"] for i in range(50)]
        primary = statistics.median(deltas)
        cpu0_slower = sum(x > 0 for x in deltas)
        c0_fail = per_condition["C0"]["failures_across_two_blocks"]
        c1_fail = per_condition["C1"]["failures_across_two_blocks"]
        failure_difference = c0_fail - c1_fail
        analysis = {
            "primary_delta_s": primary,
            "cpu0_slower_count": cpu0_slower,
            "c0_failures_across_two_blocks": c0_fail,
            "c1_failures_across_two_blocks": c1_fail,
            "failure_difference": failure_difference,
            "per_mlp_C0_minus_C1_s": deltas,
            "thresholds": GO,
        }

    owner_receipt_path = root / "R218_RECEIPT.json"
    owner_receipt = read_json(owner_receipt_path) if owner_receipt_path.is_file() else {}
    add_gate(gates, "owner_receipt_present", bool(owner_receipt))
    if owner_receipt:
        add_gate(gates, "owner_receipt_protocol_hash", owner_receipt.get("protocol_sha256") == PROTOCOL_SHA256)
        add_gate(gates, "owner_receipt_source_hash", owner_receipt.get("source_sha256") == ESTIMATOR_SHA256)
        add_gate(gates, "owner_receipt_dataset_hash", owner_receipt.get("dataset_sha256") == DATASET_SHA256)
        add_gate(gates, "owner_receipt_300_rows", len(owner_receipt.get("per_observation", [])) == 300)
        if analysis:
            oa = owner_receipt.get("analysis", {})
            owner_primary = oa.get("primary_delta_s")
            add_gate(
                gates,
                "owner_primary_delta_matches",
                isinstance(owner_primary, (int, float))
                and math.isclose(float(owner_primary), analysis["primary_delta_s"], rel_tol=0.0, abs_tol=1e-12),
                owner_primary,
            )
            add_gate(gates, "owner_cpu0_slower_count_matches", oa.get("cpu0_slower_count") == analysis["cpu0_slower_count"])
            add_gate(gates, "owner_failure_difference_matches", oa.get("failure_difference") == analysis["failure_difference"])

    actions_ok = False
    actions_evidence = None
    if args.actions_evidence:
        actions_evidence = read_json(args.actions_evidence)
        # R220 should generate this from the GitHub Actions run/job API, not from owner receipt.
        actions_ok = (
            str(actions_evidence.get("run_id")) == str(github.get("GITHUB_RUN_ID"))
            and str(actions_evidence.get("run_attempt")) == str(github.get("GITHUB_RUN_ATTEMPT"))
            and actions_evidence.get("job_name") == github.get("GITHUB_JOB") == "crossover"
            and actions_evidence.get("single_crossover_job_verified") is True
            and actions_evidence.get("executor_commit") == "85f5ba13236aad07bf31436b356cfa2a3744ad33"
        )
    add_gate(
        gates,
        "external_actions_same_job_provenance",
        actions_ok,
        "Required for final causal verdict; R234 intentionally does not fabricate or poll this evidence.",
    )

    contract_gate_names = [k for k in gates if k != "external_actions_same_job_provenance"]
    artifact_contract_ok = all(gates[k]["pass"] for k in contract_gate_names)
    if not artifact_contract_ok:
        decision = "PROTOCOL_INVALID"
    elif not actions_ok:
        decision = "PENDING_EXTERNAL_ACTIONS_PROVENANCE"
    elif not analysis:
        decision = "PROTOCOL_INVALID"
    else:
        go = (
            analysis["primary_delta_s"] >= GO["primary_delta_s_min"]
            and analysis["cpu0_slower_count"] >= GO["cpu0_slower_count_min"]
            and analysis["failure_difference"] >= GO["failure_difference_min"]
        )
        decision = "GO_CPU0_SPECIFIC" if go else "NO_GO_CPU0_SPECIFIC"

    out = {
        "schema": "arc.whitebox.r234.r218_postflight_verifier.v1",
        "decision": decision,
        "artifact_contract_ok": artifact_contract_ok,
        "external_actions_same_job_provenance_ok": actions_ok,
        "gates": gates,
        "block_sequence": BLOCKS,
        "block_summaries": block_summaries,
        "block_affinities": block_affinities,
        "condition_summaries": per_condition,
        "per_mlp": [per_mlp[i] for i in sorted(per_mlp)],
        "analysis": analysis,
        "predeclared_go_no_go": {
            "GO_CPU0_SPECIFIC": "all gates pass AND primary_delta_s>=0.020 AND cpu0_slower_count>=35 AND failure_difference>=10",
            "NO_GO_CPU0_SPECIFIC": "all gates pass and any GO threshold fails",
            "PROTOCOL_INVALID": "any contract/provenance gate fails",
        },
        "scope": "exposed public-panel runtime diagnostic; not independent quality confirmation",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "analysis": analysis}, sort_keys=True))


if __name__ == "__main__":
    main()
