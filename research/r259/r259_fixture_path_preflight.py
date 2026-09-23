#!/usr/bin/env python3
"""R259 static fixture-manifest path preflight.

Reads the immutable R254 fixture generator and proves that the workflow's expected
manifest filename matches the literal filename written by the generator.
No fixture construction, estimator import, public data, or science is performed.
"""
from __future__ import annotations

import ast
import pathlib
import sys

GENERATOR = pathlib.Path("research/r254/r254_fixture.py")
EXPECTED = "R254_FIXTURE_RUNTIME_MANIFEST.json"


def emitted_manifest_names(source: str) -> list[str]:
    tree = ast.parse(source, filename=str(GENERATOR))
    names: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "write_text"):
            continue
        target = func.value
        if not isinstance(target, ast.BinOp) or not isinstance(target.op, ast.Div):
            continue
        right = target.right
        if isinstance(right, ast.Constant) and isinstance(right.value, str):
            if "MANIFEST" in right.value and right.value.endswith(".json"):
                names.append(right.value)
    return names


def main() -> int:
    source = GENERATOR.read_text()
    names = emitted_manifest_names(source)
    if names != [EXPECTED]:
        print(
            f"R259_FIXTURE_PATH_PREFLIGHT_FAIL expected={[EXPECTED]!r} emitted={names!r}",
            file=sys.stderr,
        )
        return 2
    print(f"R259_FIXTURE_PATH_PREFLIGHT_PASS expected={EXPECTED} emitted={names[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
