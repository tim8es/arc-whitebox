from __future__ import annotations

import hashlib
import sys
import types
import urllib.request

UPSTREAM_COMMIT = "18c17e2d7a9aeacd399cfc2c6b571e4e16dbfb45"
EXPECTED_BLOB = "17df1a073a24f96c4705b04bcf61ef60fa06dd0c"
UPSTREAM_RAW_URL = (
    "https://raw.githubusercontent.com/504aldo/whest-p2-cumulant-k3/"
    + UPSTREAM_COMMIT
    + "/estimators/estimator_v29.py"
)
WIDTH = 1024
DEPTH = 16


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def fetch_exact_source() -> bytes:
    with urllib.request.urlopen(UPSTREAM_RAW_URL, timeout=60) as response:
        data = response.read()
    observed = git_blob_sha1(data)
    if observed != EXPECTED_BLOB:
        raise RuntimeError(f"V29 blob mismatch: {observed} != {EXPECTED_BLOB}")
    return data


def load_exact_v29(module_name: str = "e093_exact_v29") -> tuple[types.ModuleType, bytes]:
    data = fetch_exact_source()
    source = data.decode("utf-8")
    mod = types.ModuleType(module_name)
    mod.__file__ = f"<{module_name}:{EXPECTED_BLOB}>"
    sys.modules[module_name] = mod
    exec(compile(source, mod.__file__, "exec"), mod.__dict__)
    return mod, data
