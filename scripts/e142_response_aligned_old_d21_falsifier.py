#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import math
from pathlib import Path

import numpy as np

from methods.e142_response_aligned_d21 import (
    BUDGET_FLOPS,
    MODULE_CAP_FLOPS,
    AdaptiveResult,
    ResidualState,
    TierFactors,
    adaptive_response_sequence,
    canonical_qr,
    heldout_projection,
    orientation_certificate,
    production_cost_receipt,
    response_basis,
)

OUT = Path("e142-response-aligned-old-d21.json")
CANDIDATE_PATH = Path("methods/e142_response_aligned_d21.py")


def _orth(rng: np.random.Generator, rows: int, cols: int) -> np.ndarray:
    q, _ = np.linalg.qr(rng.standard_normal((rows, cols)))
    q = q[:, :cols]
    for j in range(q.shape[1]):
        idx = int(np.argmax(np.abs(q[:, j])))
        if q[idx, j] < 0.0:
            q[:, j] *= -1.0
    return q


def _tier(
    rng: np.random.Generator,
    *,
    k: int,
    n: int,
    q: int,
    adversarial: bool,
) -> TierFactors:
    row = np.geomspace(1.0, 0.20 if adversarial else 0.55, n)
    col = np.geomspace(1.0, 0.30 if adversarial else 0.65, n)
    qscale = np.geomspace(1.0, 0.25 if adversarial else 0.60, q)

    la = rng.standard_normal((k, n, n)) * row[None, :, None] * col[None, None, :]
    lp = rng.standard_normal((k, n, n)) * row[None, :, None] * col[::-1][None, None, :]
    fa = rng.standard_normal((k, q, n)) * qscale[None, :, None] * col[None, None, :]
    fp = rng.standard_normal((k, q, n)) * qscale[::-1][None, :, None] * row[None, None, :]

    if adversarial and k >= 2:
        # Dense near-cancelling pairs stress the difference between a global
        # residual norm and response-aware source projections.
        for s in range(1, k, 2):
            la[s] = -0.94 * la[s - 1] + 0.08 * la[s]
            lp[s] = -0.91 * lp[s - 1] + 0.10 * lp[s]
            fa[s] = 0.97 * fa[s - 1] + 0.06 * fa[s]
            fp[s] = 0.93 * fp[s - 1] + 0.08 * fp[s]

    scale = 1.0 / math.sqrt(float(n))
    return TierFactors(
        la=np.asarray(la * scale, dtype=np.float64),
        lp=np.asarray(lp * scale, dtype=np.float64),
        fa=np.asarray(fa * scale, dtype=np.float64),
        fp=np.asarray(fp * scale, dtype=np.float64),
    )


def _materialize_tier(t: TierFactors) -> np.ndarray:
    out = np.zeros((t.la.shape[1], t.fa.shape[1]), dtype=np.float64)
    for s in range(t.la.shape[0]):
        out += t.la[s] @ t.fa[s].T
        out += t.lp[s] @ t.fp[s].T
    return out


def _materialize_d(
    q_c: np.ndarray,
    u2: np.ndarray,
    shared: TierFactors,
    nested: TierFactors,
) -> np.ndarray:
    inner = _materialize_tier(shared) + _materialize_tier(nested) @ u2.T
    return inner @ q_c.T


