from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import arc_workflow_preflight as p


SIMPLE_GENERATOR = r'''
from pathlib import Path
import json

def build():
    replay={"layer_sha256": [], "weights_concat_sha256": "w", "truth_sha256": "t"}
    m={"layer_sha256": [], "weights_concat_sha256": "w", "truth_sha256": "t",
       "independent_replay": replay, "replay_equal": True}
    m.update({"seed": 254001})
    out_dir=Path(".")
    (out_dir/"R254_FIXTURE_RUNTIME_MANIFEST.json").write_text(json.dumps(m))
'''


HARDENED_GENERATOR = r'''
from pathlib import Path
import json

def build_independent_hashes():
    return {"layer_sha256": [], "weights_concat_sha256": "w", "truth_sha256": "t"}

def build_manifest():
    got={"layer_sha256": [], "weights_concat_sha256": "w", "truth_sha256": "t"}
    replay=build_independent_hashes()
    return [], None, {**got, "independent_replay": replay, "replay_equal": True}

def main():
    _, truth, m = build_manifest()
    m.update({"fixture_id": "x", "seed": 254001, "width": 1024, "depth": 16})
    out_dir=Path(".")
    (out_dir/"R254_FIXTURE_RUNTIME_MANIFEST.json").write_text(json.dumps(m)+"\\n")
'''


