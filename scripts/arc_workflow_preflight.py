#!/usr/bin/env python3
"""Offline preflight for workflow/fixture contracts before an Actions arm push.

The guard is intentionally narrow. It checks only the three infrastructure contracts
that failed in R257-R259:
1. ancestry guards require actions/checkout with fetch-depth: 0;
2. runtime manifest filenames used by the workflow must match the fixture generator;
3. inline assertions against that runtime manifest may reference only schema keys
   emitted by the fixture generator.

It uses only the Python standard library and does not execute the fixture, estimator,
workflow, network access, or competition data.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import sys


class PreflightError(ValueError):
    pass


def _checkout_steps(workflow: str) -> list[list[str]]:
    lines = workflow.splitlines()
    steps: list[list[str]] = []
    for i, line in enumerate(lines):
        if not re.search(r"\buses:\s*actions/checkout@v\d+\s*$", line):
            continue
        indent = len(line) - len(line.lstrip())
        block = [line]
        for following in lines[i + 1 :]:
            following_indent = len(following) - len(following.lstrip())
            if following.lstrip().startswith("- ") and following_indent == indent:
                break
            block.append(following)
        steps.append(block)
    return steps


def require_full_history_for_ancestry(workflow: str) -> None:
    if "git merge-base --is-ancestor" not in workflow:
        return
    steps = _checkout_steps(workflow)
    if not steps:
        raise PreflightError("ancestry guard present but actions/checkout step is missing")
    if not any(
        re.search(r"^\s*fetch-depth:\s*0\s*(?:#.*)?$", line)
        for step in steps
        for line in step
    ):
        raise PreflightError(
            "ancestry guard requires actions/checkout with fetch-depth: 0"
        )


def generator_contract(source: str, filename: str = "<fixture-generator>") -> tuple[str, set[str]]:
    tree = ast.parse(source, filename=filename)
    emitted: list[str] = []
    schema_keys: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    schema_keys.add(key.value)
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "write_text"):
            continue
        target = func.value
        if not (isinstance(target, ast.BinOp) and isinstance(target.op, ast.Div)):
            continue
        right = target.right
        if isinstance(right, ast.Constant) and isinstance(right.value, str):
            value = right.value
            if "RUNTIME" in value and "MANIFEST" in value and value.endswith(".json"):
                emitted.append(value)
    if len(emitted) != 1:
        raise PreflightError(
            f"fixture generator must emit exactly one runtime manifest, found {emitted!r}"
        )
    return emitted[0], schema_keys


_RUNTIME_MANIFEST_RE = re.compile(
    r"\bR[A-Z0-9_]*RUNTIME[A-Z0-9_]*MANIFEST\.json\b"
)


def workflow_runtime_manifest_names(workflow: str) -> set[str]:
    return set(_RUNTIME_MANIFEST_RE.findall(workflow))


def _step_blocks_with_runtime_manifest(workflow: str) -> list[str]:
    lines = workflow.splitlines()
    blocks: list[str] = []
    starts = [
        i
        for i, line in enumerate(lines)
        if re.match(r"^\s*-\s+name:\s+", line)
    ]
    starts.append(len(lines))
    for a, b in zip(starts, starts[1:]):
        block = "\n".join(lines[a:b])
        if _RUNTIME_MANIFEST_RE.search(block):
            blocks.append(block)
    return blocks


def asserted_manifest_keys(workflow: str) -> set[str]:
    keys: set[str] = set()
    for block in _step_blocks_with_runtime_manifest(workflow):
        vars_ = set(
            re.findall(
                r"(?m)^\s*([A-Za-z_]\w*)\s*=\s*json\.loads\s*\(",
                block,
            )
        )
        for var in vars_:
            chain_re = re.compile(
                rf"\b{re.escape(var)}(?:\[(?:\"[^\"]+\"|'[^']+')\])+"
            )
            for chain in chain_re.findall(block):
                keys.update(
                    match.group(2)
                    for match in re.finditer(r"\[([\"'])([^\"']+)\1\]", chain)
                )
    return keys


def check_contract(workflow: str, generator: str) -> dict:
    require_full_history_for_ancestry(workflow)
    emitted, schema_keys = generator_contract(generator)
    used_names = workflow_runtime_manifest_names(workflow)
    if not used_names:
        raise PreflightError("workflow never references a runtime fixture manifest")
    wrong_names = sorted(name for name in used_names if name != emitted)
    if wrong_names:
        raise PreflightError(
            f"workflow runtime manifest name(s) {wrong_names!r} != generator emitted {emitted!r}"
        )
    asserted = asserted_manifest_keys(workflow)
    missing = sorted(asserted - schema_keys)
    if missing:
        raise PreflightError(
            f"workflow asserts runtime-manifest schema key(s) not emitted by generator: {missing!r}"
        )
    return {
        "status": "PASS",
        "full_history_required": "git merge-base --is-ancestor" in workflow,
        "runtime_manifest": emitted,
        "workflow_runtime_manifest_names": sorted(used_names),
        "asserted_manifest_keys": sorted(asserted),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", type=Path, required=True)
    ap.add_argument("--fixture-generator", type=Path, required=True)
    args = ap.parse_args()
    try:
        result = check_contract(
            args.workflow.read_text(encoding="utf-8"),
            args.fixture_generator.read_text(encoding="utf-8"),
        )
    except Exception as exc:
        print(f"WORKFLOW_PREFLIGHT_FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