def _fixture(spec: dict) -> dict:
    rng = np.random.Generator(np.random.PCG64(int(spec["seed"])))
    n = int(spec["n"])
    q1 = int(spec["q1"])
    q2 = int(spec["q2"])
    r = int(spec["r"])
    adversarial = bool(spec["adversarial"])

    q_c = _orth(rng, n, q1)
    u2 = _orth(rng, q1, q2)

    retained_shared = _tier(
        rng, k=spec["retained_shared"], n=n, q=q1, adversarial=adversarial
    )
    omitted_shared = _tier(
        rng, k=spec["omitted_shared"], n=n, q=q1, adversarial=adversarial
    )
    retained_nested = _tier(
        rng, k=spec["retained_nested"], n=n, q=q2, adversarial=adversarial
    )
    omitted_nested = _tier(
        rng, k=spec["omitted_nested"], n=n, q=q2, adversarial=adversarial
    )

    # Materializing the retained contribution is allowed. The omitted/full D21
    # reference is intentionally not built here.
    retained_d = _materialize_d(
        q_c, u2, retained_shared, retained_nested
    )

    response_rng = np.random.Generator(
        np.random.PCG64(int(spec["seed"]) + 1000)
    )
    future_1 = response_rng.standard_normal((n, n)) / math.sqrt(float(n))
    future_2 = response_rng.standard_normal((n, n)) / math.sqrt(float(n))
    omega0 = response_rng.standard_normal((n, r))
    omega = canonical_qr(future_1 @ (future_2 @ omega0))

    held_rng = np.random.Generator(
        np.random.PCG64(int(spec["seed"]) + 2000)
    )
    heldout = canonical_qr(held_rng.standard_normal((n, r)))

    state = ResidualState(
        q_c=q_c,
        u2=u2,
        shared=omitted_shared,
        nested=omitted_nested,
    )
    return {
        "spec": spec,
        "q_c": q_c,
        "u2": u2,
        "retained_shared": retained_shared,
        "omitted_shared": omitted_shared,
        "retained_nested": retained_nested,
        "omitted_nested": omitted_nested,
        "retained_d": retained_d,
        "omega": omega,
        "heldout": heldout,
        "state": state,
    }


def _array_equal_adaptive(a: AdaptiveResult, b: AdaptiveResult) -> bool:
    names = ("y1", "q1", "z1", "y2", "q2", "b")
    if not all(np.array_equal(getattr(a, n), getattr(b, n)) for n in names):
        return False
    for xa, xb in zip(a.right_queries, b.right_queries):
        if not np.array_equal(xa, xb):
            return False
    for xa, xb in zip(a.left_queries, b.left_queries):
        if not np.array_equal(xa, xb):
            return False
    for xa, xb in zip(a.action_results, b.action_results):
        if not np.array_equal(xa.value, xb.value):
            return False
        if xa.fp_certificate != xb.fp_certificate:
            return False
        if xa.source_scale != xb.source_scale:
            return False
    return True


def _rel(a: np.ndarray, b: np.ndarray) -> float:
    den = max(float(np.linalg.norm(b)), 2.0**-500)
    return float(np.linalg.norm(np.asarray(a) - np.asarray(b)) / den)


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _source_audit() -> dict:
    src = CANDIDATE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(src)
    imports = []
    dangerous = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"open", "eval", "exec"}:
                dangerous.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                name = ast.unparse(node.func).lower()
                if any(x in name for x in ("read_text", "read_bytes", "urlopen", "request", "download")):
                    dangerous.append(name)

    low = src.lower()
    forbidden_tokens = {
        "countsketch": "countsketch" in low,
        "strassen": "strassen" in low,
        "smv_rank4": "rank-4" in low or "rank4" in low,
        "svd": ".svd" in low or "linalg.svd" in low,
        "benchmark": "whestbench" in low,
        "scorer": "scorer" in low,
        "target_fit": "target_fit" in low,
        "exact_reference_import": "exact_reference" in low,
    }
    sig = inspect.signature(adaptive_response_sequence)
    params = list(sig.parameters)
    return {
        "candidate_sha256": hashlib.sha256(src.encode()).hexdigest(),
        "imports": sorted(imports),
        "dangerous_io_network_calls": dangerous,
        "forbidden_tokens": forbidden_tokens,
        "callable_parameters": params,
        "passes": (
            not dangerous
            and not any(forbidden_tokens.values())
            and params == ["retained_d", "residual_state", "omega"]
        ),
    }


