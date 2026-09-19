from __future__ import annotations

import ast
import json
import math
import textwrap
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

BUDGET = 2**41
UTIL_NUM = 13
UTIL_DEN = 100
HARD_FLOP_LIMIT = (UTIL_NUM * BUDGET) // UTIL_DEN

WIDTH = 1024
DEPTH = 16
TRAJECTORIES = 4096
LATE_LAYERS = 4
BLOCK_WIDTH = WIDTH

E104_MEASURED_FLOPS = 149_114_620_592
E104_MEASURED_UTILIZATION = E104_MEASURED_FLOPS / BUDGET
E104_RNG_DELTA = 67_174_400

METHOD_PATH = Path("methods/e104_orthogonal_antithetic.py")
E104_RECEIPT_PATH = Path("research/E104_PRODUCTION_RECEIPT.md")
OUT = Path("e111-late4-cost.json")


def _function_source(source: str, name: str) -> str:
    tree = ast.parse(source)
    lines = source.splitlines()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return "\n".join(lines[node.lineno - 1 : node.end_lineno])
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == name:
                    return "\n".join(lines[child.lineno - 1 : child.end_lineno])
    raise RuntimeError(f"function not found: {name}")


def _attribute_roots(source: str) -> set[str]:
    roots: set[str] = set()
    tree = ast.parse(textwrap.dedent(source))
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            cur = node
            while isinstance(cur, ast.Attribute):
                cur = cur.value
            if isinstance(cur, ast.Name):
                roots.add(cur.id)
    return roots


def inherited_e104_billing_firewall() -> dict:
    method = METHOD_PATH.read_text(encoding="utf-8")
    receipt = E104_RECEIPT_PATH.read_text(encoding="utf-8")
    billed = _function_source(method, "orthogonal_antithetic_billed")
    predict = _function_source(method, "predict")
    billed_roots = _attribute_roots(billed)
    predict_roots = _attribute_roots(predict)

    billed_tokens = [
        "fnp.random.default_rng",
        "rng.standard_normal",
        "fnp.linalg.qr",
        "fnp.diag",
        "fnp.where",
        "rng.chisquare",
        "fnp.sqrt",
        "fnp.multiply",
        "astype(fnp.float32)",
        "fnp.concatenate",
    ]
    predict_tokens = [
        "orthogonal_antithetic_billed",
        "fnp.matmul",
        "fnp.maximum",
        "fnp.mean",
        "fnp.stack",
    ]

    return {
        "e104_receipt_records_measured_total": str(E104_MEASURED_FLOPS) in receipt,
        "e104_receipt_records_rng_delta": str(E104_RNG_DELTA) in receipt,
        "sampler_required_flopscope_ops_present": all(t in billed for t in billed_tokens),
        "predict_required_flopscope_ops_present": all(t in predict for t in predict_tokens),
        "plain_numpy_absent_from_billed_sampler": "np" not in billed_roots,
        "plain_numpy_absent_from_predict": "np" not in predict_roots,
    }


def gaussian_relu_plugin(z):
    mu = fnp.mean(z, axis=0, dtype=fnp.float64)
    zz = fnp.multiply(z, z)
    second = fnp.mean(zz, axis=0, dtype=fnp.float64)
    var = fnp.subtract(second, fnp.multiply(mu, mu))
    var = fnp.maximum(var, fnp.float64(1e-12))
    sigma = fnp.sqrt(var)
    alpha = fnp.divide(mu, sigma)
    phi = flops.stats.norm.pdf(alpha)
    Phi = flops.stats.norm.cdf(alpha)
    return fnp.add(fnp.multiply(sigma, phi), fnp.multiply(mu, Phi))


def gaussian_relu_plugin_two_slices(a, b):
    denom = float(a.shape[0] + b.shape[0])
    sum1 = fnp.add(
        fnp.sum(a, axis=0, dtype=fnp.float64),
        fnp.sum(b, axis=0, dtype=fnp.float64),
    )
    mu = fnp.divide(sum1, denom)

    aa = fnp.multiply(a, a)
    bb = fnp.multiply(b, b)
    sum2 = fnp.add(
        fnp.sum(aa, axis=0, dtype=fnp.float64),
        fnp.sum(bb, axis=0, dtype=fnp.float64),
    )
    second = fnp.divide(sum2, denom)
    var = fnp.subtract(second, fnp.multiply(mu, mu))
    var = fnp.maximum(var, fnp.float64(1e-12))
    sigma = fnp.sqrt(var)
    alpha = fnp.divide(mu, sigma)
    phi = flops.stats.norm.pdf(alpha)
    Phi = flops.stats.norm.cdf(alpha)
    return fnp.add(fnp.multiply(sigma, phi), fnp.multiply(mu, Phi))


def late4_increment(layer_arrays: list[np.ndarray]):
    if len(layer_arrays) != LATE_LAYERS:
        raise ValueError("expected exactly four later-layer arrays")

    plugins = []
    for arr in layer_arrays:
        if arr.shape != (TRAJECTORIES, WIDTH):
            raise ValueError(f"unexpected layer shape {arr.shape}")
        z = fnp.asarray(arr, dtype=fnp.float32)
        plugins.append(gaussian_relu_plugin(z))

    final_z = fnp.asarray(layer_arrays[-1], dtype=fnp.float32)
    n = BLOCK_WIDTH

    # Frozen E104 layout:
    # pos block0 [0:n], pos block1 [n:2n],
    # neg block0 [2n:3n], neg block1 [3n:4n].
    p0 = gaussian_relu_plugin_two_slices(final_z[0:n], final_z[2 * n : 3 * n])
    p1 = gaussian_relu_plugin_two_slices(final_z[n : 2 * n], final_z[3 * n : 4 * n])

    delta = fnp.subtract(p0, p1)
    variance_hat = fnp.mean(fnp.multiply(delta, delta), dtype=fnp.float64) * 0.25
    return fnp.stack(plugins, axis=0), variance_hat


