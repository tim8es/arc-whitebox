#!/usr/bin/env python3
from __future__ import annotations

import ast
from dataclasses import fields
import hashlib
import inspect
import json
import math
from pathlib import Path

import numpy as np

from methods.e122_haar8_simplex_source import (
    CODEWORDS,
    PRODUCTION_CAP_FLOPS,
    PRODUCTION_DEPTH,
    PRODUCTION_DIM,
    PRODUCTION_DIRECTIONS,
    PRODUCTION_FRAMES,
    PRODUCTION_WIDTH,
    SOURCE_DIM,
    SimplexSourceEstimate,
    haar8_antipodal_simplex_mean,
    production_cost_receipt,
    regular_simplex_code,
    simplex_algebra_metrics,
)
from methods.e123_multisource_verifier_fixture import (
    build_candidate_visible_12d_fixture,
    candidate_visible_dense_latent_probe_error,
    forward_batch,
    materialize_exact_reference_after_candidate,
)

FRAMES = 224
SAMPLES = FRAMES * CODEWORDS
CANDIDATE_SEEDS = (123400, 123401, 123402, 123403)
IID_SEEDS = (123500, 123501, 123502, 123503)
RAW_MSE_SCALE = 1.89e-8
RATIO_GATE = 0.95
OUT = Path("e123-candidate-multisource-verifier.json")
CANDIDATE_PATH = Path("methods/e122_haar8_simplex_source.py")
E122_PROTOCOL_PATH = Path("research/E122_PROTOCOL.md")


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _mse(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.mean(d * d))


def _mean_chi(d: int) -> float:
    return math.sqrt(2.0) * math.exp(
        math.lgamma(0.5 * (d + 1.0)) - math.lgamma(0.5 * d)
    )


def _iid_spherical_mean(
    weights: tuple[np.ndarray, ...],
    *,
    samples: int,
    seed: int,
) -> np.ndarray:
    d = int(weights[0].shape[0])
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    z = rng.standard_normal((samples, d)).astype(np.float64)
    norms = np.linalg.norm(z, axis=1)
    if np.any(norms <= 0.0) or not np.isfinite(norms).all():
        raise RuntimeError("invalid iid verifier directions")
    q = z / norms[:, None]
    return _mean_chi(d) * np.mean(
        forward_batch(q, weights), axis=0, dtype=np.float64
    )


def _source_firewall_audit() -> dict:
    source = CANDIDATE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imports: list[str] = []
    dangerous_calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id in {"open", "eval", "exec"}:
                dangerous_calls.append(fn.id)
            if isinstance(fn, ast.Attribute):
                text = ast.unparse(fn)
                if any(
                    term in text.lower()
                    for term in [
                        "read_text",
                        "read_bytes",
                        "urlopen",
                        "request",
                        "download",
                    ]
                ):
                    dangerous_calls.append(text)

    forbidden_import_terms = [
        "e114",
        "e123",
        "whestbench",
        "dataset",
        "scorer",
        "requests",
        "urllib",
        "http",
    ]
    forbidden_imports = [
        imp
        for imp in imports
        if any(term in imp.lower() for term in forbidden_import_terms)
    ]

    sig = inspect.signature(haar8_antipodal_simplex_mean)
    params = list(sig.parameters)
    callable_shape_ok = params == ["weights", "frames", "seed"]

    return {
        "candidate_path": str(CANDIDATE_PATH),
        "candidate_sha256": hashlib.sha256(
            source.encode("utf-8")
        ).hexdigest(),
        "imports": sorted(imports),
        "forbidden_imports": forbidden_imports,
        "dangerous_io_or_network_calls": dangerous_calls,
        "callable_parameters": params,
        "callable_only_weights_frames_seed": callable_shape_ok,
        "passes": bool(
            not forbidden_imports
            and not dangerous_calls
            and callable_shape_ok
        ),
    }


def _error_certificate_audit() -> dict:
    protocol = E122_PROTOCOL_PATH.read_text(encoding="utf-8")
    result_fields = [f.name for f in fields(SimplexSourceEstimate)]
    certificate_fields = [
        x
        for x in result_fields
        if any(term in x.lower() for term in ["certificate", "error_bound", "bound"])
    ]
    has_declared_finite_sample_certificate = bool(
        "finite-sample error certificate" in protocol.lower()
        or "error certificate" in protocol.lower()
    )
    # The protocol uses the word "certificates" only in an exclusion about
    # omitted-boundary certificates. That is not a candidate error certificate.
    exclusion_only = "omitted-boundary certificates" in protocol.lower()
    if exclusion_only and not certificate_fields:
        has_declared_finite_sample_certificate = False

    return {
        "candidate_result_fields": result_fields,
        "candidate_certificate_fields": certificate_fields,
        "protocol_declares_computable_finite_sample_error_certificate": (
            has_declared_finite_sample_certificate
        ),
        "verdict": (
            "PASS"
            if has_declared_finite_sample_certificate and certificate_fields
            else "ERROR_CERTIFICATE_MISSING"
        ),
        "passes": bool(
            has_declared_finite_sample_certificate and certificate_fields
        ),
    }


