#!/usr/bin/env python3
"""R236 synthetic predicate checks for R234 verifier fail-closed behavior.

No R218 artifact is read. This reproduces only the relevant boolean predicates
from research/r234/r234_verify_r218.py blob
772843d4bc2b5929e851e621f33dd25a38cd5319.
"""
import json

ESTIMATOR_SHA256 = "86d9ca9b28e6fe2b6c74750a0b6ae4bba4c14f742ddc3f5f56bc7fb4ec9d8e27"
DATASET_SHA256 = "264fa1f416d16a40821fb5e8e94f5d2da4698a201d40da999616225b38b464f1"

# Case 1: verifier accepts an existing but empty sha256.json.
manifest_ok = True
manifest = {}
manifest_errors = []
for rel, digest in sorted(manifest.items()):
    raise AssertionError("empty manifest should not iterate")
empty_manifest_pass = manifest_ok and not manifest_errors

# Case 2: expected-panel file is not pinned by blob/SHA in verifier.
panel = [
    {"mlp_index": i, "mlp_name": f"synthetic-{i}", "measured_flops": 123 + i}
    for i in range(50)
]
expected = {
    "dataset": {"sha256": DATASET_SHA256},
    "source": {"sha256": ESTIMATOR_SHA256},
    "panel": panel,
}
unpinned_expected_panel_gates_pass = all([
    len(panel) == 50,
    [x["mlp_index"] for x in panel] == list(range(50)),
    expected["dataset"]["sha256"] == DATASET_SHA256,
    expected["source"]["sha256"] == ESTIMATOR_SHA256,
    True,  # artifact copy can match the same unpinned supplied file
])

# Case 3: external provenance predicate does not require run_attempt == 1.
github = {
    "GITHUB_RUN_ID": "123",
    "GITHUB_RUN_ATTEMPT": "2",
    "GITHUB_JOB": "crossover",
}
actions_evidence = {
    "run_id": "123",
    "run_attempt": "2",
    "job_name": "crossover",
    "single_crossover_job_verified": True,
    "executor_commit": "85f5ba13236aad07bf31436b356cfa2a3744ad33",
    "estimator_source_sha256_verified": ESTIMATOR_SHA256,
}
attempt2_actions_pass = (
    str(actions_evidence.get("run_id")) == str(github.get("GITHUB_RUN_ID"))
    and str(actions_evidence.get("run_attempt")) == str(github.get("GITHUB_RUN_ATTEMPT"))
    and actions_evidence.get("job_name") == github.get("GITHUB_JOB") == "crossover"
    and actions_evidence.get("single_crossover_job_verified") is True
    and actions_evidence.get("executor_commit")
        == "85f5ba13236aad07bf31436b356cfa2a3744ad33"
    and actions_evidence.get("estimator_source_sha256_verified") == ESTIMATOR_SHA256
)

# Case 4: preflight gate-map predicate does not require the frozen gate names.
pgates = {"unrelated": True}
incomplete_preflight_map_pass = bool(pgates) and all(pgates.values())

result = {
    "schema": "arc.whitebox.r236.synthetic_fail_closed.v1",
    "r234_verifier_blob": "772843d4bc2b5929e851e621f33dd25a38cd5319",
    "uses_r218_artifact": False,
    "cases": {
        "empty_manifest_gate_passes": empty_manifest_pass,
        "unpinned_expected_panel_predicates_pass": unpinned_expected_panel_gates_pass,
        "actions_run_attempt_2_predicate_passes": attempt2_actions_pass,
        "incomplete_preflight_gate_map_predicate_passes": incomplete_preflight_map_pass,
    },
}
print(json.dumps(result, indent=2, sort_keys=True))
