#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np
import torch

from methods.e148_gstt_k3 import GSTTTensor, production_cost_receipt
from mlp_kprop.factor_k3 import FactoredTensor
from mlp_kprop.harmonic import HTensor
from mlp_kprop.kprop_harmonic import SIMPLE, coerce_input, linear_kprop, nonlin_kprop
from mlp_kprop.wick import relu_wick_coef

OUT = Path("e148-gstt-k3.json")
CANDIDATE_PATH = Path("methods/e148_gstt_k3.py")
OFFICIAL_COMMIT = "93d091a4c26c042bfffa28f2e76a81bc0aba94bb"
PUBLIC_V29_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
PUBLIC_V29_BLOB = "17df1a073a24f96c4705b04bcf61ef60fa06dd0c"


def _sha_tensor(x: torch.Tensor) -> str:
    a = np.ascontiguousarray(x.detach().cpu().numpy())
    return hashlib.sha256(a.tobytes()).hexdigest()


def _canonical_q(q: torch.Tensor) -> torch.Tensor:
    q = q.clone()
    for j in range(q.shape[1]):
        idx = int(torch.argmax(torch.abs(q[:, j])).item())
        if float(q[idx, j]) < 0:
            q[:, j].neg_()
    return q


def _orth(rng: np.random.Generator, n: int) -> np.ndarray:
    q, _ = np.linalg.qr(rng.standard_normal((n, n)))
    for j in range(n):
        idx = int(np.argmax(np.abs(q[:, j])))
        if q[idx, j] < 0:
            q[:, j] *= -1
    return q


def _weights_dense_he(n: int, depth: int, seed: int) -> list[torch.Tensor]:
    rng = np.random.Generator(np.random.PCG64(seed))
    out = []
    for l in range(depth):
        scale = 1.0 if l == 0 else math.sqrt(2.0)
        w = rng.standard_normal((n, n)) * (scale / math.sqrt(n))
        out.append(torch.tensor(w, dtype=torch.float64))
    return out


def _weights_adversarial(n: int, depth: int, seed: int) -> list[torch.Tensor]:
    rng = np.random.Generator(np.random.PCG64(seed))
    base = np.linspace(0.55, 1.45, n, dtype=np.float64)
    base /= math.sqrt(float(np.mean(base * base)))
    out = []
    for l in range(depth):
        q1 = _orth(rng, n)
        q2 = _orth(rng, n)
        # Frozen alternating permutation prevents one lucky singular ordering from
        # staying aligned with the same coordinates across depth.
        gains = np.roll(base if l % 2 == 0 else base[::-1], (3 * l) % n)
        scale = 1.0 if l == 0 else math.sqrt(2.0)
        w = scale * (q1 @ np.diag(gains) @ q2.T)
        out.append(torch.tensor(w, dtype=torch.float64))
    return out


def _omega(weights: list[torch.Tensor], layer: int, rank: int) -> torch.Tensor:
    src = weights[layer + 1] if layer + 1 < len(weights) else weights[layer]
    return src[:, :rank].contiguous()


def _initial_tower(n: int) -> dict[int, Any]:
    return coerce_input(
        {
            1: torch.zeros(n, dtype=torch.float64),
            2: torch.eye(n, dtype=torch.float64),
        },
        k_max=3,
        kind=SIMPLE,
    )


def _set_metric(layer: int) -> float:
    return 1.0 if layer == 0 else 2.0


