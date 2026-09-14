from __future__ import annotations

import hashlib
import importlib.util
import json
import statistics
import tempfile
import urllib.request
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
import whestbench

from methods.e015_mz_prony import (
    auxiliary_state_count,
    fit_shared_order3,
    poles_from_coefficients,
    rollout_order3,
)

UPSTREAM_URL = (
    "https://raw.githubusercontent.com/504aldo/whest-p2-cumulant-k3/"
    "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45/estimators/estimator_v29.py"
)
EXPECTED_BLOB = "17df1a073a24f96c4705b04bcf61ef60fa06dd0c"
DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
FLOP_BUDGET = 2**41
FIT_INDICES = (0, 1, 2, 3)
VALID_INDICES = (4, 5, 6, 7)
FIT_LAYER_START = 8
FIT_LAYER_END = 14
MEAN_RMS_GATE = 0.015
WORST_RMS_GATE = 0.022
UTIL_GATE = 0.21
V29_TOTAL_UNITS = 260.09
V29_OLD_UNITS = 106.79
V29_RETAINED_UNITS = V29_TOTAL_UNITS - V29_OLD_UNITS
N = 1024
R_OLD = 384
R_OLD2 = 224
ACTIVE_OLD_LAYERS = 10  # layers 5..14
PROXY_REPS = 7


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324 - Git object identity


def instrument_v29_source(source: str) -> str:
    import_marker = "import math\n"
    layer_marker = "        for li, w in enumerate(mlp.weights):\n            last = li == L - 1\n"
    old_marker = (
        "            if ka < k and STRASSEN_HUB > 0:\n"
        "                D21 = self._hub2(bufs, apb4, ka, k, n)\n"
        "                fnp.add(D21, fnp.matmul(inner, Qc.T, out=bufs[\"t1\"]), out=D21)\n"
    )
    if import_marker not in source:
        raise ValueError("import marker not found")
    if old_marker not in source:
        raise ValueError("old-tier D21 marker not found")
    if layer_marker not in source:
        raise ValueError("layer marker not found")

    source = source.replace(
        import_marker,
        "import math\nimport numpy as _e015_np\n\nE015_TRACE = []\nE015_LAYER = [-1]\n",
        1,
    )
    source = source.replace(
        layer_marker,
        "        for li, w in enumerate(mlp.weights):\n"
        "            E015_LAYER[0] = li\n"
        "            last = li == L - 1\n",
        1,
    )
    replacement = (
        "            if ka < k and STRASSEN_HUB > 0:\n"
        "                D21 = self._hub2(bufs, apb4, ka, k, n)\n"
        "                fnp.matmul(inner, Qc.T, out=bufs[\"t1\"])\n"
        "                if 5 <= E015_LAYER[0] <= 14:\n"
        "                    E015_TRACE.append({\n"
        "                        \"layer\": int(E015_LAYER[0]),\n"
        "                        \"ka\": int(ka),\n"
        "                        \"kb\": int(kb),\n"
        "                        \"k\": int(k),\n"
        "                        \"young\": _e015_np.array(D21, copy=True),\n"
        "                        \"old\": _e015_np.array(bufs[\"t1\"], copy=True),\n"
        "                    })\n"
        "                fnp.add(D21, bufs[\"t1\"], out=D21)\n"
    )
    return source.replace(old_marker, replacement, 1)


def _load_instrumented_module():
    with urllib.request.urlopen(UPSTREAM_URL, timeout=30) as response:  # noqa: S310
        data = response.read()
    actual_blob = _git_blob_sha(data)
    if actual_blob != EXPECTED_BLOB:
        raise RuntimeError(f"V29 blob mismatch: {actual_blob} != {EXPECTED_BLOB}")
    patched = instrument_v29_source(data.decode("utf-8"))
    temp = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8")
    try:
        temp.write(patched)
        temp.close()
        path = Path(temp.name)
        spec = importlib.util.spec_from_file_location("e015_v29_instrumented", path)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot import instrumented V29")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, actual_blob
    finally:
        try:
            Path(temp.name).unlink(missing_ok=True)
        except OSError:
            pass


def _old_history_bytes(ka: int, kb: int) -> int:
    """Conservative persistent bytes for the V29 old dense-history representation."""
    tier1 = max(ka - kb, 0)
    values = N * R_OLD  # Qc
    values += 2 * tier1 * R_OLD * N  # FAo / FPo
    if kb > 0:
        values += 2 * kb * R_OLD2 * N  # FA2 / FP2
        values += R_OLD * R_OLD2  # nested sub-basis U
    return int(values * 4)


