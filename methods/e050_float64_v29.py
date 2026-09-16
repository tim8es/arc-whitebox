from __future__ import annotations

import hashlib
import os
import sys
import types
from dataclasses import dataclass
from typing import Any

import numpy as np

EXPECTED_BLOB = "17df1a073a24f96c4705b04bcf61ef60fa06dd0c"
UPSTREAM_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
UPSTREAM_RAW_URL = (
    "https://raw.githubusercontent.com/504aldo/whest-p2-cumulant-k3/"
    + UPSTREAM_COMMIT
    + "/estimators/estimator_v29.py"
)


def git_blob_sha(source: str) -> str:
    data = source.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def mechanical_float64_source(source: str) -> tuple[str, int]:
    """The entire E050 scientific mutation: replace V29's fnp.float32 dtype token.

    No constants, ranks, gates, control flow, stabilizers, or expressions are changed.
    """
    count = source.count("fnp.float32")
    if count <= 0:
        raise RuntimeError("upstream V29 contains no fnp.float32 tokens")
    transformed = source.replace("fnp.float32", "fnp.float64")
    if "fnp.float32" in transformed:
        raise RuntimeError("incomplete dtype transform")
    return transformed, count


def load_module(source: str, name: str, filename: str) -> types.ModuleType:
    # V29 setup warm-up is not part of predict and is irrelevant to Stage-A arithmetic.
    # Keeping it disabled also prevents setup-only arithmetic from contaminating replay FLOPs.
    os.environ.setdefault("V26_WARM", "0")
    mod = types.ModuleType(name)
    mod.__file__ = filename
    sys.modules[name] = mod
    exec(compile(source, filename, "exec"), mod.__dict__)
    return mod


def capture_lineno(source: str) -> int:
    needle = "sigma = fnp.sqrt(var)"
    matches = [i for i, line in enumerate(source.splitlines(), 1) if line.strip() == needle]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one capture line, found {matches}")
    return matches[0]


def _snapshot(value: Any):
    if value is None:
        return None
    return np.array(value, dtype=np.float64, copy=True)


@dataclass
class TraceCapture:
    filename: str
    lineno: int
    layers: list[dict[str, Any]]

    def tracer(self, frame, event, arg):
        if event == "line" and frame.f_code.co_filename == self.filename and frame.f_lineno == self.lineno:
            loc = frame.f_locals
            self.layers.append(
                {
                    "layer": int(loc["li"]),
                    "mode": int(loc.get("mode", -1)),
                    "k3_d3": _snapshot(loc.get("D3")),
                    "d21": _snapshot(loc.get("D21")),
                    "dg": _snapshot(loc.get("dG")),
                }
            )
        return self.tracer