def _independent_production_cost() -> dict:
    n = 1024
    layers = 16
    response_rank = 16
    q1 = 384
    q2 = 224
    k1 = 16
    k2 = 16
    passes = 4

    a = 32 * (k1 + k2) * n * n * layers
    b = passes * layers * k1 * 4 * n * response_rank * (n + q1)
    c = passes * layers * k2 * 4 * n * response_rank * (n + q2)
    d = passes * layers * (
        2 * n * q1 * response_rank + 2 * q1 * q2 * response_rank
    )
    e = 16 * n * response_rank * response_rank * layers
    f = passes * layers * 8 * n * response_rank * response_rank
    g = passes * layers * (k1 + k2) * (
        4 * n * n + 8 * n * response_rank
    )
    h = 20_000_000_000
    total = a + b + c + d + e + f + g + h
    return {
        "left_factor_build_upper": int(a),
        "shared_response_actions_upper": int(b),
        "nested_response_actions_upper": int(c),
        "basis_lifts_upper": int(d),
        "adaptive_qr_upper": int(e),
        "adaptive_query_products_upper": int(f),
        "certificate_norms_upper": int(g),
        "helper_reserve": int(h),
        "all_in_upper": int(total),
        "budget_flops": int(BUDGET_FLOPS),
        "module_cap_flops": int(math.floor(0.135 * BUDGET_FLOPS)),
        "utilization": total / float(BUDGET_FLOPS),
        "slack_to_module_cap": int(math.floor(0.135 * BUDGET_FLOPS)) - total,
    }