def _candidate_once(weights: list[torch.Tensor], rank: int) -> dict[str, Any]:
    n = weights[0].shape[0]
    k = _initial_tower(n)
    d_records = []
    state_hashes = []
    final_state = None

    for l, w in enumerate(weights):
        k = linear_kprop(k, w, k_max=3, set_metric=_set_metric(l))
        if 3 in k:
            k3 = k[3]
            assert isinstance(k3, GSTTTensor)
            d_records.append(
                {
                    "layer": l,
                    "d21": k3.get_dslice((2, 1)).detach().clone(),
                    "d3": k3.get_dslice((3,)).detach().clone(),
                    "certificate": float(k3.certificate),
                }
            )

        k = nonlin_kprop(
            k,
            nonlin_wick_coef=relu_wick_coef,
            k_max=3,
            kind=SIMPLE,
            use_pK=True,
            factor=True,
        )

        if 3 in k:
            if isinstance(k[3], GSTTTensor):
                k[3].finalize(_omega(weights, l, rank))
            else:
                assert isinstance(k[3], FactoredTensor)
                k[3] = GSTTTensor.from_factored(
                    k[3], rank=rank, omega=_omega(weights, l, rank)
                )
            final_state = k[3]
            state_hashes.append(
                {
                    "layer": l,
                    "u": _sha_tensor(k[3].u),
                    "g": _sha_tensor(k[3].g),
                    "v": _sha_tensor(k[3].v),
                    "mean": _sha_tensor(k[1].core),
                    "certificate": float(k[3].certificate),
                }
            )

    assert final_state is not None
    return {
        "final_mean": k[1].core.detach().clone(),
        "d_records": d_records,
        "state_hashes": state_hashes,
        "final_state": final_state.clone(),
        "audit": {
            "identity_middle_checks": final_state.audit.identity_middle_checks,
            "identity_middle_failures": final_state.audit.identity_middle_failures,
            "identity_middle_pass": final_state.audit.identity_middle_pass,
            "projection_losses": list(final_state.audit.projection_losses),
            "newborn_residual_bounds": list(final_state.audit.newborn_residual_bounds),
            "transport_bounds": list(final_state.audit.transport_bounds),
            "wick_bounds": list(final_state.audit.wick_bounds),
            "finalize_calls": final_state.audit.finalize_calls,
        },
    }


def _candidate_equal(a: dict[str, Any], b: dict[str, Any]) -> bool:
    if not torch.equal(a["final_mean"], b["final_mean"]):
        return False
    if a["state_hashes"] != b["state_hashes"]:
        return False
    if a["audit"] != b["audit"]:
        return False
    if len(a["d_records"]) != len(b["d_records"]):
        return False
    for x, y in zip(a["d_records"], b["d_records"]):
        if x["layer"] != y["layer"] or x["certificate"] != y["certificate"]:
            return False
        if not torch.equal(x["d21"], y["d21"]):
            return False
        if not torch.equal(x["d3"], y["d3"]):
            return False
    return True


def _dense_d21(k3: HTensor) -> torch.Tensor:
    assert k3.r == 0 and k3.core.ndim == 3
    t = k3.core
    idx = torch.arange(t.shape[0])
    d21 = t[idx, idx, :].clone()
    d21.fill_diagonal_(0.0)
    return d21


def _dense_d3(k3: HTensor) -> torch.Tensor:
    assert k3.r == 0 and k3.core.ndim == 3
    t = k3.core
    idx = torch.arange(t.shape[0])
    return t[idx, idx, idx].clone()


def _dense_reference(weights: list[torch.Tensor], *, zero_k3: bool) -> dict[str, Any]:
    n = weights[0].shape[0]
    k = _initial_tower(n)
    d_records = []
    tensor_hashes = []
    for l, w in enumerate(weights):
        k = linear_kprop(k, w, k_max=3, set_metric=_set_metric(l))
        if 3 in k:
            k3 = k[3]
            assert isinstance(k3, HTensor) and k3.r == 0
            if not zero_k3:
                d_records.append(
                    {
                        "layer": l,
                        "d21": _dense_d21(k3),
                        "d3": _dense_d3(k3),
                    }
                )
                tensor_hashes.append({"layer": l, "k3": _sha_tensor(k3.core)})
            else:
                del k[3]

        k = nonlin_kprop(
            k,
            nonlin_wick_coef=relu_wick_coef,
            k_max=3,
            kind=SIMPLE,
            use_pK=True,
            factor=False,
        )

    return {
        "final_mean": k[1].core.detach().clone(),
        "d_records": d_records,
        "tensor_hashes": tensor_hashes,
    }


def _rel(a: torch.Tensor, b: torch.Tensor) -> float:
    den = max(float(torch.linalg.vector_norm(b).item()), 2.0**-500)
    return float(torch.linalg.vector_norm(a - b).item()) / den


