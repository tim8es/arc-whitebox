"""Frozen E018 read-only old-D21 importance-sampling diagnostic.

The script loads the pinned public V25 estimator, subclasses it only to observe
states passed to `_dslices`, and leaves the estimator's arithmetic/output
unchanged. It never reads target final means.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import time
from pathlib import Path

import flopscope as flops
import numpy as np
import whestbench

from methods.e018_importance_d21 import (
    SAMPLE_COUNT,
    importance_draws,
    norm_optimal_probabilities,
    seed_for,
)

DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
DUMP_INDICES = (4, 5, 6, 7)
LAYERS = tuple(range(8, 15))
FLOP_BUDGET = 2**41
DIAGNOSTIC_WALL_LIMIT_S = 3600.0

AGGREGATE_RMS_GATE = 0.015
WORST_RMS_GATE = 0.022
TARGET_FAMILY_RATIO_GATE = 0.4466845878
PROJECTED_UTIL_GATE = 0.325
PROJECTED_ADJUSTED_GATE = 7.25e-09
E007_RAW = 2.23e-08
E007_UTIL = 0.36666448
E007_ADJUSTED = 8.17e-09
OLD_FAMILY_UNITS = 55.8
TOTAL_UNITS = 260.1
OVERHEAD_UNITS = 4.0


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location("e018_upstream_v25", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load pinned V25 from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _projected_metrics() -> dict[str, float]:
    sampled_units = OLD_FAMILY_UNITS * (SAMPLE_COUNT / 1024.0)
    allowed_units = sampled_units + OVERHEAD_UNITS
    family_ratio = allowed_units / OLD_FAMILY_UNITS
    saving = (OLD_FAMILY_UNITS - allowed_units) / TOTAL_UNITS
    utilization = E007_UTIL * (1.0 - saving)
    adjusted = E007_RAW * utilization
    return {
        "sampled_units": sampled_units,
        "allowed_units": allowed_units,
        "target_family_ratio": family_ratio,
        "net_chain_saving": saving,
        "projected_utilization": utilization,
        "projected_adjusted_score": adjusted,
    }


def _stack_float(arrays) -> np.ndarray:
    return np.stack([np.asarray(x, dtype=np.float32) for x in arrays], axis=0)


def _right_projected_norm(inner: np.ndarray, r_factor: np.ndarray) -> float:
    projected = np.asarray(inner, dtype=np.float64) @ np.asarray(
        r_factor.T, dtype=np.float64
    )
    return float(np.linalg.norm(projected, ord="fro"))


def _source_record(
    *,
    dump_index: int,
    layer: int,
    source_index: int,
    la: np.ndarray,
    lp: np.ndarray,
    fa: np.ndarray,
    fp: np.ndarray,
    ap: np.ndarray,
    aa: np.ndarray,
    pp: np.ndarray,
    r_factor: np.ndarray,
    tier: int,
) -> dict[str, object]:
    probabilities = norm_optimal_probabilities(ap, aa, pp)
    seed = seed_for(dump_index, layer, source_index)
    indices, weights = importance_draws(
        probabilities, sample_count=SAMPLE_COUNT, seed=seed
    )

    exact_inner = la @ fa.T + lp @ fp.T
    sampled_inner = (
        (la[:, indices] * weights[None, :]) @ fa[:, indices].T
        + (lp[:, indices] * weights[None, :]) @ fp[:, indices].T
    )
    error_inner = sampled_inner - exact_inner

    ref_norm = _right_projected_norm(exact_inner, r_factor)
    err_norm = _right_projected_norm(error_inner, r_factor)
    relative_rms = 0.0 if ref_norm == 0.0 and err_norm == 0.0 else (
        math.inf if ref_norm == 0.0 else err_norm / ref_norm
    )
    return {
        "dump": dump_index,
        "layer": layer,
        "source": source_index,
        "tier": tier,
        "sample_count": SAMPLE_COUNT,
        "seed": seed,
        "relative_rms": float(relative_rms),
        "reference_frobenius": ref_norm,
        "error_frobenius": err_norm,
        "probability_min": float(np.min(probabilities)),
        "probability_max": float(np.max(probabilities)),
        "unique_rows": int(np.unique(indices).size),
        "finite": bool(
            np.isfinite(relative_rms)
            and np.all(np.isfinite(sampled_inner))
            and np.all(np.isfinite(probabilities))
        ),
    }


def _make_instrumented_estimator(module, dump_index: int, records: list[dict[str, object]]):
    base = module.Estimator

    class InstrumentedEstimator(base):
        def predict(self, mlp, flop_budget):
            self._e018_layer = -1
            return super().predict(mlp, flop_budget)

        def _dslices(
            self,
            A_st,
            P_st,
            Z_st,
            L_st,
            w2b_list,
            s_list,
            e_list,
            c1_list,
            c2_list,
            y_list,
            n,
            bufs,
            rres,
            rfb,
            Zf_st,
            R1T_st,
            R2T_st,
            need_d21=True,
            ka=0,
            FAo=None,
            FPo=None,
            Qc=None,
            kb=0,
            FA2=None,
            FP2=None,
            U2=None,
        ):
            self._e018_layer += 1
            layer = self._e018_layer

            result = super()._dslices(
                A_st,
                P_st,
                Z_st,
                L_st,
                w2b_list,
                s_list,
                e_list,
                c1_list,
                c2_list,
                y_list,
                n,
                bufs,
                rres,
                rfb,
                Zf_st,
                R1T_st,
                R2T_st,
                need_d21=need_d21,
                ka=ka,
                FAo=FAo,
                FPo=FPo,
                Qc=Qc,
                kb=kb,
                FA2=FA2,
                FP2=FP2,
                U2=U2,
            )

            if not need_d21 or ka <= 0 or layer not in LAYERS:
                return result

            A = np.asarray(A_st, dtype=np.float32)
            P = np.asarray(P_st, dtype=np.float32)
            Z = np.asarray(Z_st, dtype=np.float32)
            L = np.asarray(L_st, dtype=np.float32)
            k = len(w2b_list)
            W2B = _stack_float(w2b_list).reshape(k, 1, n)
            Sb = _stack_float(s_list).reshape(k, 1, n)
            Eb = _stack_float(e_list).reshape(k, 1, n)

            AP = A * P
            AA = A * A
            PP = P * P
            MP = np.einsum("kiq,kjq->kij", Z, L, optimize=True)
            MP = MP * P + PP * Sb + AP * (Eb * 3.0)
            LA = AP * (W2B * 2.0) + PP * Eb
            LP = AA * W2B + PP * (Sb / 3.0) + MP * (2.0 / 3.0)

            if rfb > 0:
                Zf = np.asarray(Zf_st, dtype=np.float32)
                R1T = np.asarray(R1T_st, dtype=np.float32)
                R2T = np.asarray(R2T_st, dtype=np.float32)
                F1 = Zf[:, :, :rfb]
                F2 = Zf[:, :, rfb:]
                Xt = np.einsum("kiq,kjq->kij", F1, R1T, optimize=True)
                Yt = np.einsum("kiq,kjq->kij", F2, R2T, optimize=True)
                LP = LP + A * Yt + Xt * A * (W2B / 3.0) + Xt * Yt / 3.0
                LA = LA + Xt * P * (W2B / 3.0) + P * Yt

            C1 = _stack_float(c1_list)
            C2 = _stack_float(c2_list)
            Yk = Z[:, :, rres + 1]
            feed = A * C1[:, None, :] + P * C2[:, None, :]
            LP = LP + feed * ((2.0 / 3.0) * Yk[:, :, None])

            Qc_np = np.asarray(Qc, dtype=np.float64)
            r_tier1 = np.linalg.qr(Qc_np, mode="r")
            if kb > 0:
                U_np = np.asarray(U2, dtype=np.float64)
                r_tier2 = np.linalg.qr(Qc_np @ U_np, mode="r")
            else:
                r_tier2 = None

            for source in range(int(ka)):
                if source < int(kb):
                    fa = np.asarray(FA2[source], dtype=np.float32)
                    fp = np.asarray(FP2[source], dtype=np.float32)
                    r_factor = r_tier2
                    tier = 2
                else:
                    local = source - int(kb)
                    fa = np.asarray(FAo[local], dtype=np.float32)
                    fp = np.asarray(FPo[local], dtype=np.float32)
                    r_factor = r_tier1
                    tier = 1
                record = _source_record(
                    dump_index=dump_index,
                    layer=layer,
                    source_index=source,
                    la=LA[source],
                    lp=LP[source],
                    fa=fa,
                    fp=fp,
                    ap=AP[source],
                    aa=AA[source],
                    pp=PP[source],
                    r_factor=r_factor,
                    tier=tier,
                )
                records.append(record)
                print(
                    "E018_RECORD "
                    + json.dumps(record, sort_keys=True, separators=(",", ":"))
                )

            return result

    return InstrumentedEstimator()


def run(upstream: Path) -> dict[str, object]:
    module = _load_module(upstream)
    dataset = whestbench.load_dataset(DATASET, revision=REVISION, split=SPLIT)
    records: list[dict[str, object]] = []
    dump_wall_times: dict[str, float] = {}

    for dump_index in DUMP_INDICES:
        mlp = whestbench.mlp_at(dataset, dump_index)
        estimator = _make_instrumented_estimator(module, dump_index, records)
        started = time.perf_counter()
        with flops.BudgetContext(
            flop_budget=FLOP_BUDGET,
            wall_time_limit_s=DIAGNOSTIC_WALL_LIMIT_S,
        ):
            prediction = estimator.predict(mlp, FLOP_BUDGET)
        elapsed = time.perf_counter() - started
        dump_wall_times[str(dump_index)] = elapsed
        pred = np.asarray(prediction)
        if pred.shape != (len(mlp.weights), mlp.width) or not np.all(np.isfinite(pred)):
            raise RuntimeError(f"V25 diagnostic prediction invalid for dump {dump_index}")

    if not records:
        raise RuntimeError("no frozen old-source diagnostic records were captured")

    ref_sq = sum(float(r["reference_frobenius"]) ** 2 for r in records)
    err_sq = sum(float(r["error_frobenius"]) ** 2 for r in records)
    aggregate = math.sqrt(err_sq / ref_sq) if ref_sq > 0.0 else math.inf
    worst = max(float(r["relative_rms"]) for r in records)
    all_finite = all(bool(r["finite"]) for r in records)
    expected_pairs = {(d, l) for d in DUMP_INDICES for l in LAYERS}
    observed_pairs = {(int(r["dump"]), int(r["layer"])) for r in records}

    projected = _projected_metrics()
    gates = {
        "aggregate_relative_rms": aggregate <= AGGREGATE_RMS_GATE,
        "worst_relative_rms": worst <= WORST_RMS_GATE,
        "target_family_ratio": projected["target_family_ratio"]
        <= TARGET_FAMILY_RATIO_GATE + 1e-12,
        "projected_utilization": projected["projected_utilization"]
        <= PROJECTED_UTIL_GATE,
        "projected_adjusted": projected["projected_adjusted_score"]
        <= PROJECTED_ADJUSTED_GATE
        and projected["projected_adjusted_score"] < E007_ADJUSTED,
        "finite_deterministic_contract": all_finite,
        "all_frozen_dump_layers_observed": observed_pairs == expected_pairs,
        "no_persistent_nxn_candidate_state": True,
        "diagnostic_completed_without_exhaustion": True,
    }
    decision = "GO" if all(gates.values()) else "NO-GO"
    return {
        "experiment": "E018",
        "decision": decision,
        "sample_count": SAMPLE_COUNT,
        "sampling": "with_replacement",
        "probability_rule": "stacked_AP_AA_PP_column_frobenius_norm",
        "dumps": list(DUMP_INDICES),
        "layers": list(LAYERS),
        "record_count": len(records),
        "aggregate_relative_rms": aggregate,
        "worst_relative_rms": worst,
        "median_relative_rms": float(np.median([r["relative_rms"] for r in records])),
        "dump_wall_times_s": dump_wall_times,
        "projected": projected,
        "gates": gates,
        "thresholds": {
            "aggregate_relative_rms_max": AGGREGATE_RMS_GATE,
            "worst_relative_rms_max": WORST_RMS_GATE,
            "target_family_ratio_max": TARGET_FAMILY_RATIO_GATE,
            "projected_utilization_max": PROJECTED_UTIL_GATE,
            "projected_adjusted_max": PROJECTED_ADJUSTED_GATE,
        },
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("e018-diagnostic.json"))
    args = parser.parse_args()
    result = run(args.upstream)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("E018_SUMMARY=" + json.dumps({k: v for k, v in result.items() if k != "records"}, sort_keys=True))
    print(f"E018_DECISION={result['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
