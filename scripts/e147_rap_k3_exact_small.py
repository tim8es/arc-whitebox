#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import math
from pathlib import Path

import numpy as np

from methods.e147_rap_k3 import (
    BUDGET_FLOPS,
    CAP_FLOPS,
    production_cost_receipt,
    rap_k3_estimate,
    ranks_for_width,
)

OUT = Path("e147-rap-k3-exact-small.json")
CANDIDATE_PATH = Path("methods/e147_rap_k3.py")
PROTOCOL_COMMIT = "daf997a9b1204f7916e9f5b78eba3aa6ff113d49"


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _rel(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    return float(
        np.linalg.norm(aa - bb)
        / max(float(np.linalg.norm(bb)), 2.0 ** -500)
    )


def _dense32_weights() -> list[np.ndarray]:
    n = 32
    rng = np.random.Generator(np.random.PCG64(147032))
    return [
        rng.normal(0.0, math.sqrt(2.0 / n), size=(n, n)).astype(np.float64)
        for _ in range(8)
    ]


def _adversarial16_weights() -> list[np.ndarray]:
    n = 16
    rng = np.random.Generator(np.random.PCG64(147016))
    out = []
    base_gain = np.geomspace(0.65, 1.35, n)
    for layer in range(8):
        qa, _ = np.linalg.qr(rng.standard_normal((n, n)))
        qb, _ = np.linalg.qr(rng.standard_normal((n, n)))
        gain = np.roll(base_gain, layer)
        w = math.sqrt(2.0) * qa @ np.diag(gain) @ qb.T
        out.append(np.asarray(w, dtype=np.float64))
    return out


def _source_audit() -> dict:
    src = CANDIDATE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(src)
    imports = []
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "open", "eval", "exec"
            }:
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                name = ast.unparse(node.func).lower()
                if any(
                    x in name
                    for x in (
                        "read_text", "read_bytes", "urlopen",
                        "request", "download", "loadtxt",
                        "genfromtxt", "read_csv", "read_parquet",
                    )
                ):
                    calls.append(name)

    forbidden_imports = [
        x for x in imports
        if any(
            term in x.lower()
            for term in (
                "e147_exact", "whestbench", "dataset",
                "scorer", "requests", "urllib",
            )
        )
    ]
    low = src.lower()
    forbidden_tokens = {
        "countsketch": "countsketch" in low,
        "smv_rank4": "rank4" in low or "rank-4" in low,
        "public_dataset": "whestbench" in low,
        "scorer": "official_scorer" in low or "score_submission" in low,
        "holdout": "holdout" in low,
        "e145_patch": "e145" in low,
    }
    sig = inspect.signature(rap_k3_estimate)
    params = list(sig.parameters)
    shape_ok = params == ["weights", "final_basis_seed"]

    return {
        "candidate_sha256": hashlib.sha256(src.encode("utf-8")).hexdigest(),
        "imports": sorted(imports),
        "forbidden_imports": forbidden_imports,
        "io_network_calls": calls,
        "forbidden_tokens": forbidden_tokens,
        "callable_parameters": params,
        "callable_only_weights_and_final_basis_seed": shape_ok,
        "passes": bool(
            not forbidden_imports
            and not calls
            and not any(forbidden_tokens.values())
            and shape_ok
        ),
    }


def _independent_cost() -> dict:
    n = 1024
    q = 96
    r = 48
    transitions = 15
    parts = {
        "retained_low_order_public_style_allowance": 38 * (2**31),
        "backward_response_basis_dense": transitions * 2 * n * n * (q + r),
        "thin_qr_sign_canonicalization": transitions * 8 * n * (q*q + r*r),
        "projected_k3_core_transport": transitions * (
            4 * r * q**3 + 2 * r*r*q*q
        ),
        "d21_response_and_surrogate": transitions * (
            2*n*q*q*r + 2*n*n*r
        ),
        "direct_projected_nonlinear_k3_birth": transitions * (
            8*n*q*q*r + 8*n*q*r*r + 16*n*n*r
        ),
        "error_certificate": transitions * (
            8*n*q*q*r + 8*n*n*r
        ),
        "helper_accounting_reserve": 10 * (2**31),
    }
    total = int(sum(parts.values()))
    return {
        **parts,
        "all_in_upper": total,
        "budget_flops": BUDGET_FLOPS,
        "cap_flops": int(math.floor(0.135 * BUDGET_FLOPS)),
        "utilization": total / float(BUDGET_FLOPS),
        "slack_flops": int(math.floor(0.135 * BUDGET_FLOPS)) - total,
    }


