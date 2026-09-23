#!/usr/bin/env python3
"""R260 static/runtime fixture replay-schema preflight.

Validates the immutable R254 fixture generator schema and a supplied runtime manifest.
No estimator, candidate, public data, benchmark, or science is executed.
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys

GENERATOR = pathlib.Path("research/r254/r254_fixture.py")
DEFAULT_MANIFEST = pathlib.Path("research/r259/evidence/R254_FIXTURE_RUNTIME_MANIFEST.json")
EXPECTED_FILENAME = "R254_FIXTURE_RUNTIME_MANIFEST.json"
EXPECTED_WEIGHTS = "199e5fd8c669ec927717a12f0a3bbcee83e37db8db6e61e8c50eb791f457b3f0"
EXPECTED_TRUTH = "58354221cedab39e900d78040a8383df45672425389f3865b731eea7b0063f1d"
EXPECTED_LAYERS = 16
FORBIDDEN_KEY = "all_layer_hashes_equal"


def source_contract(source: str) -> tuple[str, set[str], bool]:
    tree = ast.parse(source, filename=str(GENERATOR))
    emitted: list[str] = []
    string_keys: set[str] = set()
    has_replay_equal_true = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            string_keys.add(node.value)
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "write_text":
                target = func.value
                if isinstance(target, ast.BinOp) and isinstance(target.op, ast.Div):
                    right = target.right
                    if isinstance(right, ast.Constant) and isinstance(right.value, str):
                        if "MANIFEST" in right.value and right.value.endswith(".json"):
                            emitted.append(right.value)
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if (
                    isinstance(key, ast.Constant)
                    and key.value == "replay_equal"
                    and isinstance(value, ast.Constant)
                    and value.value is True
                ):
                    has_replay_equal_true = True
    if emitted != [EXPECTED_FILENAME]:
        raise AssertionError(f"generator emitted manifest mismatch: {emitted!r}")
    required = {"layer_sha256", "weights_concat_sha256", "truth_sha256", "independent_replay", "replay_equal"}
    if not required.issubset(string_keys):
        raise AssertionError(f"generator missing required schema literals: {sorted(required-string_keys)!r}")
    if FORBIDDEN_KEY in string_keys:
        raise AssertionError(f"forbidden stale schema key present in generator: {FORBIDDEN_KEY}")
    if not has_replay_equal_true:
        raise AssertionError("generator does not freeze replay_equal=True")
    return emitted[0], string_keys, has_replay_equal_true


def validate_manifest(path: pathlib.Path) -> dict:
    d = json.loads(path.read_text())
    required_top = {
        "replay_equal",
        "layer_sha256",
        "weights_concat_sha256",
        "truth_sha256",
        "independent_replay",
    }
    if not required_top.issubset(d):
        raise AssertionError(f"runtime manifest missing top-level keys: {sorted(required_top-set(d))!r}")
    if FORBIDDEN_KEY in d:
        raise AssertionError(f"forbidden stale top-level key present: {FORBIDDEN_KEY}")
    if d["replay_equal"] is not True:
        raise AssertionError("replay_equal is not true")
    top_layers = d["layer_sha256"]
    nested = d["independent_replay"]
    if not isinstance(nested, dict):
        raise AssertionError("independent_replay is not an object")
    required_nested = {"layer_sha256", "weights_concat_sha256", "truth_sha256"}
    if set(nested) != required_nested:
        raise AssertionError(f"independent_replay keys mismatch: {sorted(nested)!r}")
    if FORBIDDEN_KEY in nested:
        raise AssertionError(f"forbidden stale nested key present: {FORBIDDEN_KEY}")
    nested_layers = nested["layer_sha256"]
    if not isinstance(top_layers, list) or len(top_layers) != EXPECTED_LAYERS:
        raise AssertionError(f"top-level layer_sha256 length != {EXPECTED_LAYERS}")
    if not isinstance(nested_layers, list) or len(nested_layers) != EXPECTED_LAYERS:
        raise AssertionError(f"nested layer_sha256 length != {EXPECTED_LAYERS}")
    if top_layers != nested_layers:
        raise AssertionError("top-level and nested layer hashes differ")
    if d["weights_concat_sha256"] != EXPECTED_WEIGHTS:
        raise AssertionError("top-level weights hash differs from frozen value")
    if nested["weights_concat_sha256"] != EXPECTED_WEIGHTS:
        raise AssertionError("nested weights hash differs from frozen value")
    if d["truth_sha256"] != EXPECTED_TRUTH:
        raise AssertionError("top-level truth hash differs from frozen value")
    if nested["truth_sha256"] != EXPECTED_TRUTH:
        raise AssertionError("nested truth hash differs from frozen value")
    return {
        "manifest": str(path),
        "filename": path.name,
        "replay_equal": True,
        "layer_count": len(top_layers),
        "layer_hash_arrays_equal": True,
        "weights_hash": EXPECTED_WEIGHTS,
        "truth_hash": EXPECTED_TRUTH,
        "forbidden_key_absent": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=pathlib.Path, default=DEFAULT_MANIFEST)
    args = ap.parse_args()
    emitted, _, _ = source_contract(GENERATOR.read_text())
    if args.manifest.name != emitted:
        raise AssertionError(f"manifest filename {args.manifest.name!r} != generator emitted {emitted!r}")
    result = validate_manifest(args.manifest)
    print(json.dumps({"status":"R260_FIXTURE_SCHEMA_PREFLIGHT_PASS", **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"R260_FIXTURE_SCHEMA_PREFLIGHT_FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
