#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

import numpy as np

from methods.e123_multisource_verifier_fixture import (
    build_adversarial_12d_fixture,
    dense_vs_latent_probe_error,
    fixture_replay_equal,
)

OUT = Path("e123-independent-multisource-verifier.json")
E122_PROTOCOL = Path("research/E122_PROTOCOL.md")
E128_REGISTRY = Path("research/E128_ID_REGISTRY.json")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _candidate_inventory() -> dict:
    method_files = sorted(str(p) for p in Path("methods").glob("e122*.py"))
    script_files = sorted(str(p) for p in Path("scripts").glob("e122*.py"))
    manifests = [
        str(p)
        for p in [
            Path("research/E122_CANDIDATE_MANIFEST.json"),
            Path("research/E122_OWNER_PROTOCOL.md"),
            Path("research/E122_IMPLEMENTATION_PROTOCOL.md"),
            Path("research/E122_RECEIPT.json"),
            Path("research/E122_RESULT_RECEIPT.json"),
        ]
        if p.exists()
    ]
    return {
        "method_files": method_files,
        "script_files": script_files,
        "supporting_files": manifests,
        "candidate_code_present": bool(method_files or script_files),
        "candidate_manifest_present": Path(
            "research/E122_CANDIDATE_MANIFEST.json"
        ).exists(),
    }


def _protocol_readiness() -> dict:
    text = E122_PROTOCOL.read_text(encoding="utf-8")
    low = text.lower()
    protocol_only = (
        "protocol only" in low
        and "no scientific run authorized" in low
    )
    required_before_code = all(
        phrase in low
        for phrase in [
            "source-state representation and dimension",
            "compression operator",
            "deterministic seeds",
            "complete all-in flop accounting",
            "numerical pass/no-go gates",
            "target-access audit",
            "one-run/no-rescue discipline",
        ]
    )
    return {
        "path": str(E122_PROTOCOL),
        "sha256": _sha256_file(E122_PROTOCOL),
        "declares_protocol_only": protocol_only,
        "lists_required_owner_freeze_fields": required_before_code,
        "implementation_level_protocol_present": (
            Path("research/E122_OWNER_PROTOCOL.md").exists()
            or Path("research/E122_IMPLEMENTATION_PROTOCOL.md").exists()
        ),
    }


def _registry_readiness() -> dict:
    reg = json.loads(E128_REGISTRY.read_text(encoding="utf-8"))
    e122 = reg.get("ids", {}).get("E122", {})
    return {
        "path": str(E128_REGISTRY),
        "sha256": _sha256_file(E128_REGISTRY),
        "e122_status": e122.get("status"),
        "authoritative_branch": e122.get("authoritative_branch"),
        "protocol": e122.get("protocol"),
        "receipt": e122.get("receipt"),
        "run": e122.get("run"),
        "decision": e122.get("decision"),
    }


def _candidate_source_firewall_inventory(paths: list[str]) -> dict:
    forbidden_terms = [
        "e114_exact",
        "exact_reference",
        "whestbench",
        "benchmark",
        "public_mini",
        "official_scorer",
        "holdout",
        "final_means",
        "target",
        "oracle",
        "e123_multisource_verifier_fixture",
    ]
    hits = []
    for item in paths:
        p = Path(item)
        if not p.exists() or p.suffix != ".py":
            continue
        source = p.read_text(encoding="utf-8")
        for term in forbidden_terms:
            if re.search(re.escape(term), source, flags=re.IGNORECASE):
                hits.append({"path": item, "term": term})
    return {
        "scanned_paths": paths,
        "forbidden_term_hits": hits,
        "static_firewall_pass": bool(paths) and not hits,
    }