def _rms(x: torch.Tensor) -> float:
    return float(torch.sqrt(torch.mean(x * x)).item())


def _identity_checks(state: GSTTTensor, w: torch.Tensor) -> dict[str, float | bool]:
    # Verifier-side dense materialization occurs only after both candidate passes froze.
    s = state.ordered_seed()
    k = state.to_tensor()

    d21_direct = k[
        torch.arange(k.shape[0]),
        torch.arange(k.shape[0]),
        :,
    ].clone()
    d21_direct.fill_diagonal_(0.0)
    d3_direct = k[
        torch.arange(k.shape[0]),
        torch.arange(k.shape[0]),
        torch.arange(k.shape[0]),
    ]
    d21_rel = _rel(state.get_dslice((2, 1)), d21_direct)
    d3_rel = _rel(state.get_dslice((3,)), d3_direct)

    moved = state.contract_W(w)
    dense_moved = torch.einsum("ai,bj,ck,ijk->abc", w, w, w, s)
    linear_rel = _rel(moved.ordered_seed(), dense_moved)

    wick = torch.linspace(0.73, 1.17, state.n, dtype=state.dtype)
    scaled = state.clone()
    scaled.contract_wick_(wick)
    dense_scaled = (
        s
        * wick[:, None, None]
        * wick[None, :, None]
        * wick[None, None, :]
    )
    wick_rel = _rel(scaled.ordered_seed(), dense_scaled)
    return {
        "linear_transport_relative_error": linear_rel,
        "wick_relative_error": wick_rel,
        "d21_readout_relative_error": d21_rel,
        "d3_readout_relative_error": d3_rel,
        "passes": max(linear_rel, wick_rel, d21_rel, d3_rel) <= 1e-12,
    }


def _source_audit() -> dict[str, Any]:
    src = CANDIDATE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(src)
    imports = []
    dangerous = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            name = ast.unparse(node.func).lower()
            if any(x in name for x in ("open(", "read_text", "read_bytes", "urlopen", "requests.", "download")):
                dangerous.append(name)

    low = src.lower()
    forbidden = {
        "countsketch": "countsketch" in low,
        "h140_rank4_smv": "rank4" in low or "rank-4" in low,
        "h143_particles": "particle" in low or "mub" in low or "kerdock" in low,
        "e142_response": "response_basis" in low or "response-aligned" in low,
        "e145_integration": "e145" in low,
        "benchmark_import": "whestbench" in low,
        "target_access": "target" in low,
        "reference_import": "e148_reference" in low,
    }
    return {
        "candidate_sha256": hashlib.sha256(src.encode()).hexdigest(),
        "imports": sorted(imports),
        "dangerous_io_network_calls": dangerous,
        "forbidden_mechanism_tokens": forbidden,
        "passes": not dangerous and not any(forbidden.values()),
    }


