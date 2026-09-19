from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path
from types import SimpleNamespace

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np

WIDTH = 64
DEPTH = 16
NETWORK_SEEDS = (104200, 104201, 104202, 104203)
REFERENCE_SEEDS = (504200, 504201, 504202, 504203)
IID_BASELINE_SEEDS = (604200, 604201, 604202, 604203)
DIRECTION_SEEDS = (704200, 704201, 704202, 704203)
E100_RADIUS_SEEDS = (804200, 804201, 804202, 804203)
REFERENCE_SAMPLES = 65536
CANDIDATE_SAMPLES = 4096

PROD_WIDTH = 1024
PROD_DEPTH = 16
PROD_SAMPLES = 4096
PROD_WEIGHT_SEED = 104300
PROD_IID_SEED = 104301
BUDGET = 2**41

E104_PROD_FLOPS = 149_047_442_096
E104_PROD_UTIL = 0.06777892944955966
E100_PROD_FLOPS = 149_047_446_192
E100_PROD_UTIL = 0.0677789313122048

E051_RAW = 2.29004485946887e-8
E051_UTIL = 0.267056
TARGET_RAW = 1.89e-8

OUT = Path("e104-independent-error-verify.json")


def mean_chi_radius(width: int) -> float:
    return math.sqrt(2.0) * math.exp(
        math.lgamma((width + 1.0) / 2.0) - math.lgamma(width / 2.0)
    )