def _run_fixture(spec: dict) -> dict:
    fx = _fixture(spec)
    state = fx["state"]
    retained_d = fx["retained_d"]
    omega = fx["omega"]
    heldout = fx["heldout"]

    # Candidate path and deterministic replay happen before exact residual/full
    # matrices are materialized.
    cand = adaptive_response_sequence(retained_d, state, omega)
    replay = adaptive_response_sequence(retained_d, state, omega)
    deterministic = _array_equal_adaptive(cand, replay)

    basis = response_basis(cand.right_queries)
    held_approx, held_e, held_basis_action = heldout_projection(
        retained_d, state, basis, heldout
    )
    orient_bound, source_norm_bound = orientation_certificate(state, held_e)

    frozen_candidate = {
        "candidate_y1_sha256": _sha(cand.y1),
        "candidate_q1_sha256": _sha(cand.q1),
        "candidate_z1_sha256": _sha(cand.z1),
        "candidate_y2_sha256": _sha(cand.y2),
        "candidate_q2_sha256": _sha(cand.q2),
        "candidate_b_sha256": _sha(cand.b),
        "heldout_approx_sha256": _sha(held_approx),
        "heldout_e_sha256": _sha(held_e),
        "orientation_bound": float(orient_bound),
        "source_norm_bound": float(source_norm_bound),
    }

    # Verifier-only exact materialization starts here.
    residual_d = _materialize_d(
        fx["q_c"],
        fx["u2"],
        fx["omitted_shared"],
        fx["omitted_nested"],
    )
    full_d = retained_d + residual_d

    exact_y1 = full_d @ omega
    exact_q1 = canonical_qr(exact_y1)
    exact_z1 = full_d.T @ exact_q1
    exact_y2 = full_d @ exact_z1
    exact_q2 = canonical_qr(exact_y2)
    exact_b = full_d.T @ exact_q2

    direct_exact_residual = (
        residual_d @ cand.right_queries[0],
        residual_d.T @ cand.left_queries[0],
        residual_d @ cand.right_queries[1],
        residual_d.T @ cand.left_queries[1],
    )
    direct_total_exact = (
        full_d @ cand.right_queries[0],
        full_d.T @ cand.left_queries[0],
        full_d @ cand.right_queries[1],
        full_d.T @ cand.left_queries[1],
    )
    direct_candidate = (cand.y1, cand.z1, cand.y2, cand.b)

    direct_rel = [
        _rel(a, b) for a, b in zip(direct_candidate, direct_total_exact)
    ]

    residual_abs = []
    residual_fp_pass = []
    for action, exact_res in zip(cand.action_results, direct_exact_residual):
        err = float(np.linalg.norm(action.value - exact_res))
        scale = max(1.0, float(np.linalg.norm(exact_res)))
        residual_abs.append(err)
        residual_fp_pass.append(
            err <= action.fp_certificate + 1e-12 * scale
        )

    proj_den = max(float(np.linalg.norm(exact_q2 @ exact_q2.T)), 2.0**-500)
    projector_rel = float(
        np.linalg.norm(cand.q2 @ cand.q2.T - exact_q2 @ exact_q2.T) / proj_den
    )
    adaptive_b_rel = _rel(cand.b, exact_b)

    held_exact = full_d @ heldout
    held_error = float(np.linalg.norm(held_exact - held_approx))
    held_scale = max(1.0, float(np.linalg.norm(held_exact)))
    cert_contains = held_error <= orient_bound + 1e-12 * held_scale
    orient_beats_source_norm = (
        orient_bound <= source_norm_bound + 1e-12 * max(1.0, source_norm_bound)
    )
    sharp_norm_diagnostic = float(np.linalg.norm(residual_d) * np.linalg.norm(held_e))

    finite = bool(
        all(
            np.isfinite(x).all()
            for x in (
                cand.y1,
                cand.q1,
                cand.z1,
                cand.y2,
                cand.q2,
                cand.b,
                held_approx,
                residual_d,
                full_d,
            )
        )
        and math.isfinite(orient_bound)
        and math.isfinite(source_norm_bound)
    )

    return {
        "name": spec["name"],
        "spec": spec,
        "candidate_frozen_before_reference": frozen_candidate,
        "deterministic_replay_bitwise_exact": deterministic,
        "finite": finite,
        "direct_action_relative_errors": direct_rel,
        "max_direct_action_relative_error": max(direct_rel),
        "residual_action_absolute_errors": residual_abs,
        "residual_fp_certificates": [
            float(x.fp_certificate) for x in cand.action_results
        ],
        "residual_fp_certificate_pass_all": bool(all(residual_fp_pass)),
        "q2_projector_relative_error": projector_rel,
        "adaptive_b_relative_error": adaptive_b_rel,
        "heldout_actual_error": held_error,
        "heldout_orientation_certificate": float(orient_bound),
        "heldout_sourcewise_norm_only_certificate": float(source_norm_bound),
        "heldout_sharp_full_residual_norm_diagnostic": sharp_norm_diagnostic,
        "heldout_certificate_contains_error": cert_contains,
        "orientation_bound_le_sourcewise_norm_bound": orient_beats_source_norm,
        "response_basis_rank": int(basis.shape[1]),
        "full_residual_entries": int(spec["n"] ** 2),
        "response_statistic_entries": int(spec["n"] * basis.shape[1]),
        "full_d_sha256": _sha(full_d),
        "residual_d_sha256": _sha(residual_d),
    }


