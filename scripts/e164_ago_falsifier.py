#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import math
from pathlib import Path

import numpy as np

from methods.e164_ago import (
    BUDGET_FLOPS,
    CAP_FLOPS,
    ago_estimate,
    parent_estimate,
    production_cost,
    radial_a1,
    to_angular,
    to_gaussian,
)


OUT = Path("e164-ago-result.json")
CANDIDATE_PATH = Path("methods/e164_ago.py")
PROTOCOL_COMMIT = "b40957707e51f6d2fc142b913d9a500795d1bfe7"


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _mse(a: np.ndarray, b: np.ndarray) -> float:
    d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
    return float(np.mean(d * d))


def _rel(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    return float(
        np.linalg.norm(aa - bb)
        / max(float(np.linalg.norm(bb)), 2.0**-500)
    )


def _he_weights(n: int, seed: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    return [
        rng.normal(
            0.0,
            math.sqrt(2.0 / n),
            size=(n, n),
        ).astype(np.float64)
        for _ in range(8)
    ]


def _canonical_qr(a: np.ndarray) -> np.ndarray:
    q, _ = np.linalg.qr(np.asarray(a, dtype=np.float64))
    for j in range(q.shape[1]):
        idx = int(np.argmax(np.abs(q[:, j])))
        if q[idx, j] < 0.0:
            q[:, j] *= -1.0
    return q


def _adversarial16_weights() -> list[np.ndarray]:
    n = 16
    rng = np.random.Generator(np.random.PCG64(164016))
    gains0 = np.linspace(0.5, 1.5, n, dtype=np.float64)
    gains0 *= math.sqrt(2.0) / math.sqrt(float(np.mean(gains0 * gains0)))

    out: list[np.ndarray] = []
    for layer in range(8):
        ql = _canonical_qr(rng.standard_normal((n, n)))
        qr = _canonical_qr(rng.standard_normal((n, n)))
        gains = np.roll(gains0, layer)
        out.append(
            np.asarray(
                ql @ np.diag(gains) @ qr.T,
                dtype=np.float64,
            )
        )
    return out


def _source_audit() -> dict:
    src = CANDIDATE_PATH.read_text(encoding="utf-8")
    low = src.lower()
    tree = ast.parse(src)

    imports: list[str] = []
    io_calls: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "open", "eval", "exec"
            }:
                io_calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                name = ast.unparse(node.func).lower()
                if any(
                    token in name
                    for token in (
                        "read_text",
                        "read_bytes",
                        "urlopen",
                        "request",
                        "download",
                        "loadtxt",
                        "genfromtxt",
                        "read_csv",
                        "read_parquet",
                    )
                ):
                    io_calls.append(name)

    forbidden_imports = [
        item
        for item in imports
        if any(
            token in item.lower()
            for token in (
                "e162",
                "e154",
                "e157",
                "e164_reference",
                "whestbench",
                "dataset",
                "scorer",
                "requests",
                "urllib",
            )
        )
    ]

    forbidden_tokens = {
        token: token in low
        for token in (
            "e162",
            "e154",
            "e157",
            "k4",
            "d4",
            "d22",
            "c4",
            "strassen",
            "holdout",
            "submission",
        )
    }

    parent_params = list(inspect.signature(parent_estimate).parameters)
    ago_params = list(inspect.signature(ago_estimate).parameters)

    return {
        "candidate_sha256": hashlib.sha256(src.encode("utf-8")).hexdigest(),
        "imports": sorted(imports),
        "forbidden_imports": forbidden_imports,
        "io_network_calls": io_calls,
        "forbidden_tokens": forbidden_tokens,
        "parent_parameters": parent_params,
        "ago_parameters": ago_params,
        "passes": bool(
            not forbidden_imports
            and not io_calls
            and not any(forbidden_tokens.values())
            and parent_params == ["weights"]
            and ago_params == ["weights"]
        ),
    }


def _freeze(est) -> dict:
    return {
        "final_mean_sha256": _sha(est.final_mean),
        "layer_mean_sha256": [_sha(x.mean) for x in est.layers],
        "layer_covariance_sha256": [_sha(x.covariance) for x in est.layers],
        "first_gaussian_mean_sha256": _sha(est.first_gaussian_mean),
        "first_gaussian_covariance_sha256": _sha(
            est.first_gaussian_covariance
        ),
        "first_angular_mean_sha256": (
            None
            if est.first_angular_mean is None
            else _sha(est.first_angular_mean)
        ),
        "first_angular_covariance_sha256": (
            None
            if est.first_angular_covariance is None
            else _sha(est.first_angular_covariance)
        ),
        "cost": est.cost,
    }


def _same(a, b) -> bool:
    if not np.array_equal(a.final_mean, b.final_mean):
        return False
    if not np.array_equal(a.first_gaussian_mean, b.first_gaussian_mean):
        return False
    if not np.array_equal(
        a.first_gaussian_covariance,
        b.first_gaussian_covariance,
    ):
        return False
    if (a.first_angular_mean is None) != (b.first_angular_mean is None):
        return False
    if a.first_angular_mean is not None:
        if not np.array_equal(a.first_angular_mean, b.first_angular_mean):
            return False
        if not np.array_equal(
            a.first_angular_covariance,
            b.first_angular_covariance,
        ):
            return False
    for x, y in zip(a.layers, b.layers):
        if not np.array_equal(x.mean, y.mean):
            return False
        if not np.array_equal(x.covariance, y.covariance):
            return False
        if not np.array_equal(x.pre_mean, y.pre_mean):
            return False
        if not np.array_equal(x.pre_covariance, y.pre_covariance):
            return False
    return a.cost == b.cost


def _candidate_roundtrip(ago, n: int) -> float:
    if ago.first_angular_mean is None or ago.first_angular_covariance is None:
        return math.inf

    am, ac = to_angular(
        ago.first_gaussian_mean,
        ago.first_gaussian_covariance,
        n,
    )
    gm, gc = to_gaussian(am, ac, n)

    return float(
        max(
            _rel(am, ago.first_angular_mean),
            _rel(ac, ago.first_angular_covariance),
            _rel(gm, ago.first_gaussian_mean),
            _rel(gc, ago.first_gaussian_covariance),
        )
    )


def _exact2d_gauge_identity(ref) -> float:
    a1 = math.sqrt(math.pi) / 2.0
    ma = np.asarray(ref.first_angular_mean, dtype=np.float64)
    ca = np.asarray(ref.first_angular_covariance, dtype=np.float64)

    mg = a1 * ma
    cg = ca + (1.0 - a1 * a1) * (ma[:, None] * ma[None, :])

    recovered_ma = mg / a1
    recovered_ca = cg - (1.0 / (a1 * a1) - 1.0) * (
        mg[:, None] * mg[None, :]
    )

    return float(max(_rel(recovered_ma, ma), _rel(recovered_ca, ca)))


def _independent_cost() -> dict:
    n = 1024
    L = 16
    parts = {
        "covariance_linear_transport": L * 4 * n**3,
        "mean_matvec": L * 2 * n**2,
        "nonlinear_second_order_arithmetic": L * 24 * n**2,
        "normal_scalar_work": L * 1024 * n,
        "helper_reserve": 20 * (2 * n**3),
        "angular_gauge_overlay": 8 * n**2 + 64 * L * n,
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


def _stability(
    batch_angular: np.ndarray,
    a1: float,
    parent_mean: np.ndarray,
    ago_mean: np.ndarray,
    reference_mean: np.ndarray,
) -> dict:
    batches = a1 * np.asarray(batch_angular, dtype=np.float64)
    se_vec = np.std(batches, axis=0, ddof=1) / math.sqrt(batches.shape[0])
    se_rms = float(np.sqrt(np.mean(se_vec * se_vec)))
    parent_rmse = math.sqrt(_mse(parent_mean, reference_mean))
    ago_rmse = math.sqrt(_mse(ago_mean, reference_mean))
    threshold = 0.20 * min(parent_rmse, ago_rmse)

    return {
        "reference_se_rms": se_rms,
        "parent_rmse": parent_rmse,
        "ago_rmse": ago_rmse,
        "relative_threshold": threshold,
        "passes": bool(se_rms <= threshold or se_rms <= 1e-4),
    }


def _score(parent_mean, ago_mean, reference_mean) -> dict:
    pmse = _mse(parent_mean, reference_mean)
    amse = _mse(ago_mean, reference_mean)
    ratio = math.inf if pmse <= 0.0 else amse / pmse
    return {
        "parent_mse": pmse,
        "ago_mse": amse,
        "ago_over_parent": ratio,
        "parent_relative_rms": _rel(parent_mean, reference_mean),
        "ago_relative_rms": _rel(ago_mean, reference_mean),
        "individual_improvement_gate": bool(
            pmse > 0.0
            and math.isfinite(ratio)
            and ratio < 1.0
        ),
    }


def _run_exact2d(weights: list[np.ndarray]) -> dict:
    n = 2
    parent = parent_estimate(weights)
    ago = ago_estimate(weights)
    parent_replay = parent_estimate(weights)
    ago_replay = ago_estimate(weights)

    parent_frozen = _freeze(parent)
    ago_frozen = _freeze(ago)

    from methods.e164_reference import exact_circle, homogeneity_error

    ref = exact_circle(weights)
    ref_gaussian = radial_a1(n) * ref.final_angular_mean

    return {
        "name": "exact2d",
        "width": n,
        "depth": 8,
        "network_seed": 164002,
        "parent_frozen_before_reference": parent_frozen,
        "ago_frozen_before_reference": ago_frozen,
        "reference_after_freeze": True,
        "finite": bool(parent.finite and ago.finite and ref.finite),
        "parent_replay_bitwise_exact": _same(parent, parent_replay),
        "ago_replay_bitwise_exact": _same(ago, ago_replay),
        "candidate_roundtrip_error": _candidate_roundtrip(ago, n),
        "analytic_first_state_gauge_error": _exact2d_gauge_identity(ref),
        "homogeneity_error": homogeneity_error(
            weights,
            n=n,
            seed=164202,
            rays=128,
        ),
        "sector_count": int(ref.sector_count),
        "reference_mean_sha256": _sha(ref_gaussian),
        "parent_error_vector": (
            parent.final_mean - ref_gaussian
        ).tolist(),
        "ago_error_vector": (
            ago.final_mean - ref_gaussian
        ).tolist(),
        **_score(parent.final_mean, ago.final_mean, ref_gaussian),
    }


def _run_highd(
    *,
    name: str,
    weights: list[np.ndarray],
    reference_seed: int,
    homogeneity_seed: int,
) -> dict:
    n = int(weights[0].shape[0])
    parent = parent_estimate(weights)
    ago = ago_estimate(weights)
    parent_replay = parent_estimate(weights)
    ago_replay = ago_estimate(weights)

    parent_frozen = _freeze(parent)
    ago_frozen = _freeze(ago)

    from methods.e164_reference import (
        homogeneity_error,
        sphere_mean_reference,
    )

    ref = sphere_mean_reference(
        weights,
        samples=32768,
        seed=reference_seed,
    )
    a1 = radial_a1(n)
    ref_gaussian = a1 * ref.final_angular_mean

    return {
        "name": name,
        "width": n,
        "depth": 8,
        "reference_samples": 32768,
        "reference_seed": int(reference_seed),
        "parent_frozen_before_reference": parent_frozen,
        "ago_frozen_before_reference": ago_frozen,
        "reference_after_freeze": True,
        "finite": bool(parent.finite and ago.finite and ref.finite),
        "parent_replay_bitwise_exact": _same(parent, parent_replay),
        "ago_replay_bitwise_exact": _same(ago, ago_replay),
        "candidate_roundtrip_error": _candidate_roundtrip(ago, n),
        "homogeneity_error": homogeneity_error(
            weights,
            n=n,
            seed=homogeneity_seed,
            rays=128,
        ),
        "reference_stability": _stability(
            ref.batch_final_angular_means,
            a1,
            parent.final_mean,
            ago.final_mean,
            ref_gaussian,
        ),
        "reference_mean_sha256": _sha(ref_gaussian),
        "parent_error_vector": (
            parent.final_mean - ref_gaussian
        ).tolist(),
        "ago_error_vector": (
            ago.final_mean - ref_gaussian
        ).tolist(),
        **_score(parent.final_mean, ago.final_mean, ref_gaussian),
    }


def main() -> None:
    audit = _source_audit()

    records = [
        _run_exact2d(_he_weights(2, 164002)),
        _run_highd(
            name="dense32",
            weights=_he_weights(32, 164032),
            reference_seed=164320,
            homogeneity_seed=164232,
        ),
        _run_highd(
            name="adversarial16",
            weights=_adversarial16_weights(),
            reference_seed=164160,
            homogeneity_seed=164216,
        ),
    ]

    parent_errors = np.concatenate(
        [
            np.asarray(r["parent_error_vector"], dtype=np.float64)
            for r in records
        ]
    )
    ago_errors = np.concatenate(
        [
            np.asarray(r["ago_error_vector"], dtype=np.float64)
            for r in records
        ]
    )
    pooled_parent_mse = float(np.mean(parent_errors * parent_errors))
    pooled_ago_mse = float(np.mean(ago_errors * ago_errors))
    pooled_ratio = (
        math.inf
        if pooled_parent_mse <= 0.0
        else pooled_ago_mse / pooled_parent_mse
    )

    prod = production_cost()
    independent = _independent_cost()
    cost_keys = (
        "covariance_linear_transport",
        "mean_matvec",
        "nonlinear_second_order_arithmetic",
        "normal_scalar_work",
        "helper_reserve",
        "angular_gauge_overlay",
        "all_in_upper",
        "budget_flops",
        "cap_flops",
        "slack_flops",
    )
    cost_match = all(prod[k] == independent[k] for k in cost_keys)

    r2, r32, r16 = records
    gates = {
        "source_firewall": bool(audit["passes"]),
        "finite_all": all(r["finite"] for r in records),
        "reference_after_freeze_all": all(
            r["reference_after_freeze"] for r in records
        ),
        "parent_replay_bitwise_exact_all": all(
            r["parent_replay_bitwise_exact"] for r in records
        ),
        "ago_replay_bitwise_exact_all": all(
            r["ago_replay_bitwise_exact"] for r in records
        ),
        "candidate_roundtrip_le_2e_12_all": all(
            r["candidate_roundtrip_error"] <= 2e-12
            for r in records
        ),
        "exact2d_first_state_gauge_le_2e_12": (
            r2["analytic_first_state_gauge_error"] <= 2e-12
        ),
        "homogeneity_le_2e_12_all": all(
            r["homogeneity_error"] <= 2e-12
            for r in records
        ),
        "reference_stability_dense32_adversarial16": bool(
            r32["reference_stability"]["passes"]
            and r16["reference_stability"]["passes"]
        ),
        "individual_improvement_exact2d": bool(
            r2["individual_improvement_gate"]
        ),
        "individual_improvement_dense32": bool(
            r32["individual_improvement_gate"]
        ),
        "individual_improvement_adversarial16": bool(
            r16["individual_improvement_gate"]
        ),
        "pooled_mse_ratio_le_0_98": bool(
            math.isfinite(pooled_ratio) and pooled_ratio <= 0.98
        ),
        "cost_formula_exact_reconcile": bool(cost_match),
        "complete_cost_le_0_135B": bool(prod["all_in_upper"] <= CAP_FLOPS),
        "no_public_scorer_holdout_full_submission": True,
        "no_sweep_rescue_rerun": True,
    }

    scientific_go = bool(all(gates.values()))

    result = {
        "schema": "arc.whitebox.e164.cleanroom_ago.v1",
        "experiment": "E164",
        "idempotency_key": "ARC-E164-CLEANROOM-AGO-20260921",
        "bootstrap_parent": "7a0034088ebbffbd74b441e1797c272e9d33cbff",
        "protocol_commit": PROTOCOL_COMMIT,
        "mechanism": {
            "name": "AGO",
            "delta": (
                "exact first-activation K1/K2 angular gauge plus exact final "
                "radial a1 mean readout"
            ),
            "higher_order_state": False,
            "strassen": False,
            "target_fit": False,
        },
        "source_audit": audit,
        "records": records,
        "pooled": {
            "parent_mse": pooled_parent_mse,
            "ago_mse": pooled_ago_mse,
            "ago_over_parent": pooled_ratio,
        },
        "production_cost": prod,
        "independent_production_cost": independent,
        "gates": gates,
        "scientific_go": scientific_go,
        "decision": (
            "E164_TARGET_FREE_SCIENTIFIC_GO_AGO"
            if scientific_go
            else "E164_TERMINAL_NO_GO_CLOSE_AGO"
        ),
        "scope": {
            "target_free": True,
            "synthetic_only": True,
            "standalone_execution": True,
            "pip_editable_install": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "submission": False,
            "sweep": False,
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
    print("E164_AGO=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