def make_weights(seed: int, width: int, depth: int) -> list[np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    scale = np.float32(math.sqrt(2.0 / width))
    return [
        (rng.standard_normal((width, width), dtype=np.float32) * scale).astype(np.float32)
        for _ in range(depth)
    ]


def iid_antithetic(seed: int, total: int, width: int) -> np.ndarray:
    if total % 2:
        raise ValueError("total must be even")
    rng = np.random.Generator(np.random.PCG64(seed))
    pos = rng.standard_normal((total // 2, width), dtype=np.float32)
    return np.concatenate((pos, -pos), axis=0)


def haar_directions(seed: int, total: int, width: int) -> np.ndarray:
    if total % (2 * width):
        raise ValueError("total must be divisible by 2*width")
    rng = np.random.Generator(np.random.PCG64(seed))
    blocks = []
    for _ in range(total // (2 * width)):
        g = rng.standard_normal((width, width)).astype(np.float64)
        q, r = np.linalg.qr(g)
        signs = np.where(np.diag(r) < 0.0, -1.0, 1.0)
        blocks.append(q * signs[None, :])
    return np.concatenate(blocks, axis=0)


def e100_samples(directions: np.ndarray, radius_seed: int, width: int) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(radius_seed))
    radii = np.sqrt(rng.chisquare(df=width, size=directions.shape[0]))
    pos = (radii[:, None] * directions).astype(np.float32)
    return np.concatenate((pos, -pos), axis=0)


def e104_samples(directions: np.ndarray, width: int) -> np.ndarray:
    pos = (mean_chi_radius(width) * directions).astype(np.float32)
    return np.concatenate((pos, -pos), axis=0)


def layer_means(weights: list[np.ndarray], samples: np.ndarray) -> np.ndarray:
    h = np.asarray(samples, dtype=np.float32)
    rows = []
    for w in weights:
        h = h @ w.T
        np.maximum(h, np.float32(0.0), out=h)
        rows.append(np.mean(h, axis=0, dtype=np.float64))
    return np.stack(rows, axis=0)


def errors(pred: np.ndarray, ref: np.ndarray) -> dict[str, float]:
    d = np.asarray(pred, dtype=np.float64) - np.asarray(ref, dtype=np.float64)
    final = d[-1]
    return {
        "final_mse": float(np.mean(final * final)),
        "all_layers_mse": float(np.mean(d * d)),
        "final_max_abs": float(np.max(np.abs(final))),
        "final_sse": float(np.sum(final * final)),
        "all_layers_sse": float(np.sum(d * d)),
    }


def candidate_bundle(
    weights: list[np.ndarray],
    reference: np.ndarray,
    iid_seed: int,
    direction_seed: int,
    radius_seed: int,
) -> dict[str, object]:
    directions = haar_directions(direction_seed, CANDIDATE_SAMPLES, WIDTH)
    direction_hash_before = hashlib.sha256(directions.tobytes()).hexdigest()

    e100_x = e100_samples(directions, radius_seed, WIDTH)
    direction_hash_after_e100 = hashlib.sha256(directions.tobytes()).hexdigest()
    e104_x = e104_samples(directions, WIDTH)
    direction_hash_after_e104 = hashlib.sha256(directions.tobytes()).hexdigest()
    iid_x = iid_antithetic(iid_seed, CANDIDATE_SAMPLES, WIDTH)

    half = CANDIDATE_SAMPLES // 2
    pair_max_abs = {
        "E104": float(np.max(np.abs(e104_x[:half] + e104_x[half:]))),
        "E100": float(np.max(np.abs(e100_x[:half] + e100_x[half:]))),
        "fixed_iid": float(np.max(np.abs(iid_x[:half] + iid_x[half:]))),
    }

    e104_pred = layer_means(weights, e104_x)
    e100_pred = layer_means(weights, e100_x)
    iid_pred = layer_means(weights, iid_x)

    return {
        "directions_hash_unchanged": (
            direction_hash_before == direction_hash_after_e100 == direction_hash_after_e104
        ),
        "pair_max_abs": pair_max_abs,
        "E104_pred": e104_pred,
        "E100_pred": e100_pred,
        "fixed_iid_pred": iid_pred,
        "E104_error": errors(e104_pred, reference),
        "E100_error": errors(e100_pred, reference),
        "fixed_iid_error": errors(iid_pred, reference),
    }


def scalar_signature(bundle: dict[str, object]) -> np.ndarray:
    vals = []
    for name in ("E104", "E100", "fixed_iid"):
        err = bundle[f"{name}_error"]
        vals.extend(
            [err["final_mse"], err["all_layers_mse"], err["final_max_abs"]]
        )
        pred = np.asarray(bundle[f"{name}_pred"], dtype=np.float64)
        vals.extend([float(np.max(pred)), float(np.min(pred)), float(np.sum(pred))])
    return np.asarray(vals, dtype=np.float64)


def measure_fixed_iid_production_cost() -> dict[str, object]:
    weights = make_weights(PROD_WEIGHT_SEED, PROD_WIDTH, PROD_DEPTH)
    rng = np.random.Generator(np.random.PCG64(PROD_IID_SEED))
    pos_np = rng.standard_normal(
        (PROD_SAMPLES // 2, PROD_WIDTH), dtype=np.float32
    )

    started = time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET, quiet=True) as ctx:
        pos = fnp.asarray(pos_np)
        h = fnp.concatenate((pos, -pos), axis=0)
        after_input = int(ctx.flops_used)

        rows = []
        layer_cumulative = []
        for raw_w in weights:
            w = fnp.asarray(raw_w)
            h = fnp.matmul(h, fnp.swapaxes(w, 0, 1))
            fnp.maximum(h, fnp.float32(0.0), out=h)
            rows.append(fnp.mean(h, axis=0, dtype=fnp.float64))
            layer_cumulative.append(int(ctx.flops_used))

        pred = fnp.stack(rows, axis=0)
        total = int(ctx.flops_used)

    wall_s = time.perf_counter() - started
    pred_np = np.asarray(pred, dtype=np.float64)

    layer_flops = []
    previous = after_input
    for current in layer_cumulative:
        layer_flops.append(current - previous)
        previous = current
    finalization = total - previous
    reconciled = after_input + sum(layer_flops) + finalization

    return {
        "finite": bool(np.isfinite(pred_np).all()),
        "shape": list(pred_np.shape),
        "input_flops": after_input,
        "layer_flops": layer_flops,
        "finalization_flops": finalization,
        "reconciled_sum": reconciled,
        "total_flops": total,
        "exact_reconciliation": reconciled == total,
        "utilization": total / BUDGET,
        "wall_s": wall_s,
    }


def main() -> None:
    rows = []
    pooled = {
        "E104": {"final_sse": 0.0, "all_sse": 0.0},
        "E100": {"final_sse": 0.0, "all_sse": 0.0},
        "fixed_iid": {"final_sse": 0.0, "all_sse": 0.0},
    }
    all_finite = True
    deterministic = True
    direction_hashes_unchanged = True
    antithetic_exact = True

    for i, network_seed in enumerate(NETWORK_SEEDS):
        weights = make_weights(network_seed, WIDTH, DEPTH)
        reference = layer_means(
            weights, iid_antithetic(REFERENCE_SEEDS[i], REFERENCE_SAMPLES, WIDTH)
        )

        first = candidate_bundle(
            weights,
            reference,
            IID_BASELINE_SEEDS[i],
            DIRECTION_SEEDS[i],
            E100_RADIUS_SEEDS[i],
        )
        second = candidate_bundle(
            weights,
            reference,
            IID_BASELINE_SEEDS[i],
            DIRECTION_SEEDS[i],
            E100_RADIUS_SEEDS[i],
        )

        signature_equal = bool(
            np.array_equal(scalar_signature(first), scalar_signature(second))
        )
        pred_equal = all(
            np.array_equal(
                np.asarray(first[f"{name}_pred"]),
                np.asarray(second[f"{name}_pred"]),
            )
            for name in ("E104", "E100", "fixed_iid")
        )
        deterministic &= signature_equal and pred_equal
        direction_hashes_unchanged &= bool(first["directions_hash_unchanged"])

        pair_info = first["pair_max_abs"]
        antithetic_exact &= all(float(v) == 0.0 for v in pair_info.values())

        finite = bool(
            np.isfinite(reference).all()
            and all(
                np.isfinite(np.asarray(first[f"{name}_pred"])).all()
                for name in ("E104", "E100", "fixed_iid")
            )
        )
        all_finite &= finite

        row = {
            "network_seed": network_seed,
            "finite": finite,
            "deterministic_repeat": signature_equal and pred_equal,
            "directions_hash_unchanged": bool(first["directions_hash_unchanged"]),
            "pair_max_abs": pair_info,
        }
        for name in ("E104", "E100", "fixed_iid"):
            err = first[f"{name}_error"]
            row[name] = {
                "final_mse": err["final_mse"],
                "all_layers_mse": err["all_layers_mse"],
                "final_max_abs": err["final_max_abs"],
            }
            pooled[name]["final_sse"] += err["final_sse"]
            pooled[name]["all_sse"] += err["all_layers_sse"]
        row["ratios"] = {
            "E104_over_E100_final": row["E104"]["final_mse"] / row["E100"]["final_mse"],
            "E104_over_fixed_iid_final": row["E104"]["final_mse"] / row["fixed_iid"]["final_mse"],
        }
        rows.append(row)

    final_count = len(NETWORK_SEEDS) * WIDTH
    all_count = len(NETWORK_SEEDS) * WIDTH * DEPTH
    aggregate = {}
    for name in ("E104", "E100", "fixed_iid"):
        aggregate[name] = {
            "final_raw_mse": pooled[name]["final_sse"] / final_count,
            "all_layers_mse": pooled[name]["all_sse"] / all_count,
        }

    aggregate["ratios"] = {
        "E104_over_E100_final": (
            aggregate["E104"]["final_raw_mse"] / aggregate["E100"]["final_raw_mse"]
        ),
        "E104_over_fixed_iid_final": (
            aggregate["E104"]["final_raw_mse"] / aggregate["fixed_iid"]["final_raw_mse"]
        ),
        "E100_over_fixed_iid_final": (
            aggregate["E100"]["final_raw_mse"] / aggregate["fixed_iid"]["final_raw_mse"]
        ),
    }
    aggregate["wins"] = {
        "E104_vs_E100": int(
            sum(row["E104"]["final_mse"] < row["E100"]["final_mse"] for row in rows)
        ),
        "E104_vs_fixed_iid": int(
            sum(row["E104"]["final_mse"] < row["fixed_iid"]["final_mse"] for row in rows)
        ),
    }

    fixed_iid_cost = measure_fixed_iid_production_cost()

    integrity_gates = {
        "all_finite": all_finite,
        "deterministic_repeat_exact": deterministic,
        "direction_hashes_unchanged": direction_hashes_unchanged,
        "antithetic_exact": antithetic_exact,
        "fixed_iid_cost_finite": fixed_iid_cost["finite"],
        "fixed_iid_cost_shape": fixed_iid_cost["shape"] == [PROD_DEPTH, PROD_WIDTH],
        "fixed_iid_accounting_exact": fixed_iid_cost["exact_reconciliation"],
    }

    out = {
        "schema": "arc.whitebox.e104.independent_error_verify.v1",
        "experiment": "E104",
        "same_corpus": {
            "width": WIDTH,
            "depth": DEPTH,
            "network_seeds": NETWORK_SEEDS,
            "reference_samples": REFERENCE_SAMPLES,
            "candidate_samples": CANDIDATE_SAMPLES,
            "rows": rows,
            "aggregate": aggregate,
        },
        "production_cost": {
            "E104": {
                "source": "physical independent production verifier run 35446062235",
                "flops": E104_PROD_FLOPS,
                "utilization": E104_PROD_UTIL,
            },
            "E100": {
                "source": "physical E103 production run 35287256818",
                "flops": E100_PROD_FLOPS,
                "utilization": E100_PROD_UTIL,
            },
            "fixed_iid": fixed_iid_cost,
        },
        "historical_competition_reference": {
            "E051_raw_final_layer_mse": E051_RAW,
            "E051_utilization": E051_UTIL,
            "competition_target_raw": TARGET_RAW,
            "same_corpus_comparable": False,
        },
        "integrity_gates": integrity_gates,
        "verification_pass": bool(all(integrity_gates.values())),
        "scientific_target": {
            "raw_le_1_89e_8_executed": False,
            "reason": (
                "No authorized benchmark/public target was read. Synthetic raw MSE is "
                "not a substitute for the competition raw threshold."
            ),
            "next_executable_step": (
                "Under a successor protocol and explicit benchmark authorization, run exactly "
                "one frozen width=1024 depth=16 N=4096 E104 evaluation on the same benchmark "
                "record/split used for the E051 comparison, record final-layer raw MSE, "
                "flopscope all-in utilization, failures, and compare directly to E051 "
                "raw=2.29004485946887e-08 and target=1.89e-08. No tuning or rerun."
            ),
        },
        "scope": {
            "synthetic_only": True,
            "public": False,
            "official_scorer": False,
            "holdout": False,
            "full_suite": False,
            "benchmark_targets": False,
            "tuning": False,
        },
    }

    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E104_INDEPENDENT_ERROR_VERIFY=" + json.dumps(out, sort_keys=True), flush=True)
    if not out["verification_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
