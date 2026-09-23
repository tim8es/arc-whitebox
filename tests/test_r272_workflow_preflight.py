from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import arc_workflow_preflight as p


GENERATOR = r'''
from pathlib import Path
def build():
    replay={"layer_sha256": [], "weights_concat_sha256": "w", "truth_sha256": "t"}
    m={"layer_sha256": [], "weights_concat_sha256": "w", "truth_sha256": "t",
       "independent_replay": replay, "replay_equal": True}
    m.update({"seed": 254001})
    out_dir=Path(".")
    (out_dir/"R254_FIXTURE_RUNTIME_MANIFEST.json").write_text("{}")
'''


def workflow(fetch_depth=True, runtime_name="R254_FIXTURE_RUNTIME_MANIFEST.json",
             stale_schema=False):
    checkout = """      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
""" if fetch_depth else """      - uses: actions/checkout@v4
"""
    stale = '          assert d["independent_replay"]["all_layer_hashes_equal"] is True\n' if stale_schema else ""
    return f"""jobs:
  test:
    steps:
{checkout}
      - name: Verify ancestry
        run: |
          git merge-base --is-ancestor "$PROTOCOL_COMMIT" HEAD
      - name: Reconstruct fixture
        run: |
          python fixture.py --out-dir artifacts/fixture
          python - <<'PY'
          import json, pathlib
          p=pathlib.Path("artifacts/fixture/{runtime_name}")
          d=json.loads(p.read_text())
          assert d["seed"] == 254001
          assert d["replay_equal"] is True
{stale}          PY
"""


class WorkflowPreflightTests(unittest.TestCase):
    def test_r257_like_shallow_history_is_rejected(self):
        with self.assertRaisesRegex(p.PreflightError, "fetch-depth: 0"):
            p.check_contract(workflow(fetch_depth=False), GENERATOR)

    def test_r258_like_manifest_name_mismatch_is_rejected(self):
        with self.assertRaisesRegex(p.PreflightError, "runtime manifest name"):
            p.check_contract(
                workflow(runtime_name="R254_RUNTIME_FIXTURE_MANIFEST.json"),
                GENERATOR,
            )

    def test_r259_like_nonexistent_schema_field_is_rejected(self):
        with self.assertRaisesRegex(p.PreflightError, "all_layer_hashes_equal"):
            p.check_contract(workflow(stale_schema=True), GENERATOR)

    def test_r260_like_repaired_contract_passes(self):
        result = p.check_contract(workflow(), GENERATOR)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(
            result["runtime_manifest"], "R254_FIXTURE_RUNTIME_MANIFEST.json"
        )
        self.assertEqual(result["asserted_manifest_keys"], ["replay_equal", "seed"])


if __name__ == "__main__":
    unittest.main()
