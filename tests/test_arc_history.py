"""Run with python -m unittest discover -s tests -p test_arc_history.py."""

import importlib.util
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "arc_history", Path(__file__).resolve().parents[1] / "scripts" / "arc_history.py"
)
history = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(history)


class HistoryTest(unittest.TestCase):
    def test_history_dedup_gaps_and_missing_blob(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=repo).decode().strip()

            def write(path, payload):
                target = repo / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)

            def commit(message):
                git("add", ".")
                git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                    "-c", "commit.gpgsign=false", "commit", "-qm", message)
                return git("rev-parse", "HEAD")

            git("init", "-q")
            git("config", "core.autocrlf", "false")
            git("remote", "add", "origin", "https://github.com/example/history.git")
            legacy = (b'\xef\xbb\xbfid,status,result\r\nE000,DONE,"mse=0.1; not comparable"\r\n'
                      b'E001,IDEA,"mentions E002, which is not a row id"\r\n')
            write("research/ledger.csv", legacy)
            write("research/E000_PROTOCOL.md", b"baseline")
            write("research/e003_REJECTED.json", b'{"status":"RUNNING","decision":"DROP"}')
            write("docs/E003_OLD.md", b"removed in the next commit")
            write("research/e181/E181_RESULTS.json", b'{"decision":"KEEP"}')
            write("research/e181/plain.json", b'{"status":"DO NOT INDEX DIRECTORY IDS"}')
            write("scripts/E002.py", b"not a research or docs artifact")
            write("research/E004_REJECTED.md", b"filename is not a verdict")
            write("research/E005.json", b'{"nested":{"status":"DROP"}}')
            write("research/E006.json", b"invalid JSON")
            write("research/E007.json", b'{"status":42}')
            write("research/E008.json", b'{"status":"TOO LARGE"}')
            write("research/E009_DATA.npz", b"do not read vector content")
            first = commit("first evidence")
            git("update-ref", history.BOOTSTRAP, first)
            git("update-ref", "refs/remotes/origin/research/e181-original", first)
            initial, _ = history.build_inventory(repo)
            self.assertEqual(len(initial["experiments"]), 194)
            self.assertEqual(initial["experiments"][-1]["coverage"], "MISSING")
            (repo / "docs/E003_OLD.md").unlink()
            write("docs/E193_E194.txt", b"both IDs")
            write("research/e003_REJECTED.json", b'{"decision":"NEEDS_REVIEW"}')
            write("research/e181/E181_RESULTS.json", b'{"decision":"INDEPENDENT"}')
            second = commit("historical variants")
            git("update-ref", "refs/remotes/origin/research/e181-cleanroom", second)
            git("symbolic-ref", "refs/remotes/origin/HEAD", history.BOOTSTRAP)

            with patch.object(history, "JSON_LIMIT", 20):
                capped, _ = history.build_inventory(repo)
            self.assertIsNone(capped["experiments"][8]["artifacts"][0]["declared_status"])

            def refresh():
                with redirect_stdout(io.StringIO()):
                    return history.refresh(repo)

            inventory = refresh()
            entries = {item["experiment_id"]: item for item in inventory["experiments"]}
            self.assertEqual(len(inventory["generated_from"]), 3)
            self.assertEqual(len(entries), 195)
            self.assertEqual(entries["E000"]["coverage"], "ARTIFACTS")
            self.assertEqual(entries["E001"]["coverage"], "LEGACY_ONLY")
            self.assertEqual(entries["E002"]["coverage"], "MISSING")
            self.assertEqual(entries["E192"]["coverage"], "MISSING")
            self.assertEqual(entries["E194"]["coverage"], "ARTIFACTS")
            self.assertEqual(entries["E002"]["artifacts"], [])
            self.assertEqual(entries["E002"]["legacy_rows"], [])
            self.assertEqual(entries["E000"]["legacy_rows"][0]["result"],
                             "mse=0.1; not comparable")
            self.assertEqual((repo / "research/legacy-ledger.csv").read_bytes(), legacy)
            self.assertEqual(len(entries["E000"]["artifacts"]), 1)
            self.assertEqual(len(entries["E000"]["artifacts"][0]["refs"]), 3)
            self.assertEqual(len(entries["E003"]["artifacts"]), 3)
            self.assertEqual(len(entries["E181"]["artifacts"]), 2)
            self.assertEqual({item["declared_status"] for item in entries["E181"]["artifacts"]},
                             {"KEEP", "INDEPENDENT"})
            for experiment_id in ("E004", "E005", "E006", "E007", "E009"):
                self.assertIsNone(entries[experiment_id]["artifacts"][0]["declared_status"])
            self.assertEqual({item["declared_status"] for item in entries["E003"]["artifacts"]},
                             {None, "RUNNING", "NEEDS_REVIEW"})
            for entry in inventory["experiments"]:
                for artifact in entry["artifacts"]:
                    self.assertIn(artifact["commit"], {first, second})
                    self.assertIn(f"/blob/{artifact['commit']}/", artifact["url"])
                    self.assertEqual(git("rev-parse", f"{artifact['commit']}:{artifact['path']}"),
                                     artifact["blob"])

            expected = (repo / "research/history.json").read_bytes()
            refresh()
            self.assertEqual((repo / "research/history.json").read_bytes(), expected)
            self.assertEqual(json.loads(expected), inventory)

            # Delete one fixture-only loose object. A refresh must fail without
            # rewriting existing outputs, even for blobs whose content is skipped.
            blob = entries["E009"]["artifacts"][0]["blob"]
            object_path = repo / ".git/objects" / blob[:2] / blob[2:]
            object_path.chmod(0o600)
            object_path.unlink()
            with self.assertRaisesRegex(RuntimeError, "missing local blob.*Explicitly fetch"):
                refresh()
            self.assertEqual((repo / "research/history.json").read_bytes(), expected)
            self.assertEqual((repo / "research/legacy-ledger.csv").read_bytes(), legacy)


if __name__ == "__main__":
    unittest.main()
