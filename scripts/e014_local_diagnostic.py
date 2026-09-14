from __future__ import annotations

import argparse
import importlib.util
import json
import traceback
from pathlib import Path

import flopscope as flops
import numpy as np
import whestbench

FLOP_BUDGET = 2**41
WALL_TIME_LIMIT_S = 180.0
MSE_RATIO_GATE = 1.01
FLOP_RATIO_GATE = 0.9995
RESIDUAL_RATIO_GATE = 1.0
DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
INDEX = 0


def _load_estimator(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import estimator from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Estimator()


def _ctx_metric(ctx, name: str):
    value = getattr(ctx, name, None)
    if value is None:
        return None
    if isinstance(value, (int, np.integer)):
        return int(value)
    return float(value)


def measure(estimator_path: Path, output: Path, label: str) -> int:
    ds = whestbench.load_dataset(DATASET, revision=REVISION, split=SPLIT)
    mlp = whestbench.mlp_at(ds, INDEX)
    target = np.asarray(ds[INDEX]["final_means"], dtype=np.float64)
    expected_shape = (len(mlp.weights), mlp.width)
    ctx = None
    prediction = None
    error = None

    try:
        estimator = _load_estimator(estimator_path, f"e014_{label}")
        with flops.BudgetContext(
            flop_budget=FLOP_BUDGET,
            wall_time_limit_s=WALL_TIME_LIMIT_S,
        ) as ctx:
            prediction = estimator.predict(mlp, FLOP_BUDGET)
    except Exception as exc:  # noqa: BLE001 - diagnostic must record failure and gate it
        error = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()

    result = {
        "experiment": "E014",
        "scope": "public Phase-2 mini index 0 direct estimator diagnostic",
        "label": label,
        "estimator": str(estimator_path),
        "index": INDEX,
        "flop_budget": FLOP_BUDGET,
        "success": prediction is not None and error is None,
        "error": error,
        "flops_used": _ctx_metric(ctx, "flops_used") if ctx is not None else None,
        "residual_wall_time_s": (
            _ctx_metric(ctx, "residual_wall_time_s") if ctx is not None else None
        ),
        "backend_time_s": (
            _ctx_metric(ctx, "flopscope_backend_time_s") if ctx is not None else None
        ),
        "wrapper_overhead_s": (
            _ctx_metric(ctx, "flopscope_overhead_time_s") if ctx is not None else None
        ),
        "wall_time_s": _ctx_metric(ctx, "wall_time_s") if ctx is not None else None,
    }

    if prediction is not None:
        pred = np.asarray(prediction, dtype=np.float64)
        finite = bool(np.all(np.isfinite(pred)))
        shape_ok = tuple(pred.shape) == expected_shape
        mse = float(np.mean((pred[-1] - target) ** 2)) if finite and shape_ok else None
        result.update(
            {
                "prediction_shape": list(pred.shape),
                "expected_shape": list(expected_shape),
                "finite": finite,
                "shape_ok": shape_ok,
                "final_layer_mse": mse,
            }
        )
    else:
        result.update(
            {
                "prediction_shape": None,
                "expected_shape": list(expected_shape),
                "finite": False,
                "shape_ok": False,
                "final_layer_mse": None,
            }
        )

    flops_used = result["flops_used"]
    result["billed_utilization"] = (
        flops_used / FLOP_BUDGET if flops_used is not None else None
    )
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def _ratio(numerator, denominator):
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return float(numerator / denominator)


def compare(baseline_path: Path, candidate_path: Path) -> int:
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))

    mse_ratio = _ratio(candidate.get("final_layer_mse"), baseline.get("final_layer_mse"))
    flop_ratio = _ratio(candidate.get("flops_used"), baseline.get("flops_used"))
    residual_ratio = _ratio(
        candidate.get("residual_wall_time_s"), baseline.get("residual_wall_time_s")
    )

    gates = {
        "baseline_valid": bool(
            baseline.get("success") and baseline.get("finite") and baseline.get("shape_ok")
        ),
        "candidate_valid": bool(
            candidate.get("success") and candidate.get("finite") and candidate.get("shape_ok")
        ),
        "mse": mse_ratio is not None and mse_ratio <= MSE_RATIO_GATE,
        "billed_flops": flop_ratio is not None and flop_ratio <= FLOP_RATIO_GATE,
        "residual": residual_ratio is not None and residual_ratio <= RESIDUAL_RATIO_GATE,
    }
    decision = "GO" if all(gates.values()) else "DROP"
    summary = {
        "experiment": "E014",
        "scope": "frozen local promotion gate",
        "baseline": baseline,
        "candidate": candidate,
        "mse_ratio": mse_ratio,
        "flop_ratio": flop_ratio,
        "residual_ratio": residual_ratio,
        "gates": gates,
        "thresholds": {
            "mse_ratio_max": MSE_RATIO_GATE,
            "flop_ratio_max": FLOP_RATIO_GATE,
            "residual_ratio_max": RESIDUAL_RATIO_GATE,
        },
        "decision": decision,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"LOCAL_DECISION={decision}")
    return 0 if decision == "GO" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    measure_parser = sub.add_parser("measure")
    measure_parser.add_argument("--estimator", type=Path, required=True)
    measure_parser.add_argument("--output", type=Path, required=True)
    measure_parser.add_argument("--label", required=True)

    compare_parser = sub.add_parser("compare")
    compare_parser.add_argument("--baseline", type=Path, required=True)
    compare_parser.add_argument("--candidate", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "measure":
        return measure(args.estimator, args.output, args.label)
    return compare(args.baseline, args.candidate)


if __name__ == "__main__":
    raise SystemExit(main())