def main() -> None:
    protocol = _protocol_readiness()
    registry = _registry_readiness()
    inventory = _candidate_inventory()
    candidate_paths = inventory["method_files"] + inventory["script_files"]
    firewall_inventory = _candidate_source_firewall_inventory(candidate_paths)

    fixture_a = build_adversarial_12d_fixture()
    fixture_b = build_adversarial_12d_fixture()

    replay_exact = fixture_replay_equal(fixture_a, fixture_b)
    q_orth_error = float(
        np.max(
            np.abs(
                fixture_a.mixing_q.T @ fixture_a.mixing_q
                - np.eye(12, dtype=np.float64)
            )
        )
    )
    forward_equivalence_error = dense_vs_latent_probe_error(fixture_a)
    dense_first_layer_nonzeros = int(
        np.count_nonzero(np.abs(fixture_a.dense_weights[0]) > 1e-14)
    )

    e122_ready = bool(
        not protocol["declares_protocol_only"]
        and protocol["implementation_level_protocol_present"]
        and inventory["candidate_code_present"]
        and inventory["candidate_manifest_present"]
        and registry["authoritative_branch"] is not None
    )

    if e122_ready:
        candidate_specific = {
            "deterministic_replay": "NOT_IMPLEMENTED_IN_THIS_SNAPSHOT",
            "target_oracle_firewall": "NOT_IMPLEMENTED_IN_THIS_SNAPSHOT",
            "error_certificate": "NOT_IMPLEMENTED_IN_THIS_SNAPSHOT",
            "all_in_cost": "NOT_IMPLEMENTED_IN_THIS_SNAPSHOT",
        }
        decision = "INSTRUMENT_NO_GO_UNEXPECTED_READY_STATE"
    else:
        candidate_specific = {
            "deterministic_replay": "UNEXECUTED_BY_READINESS_GATE",
            "target_oracle_firewall": "UNEXECUTED_BY_READINESS_GATE",
            "error_certificate": "UNEXECUTED_BY_READINESS_GATE",
            "all_in_cost": "UNEXECUTED_BY_READINESS_GATE",
        }
        decision = "BLOCKED_BY_MISSING_E122_CANDIDATE"

    fixture_gates = {
        "fixture_replay_exact": replay_exact,
        "mixing_orthogonality_le_2e_12": q_orth_error <= 2e-12,
        "dense_vs_latent_probe_error_le_1e_12": (
            forward_equivalence_error <= 1e-12
        ),
        "exact_mean_finite": bool(np.isfinite(fixture_a.exact_mean).all()),
        "exact_mean_shape_12": fixture_a.exact_mean.shape == (12,),
        "dense_first_layer_materially_dense": dense_first_layer_nonzeros >= 120,
    }

    result = {
        "schema": "arc.whitebox.e123.independent_multisource_verifier.v1",
        "experiment": "E123",
        "idempotency_key": (
            "ARC-E123-INDEPENDENT-MULTISOURCE-VERIFIER-20260920"
        ),
        "decision": decision,
        "e122_readiness": {
            "ready_for_candidate_verification": e122_ready,
            "protocol": protocol,
            "registry": registry,
            "candidate_inventory": inventory,
        },
        "adversarial_fixture": {
            "input_dimension": 12,
            "output_width": 12,
            "relu_depth": 4,
            "independent_source_pairs": 6,
            "block_subnetwork_seeds": [
                123300,
                123301,
                123302,
                123303,
                123304,
                123305,
            ],
            "orthogonal_mixing_seed": 123390,
            "candidate_visible_weights": "four dense/full 12x12 matrices only",
            "candidate_visible_block_decomposition": False,
            "fixture_sha256": fixture_a.fixture_sha256,
            "exact_mean_sha256": _sha256_bytes(
                np.ascontiguousarray(
                    fixture_a.exact_mean, dtype=np.float64
                ).tobytes()
            ),
            "mixing_q_sha256": _sha256_bytes(
                np.ascontiguousarray(
                    fixture_a.mixing_q, dtype=np.float64
                ).tobytes()
            ),
            "dense_first_layer_nonzeros_gt_1e_14": (
                dense_first_layer_nonzeros
            ),
            "mixing_orthogonality_max_abs": q_orth_error,
            "dense_vs_latent_probe_max_abs": forward_equivalence_error,
            "deterministic_fixture_replay_exact": replay_exact,
        },
        "fixture_gates": fixture_gates,
        "candidate_firewall_inventory": firewall_inventory,
        "candidate_specific_checks": candidate_specific,
        "classification": {
            "fixture_verifier_ready": bool(all(fixture_gates.values())),
            "e122_candidate_scientific_verdict": "UNEXECUTED",
            "reason": (
                "Repository contains only the protocol-only E122 reservation; "
                "no authoritative implementation-level owner protocol, "
                "candidate module/manifest, receipt, or scientific run exists."
            ),
            "no_surrogate_candidate_invented": True,
        },
        "scope": {
            "canonical_mutated": False,
            "ledger_mutated": False,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "production_run": False,
            "target_fit": False,
            "e121_rerun": False,
        },
    }

    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "E123_INDEPENDENT_VERIFIER="
        + json.dumps(result, sort_keys=True),
        flush=True,
    )

    if not all(fixture_gates.values()):
        raise SystemExit(2)
    if e122_ready:
        # Fail closed: this frozen verifier snapshot was explicitly constructed
        # for the observed candidate-missing repository state.
        raise SystemExit(3)


if __name__ == "__main__":
    main()
