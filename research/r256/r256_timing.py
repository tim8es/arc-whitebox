#!/usr/bin/env python3
"""R256 typed FlopScope timing boundary for the isolated R254 harness repair.

Primary contract pinned by R255/R256:
- FlopScope 0.12.1 BudgetContext.summary() -> str (display text)
- BudgetContext.residual_wall_time_s -> float | None
- BudgetContext.summary_dict() -> dict

Unknown timing is never coerced to zero.
"""
from __future__ import annotations

import math
from typing import Any


def capture_budget_telemetry(ctx: Any) -> dict:
    """Capture display summary plus the supported typed residual-time property."""
    summary_text = ctx.summary()
    if not isinstance(summary_text, str):
        raise TypeError("BudgetContext.summary() contract mismatch: expected str")
    residual = ctx.residual_wall_time_s
    if residual is None:
        residual_value = None
    elif isinstance(residual, bool) or not isinstance(residual, (int, float)):
        raise TypeError("BudgetContext.residual_wall_time_s contract mismatch: expected float|None")
    else:
        residual_value = float(residual)
        if not math.isfinite(residual_value) or residual_value < 0.0:
            raise ValueError("BudgetContext.residual_wall_time_s must be finite and nonnegative")
    return {
        "budget_summary": summary_text,
        "residual_wall_time_s": residual_value,
    }


def require_residual_wall_time(record: dict, label: str) -> tuple[float | None, str | None]:
    """Return a valid measured residual time or a fail-closed gate failure."""
    value = record.get("residual_wall_time_s")
    if value is None:
        return None, f"{label}_residual_wall_time_unavailable"
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None, f"{label}_residual_wall_time_invalid"
    value = float(value)
    if not math.isfinite(value) or value < 0.0:
        return None, f"{label}_residual_wall_time_invalid"
    return value, None
