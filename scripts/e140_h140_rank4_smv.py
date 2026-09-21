#!/usr/bin/env python3
"""E140/H140 one-shot target-free rank-4 SMV falsifier.

This script uses only synthetic fixtures and the pinned ARC cumulant-propagation
implementation supplied on PYTHONPATH by the workflow. It never imports
whestbench, opens a dataset, or reads benchmark targets/reference means.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
from pathlib import Path
from typing import Any

import torch

from mlp_kprop.kprop_harmonic import Kind, coerce_input, linear_kprop, nonlin_kprop
from mlp_kprop.wick import relu_wick_coef

torch.set_default_dtype(torch.float64)
torch.set_grad_enabled(False)
torch.set_num_threads(1)
torch.set_num_interop_threads(1)
torch.use_deterministic_algorithms(True)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "e140_artifacts"
OUT.mkdir(exist_ok=True)

RANK = 4
DEPTH = 8
BUDGET = 2**41
CAP = 0.135
ARC_COMMIT = os.environ.get("E140_ARC_COMMIT", "UNKNOWN")

# Frozen production ledger from the preregistered E140 note.
# Crucially, 124.2 units excludes SMV birth/recompression. No production
# n^3-free rank-4 recompression algorithm was preregistered or implemented.
# Protocol gate 7 requires a *complete* upper bound, and gate 8 forbids using
# this small-fixture dense SVD in production. Therefore the production cost
# gate is false/unevaluable unless such a path exists before this run. It does not.
COST = {
    "unit_flops": 2 * 1024**3,
    "budget_flops": BUDGET,
    "budget_units": 1024.0,
    "cap_utilization": CAP,
    "cap_units": 0.135 * 1024.0,
    "four_mode_transport_units": 96.0,
    "covariance_allowance_units": 22.5,
    "closure_birth_allowance_units": 5.7,
    "pre_recompression_subtotal_units": 124.2,
    "pre_recompression_subtotal_utilization": 124.2 / 1024.0,
    "remaining_units_for_birth_recompression": 0.135 * 1024.0 - 124.2,
    "production_birth_recompression_algorithm_defined": False,
    "production_birth_recompression_upper_units": None,
    "complete_all_in_units": None,
    "complete_all_in_utilization": None,
    "production_n3_materialization": False,
    "production_dense_n3m_svd": False,
    "gate_complete_all_in_cost_le_cap": False,
    "gate_reason": (
        "No production n^3-free rank-4 birth/recompression algorithm with a finite "
        "upper bound was defined before the one-shot run. The dense mode-3 SVD used "
        "only on exact-small fixtures is forbidden by protocol gate 8. Hence complete "
        "all-in cost is unevaluable and gate 7 fails."
    ),
}


def _fix_qr_sign(q: torch.Tensor, r: torch.Tensor) -> torch.Tensor:
    d = torch.diagonal(r)
    s = torch.where(d < 0, -torch.ones_like(d), torch.ones_like(d))
    return q * s.unsqueeze(0)


def make_weights(kind: str, n: int, depth: int, seed: int) -> list[torch.Tensor]:
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    ws: list[torch.Tensor] = []
    if kind == "he":
        for _ in range(depth):
            ws.append(torch.randn((n, n), generator=g) * math.sqrt(2.0 / n))
        return ws
    if kind != "adversarial":
        raise ValueError(kind)

    base_gain = torch.linspace(0.65, 1.35, n)
    base_gain = base_gain / torch.sqrt(torch.mean(base_gain.square()))
    for layer in range(depth):
        a = torch.randn((n, n), generator=g)
        b = torch.randn((n, n), generator=g)
        q1, r1 = torch.linalg.qr(a)
        q2, r2 = torch.linalg.qr(b)
        q1 = _fix_qr_sign(q1, r1)
        q2 = _fix_qr_sign(q2, r2)
        gains = base_gain if layer % 2 == 0 else torch.flip(base_gain, dims=(0,))
        # RMS singular value sqrt(2), matching He scale while imposing anisotropy.
        w = math.sqrt(2.0) * (q1 @ torch.diag(gains) @ q2.T)
        ws.append(w)
    return ws


def smv_tensor(r: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
    # r: [m,n,n], v: [m,n]
    t0 = torch.einsum("aij,ak->ijk", r, v)
    t1 = torch.einsum("aik,aj->ijk", r, v)
    t2 = torch.einsum("ajk,ai->ijk", r, v)
    return (t0 + t1 + t2) / 3.0


def compress_smv(k3: torch.Tensor, rank: int = RANK) -> tuple[torch.Tensor, torch.Tensor]:
    n = k3.shape[0]
    m = k3.reshape(n * n, n)
    u, s, vh = torch.linalg.svd(m, full_matrices=False)
    r = (u[:, :rank] * s[:rank]).T.reshape(rank, n, n)
    # The exact unfolding column space consists of symmetric matrices. Enforce
    # symmetry only at roundoff level before the frozen full-tensor symmetrization.
    r = 0.5 * (r + r.transpose(1, 2))
    v = vh[:rank, :]
    return r, v


def transport_smv(
    r: torch.Tensor, v: torch.Tensor, w: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    rt = torch.einsum("ij,ajk,lk->ail", w, r, w)
    vt = torch.einsum("ij,aj->ai", w, v)
    return rt, vt


def dense_transport(k3: torch.Tensor, w: torch.Tensor) -> torch.Tensor:
    x = torch.einsum("ia,abc->ibc", w, k3)
    x = torch.einsum("jb,ibc->ijc", w, x)
    return torch.einsum("kc,ijc->ijk", w, x)


def wick_scale_smv(
    r: torch.Tensor, v: torch.Tensor, d: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    return (
        r * d[None, :, None] * d[None, None, :],
        v * d[None, :],
    )


def d21_d3_from_tensor(k3: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    n = k3.shape[0]
    idx = torch.arange(n)
    d21 = k3[idx, idx, :]
    d3 = k3[idx, idx, idx]
    return d21, d3


def d21_d3_from_smv(r: torch.Tensor, v: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    # D21[i,c] = sum_a (R_a[ii] v_a[c] + 2 R_a[ic] v_a[i]) / 3
    diag = torch.diagonal(r, dim1=1, dim2=2)  # [a,i]
    term1 = torch.einsum("ai,ac->ic", diag, v)
    term2 = torch.einsum("aic,ai->ic", r, v)
    d21 = (term1 + 2.0 * term2) / 3.0
    d3 = torch.einsum("ai,ai->i", diag, v)
    return d21, d3


def rel_sq(err: torch.Tensor, ref: torch.Tensor) -> tuple[float, float]:
    return float(torch.sum(err.square())), float(torch.sum(ref.square()))


def tensor_sha256(h: hashlib._Hash, x: torch.Tensor) -> None:
    y = x.detach().contiguous().cpu().numpy()
    h.update(str(tuple(y.shape)).encode())
    h.update(y.tobytes())


def run_fixture(name: str, n: int, seed: int, kind: str) -> dict[str, Any]:
    weights = make_weights(kind, n, DEPTH, seed)
    k = coerce_input(
        {1: torch.zeros(n), 2: torch.eye(n)},
        k_max=3,
        kind=Kind.SIMPLE,
    )

    prev_r: torch.Tensor | None = None
    prev_v: torch.Tensor | None = None
    layer_rows: list[dict[str, Any]] = []
    d21_err2 = 0.0
    d21_ref2 = 0.0
    d3_err2 = 0.0
    d3_ref2 = 0.0
    max_linear_identity = 0.0
    max_wick_identity = 0.0
    finite = True
    digest = hashlib.sha256()

    for layer, w in enumerate(weights):
        pre = linear_kprop(k, w, k_max=3, set_metric=None)

        if layer > 0:
            assert prev_r is not None and prev_v is not None
            rt, vt = transport_smv(prev_r, prev_v, w)
            k_candidate = smv_tensor(rt, vt)
            k_prev = smv_tensor(prev_r, prev_v)
            dense = dense_transport(k_prev, w)
            linear_abs = float(torch.max(torch.abs(k_candidate - dense)))
            max_linear_identity = max(max_linear_identity, linear_abs)

            k_exact = pre[3].to_tensor()
            d21_exact, d3_exact = d21_d3_from_tensor(k_exact)
            d21_hat, d3_hat = d21_d3_from_smv(rt, vt)

            e21, r21 = rel_sq(d21_hat - d21_exact, d21_exact)
            e3, r3 = rel_sq(d3_hat - d3_exact, d3_exact)
            d21_err2 += e21
            d21_ref2 += r21
            d3_err2 += e3
            d3_ref2 += r3
            layer_d21 = math.sqrt(e21 / r21) if r21 > 0 else math.inf
            layer_d3 = math.sqrt(e3 / r3) if r3 > 0 else math.inf

            mean = pre[1].core
            var = pre[2].core.diag()
            w1 = relu_wick_coef(mean=mean, var=var, k=1, p=1)
            rw, vw = wick_scale_smv(rt, vt, w1)
            wick_candidate = smv_tensor(rw, vw)
            wick_dense = (
                k_candidate
                * w1[:, None, None]
                * w1[None, :, None]
                * w1[None, None, :]
            )
            wick_abs = float(torch.max(torch.abs(wick_candidate - wick_dense)))
            max_wick_identity = max(max_wick_identity, wick_abs)

            finite = finite and all(
                torch.isfinite(x).all().item()
                for x in (k_exact, d21_exact, d3_exact, d21_hat, d3_hat, w1)
            )
            tensor_sha256(digest, d21_exact)
            tensor_sha256(digest, d21_hat)
            tensor_sha256(digest, d3_exact)
            tensor_sha256(digest, d3_hat)

            layer_rows.append(
                {
                    "pre_layer": layer,
                    "d21_relative_error": layer_d21,
                    "d3_relative_error": layer_d3,
                    "linear_transport_identity_max_abs": linear_abs,
                    "wick_scaling_identity_max_abs": wick_abs,
                    "d21_ref_norm": math.sqrt(r21),
                    "d3_ref_norm": math.sqrt(r3),
                }
            )

        # Exact ARC K=3 SIMPLE nonlinear birth.
        k = nonlin_kprop(
            pre,
            nonlin_wick_coef=relu_wick_coef,
            k_max=3,
            kind=Kind.SIMPLE,
            use_pK=True,
            factor=True,
        )
        k3_act = k[3].to_tensor()
        prev_r, prev_v = compress_smv(k3_act, rank=RANK)
        reconstructed = smv_tensor(prev_r, prev_v)
        tensor_sha256(digest, prev_r)
        tensor_sha256(digest, prev_v)
        tensor_sha256(digest, reconstructed)
        finite = finite and all(
            torch.isfinite(x).all().item()
            for x in (k3_act, prev_r, prev_v, reconstructed)
        )

    pooled_d21 = math.sqrt(d21_err2 / d21_ref2) if d21_ref2 > 0 else math.inf
    pooled_d3 = math.sqrt(d3_err2 / d3_ref2) if d3_ref2 > 0 else math.inf
    max_layer_d21 = max((x["d21_relative_error"] for x in layer_rows), default=math.inf)
    max_layer_d3 = max((x["d3_relative_error"] for x in layer_rows), default=math.inf)

    return {
        "name": name,
        "width": n,
        "depth": DEPTH,
        "seed": seed,
        "weight_kind": kind,
        "rank": RANK,
        "transitions_evaluated": len(layer_rows),
        "pooled_d21_relative_error": pooled_d21,
        "pooled_d3_relative_error": pooled_d3,
        "max_layer_d21_relative_error": max_layer_d21,
        "max_layer_d3_relative_error": max_layer_d3,
        "linear_transport_identity_max_abs": max_linear_identity,
        "wick_scaling_identity_max_abs": max_wick_identity,
        "finite": bool(finite),
        "state_sha256": digest.hexdigest(),
        "layers": layer_rows,
    }


def same_fixture(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return a == b


def main() -> None:
    fixtures = [
        ("he32", 32, 140032, "he"),
        ("adv16", 16, 140016, "adversarial"),
    ]

    first = [run_fixture(*f) for f in fixtures]
    second = [run_fixture(*f) for f in fixtures]
    deterministic = all(same_fixture(a, b) for a, b in zip(first, second))

    gate_rows = {}
    for f in first:
        gate_rows[f["name"]] = {
            "pooled_d21_le_0p022": f["pooled_d21_relative_error"] <= 0.022,
            "max_layer_d21_le_0p03": f["max_layer_d21_relative_error"] <= 0.03,
            "pooled_d3_le_0p022": f["pooled_d3_relative_error"] <= 0.022,
            "linear_identity_le_1e_12": f["linear_transport_identity_max_abs"] <= 1e-12,
            "wick_identity_le_1e_12": f["wick_scaling_identity_max_abs"] <= 1e-12,
            "finite": f["finite"],
        }

    all_scientific_small = all(all(g.values()) for g in gate_rows.values())
    cost_gate = bool(COST["gate_complete_all_in_cost_le_cap"])
    all_go = all_scientific_small and deterministic and cost_gate

    receipt = {
        "schema": "arc.whitebox.e140.h140_rank4_smv_result.v1",
        "experiment": "E140",
        "hypothesis": "H140",
        "rank": RANK,
        "arc_reference_commit": ARC_COMMIT,
        "reference_kind": "ARC K=3 SIMPLE factorized synthetic state",
        "target_firewall": {
            "benchmark_dataset_access": False,
            "benchmark_target_access": False,
            "benchmark_reference_mean_access": False,
            "whestbench_imported": False,
            "synthetic_only": True,
        },
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "platform": platform.platform(),
            "torch_num_threads": torch.get_num_threads(),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
        "fixtures": first,
        "replay_fixtures": second,
        "deterministic_replay_exact": deterministic,
        "gates_by_fixture": gate_rows,
        "production_cost": COST,
        "small_scientific_gates_pass": all_scientific_small,
        "cost_gate_pass": cost_gate,
        "all_gates_pass": all_go,
        "decision": (
            "GO_IMMUTABLE_RESULT_HANDOFF_VERIFIER"
            if all_go
            else "TERMINAL_NO_GO_H140_RANK4_SMV"
        ),
        "failure_policy_applied": not all_go,
        "restrictions": {
            "rank_sweep": False,
            "rescue": False,
            "seed_replacement": False,
            "public_run": False,
            "scorer": False,
            "holdout": False,
            "full_suite": False,
            "canonical_mutation": False,
            "ledger_mutation": False,
        },
    }

    out = OUT / "E140_H140_RESULT.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
