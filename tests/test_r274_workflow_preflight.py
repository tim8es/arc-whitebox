from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import arc_workflow_preflight as p


BASE_GENERATOR = r'''
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


def inline_manifest_step(key='seed', named=True):
    prefix = "      - name: Check fixture\n        run: |" if named else "      - run: |"
    return f'''{prefix}
          import_placeholder=1
          p=pathlib.Path("artifacts/R254_FIXTURE_RUNTIME_MANIFEST.json")
          d=json.loads(p.read_text())
          assert d["{key}"] is not None
'''


def workflow(manifest_step, verify_checkout=True, extra_job=""):
    checkout = '''      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
''' if verify_checkout else '''      - uses: actions/checkout@v4
'''
    return f'''jobs:
{extra_job}  verify:
    steps:
{checkout}      - run: |
          git merge-base --is-ancestor "$PROTOCOL_COMMIT" HEAD
{manifest_step}'''


class WorkflowPreflightHardeningTests(unittest.TestCase):
    def test_unrelated_dict_cannot_legalize_manifest_key(self):
        generator = BASE_GENERATOR.replace(
            'def main():\n    _, truth, m = build_manifest()',
            'def main():\n    unrelated = {"ghost_only_elsewhere": True}\n    _, truth, m = build_manifest()'
        )
        with self.assertRaisesRegex(p.PreflightError, "ghost_only_elsewhere"):
            p.check_contract(workflow(inline_manifest_step("ghost_only_elsewhere")), generator)

    def test_manifest_schema_tracks_serialized_object_and_nested_helper(self):
        wf = workflow('''      - run: |
          p=pathlib.Path("artifacts/R254_FIXTURE_RUNTIME_MANIFEST.json")
          d=json.loads(p.read_text())
          assert d["seed"] == 254001
          assert d["independent_replay"]["layer_sha256"] == []
''')
        result = p.check_contract(wf, BASE_GENERATOR)
        self.assertEqual(
            result["asserted_manifest_keys"],
            ["independent_replay.layer_sha256", "seed"],
        )

    def test_full_checkout_in_other_job_does_not_satisfy_ancestry_job(self):
        other = '''  prep:
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
'''
        with self.assertRaisesRegex(p.PreflightError, "same job"):
            p.check_contract(
                workflow(inline_manifest_step(), verify_checkout=False, extra_job=other),
                BASE_GENERATOR,
            )

    def test_unnamed_run_manifest_assertion_is_checked(self):
        with self.assertRaisesRegex(p.PreflightError, "ghost"):
            p.check_contract(
                workflow(inline_manifest_step("ghost", named=False)),
                BASE_GENERATOR,
            )

    def test_manifest_read_without_extracted_key_references_fails_closed(self):
        step = '''      - run: |
          p=pathlib.Path("artifacts/R254_FIXTURE_RUNTIME_MANIFEST.json")
          d=json.loads(p.read_text())
          print(d)
'''
        with self.assertRaisesRegex(p.PreflightError, "no statically verifiable key references"):
            p.check_contract(workflow(step), BASE_GENERATOR)

    def test_manifest_step_delegated_to_unknown_helper_fails_closed(self):
        step = '''      - run: |
          python validate_fixture.py --manifest artifacts/R254_FIXTURE_RUNTIME_MANIFEST.json
'''
        with self.assertRaisesRegex(p.PreflightError, "no statically traceable json.loads binding"):
            p.check_contract(workflow(step), BASE_GENERATOR)


if __name__ == "__main__":
    unittest.main()