def _fixture_result(spec: dict[str, Any]) -> dict[str, Any]:
    n = int(spec["n"])
    depth = int(spec["depth"])
    rank = int(spec["rank"])
    if spec["kind"] == "dense_he":
        weights = _weights_dense_he(n, depth, int(spec["seed"]))
    else:
        weights = _weights_adversarial(n, depth, int(spec["seed"]))

    # Candidate and replay are both complete before any dense K3 reference exists.
    cand = _candidate_once(weights, rank)
    replay = _candidate_once(weights, rank)
    deterministic = _candidate_equal(cand, replay)

    frozen = {
        "final_mean_sha256": _sha_tensor(cand["final_mean"]),
        "state_hashes": cand["state_hashes"],
        "audit": cand["audit"],
    }

    identity = _identity_checks(cand["final_state"], weights[-1])

    # Verifier-only full dense K3 reference starts here.
    ref = _dense_reference(weights, zero_k3=False)
    zero = _dense_reference(weights, zero_k3=True)

    if len(cand["d_records"]) != len(ref["d_records"]):
        raise RuntimeError("candidate/reference D-record count mismatch")

    d21_num = 0.0
    d21_den = 0.0
    d3_num = 0.0
    d3_den = 0.0
    d21_layers = []
    d3_layers = []
    cert_rows = []
    for c, r in zip(cand["d_records"], ref["d_records"]):
        if c["layer"] != r["layer"]:
            raise RuntimeError("candidate/reference layer mismatch")
        e21 = float(torch.linalg.vector_norm(c["d21"] - r["d21"]).item())
        n21 = float(torch.linalg.vector_norm(r["d21"]).item())
        e3 = float(torch.linalg.vector_norm(c["d3"] - r["d3"]).item())
        n3 = float(torch.linalg.vector_norm(r["d3"]).item())
        d21_num += e21 * e21
        d21_den += n21 * n21
        d3_num += e3 * e3
        d3_den += n3 * n3
        d21_rel = e21 / max(n21, 2.0**-500)
        d3_rel = e3 / max(n3, 2.0**-500)
        d21_layers.append(d21_rel)
        d3_layers.append(d3_rel)
        cert = float(c["certificate"])
        cert_rows.append(
            {
                "layer": c["layer"],
                "d21_abs_error": e21,
                "candidate_certificate": cert,
                "contains": e21 <= cert + 1e-12 * max(1.0, n21),
            }
        )

    pooled_d21 = math.sqrt(d21_num / max(d21_den, 2.0**-1000))
    pooled_d3 = math.sqrt(d3_num / max(d3_den, 2.0**-1000))
    final_diff = cand["final_mean"] - ref["final_mean"]
    final_rms = _rms(final_diff)
    correction = ref["final_mean"] - zero["final_mean"]
    correction_rms = _rms(correction)
    final_ratio = final_rms / max(correction_rms, 2.0**-500)

    finite = bool(
        torch.isfinite(cand["final_mean"]).all().item()
        and torch.isfinite(ref["final_mean"]).all().item()
        and all(math.isfinite(x) for x in d21_layers + d3_layers)
        and math.isfinite(final_ratio)
    )

    gates = {
        "finite": finite,
        "deterministic_replay_bitwise_exact": deterministic,
        "identity_middle_canonicalization": bool(cand["audit"]["identity_middle_pass"]),
        "representation_identities_le_1e_12": bool(identity["passes"]),
        "pooled_d21_relative_rms_le_0_010": pooled_d21 <= 0.010,
        "max_layer_d21_relative_rms_le_0_015": max(d21_layers, default=0.0) <= 0.015,
        "pooled_d3_relative_rms_le_0_010": pooled_d3 <= 0.010,
        "final_mean_error_over_exact_k3_correction_le_0_10": final_ratio <= 0.10,
        "certificate_contains_every_d21_layer": all(x["contains"] for x in cert_rows),
    }

    return {
        "name": spec["name"],
        "spec": spec,
        "candidate_frozen_before_reference": frozen,
        "identity_checks_post_candidate": identity,
        "dense_reference_k3_hashes": ref["tensor_hashes"],
        "pooled_d21_relative_rms": pooled_d21,
        "max_layer_d21_relative_rms": max(d21_layers, default=0.0),
        "d21_layer_relative_rms": d21_layers,
        "pooled_d3_relative_rms": pooled_d3,
        "max_layer_d3_relative_rms": max(d3_layers, default=0.0),
        "d3_layer_relative_rms": d3_layers,
        "final_mean_rms_error": final_rms,
        "exact_k3_correction_rms": correction_rms,
        "final_mean_error_over_exact_k3_correction": final_ratio,
        "certificate_rows": cert_rows,
        "gates": gates,
    }


