#!/usr/bin/env python3
from __future__ import annotations

import gc
import hashlib
import json
import math
from pathlib import Path

import flopscope.numpy as fnp
import numpy as np
from datasets import load_dataset
from whestbench.domain import MLP

from methods.e173_starter_ago import AGOEstimator, ParentEstimator


DATASET = "aicrowd/arc-whestbench-public-2026"
REVISION = "v2-phase2"
SPLIT = "mini"
N_MLPS = 5
BUDGET = 2**41
ROOT = Path("e173_vectors")
MANIFEST_PATH = Path("e173_vector_manifest.json")

PAYLOAD_NAMES = (
    "target_all_layer_means.npy",
    "parent_prediction.npy",
    "ago_prediction.npy",
    "parent_final_error.npy",
    "ago_final_error.npy",
    "parent_final_squared_error.npy",
    "ago_final_squared_error.npy",
)


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _raw_sha(array: np.ndarray) -> str:
    return hashlib.sha256(
        np.ascontiguousarray(array).tobytes()
    ).hexdigest()


def _save(root: Path, name: str, array: np.ndarray) -> dict:
    arr = np.ascontiguousarray(array)
    path = root / name
    np.save(path, arr, allow_pickle=False)
    loaded = np.load(path, allow_pickle=False)
    return {
        "path": str(path),
        "dtype": str(arr.dtype),
        "shape": list(arr.shape),
        "nbytes": int(arr.nbytes),
        "file_sha256": _file_sha(path),
        "raw_array_sha256": _raw_sha(arr),
        "reload_raw_array_sha256": _raw_sha(loaded),
        "reload_equal": bool(np.array_equal(arr, loaded)),
    }


def _mse_se(error: np.ndarray) -> tuple[float, float]:
    sq = np.asarray(error, dtype=np.float64) ** 2
    mse = float(np.mean(sq))
    se = float(np.std(sq, ddof=1) / math.sqrt(sq.size))
    return mse, se