def _extract_record(module, ds, index: int):
    module.E015_TRACE.clear()
    estimator = module.Estimator()
    mlp = whestbench.mlp_at(ds, index)
    error = None
    ctx = None
    try:
        with flops.BudgetContext(flop_budget=FLOP_BUDGET, wall_time_limit_s=180.0) as ctx:
            prediction = estimator.predict(mlp, FLOP_BUDGET)
        finite_prediction = bool(np.all(np.isfinite(np.asarray(prediction))))
    except Exception as exc:  # noqa: BLE001 - diagnostic records hard blockers
        error = f"{type(exc).__name__}: {exc}"
        finite_prediction = False

    trace = sorted(module.E015_TRACE, key=lambda item: item["layer"])
    layers = [item["layer"] for item in trace]
    expected_layers = list(range(5, 15))
    if error is None and layers != expected_layers:
        error = f"trace layers {layers} != {expected_layers}"
    if error is not None:
        return None, None, {
            "index": index,
            "error": error,
            "finite_prediction": finite_prediction,
            "flops_used": getattr(ctx, "flops_used", None) if ctx is not None else None,
        }

    young = np.stack([np.asarray(item["young"], dtype=np.float32) for item in trace])
    old = np.stack([np.asarray(item["old"], dtype=np.float32) for item in trace])
    geometry = [
        {
            "layer": int(item["layer"]),
            "ka": int(item["ka"]),
            "kb": int(item["kb"]),
            "k": int(item["k"]),
            "old_history_bytes": _old_history_bytes(int(item["ka"]), int(item["kb"])),
        }
        for item in trace
    ]
    return young, old, {
        "index": index,
        "error": None,
        "finite_prediction": finite_prediction,
        "flops_used": int(ctx.flops_used),
        "billed_utilization": float(ctx.flops_used / FLOP_BUDGET),
        "residual_wall_time_s": float(ctx.residual_wall_time_s),
        "geometry": geometry,
    }


def _relative_rms(pred: np.ndarray, truth: np.ndarray) -> float:
    denom = float(np.sqrt(np.mean(np.square(truth, dtype=np.float64))))
    if denom == 0.0:
        return 0.0 if np.array_equal(pred, truth) else float("inf")
    numer = float(np.sqrt(np.mean(np.square(pred - truth, dtype=np.float64))))
    return numer / denom


def _measure_proxy_once(kind: str, rng: np.random.Generator):
    if kind == "baseline":
        left = rng.standard_normal((N, R_OLD), dtype=np.float32)
        right = rng.standard_normal((R_OLD, N), dtype=np.float32)
        out = np.empty((N, N), dtype=np.float32)
        with flops.BudgetContext(flop_budget=20_000_000_000, wall_time_limit_s=30.0) as ctx:
            fnp.matmul(left, right, out=out)
        return int(ctx.flops_used), float(ctx.residual_wall_time_s)

    u = rng.standard_normal((N, N), dtype=np.float32)
    states = [rng.standard_normal((N, N), dtype=np.float32) for _ in range(3)]
    w = np.empty_like(u)
    y = np.empty_like(u)
    tmp = np.empty_like(u)
    coeff = np.array([0.3, -0.08, 0.02, 0.7, 0.12, -0.04, 0.01], dtype=np.float32)
    with flops.BudgetContext(flop_budget=20_000_000_000, wall_time_limit_s=30.0) as ctx:
        fnp.multiply(states[0], coeff[0], out=w)
        fnp.add(w, u, out=w)
        for j in (1, 2):
            fnp.multiply(states[j], coeff[j], out=tmp)
            fnp.add(w, tmp, out=w)
        fnp.multiply(w, coeff[3], out=y)
        for j in range(3):
            fnp.multiply(states[j], coeff[4 + j], out=tmp)
            fnp.add(y, tmp, out=y)
    return int(ctx.flops_used), float(ctx.residual_wall_time_s)


def _proxy_measurements():
    _measure_proxy_once("baseline", np.random.default_rng(1500))
    _measure_proxy_once("candidate", np.random.default_rng(1501))
    baseline = [
        _measure_proxy_once("baseline", np.random.default_rng(1510 + i))
        for i in range(PROXY_REPS)
    ]
    candidate = [
        _measure_proxy_once("candidate", np.random.default_rng(1520 + i))
        for i in range(PROXY_REPS)
    ]
    return {
        "baseline_flops": baseline[0][0],
        "candidate_flops": candidate[0][0],
        "baseline_residual_s_all": [x[1] for x in baseline],
        "candidate_residual_s_all": [x[1] for x in candidate],
        "baseline_residual_s_median": statistics.median(x[1] for x in baseline),
        "candidate_residual_s_median": statistics.median(x[1] for x in candidate),
    }


