from __future__ import annotations

FINAL_K4_DAMP = 0.95

_TARGET = "                    g4row = dG * METRIC_C\n"
_REPLACEMENT = "                    g4row = dG * METRIC_C * (0.95 if last else 1.0)\n"


def final_k4_factor(*, last: bool) -> float:
    return FINAL_K4_DAMP if last else 1.0


def patch_v25_source(source: str) -> str:
    count = source.count(_TARGET)
    if count != 1:
        raise RuntimeError(f"E026 V25 patch target count={count}, expected 1")
    return source.replace(_TARGET, _REPLACEMENT, 1)