def _independent_production_cost() -> dict:
    d = PRODUCTION_DIM
    n = PRODUCTION_WIDTH
    l = PRODUCTION_DEPTH
    k = SOURCE_DIM
    j = CODEWORDS
    p = PRODUCTION_FRAMES
    trajectories = PRODUCTION_DIRECTIONS

    simplex_setup = 8 * k * (k + 1) + 256
    frame_setup = p * (d * (2 * k * k + 17 * k) + 64 * k)
    source = p * (2 * d * k * j)
    deep = trajectories * l * (2 * n * n + 2 * n)
    final = trajectories * n + 2 * trajectories + 5 * n
    base_total = simplex_setup + frame_setup + source + deep + final

    orth_diag_per_frame = 2 * d * k * k + 3 * k * k
    source_norm_per_frame = j * (2 * d + 5)
    omitted_diagnostics = p * (orth_diag_per_frame + source_norm_per_frame)
    corrected_total = base_total + omitted_diagnostics

    return {
        "simplex_setup_upper": int(simplex_setup),
        "haar_frame_rng_mgs_upper": int(frame_setup),
        "source_code_materialization_upper": int(source),
        "deep_propagation_upper": int(deep),
        "final_reduction_radial_upper": int(final),
        "protocol_base_total": int(base_total),
        "orthogonality_diagnostic_per_frame": int(orth_diag_per_frame),
        "source_norm_diagnostic_per_frame": int(source_norm_per_frame),
        "omitted_diagnostic_total": int(omitted_diagnostics),
        "corrected_all_in_upper": int(corrected_total),
        "hard_cap_flops": int(PRODUCTION_CAP_FLOPS),
        "corrected_slack_flops": int(PRODUCTION_CAP_FLOPS - corrected_total),
        "corrected_total_passes_cap": bool(corrected_total <= PRODUCTION_CAP_FLOPS),
    }


def _cost_audit() -> dict:
    candidate = production_cost_receipt()
    independent = _independent_production_cost()

    numeric_match = bool(
        candidate["simplex_setup_upper"]
        == independent["simplex_setup_upper"]
        and candidate["haar_frame_rng_mgs_upper"]
        == independent["haar_frame_rng_mgs_upper"]
        and candidate["source_code_materialization_upper"]
        == independent["source_code_materialization_upper"]
        and candidate["deep_propagation_upper"]
        == independent["deep_propagation_upper"]
        and candidate["final_reduction_radial_upper"]
        == independent["final_reduction_radial_upper"]
        and candidate["all_in_upper"]
        == independent["protocol_base_total"]
    )

    source = CANDIDATE_PATH.read_text(encoding="utf-8")
    executes_orth_diag = "gram = q.T @ q" in source
    executes_source_norm_diag = "np.linalg.norm(q, axis=1)" in source
    operation_classes = []
    probe = haar8_antipodal_simplex_mean(
        [np.eye(8, dtype=np.float64)],
        frames=1,
        seed=123001,
    )
    operation_classes = list(probe.ledger.get("operation_classes_complete", []))

    ledger_names_diagnostics = any(
        "orthogon" in x.lower() or "source_direction_norm" in x.lower()
        for x in operation_classes
    )
    accounting_complete = bool(
        not (executes_orth_diag or executes_source_norm_diag)
        or ledger_names_diagnostics
    )

    return {
        "candidate_production_receipt": candidate,
        "independent_recompute": independent,
        "protocol_numeric_terms_match": numeric_match,
        "candidate_executes_orthogonality_diagnostic": executes_orth_diag,
        "candidate_executes_source_norm_diagnostic": executes_source_norm_diag,
        "ledger_operation_classes": operation_classes,
        "diagnostic_operation_classes_explicitly_billed": (
            ledger_names_diagnostics
        ),
        "accounting_complete": accounting_complete,
        "corrected_total_passes_cap": independent["corrected_total_passes_cap"],
        "passes": bool(
            numeric_match
            and accounting_complete
            and independent["corrected_total_passes_cap"]
        ),
    }