def _candidate_freeze(candidate) -> dict:
    return {
        "final_mean_sha256": _sha(candidate.final_mean),
        "final_pre_d3_sha256": _sha(candidate.final_pre_d3),
        "layer_core_sha256": [_sha(x.core) for x in candidate.layers],
        "layer_d3_sha256": [_sha(x.d3) for x in candidate.layers],
        "layer_d21_sha256": [_sha(x.d21) for x in candidate.layers],
        "layer_rho": [float(x.rho) for x in candidate.layers],
        "layer_rel_certificate": [
            float(x.d21_rel_certificate) for x in candidate.layers
        ],
        "pooled_d21_certificate": float(candidate.pooled_d21_certificate),
        "final_mean_certificate": float(candidate.final_mean_certificate),
        "production_cost": candidate.production_cost,
    }


def _candidate_equal(a, b) -> bool:
    if not np.array_equal(a.final_mean, b.final_mean):
        return False
    if not np.array_equal(a.final_pre_d3, b.final_pre_d3):
        return False
    if a.final_mean_certificate != b.final_mean_certificate:
        return False
    if a.pooled_d21_certificate != b.pooled_d21_certificate:
        return False
    for x, y in zip(a.layers, b.layers):
        if not np.array_equal(x.core, y.core):
            return False
        if not np.array_equal(x.d3, y.d3):
            return False
        if not np.array_equal(x.d21, y.d21):
            return False
        if (
            x.rho != y.rho
            or x.d21_rel_certificate != y.d21_rel_certificate
            or x.transport_projection_bound != y.transport_projection_bound
            or x.birth_projection_bound != y.birth_projection_bound
            or x.fp_bound != y.fp_bound
        ):
            return False
    return True


def _materialize_candidate_tensor(core, u, v) -> np.ndarray:
    return np.einsum(
        "abc,ia,jb,kc->ijk",
        core, u, u, v, optimize=True
    )


def _transport_identity_errors(candidate) -> list[float]:
    errs = []
    for l in range(1, len(candidate.layers)):
        prev = candidate.layers[l - 1]
        cur = candidate.layers[l]
        khat = _materialize_candidate_tensor(
            prev.core,
            candidate.bases_u[l - 1],
            candidate.bases_v[l - 1],
        )
        t = candidate.transports[l]
        transported = np.einsum(
            "abc,ia,jb,kc->ijk",
            khat, t, t, t, optimize=True
        )
        projected = np.einsum(
            "ijk,ia,jb,kc->abc",
            transported,
            candidate.bases_u[l],
            candidate.bases_u[l],
            candidate.bases_v[l],
            optimize=True,
        )
        errs.append(_rel(cur.transport_core, projected))
    return errs