def make_fixture() -> list[np.ndarray]:
    # Cost-only deterministic fixture. Construction is outside BudgetContext because
    # production E111 consumes pre-ReLU activations already created by the billed
    # E104 dense forward path. No RNG is used here or in the E111 increment.
    rows = np.arange(TRAJECTORIES, dtype=np.float32)[:, None]
    cols = np.arange(WIDTH, dtype=np.float32)[None, :]
    out: list[np.ndarray] = []
    for layer in range(LATE_LAYERS):
        base = (
            ((rows % np.float32(31.0)) - np.float32(15.0)) * np.float32(0.021)
            + ((cols % np.float32(19.0)) - np.float32(9.0)) * np.float32(0.013)
            + np.float32((layer - 1.5) * 0.017)
        )
        out.append(np.asarray(base, dtype=np.float32))
    return out


def execute_once(fixtures: list[np.ndarray]) -> tuple[dict, np.ndarray, float]:
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        plugins, variance_hat = late4_increment(fixtures)

    p = np.asarray(plugins, dtype=np.float64)
    v = float(np.asarray(variance_hat))
    return (
        {
            "incremental_flops": int(ctx.flops_used),
            "plugin_shape": list(p.shape),
            "plugin_max_abs": float(np.max(np.abs(p))),
            "variance_hat": v,
            "finite": bool(np.isfinite(p).all() and math.isfinite(v)),
        },
        p,
        v,
    )


def main() -> None:
    fixtures = make_fixture()
    inherited = inherited_e104_billing_firewall()

    first, p1, v1 = execute_once(fixtures)
    second, p2, v2 = execute_once(fixtures)

    repeat_max_abs = max(
        float(np.max(np.abs(p1 - p2))),
        abs(v1 - v2),
    )
    flop_repeat_equal = first["incremental_flops"] == second["incremental_flops"]

    increment = first["incremental_flops"]
    total_upper = E104_MEASURED_FLOPS + increment
    remaining = HARD_FLOP_LIMIT - total_upper
    utilization = total_upper / BUDGET

    gates = {
        "e104_inherited_billing_firewall": all(inherited.values()),
        "increment_finite": first["finite"],
        "plugin_shape_exact": first["plugin_shape"] == [LATE_LAYERS, WIDTH],
        "no_incremental_rng": True,
        "deterministic_repeat_max_abs_eq_0": repeat_max_abs == 0.0,
        "repeat_flop_ledger_equal": flop_repeat_equal,
        "all_in_flops_le_floor_0_13_budget": total_upper <= HARD_FLOP_LIMIT,
        "all_in_utilization_le_0_13": utilization <= 0.13,
        "positive_remaining_flops": remaining > 0,
    }

    result = {
        "schema": "arc.whitebox.e111.late4_gaussian_relu_plugin_cost.v1",
        "experiment": "E111",
        "scope": {
            "cost_only": True,
            "scientific_accuracy": False,
            "public": False,
            "public_mini": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
        },
        "shape": {
            "width": WIDTH,
            "depth": DEPTH,
            "trajectories": TRAJECTORIES,
            "late_layers": LATE_LAYERS,
            "independent_haar_blocks": 2,
        },
        "competition_budget": {
            "budget": BUDGET,
            "utilization_limit": 0.13,
            "hard_flop_limit_floor": HARD_FLOP_LIMIT,
        },
        "inherited_e104": {
            "measured_flops": E104_MEASURED_FLOPS,
            "measured_utilization": E104_MEASURED_UTILIZATION,
            "rng_delta_vs_e103": E104_RNG_DELTA,
            "billing_firewall": inherited,
        },
        "incremental_nonlinear_estimator": {
            "mechanism": "last-4 pre-ReLU sample moments -> analytic Gaussian ReLU mean",
            "formula": "sigma*phi(mu/sigma)+mu*Phi(mu/sigma)",
            "measured_flops": increment,
            "plugin_shape": first["plugin_shape"],
            "plugin_max_abs": first["plugin_max_abs"],
            "fresh_rng": False,
            "fresh_forward_trajectories": False,
            "old_e104_mean_reduction_credit_taken": False,
        },
        "error_estimator": {
            "kind": "two-independent-block plug-in disagreement variance",
            "formula": "mean((plugin0-plugin1)^2)/4",
            "value_on_fixture": first["variance_hat"],
            "included_inside_incremental_flops": True,
            "fresh_rng": False,
            "limitation": (
                "estimates randomization variance of the nonlinear plug-in; "
                "does not certify Gaussian-approximation bias"
            ),
        },
        "determinism": {
            "repeat_max_abs": repeat_max_abs,
            "repeat_flop_ledger_equal": flop_repeat_equal,
        },
        "all_in_upper_bound": {
            "flops": total_upper,
            "utilization": utilization,
            "remaining_flops": remaining,
            "remaining_utilization": remaining / BUDGET,
        },
        "gates": gates,
        "decision": (
            "COST_FEASIBLE_BELOW_0_13"
            if all(gates.values())
            else "TERMINAL_COST_NO_GO"
        ),
        "scientific_go": False,
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E111_COST_AUDIT=" + json.dumps(result, sort_keys=True), flush=True)

    if not all(gates.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