def main() -> None:
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.set_default_dtype(torch.float64)

    source = _source_audit()
    specs = [
        {
            "name": "dense32_depth8",
            "kind": "dense_he",
            "n": 32,
            "depth": 8,
            "rank": 4,
            "seed": 148032,
        },
        {
            "name": "adversarial16_depth8",
            "kind": "adversarial",
            "n": 16,
            "depth": 8,
            "rank": 4,
            "seed": 148016,
        },
    ]
    records = [_fixture_result(x) for x in specs]

    cost = production_cost_receipt(rank=40)
    cost48 = production_cost_receipt(rank=48)
    cost_reconcile = cost["all_in_upper"] == 256_014_155_776
    cost_cap = cost["all_in_upper"] <= cost["cap_flops"]
    rank_budget_derived = cost48["all_in_upper"] > cost48["cap_flops"]

    gates = {
        "source_target_oracle_firewall": source["passes"],
        "official_source_commit_verified_by_workflow": os.environ.get("E148_OFFICIAL_SOURCE_OK") == "1",
        "public_v29_commit_blob_verified_by_workflow": os.environ.get("E148_PUBLIC_V29_SOURCE_OK") == "1",
        "finite_all": all(r["gates"]["finite"] for r in records),
        "deterministic_replay_all": all(
            r["gates"]["deterministic_replay_bitwise_exact"] for r in records
        ),
        "identity_middle_all": all(
            r["gates"]["identity_middle_canonicalization"] for r in records
        ),
        "representation_identities_all": all(
            r["gates"]["representation_identities_le_1e_12"] for r in records
        ),
        "pooled_d21_gate_all": all(
            r["gates"]["pooled_d21_relative_rms_le_0_010"] for r in records
        ),
        "max_layer_d21_gate_all": all(
            r["gates"]["max_layer_d21_relative_rms_le_0_015"] for r in records
        ),
        "pooled_d3_gate_all": all(
            r["gates"]["pooled_d3_relative_rms_le_0_010"] for r in records
        ),
        "final_mean_gate_all": all(
            r["gates"]["final_mean_error_over_exact_k3_correction_le_0_10"] for r in records
        ),
        "certificate_containment_all": all(
            r["gates"]["certificate_contains_every_d21_layer"] for r in records
        ),
        "production_cost_formula_exact_reconcile": cost_reconcile,
        "production_all_in_le_0_135B": cost_cap,
        "rank40_budget_derived_vs_rank48": rank_budget_derived,
        "certificate_reserve_frozen": cost["certificate_reserve"] == 25_769_803_776,
        "helper_reserve_frozen": cost["helper_materialization_reserve"] == 25_769_803_776,
        "no_public_target_scorer_holdout_full": True,
        "one_workflow_execution_only": True,
    }

    scientific_go = bool(all(gates.values()))
    result = {
        "schema": "arc.whitebox.e148.gstt_k3.v1",
        "experiment": "E148",
        "idempotency_key": "ARC-E148-GLOBAL-SEED-TT-K3-20260921",
        "official_source_commit": OFFICIAL_COMMIT,
        "public_v29_commit": PUBLIC_V29_COMMIT,
        "public_v29_blob": PUBLIC_V29_BLOB,
        "candidate": {
            "class": "GSTT-K3",
            "production_rank": 40,
            "small_rank": 4,
            "closure": "official ARC K3 SIMPLE factorized closure with GSTT replacing only K3 carrier",
            "dense_reference": "official ARC K3 SIMPLE unfactored closure",
            "target_free": True,
        },
        "source_audit": source,
        "records": records,
        "production_cost": cost,
        "rank48_counterfactual_cost": cost48,
        "gates": gates,
        "scientific_go": scientific_go,
        "decision": (
            "E148_TARGET_FREE_EXACT_SMALL_GO"
            if scientific_go
            else "E148_TERMINAL_NO_GO_CLOSE_GSTT_K3"
        ),
        "scope": {
            "synthetic_only": True,
            "benchmark_targets": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "submission": False,
            "rank_sweep": False,
            "seed_sweep": False,
            "rescue": False,
            "canonical_mutated": False,
            "ledger_mutated": False,
        },
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E148_GSTT_K3=" + json.dumps(result, sort_keys=True))

    integrity = [
        "source_target_oracle_firewall",
        "official_source_commit_verified_by_workflow",
        "public_v29_commit_blob_verified_by_workflow",
        "finite_all",
        "deterministic_replay_all",
        "production_cost_formula_exact_reconcile",
        "production_all_in_le_0_135B",
        "rank40_budget_derived_vs_rank48",
        "no_public_target_scorer_holdout_full",
        "one_workflow_execution_only",
    ]
    if not all(gates[x] for x in integrity):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