def _run_fixture(
    *,
    name: str,
    weights: list[np.ndarray],
    final_basis_seed: int,
) -> dict:
    n = weights[0].shape[0]
    q, r = ranks_for_width(n)

    candidate = rap_k3_estimate(
        weights, final_basis_seed=final_basis_seed
    )
    replay = rap_k3_estimate(
        weights, final_basis_seed=final_basis_seed
    )
    deterministic = _candidate_equal(candidate, replay)

    # Candidate state is frozen and hashed before verifier-only dense K3 exists.
    frozen = _candidate_freeze(candidate)
    weights_sha = hashlib.sha256(
        b"".join(np.ascontiguousarray(w).tobytes() for w in weights)
    ).hexdigest()

    # Verifier-only materialization begins here.
    from methods.e147_exact_dense_k3_reference import build_exact_reference

    exact = build_exact_reference(weights)

    layer_d21_rel = []
    layer_d21_abs = []
    layer_d3_abs2 = 0.0
    layer_d3_ref2 = 0.0
    d21_abs2 = 0.0
    d21_ref2 = 0.0
    cert_contains = []
    cert_rel_contains = []

    for cand_layer, ref_layer in zip(candidate.layers, exact.layers):
        ea = float(np.linalg.norm(cand_layer.d21 - ref_layer.d21))
        er = max(float(np.linalg.norm(ref_layer.d21)), 2.0 ** -500)
        rel = ea / er
        layer_d21_abs.append(ea)
        layer_d21_rel.append(rel)
        d21_abs2 += ea * ea
        d21_ref2 += er * er

        d3e = float(np.linalg.norm(cand_layer.d3 - ref_layer.d3))
        d3r = max(float(np.linalg.norm(ref_layer.d3)), 2.0 ** -500)
        layer_d3_abs2 += d3e * d3e
        layer_d3_ref2 += d3r * d3r

        scale = max(1.0, er)
        cert_contains.append(
            ea <= cand_layer.d21_abs_certificate + 1e-12 * scale
        )
        cert_rel_contains.append(
            rel <= cand_layer.d21_rel_certificate + 1e-12
            if math.isfinite(cand_layer.d21_rel_certificate)
            else True
        )

    pooled_d21 = math.sqrt(d21_abs2 / max(d21_ref2, 2.0 ** -1000))
    pooled_d3 = math.sqrt(
        layer_d3_abs2 / max(layer_d3_ref2, 2.0 ** -1000)
    )
    final_rel = _rel(candidate.final_mean, exact.final_mean)
    final_abs = float(np.linalg.norm(candidate.final_mean - exact.final_mean))
    final_scale = max(1.0, float(np.linalg.norm(exact.final_mean)))
    final_cert_contains = (
        final_abs <= candidate.final_mean_certificate + 1e-12 * final_scale
    )

    transport_errors = _transport_identity_errors(candidate)
    pullback_max = max(
        max(x.pullback_residual_u, x.pullback_residual_v)
        for x in candidate.layers
    )

    scaffold_max = 0.0
    for cst, rst in zip(candidate.scaffold, exact.layers):
        scaffold_max = max(
            scaffold_max,
            float(np.max(np.abs(cst.mean - rst.mean))),
            float(np.max(np.abs(cst.covariance - rst.covariance))),
            float(np.max(np.abs(cst.wick1 - rst.wick1))),
            float(np.max(np.abs(cst.birth_k3 - rst.birth_k3))),
        )

    finite = bool(candidate.finite and exact.finite)
    return {
        "name": name,
        "width": int(n),
        "depth": 8,
        "q": int(q),
        "r": int(r),
        "weights_sha256": weights_sha,
        "candidate_frozen_before_reference": frozen,
        "reference_materialized_after_candidate_freeze": True,
        "deterministic_replay_bitwise_exact": deterministic,
        "finite": finite,
        "pullback_residual_max": float(pullback_max),
        "transport_identity_relative_errors": transport_errors,
        "transport_identity_max_relative_error": float(max(transport_errors)),
        "scaffold_candidate_reference_max_abs": float(scaffold_max),
        "layer_d21_relative_errors": layer_d21_rel,
        "layer_d21_absolute_errors": layer_d21_abs,
        "pooled_d21_relative_rms": float(pooled_d21),
        "max_layer_d21_relative_error": float(max(layer_d21_rel)),
        "pooled_d3_relative_rms": float(pooled_d3),
        "final_mean_relative_rms": float(final_rel),
        "final_mean_absolute_l2_error": final_abs,
        "certificate_contains_every_d21_layer": bool(all(cert_contains)),
        "relative_certificate_contains_every_d21_layer": bool(
            all(cert_rel_contains)
        ),
        "d21_relative_certificates": [
            float(x.d21_rel_certificate) for x in candidate.layers
        ],
        "d21_absolute_certificates": [
            float(x.d21_abs_certificate) for x in candidate.layers
        ],
        "pooled_certified_d21_relative_error": float(
            candidate.pooled_d21_certificate
        ),
        "final_mean_certificate": float(candidate.final_mean_certificate),
        "final_mean_certificate_contains_error": bool(final_cert_contains),
        "exact_final_mean_sha256": _sha(exact.final_mean),
        "exact_layer_d3_sha256": [_sha(x.d3) for x in exact.layers],
        "exact_layer_d21_sha256": [_sha(x.d21) for x in exact.layers],
    }