def _make_mlp(row: dict) -> MLP:
    weights_np = np.asarray(row["weights"], dtype=np.float32)
    if weights_np.shape != (16, 1024, 1024):
        raise ValueError(f"unexpected official Mini shape {weights_np.shape}")
    weights = [
        fnp.asarray(weights_np[i], dtype=fnp.float32)
        for i in range(weights_np.shape[0])
    ]
    return MLP(
        width=1024,
        depth=16,
        weights=weights,
        seed=int(row.get("mlp_seed", 0)),
        name=str(row["mlp_name"]),
    )


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)

    ds = load_dataset(
        DATASET,
        revision=REVISION,
        split=SPLIT,
        streaming=True,
    )
    ds = ds.with_format("numpy")

    parent_estimator = ParentEstimator()
    ago_estimator = AGOEstimator()

    records: list[dict] = []

    for index, row in enumerate(ds):
        if index >= N_MLPS:
            break

        mlp = _make_mlp(row)
        target = np.asarray(
            row["all_layer_means"],
            dtype=np.float32,
        )
        if target.shape != (16, 1024):
            raise ValueError(
                f"unexpected target shape for {mlp.name}: {target.shape}"
            )

        parent_1 = np.asarray(
            parent_estimator.predict(mlp, BUDGET),
            dtype=np.float32,
        )
        parent_2 = np.asarray(
            parent_estimator.predict(mlp, BUDGET),
            dtype=np.float32,
        )
        ago_1 = np.asarray(
            ago_estimator.predict(mlp, BUDGET),
            dtype=np.float32,
        )
        ago_2 = np.asarray(
            ago_estimator.predict(mlp, BUDGET),
            dtype=np.float32,
        )

        parent_replay = bool(np.array_equal(parent_1, parent_2))
        ago_replay = bool(np.array_equal(ago_1, ago_2))
        if not parent_replay or not ago_replay:
            raise RuntimeError(
                f"replay mismatch for {mlp.name}: "
                f"parent={parent_replay} ago={ago_replay}"
            )

        if parent_1.shape != target.shape or ago_1.shape != target.shape:
            raise ValueError(
                f"prediction shape mismatch {mlp.name}: "
                f"target={target.shape} parent={parent_1.shape} ago={ago_1.shape}"
            )

        parent_error = np.asarray(
            parent_1[-1], dtype=np.float64
        ) - np.asarray(target[-1], dtype=np.float64)
        ago_error = np.asarray(
            ago_1[-1], dtype=np.float64
        ) - np.asarray(target[-1], dtype=np.float64)
        parent_sq = parent_error * parent_error
        ago_sq = ago_error * ago_error

        parent_mse, parent_se = _mse_se(parent_error)
        ago_mse, ago_se = _mse_se(ago_error)

        layer_parent_mse = np.mean(
            (
                np.asarray(parent_1, dtype=np.float64)
                - np.asarray(target, dtype=np.float64)
            )
            ** 2,
            axis=1,
        )
        layer_ago_mse = np.mean(
            (
                np.asarray(ago_1, dtype=np.float64)
                - np.asarray(target, dtype=np.float64)
            )
            ** 2,
            axis=1,
        )

        safe_name = (
            f"{index:02d}_"
            + "".join(
                c if c.isalnum() or c in "-_" else "_"
                for c in mlp.name
            )
        )
        mlp_root = ROOT / safe_name
        mlp_root.mkdir(parents=True, exist_ok=True)

        arrays = {
            "target_all_layer_means.npy": target,
            "parent_prediction.npy": parent_1,
            "ago_prediction.npy": ago_1,
            "parent_final_error.npy": parent_error,
            "ago_final_error.npy": ago_error,
            "parent_final_squared_error.npy": parent_sq,
            "ago_final_squared_error.npy": ago_sq,
        }
        payloads = [
            _save(mlp_root, name, array)
            for name, array in arrays.items()
        ]

        observed = {Path(p["path"]).name for p in payloads}
        if observed != set(PAYLOAD_NAMES):
            raise RuntimeError(
                f"payload set mismatch for {mlp.name}: {observed}"
            )

        records.append(
            {
                "mlp_index": index,
                "mlp_id": int(row.get("mlp_id", index)),
                "mlp_name": mlp.name,
                "input_mlp_seed": int(row.get("mlp_seed", 0)),
                "parent_replay_bitwise_exact": parent_replay,
                "ago_replay_bitwise_exact": ago_replay,
                "parent_prediction_raw_sha256": _raw_sha(parent_1),
                "ago_prediction_raw_sha256": _raw_sha(ago_1),
                "target_raw_sha256": _raw_sha(target),
                "parent_final_mse": parent_mse,
                "ago_final_mse": ago_mse,
                "parent_final_mse_coordinate_se": parent_se,
                "ago_final_mse_coordinate_se": ago_se,
                "final_mse_ratio_ago_over_parent": (
                    ago_mse / parent_mse
                    if parent_mse > 0.0
                    else math.inf
                ),
                "parent_per_layer_mse": layer_parent_mse.tolist(),
                "ago_per_layer_mse": layer_ago_mse.tolist(),
                "payloads": payloads,
            }
        )

        del (
            mlp,
            target,
            parent_1,
            parent_2,
            ago_1,
            ago_2,
            parent_error,
            ago_error,
            parent_sq,
            ago_sq,
            layer_parent_mse,
            layer_ago_mse,
        )
        gc.collect()

    if len(records) != N_MLPS:
        raise RuntimeError(
            f"expected {N_MLPS} Mini rows, captured {len(records)}"
        )

    manifest = {
        "schema": "arc.whitebox.e173.vector_manifest.v1",
        "dataset": DATASET,
        "revision": REVISION,
        "split": SPLIT,
        "n_mlps": N_MLPS,
        "payload_names": list(PAYLOAD_NAMES),
        "records": records,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = {
        "manifest_path": str(MANIFEST_PATH),
        "manifest_sha256": _file_sha(MANIFEST_PATH),
        "mlp_names": [r["mlp_name"] for r in records],
        "parent_replay_all": all(
            r["parent_replay_bitwise_exact"] for r in records
        ),
        "ago_replay_all": all(
            r["ago_replay_bitwise_exact"] for r in records
        ),
        "payload_file_count": sum(
            len(r["payloads"]) for r in records
        ),
    }
    print("E173_CAPTURE=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
