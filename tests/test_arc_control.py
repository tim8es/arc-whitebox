import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import arc_control as c


def result(name="a"):
    return {"id": name, "panel": {"dataset": "d", "revision": "pinned", "stage": "development",
            "shape": [16, 1024], "dtype": "float32", "evaluator": "v1", "meter": "v1", "count": 2},
            "per_network": [{"network_id": str(i), "target_sha256": str(i)*64,
                "final_mse": mse, "measured_flops": flops, "budget_flops": 100,
                "status": "ok"} for i, mse, flops in [(1, 1, 5), (2, 3, 50)]]}


def state():
    return {"schema_version": 2, "revision": 0, "jobs": [
        {"id": "a", "status": "QUEUED", "owner": None, "depends_on": [], "attempts": []},
        {"id": "b", "status": "QUEUED", "owner": None, "depends_on": ["a"], "attempts": []}]}


class ControlTests(unittest.TestCase):
    def test_score_is_mean_of_products_with_floor(self):
        self.assertAlmostEqual(c.score_record(result())["adjusted_score"], .8)
        self.assertNotAlmostEqual(.8, 2*.275)

    def test_failed_network_is_not_dropped(self):
        r = result()
        r["per_network"][0].update(status="failed", official_adjusted_score=9)
        self.assertEqual(c.score_record(r)["adjusted_score"], 5.25)
        del r["per_network"][0]["official_adjusted_score"]
        with self.assertRaises(ValueError): c.score_record(r)

    def test_135_percent_is_not_hard_gate(self):
        self.assertEqual(c.score_record(result())["failures"], 0)

    def test_panels_and_targets_must_match(self):
        for field, value in [("revision", "other"), ("meter", "v2"), ("stage", "confirmation")]:
            r = result(); r["panel"][field] = value
            with self.assertRaisesRegex(ValueError, "NOT_COMPARABLE"): c.compare(r, result())
        r = result(); r["per_network"][0]["target_sha256"] = "f"*64
        with self.assertRaisesRegex(ValueError, "NOT_COMPARABLE"): c.compare(r, result())

    def test_reordered_rows_are_paired_by_id(self):
        r = result(); r["per_network"].reverse()
        self.assertEqual(c.compare(r, result())["paired_gain_mean"], 0)

    def test_missing_rows_nan_and_unsafe_id_rejected(self):
        for edit in (lambda r: r["per_network"].pop(),
                     lambda r: r["per_network"][0].update(final_mse=float("nan")),
                     lambda r: r["per_network"][0].update(network_id=2**63)):
            r = result(); edit(r)
            with self.assertRaises(ValueError): c.score_record(r)

    def test_claim_is_exclusive_and_idempotent(self):
        s = c.update(state(), "claim", "a", "alice")
        self.assertEqual(s, c.update(s, "claim", "a", "alice"))
        with self.assertRaises(ValueError): c.update(s, "claim", "a", "bob")
        with self.assertRaisesRegex(ValueError, "WAITING_INPUT"): c.update(s, "claim", "b", "bob")

    def test_infra_repair_retains_attempts(self):
        s = c.update(state(), "claim", "a", "alice")
        s = c.update(s, "start", "a", "alice", {"run_id": "1", "code_commit": "abc", "command": "smoke"})
        s = c.update(s, "finish", "a", "alice", {"status": "INFRA_ERROR", "reason": "import",
            "receipt": {"url": "https://example.org/receipt", "sha256": "f"*64}})
        s = c.update(s, "repair", "a", "alice", {"reason": "fixed import"})
        s = c.update(s, "start", "a", "alice", {"run_id": "2", "code_commit": "def", "command": "smoke"})
        self.assertEqual(len(s["jobs"][0]["attempts"]), 2)
        self.assertEqual(s["jobs"][0]["attempts"][0]["status"], "INFRA_ERROR")

    def test_cycles_rejected(self):
        s = state(); s["jobs"][0]["depends_on"] = ["b"]
        with self.assertRaisesRegex(ValueError, "cycle"): c.validate_state(s)

    def test_coordinator_only_enqueue_and_unique_run_ids(self):
        payload = {"title": "test", "hypothesis_id": "H", "priority": 1,
                   "deliverable": "receipt", "depends_on": []}
        with self.assertRaises(ValueError): c.update(state(), "enqueue", "R205", "alice", payload)
        s = c.update(state(), "enqueue", "R205", "coordinator", payload)
        with self.assertRaises(ValueError): c.update(s, "enqueue", "R205", "coordinator", payload)
        s["jobs"][0]["attempts"] = [{"run_id": "duplicate"}]
        s["jobs"][1]["attempts"] = [{"run_id": "duplicate"}]
        with self.assertRaisesRegex(ValueError, "Run ID used twice"): c.validate_state(s)

    def test_git_non_fast_forward_rejects_second_owner(self):
        # Two writers read the same authoritative state. Only one push can win.
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
                   "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"}
            def git(path, *args, data=None, ok=True):
                r = subprocess.run(["git", *args], cwd=path, input=data, capture_output=True,
                                   text=True, env=env)
                if ok: self.assertEqual(r.returncode, 0, r.stderr)
                return r
            root = Path(tmp); bare = root/"remote"; bare.mkdir()
            git(bare, "init", "--bare")
            work = root/"work"; git(root, "clone", str(bare), str(work))
            git(work, "config", "user.email", "test@example.org")
            git(work, "config", "user.name", "Test")
            (work/"state.json").write_text(json.dumps(state()))
            git(work, "add", "state.json"); git(work, "commit", "-m", "base")
            base = git(work, "rev-parse", "HEAD").stdout.strip()
            git(work, "push", "origin", f"{base}:refs/heads/control")
            commits = []
            for owner in ("alice", "bob"):
                (work/"state.json").write_text(json.dumps(c.update(state(), "claim", "a", owner)))
                git(work, "add", "state.json")
                tree = git(work, "write-tree").stdout.strip()
                commits.append(git(work, "commit-tree", tree, "-p", base, data=owner).stdout.strip())
            git(work, "push", "origin", f"{commits[0]}:refs/heads/control")
            rejected = git(work, "push", "origin", f"{commits[1]}:refs/heads/control", ok=False)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("rejected", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