def main() -> None:
    audit = _source_audit()
    records = [
        _run_fixture(
            name="dense32",
            weights=_dense32_weights(),
            final_basis_seed=147320,
        ),
        _run_fixture(
            name="adversarial16",
            weights=_adversarial16_weights(),
            final_basis_seed=147160,
        ),
    ]

    prod = production_cost_receipt()
    independent = _independent_cost()
    cost_keys = (
        "retained_low_order_public_style_allowance",
        "backward_response_basis_dense",
        "thin_qr_sign_canonicalization",
        "projected_k3_core_transport",
        "d21_response_and_surrogate",
        "direct_projected_nonlinear_k3_birth",
        "error_certificate",
        "helper_accounting_reserve",
        "all_in_upper",
        "budget_flops",
        "cap_flops",
        "slack_flops",
    )
    cost_match = all(prod[k] == independent[k] for k in cost_keys)

    gates = {
        "finite_all": all(x["finite"] for x in records),
        "deterministic_replay_bitwise_exact_all": all(
            x["deterministic_replay_bitwise_exact"] for x in records
        ),
        "backward_pullback_residual_le_1e_12_all": all(
            x["pullback_residual_max"] <= 1e-12 for x in records
        ),
        "projected_core_transport_identity_le_1e_11_all": all(
            x["transport_identity_max_relative_error"] <= 1e-11
            for x in records
        ),
        "candidate_source_audit_pass": bool(audit["passes"]),
        "reference_after_candidate_freeze_all": all(
            x["reference_materialized_after_candidate_freeze"]
            for x in records
        ),
        "no_public_publicmini_scorer_holdout_full_submission": True,
        "pooled_d21_relative_rms_le_0_022_both": all(
            x["pooled_d21_relative_rms"] <= 0.022 for x in records
        ),
        "max_layer_d21_relative_error_le_0_030_both": all(
            x["max_layer_d21_relative_error"] <= 0.030 for x in records
        ),
        "pooled_d3_relative_rms_le_0_022_both": all(
            x["pooled_d3_relative_rms"] <= 0.022 for x in records
        ),
        "final_mean_relative_rms_le_0_022_both": all(
            x["final_mean_relative_rms"] <= 0.022 for x in records
        ),
        "certificate_contains_every_exact_d21_error": all(
            x["certificate_contains_every_d21_layer"] for x in records
        ),
        "relative_certificate_contains_every_exact_d21_error": all(
            x["relative_certificate_contains_every_d21_layer"]
            for x in records
        ),
        "certified_d21_relative_error_le_0_030_every_layer": all(
            all(
                math.isfinite(v) and v <= 0.030
                for v in x["d21_relative_certificates"]
            )
            for x in records
        ),
        "pooled_certified_d21_relative_error_le_0_022_both": all(
            math.isfinite(x["pooled_certified_d21_relative_error"])
            and x["pooled_certified_d21_relative_error"] <= 0.022
            for x in records
        ),
        "final_mean_error_contained_by_certificate_both": all(
            x["final_mean_certificate_contains_error"] for x in records
        ),
        "production_cost_formula_exact_reconcile": bool(cost_match),
        "production_all_in_le_0_135B": bool(
            prod["all_in_upper"] <= CAP_FLOPS
        ),
    }

    integrity_keys = [
        "finite_all",
        "deterministic_replay_bitwise_exact_all",
        "backward_pullback_residual_le_1e_12_all",
        "projected_core_transport_identity_le_1e_11_all",
        "candidate_source_audit_pass",
        "reference_after_candidate_freeze_all",
        "no_public_publicmini_scorer_holdout_full_submission",
        "production_cost_formula_exact_reconcile",
        "production_all_in_le_0_135B",
    ]
    scientific_keys = [k for k in gates if k not in integrity_keys]
    integrity_go = bool(all(gates[k] for k in integrity_keys))
    scientific_go = bool(
        integrity_go and all(gates[k] for k in scientific_keys)
    )

    result = {
        "schema": "arc.whitebox.e147.rap_k3_exact_small.v1",
        "experiment": "E147",
        "idempotency_key": "ARC-E147-RESPONSE-PROJECTED-K3-ESTIMATOR-20260921",
        "protocol_commit": PROTOCOL_COMMIT,
        "mechanism": {
            "name": "RAP-K3",
            "persistent_source_stack": False,
            "full_d21_estimator_state": False,
            "response_aligned_projected_core": True,
            "production_q": 96,
            "production_r": 48,
            "small_q": 8,
            "small_r": 4,
            "closure_execution": (
                "target-free simple K3 leading closure: K2 Gaussian scaffold, "
                "Wick-linear represented-K3 transport, projected Gaussian-ReLU "
                "diagonal K3 birth"
            ),
            "rank_sweep": False,
            "basis_sweep": False,
            "certificate_sweep": False,
        },
        "source_audit": audit,
        "records": records,
        "production_cost": prod,
        "independent_production_cost": independent,
        "gates": gates,
        "integrity_go": integrity_go,
        "scientific_go": scientific_go,
        "physical_run_authorized": scientific_go,
        "decision": (
            "E147_EXACT_SMALL_GO_PHYSICAL_RUN_AUTHORIZED"
            if scientific_go
            else "E147_TERMINAL_NO_GO_CLOSE_RAP_K3"
        ),
        "scope": {
            "synthetic_exact_small_only": True,
            "target_free": True,
            "physical_1024x16_run": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "submission": False,
            "rank_sweep": False,
            "basis_sweep": False,
            "certificate_sweep": False,
            "rescue": False,
            "rerun": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }

    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("E147_RAP_K3_EXACT_SMALL=" + json.dumps(result, sort_keys=True))

    if not integrity_go:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