def main() -> int:
    module, blob = _load_instrumented_module()
    ds = whestbench.load_dataset(DATASET, revision=REVISION, split=SPLIT)

    train_u = []
    train_y = []
    extraction = []
    baseline_utils = []
    baseline_storage = []
    hard_error = None

    for index in FIT_INDICES:
        u, y, meta = _extract_record(module, ds, index)
        extraction.append(meta)
        if u is None or y is None:
            hard_error = meta["error"]
            break
        train_u.append(u)
        train_y.append(y)
        baseline_utils.append(meta["billed_utilization"])
        baseline_storage.extend(
            item["old_history_bytes"]
            for item in meta["geometry"]
            if FIT_LAYER_START <= item["layer"] <= FIT_LAYER_END
        )

    if hard_error is not None:
        result = {
            "experiment": "E015",
            "decision": "NO-GO",
            "blocker": hard_error,
            "extraction": extraction,
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        print("DECISION=NO-GO")
        return 0

    coefficients = fit_shared_order3(train_u, train_y, fit_start=3)
    coefficients_repeat = fit_shared_order3(train_u, train_y, fit_start=3)
    poles = poles_from_coefficients(coefficients)
    fit_deterministic = bool(np.array_equal(coefficients, coefficients_repeat))
    finite_model = bool(np.all(np.isfinite(coefficients)) and np.all(np.isfinite(poles)))
    stable = bool(np.max(np.abs(poles)) < 1.0) if finite_model else False

    validation_errors = []
    rollout_deterministic = True
    for index in VALID_INDICES:
        u, y, meta = _extract_record(module, ds, index)
        extraction.append(meta)
        if u is None or y is None:
            hard_error = meta["error"]
            break
        baseline_utils.append(meta["billed_utilization"])
        baseline_storage.extend(
            item["old_history_bytes"]
            for item in meta["geometry"]
            if FIT_LAYER_START <= item["layer"] <= FIT_LAYER_END
        )
        pred = rollout_order3(u, coefficients)
        pred_repeat = rollout_order3(u.copy(), coefficients.copy())
        rollout_deterministic &= bool(np.array_equal(pred, pred_repeat))
        for offset, layer in enumerate(range(5, 15)):
            if FIT_LAYER_START <= layer <= FIT_LAYER_END:
                validation_errors.append(
                    {
                        "index": index,
                        "layer": layer,
                        "relative_rms": _relative_rms(pred[offset], y[offset]),
                    }
                )

    proxy = _proxy_measurements()
    recurrence_flops_per_layer = proxy["candidate_flops"]
    mean_v29_util = float(np.mean(baseline_utils)) if baseline_utils else float("inf")
    projected_util = (
        mean_v29_util * (V29_RETAINED_UNITS / V29_TOTAL_UNITS)
        + ACTIVE_OLD_LAYERS * recurrence_flops_per_layer / FLOP_BUDGET
    )
    persistent_state_bytes = 3 * N * N * 4
    minimum_replaced_history_bytes = int(min(baseline_storage)) if baseline_storage else 0
    maximum_replaced_history_bytes = int(max(baseline_storage)) if baseline_storage else 0

    if validation_errors:
        values = [item["relative_rms"] for item in validation_errors]
        mean_rms = float(np.mean(values))
        worst_rms = float(np.max(values))
    else:
        mean_rms = float("inf")
        worst_rms = float("inf")

    gates = {
        "extraction": hard_error is None,
        "mean_rms": mean_rms <= MEAN_RMS_GATE,
        "worst_rms": worst_rms <= WORST_RMS_GATE,
        "auxiliary_states": auxiliary_state_count() <= 3,
        "shared_coefficients_only": coefficients.shape == (7,),
        "deterministic": fit_deterministic and rollout_deterministic,
        "finite": finite_model,
        "stable_poles": stable,
        "projected_utilization": projected_util <= UTIL_GATE,
        "residual": proxy["candidate_residual_s_median"] <= proxy["baseline_residual_s_median"],
        "persistent_resource": persistent_state_bytes <= minimum_replaced_history_bytes,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"
    result = {
        "experiment": "E015",
        "scope": "public dev indices 0-7 direct instrumented V29; no whest scorer or holdout",
        "v29_blob": blob,
        "fit_indices": list(FIT_INDICES),
        "validation_indices": list(VALID_INDICES),
        "coefficients": coefficients.tolist(),
        "poles_real_imag": [[float(z.real), float(z.imag)] for z in poles],
        "pole_radius_max": float(np.max(np.abs(poles))) if finite_model else None,
        "fit_deterministic": fit_deterministic,
        "rollout_deterministic": rollout_deterministic,
        "validation_mean_relative_rms": mean_rms,
        "validation_worst_relative_rms": worst_rms,
        "validation_errors": validation_errors,
        "mean_v29_dev_utilization": mean_v29_util,
        "projected_total_utilization": projected_util,
        "recurrence_flops_per_active_layer": recurrence_flops_per_layer,
        "persistent_state_bytes": persistent_state_bytes,
        "minimum_replaced_history_bytes_scored_layers": minimum_replaced_history_bytes,
        "maximum_replaced_history_bytes_scored_layers": maximum_replaced_history_bytes,
        "proxy": proxy,
        "extraction": extraction,
        "gates": gates,
        "decision": decision,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"DECISION={decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