def legacy_workflow(fetch_depth=True, runtime_name="R254_FIXTURE_RUNTIME_MANIFEST.json",
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


def inline_manifest_step(key="seed", named=True):
    prefix = "      - name: Check fixture\n        run: |" if named else "      - run: |"
    return f"""{prefix}
          p=pathlib.Path("artifacts/R254_FIXTURE_RUNTIME_MANIFEST.json")
          d=json.loads(p.read_text())
          assert d["{key}"] is not None
"""


def hardened_workflow(manifest_step, verify_checkout=True, extra_job=""):
    checkout = """      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
""" if verify_checkout else """      - uses: actions/checkout@v4
"""
    return f"""jobs:
{extra_job}  verify:
    steps:
{checkout}      - run: |
          git merge-base --is-ancestor "$PROTOCOL_COMMIT" HEAD
{manifest_step}"""


class WorkflowPreflightTests(unittest.TestCase):
    def test_shallow_history_is_rejected(self):
        with self.assertRaisesRegex(p.PreflightError, "fetch-depth: 0"):
            p.check_contract(legacy_workflow(fetch_depth=False), SIMPLE_GENERATOR)

    def test_manifest_name_mismatch_is_rejected(self):
        with self.assertRaisesRegex(p.PreflightError, "runtime manifest name"):
            p.check_contract(
                legacy_workflow(runtime_name="R254_RUNTIME_FIXTURE_MANIFEST.json"),
                SIMPLE_GENERATOR,
            )

    def test_nonexistent_schema_field_is_rejected(self):
        with self.assertRaisesRegex(p.PreflightError, "all_layer_hashes_equal"):
            p.check_contract(legacy_workflow(stale_schema=True), SIMPLE_GENERATOR)

    def test_repaired_contract_passes(self):
        result = p.check_contract(legacy_workflow(), SIMPLE_GENERATOR)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["runtime_manifest"], "R254_FIXTURE_RUNTIME_MANIFEST.json")
        self.assertEqual(result["asserted_manifest_keys"], ["replay_equal", "seed"])

    def test_unrelated_dict_cannot_legalize_manifest_key(self):
        generator = HARDENED_GENERATOR.replace(
            'def main():\n    _, truth, m = build_manifest()',
            'def main():\n    unrelated = {"ghost_only_elsewhere": True}\n    _, truth, m = build_manifest()',
        )
        with self.assertRaisesRegex(p.PreflightError, "ghost_only_elsewhere"):
            p.check_contract(
                hardened_workflow(inline_manifest_step("ghost_only_elsewhere")),
                generator,
            )

    def test_manifest_schema_tracks_serialized_object_and_nested_helper(self):
        wf = hardened_workflow("""      - run: |
          p=pathlib.Path("artifacts/R254_FIXTURE_RUNTIME_MANIFEST.json")
          d=json.loads(p.read_text())
          assert d["seed"] == 254001
          assert d["independent_replay"]["layer_sha256"] == []
""")
        result = p.check_contract(wf, HARDENED_GENERATOR)
        self.assertEqual(
            result["asserted_manifest_keys"],
            ["independent_replay.layer_sha256", "seed"],
        )

    def test_full_checkout_in_other_job_does_not_satisfy_ancestry_job(self):
        other = """  prep:
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
"""
        with self.assertRaisesRegex(p.PreflightError, "same job"):
            p.check_contract(
                hardened_workflow(
                    inline_manifest_step(),
                    verify_checkout=False,
                    extra_job=other,
                ),
                HARDENED_GENERATOR,
            )

    def test_unnamed_run_manifest_assertion_is_checked(self):
        with self.assertRaisesRegex(p.PreflightError, "ghost"):
            p.check_contract(
                hardened_workflow(inline_manifest_step("ghost", named=False)),
                HARDENED_GENERATOR,
            )

    def test_manifest_read_without_extracted_key_references_fails_closed(self):
        step = """      - run: |
          p=pathlib.Path("artifacts/R254_FIXTURE_RUNTIME_MANIFEST.json")
          d=json.loads(p.read_text())
          print(d)
"""
        with self.assertRaisesRegex(
            p.PreflightError,
            "no statically verifiable key references",
        ):
            p.check_contract(hardened_workflow(step), HARDENED_GENERATOR)

    def test_manifest_step_delegated_to_unknown_helper_fails_closed(self):
        step = """      - run: |
          python validate_fixture.py --manifest artifacts/R254_FIXTURE_RUNTIME_MANIFEST.json
"""
        with self.assertRaisesRegex(
            p.PreflightError,
            "no statically traceable json.loads binding",
        ):
            p.check_contract(hardened_workflow(step), HARDENED_GENERATOR)


    def test_checkout_env_fetch_depth_does_not_satisfy_checkout_input(self):
        wf = """jobs:
  verify:
    steps:
      - uses: actions/checkout@v4
        env:
          fetch-depth: 0
      - run: |
          git merge-base --is-ancestor "$PROTOCOL_COMMIT" HEAD
      - run: |
          p=pathlib.Path("artifacts/R254_FIXTURE_RUNTIME_MANIFEST.json")
          d=json.loads(p.read_text())
          assert d["seed"] == 254001
"""
        with self.assertRaisesRegex(p.PreflightError, "checkout.*with.*fetch-depth"):
            p.check_contract(wf, HARDENED_GENERATOR)

    def test_manifest_clear_fails_closed(self):
        generator = HARDENED_GENERATOR.replace(
            'm.update({"fixture_id": "x", "seed": 254001, "width": 1024, "depth": 16})',
            'm.update({"fixture_id": "x", "seed": 254001, "width": 1024, "depth": 16})\n    m.clear()',
        )
        with self.assertRaisesRegex(p.PreflightError, "unsupported manifest mutation.*clear"):
            p.check_contract(hardened_workflow(inline_manifest_step("seed")), generator)

    def test_manifest_pop_fails_closed(self):
        generator = HARDENED_GENERATOR.replace(
            'm.update({"fixture_id": "x", "seed": 254001, "width": 1024, "depth": 16})',
            'm.update({"fixture_id": "x", "seed": 254001, "width": 1024, "depth": 16})\n    m.pop("seed")',
        )
        with self.assertRaisesRegex(p.PreflightError, "unsupported manifest mutation.*pop"):
            p.check_contract(hardened_workflow(inline_manifest_step("seed")), generator)

    def test_unknown_manifest_mutation_helper_fails_closed(self):
        generator = HARDENED_GENERATOR.replace(
            "def main():",
            'def mutate_manifest(value):\n    value.pop("seed")\n\ndef main():',
        ).replace(
            'm.update({"fixture_id": "x", "seed": 254001, "width": 1024, "depth": 16})',
            'm.update({"fixture_id": "x", "seed": 254001, "width": 1024, "depth": 16})\n    mutate_manifest(m)',
        )
        with self.assertRaisesRegex(p.PreflightError, "unsupported manifest mutation.*mutate_manifest"):
            p.check_contract(hardened_workflow(inline_manifest_step("seed")), generator)

    def test_json_loads_must_read_exact_manifest_path(self):
        step = """      - run: |
          p=pathlib.Path("artifacts/R254_FIXTURE_RUNTIME_MANIFEST.json")
          other=pathlib.Path("artifacts/other.json")
          d=json.loads(other.read_text() + ("" if p else ""))
          assert d["seed"] == 254001
"""
        with self.assertRaisesRegex(p.PreflightError, "exact runtime manifest path"):
            p.check_contract(hardened_workflow(step), HARDENED_GENERATOR)

    def test_get_access_is_not_silently_ignored(self):
        step = """      - run: |
          p=pathlib.Path("artifacts/R254_FIXTURE_RUNTIME_MANIFEST.json")
          d=json.loads(p.read_text())
          assert d["seed"] == 254001
          assert d.get("ghost") is None
"""
        with self.assertRaisesRegex(p.PreflightError, "unsupported manifest access.*get"):
            p.check_contract(hardened_workflow(step), HARDENED_GENERATOR)



if __name__ == "__main__":
    unittest.main()
