#!/usr/bin/env python3
"""Offline preflight for workflow/fixture contracts before an Actions arm push.

The guard is intentionally narrow. It checks only the infrastructure contracts that
failed in R257-R259 and fails closed when it cannot statically prove them:
1. every job with an ancestry guard must use full-history checkout in that same job;
2. runtime manifest filenames used by the workflow must match the fixture generator;
3. workflow key references must exist in the object actually serialized to that
   runtime manifest, not merely somewhere else in the generator source.

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
from typing import TypeAlias


class PreflightError(ValueError):
    pass


SchemaPath: TypeAlias = tuple[str, ...]
Schema: TypeAlias = frozenset[SchemaPath]
_SCALAR = object()


class _SequenceValue:
    def __init__(self, items: list[object]):
        self.items = items


class _GeneratorResolver:
    """Resolve only the small, explicit dict dataflow needed by fixture manifests."""

    def __init__(self, tree: ast.Module, filename: str):
        self.filename = filename
        self.functions = {
            node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
        }

    def _assign(self, target: ast.expr, value: object, env: dict[str, object]) -> None:
        if isinstance(target, ast.Name):
            env[target.id] = value
            return
        if isinstance(target, (ast.Tuple, ast.List)):
            if not isinstance(value, _SequenceValue) or len(target.elts) != len(value.items):
                raise PreflightError("cannot statically resolve tuple assignment feeding runtime manifest")
            for child, item in zip(target.elts, value.items):
                self._assign(child, item, env)
            return
        raise PreflightError("unsupported assignment target feeding runtime manifest")

    def _local_call(self, call: ast.Call, stack: tuple[str, ...]) -> object:
        if not isinstance(call.func, ast.Name) or call.func.id not in self.functions:
            return _SCALAR
        fn = self.functions[call.func.id]
        if call.args or call.keywords or fn.args.args or fn.args.kwonlyargs or fn.args.vararg or fn.args.kwarg:
            raise PreflightError(
                f"cannot statically resolve helper call {call.func.id}() feeding runtime manifest"
            )
        if call.func.id in stack:
            raise PreflightError("recursive manifest dataflow is unsupported")
        return self._function_return(fn, stack + (call.func.id,))

    def _value(self, expr: ast.expr, env: dict[str, object], stack: tuple[str, ...]) -> object:
        if isinstance(expr, ast.Dict):
            paths: set[SchemaPath] = set()
            for key, value_expr in zip(expr.keys, expr.values):
                if key is None:
                    expanded = self._value(value_expr, env, stack)
                    if not isinstance(expanded, frozenset):
                        raise PreflightError("cannot statically resolve ** expansion in runtime manifest")
                    paths.update(expanded)
                    continue
                if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                    raise PreflightError("runtime manifest dict contains non-literal key")
                key_name = key.value
                paths.add((key_name,))
                nested = self._value(value_expr, env, stack)
                if isinstance(nested, frozenset):
                    paths.update((key_name, *child) for child in nested)
            return frozenset(paths)
        if isinstance(expr, ast.Name):
            return env.get(expr.id, _SCALAR)
        if isinstance(expr, (ast.Tuple, ast.List)):
            return _SequenceValue([self._value(item, env, stack) for item in expr.elts])
        if isinstance(expr, ast.Call):
            return self._local_call(expr, stack)
        return _SCALAR

    @staticmethod
    def _tracked_dict_name(expr: ast.expr, env: dict[str, object]) -> str | None:
        if isinstance(expr, ast.Name) and isinstance(env.get(expr.id), frozenset):
            return expr.id
        return None

    def _apply_manifest_call(
        self,
        call: ast.Call,
        env: dict[str, object],
        stack: tuple[str, ...],
    ) -> None:
        if isinstance(call.func, ast.Attribute):
            name = self._tracked_dict_name(call.func.value, env)
            if name is None:
                return
            if call.func.attr != "update":
                raise PreflightError(
                    f"unsupported manifest mutation {call.func.attr!r} on {name!r}"
                )
            current = env[name]
            if len(call.args) != 1 or call.keywords:
                raise PreflightError(
                    "runtime manifest update must use one statically resolvable dict"
                )
            added = self._value(call.args[0], env, stack)
            if not isinstance(added, frozenset):
                raise PreflightError("cannot statically resolve runtime manifest update")
            env[name] = frozenset(set(current) | set(added))
            return

        tracked_args = [
            arg.id
            for arg in call.args
            if isinstance(arg, ast.Name) and isinstance(env.get(arg.id), frozenset)
        ]
        if tracked_args:
            if isinstance(call.func, ast.Name):
                callee = call.func.id
            else:
                callee = ast.unparse(call.func)
            raise PreflightError(
                f"unsupported manifest mutation via {callee!r} for {tracked_args!r}"
            )

    def _process(self, statements: list[ast.stmt], stack: tuple[str, ...]) -> tuple[dict[str, object], object | None]:
        env: dict[str, object] = {}
        for stmt in statements:
            if isinstance(stmt, ast.Assign):
                value = self._value(stmt.value, env, stack)
                for target in stmt.targets:
                    self._assign(target, value, env)
            elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
                self._assign(stmt.target, self._value(stmt.value, env, stack), env)
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                self._apply_manifest_call(stmt.value, env, stack)
            elif isinstance(stmt, ast.Return):
                if stmt.value is None:
                    return env, _SCALAR
                return env, self._value(stmt.value, env, stack)
        return env, None

    def _function_return(self, fn: ast.FunctionDef, stack: tuple[str, ...]) -> object:
        _, value = self._process(fn.body, stack)
        if value is None:
            raise PreflightError(f"cannot statically resolve return value of {fn.name}()")
        return value

    @staticmethod
    def _runtime_write_call(stmt: ast.stmt) -> tuple[str, ast.Call] | None:
        if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
            return None
        call = stmt.value
        if not (isinstance(call.func, ast.Attribute) and call.func.attr == "write_text"):
            return None
        target = call.func.value
        if not (isinstance(target, ast.BinOp) and isinstance(target.op, ast.Div)):
            return None
        right = target.right
        if not (isinstance(right, ast.Constant) and isinstance(right.value, str)):
            return None
        name = right.value
        if "RUNTIME" not in name or "MANIFEST" not in name or not name.endswith(".json"):
            return None
        return name, call

    @staticmethod
    def _json_payload(write_call: ast.Call) -> ast.expr:
        if not write_call.args:
            raise PreflightError("runtime manifest write_text() has no payload")
        dumps_calls = [
            node
            for node in ast.walk(write_call.args[0])
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "json"
            and node.func.attr == "dumps"
        ]
        if len(dumps_calls) != 1 or not dumps_calls[0].args:
            raise PreflightError("runtime manifest payload is not one statically traceable json.dumps(...) call")
        return dumps_calls[0].args[0]

    def contract(self) -> tuple[str, Schema]:
        writes: list[tuple[ast.FunctionDef, int, str, ast.Call]] = []
        for fn in self.functions.values():
            for index, stmt in enumerate(fn.body):
                found = self._runtime_write_call(stmt)
                if found is not None:
                    name, call = found
                    writes.append((fn, index, name, call))
        if len(writes) != 1:
            names = [name for _, _, name, _ in writes]
            raise PreflightError(
                f"fixture generator must have exactly one top-level runtime manifest write, found {names!r}"
            )
        fn, index, emitted, write_call = writes[0]
        env, early_return = self._process(fn.body[:index], (fn.name,))
        if early_return is not None:
            raise PreflightError("runtime manifest write occurs after an earlier top-level return")
        payload = self._json_payload(write_call)
        value = self._value(payload, env, (fn.name,))
        if not isinstance(value, frozenset):
            raise PreflightError("cannot statically resolve the object serialized to runtime manifest")
        if not value:
            raise PreflightError("resolved runtime manifest schema is empty")
        return emitted, value


def generator_contract(source: str, filename: str = "<fixture-generator>") -> tuple[str, Schema]:
    tree = ast.parse(source, filename=filename)
    return _GeneratorResolver(tree, filename).contract()


_RUNTIME_MANIFEST_RE = re.compile(r"\bR[A-Z0-9_]*RUNTIME[A-Z0-9_]*MANIFEST\.json\b")


def workflow_runtime_manifest_names(workflow: str) -> set[str]:
    return set(_RUNTIME_MANIFEST_RE.findall(workflow))


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _job_blocks(workflow: str) -> list[tuple[str, str]]:
    lines = workflow.splitlines()
    jobs_indexes = [
        i for i, line in enumerate(lines)
        if re.match(r"^\s*jobs:\s*(?:#.*)?$", line)
    ]
    if len(jobs_indexes) != 1:
        raise PreflightError("cannot statically identify one jobs: mapping")
    jobs_index = jobs_indexes[0]
    jobs_indent = _indent(lines[jobs_index])
    job_indent = None
    for line in lines[jobs_index + 1:]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = _indent(line)
        if indent <= jobs_indent:
            break
        if re.match(r"^\s*[A-Za-z0-9_.-]+:\s*(?:#.*)?$", line):
            job_indent = indent
            break
    if job_indent is None:
        raise PreflightError("cannot statically identify workflow jobs")
    starts: list[tuple[int, str]] = []
    for i in range(jobs_index + 1, len(lines)):
        line = lines[i]
        stripped = line.strip()
        if stripped and _indent(line) <= jobs_indent:
            break
        match = re.match(r"^\s*([A-Za-z0-9_.-]+):\s*(?:#.*)?$", line)
        if match and _indent(line) == job_indent:
            starts.append((i, match.group(1)))
    if not starts:
        raise PreflightError("cannot statically identify workflow jobs")
    end = len(lines)
    for i in range(starts[-1][0] + 1, len(lines)):
        if lines[i].strip() and _indent(lines[i]) <= jobs_indent:
            end = i
            break
    blocks: list[tuple[str, str]] = []
    for pos, (start, name) in enumerate(starts):
        stop = starts[pos + 1][0] if pos + 1 < len(starts) else end
        blocks.append((name, "\n".join(lines[start:stop])))
    return blocks


def _checkout_steps(job_block: str) -> list[tuple[int, list[str]]]:
    lines = job_block.splitlines()
    steps: list[tuple[int, list[str]]] = []
    for i, line in enumerate(lines):
        if not re.search(r"\buses:\s*actions/checkout@v\d+\s*$", line):
            continue
        indent = _indent(line)
        block = [line]
        for following in lines[i + 1:]:
            if following.lstrip().startswith("- ") and _indent(following) == indent:
                break
            block.append(following)
        steps.append((i, block))
    return steps


def _checkout_has_full_history(step: list[str]) -> bool:
    uses_indent = _indent(step[0])
    with_index = None
    with_indent = None
    for i, line in enumerate(step[1:], start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = _indent(line)
        if indent <= uses_indent:
            break
        if re.match(r"^\s*with:\s*(?:#.*)?$", line):
            with_index = i
            with_indent = indent
            break
    if with_index is None or with_indent is None:
        return False
    for line in step[with_index + 1:]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = _indent(line)
        if indent <= with_indent:
            break
        if re.match(r"^\s*fetch-depth:\s*0\s*(?:#.*)?$", line):
            return True
    return False


def require_full_history_for_ancestry(workflow: str) -> None:
    total_guards = workflow.count("git merge-base --is-ancestor")
    if total_guards == 0:
        return
    jobs = _job_blocks(workflow)
    mapped_guards = 0
    for job_name, block in jobs:
        guard_count = block.count("git merge-base --is-ancestor")
        mapped_guards += guard_count
        if guard_count == 0:
            continue
        checkouts = _checkout_steps(block)
        if not checkouts:
            raise PreflightError(
                f"job {job_name!r} has ancestry guard but no actions/checkout step"
            )
        job_lines = block.splitlines()
        guard_indexes = [
            i for i, line in enumerate(job_lines)
            if "git merge-base --is-ancestor" in line
        ]
        for guard_index in guard_indexes:
            prior = [(index, step) for index, step in checkouts if index < guard_index]
            if not prior:
                raise PreflightError(
                    f"job {job_name!r} ancestry guard has no preceding actions/checkout in the same job"
                )
            _, active_checkout = prior[-1]
            if not _checkout_has_full_history(active_checkout):
                raise PreflightError(
                    f"job {job_name!r} ancestry guard requires a preceding actions/checkout with fetch-depth: 0 under its with: block in the same job"
                )
    if mapped_guards != total_guards:
        raise PreflightError("ancestry guard could not be mapped unambiguously to a workflow job")


def _step_blocks(job_name: str, job_block: str) -> list[str]:
    lines = job_block.splitlines()
    step_headers = [
        i for i, line in enumerate(lines)
        if re.match(r"^\s*steps:\s*(?:#.*)?$", line)
    ]
    if len(step_headers) != 1:
        raise PreflightError(f"cannot statically identify one steps: list in job {job_name!r}")
    steps_index = step_headers[0]
    steps_indent = _indent(lines[steps_index])
    candidate_indents = [
        _indent(line)
        for line in lines[steps_index + 1:]
        if line.strip() and _indent(line) > steps_indent and line.lstrip().startswith("- ")
    ]
    if not candidate_indents:
        raise PreflightError(f"cannot statically identify steps in job {job_name!r}")
    item_indent = min(candidate_indents)
    starts = [
        i for i in range(steps_index + 1, len(lines))
        if lines[i].strip()
        and _indent(lines[i]) == item_indent
        and lines[i].lstrip().startswith("- ")
    ]
    blocks: list[str] = []
    for pos, start in enumerate(starts):
        stop = starts[pos + 1] if pos + 1 < len(starts) else len(lines)
        blocks.append("\n".join(lines[start:stop]))
    return blocks


def _step_blocks_with_runtime_manifest(workflow: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for job_name, job_block in _job_blocks(workflow):
        for step in _step_blocks(job_name, job_block):
            if _RUNTIME_MANIFEST_RE.search(step):
                blocks.append((job_name, step))
    return blocks


def _manifest_data_vars(block: str) -> set[str]:
    path_vars: set[str] = set()
    for line in block.splitlines():
        if not _RUNTIME_MANIFEST_RE.search(line):
            continue
        match = re.match(r"^\s*([A-Za-z_]\w*)\s*=", line)
        if match:
            path_vars.add(match.group(1))

    data_vars: set[str] = set()
    loads = list(re.finditer(
        r"(?m)^\s*([A-Za-z_]\w*)\s*=\s*json\.loads\s*\(([^\n]+)\)\s*$",
        block,
    ))
    manifest_load_seen = False
    for match in loads:
        target, argument = match.group(1), match.group(2).strip()
        direct = re.fullmatch(
            r"pathlib\.Path\([^\n]*R[A-Z0-9_]*RUNTIME[A-Z0-9_]*MANIFEST\.json[^\n]*\)\.read_text\(\s*\)",
            argument,
        )
        via_var = re.fullmatch(r"([A-Za-z_]\w*)\.read_text\(\s*\)", argument)
        if direct or (via_var and via_var.group(1) in path_vars):
            data_vars.add(target)
            manifest_load_seen = True
        elif any(re.search(rf"\b{re.escape(path_var)}\b", argument) for path_var in path_vars):
            raise PreflightError(
                "json.loads must read the exact runtime manifest path via <manifest_path>.read_text()"
            )
    if loads and not manifest_load_seen and path_vars:
        raise PreflightError(
            "json.loads must read the exact runtime manifest path via <manifest_path>.read_text()"
        )
    return data_vars


def asserted_manifest_paths(workflow: str) -> set[SchemaPath]:
    blocks = _step_blocks_with_runtime_manifest(workflow)
    if not blocks:
        raise PreflightError("workflow never references a runtime fixture manifest in a step")
    paths: set[SchemaPath] = set()
    for job_name, block in blocks:
        vars_ = _manifest_data_vars(block)
        if not vars_:
            raise PreflightError(
                f"job {job_name!r} runtime-manifest step has no statically traceable json.loads binding; cannot verify key references"
            )
        block_paths: set[SchemaPath] = set()
        for var in vars_:
            unsupported = re.search(
                rf"\b{re.escape(var)}(?:\[(?:\"[^\"]+\"|'[^']+')\])*\.([A-Za-z_]\w*)\s*\(",
                block,
            )
            if unsupported:
                raise PreflightError(
                    f"unsupported manifest access {unsupported.group(1)!r} on {var!r}"
                )
            chain_re = re.compile(
                rf"\b{re.escape(var)}(?:\[(?:\"[^\"]+\"|'[^']+')\])+"
            )
            for chain in chain_re.findall(block):
                keys = tuple(
                    match.group(2)
                    for match in re.finditer(r"\[([\"'])([^\"']+)\1\]", chain)
                )
                if keys:
                    block_paths.add(keys)
        if not block_paths:
            raise PreflightError(
                f"job {job_name!r} reads runtime manifest but no statically verifiable key references were extracted"
            )
        paths.update(block_paths)
    return paths


def _display_path(path: SchemaPath) -> str:
    return ".".join(path)


def check_contract(workflow: str, generator: str) -> dict:
    require_full_history_for_ancestry(workflow)
    emitted, schema_paths = generator_contract(generator)
    used_names = workflow_runtime_manifest_names(workflow)
    if not used_names:
        raise PreflightError("workflow never references a runtime fixture manifest")
    wrong_names = sorted(name for name in used_names if name != emitted)
    if wrong_names:
        raise PreflightError(
            f"workflow runtime manifest name(s) {wrong_names!r} != generator emitted {emitted!r}"
        )
    asserted = asserted_manifest_paths(workflow)
    missing = sorted(asserted - schema_paths)
    if missing:
        raise PreflightError(
            "workflow asserts runtime-manifest schema path(s) not emitted by serialized object: "
            + repr([_display_path(path) for path in missing])
        )
    return {
        "status": "PASS",
        "full_history_required": "git merge-base --is-ancestor" in workflow,
        "runtime_manifest": emitted,
        "workflow_runtime_manifest_names": sorted(used_names),
        "asserted_manifest_keys": sorted(_display_path(path) for path in asserted),
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
