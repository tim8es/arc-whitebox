#!/usr/bin/env python3
"""Static provenance/rules audit for E136 public 504aldo reproduction."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "methods" / "public_504aldo"
OUT = ROOT / "e136_artifacts"
OUT.mkdir(exist_ok=True)

EXPECTED = {
    "estimator_v25.py": "195373a110215256b759d7c172ba8c923c62e5cc",
    "estimator_v29.py": "17df1a073a24f96c4705b04bcf61ef60fa06dd0c",
    "LICENSE": "2c843327a87b547245b566f02391295ba71ad26a",
}
UPSTREAM_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return sorted(out)


files = {}
for name, expected_blob in EXPECTED.items():
    data = (BASE / name).read_bytes()
    blob = git_blob_sha1(data)
    files[name] = {
        "bytes": len(data),
        "git_blob_sha1": blob,
        "expected_upstream_git_blob_sha1": expected_blob,
        "blob_match": blob == expected_blob,
        "sha256": hashlib.sha256(data).hexdigest(),
    }

v25 = (BASE / "estimator_v25.py").read_text(encoding="utf-8")
v29 = (BASE / "estimator_v29.py").read_text(encoding="utf-8")
license_text = (BASE / "LICENSE").read_text(encoding="utf-8")

forbidden_roots = {"numpy", "scipy", "torch", "jax", "tensorflow"}
import_audit = {}
for name in ("estimator_v25.py", "estimator_v29.py"):
    imps = imports(BASE / name)
    bad = sorted({x.split(".", 1)[0] for x in imps} & forbidden_roots)
    import_audit[name] = {"imports": imps, "forbidden_direct_import_roots": bad}

shape_tokens = (
    "n == 1024 and L == 16",
    "n == 1024 and L == len(CORR_BETA)",
)
receipt = {
    "schema": "arc.whitebox.e136.public_k3_static.v1",
    "upstream": {
        "repository": "504aldo/whest-p2-cumulant-k3",
        "commit": UPSTREAM_COMMIT,
        "license": "MIT",
    },
    "files": files,
    "license_audit": {
        "contains_mit_license": "MIT License" in license_text,
        "contains_504aldo_copyright": "Copyright (c) 2026 504aldo" in license_text,
    },
    "phase2_import_audit": import_audit,
    "v25": {
        "strassen_symbol_present": "Strassen" in v25 or "STRASSEN" in v25,
        "suite_shape_gate_present": any(t in v25 for t in shape_tokens),
    },
    "v29": {
        "strassen_class_present": "class _Strassen" in v29,
        "strassen_levels_present": "STRASSEN_LEVELS" in v29,
        "suite_shape_gate_present": any(t in v29 for t in shape_tokens),
    },
    "published_reference": {
        "raw_final_layer_mse_approx": 2.13e-8,
        "v25_cb": 0.3667,
        "v29_cb": 0.2526,
    },
}

gates = {
    "all_upstream_blobs_match": all(v["blob_match"] for v in files.values()),
    "mit_notice_preserved": receipt["license_audit"]["contains_mit_license"]
    and receipt["license_audit"]["contains_504aldo_copyright"],
    "no_forbidden_direct_imports": all(
        not v["forbidden_direct_import_roots"] for v in import_audit.values()
    ),
    "v25_has_no_strassen": not receipt["v25"]["strassen_symbol_present"],
    "v29_has_strassen_cost_path": receipt["v29"]["strassen_class_present"]
    and receipt["v29"]["strassen_levels_present"],
    "suite_shape_gate_visible": receipt["v25"]["suite_shape_gate_present"]
    and receipt["v29"]["suite_shape_gate_present"],
}
receipt["gates"] = gates
receipt["static_pass"] = all(gates.values())

path = OUT / "E136_STATIC_RECEIPT.json"
path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(receipt, indent=2, sort_keys=True))
if not receipt["static_pass"]:
    raise SystemExit(1)
