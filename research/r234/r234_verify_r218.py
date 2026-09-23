#!/usr/bin/env python3
"""Fail-closed independent verifier for the frozen R218 six-block crossover.

R237 hardens the R234 verifier after the R236 independent audit. It never launches
whest/estimators and never accesses holdout data. R220 may run it only after R218 is
COMPLETE, against an independently downloaded immutable Actions artifact plus Actions
provenance evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import re
import statistics
import zipfile

BLOCKS = ["U", "C0", "C1", "C1", "C0", "U"]
PROTOCOL_SHA256 = "40d7153775efcc882410ff414a909ab6f6bab24193ecb2d746d7acdab33f6968"
EXPECTED_PANEL_SHA256 = "c09fdfb867fbb20ea1bea7e7334b3592d9fb5996a02419a0488d622413dbf9b6"
PRELAUNCH_SHA256 = "e7ca2c1ff2449ff4c9bd393969f63fbd7416e1d62209fa1b6a16687aae819cd9"
ARM_SHA256 = "2c4c430c8ec8f0abcdbd84192f8c9040485804e65ca7adab3505dbf9c222cb54"
DATASET_SHA256 = "264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"
DATASET_PATH = "hf://aicrowd/arc-whestbench-public-2026@v2-phase2"
ESTIMATOR_SHA256 = "86d9ca9b28e6fe2b6c74750a0b6ae4bba4c14f742ddc3f5f56bc7fb4ec9d8e27"
FLOP_BUDGET = 2199023255552
RESIDUAL_LIMIT = 0.4
EXPECTED_SHAPE = (16, 1024)
EXPECTED_MAX_THREADS = 1

EXECUTOR_COMMIT = "85f5ba13236aad07bf31436b356cfa2a3744ad33"
FROZEN_ARM_HEAD = "c8cb97dcd1383f4a1d741c5a36ba816deec452eb"
ARM_BLOB = "542f8f80cee29c83b4f9648a1c56f49ae9b9262a"
WORKFLOW_BLOB = "d1fa366b1056d09f829a9620eda81034584147af"
EXECUTOR_BLOB = "456364bd0558eb98d41a4f9cd0512484fe972d20"
EXPECTED_PANEL_BLOB = "8669ffff7408c4f251c700ca0d5f9fc24db5c8f0"
PRELAUNCH_BLOB = "fe0745d3d0265b7afb8d952530998c6b0f942aa3"
EXPECTED_ARTIFACT_NAME = "r218-v29-l4-affinity-crossover"

EXPECTED_VERSIONS = {
    "python": "3.11.16",
    "numpy": "2.4.6",
    "flopscope": "0.12.1",
    "whestbench": "0.16.1",
}
REQUIRED_THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
}
REQUIRED_PREFLIGHT_GATES = {
    "protocol_sha256",
    "expected_panel_static",
    "source_sha256",
    "python",
    "numpy",
    "flopscope",
    "whestbench",
    "V26_STRASSEN",
    "thread_env",
    "required_allowed_cpus",
    "block_sequence",
    "dataset_contract",
    "panel_static_identity",
    "same_worker_single_job_design",
}
REQUIRED_PREFLIGHT_FILES = {
    "preflight.json",
    "runner_env.txt",
    "azure_instance_metadata.json",
    "preflight_lscpu.json",
    "preflight_proc_cpuinfo.txt",
    "preflight_proc_self_status.txt",
    "preflight_taskset.txt",
    "preflight_affinity.json",
    "whest_version.json",
}
REQUIRED_BLOCK_TELEMETRY = {
    "lscpu.json",
    "proc_cpuinfo.txt",
    "orchestrator_proc_self_status.txt",
    "orchestrator_affinity.json",
    "taskset_orchestrator.txt",
    "child_proc_self_status.txt",
    "child_taskset.txt",
}
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


def read_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def proc_status_cpus(text: str):
    m = re.search(r"^Cpus_allowed_list:\s*([^\n]+)", text, flags=re.MULTILINE)
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


def pinned_file_ok(path: pathlib.Path, expected_sha256: str) -> bool:
    return path.is_file() and sha256(path) == expected_sha256


def manifest_contract(root: pathlib.Path):
    """Require a nonempty manifest that exactly covers every artifact file except itself."""
    manifest_path = root / "sha256.json"
    detail = {"errors": [], "listed": [], "actual": []}
    if not manifest_path.is_file():
        detail["errors"].append("missing:sha256.json")
        return False, detail
    try:
        manifest = read_json(manifest_path)
    except Exception as exc:
        detail["errors"].append(f"invalid_json:{type(exc).__name__}")
        return False, detail
    if not isinstance(manifest, dict) or not manifest:
        detail["errors"].append("manifest_empty_or_not_object")
        return False, detail

    actual = {
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file() and p != manifest_path
    }
    listed = set(manifest)
    detail["listed"] = sorted(listed)
    detail["actual"] = sorted(actual)
    if listed != actual:
        missing = sorted(actual - listed)
        extra = sorted(listed - actual)
        if missing:
            detail["errors"].append("unlisted:" + ",".join(missing))
        if extra:
            detail["errors"].append("listed_but_absent:" + ",".join(extra))
    for rel in sorted(listed & actual):
        digest = manifest.get(rel)
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            detail["errors"].append(f"invalid_digest:{rel}")
        elif sha256(root / rel) != digest:
            detail["errors"].append(f"hash:{rel}")
    return not detail["errors"], detail


def archive_directory_binding(archive: pathlib.Path, root: pathlib.Path):
    """Verify the independently downloaded Actions ZIP is byte-for-byte the local dir."""
    detail = {"errors": [], "archive_sha256": None}
    if not archive or not archive.is_file():
        detail["errors"].append("missing_artifact_archive")
        return False, detail
    detail["archive_sha256"] = sha256(archive)
    try:
        with zipfile.ZipFile(archive, "r") as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            # upload-artifact normally strips the common r218/ root. Tolerate exactly
            # one common r218/ prefix, but no arbitrary path remapping.
            if names and all(n.startswith("r218/") for n in names):
                mapped = {n[len("r218/"):]: n for n in names}
            else:
                mapped = {n: n for n in names}
            actual = {
                str(p.relative_to(root))
                for p in root.rglob("*")
                if p.is_file()
            }
            if set(mapped) != actual:
                detail["errors"].append(
                    "zip_file_set_mismatch"
                    f":missing={sorted(actual-set(mapped))}"
                    f":extra={sorted(set(mapped)-actual)}"
                )
            for rel in sorted(set(mapped) & actual):
                if sha256_bytes(zf.read(mapped[rel])) != sha256(root / rel):
                    detail["errors"].append(f"zip_hash:{rel}")
    except Exception as exc:
        detail["errors"].append(f"zip_error:{type(exc).__name__}:{exc}")
    return not detail["errors"], detail


def whest_version_value(obj):
    if not isinstance(obj, dict):
        return None
    return obj.get("whestbench_version") or obj.get("version")


def preflight_contract(preflight, whest_file):
    pgates = preflight.get("gates", {}) if isinstance(preflight, dict) else {}
    allowed = set(preflight.get("allowed_cpu_affinity", [])) if isinstance(preflight, dict) else set()
    checks = {
        "all_pass": preflight.get("all_pass") is True,
        "exact_gate_keys": set(pgates) == REQUIRED_PREFLIGHT_GATES,
        "all_gate_values_true": set(pgates) == REQUIRED_PREFLIGHT_GATES
        and all(pgates.get(k) is True for k in REQUIRED_PREFLIGHT_GATES),
        "python_exact": preflight.get("python") == EXPECTED_VERSIONS["python"],
        "whest_file_exact": whest_version_value(whest_file) == EXPECTED_VERSIONS["whestbench"],
        "whest_preflight_matches_file": preflight.get("whest_version") == whest_file,
        "v26_strassen": preflight.get("V26_STRASSEN") == "4",
        "thread_env": all(preflight.get("thread_env", {}).get(k) == v for k, v in REQUIRED_THREAD_ENV.items()),
        "cpu0_cpu1_allowed": 0 in allowed and 1 in allowed,
    }
    return all(checks.values()), {"checks": checks, "allowed": sorted(allowed), "gate_keys": sorted(pgates)}


def report_contract(report, expected_names, expected_flops):
    cfg = report.get("run_config", {})
    ds = cfg.get("dataset", {})
    rows = report.get("results", {}).get("per_mlp", [])
    names = [x.get("mlp_name") for x in rows]
    try:
        flops = [int(x.get("flops_used")) for x in rows]
    except Exception:
        flops = []
    checks = {
        "count_50": len(rows) == 50,
        "name_order": names == expected_names,
        "flops": flops == expected_flops,
        "dataset_hash": ds.get("sha256") == DATASET_SHA256,
        "dataset_path": ds.get("path") == DATASET_PATH,
        "flop_budget": cfg.get("flop_budget") == FLOP_BUDGET,
        "residual_limit": cfg.get("residual_wall_time_limit_s") == RESIDUAL_LIMIT,
        "shape": (cfg.get("depth"), cfg.get("width")) == EXPECTED_SHAPE,
        "max_threads": cfg.get("max_threads") == EXPECTED_MAX_THREADS,
        "whestbench": report.get("whestbench_version") == EXPECTED_VERSIONS["whestbench"],
    }
    return all(checks.values()), checks


def telemetry_contract(td: pathlib.Path, condition: str, allowed: set[int]):
    detail = {"errors": [], "files": {}}
    for name in sorted(REQUIRED_BLOCK_TELEMETRY):
        p = td / name
        detail["files"][name] = p.is_file() and p.stat().st_size > 0
        if not detail["files"][name]:
            detail["errors"].append(f"missing_or_empty:{name}")
    if detail["errors"]:
        return False, detail

    try:
        orch_aff = set(read_json(td / "orchestrator_affinity.json").get("sched_getaffinity", []))
    except Exception:
        orch_aff = set()
    orch_task = taskset_cpus((td / "taskset_orchestrator.txt").read_text(encoding="utf-8", errors="replace"))
    orch_status = proc_status_cpus((td / "orchestrator_proc_self_status.txt").read_text(encoding="utf-8", errors="replace"))
    child_task = taskset_cpus((td / "child_taskset.txt").read_text(encoding="utf-8", errors="replace"))
    child_status = proc_status_cpus((td / "child_proc_self_status.txt").read_text(encoding="utf-8", errors="replace"))

    if condition == "C0":
        child_expected = {0}
    elif condition == "C1":
        child_expected = {1}
    elif condition == "U":
        child_expected = allowed
    else:
        child_expected = set()

    checks = {
        "orchestrator_affinity": orch_aff == allowed,
        "orchestrator_taskset": orch_task == allowed,
        "orchestrator_proc_status": orch_status == allowed,
        "child_taskset": child_task == child_expected,
        "child_proc_status": child_status == child_expected,
        "cpuinfo_nonempty": (td / "proc_cpuinfo.txt").stat().st_size > 0,
        "lscpu_nonempty": (td / "lscpu.json").stat().st_size > 0,
    }
    detail["checks"] = checks
    detail["orchestrator_allowed"] = sorted(orch_aff)
    detail["child_cpus"] = sorted(child_task) if child_task is not None else None
    return all(checks.values()), detail


def runner_region_from_metadata(obj):
    if not isinstance(obj, dict):
        return None
    compute = obj.get("compute")
    if not isinstance(compute, dict):
        return None
    val = compute.get("location") or compute.get("locationDisplayName")
    return val if isinstance(val, str) and val.strip() else None


def validate_actions_evidence(evidence, github, archive, root, runner_region):
    """Strict R220 external provenance contract. Any mismatch is fail-closed."""
    zip_ok, zip_detail = archive_directory_binding(archive, root)
    archive_sha = zip_detail.get("archive_sha256")
    versions = evidence.get("environment_versions_verified", {}) if isinstance(evidence, dict) else {}
    checks = {
        "evidence_source": evidence.get("evidence_source") == "github_actions_api_independent",
        "run_id": str(evidence.get("run_id")) == str(github.get("GITHUB_RUN_ID")),
        "run_attempt_exactly_1": str(evidence.get("run_attempt")) == "1"
        and str(github.get("GITHUB_RUN_ATTEMPT")) == "1",
        "job_name": evidence.get("job_name") == github.get("GITHUB_JOB") == "crossover",
        "job_id": isinstance(evidence.get("job_id"), int) and evidence.get("job_id") > 0,
        "single_job": evidence.get("single_crossover_job_verified") is True,
        "run_conclusion": evidence.get("run_conclusion") == "success",
        "job_conclusion": evidence.get("job_conclusion") == "success",
        "artifact_id": isinstance(evidence.get("artifact_id"), int) and evidence.get("artifact_id") > 0,
        "artifact_name": evidence.get("artifact_name") == EXPECTED_ARTIFACT_NAME,
        "artifact_run_id": str(evidence.get("artifact_run_id")) == str(github.get("GITHUB_RUN_ID")),
        "artifact_digest": isinstance(evidence.get("artifact_digest_sha256"), str)
        and evidence.get("artifact_digest_sha256") == archive_sha,
        "archive_matches_directory": zip_ok,
        "head_sha": evidence.get("head_sha") == FROZEN_ARM_HEAD,
        "arm_commit": evidence.get("arm_commit") == FROZEN_ARM_HEAD,
        "arm_blob": evidence.get("arm_blob") == ARM_BLOB,
        "arm_sha256": evidence.get("arm_sha256") == ARM_SHA256,
        "arm_parent": evidence.get("arm_parent_commit") == EXECUTOR_COMMIT,
        "arm_only_file_diff": evidence.get("arm_only_file_diff_verified") is True,
        "workflow_blob": evidence.get("workflow_blob") == WORKFLOW_BLOB,
        "executor_blob": evidence.get("executor_blob") == EXECUTOR_BLOB,
        "executor_commit": evidence.get("executor_commit") == EXECUTOR_COMMIT,
        "expected_panel_blob": evidence.get("expected_panel_blob") == EXPECTED_PANEL_BLOB,
        "prelaunch_blob": evidence.get("prelaunch_blob") == PRELAUNCH_BLOB,
        "estimator_sha256": evidence.get("estimator_source_sha256_verified") == ESTIMATOR_SHA256,
        "versions": versions == EXPECTED_VERSIONS,
        "runner_name": bool(github.get("RUNNER_NAME")) and evidence.get("runner_name") == github.get("RUNNER_NAME"),
        "runner_region": bool(runner_region) and evidence.get("runner_region") == runner_region,
    }
    return all(checks.values()), {"checks": checks, "zip": zip_detail}


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
    ap.add_argument("--artifact-archive", type=pathlib.Path,
                    help="Independently downloaded GitHub Actions artifact ZIP; required with --actions-evidence.")
    ap.add_argument("--protocol", required=True, type=pathlib.Path)
    ap.add_argument("--expected-panel", required=True, type=pathlib.Path)
    ap.add_argument(
        "--actions-evidence",
        type=pathlib.Path,
        help="R220-produced independent GitHub Actions provenance JSON. Final verdict is withheld if absent.",
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
    add_gate(gates, "expected_panel_frozen_sha256", sha256(args.expected_panel) == EXPECTED_PANEL_SHA256)

    artifact_protocol = root / "R217_NEXT_RUNTIME_PROTOCOL.json"
    artifact_expected = root / "R218_EXPECTED_PANEL.json"
    artifact_prelaunch = root / "R218_PRELAUNCH_GATE.json"
    add_gate(gates, "artifact_protocol_copy_hash",
             pinned_file_ok(artifact_protocol, PROTOCOL_SHA256),
             sha256(artifact_protocol) if artifact_protocol.is_file() else None)
    add_gate(gates, "artifact_expected_panel_frozen_hash",
             pinned_file_ok(artifact_expected, EXPECTED_PANEL_SHA256),
             sha256(artifact_expected) if artifact_expected.is_file() else None)
    add_gate(gates, "artifact_prelaunch_frozen_hash",
             pinned_file_ok(artifact_prelaunch, PRELAUNCH_SHA256),
             sha256(artifact_prelaunch) if artifact_prelaunch.is_file() else None)

    panel = expected.get("panel", [])
    expected_names = [x.get("mlp_name") for x in panel]
    try:
        expected_flops = [int(x.get("measured_flops")) for x in panel]
    except Exception:
        expected_flops = []
    add_gate(gates, "expected_panel_50", len(panel) == 50)
    add_gate(gates, "expected_panel_indices", [x.get("mlp_index") for x in panel] == list(range(50)))
    add_gate(gates, "expected_dataset_hash", expected.get("dataset", {}).get("sha256") == DATASET_SHA256)
    add_gate(gates, "expected_dataset_path", expected.get("dataset", {}).get("path") == DATASET_PATH)
    add_gate(gates, "expected_source_hash", expected.get("source", {}).get("sha256") == ESTIMATOR_SHA256)

    manifest_ok, manifest_detail = manifest_contract(root)
    add_gate(gates, "artifact_manifest_complete_nonempty", manifest_ok, manifest_detail)

    for rel in sorted(REQUIRED_PREFLIGHT_FILES):
        p = root / rel
        add_gate(gates, f"required_preflight_file_{rel.replace('.', '_')}",
                 p.is_file() and p.stat().st_size > 0)

    preflight_path = root / "preflight.json"
    preflight = read_json(preflight_path) if preflight_path.is_file() else {}
    whest_path = root / "whest_version.json"
    whest_file = read_json(whest_path) if whest_path.is_file() else {}
    preflight_ok, preflight_detail = preflight_contract(preflight, whest_file)
    add_gate(gates, "preflight_exact_contract", preflight_ok, preflight_detail)
    allowed = set(preflight.get("allowed_cpu_affinity", []))

    env_path = root / "runner_env.txt"
    runner_env = parse_env(env_path) if env_path.is_file() else {}
    github = preflight.get("github", {})
    add_gate(gates, "runner_env_present", bool(runner_env))
    for key in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_JOB", "RUNNER_NAME",
                "RUNNER_OS", "RUNNER_ARCH", "ImageOS", "ImageVersion"):
        add_gate(
            gates,
            f"runner_env_matches_preflight_{key}",
            bool(github.get(key)) and runner_env.get(key) == github.get(key),
            {"preflight": github.get(key), "runner_env": runner_env.get(key)},
        )
    add_gate(gates, "preflight_attempt_exactly_1",
             str(github.get("GITHUB_RUN_ATTEMPT")) == "1")

    preflight_aff = root / "preflight_affinity.json"
    preflight_task = root / "preflight_taskset.txt"
    preflight_status = root / "preflight_proc_self_status.txt"
    try:
        preflight_allowed = set(read_json(preflight_aff).get("allowed_cpus", []))
    except Exception:
        preflight_allowed = set()
    add_gate(gates, "preflight_affinity_matches",
             preflight_allowed == allowed and 0 in allowed and 1 in allowed,
             sorted(preflight_allowed))
    add_gate(gates, "preflight_taskset_matches",
             preflight_task.is_file() and taskset_cpus(preflight_task.read_text(errors="replace")) == allowed)
    add_gate(gates, "preflight_proc_status_matches",
             preflight_status.is_file() and proc_status_cpus(preflight_status.read_text(errors="replace")) == allowed)

    azure_path = root / "azure_instance_metadata.json"
    azure = read_json(azure_path) if azure_path.is_file() else {}
    runner_region = runner_region_from_metadata(azure)
    add_gate(gates, "worker_region_recorded", bool(runner_region), runner_region)

    preflight_lscpu_path = root / "preflight_lscpu.json"
    preflight_lscpu_identity = lscpu_identity(preflight_lscpu_path) if preflight_lscpu_path.is_file() else None
    add_gate(gates, "preflight_lscpu_identity_present",
             isinstance(preflight_lscpu_identity, dict) and all(preflight_lscpu_identity.values()),
             preflight_lscpu_identity)

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

        report_ok, report_checks = report_contract(report, expected_names, expected_flops)
        for key, val in report_checks.items():
            add_gate(gates, f"block_{bi:02d}_{key}", val)

        rows = normalize_report_rows(report, bi, condition)
        all_rows.extend(rows)

        td = root / "telemetry" / f"block_{bi:02d}_{condition}"
        telemetry_ok, telemetry_detail = telemetry_contract(td, condition, allowed) if td.is_dir() else (False, {"errors": ["missing_telemetry_dir"]})
        add_gate(gates, f"block_{bi:02d}_mandatory_telemetry", telemetry_ok, telemetry_detail)
        child = telemetry_detail.get("child_cpus")
        block_affinities.append({"block_index": bi, "condition": condition, "child_cpus": child})

        lscpu_path = td / "lscpu.json"
        if lscpu_path.is_file():
            ident = lscpu_identity(lscpu_path)
            lscpu_identities.append(ident)
            add_gate(gates, f"block_{bi:02d}_lscpu_matches_preflight",
                     ident == preflight_lscpu_identity,
                     {"block": ident, "preflight": preflight_lscpu_identity})

        failures = sum(r["status"] == "failed" for r in rows)
        score_vals = [r["official_adjusted_score"] for r in rows]
        numeric_scores = [float(x) for x in score_vals if isinstance(x, (int, float))]
        row_score_mean = statistics.mean(numeric_scores) if len(numeric_scores) == len(rows) and rows else None
        report_score = report.get("results", {}).get("adjusted_final_layer_score")
        add_gate(
            gates,
            f"block_{bi:02d}_aggregate_score_matches_rows",
            isinstance(report_score, (int, float))
            and row_score_mean is not None
            and math.isclose(float(report_score), row_score_mean, rel_tol=0.0, abs_tol=1e-12),
            {"report": report_score, "row_mean": row_score_mean},
        )
        residuals = [float(r["residual_wall_time_s"]) for r in rows if isinstance(r["residual_wall_time_s"], (int, float))]
        block_summaries.append({
            "block_index": bi,
            "condition": condition,
            "failures": failures,
            "mean_residual_wall_time_s": statistics.mean(residuals) if len(residuals) == len(rows) and rows else None,
            "median_residual_wall_time_s": statistics.median(residuals) if len(residuals) == len(rows) and rows else None,
            "official_adjusted_score_from_report": report_score,
            "official_adjusted_score_recomputed_row_mean": row_score_mean,
            "report_sha256": sha256(report_path),
        })

    add_gate(gates, "exact_300_rows", len(all_rows) == 300, len(all_rows))
    add_gate(gates, "six_lscpu_identities_present", len(lscpu_identities) == 6, len(lscpu_identities))
    add_gate(
        gates,
        "stable_lscpu_identity_across_blocks",
        len(lscpu_identities) == 6
        and all(x == preflight_lscpu_identity for x in lscpu_identities),
        lscpu_identities,
    )

    counts = {c: sum(r["condition"] == c for r in all_rows) for c in ("U", "C0", "C1")}
    add_gate(gates, "two_blocks_each_condition", counts == {"U": 100, "C0": 100, "C1": 100}, counts)

    per_condition = {}
    per_mlp = {}
    if len(all_rows) == 300 and counts == {"U": 100, "C0": 100, "C1": 100}:
        for c in ("U", "C0", "C1"):
            rr = [r for r in all_rows if r["condition"] == c]
            residuals = [r["residual_wall_time_s"] for r in rr]
            scores = [r["official_adjusted_score"] for r in rr]
            if all(isinstance(x, (int, float)) for x in residuals + scores):
                per_condition[c] = {
                    "residual_wall_time_s": summary(residuals),
                    "failures_across_two_blocks": sum(r["status"] == "failed" for r in rr),
                    "mean_official_adjusted_score": statistics.mean(float(x) for x in scores),
                }
        for i in range(50):
            entry = {"mlp_index": i, "mlp_name": expected_names[i]}
            for c in ("U", "C0", "C1"):
                rr = [r for r in all_rows if r["condition"] == c and r["mlp_index"] == i]
                ok = len(rr) == 2 and all(isinstance(r["residual_wall_time_s"], (int, float)) for r in rr)
                add_gate(gates, f"mlp_{i:02d}_{c}_two_numeric_observations", ok, len(rr))
                if ok:
                    entry[f"{c}_mean_residual_s"] = statistics.mean(float(r["residual_wall_time_s"]) for r in rr)
            per_mlp[i] = entry

    analysis = {}
    if (
        len(per_condition) == 3
        and len(per_mlp) == 50
        and all(
            "C0_mean_residual_s" in x
            and "C1_mean_residual_s" in x
            and "U_mean_residual_s" in x
            for x in per_mlp.values()
        )
    ):
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
            add_gate(gates, "owner_cpu0_slower_count_matches",
                     oa.get("cpu0_slower_count") == analysis["cpu0_slower_count"])
            add_gate(gates, "owner_failure_difference_matches",
                     oa.get("failure_difference") == analysis["failure_difference"])

    actions_evidence_supplied = args.actions_evidence is not None
    actions_ok = False
    actions_detail = {"reason": "not supplied"}
    if actions_evidence_supplied:
        evidence = read_json(args.actions_evidence)
        actions_ok, actions_detail = validate_actions_evidence(
            evidence, github, args.artifact_archive, root, runner_region
        )
    add_gate(
        gates,
        "external_actions_artifact_source_provenance",
        actions_ok,
        actions_detail,
    )

    artifact_gate_names = [k for k in gates if k != "external_actions_artifact_source_provenance"]
    artifact_contract_ok = all(gates[k]["pass"] for k in artifact_gate_names)

    if not artifact_contract_ok:
        decision = "PROTOCOL_INVALID"
    elif not actions_evidence_supplied:
        decision = "PENDING_EXTERNAL_ACTIONS_PROVENANCE"
    elif not actions_ok:
        decision = "PROTOCOL_INVALID"
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
        "schema": "arc.whitebox.r234.r218_postflight_verifier.v2_hardened_r237",
        "decision": decision,
        "artifact_contract_ok": artifact_contract_ok,
        "external_actions_artifact_source_provenance_ok": actions_ok,
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
        "hardening": {
            "source": "R236 defects D1-D7",
            "r217_thresholds_changed": False,
            "r218_changed": False,
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "analysis": analysis}, sort_keys=True))


if __name__ == "__main__":
    main()