def _independent_small_ledger(weights: tuple[np.ndarray, ...]) -> dict:
    d = int(weights[0].shape[0])
    k = SOURCE_DIM
    j = CODEWORDS
    frames = FRAMES
    ntraj = frames * j
    out_width = int(weights[-1].shape[1])

    simplex = 8 * k * (k + 1) + 256
    frame = frames * (d * (2 * k * k + 17 * k) + 64 * k)
    source = frames * (2 * d * k * j)

    layer_flops = []
    previous = d
    for w in weights:
        out = int(w.shape[1])
        layer_flops.append(ntraj * (2 * previous * out + 2 * out))
        previous = out

    final = ntraj * out_width + 2 * ntraj + 5 * out_width
    total = simplex + frame + source + sum(layer_flops) + final
    return {
        "simplex_setup_upper": int(simplex),
        "haar_frame_rng_mgs_upper": int(frame),
        "source_code_materialization_upper": int(source),
        "deep_layer_flops": [int(x) for x in layer_flops],
        "deep_propagation_upper": int(sum(layer_flops)),
        "final_reduction_radial_upper": int(final),
        "all_in_upper": int(total),
    }


def main() -> None:
    # Candidate-visible construction intentionally does not materialize exact means.
    fixture = build_candidate_visible_12d_fixture()
    weights = fixture.dense_weights

    firewall = _source_firewall_audit()
    certificate = _error_certificate_audit()
    cost = _cost_audit()

    code = regular_simplex_code()
    simplex = simplex_algebra_metrics(code)

    candidate_records = []
    candidate_means = []
    iid_means = []
    deterministic_all = True
    ledger_replay_all = True
    finite_all = True
    orth_max = 0.0
    norm_max = 0.0
    small_ledger_match_all = True

    # Candidate and comparator run before exact reference materialization.
    for cseed, iseed in zip(CANDIDATE_SEEDS, IID_SEEDS):
        cand = haar8_antipodal_simplex_mean(
            weights, frames=FRAMES, seed=cseed
        )
        replay = haar8_antipodal_simplex_mean(
            weights, frames=FRAMES, seed=cseed
        )
        iid = _iid_spherical_mean(
            weights, samples=SAMPLES, seed=iseed
        )

        replay_exact = bool(
            np.array_equal(cand.mean, replay.mean)
            and cand.frame_orthogonality_max_abs
            == replay.frame_orthogonality_max_abs
            and cand.source_direction_norm_max_abs
            == replay.source_direction_norm_max_abs
        )
        ledger_exact = cand.ledger == replay.ledger
        independent_small = _independent_small_ledger(weights)
        small_match = all(
            cand.ledger[k] == independent_small[k]
            for k in independent_small
        )

        deterministic_all = deterministic_all and replay_exact
        ledger_replay_all = ledger_replay_all and ledger_exact
        small_ledger_match_all = small_ledger_match_all and small_match
        finite_all = finite_all and cand.finite
        orth_max = max(orth_max, cand.frame_orthogonality_max_abs)
        norm_max = max(norm_max, cand.source_direction_norm_max_abs)

        candidate_means.append(cand.mean.copy())
        iid_means.append(iid.copy())
        candidate_records.append(
            {
                "candidate_seed": cseed,
                "iid_seed": iseed,
                "candidate_mean_sha256": _sha(cand.mean),
                "iid_mean_sha256": _sha(iid),
                "deterministic_replay_bitwise_exact": replay_exact,
                "ledger_replay_exact": ledger_exact,
                "small_ledger_matches_independent_formula": small_match,
                "frame_orthogonality_max_abs": (
                    cand.frame_orthogonality_max_abs
                ),
                "source_direction_norm_max_abs": (
                    cand.source_direction_norm_max_abs
                ),
                "finite": cand.finite,
                "candidate_ledger": cand.ledger,
            }
        )

    # Firewall ordering: exact reference exists only from this point onward.
    exact_mean = materialize_exact_reference_after_candidate(fixture)
    exact_sha = _sha(exact_mean)

    for rec, cand_mean, iid_mean in zip(
        candidate_records, candidate_means, iid_means
    ):
        cmse = _mse(cand_mean, exact_mean)
        imse = _mse(iid_mean, exact_mean)
        rec.update(
            {
                "exact_mean_sha256": exact_sha,
                "candidate_mse": cmse,
                "iid_mse": imse,
                "candidate_over_iid": (
                    cmse / imse if imse > 0.0 else math.inf
                ),
                "candidate_over_raw_scale": cmse / RAW_MSE_SCALE,
            }
        )

    pooled_candidate = float(
        np.mean([r["candidate_mse"] for r in candidate_records])
    )
    pooled_iid = float(
        np.mean([r["iid_mse"] for r in candidate_records])
    )
    pooled_ratio = (
        pooled_candidate / pooled_iid if pooled_iid > 0.0 else math.inf
    )

    fixture_probe_error = candidate_visible_dense_latent_probe_error(fixture)

    algebra_pass = bool(
        simplex["max_vertex_norm_error"] <= 2e-14
        and simplex["max_vertex_gram_error"] <= 2e-14
        and simplex["vertex_sum_inf"] <= 2e-14
        and simplex["second_moment_max_abs_error"] <= 2e-14
    )

    gates = {
        "simplex_algebra_pass": algebra_pass,
        "candidate_outputs_finite_all": finite_all,
        "haar8_orthogonality_le_2e_12": orth_max <= 2e-12,
        "source_direction_norm_le_2e_12": norm_max <= 2e-12,
        "deterministic_replay_bitwise_exact_all": deterministic_all,
        "candidate_ledger_replay_exact_all": ledger_replay_all,
        "small_candidate_ledger_matches_independent_formula_all": (
            small_ledger_match_all
        ),
        "adversarial_12d_candidate_over_iid_le_0_95": (
            pooled_ratio <= RATIO_GATE
        ),
        "target_oracle_firewall_pass": firewall["passes"],
        "runtime_reference_materialized_after_candidate": True,
        "finite_sample_error_certificate_present_and_computable": (
            certificate["passes"]
        ),
        "production_cost_accounting_complete_and_under_cap": cost["passes"],
        "no_public_benchmark_scorer_holdout_full": True,
    }

    scientific_go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e123.e122_c733af8_verifier.v1",
        "experiment": "E123",
        "verified_experiment": "E122",
        "idempotency_key": (
            "ARC-E123-E122-C733AF8-ADVERSARIAL-12D-20260920"
        ),
        "frozen_e122": {
            "branch": (
                "research/e122-haar8-antipodal-simplex-source-code-20260920"
            ),
            "protocol_commit": (
                "fd2f2d93ed7be6124cd70485b561177c3b2787ad"
            ),
            "implementation_commit": (
                "3853efd5177f6931c7dcf884dd97f7342751ca03"
            ),
            "candidate_head": (
                "c733af8f3b179c9c9ef8314abc136b2ff6a7940b"
            ),
            "protocol_blob": "fca1c0a0beb88f3bf2573cd4620a886b9dfaa0e7",
            "candidate_blob": "bf03692f9c205805fbea4113ec9e17e9d1ce2811",
            "tests_blob": "7b6f1e80def4b76a00526c04c90b20bb008cfa6f",
        },
        "adversarial_fixture": {
            "input_dimension": 12,
            "output_width": 12,
            "relu_depth": 4,
            "independent_source_pairs": 6,
            "dense_input_mixing": True,
            "block_subnetwork_seeds": list(range(123300, 123306)),
            "mixing_seed": 123390,
            "candidate_seeds": list(CANDIDATE_SEEDS),
            "iid_seeds": list(IID_SEEDS),
            "directions_per_estimate": SAMPLES,
            "fixture_weights_sha256": fixture.fixture_weights_sha256,
            "dense_vs_latent_probe_max_abs": fixture_probe_error,
            "candidate_received_exact_reference": False,
            "candidate_received_block_decomposition": False,
            "exact_mean_sha256": exact_sha,
        },
        "simplex_algebra": simplex,
        "candidate_records": candidate_records,
        "error_summary": {
            "pooled_candidate_mse": pooled_candidate,
            "pooled_iid_mse": pooled_iid,
            "candidate_over_iid": pooled_ratio,
            "ratio_gate": RATIO_GATE,
            "candidate_over_raw_scale": pooled_candidate / RAW_MSE_SCALE,
            "raw_mse_scale_diagnostic": RAW_MSE_SCALE,
        },
        "determinism": {
            "bitwise_prediction_replay_all": deterministic_all,
            "ledger_replay_exact_all": ledger_replay_all,
            "max_frame_orthogonality_abs": orth_max,
            "max_source_direction_norm_abs": norm_max,
        },
        "firewall": firewall,
        "error_certificate": certificate,
        "cost": cost,
        "gates": gates,
        "scientific_go": scientific_go,
        "decision": (
            "E123_VERIFIED_E122_GO"
            if scientific_go
            else "E123_TERMINAL_NO_GO_FOR_FROZEN_E122_CANDIDATE"
        ),
        "scope": {
            "canonical_mutated": False,
            "ledger_mutated": False,
            "public": False,
            "public_mini": False,
            "benchmark_targets": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "production_execution": False,
            "e122_modified": False,
            "e122_rescue": False,
        },
    }

    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "E123_E122_VERIFIER=" + json.dumps(result, sort_keys=True),
        flush=True,
    )

    integrity_keys = [
        "simplex_algebra_pass",
        "candidate_outputs_finite_all",
        "haar8_orthogonality_le_2e_12",
        "source_direction_norm_le_2e_12",
        "deterministic_replay_bitwise_exact_all",
        "candidate_ledger_replay_exact_all",
        "small_candidate_ledger_matches_independent_formula_all",
        "target_oracle_firewall_pass",
        "runtime_reference_materialized_after_candidate",
        "no_public_benchmark_scorer_holdout_full",
    ]
    if not all(gates[k] for k in integrity_keys):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
