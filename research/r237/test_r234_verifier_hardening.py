#!/usr/bin/env python3
"""Offline fail-closed regression suite for R237 hardened R234 verifier.

Uses only synthetic temporary files/ZIPs. It never reads the R218 artifact, never
launches Actions, and never executes whest or an estimator.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest
import zipfile

HERE = pathlib.Path(__file__).resolve()
VERIFIER = HERE.parents[1] / "r234" / "r234_verify_r218.py"
spec = importlib.util.spec_from_file_location("r234_verify_r218", VERIFIER)
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)


def write_json(path: pathlib.Path, obj):
    path.write_text(json.dumps(obj, sort_keys=True) + "\n", encoding="utf-8")


def file_sha(path: pathlib.Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class HardenedVerifierRegression(unittest.TestCase):
    def _zip_root(self, root: pathlib.Path, archive: pathlib.Path):
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(root.rglob("*")):
                if p.is_file():
                    zf.write(p, str(p.relative_to(root)))

    def _valid_actions(self, archive: pathlib.Path, run_attempt=1):
        return {
            "evidence_source": "github_actions_api_independent",
            "run_id": "12345",
            "run_attempt": run_attempt,
            "run_conclusion": "success",
            "job_id": 98765,
            "job_name": "crossover",
            "job_conclusion": "success",
            "single_crossover_job_verified": True,
            "artifact_id": 444,
            "artifact_name": m.EXPECTED_ARTIFACT_NAME,
            "artifact_run_id": "12345",
            "artifact_digest_sha256": file_sha(archive),
            "head_sha": m.FROZEN_ARM_HEAD,
            "arm_commit": m.FROZEN_ARM_HEAD,
            "arm_blob": m.ARM_BLOB,
            "arm_sha256": m.ARM_SHA256,
            "arm_parent_commit": m.EXECUTOR_COMMIT,
            "arm_only_file_diff_verified": True,
            "workflow_blob": m.WORKFLOW_BLOB,
            "executor_blob": m.EXECUTOR_BLOB,
            "executor_commit": m.EXECUTOR_COMMIT,
            "expected_panel_blob": m.EXPECTED_PANEL_BLOB,
            "prelaunch_blob": m.PRELAUNCH_BLOB,
            "estimator_source_sha256_verified": m.ESTIMATOR_SHA256,
            "environment_versions_verified": dict(m.EXPECTED_VERSIONS),
            "runner_name": "runner-1",
            "runner_region": "eastus",
        }

    def _github(self, attempt="1"):
        return {
            "GITHUB_RUN_ID": "12345",
            "GITHUB_RUN_ATTEMPT": str(attempt),
            "GITHUB_JOB": "crossover",
            "RUNNER_NAME": "runner-1",
        }

    def test_d1_attempt2_rejected_even_when_matching(self):
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            root = d / "artifact"
            root.mkdir()
            (root / "x.txt").write_text("x", encoding="utf-8")
            archive = d / "artifact.zip"
            self._zip_root(root, archive)
            evidence = self._valid_actions(archive, run_attempt=2)
            ok, detail = m.validate_actions_evidence(
                evidence, self._github(attempt="2"), archive, root, "eastus"
            )
            self.assertFalse(ok)
            self.assertFalse(detail["checks"]["run_attempt_exactly_1"])

    def test_d2_artifact_and_source_binding_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            root = d / "artifact"
            root.mkdir()
            (root / "x.txt").write_text("x", encoding="utf-8")
            archive = d / "artifact.zip"
            self._zip_root(root, archive)
            base = self._valid_actions(archive)
            ok, detail = m.validate_actions_evidence(base, self._github(), archive, root, "eastus")
            self.assertTrue(ok, detail)

            mutations = {
                "artifact_id": 0,
                "artifact_name": "wrong",
                "artifact_digest_sha256": "0" * 64,
                "head_sha": "0" * 40,
                "arm_commit": "0" * 40,
                "arm_blob": "0" * 40,
                "workflow_blob": "0" * 40,
                "executor_blob": "0" * 40,
                "executor_commit": "0" * 40,
                "expected_panel_blob": "0" * 40,
                "prelaunch_blob": "0" * 40,
                "estimator_source_sha256_verified": "0" * 64,
                "runner_region": "wrong-region",
            }
            for key, value in mutations.items():
                with self.subTest(key=key):
                    bad = dict(base)
                    bad[key] = value
                    ok, _ = m.validate_actions_evidence(
                        bad, self._github(), archive, root, "eastus"
                    )
                    self.assertFalse(ok)

            (root / "x.txt").write_text("tampered", encoding="utf-8")
            ok, detail = m.validate_actions_evidence(
                base, self._github(), archive, root, "eastus"
            )
            self.assertFalse(ok)
            self.assertFalse(detail["checks"]["archive_matches_directory"])

    def test_d3_exact_panel_and_prelaunch_pins(self):
        self.assertEqual(
            m.EXPECTED_PANEL_SHA256,
            "c09fdfb867fbb20ea1bea7e7334b3592d9fb5996a02419a0488d622413dbf9b6",
        )
        self.assertEqual(
            m.PRELAUNCH_SHA256,
            "e7ca2c1ff2449ff4c9bd393969f63fbd7416e1d62209fa1b6a16687aae819cd9",
        )
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "modified.json"
            p.write_text("{}\n", encoding="utf-8")
            self.assertFalse(m.pinned_file_ok(p, m.EXPECTED_PANEL_SHA256))
            self.assertFalse(m.pinned_file_ok(p, m.PRELAUNCH_SHA256))

    def test_d4_manifest_must_be_complete_and_nonempty(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            (root / "a.txt").write_text("a", encoding="utf-8")
            (root / "b.txt").write_text("b", encoding="utf-8")
            write_json(root / "sha256.json", {
                "a.txt": file_sha(root / "a.txt"),
                "b.txt": file_sha(root / "b.txt"),
            })
            ok, detail = m.manifest_contract(root)
            self.assertTrue(ok, detail)

            write_json(root / "sha256.json", {})
            ok, _ = m.manifest_contract(root)
            self.assertFalse(ok)

            write_json(root / "sha256.json", {"a.txt": file_sha(root / "a.txt")})
            ok, detail = m.manifest_contract(root)
            self.assertFalse(ok)
            self.assertTrue(any(x.startswith("unlisted:") for x in detail["errors"]))

    def _valid_preflight(self):
        whest = {"whestbench_version": m.EXPECTED_VERSIONS["whestbench"]}
        preflight = {
            "gates": {k: True for k in m.REQUIRED_PREFLIGHT_GATES},
            "all_pass": True,
            "allowed_cpu_affinity": [0, 1],
            "python": m.EXPECTED_VERSIONS["python"],
            "whest_version": whest,
            "thread_env": dict(m.REQUIRED_THREAD_ENV),
            "V26_STRASSEN": "4",
        }
        return preflight, whest

    def test_d5_exact_preflight_keys_and_versions(self):
        preflight, whest = self._valid_preflight()
        ok, detail = m.preflight_contract(preflight, whest)
        self.assertTrue(ok, detail)

        bad = json.loads(json.dumps(preflight))
        bad["gates"].pop("numpy")
        ok, _ = m.preflight_contract(bad, whest)
        self.assertFalse(ok)

        bad = json.loads(json.dumps(preflight))
        bad["gates"]["unexpected"] = True
        ok, _ = m.preflight_contract(bad, whest)
        self.assertFalse(ok)

        bad = json.loads(json.dumps(preflight))
        bad["python"] = "3.11.15"
        ok, _ = m.preflight_contract(bad, whest)
        self.assertFalse(ok)

        wrong_whest = {"whestbench_version": "0.16.0"}
        ok, _ = m.preflight_contract(preflight, wrong_whest)
        self.assertFalse(ok)

    def _report(self, dataset_path=None, max_threads=1):
        names = [f"mlp-{i}" for i in range(50)]
        flops = [1000 + i for i in range(50)]
        report = {
            "whestbench_version": m.EXPECTED_VERSIONS["whestbench"],
            "run_config": {
                "dataset": {
                    "path": dataset_path or m.DATASET_PATH,
                    "sha256": m.DATASET_SHA256,
                },
                "flop_budget": m.FLOP_BUDGET,
                "residual_wall_time_limit_s": m.RESIDUAL_LIMIT,
                "depth": m.EXPECTED_SHAPE[0],
                "width": m.EXPECTED_SHAPE[1],
                "max_threads": max_threads,
            },
            "results": {
                "per_mlp": [
                    {"mlp_name": names[i], "flops_used": flops[i]}
                    for i in range(50)
                ]
            },
        }
        return report, names, flops

    def test_d6_dataset_path_and_max_threads(self):
        report, names, flops = self._report()
        ok, checks = m.report_contract(report, names, flops)
        self.assertTrue(ok, checks)

        report, names, flops = self._report(dataset_path="hf://wrong")
        ok, checks = m.report_contract(report, names, flops)
        self.assertFalse(ok)
        self.assertFalse(checks["dataset_path"])

        report, names, flops = self._report(max_threads=2)
        ok, checks = m.report_contract(report, names, flops)
        self.assertFalse(ok)
        self.assertFalse(checks["max_threads"])

    def _write_telemetry(self, td: pathlib.Path, child_spec="0-1"):
        td.mkdir(parents=True, exist_ok=True)
        write_json(td / "lscpu.json", {"lscpu": [{"field": "Architecture:", "data": "x86_64"}]})
        (td / "proc_cpuinfo.txt").write_text("processor\t: 0\n", encoding="utf-8")
        (td / "orchestrator_proc_self_status.txt").write_text(
            "Cpus_allowed_list:\t0-1\n", encoding="utf-8"
        )
        write_json(td / "orchestrator_affinity.json", {"sched_getaffinity": [0, 1]})
        (td / "taskset_orchestrator.txt").write_text(
            "pid 10's current affinity list: 0,1\n", encoding="utf-8"
        )
        (td / "child_proc_self_status.txt").write_text(
            f"Cpus_allowed_list:\t{child_spec}\n", encoding="utf-8"
        )
        (td / "child_taskset.txt").write_text(
            f"pid 11's current affinity list: {child_spec}\n", encoding="utf-8"
        )

    def test_d7_full_mandatory_telemetry(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = pathlib.Path(tmp) / "telemetry"
            self._write_telemetry(td, "0-1")
            ok, detail = m.telemetry_contract(td, "U", {0, 1})
            self.assertTrue(ok, detail)

            (td / "child_proc_self_status.txt").unlink()
            ok, detail = m.telemetry_contract(td, "U", {0, 1})
            self.assertFalse(ok)
            self.assertIn("missing_or_empty:child_proc_self_status.txt", detail["errors"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