def main() -> None:
    audit = _source_audit()
    fixtures = [
        {
            "name": "dense32",
            "n": 32,
            "q1": 12,
            "q2": 7,
            "retained_shared": 3,
            "omitted_shared": 6,
            "retained_nested": 2,
            "omitted_nested": 5,
            "r": 4,
            "seed": 142032,
            "adversarial": False,
        },
        {
            "name": "adversarial16",
            "n": 16,
            "q1": 8,
            "q2": 5,
            "retained_shared": 2,
            "omitted_shared": 5,
            "retained_nested": 2,
            "omitted_nested": 4,
            "r": 4,
            "seed": 142016,
            "adversarial": True,
        },
    ]

    records = [_run_fixture(spec) for spec in fixtures]

    candidate_cost = production_cost_receipt()
    independent_cost = _independent_production_cost()
    cost_keys = (
        "left_factor_build_upper",
        "shared_response_actions_upper",
        "nested_response_actions_upper",
        "basis_lifts_upper",
        "adaptive_qr_upper",
        "adaptive_query_products_upper",
        "certificate_norms_upper",
        "helper_reserve",
        "all_in_upper",
        "budget_flops",
        "module_cap_flops",
        "slack_to_module_cap",
    )
    cost_match = all(candidate_cost[k] == independent_cost[k] for k in cost_keys)

    gates = {
        "finite_all": all(r["finite"] for r in records),
        "deterministic_replay_bitwise_exact_all": all(
            r["deterministic_replay_bitwise_exact"] for r in records
        ),
        "right_left_action_relative_error_le_1e_12_all": all(
            r["max_direct_action_relative_error"] <= 1e-12 for r in records
        ),
        "q2_projector_relative_error_le_1e_11_all": all(
            r["q2_projector_relative_error"] <= 1e-11 for r in records
        ),
        "adaptive_b_relative_error_le_1e_12_all": all(
            r["adaptive_b_relative_error"] <= 1e-12 for r in records
        ),
        "heldout_orientation_certificate_contains_error_all": all(
            r["heldout_certificate_contains_error"] for r in records
        ),
        "orientation_bound_le_sourcewise_norm_bound_all": all(
            r["orientation_bound_le_sourcewise_norm_bound"] for r in records
        ),
        "floating_response_certificate_pass_all": all(
            r["residual_fp_certificate_pass_all"] for r in records
        ),
        "target_oracle_firewall_pass": audit["passes"],
        "production_cost_formula_exact_reconcile": cost_match,
        "production_module_cost_le_0_135B": (
            candidate_cost["all_in_upper"] <= MODULE_CAP_FLOPS
        ),
        "no_public_scorer_holdout_full": True,
    }

    go = bool(all(gates.values()))
    result = {
        "schema": "arc.whitebox.e142.response_aligned_old_d21.v1",
        "experiment": "E142",
        "idempotency_key": "ARC-E142-RESPONSE-ALIGNED-OLD-D21-20260921",
        "mechanism": {
            "name": "response-aligned residual projection sufficient statistic",
            "countsketch": False,
            "smv_rank4": False,
            "svd_recompression": False,
            "norm_only_certificate": False,
            "adaptive_response_actions": 4,
            "production_response_rank": 16,
            "target_free": True,
        },
        "source_audit": audit,
        "records": records,
        "production_cost": candidate_cost,
        "independent_production_cost": independent_cost,
        "gates": gates,
        "scientific_go": go,
        "decision": (
            "E142_EXACT_SMALL_SUFFICIENT_STATISTIC_GO"
            if go
            else "E142_TERMINAL_NO_GO_CLOSE_RESPONSE_ALIGNED_OLD_D21"
        ),
        "interpretation": {
            "go_scope": (
                "Exact-small validation of the old-tier D21 response-statistic "
                "module only; not a final challenge estimator or V29 rescue."
            ),
            "production_cost_scope": (
                "Module cost from existing old-source factor arrays at the D21 "
                "contraction interface through four adaptive response passes "
                "and certificates."
            ),
        },
        "scope": {
            "synthetic_only": True,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "submission": False,
            "h140_rescue": False,
            "e137_rescue": False,
            "rank_sweep": False,
            "seed_sweep": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }
    OUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("E142_RESPONSE_ALIGNED_D21=" + json.dumps(result, sort_keys=True))

    integrity = [
        "finite_all",
        "deterministic_replay_bitwise_exact_all",
        "target_oracle_firewall_pass",
        "production_cost_formula_exact_reconcile",
        "no_public_scorer_holdout_full",
    ]
    if not all(gates[k] for k in integrity):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
